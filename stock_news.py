import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import os
from dotenv import load_dotenv
import logging
import time
from typing import Optional, Dict, List
import json
from pyspark.sql import SparkSession
from delta.tables import DeltaTable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Inizializza la sessione Spark
spark = (SparkSession.builder
    .appName("StockNewsFetcher")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate())

# Imposta il livello di log
spark.sparkContext.setLogLevel("WARN")

class StockNewsFetcher:
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
    def _retry_on_failure(self, func, *args, **kwargs):
        """Generic retry mechanism for API calls"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed after {self.max_retries} attempts: {str(e)}")
                    raise
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(self.retry_delay)

    def get_stock_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """Fetch stock data with retry mechanism"""
        try:
            logger.info(f"Fetching stock data for {ticker}")
            stock = yf.Ticker(ticker)
            data = self._retry_on_failure(
                stock.history,
                start=start_date,
                end=end_date
            )
            
            if data.empty:
                logger.warning(f"No data found for {ticker}")
                return None
                
            return data
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            return None

    def get_news(self, ticker: str, from_date: str, to_date: str) -> List[Dict]:
        """Fetch news articles with retry mechanism"""
        try:
            logger.info(f"Fetching news for {ticker}")
            news = self._retry_on_failure(
                self.newsapi.get_everything,
                q=ticker,
                from_param=from_date,
                to=to_date,
                language='en',
                sort_by='relevancy'
            )
            
            if not news.get('articles'):
                logger.warning(f"No news found for {ticker}")
                return []
                
            return news['articles']
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def save_results(self, ticker: str, stock_data: pd.DataFrame, news_articles: List[Dict]):
        """Save results to Delta Lake table with upsert (merge)"""
        try:
            # Prepara i dati per il DataFrame
            results = {
                'ticker': ticker,
                'timestamp': datetime.now().isoformat(),
                'stock_data': json.dumps(stock_data.to_dict(orient='records') if stock_data is not None else []),
                'news': json.dumps(news_articles)
            }
            
            # Converti in DataFrame Spark
            df = spark.createDataFrame([results])
            
            # Percorso della tabella Delta
            delta_path = f"data/delta_table_{ticker}"
            
            # Se la tabella esiste, fai merge (upsert), altrimenti creala
            if os.path.exists(delta_path):
                deltaTable = DeltaTable.forPath(spark, delta_path)
                deltaTable.alias("old").merge(
                    df.alias("new"),
                    "old.timestamp = new.timestamp"
                ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
            else:
                df.write.format("delta").mode("overwrite").save(delta_path)
            
            logger.info(f"Results saved to Delta table at {delta_path}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

def main():
    # Example parameters
    ticker = "AAPL"  # Apple stock
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Format dates for API calls
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    logger.info(f"Starting data fetch for {ticker} from {start_str} to {end_str}")
    
    fetcher = StockNewsFetcher()
    
    # Get stock data
    stock_data = fetcher.get_stock_data(ticker, start_str, end_str)
    if stock_data is not None:
        logger.info("\nStock Data:")
        logger.info(stock_data[['Open', 'Close', 'Volume']].tail())
    
    # Get news
    news_articles = fetcher.get_news(ticker, start_str, end_str)
    if news_articles:
        logger.info("\nRecent News Articles:")
        for article in news_articles[:5]:  # Show top 5 articles
            logger.info(f"\nTitle: {article['title']}")
            logger.info(f"Published: {article['publishedAt']}")
            logger.info(f"Source: {article['source']['name']}")
            logger.info(f"URL: {article['url']}")
    
    # Save results
    fetcher.save_results(ticker, stock_data, news_articles)

if __name__ == "__main__":
    main() 