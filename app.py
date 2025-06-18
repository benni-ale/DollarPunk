import streamlit as st
import json
import os
from datetime import datetime
import glob
from fetch_news import fetch_and_save_news
from sentiment_analysis import process_json_file, load_finbert

st.set_page_config(page_title="DollarPunk Dashboard", layout="wide")

def load_json_file(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def main():
    st.title("🤑 DollarPunk Dashboard")
    
    # Sidebar for operation selection
    st.sidebar.title("Operations")
    operation = st.sidebar.radio(
        "Select Operation",
        ["📰 Fetch News", "🎭 Analyze Sentiment", "📊 View Results"]
    )
    
    if operation == "📰 Fetch News":
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