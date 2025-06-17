import os
import yfinance as yf
from newsapi import NewsApiClient
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv
import requests
from time import sleep

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockNewsFetcher:
    def __init__(self):
        """Initialize the fetcher with API keys"""
        self.news_api = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
    def get_stock_data(self, ticker: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        Fetch stock data from Yahoo Finance
        """
        try:
            # Convert string dates to datetime if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Add one day to end_date to include the last day in the range
            end_date = end_date + timedelta(days=1)

            def fetch_data():
                # Download historical data directly without checking info
                hist = yf.download(
                    ticker,
                    start=start_date.strftime('%Y-%m-%d'),
                    end=end_date.strftime('%Y-%m-%d'),
                    interval='1d',
                    progress=False,
                    show_errors=False,
                    timeout=10
                )
                
                if hist.empty:
                    raise ValueError(f"No historical data found for {ticker}")
                
                return hist

            # Try to fetch data with retries and longer waits
            for attempt in range(3):
                try:
                    df = fetch_data()
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise
                    wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                    logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time}s")
                    sleep(wait_time)
            
            if df.empty:
                logger.warning(f"No stock data found for {ticker}")
                return None
                
            # Reset index to make date a column and ensure it's in the correct format
            df = df.reset_index()
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            
            # Rename columns to match database schema
            df = df.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Ensure all numeric columns are float
            numeric_columns = ['open', 'high', 'low', 'close']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Ensure volume is int
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
            
            # Add some debug logging
            logger.info(f"Successfully fetched data for {ticker}")
            logger.info(f"Data shape: {df.shape}")
            logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
            
            return df[['date', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Error fetching stock data: {str(e)}")
            return None

    def get_news(self, ticker: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch news articles from News API
        """
        try:
            # Convert string dates to datetime if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Limit the date range to last 30 days for free API
            today = datetime.now()
            from_date = max(start_date, today - timedelta(days=30))
            to_date = min(end_date, today)

            # Format dates for News API
            from_param = from_date.strftime('%Y-%m-%d')
            to_param = to_date.strftime('%Y-%m-%d')

            # Get news articles
            news = self.news_api.get_everything(
                q=ticker,
                from_param=from_param,
                to=to_param,
                language='en',
                sort_by='publishedAt'
            )

            if not news or not news.get('articles'):
                logger.warning(f"No news found for {ticker}")
                return []

            # Process articles
            articles = []
            for article in news['articles']:
                articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'source': article['source']['name'] if article['source'] else None
                })

            return articles

        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []

    def save_results(self, ticker: str, stock_data: pd.DataFrame, news_articles: List[Dict]):
        """Save results to two separate Delta Lake tables"""
        try:
            # 1. Prepara i dati per la tabella stock_data
            if stock_data is not None:
                # Converti l'indice datetime in colonna
                stock_data = stock_data.reset_index()
                # Aggiungi il ticker come colonna
                stock_data['ticker'] = ticker
                # Converti in DataFrame Spark
                stock_df = spark.createDataFrame(stock_data)
                
                # Percorso della tabella Delta per i dati azionari
                stock_delta_path = "data/stock_data_delta"
                
                # Se la tabella esiste, elimina i dati vecchi per questo ticker
                try:
                    delta_table = DeltaTable.forPath(spark, stock_delta_path)
                    delta_table.delete(f"ticker = '{ticker}'")
                except Exception:
                    # La tabella non esiste ancora, va bene così
                    pass
                
                # Salva i nuovi dati
                stock_df.write.format("delta") \
                    .option("delta.columnMapping.mode", "name") \
                    .option("delta.minReaderVersion", "2") \
                    .option("delta.minWriterVersion", "5") \
                    .mode("append") \
                    .save(stock_delta_path)
                
                logger.info(f"Stock data saved to Delta table at {stock_delta_path}")

            # 2. Prepara i dati per la tabella news
            if news_articles:
                # Crea una lista di dizionari con i dati delle news
                news_data = []
                for article in news_articles:
                    news_data.append({
                        'ticker': ticker,
                        'url': article['url'],
                        'published_at': article['published_at'],
                        'title': article['title'],
                        'source': article['source'],
                        'description': article['description'],
                        'content': '',
                        'author': '',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Converti in DataFrame Spark
                news_df = spark.createDataFrame(news_data)
                
                # Percorso della tabella Delta per le news
                news_delta_path = "data/news_delta"
                
                # Se la tabella esiste, elimina le news vecchie per questo ticker
                try:
                    delta_table = DeltaTable.forPath(spark, news_delta_path)
                    delta_table.delete(f"ticker = '{ticker}'")
                except Exception:
                    # La tabella non esiste ancora, va bene così
                    pass
                
                # Salva le nuove news
                news_df.write.format("delta") \
                    .option("delta.columnMapping.mode", "name") \
                    .option("delta.minReaderVersion", "2") \
                    .option("delta.minWriterVersion", "5") \
                    .mode("append") \
                    .save(news_delta_path)
                
                logger.info(f"News data saved to Delta table at {news_delta_path}")

        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            raise  # Rilanciamo l'eccezione per gestirla nel chiamante

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
        logger.info(stock_data[['date', 'open', 'high', 'low', 'close', 'volume']].tail())
    
    # Get news
    news_articles = fetcher.get_news(ticker, start_str, end_str)
    if news_articles:
        logger.info("\nRecent News Articles:")
        for article in news_articles[:5]:  # Show top 5 articles
            logger.info(f"\nTitle: {article['title']}")
            logger.info(f"Published: {article['published_at']}")
            logger.info(f"Source: {article['source']}")
            logger.info(f"URL: {article['url']}")
    
    # Save results
    fetcher.save_results(ticker, stock_data, news_articles)

if __name__ == "__main__":
    main() 