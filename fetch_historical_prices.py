import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv
from simple_logger import logger

def load_portfolio():
    """Load stock tickers from portfolio.json"""
    with open('portfolio.json', 'r') as f:
        portfolio = json.load(f)
    return portfolio['stocks']

def fetch_historical_data(ticker, start_date, end_date, max_retries=3):
    """Fetch historical data for a single ticker with retries using FMP API"""
    load_dotenv()
    api_key = os.getenv('FMP_KEY')
    if not api_key:
        raise ValueError("FMP_KEY not found in .env file")

    base_url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}"
    params = {
        "apikey": api_key,
        "serietype": "line"
    }
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(2)
            print(f"Attempt {attempt + 1} for {ticker}")
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'historical' not in data or not data['historical']:
                print(f"No data available for {ticker}")
                return None
            df = pd.DataFrame(data['historical'])
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            if df.empty:
                print(f"No data in specified date range for {ticker}")
                return None
            df = df.sort_values('date')
            df['Ticker'] = ticker
            # Rinomina solo le colonne che esistono
            rename_map = {k: v for k, v in {
                'date': 'Date',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }.items() if k in df.columns}
            df.rename(columns=rename_map, inplace=True)
            # Calcola metriche solo se le colonne esistono
            if 'Close' in df.columns:
                df['Daily_Return'] = df['Close'].pct_change()
                df['Volatility'] = df['Daily_Return'].rolling(window=20).std()
                df['MA50'] = df['Close'].rolling(window=50).mean()
                df['MA200'] = df['Close'].rolling(window=200).mean()
            if 'Volume' in df.columns:
                df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
            print(f"Successfully fetched data for {ticker}")
            return df
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed for {ticker}: {str(e)}")
            if attempt == max_retries - 1:
                print(f"All attempts failed for {ticker}")
                return None
        except Exception as e:
            print(f"Unexpected error for {ticker}: {str(e)}")
            if attempt == max_retries - 1:
                print(f"All attempts failed for {ticker}")
                return None

def main():
    # Log start of execution
    logger.log_execution("fetch_historical_prices.py", "started", {"function": "main"})
    
    try:
        os.makedirs('data', exist_ok=True)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        tickers = load_portfolio()
        all_data = []
        failed_tickers = []
        
        for ticker in tickers:
            print(f"\nFetching historical data for {ticker}...")
            hist_data = fetch_historical_data(ticker, start_date, end_date)
            if hist_data is not None:
                all_data.append(hist_data)
            else:
                failed_tickers.append(ticker)
            time.sleep(0.5)
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.sort_values(['Date', 'Ticker'])
            output_file = os.path.join('data', 'historical_prices.csv')
            combined_data.to_csv(output_file, index=False)
            print(f"\nHistorical data saved to {output_file}")
            
            # Calcola summary solo sulle colonne esistenti
            summary_cols = {k: v for k, v in {
                'Close': ['last', 'mean', 'std', 'min', 'max'],
                'Volume': 'mean',
                'Daily_Return': ['mean', 'std'],
                'Volatility': 'mean'
            }.items() if k in combined_data.columns}
            summary = combined_data.groupby('Ticker').agg(summary_cols).round(4)
            summary_file = os.path.join('data', 'price_summary.json')
            summary.to_json(summary_file)
            print(f"Summary statistics saved to {summary_file}")
            
            if failed_tickers:
                print(f"\nWarning: Failed to fetch data for: {', '.join(failed_tickers)}")
            
            # Log successful completion
            logger.log_execution("fetch_historical_prices.py", "completed", {
                "output_file": output_file,
                "summary_file": summary_file,
                "tickers_processed": len(tickers),
                "tickers_successful": len(tickers) - len(failed_tickers),
                "tickers_failed": len(failed_tickers),
                "failed_tickers": failed_tickers
            })
            
        else:
            error_msg = "Failed to fetch data for all tickers"
            logger.log_execution("fetch_historical_prices.py", "failed", {"error": error_msg})
            print("\nError: No data was fetched successfully for any ticker")
            raise Exception(error_msg)
            
    except Exception as e:
        # Log error
        logger.log_execution("fetch_historical_prices.py", "failed", {"error": str(e)})
        raise e

if __name__ == "__main__":
    main() 