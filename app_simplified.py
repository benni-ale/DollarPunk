import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
from dataclasses import dataclass
from typing import List, Dict, Optional
import hashlib
import requests
from newsapi import NewsApiClient
from dotenv import load_dotenv
import yfinance as yf

# Load environment variables
load_dotenv()

# Configurazione pagina
st.set_page_config(
    page_title="DollarPunk - Data Collection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@dataclass
class NewsConfig:
    """Configurazione per la raccolta notizie"""
    tickers: List[str]
    keywords_per_ticker: Dict[str, List[str]]
    sources: List[str]
    date_from: datetime
    date_to: datetime
    max_articles_per_query: int = 100
    delay_between_requests: float = 1.0

class NewsCollector:
    """Sistema ottimizzato per raccolta notizie massive"""
    
    def __init__(self):
        self.db_path = "data/news_database.db"
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        self.init_database()
    
    def init_database(self):
        """Inizializza database SQLite per storage efficiente"""
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella articoli
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                description TEXT,
                content TEXT,
                url TEXT UNIQUE,
                published_at TIMESTAMP,
                source_name TEXT,
                ticker TEXT,
                keywords TEXT,
                sentiment_positive REAL,
                sentiment_negative REAL,
                sentiment_neutral REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabella per tracking delle query
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                ticker TEXT,
                articles_found INTEGER,
                articles_new INTEGER,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indici per performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_ticker ON articles(ticker)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)')
        
        conn.commit()
        conn.close()
    
    def generate_article_id(self, url: str, published_at: str) -> str:
        """Genera ID univoco per articolo"""
        unique_string = f"{url}{published_at}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def article_exists(self, url: str) -> bool:
        """Controlla se articolo esiste già"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE url = ?", (url,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    
    def save_articles(self, articles: List[Dict], ticker: str, keywords: str):
        """Salva articoli nel database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_articles = 0
        for article in articles:
            if not self.article_exists(article['url']):
                cursor.execute('''
                    INSERT INTO articles (
                        id, title, description, content, url, published_at,
                        source_name, ticker, keywords
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.generate_article_id(article['url'], article['publishedAt']),
                    article.get('title', ''),
                    article.get('description', ''),
                    article.get('content', ''),
                    article['url'],
                    article['publishedAt'],
                    article.get('source', {}).get('name', ''),
                    ticker,
                    keywords
                ))
                new_articles += 1
        
        conn.commit()
        conn.close()
        return new_articles
    
    def fetch_news_for_ticker(self, ticker: str, keywords: List[str], config: NewsConfig) -> Dict:
        """Raccoglie notizie per un singolo ticker"""
        start_time = time.time()
        
        try:
            # Costruisci query
            keywords_str = ' OR '.join(f'"{kw}"' for kw in keywords)
            query = f'({keywords_str}) AND (stock OR market OR shares OR company OR earnings)'
            
            # Parametri API
            params = {
                'q': query,
                'language': 'en',
                'from': config.date_from.strftime('%Y-%m-%d'),
                'to': config.date_to.strftime('%Y-%m-%d'),
                'sort_by': 'relevancy',
                'page_size': config.max_articles_per_query
            }
            
            if config.sources:
                params['sources'] = ','.join(config.sources)
            
            # Chiamata API
            response = self.newsapi.get_everything(**params)
            articles = response.get('articles', [])
            
            # Salva articoli
            keywords_str = ','.join(keywords)
            new_articles = self.save_articles(articles, ticker, keywords_str)
            
            execution_time = time.time() - start_time
            
            # Log query
            self.log_query(query, ticker, len(articles), new_articles, execution_time)
            
            return {
                'ticker': ticker,
                'articles_found': len(articles),
                'articles_new': new_articles,
                'execution_time': execution_time,
                'success': True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_query(query, ticker, 0, 0, execution_time)
            
            return {
                'ticker': ticker,
                'articles_found': 0,
                'articles_new': 0,
                'execution_time': execution_time,
                'success': False,
                'error': str(e)
            }
    
    def log_query(self, query: str, ticker: str, articles_found: int, articles_new: int, execution_time: float):
        """Logga i risultati di una query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_log (query, ticker, articles_found, articles_new, execution_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (query, ticker, articles_found, articles_new, execution_time))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Ottiene statistiche del database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Totale articoli
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_articles = cursor.fetchone()[0]
        
        # Articoli per ticker
        cursor.execute("""
            SELECT ticker, COUNT(*) 
            FROM articles 
            GROUP BY ticker 
            ORDER BY COUNT(*) DESC
        """)
        articles_by_ticker = dict(cursor.fetchall())
        
        # Articoli per giorno
        cursor.execute("""
            SELECT DATE(published_at) as date, COUNT(*) 
            FROM articles 
            GROUP BY DATE(published_at) 
            ORDER BY date DESC 
            LIMIT 30
        """)
        articles_by_date = dict(cursor.fetchall())
        
        # Ultime query
        cursor.execute("""
            SELECT ticker, articles_found, articles_new, execution_time, created_at
            FROM query_log 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_queries = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_articles': total_articles,
            'articles_by_ticker': articles_by_ticker,
            'articles_by_date': articles_by_date,
            'recent_queries': recent_queries
        }
    
    def get_articles_sample(self, limit: int = 100) -> pd.DataFrame:
        """Ottiene un campione di articoli per preview"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(f"""
            SELECT title, source_name, ticker, published_at, url
            FROM articles 
            ORDER BY published_at DESC 
            LIMIT {limit}
        """, conn)
        conn.close()
        return df

def main():
    st.title("📊 DollarPunk - Mass Data Collection System")
    
    # Inizializza collector
    if 'collector' not in st.session_state:
        st.session_state.collector = NewsCollector()
    
    # Sidebar semplificata
    st.sidebar.title("🎯 Operations")
    operation = st.sidebar.selectbox(
        "Choose Operation:",
        [
            "📰 Mass News Collection",
            "📊 Data Analytics", 
            "⚙️ Configuration",
            "📋 Recent Activity"
        ]
    )
    
    if operation == "📰 Mass News Collection":
        st.header("📰 Mass News Collection")
        
        # Statistiche attuali
        stats = st.session_state.collector.get_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Articles", f"{stats['total_articles']:,}")
        with col2:
            st.metric("Target", "1,000,000")
        with col3:
            progress = min(stats['total_articles'] / 1_000_000 * 100, 100)
            st.metric("Progress", f"{progress:.1f}%")
        with col4:
            st.metric("Tickers", len(stats['articles_by_ticker']))
        
        # Progress bar
        st.progress(progress / 100)
        
        # Configurazione raccolta
        st.subheader("Collection Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tickers da portfolio
            portfolio = load_json_file('portfolio.json').get('stocks', [])
            selected_tickers = st.multiselect(
                "Select Tickers:",
                options=portfolio,
                default=portfolio[:3],  # Primi 3 di default
                help="Select stocks to collect news for"
            )
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            date_range = st.date_input(
                "Date Range:",
                value=(start_date.date(), end_date.date()),
                help="Select date range for news collection"
            )
        
        with col2:
            # Parametri avanzati
            max_articles = st.number_input(
                "Max Articles per Query:",
                min_value=10,
                max_value=100,
                value=50,
                help="NewsAPI limit is 100 per query"
            )
            
            delay = st.number_input(
                "Delay between requests (seconds):",
                min_value=0.1,
                max_value=5.0,
                value=1.0,
                step=0.1,
                help="Avoid rate limiting"
            )
            
            # Fonti
            sources = st.multiselect(
                "News Sources (optional):",
                options=["bloomberg", "cnbc", "reuters", "wsj", "fortune", "business-insider"],
                help="Leave empty for all sources"
            )
        
        # Avvio raccolta
        if st.button("🚀 Start Mass Collection", type="primary"):
            if not selected_tickers:
                st.error("Please select at least one ticker!")
                return
            
            # Configurazione
            keywords_data = load_json_file('keywords.json')
            config = NewsConfig(
                tickers=selected_tickers,
                keywords_per_ticker=keywords_data,
                sources=sources,
                date_from=datetime.combine(date_range[0], datetime.min.time()),
                date_to=datetime.combine(date_range[1], datetime.max.time()),
                max_articles_per_query=max_articles,
                delay_between_requests=delay
            )
            
            # Avvia raccolta con progress tracking
            run_mass_collection(config)
    
    elif operation == "📊 Data Analytics":
        st.header("📊 Data Analytics")
        
        stats = st.session_state.collector.get_stats()
        
        # Grafico articoli per ticker
        if stats['articles_by_ticker']:
            fig_ticker = px.bar(
                x=list(stats['articles_by_ticker'].keys()),
                y=list(stats['articles_by_ticker'].values()),
                title="Articles by Ticker",
                labels={'x': 'Ticker', 'y': 'Articles Count'}
            )
            st.plotly_chart(fig_ticker, use_container_width=True)
        
        # Grafico articoli per data
        if stats['articles_by_date']:
            dates = list(stats['articles_by_date'].keys())
            counts = list(stats['articles_by_date'].values())
            
            fig_date = px.line(
                x=dates,
                y=counts,
                title="Articles Collection Over Time",
                labels={'x': 'Date', 'y': 'Articles Count'}
            )
            st.plotly_chart(fig_date, use_container_width=True)
        
        # Tabella dettagliata
        st.subheader("Detailed Statistics")
        df_stats = pd.DataFrame([
            {'Ticker': ticker, 'Articles': count}
            for ticker, count in stats['articles_by_ticker'].items()
        ])
        st.dataframe(df_stats, use_container_width=True)
        
        # Preview articoli recenti
        st.subheader("Recent Articles Preview")
        df_recent = st.session_state.collector.get_articles_sample(50)
        st.dataframe(df_recent, use_container_width=True)
    
    elif operation == "⚙️ Configuration":
        st.header("⚙️ Configuration")
        
        # Portfolio management
        st.subheader("Portfolio Management")
        
        current_portfolio = load_json_file('portfolio.json').get('stocks', [])
        new_portfolio = st.text_area(
            "Portfolio Tickers (one per line):",
            value='\n'.join(current_portfolio),
            height=150
        )
        
        if st.button("💾 Save Portfolio"):
            portfolio_data = {
                "stocks": [ticker.strip().upper() for ticker in new_portfolio.split('\n') if ticker.strip()]
            }
            with open('portfolio.json', 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            st.success("Portfolio saved!")
            st.rerun()
        
        # Keywords management
        st.subheader("Keywords Management")
        
        current_keywords = load_json_file('keywords.json')
        keywords_json = st.text_area(
            "Keywords JSON:",
            value=json.dumps(current_keywords, indent=2),
            height=300
        )
        
        if st.button("💾 Save Keywords"):
            try:
                keywords_data = json.loads(keywords_json)
                with open('keywords.json', 'w') as f:
                    json.dump(keywords_data, f, indent=2)
                st.success("Keywords saved!")
                st.rerun()
            except json.JSONDecodeError:
                st.error("Invalid JSON format!")
    
    elif operation == "📋 Recent Activity":
        st.header("📋 Recent Activity")
        
        stats = st.session_state.collector.get_stats()
        
        if stats['recent_queries']:
            # Tabella query recenti
            df_queries = pd.DataFrame(stats['recent_queries'], 
                                    columns=['Ticker', 'Found', 'New', 'Time(s)', 'Created'])
            st.dataframe(df_queries, use_container_width=True)
            
            # Grafico performance
            fig_perf = px.line(
                df_queries,
                x='Created',
                y=['Found', 'New'],
                title="Query Performance Over Time",
                labels={'value': 'Articles', 'variable': 'Type'}
            )
            st.plotly_chart(fig_perf, use_container_width=True)
        else:
            st.info("No recent activity found. Start collecting news to see activity here!")

def run_mass_collection(config: NewsConfig):
    """Esegue raccolta massiva con progress tracking"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    total_queries = len(config.tickers)
    completed_queries = 0
    results = []
    
    with results_container:
        st.subheader("Collection Progress")
        results_table = st.empty()
    
    for ticker in config.tickers:
        status_text.text(f"Collecting news for {ticker}...")
        
        try:
            # Ottieni keywords per questo ticker
            keywords = config.keywords_per_ticker.get(ticker, {}).get('keywords', [ticker])
            
            # Raccogli notizie
            result = st.session_state.collector.fetch_news_for_ticker(
                ticker, keywords, config
            )
            results.append(result)
            
            # Delay tra richieste
            time.sleep(config.delay_between_requests)
            
            # Aggiorna progress
            completed_queries += 1
            progress = completed_queries / total_queries
            progress_bar.progress(progress)
            
            # Aggiorna tabella risultati
            df_results = pd.DataFrame(results)
            if not df_results.empty:
                results_table.dataframe(df_results, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error collecting news for {ticker}: {str(e)}")
            results.append({
                'ticker': ticker,
                'articles_found': 0,
                'articles_new': 0,
                'success': False,
                'error': str(e)
            })
    
    status_text.text("Collection completed!")
    
    # Summary finale
    total_found = sum(r.get('articles_found', 0) for r in results)
    total_new = sum(r.get('articles_new', 0) for r in results)
    successful = sum(1 for r in results if r.get('success', False))
    
    st.success(f"""
    🎉 Collection completed!
    - Processed: {len(config.tickers)} tickers
    - Successful: {successful} queries
    - Total articles found: {total_found:,}
    - New articles added: {total_new:,}
    """)
    
    st.rerun()

def load_json_file(file_path: str) -> dict:
    """Carica file JSON"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

if __name__ == "__main__":
    main() 