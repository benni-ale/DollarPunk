from flask import Flask, render_template, jsonify, request
from pyspark.sql import SparkSession
from delta.tables import DeltaTable
import pandas as pd
import plotly.express as px
import plotly.utils
import json

app = Flask(__name__)

# Inizializza Spark
spark = (SparkSession.builder
    .appName("StockNewsViewer")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock_data')
def get_stock_data():
    ticker = request.args.get('ticker', 'AAPL')
    stock_df = spark.read.format("delta").load("data/stock_data_delta")
    stock_df = stock_df.filter(f"ticker = '{ticker}'")
    
    # Converti in pandas per la visualizzazione
    pdf = stock_df.toPandas()
    
    # Crea il grafico con Plotly
    fig = px.line(pdf, x='Date', y=['Open', 'Close', 'High', 'Low'],
                  title=f'Stock Prices for {ticker}')
    
    return jsonify({
        'data': pdf.to_dict(orient='records'),
        'plot': json.loads(fig.to_json())
    })

@app.route('/api/news')
def get_news():
    ticker = request.args.get('ticker', 'AAPL')
    news_df = spark.read.format("delta").load("data/news_delta")
    news_df = news_df.filter(f"ticker = '{ticker}'")
    
    # Converti in pandas per la visualizzazione
    pdf = news_df.toPandas()
    return jsonify(pdf.to_dict(orient='records'))

@app.route('/api/query', methods=['POST'])
def execute_query():
    query = request.json.get('query', '')
    try:
        # Registra le Delta table come temporary view
        spark.read.format("delta").load("data/stock_data_delta").createOrReplaceTempView("stock_data_delta")
        spark.read.format("delta").load("data/news_delta").createOrReplaceTempView("news_delta")
        # Esegui la query SQL
        result_df = spark.sql(query)
        pdf = result_df.toPandas()
        return jsonify({
            'success': True,
            'data': pdf.to_dict(orient='records'),
            'columns': pdf.columns.tolist()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 