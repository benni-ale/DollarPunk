import os
import json
import hashlib
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

def generate_article_id(url, published_at):
    """
    Generate a unique ID for an article based on URL and publication date
    """
    # Combine URL and published_at to create a unique string
    unique_string = f"{url}{published_at}"
    # Create SHA-256 hash
    return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

def load_portfolio():
    """
    Load portfolio stocks from portfolio.json
    """
    try:
        with open('portfolio.json', 'r') as f:
            data = json.load(f)
            return data.get('stocks', [])
    except Exception as e:
        print(f"Error loading portfolio: {e}")
        return []

def load_keywords():
    """
    Load keywords for each stock from keywords.json
    """
    try:
        with open('keywords.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading keywords: {e}")
        return {}

def fetch_stock_news(ticker, stock_info):
    """
    Fetch news for a specific stock
    """
    try:
        # Costruisci la query combinando le keywords
        keywords = ' OR '.join(f'"{keyword}"' for keyword in stock_info['keywords'])
        query = f'({keywords}) AND (stock OR market OR shares OR company OR earnings)'
        
        yesterday = datetime.now() - timedelta(days=1)
        
        news = newsapi.get_everything(
            q=query,
            language='en',
            from_param=yesterday.strftime('%Y-%m-%d'),
            sort_by='relevancy',
            page_size=10  # Limita a 10 notizie più rilevanti per azione
        )
        
        # Aggiungi informazioni aggiuntive a ogni articolo
        for article in news['articles']:
            article['ticker'] = ticker
            article['company'] = stock_info['company']
            article['id'] = generate_article_id(article['url'], article['publishedAt'])
            article['data_source'] = {
                'api': 'NewsAPI',
                'version': 'v2',
                'endpoint': 'everything',
                'fetch_timestamp': datetime.now().isoformat()
            }
        
        return news['articles']
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []

def save_news_by_stock(all_articles):
    """
    Save news articles organized by stock
    """
    if not all_articles:
        print("No articles to save")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate filename with current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Organize articles by stock
    news_by_stock = {}
    for article in all_articles:
        ticker = article['ticker']
        if ticker not in news_by_stock:
            news_by_stock[ticker] = []
        news_by_stock[ticker].append(article)
    
    # Prepare the complete data structure
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_api': 'NewsAPI',
            'api_version': 'v2',
            'stocks_count': len(news_by_stock),
            'total_articles': len(all_articles)
        },
        'stocks': news_by_stock
    }
    
    # Save organized news
    filename = f"data/portfolio_news_{timestamp}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved news for {len(news_by_stock)} stocks to {filename}")
        
        # Print summary
        for ticker, articles in news_by_stock.items():
            print(f"{ticker}: {len(articles)} articles found")
    except Exception as e:
        print(f"Error saving articles to file: {e}")

def main():
    # Load portfolio and keywords
    portfolio = load_portfolio()
    keywords = load_keywords()
    
    if not portfolio:
        print("No stocks found in portfolio!")
        return
    
    if not keywords:
        print("No keywords found!")
        return
    
    # Fetch news for each stock in portfolio
    all_articles = []
    for ticker in portfolio:
        if ticker in keywords:
            print(f"Fetching news for {ticker}...")
            articles = fetch_stock_news(ticker, keywords[ticker])
            all_articles.extend(articles)
        else:
            print(f"No keywords found for {ticker}, skipping...")
    
    # Save all articles organized by stock
    save_news_by_stock(all_articles)

if __name__ == "__main__":
    main() 