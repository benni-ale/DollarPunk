import yfinance as yf
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import time
from requests.exceptions import RequestException

def load_portfolio():
    """Load stock tickers from portfolio.json"""
    with open('portfolio.json', 'r') as f:
        portfolio = json.load(f)
    return portfolio['stocks']

def fetch_historical_data(ticker, start_date, end_date, max_retries=3):
    """Fetch historical data for a single ticker with retries"""
    for attempt in range(max_retries):
        try:
            # Add delay between attempts
            if attempt > 0:
                time.sleep(2)
            
            print(f"Attempt {attempt + 1} for {ticker}")
            
            # Initialize ticker with session
            stock = yf.Ticker(ticker)
            
            # Force download of info to verify ticker validity
            info = stock.info
            if not info:
                print(f"No info available for {ticker}, might be delisted")
                return None
            
            # Get history with progress=False to avoid TQDM output
            hist = stock.history(
                start=start_date, 
                end=end_date, 
                interval='1d',
                progress=False,
                timeout=10
            )
            
            if hist.empty:
                print(f"No historical data available for {ticker}")
                return None
            
            # Reset index to make Date a column
            hist = hist.reset_index()
            
            # Add ticker column
            hist['Ticker'] = ticker
            
            # Calculate daily returns
            hist['Daily_Return'] = hist['Close'].pct_change()
            
            # Calculate volatility (20-day rolling standard deviation of returns)
            hist['Volatility'] = hist['Daily_Return'].rolling(window=20).std()
            
            # Calculate moving averages
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            hist['MA200'] = hist['Close'].rolling(window=200).mean()
            
            # Calculate trading volume moving average
            hist['Volume_MA20'] = hist['Volume'].rolling(window=20).mean()
            
            print(f"Successfully fetched data for {ticker}")
            return hist
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed for {ticker}: {str(e)}")
            if attempt == max_retries - 1:
                print(f"All attempts failed for {ticker}")
                return None

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Set date range (5 years from today)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    # Load portfolio
    tickers = load_portfolio()
    
    # Fetch data for all tickers
    all_data = []
    failed_tickers = []
    
    for ticker in tickers:
        print(f"\nFetching historical data for {ticker}...")
        hist_data = fetch_historical_data(ticker, start_date, end_date)
        if hist_data is not None:
            all_data.append(hist_data)
        else:
            failed_tickers.append(ticker)
    
    if all_data:
        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Sort by Date and Ticker
        combined_data = combined_data.sort_values(['Date', 'Ticker'])
        
        # Save to CSV
        output_file = os.path.join('data', 'historical_prices.csv')
        combined_data.to_csv(output_file, index=False)
        print(f"\nHistorical data saved to {output_file}")
        
        # Save summary statistics
        summary = combined_data.groupby('Ticker').agg({
            'Close': ['last', 'mean', 'std', 'min', 'max'],
            'Volume': 'mean',
            'Daily_Return': ['mean', 'std'],
            'Volatility': 'mean'
        }).round(4)
        
        summary_file = os.path.join('data', 'price_summary.json')
        summary.to_json(summary_file)
        print(f"Summary statistics saved to {summary_file}")
        
        if failed_tickers:
            print(f"\nWarning: Failed to fetch data for: {', '.join(failed_tickers)}")
    else:
        print("\nError: No data was fetched successfully for any ticker")
        raise Exception("Failed to fetch data for all tickers")

if __name__ == "__main__":
    main() 