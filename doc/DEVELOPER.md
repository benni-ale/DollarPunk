# 🛠️ DollarPunk - Documentazione Tecnica per Sviluppatori

## 📋 Indice

1. [Architettura del Sistema](#architettura-del-sistema)
2. [API e Integrazioni](#api-e-integrazioni)
3. [Struttura del Codice](#struttura-del-codice)
4. [Database e Storage](#database-e-storage)
5. [Machine Learning](#machine-learning)
6. [Testing](#testing)
7. [Deployment](#deployment)
8. [Performance e Ottimizzazioni](#performance-e-ottimizzazioni)

## 🏗️ Architettura del Sistema

### Diagramma Architetturale

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Streamlit)   │◄──►│   (Python)      │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Storage  │    │   ML Models     │    │   NewsAPI       │
│   (JSON/CSV)    │    │   (FinBERT)     │    │   FMP API       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Componenti Principali

#### 1. Frontend Layer (Streamlit)
- **File**: `app.py`
- **Responsabilità**: Interfaccia utente, routing, visualizzazioni
- **Tecnologie**: Streamlit, Plotly, Pandas

#### 2. Data Fetcher Layer
- **File**: `fetch_news.py`, `fetch_historical_prices.py`
- **Responsabilità**: Raccolta dati esterni, caching, error handling
- **Tecnologie**: Requests, NewsAPI, Financial Modeling Prep

#### 3. ML Processing Layer
- **File**: `sentiment_analysis.py`
- **Responsabilità**: Analisi sentiment, preprocessing, model inference
- **Tecnologie**: Transformers, PyTorch, FinBERT

#### 4. Data Storage Layer
- **Directory**: `data/`
- **Responsabilità**: Persistenza dati, file management
- **Formati**: JSON, CSV

## 🔌 API e Integrazioni

### NewsAPI Integration

#### Configurazione
```python
from newsapi import NewsApiClient
from dotenv import load_dotenv

load_dotenv()
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
```

#### Endpoint Utilizzati
- **`get_everything`**: Ricerca notizie complete
- **Parametri**:
  - `q`: Query di ricerca
  - `language`: 'en' (inglese)
  - `from_param`: Data inizio (ieri)
  - `sort_by`: 'relevancy'
  - `page_size`: 10 articoli per stock

#### Rate Limiting
- **Free Tier**: 1,000 requests/day
- **Strategia**: Cache locale, batch processing
- **Fallback**: Retry con exponential backoff

### Financial Modeling Prep API

#### Configurazione
```python
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('FMP_KEY')
base_url = "https://financialmodelingprep.com/api/v3"
```

#### Endpoint Utilizzati
- **`/historical-price-full/{ticker}`**: Dati storici completi
- **Parametri**:
  - `apikey`: Chiave API
  - `serietype`: 'line' (dati giornalieri)

#### Gestione Errori
```python
def fetch_historical_data(ticker, start_date, end_date, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return process_response(response.json())
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise Exception(f"Failed to fetch data for {ticker}")
            time.sleep(2 ** attempt)  # Exponential backoff
```

## 📁 Struttura del Codice

### Organizzazione Moduli

```
DollarPunk/
├── app.py                          # Entry point principale
├── fetch_news.py                   # News fetching module
├── sentiment_analysis.py           # ML sentiment analysis
├── fetch_historical_prices.py      # Historical data fetcher
├── utils/                          # Utility functions (future)
│   ├── __init__.py
│   ├── data_processing.py
│   └── visualization.py
├── models/                         # ML models (future)
│   ├── __init__.py
│   └── sentiment_model.py
└── config/                         # Configuration (future)
    ├── __init__.py
    └── settings.py
```

### Pattern di Design Utilizzati

#### 1. Factory Pattern (News Fetching)
```python
def fetch_stock_news(ticker, stock_info):
    """Factory method per fetching notizie per stock specifico"""
    keywords = ' OR '.join(f'"{keyword}"' for keyword in stock_info['keywords'])
    query = f'({keywords}) AND (stock OR market OR shares OR company OR earnings)'
    return newsapi.get_everything(q=query, ...)
```

#### 2. Strategy Pattern (Sentiment Analysis)
```python
def get_sentiment(text, tokenizer, model):
    """Strategy per analisi sentiment con FinBERT"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    return process_predictions(predictions)
```

#### 3. Observer Pattern (Data Updates)
```python
# Future implementation
class DataObserver:
    def update(self, data_type, new_data):
        if data_type == "news":
            self.process_news(new_data)
        elif data_type == "prices":
            self.process_prices(new_data)
```

### Gestione Errori

#### Custom Exceptions
```python
class DollarPunkException(Exception):
    """Base exception for DollarPunk application"""
    pass

class APIError(DollarPunkException):
    """Raised when external API calls fail"""
    pass

class DataProcessingError(DollarPunkException):
    """Raised when data processing fails"""
    pass
```

#### Error Handling Strategy
```python
def safe_api_call(func, *args, **kwargs):
    """Decorator per safe API calls con retry logic"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise APIError(f"API call failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)
```

## 💾 Database e Storage

### Struttura File System

#### Directory `data/`
```
data/
├── historical_prices.csv           # Dati storici prezzi
├── portfolio_news_YYYYMMDD_HHMMSS.json      # Notizie raw
├── portfolio_news_YYYYMMDD_HHMMSS_sentiment.json  # Notizie con sentiment
├── price_summary.json             # Statistiche riassuntive
└── cache/                         # Cache locale (future)
    ├── news_cache.json
    └── prices_cache.json
```

#### Schema Dati

##### Historical Prices (CSV)
```csv
Date,Ticker,Open,High,Low,Close,Volume,Daily_Return,Volatility,MA50,MA200,Volume_MA20
2025-01-17,TSLA,215.50,218.30,214.20,217.80,45678900,0.0123,0.0234,220.15,198.45,42345678
```

##### News Data (JSON)
```json
{
  "metadata": {
    "generated_at": "2025-01-18T10:45:33.123456",
    "source_api": "NewsAPI",
    "api_version": "v2",
    "stocks_count": 5,
    "total_articles": 47
  },
  "stocks": {
    "TSLA": [
      {
        "title": "Tesla Q4 Earnings Beat Expectations",
        "description": "Tesla reported strong Q4 results...",
        "url": "https://example.com/article",
        "publishedAt": "2025-01-18T09:00:00Z",
        "ticker": "TSLA",
        "company": "Tesla",
        "id": "abc123def456",
        "data_source": {
          "api": "NewsAPI",
          "version": "v2",
          "endpoint": "everything",
          "fetch_timestamp": "2025-01-18T10:45:33.123456"
        }
      }
    ]
  }
}
```

### Future Database Migration

#### PostgreSQL Schema (Proposed)
```sql
-- Stocks table
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Historical prices table
CREATE TABLE historical_prices (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    daily_return DECIMAL(8,6),
    volatility DECIMAL(8,6),
    ma50 DECIMAL(10,2),
    ma200 DECIMAL(10,2),
    volume_ma20 BIGINT,
    UNIQUE(stock_id, date)
);

-- News articles table
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    published_at TIMESTAMP,
    article_id VARCHAR(255) UNIQUE,
    sentiment_positive DECIMAL(5,4),
    sentiment_negative DECIMAL(5,4),
    sentiment_neutral DECIMAL(5,4),
    sentiment_label VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 Machine Learning

### FinBERT Model

#### Caricamento Modello
```python
def load_finbert():
    """Load FinBERT model and tokenizer"""
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    return tokenizer, model
```

#### Preprocessing
```python
def preprocess_text(text):
    """Preprocess text for sentiment analysis"""
    # Combine title and description
    combined_text = f"{text['title']} {text['description']}"
    
    # Clean text (future enhancement)
    cleaned_text = clean_text(combined_text)
    
    return cleaned_text

def clean_text(text):
    """Clean and normalize text"""
    import re
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text
```

#### Inference Pipeline
```python
def get_sentiment(text, tokenizer, model):
    """Get sentiment scores for a text using FinBERT"""
    # Tokenize
    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        max_length=512
    )
    
    # Inference
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # Process results
    scores = predictions[0].detach().numpy()
    sentiment_dict = {
        "sentiment_positive": float(scores[0]),
        "sentiment_negative": float(scores[1]),
        "sentiment_neutral": float(scores[2]),
        "sentiment_label": ["positive", "negative", "neutral"][scores.argmax()]
    }
    
    return sentiment_dict
```

### Performance Optimization

#### Batch Processing
```python
def process_batch(texts, tokenizer, model, batch_size=8):
    """Process multiple texts in batches"""
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        
        # Tokenize batch
        inputs = tokenizer(
            batch, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        # Inference
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Process results
        for pred in predictions:
            scores = pred.detach().numpy()
            results.append({
                "sentiment_positive": float(scores[0]),
                "sentiment_negative": float(scores[1]),
                "sentiment_neutral": float(scores[2]),
                "sentiment_label": ["positive", "negative", "neutral"][scores.argmax()]
            })
    
    return results
```

## 🧪 Testing

### Test Structure (Future)

```
tests/
├── __init__.py
├── test_fetch_news.py
├── test_sentiment_analysis.py
├── test_historical_prices.py
├── test_app.py
├── conftest.py
└── fixtures/
    ├── sample_news.json
    ├── sample_prices.csv
    └── sample_sentiment.json
```

### Unit Tests

#### Test News Fetching
```python
import pytest
from unittest.mock import Mock, patch
from fetch_news import fetch_stock_news, generate_article_id

def test_generate_article_id():
    """Test article ID generation"""
    url = "https://example.com/article"
    published_at = "2025-01-18T09:00:00Z"
    
    id1 = generate_article_id(url, published_at)
    id2 = generate_article_id(url, published_at)
    
    assert id1 == id2
    assert len(id1) == 16

@patch('fetch_news.newsapi')
def test_fetch_stock_news(mock_newsapi):
    """Test news fetching for a stock"""
    # Mock API response
    mock_response = {
        'articles': [
            {
                'title': 'Test Article',
                'description': 'Test Description',
                'url': 'https://example.com',
                'publishedAt': '2025-01-18T09:00:00Z'
            }
        ]
    }
    mock_newsapi.get_everything.return_value = mock_response
    
    # Test
    stock_info = {
        'company': 'Tesla',
        'keywords': ['Tesla', 'Elon Musk']
    }
    
    result = fetch_stock_news('TSLA', stock_info)
    
    assert len(result) == 1
    assert result[0]['ticker'] == 'TSLA'
    assert result[0]['company'] == 'Tesla'
```

#### Test Sentiment Analysis
```python
import pytest
from unittest.mock import Mock, patch
from sentiment_analysis import get_sentiment, process_json_file

@patch('sentiment_analysis.AutoTokenizer')
@patch('sentiment_analysis.AutoModelForSequenceClassification')
def test_get_sentiment(mock_model_class, mock_tokenizer_class):
    """Test sentiment analysis"""
    # Mock tokenizer and model
    mock_tokenizer = Mock()
    mock_model = Mock()
    
    mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
    mock_model_class.from_pretrained.return_value = mock_model
    
    # Mock tokenization
    mock_tokenizer.return_value = {'input_ids': Mock(), 'attention_mask': Mock()}
    
    # Mock model output
    mock_output = Mock()
    mock_output.logits = Mock()
    mock_model.return_value = mock_output
    
    # Test
    text = "Tesla reports strong earnings"
    result = get_sentiment(text, mock_tokenizer, mock_model)
    
    assert 'sentiment_positive' in result
    assert 'sentiment_negative' in result
    assert 'sentiment_neutral' in result
    assert 'sentiment_label' in result
```

### Integration Tests

```python
import pytest
from app import main
import tempfile
import os

def test_end_to_end_workflow():
    """Test complete workflow from news fetching to sentiment analysis"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Setup test environment
        os.chdir(temp_dir)
        
        # Create test portfolio
        with open('portfolio.json', 'w') as f:
            json.dump({"stocks": ["TSLA"]}, f)
        
        # Create test keywords
        with open('keywords.json', 'w') as f:
            json.dump({
                "TSLA": {
                    "company": "Tesla",
                    "keywords": ["Tesla"]
                }
            }, f)
        
        # Test workflow
        # 1. Fetch news
        # 2. Analyze sentiment
        # 3. View results
        
        assert os.path.exists('data/')
```

## 🚀 Deployment

### Docker Configuration

#### Multi-stage Build (Optimized)
```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .

RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data && chmod 777 data

# Make start script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8501

# Run application
CMD ["/app/start.sh"]
```

#### Docker Compose (Production)
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./portfolio.json:/app/portfolio.json
      - ./keywords.json:/app/keywords.json
    environment:
      - NEWS_API_KEY=${NEWS_API_KEY}
      - FMP_KEY=${FMP_KEY}
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 12G
        reservations:
          memory: 8G
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Future: Add Redis for caching
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### CI/CD Pipeline (GitHub Actions)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t dollarpunk .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker tag dollarpunk ${{ secrets.DOCKER_USERNAME }}/dollarpunk:latest
        docker push ${{ secrets.DOCKER_USERNAME }}/dollarpunk:latest
```

## ⚡ Performance e Ottimizzazioni

### Caching Strategy

#### Redis Cache Implementation
```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=3600):
    """Decorator per caching risultati"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key, 
                expire_time, 
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

@cache_result(expire_time=1800)  # 30 minutes
def fetch_stock_news(ticker, stock_info):
    """Cached news fetching"""
    # ... existing implementation
```

### Async Processing

#### Async News Fetching
```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def fetch_news_async(tickers, keywords):
    """Async news fetching for multiple tickers"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ticker in tickers:
            if ticker in keywords:
                task = fetch_stock_news_async(session, ticker, keywords[ticker])
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

async def fetch_stock_news_async(session, ticker, stock_info):
    """Async news fetching for single stock"""
    # Implementation with aiohttp
    pass
```

### Database Optimization

#### Indexing Strategy
```sql
-- Performance indexes
CREATE INDEX idx_historical_prices_stock_date ON historical_prices(stock_id, date);
CREATE INDEX idx_news_articles_stock_published ON news_articles(stock_id, published_at);
CREATE INDEX idx_news_articles_sentiment ON news_articles(sentiment_label);

-- Partitioning for large datasets
CREATE TABLE historical_prices_2025 PARTITION OF historical_prices
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Memory Optimization

#### Streaming Processing
```python
def process_large_dataset(file_path):
    """Stream processing for large datasets"""
    with open(file_path, 'r') as f:
        for line in f:
            # Process one line at a time
            data = json.loads(line)
            yield process_item(data)

def process_item(item):
    """Process single item"""
    # Process without loading entire dataset in memory
    return transformed_item
```

## 🔧 Configurazione Avanzata

### Environment Variables

```bash
# API Keys
NEWS_API_KEY=your_newsapi_key
FMP_KEY=your_fmp_key

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
CACHE_TTL=3600
MAX_RETRIES=3

# Database (Future)
DATABASE_URL=postgresql://user:pass@localhost/dollarpunk
REDIS_URL=redis://localhost:6379

# ML Model Settings
MODEL_CACHE_DIR=/app/models
BATCH_SIZE=8
MAX_SEQUENCE_LENGTH=512

# Performance
WORKER_PROCESSES=4
MAX_CONCURRENT_REQUESTS=10
```

### Logging Configuration

```python
import logging
import os

def setup_logging():
    """Setup application logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('dollarpunk.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('transformers').setLevel(logging.WARNING)
```

---

Questa documentazione tecnica fornisce una guida completa per gli sviluppatori che vogliono contribuire o estendere il progetto DollarPunk. Per domande specifiche, consultare i commenti nel codice o aprire un issue su GitHub. 