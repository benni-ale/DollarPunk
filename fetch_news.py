import os
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'dollarpunk'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def fetch_news():
    """
    Fetch financial news from NewsAPI
    """
    try:
        # Get news from the last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        
        news = newsapi.get_everything(
            q='(finance OR stock market OR cryptocurrency)',
            language='en',
            from_param=yesterday.strftime('%Y-%m-%d'),
            sort_by='publishedAt'
        )
        
        return news['articles']
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []

def store_news(articles):
    """
    Store news articles in PostgreSQL database
    """
    if not articles:
        print("No articles to store")
        return
    
    # Prepare data for insertion
    values = [
        (
            article['title'],
            article.get('description'),
            article['url'],
            article['publishedAt'],
            article['source']['name']
        )
        for article in articles
    ]
    
    # SQL query for inserting data
    insert_query = """
        INSERT INTO news_articles (title, description, url, published_at, source_name)
        VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                execute_values(cur, insert_query, values)
            conn.commit()
            print(f"Successfully stored {len(values)} articles")
    except Exception as e:
        print(f"Error storing articles in database: {e}")

def main():
    # Fetch news articles
    articles = fetch_news()
    
    # Store articles in database
    store_news(articles)

if __name__ == "__main__":
    main() 