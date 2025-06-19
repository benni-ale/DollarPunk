# 🚀 DollarPunk - Guida al Deployment

## 📋 Panoramica

Questa guida ti accompagnerà attraverso il processo di deployment di DollarPunk in diversi ambienti, dal locale alla produzione.

## 🏠 Deployment Locale

### Prerequisiti

- Docker e Docker Compose installati
- Chiavi API per NewsAPI e Financial Modeling Prep
- Almeno 8GB di RAM disponibile

### Setup Rapido

1. **Clona il repository**:
   ```bash
   git clone <repository-url>
   cd DollarPunk
   ```

2. **Crea file di configurazione**:
   ```bash
   # Crea .env
   cat > .env << EOF
   NEWS_API_KEY=your_newsapi_key_here
   FMP_KEY=your_financial_modeling_prep_key_here
   EOF
   ```

3. **Avvia l'applicazione**:
   ```bash
   docker-compose up --build
   ```

4. **Accesso**:
   Apri http://localhost:8501 nel browser

### Configurazione Avanzata Locale

#### Personalizzazione Portfolio
```bash
# Modifica portfolio.json
cat > portfolio.json << EOF
{
  "stocks": ["TSLA", "AAPL", "NVDA", "MSFT", "GOOGL"]
}
EOF
```

#### Personalizzazione Keywords
```bash
# Modifica keywords.json
cat > keywords.json << EOF
{
  "TSLA": {
    "company": "Tesla",
    "keywords": ["Tesla", "Elon Musk", "Cybertruck"]
  }
}
EOF
```

#### Ottimizzazione Risorse
```yaml
# docker-compose.yml personalizzato
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
          cpus: '4.0'
          memory: 16G
        reservations:
          memory: 12G
    restart: unless-stopped
```

## ☁️ Deployment Cloud

### AWS Deployment

#### EC2 con Docker

1. **Setup EC2 Instance**:
   ```bash
   # Ubuntu 22.04 LTS
   # t3.large o superiore (2 vCPU, 8GB RAM)
   ```

2. **Installazione Docker**:
   ```bash
   # Aggiorna sistema
   sudo apt update && sudo apt upgrade -y

   # Installa Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Installa Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose

   # Aggiungi utente al gruppo docker
   sudo usermod -aG docker $USER
   ```

3. **Deployment**:
   ```bash
   # Clona repository
   git clone <repository-url>
   cd DollarPunk

   # Configura environment
   cat > .env << EOF
   NEWS_API_KEY=your_newsapi_key_here
   FMP_KEY=your_financial_modeling_prep_key_here
   EOF

   # Avvia applicazione
   docker-compose up -d --build
   ```

4. **Configurazione Security Group**:
   - Porta 8501: Inbound TCP
   - Porta 22: SSH (se necessario)

#### AWS ECS (Elastic Container Service)

