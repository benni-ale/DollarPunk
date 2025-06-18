import streamlit as st
import json
import os
from datetime import datetime
import glob
from fetch_news import fetch_and_save_news
from sentiment_analysis import process_json_file, load_finbert
from fetch_historical_prices import main as fetch_historical_prices
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="DollarPunk Dashboard", layout="wide")

def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def calculate_sentiment_score(article):
    """Calculate a single sentiment score from the sentiment probabilities"""
    if 'sentiment_positive' in article:
        return (article['sentiment_positive'] - article['sentiment_negative'])
    return 0

def get_average_sentiment(data, ticker):
    """Calculate average sentiment for a specific ticker"""
    if 'stocks' not in data or ticker not in data['stocks']:
        return 0
    
    sentiments = [calculate_sentiment_score(article) for article in data['stocks'][ticker]]
    return sum(sentiments) / len(sentiments) if sentiments else 0

def calculate_percentage_change(value1, value2):
    """Calculate percentage change between two values"""
    if value1 == 0:
        return 0
    return ((value2 - value1) / abs(value1)) * 100

def main():
    st.title("🤑 DollarPunk Dashboard")
    
    # Sidebar for operation selection
    st.sidebar.title("Operations")
    operation = st.sidebar.radio(
        "Select Operation",
        ["📈 Historical Analysis", "📰 Fetch News", "🎭 Analyze Sentiment", "📊 View Results", "📈 Compare Changes"]
    )
    
    if operation == "📈 Historical Analysis":
        st.header("Historical Price Analysis")
        
        # Check if historical data exists
        hist_file = 'data/historical_prices.csv'
        if not os.path.exists(hist_file):
            st.error("No historical data found! The data should be automatically updated when the container starts.")
            return
            
        # Load historical data
        df = pd.read_csv(hist_file)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Sidebar controls
        st.sidebar.subheader("Chart Controls")
        selected_tickers = st.sidebar.multiselect(
            "Select Stocks",
            options=df['Ticker'].unique(),
            default=df['Ticker'].unique()
        )
        
        metrics = st.sidebar.multiselect(
            "Select Metrics",
            options=['Close', 'Volume', 'Daily_Return', 'Volatility', 'MA50', 'MA200', 'Volume_MA20'],
            default=['Close', 'MA50', 'MA200']
        )
        
        # Main chart
        if selected_tickers and metrics:
            filtered_df = df[df['Ticker'].isin(selected_tickers)]
            
            # Create figure with secondary y-axis
            fig = make_subplots(
                rows=len(metrics), 
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                subplot_titles=metrics
            )
            
            for i, metric in enumerate(metrics, 1):
                for ticker in selected_tickers:
                    ticker_df = filtered_df[filtered_df['Ticker'] == ticker]
                    fig.add_trace(
                        go.Scatter(
                            x=ticker_df['Date'],
                            y=ticker_df[metric],
                            name=f"{ticker} - {metric}",
                            mode='lines'
                        ),
                        row=i,
                        col=1
                    )
            
            fig.update_layout(
                height=300 * len(metrics),
                showlegend=True,
                title_text="Historical Analysis"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            summary = filtered_df.groupby('Ticker').agg({
                'Close': ['last', 'mean', 'std', 'min', 'max'],
                'Volume': 'mean',
                'Daily_Return': ['mean', 'std'],
                'Volatility': 'mean'
            }).round(4)
            
            st.dataframe(summary)
            
            # Correlation matrix
            st.subheader("Price Correlation Matrix")
            pivot_df = filtered_df.pivot(index='Date', columns='Ticker', values='Close')
            corr_matrix = pivot_df.corr()
            
            fig_corr = px.imshow(
                corr_matrix,
                labels=dict(color="Correlation"),
                color_continuous_scale="RdBu"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
            
            # Tabella interattiva dei dati raw
            st.subheader("Raw Daily Stock Data")
            # Filtro per ticker
            tickers_for_table = st.multiselect(
                "Select Tickers for Table:",
                options=df['Ticker'].unique(),
                default=df['Ticker'].unique(),
                key="table_tickers"
            )
            # Filtro per intervallo di date
            min_date = df['Date'].min()
            max_date = df['Date'].max()
            date_range = st.date_input(
                "Select Date Range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                key="table_dates"
            )
            filtered_table = df[
                (df['Ticker'].isin(tickers_for_table)) &
                (df['Date'] >= pd.to_datetime(date_range[0])) &
                (df['Date'] <= pd.to_datetime(date_range[1]))
            ]
            # Mostra solo le colonne principali se esistono
            main_cols = [c for c in ['Date', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume'] if c in filtered_table.columns]
            st.dataframe(filtered_table[main_cols].sort_values(['Ticker', 'Date']))
            
    elif operation == "📰 Fetch News":
        st.header("Fetch Financial News")
        
        # Load and display current portfolio
        if os.path.exists('portfolio.json'):
            portfolio = load_json_file('portfolio.json')
            st.write("Current Portfolio Stocks:", ", ".join(portfolio))
        
        if st.button("🚀 Fetch Latest News"):
            with st.spinner('Fetching news...'):
                try:
                    output_file = fetch_and_save_news()
                    st.success(f"News fetched successfully! Saved to: {output_file}")
                except Exception as e:
                    st.error(f"Error fetching news: {str(e)}")
    
    elif operation == "🎭 Analyze Sentiment":
        st.header("Sentiment Analysis")
        
        # Find all news files
        json_files = glob.glob('data/*_news_*.json')
        json_files = [f for f in json_files if '_sentiment' not in f]
        
        if not json_files:
            st.warning("No news files found to analyze! Please fetch news first.")
            return
        
        # File selection
        selected_file = st.selectbox(
            "Select news file to analyze:",
            json_files,
            format_func=lambda x: os.path.basename(x)
        )
        
        if st.button("🧠 Run Sentiment Analysis"):
            with st.spinner('Analyzing sentiment... This might take a few minutes...'):
                try:
                    tokenizer, model = load_finbert()
                    output_file = process_json_file(selected_file, tokenizer, model)
                    st.success(f"Sentiment analysis completed! Results saved to: {output_file}")
                except Exception as e:
                    st.error(f"Error during sentiment analysis: {str(e)}")
    
    elif operation == "📈 Compare Changes":
        st.header("Compare Sentiment vs Price Changes")
        
        # Find all sentiment files
        sentiment_files = sorted(glob.glob('data/*_sentiment.json'))
        
        if len(sentiment_files) < 2:
            st.warning("Need at least 2 sentiment files to compare changes!")
            return
            
        col1, col2 = st.columns(2)
        
        with col1:
            file1 = st.selectbox(
                "Select first (earlier) file:",
                sentiment_files[:-1],
                format_func=lambda x: os.path.basename(x)
            )
        
        with col2:
            # Only show files that come after file1
            idx = sentiment_files.index(file1)
            file2 = st.selectbox(
                "Select second (later) file:",
                sentiment_files[idx+1:],
                format_func=lambda x: os.path.basename(x)
            )
        
        if st.button("🔄 Compare Changes"):
            try:
                data1 = load_json_file(file1)
                data2 = load_json_file(file2)
                
                # Get the tickers from portfolio
                portfolio = load_json_file('portfolio.json')
                
                # Calculate changes for each ticker
                changes = []
                
                for ticker in portfolio:
                    # Calculate sentiment changes
                    sentiment1 = get_average_sentiment(data1, ticker)
                    sentiment2 = get_average_sentiment(data2, ticker)
                    sentiment_change = calculate_percentage_change(sentiment1, sentiment2)
                    
                    # Get price changes using yfinance
                    try:
                        stock = yf.Ticker(ticker)
                        # Get dates from filenames
                        date1 = datetime.strptime(file1.split('_')[2], '%Y%m%d')
                        date2 = datetime.strptime(file2.split('_')[2], '%Y%m%d')
                        
                        hist = stock.history(start=date1, end=date2)
                        if not hist.empty:
                            price_change = calculate_percentage_change(
                                hist.iloc[0]['Close'],
                                hist.iloc[-1]['Close']
                            )
                        else:
                            price_change = 0
                            st.warning(f"No price data available for {ticker}")
                    except Exception as e:
                        st.warning(f"Error fetching price data for {ticker}: {str(e)}")
                        price_change = 0
                    
                    changes.append({
                        'Ticker': ticker,
                        'Sentiment Change %': round(sentiment_change, 2),
                        'Price Change %': round(price_change, 2)
                    })
                
                # Create DataFrame and display
                df = pd.DataFrame(changes)
                
                # Display table
                st.subheader("Changes Summary")
                st.dataframe(df.style.format({
                    'Sentiment Change %': '{:,.2f}%',
                    'Price Change %': '{:,.2f}%'
                }))
                
                # Create comparison plot
                fig = px.bar(
                    df,
                    x='Ticker',
                    y=['Sentiment Change %', 'Price Change %'],
                    barmode='group',
                    title='Sentiment vs Price Changes Comparison',
                    labels={'value': 'Change %', 'variable': 'Metric'}
                )
                st.plotly_chart(fig)
                
                # Calculate correlation
                correlation = df['Sentiment Change %'].corr(df['Price Change %'])
                st.metric(
                    "Correlation between Sentiment and Price Changes",
                    f"{correlation:.2f}",
                    help="1 means perfect positive correlation, -1 means perfect negative correlation, 0 means no correlation"
                )
                
            except Exception as e:
                st.error(f"Error comparing changes: {str(e)}")
    
    else:  # View Results
        st.header("View Results")
        
        # Find all files
        all_files = glob.glob('data/*.json')
        if not all_files:
            st.warning("No result files found!")
            return
        
        # File selection
        selected_file = st.selectbox(
            "Select file to view:",
            all_files,
            format_func=lambda x: os.path.basename(x)
        )
        
        # Load and display data
        try:
            data = load_json_file(selected_file)
            
            # Display metadata
            if 'metadata' in data:
                st.subheader("Metadata")
                st.json(data['metadata'])
            
            # Display news with sentiment if available
            if 'stocks' in data:
                st.subheader("News by Stock")
                for ticker, news_list in data['stocks'].items():
                    with st.expander(f"{ticker} ({len(news_list)} articles)"):
                        for article in news_list:
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**{article['title']}**")
                                st.write(article['description'])
                                st.write(f"Source: {article['source']['name']} | Date: {article['publishedAt']}")
                            with col2:
                                if 'sentiment_label' in article:
                                    sentiment_color = {
                                        'positive': 'green',
                                        'negative': 'red',
                                        'neutral': 'gray'
                                    }.get(article['sentiment_label'], 'black')
                                    
                                    st.markdown(f"Sentiment: :{sentiment_color}[{article['sentiment_label']}]")
                                    st.progress(article['sentiment_positive'], text="Positive")
                                    st.progress(article['sentiment_negative'], text="Negative")
                                    st.progress(article['sentiment_neutral'], text="Neutral")
                            st.divider()
                            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

if __name__ == "__main__":
    main() 