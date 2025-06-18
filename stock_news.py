from newsapi import NewsApiClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

class StockNewsFetcher:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NEWS_API_KEY environment variable is not set")
        self.newsapi = NewsApiClient(api_key=self.api_key)
        self.load_config()

    def load_config(self):
        """Load portfolio and keywords configuration"""
        try:
            with open('config/portfolio.json', 'r') as f:
                self.portfolio = json.load(f)
            with open('config/keywords.json', 'r') as f:
                self.keywords = json.load(f)
            logging.info("Configuration loaded successfully")
        except FileNotFoundError as e:
            logging.error(f"Configuration file not found: {e}")
            raise

    def fetch_news_for_stock(self, stock: str) -> List[Dict[str, Any]]:
        """Fetch news for a specific stock using its keywords"""
        keywords = self.keywords.get(stock, [])
        if not keywords:
            logging.warning(f"No keywords found for stock {stock}")
            return []

        # Create query string with stock symbol and keywords
        query = f"{stock} OR {' OR '.join(keywords)}"
        
        try:
            # Get news from the last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            
            news = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                from_param=yesterday.isoformat(),
                page_size=100
            )

            articles = news.get('articles', [])
            logging.info(f"Fetched {len(articles)} articles for {stock}")
            
            # Add stock symbol to each article
            for article in articles:
                article['stock'] = stock
                article['fetch_time'] = datetime.now().isoformat()
                
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching news for {stock}: {e}")
            return []

    def fetch_all_news(self) -> Dict[str, Any]:
        """Fetch news for all stocks in portfolio"""
        all_news = []
        stocks = self.portfolio.get('stocks', [])
        
        for stock in stocks:
            logging.info(f"Fetching news for {stock}")
            articles = self.fetch_news_for_stock(stock)
            all_news.extend(articles)
            # Sleep to respect API rate limits
            time.sleep(1)

        return {
            "metadata": {
                "fetch_time": datetime.now().isoformat(),
                "stocks_processed": stocks,
                "total_articles": len(all_news)
            },
            "articles": all_news
        }

def main():
    try:
        fetcher = StockNewsFetcher()
        news_data = fetcher.fetch_all_news()
        
        # Save to JSON file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "data/news_json"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/news_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(news_data, f, indent=2)
            
        logging.info(f"News data saved to {output_file}")
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main() 