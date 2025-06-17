import os
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.graph_objects as go
from flask import Flask, render_template, jsonify, request
from stock_news import StockNewsFetcher
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://dollarpunk:dollarpunk@db:5432/dollarpunk')
engine = create_engine(DATABASE_URL)

def init_db():
    """Initialize the database with the schema"""
    with engine.connect() as conn:
        with app.open_resource('schema.sql', mode='r') as f:
            conn.execute(text(f.read()))
            conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock_data')
def get_stock_data():
    try:
        ticker = request.args.get('ticker', 'AAPL')
        
        # Get stock data from database
        query = """
            SELECT date, open, high, low, close, volume 
            FROM stocks 
            WHERE ticker = :ticker 
            ORDER BY date
        """
        df = pd.read_sql_query(
            query,
            engine,
            params={'ticker': ticker},
            parse_dates=['date']
        )
        
        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data found for this ticker'
            }), 404
        
        # Create the plot
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['close'],
                mode='lines+markers',
                name='Close Price',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            )
        )
        
        fig.update_layout(
            title=f'Stock Price for {ticker}',
            yaxis=dict(
                title='Price ($)',
                tickformat='.2f',
                tickprefix='$'
            ),
            xaxis=dict(
                title='Date',
                tickformat='%Y-%m-%d'
            ),
            hovermode='x unified',
            showlegend=True
        )
        
        fig.update_traces(
            hovertemplate='$%{y:.2f}<extra></extra>'
        )
        
        return jsonify({
            'success': True,
            'data': df.to_dict(orient='records'),
            'plot': json.loads(fig.to_json())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news')
def get_news():
    try:
        ticker = request.args.get('ticker', 'AAPL')
        
        # Get news from database
        query = """
            SELECT title, description, url, published_at, source 
            FROM news 
            WHERE ticker = :ticker 
            ORDER BY published_at DESC
            LIMIT 10
        """
        df = pd.read_sql_query(
            query,
            engine,
            params={'ticker': ticker},
            parse_dates=['published_at']
        )
        
        return jsonify({
            'success': True,
            'data': df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tables')
def get_tables():
    """Get information about available tables"""
    try:
        tables = []
        for table_name in ['stocks', 'news']:
            # Get column information
            columns_query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """
            with engine.connect() as conn:
                columns = [row[0] for row in conn.execute(text(columns_query), {'table_name': table_name})]
            
            # Get row count
            count_query = f"SELECT COUNT(*) FROM {table_name}"
            with engine.connect() as conn:
                row_count = conn.execute(text(count_query)).scalar()
            
            tables.append({
                "name": table_name,
                "display_name": "Stock Data" if table_name == "stocks" else "News Articles",
                "columns": columns,
                "row_count": row_count
            })
        
        return jsonify({
            "success": True,
            "tables": tables
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/table_details/<table_name>')
def get_table_details(table_name):
    """Get detailed information about a specific table"""
    try:
        if table_name not in ['stocks', 'news']:
            raise ValueError("Invalid table name")
        
        # Get basic table information
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5", engine)
        
        # Get table statistics
        if table_name == 'stocks':
            stats_query = """
                SELECT 
                    'count' as statistic,
                    COUNT(*)::text as value
                FROM stocks
                UNION ALL
                SELECT 
                    'avg_close' as statistic,
                    ROUND(AVG(close)::numeric, 2)::text as value
                FROM stocks
                UNION ALL
                SELECT 
                    'min_date' as statistic,
                    MIN(date)::text as value
                FROM stocks
                UNION ALL
                SELECT 
                    'max_date' as statistic,
                    MAX(date)::text as value
                FROM stocks
            """
        else:
            stats_query = """
                SELECT 
                    'count' as statistic,
                    COUNT(*)::text as value
                FROM news
                UNION ALL
                SELECT 
                    'sources' as statistic,
                    COUNT(DISTINCT source)::text as value
                FROM news
                UNION ALL
                SELECT 
                    'oldest_article' as statistic,
                    MIN(published_at)::text as value
                FROM news
                UNION ALL
                SELECT 
                    'newest_article' as statistic,
                    MAX(published_at)::text as value
                FROM news
            """
        
        stats_df = pd.read_sql_query(stats_query, engine)
        
        return jsonify({
            "success": True,
            "details": {
                "sample_data": df.to_dict(orient='records'),
                "statistics": stats_df.to_dict(orient='records'),
                "total_rows": len(df),
                "columns": list(df.columns)
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

@app.route('/api/extract', methods=['POST'])
def extract_data():
    """Extract new data for a specific ticker"""
    try:
        ticker = request.json.get('ticker', '').upper()
        days = int(request.json.get('days', 7))
        
        if not ticker:
            return jsonify({'error': 'Ticker is required'}), 400
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format dates
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Initialize fetcher
        fetcher = StockNewsFetcher()
        
        # Get data
        stock_data = fetcher.get_stock_data(ticker, start_str, end_str)
        news_articles = fetcher.get_news(ticker, start_str, end_str)
        
        # Save to database
        if stock_data is not None:
            stock_data['ticker'] = ticker
            stock_data.to_sql('stocks', engine, if_exists='append', index=True, index_label='date')
        
        if news_articles:
            news_df = pd.DataFrame(news_articles)
            news_df['ticker'] = ticker
            news_df.to_sql('news', engine, if_exists='append', index=False)
        
        return jsonify({
            'success': True,
            'message': f'Data extracted successfully for {ticker}',
            'period': f'from {start_str} to {end_str}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create database and tables if they don't exist
    init_db()
    
    app.run(host='0.0.0.0', port=5000, debug=True) 