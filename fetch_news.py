import os
import json
from datetime import datetime, timedelta
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

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

def save_news(articles):
    """
    Save news articles to a JSON file
    """
    if not articles:
        print("No articles to save")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate filename with current timestamp
    filename = f"data/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {len(articles)} articles to {filename}")
    except Exception as e:
        print(f"Error saving articles to file: {e}")

def main():
    # Fetch news articles
    articles = fetch_news()
    
    # Save articles to JSON file
    save_news(articles)

if __name__ == "__main__":
    main() 