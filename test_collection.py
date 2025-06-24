#!/usr/bin/env python3
"""
Script di test per il sistema di raccolta notizie DollarPunk
Verifica che tutte le componenti funzionino correttamente
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient

# Aggiungi il path corrente per importare i moduli
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_environment():
    """Testa la configurazione dell'ambiente"""
    print("🔧 Testing Environment Configuration...")
    
    # Test .env file
    load_dotenv()
    news_api_key = os.getenv('NEWS_API_KEY')
    fmp_key = os.getenv('FMP_KEY')
    
    if not news_api_key:
        print("❌ NEWS_API_KEY not found in .env file")
        return False
    else:
        print("✅ NEWS_API_KEY found")
    
    if not fmp_key:
        print("⚠️  FMP_KEY not found (optional for news collection)")
    else:
        print("✅ FMP_KEY found")
    
    return True

def test_files():
    """Testa l'esistenza dei file di configurazione"""
    print("\n📁 Testing Configuration Files...")
    
    required_files = ['portfolio.json', 'keywords.json']
    optional_files = ['requirements.txt', 'app.py', 'app_simplified.py']
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    for file in optional_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"⚠️  {file} missing (optional)")
    
    return True

def test_portfolio_config():
    """Testa la configurazione del portfolio"""
    print("\n📊 Testing Portfolio Configuration...")
    
    try:
        with open('portfolio.json', 'r') as f:
            portfolio = json.load(f)
        
        stocks = portfolio.get('stocks', [])
        if not stocks:
            print("❌ No stocks found in portfolio.json")
            return False
        
        print(f"✅ Portfolio loaded with {len(stocks)} stocks: {', '.join(stocks)}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading portfolio.json: {e}")
        return False

def test_keywords_config():
    """Testa la configurazione delle keywords"""
    print("\n🔍 Testing Keywords Configuration...")
    
    try:
        with open('keywords.json', 'r') as f:
            keywords = json.load(f)
        
        if not keywords:
            print("❌ No keywords found in keywords.json")
            return False
        
        print(f"✅ Keywords loaded for {len(keywords)} tickers")
        for ticker, data in keywords.items():
            company = data.get('company', 'Unknown')
            kw_count = len(data.get('keywords', []))
            print(f"   - {ticker} ({company}): {kw_count} keywords")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading keywords.json: {e}")
        return False

def test_newsapi_connection():
    """Testa la connessione a NewsAPI"""
    print("\n🌐 Testing NewsAPI Connection...")
    
    try:
        load_dotenv()
        newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
        # Test semplice query
        response = newsapi.get_everything(
            q='Tesla',
            language='en',
            from_param=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            sort_by='relevancy',
            page_size=5
        )
        
        articles = response.get('articles', [])
        print(f"✅ NewsAPI connection successful - Found {len(articles)} articles for 'Tesla'")
        
        if articles:
            print(f"   Sample article: {articles[0].get('title', 'No title')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ NewsAPI connection failed: {e}")
        return False

def test_database():
    """Testa il database SQLite"""
    print("\n🗄️ Testing Database...")
    
    try:
        # Crea directory data se non esiste
        os.makedirs('data', exist_ok=True)
        
        # Test connessione database
        db_path = "data/news_database.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test creazione tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                test_field TEXT
            )
        ''')
        
        # Test inserimento
        cursor.execute('INSERT INTO test_table (test_field) VALUES (?)', ('test_value',))
        
        # Test lettura
        cursor.execute('SELECT * FROM test_table')
        result = cursor.fetchone()
        
        # Cleanup
        cursor.execute('DROP TABLE test_table')
        conn.commit()
        conn.close()
        
        if result and result[1] == 'test_value':
            print("✅ Database operations successful")
            return True
        else:
            print("❌ Database test failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_streamlit_imports():
    """Testa gli import di Streamlit"""
    print("\n📱 Testing Streamlit Imports...")
    
    try:
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        print("✅ All Streamlit dependencies imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def run_performance_test():
    """Esegue un test di performance"""
    print("\n⚡ Running Performance Test...")
    
    try:
        from app_simplified import NewsCollector, NewsConfig
        
        # Inizializza collector
        collector = NewsCollector()
        
        # Test configurazione
        config = NewsConfig(
            tickers=['TSLA'],
            keywords_per_ticker={'TSLA': {'keywords': ['Tesla', 'Elon Musk']}},
            sources=[],
            date_from=datetime.now() - timedelta(days=7),
            date_to=datetime.now(),
            max_articles_per_query=10,
            delay_between_requests=0.1
        )
        
        # Test raccolta singola
        start_time = datetime.now()
        result = collector.fetch_news_for_ticker('TSLA', ['Tesla'], config)
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Performance test completed in {execution_time:.2f} seconds")
        print(f"   - Articles found: {result.get('articles_found', 0)}")
        print(f"   - New articles: {result.get('articles_new', 0)}")
        print(f"   - Success: {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 DollarPunk Collection System - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment", test_environment),
        ("Files", test_files),
        ("Portfolio Config", test_portfolio_config),
        ("Keywords Config", test_keywords_config),
        ("NewsAPI Connection", test_newsapi_connection),
        ("Database", test_database),
        ("Streamlit Imports", test_streamlit_imports),
        ("Performance", run_performance_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 To start the application:")
        print("   streamlit run app_simplified.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues before using the system.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 