1. **Dockerfile ottimizzato**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       && rm -rf /var/lib/apt/lists/*

   # Install Python packages
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   # Copy application
   COPY . .

   # Create data directory
   RUN mkdir -p data && chmod 777 data

   # Health check
   HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
     CMD curl -f http://localhost:8501/_stcore/health || exit 1

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
   ```

2. **Task Definition**:
   ```json
   {
     "family": "dollarpunk",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "2048",
     "memory": "8192",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "dollarpunk",
         "image": "your-account.dkr.ecr.region.amazonaws.com/dollarpunk:latest",
         "portMappings": [
           {
             "containerPort": 8501,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "NEWS_API_KEY",
             "value": "your_newsapi_key"
           },
           {
             "name": "FMP_KEY",
             "value": "your_fmp_key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/dollarpunk",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

### Google Cloud Platform

#### Cloud Run

1. **Dockerfile per Cloud Run**:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   # Install dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       && rm -rf /var/lib/apt/lists/*

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   # Create data directory
   RUN mkdir -p data && chmod 777 data

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
   ```

2. **Deployment**:
   ```bash
   # Build e push immagine
   gcloud builds submit --tag gcr.io/PROJECT_ID/dollarpunk

   # Deploy su Cloud Run
   gcloud run deploy dollarpunk \
     --image gcr.io/PROJECT_ID/dollarpunk \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 8Gi \
     --cpu 2 \
     --set-env-vars NEWS_API_KEY=your_key,FMP_KEY=your_key
   ```

### Azure

#### Azure Container Instances

1. **Deployment con Azure CLI**:
   ```bash
   # Login
   az login

   # Create resource group
   az group create --name dollarpunk-rg --location eastus

   # Deploy container
   az container create \
     --resource-group dollarpunk-rg \
     --name dollarpunk \
     --image your-registry.azurecr.io/dollarpunk:latest \
     --dns-name-label dollarpunk \
     --ports 8501 \
     --memory 8 \
     --cpu 2 \
     --environment-variables NEWS_API_KEY=your_key FMP_KEY=your_key
   ```

## 🐳 Docker Production

### Multi-stage Build Ottimizzato

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data && chmod 777 data

# Add user for security
RUN useradd -m -u 1000 dollarpunk && \
    chown -R dollarpunk:dollarpunk /app
USER dollarpunk

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### Docker Compose Production

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - dollarpunk_data:/app/data
      - ./portfolio.json:/app/portfolio.json:ro
      - ./keywords.json:/app/keywords.json:ro
    environment:
      - NEWS_API_KEY=${NEWS_API_KEY}
      - FMP_KEY=${FMP_KEY}
      - DEBUG=False
      - LOG_LEVEL=INFO
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
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis per caching (opzionale)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

volumes:
  dollarpunk_data:
    driver: local
  redis_data:
    driver: local
```

## 🔒 Sicurezza

### Best Practices

1. **Environment Variables**:
   ```bash
   # Non committare mai le chiavi API
   echo ".env" >> .gitignore
   echo "data/" >> .gitignore
   ```

2. **Docker Security**:
   ```dockerfile
   # Usa utente non-root
   RUN useradd -m -u 1000 dollarpunk
   USER dollarpunk

   # Non esporre porte non necessarie
   EXPOSE 8501
   ```

3. **Network Security**:
   ```yaml
   # Docker Compose con network isolato
   networks:
     dollarpunk_network:
       driver: bridge
   ```

### SSL/TLS Configuration

#### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Let's Encrypt con Certbot

```bash
# Installazione Certbot
sudo apt install certbot python3-certbot-nginx

# Generazione certificato
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Aggiungi: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring e Logging

### Prometheus + Grafana

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'dollarpunk'
    static_configs:
      - targets: ['localhost:8501']
    metrics_path: '/metrics'
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "DollarPunk Metrics",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_request_duration_seconds_sum[5m])"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{name=\"dollarpunk\"}"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration

```python
# logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # File handler con rotation
    file_handler = RotatingFileHandler(
        'dollarpunk.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
```

## 🔄 CI/CD Pipeline

### GitHub Actions

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

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/dollarpunk:latest
          ${{ secrets.DOCKER_USERNAME }}/dollarpunk:${{ github.sha }}
    
    - name: Deploy to production
      run: |
        # Deploy script
        echo "Deploying to production..."
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
    - pytest tests/ --cov=.

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t dollarpunk .
    - docker tag dollarpunk registry.gitlab.com/user/dollarpunk:latest
    - docker push registry.gitlab.com/user/dollarpunk:latest

deploy:
  stage: deploy
  script:
    - echo "Deploying to production..."
  only:
    - main
```

## 🔧 Troubleshooting

### Problemi Comuni

#### 1. Container non si avvia
```bash
# Controlla log
docker-compose logs app

# Verifica risorse
docker stats

# Riavvia container
docker-compose restart app
```

#### 2. Problemi di memoria
```bash
# Aumenta memoria in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 16G
    reservations:
      memory: 12G
```

#### 3. Problemi di rete
```bash
# Verifica porte
netstat -tulpn | grep 8501

# Test connettività
curl -f http://localhost:8501/_stcore/health
```

#### 4. Problemi di permessi
```bash
# Fix permessi data directory
sudo chown -R 1000:1000 data/
sudo chmod -R 755 data/
```

### Debug Avanzato

#### Profiling Performance
```python
# Aggiungi profiling al codice
import cProfile
import pstats

def profile_function(func):
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)
        return result
    return wrapper
```

#### Memory Profiling
```python
# Monitora uso memoria
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    logging.info(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
```

---

Questa guida copre tutti gli aspetti del deployment di DollarPunk. Per domande specifiche o problemi, consultare la documentazione ufficiale o aprire un issue su GitHub. 