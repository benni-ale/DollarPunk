import os
import json
import hashlib
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv
from simple_logger import logger

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
    Save news articles organized by stock and return the filename
    """
    if not all_articles:
        print("No articles to save")
        return None
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate filename with current timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"data/portfolio_news_{timestamp}.json"
    
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
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved news for {len(news_by_stock)} stocks to {filename}")
        
        # Print summary
        for ticker, articles in news_by_stock.items():
            print(f"{ticker}: {len(articles)} articles found")
            
        return filename
    except Exception as e:
        print(f"Error saving articles to file: {e}")
        return None

def fetch_and_save_news():
    """
    Main function to fetch and save news, returns the filename where news was saved
    """
    # Log start of execution
    logger.log_execution("fetch_news.py", "started", {"function": "fetch_and_save_news"})
    
    try:
        # Load portfolio and keywords
        portfolio = load_portfolio()
        keywords = load_keywords()
        
        if not portfolio:
            error_msg = "No stocks found in portfolio!"
            logger.log_execution("fetch_news.py", "failed", {"error": error_msg})
            raise Exception(error_msg)
        
        if not keywords:
            error_msg = "No keywords found!"
            logger.log_execution("fetch_news.py", "failed", {"error": error_msg})
            raise Exception(error_msg)
        
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
        filename = save_news_by_stock(all_articles)
        if not filename:
            error_msg = "Failed to save news articles"
            logger.log_execution("fetch_news.py", "failed", {"error": error_msg})
            raise Exception(error_msg)
        
        # Log successful completion
        logger.log_execution("fetch_news.py", "completed", {
            "output_file": filename,
            "articles_count": len(all_articles),
            "stocks_processed": len(portfolio)
        })
        
        return filename
        
    except Exception as e:
        # Log error
        logger.log_execution("fetch_news.py", "failed", {"error": str(e)})
        raise e

def fetch_and_save_news_custom(query):
    """
    Fetch and save news using a custom query string (tickers, keywords, testo libero)
    """
    logger.log_execution("fetch_news.py", "started", {"function": "fetch_and_save_news_custom", "query": query})
    try:
        yesterday = datetime.now() - timedelta(days=1)
        news = newsapi.get_everything(
            q=query,
            language='en',
            from_param=yesterday.strftime('%Y-%m-%d'),
            sort_by='relevancy',
            page_size=50  # Più ampio per query custom
        )
        all_articles = news['articles']
        # Aggiungi info extra
        for article in all_articles:
            article['id'] = generate_article_id(article['url'], article['publishedAt'])
            article['data_source'] = {
                'api': 'NewsAPI',
                'version': 'v2',
                'endpoint': 'everything',
                'fetch_timestamp': datetime.now().isoformat(),
                'custom_query': query
            }
        # Salva in un file unico
        os.makedirs('data', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/custom_news_{timestamp}.json"
        output_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_api': 'NewsAPI',
                'api_version': 'v2',
                'query': query,
                'total_articles': len(all_articles)
            },
            'articles': all_articles
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.log_execution("fetch_news.py", "completed", {
            "output_file": filename,
            "articles_count": len(all_articles),
            "query": query
        })
        return filename
    except Exception as e:
        logger.log_execution("fetch_news.py", "failed", {"error": str(e), "query": query})
        raise e

if __name__ == "__main__":
    fetch_and_save_news() 