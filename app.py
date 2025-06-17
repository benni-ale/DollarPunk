from flask import Flask, render_template, jsonify, request
from pyspark.sql import SparkSession
from delta.tables import DeltaTable
import pandas as pd
import plotly.express as px
import plotly.utils
import json
from pyspark.sql.types import DateType, TimestampType
import sys
import plotly.graph_objects as go
import os

app = Flask(__name__)

# Inizializza Spark
spark = (SparkSession.builder
    .appName("StockNewsViewer")
    .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0")
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
    
    # Debug: stampa lo schema Spark
    print("Schema Spark:", stock_df.schema, file=sys.stderr)
    
    # Debug: stampa i dati Spark prima del filtro
    print("Dati Spark prima del filtro:", stock_df.show(5), file=sys.stderr)
    
    stock_df = stock_df.filter(f"ticker = '{ticker}'")
    
    # Debug: stampa i dati dopo il filtro
    print("Dati Spark dopo il filtro:", stock_df.show(5), file=sys.stderr)
    
    # Converti le colonne datetime in stringa PRIMA di chiamare toPandas
    for field in stock_df.schema.fields:
        if isinstance(field.dataType, (DateType, TimestampType)):
            stock_df = stock_df.withColumn(field.name, stock_df[field.name].cast("string"))
    
    pdf = stock_df.toPandas()
    
    # Debug: stampa i dati dopo la conversione a Pandas
    print("Dati Pandas dopo la conversione:", file=sys.stderr)
    print(pdf.dtypes, file=sys.stderr)
    print(pdf.head(), file=sys.stderr)
    
    # Forza la colonna Close a numerica mantenendo i valori originali
    pdf['Close'] = pd.to_numeric(pdf['Close'], errors='coerce')
    
    # Debug: stampa i dati dopo la conversione numerica
    print("Dati dopo conversione numerica:", file=sys.stderr)
    print(pdf[['Date', 'Close']].head(), file=sys.stderr)
    
    # Converte e ordina la colonna Date
    pdf['Date'] = pd.to_datetime(pdf['Date'])
    
    # Ordina i dati per data
    pdf = pdf.sort_values('Date')
    
    # Converti i dati in liste
    dates = pdf['Date'].tolist()
    prices = pdf['Close'].tolist()
    
    print("Debug - Date:", dates)
    print("Debug - Prezzi:", prices)
    
    # Crea il grafico solo per il prezzo di chiusura
    fig = go.Figure()
    
    # Aggiungi la traccia con i dati come liste
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=prices,
            mode='lines+markers',
            name='Close Price',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        )
    )
    
    # Configura il layout
    fig.update_layout(
        title=f'Close Price for {ticker}',
        yaxis=dict(
            title='Price ($)',
            tickformat='.2f',
            tickprefix='$',
            range=[min(prices) * 0.99, max(prices) * 1.01]
        ),
        xaxis=dict(
            title='Date',
            tickformat='%Y-%m-%d'
        ),
        hovermode='x unified',
        showlegend=True
    )
    
    # Configura il formato del tooltip
    fig.update_traces(
        hovertemplate='$%{y:.2f}<extra></extra>'
    )
    
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
        # Fix per colonne datetime
        for col in pdf.columns:
            if str(pdf[col].dtype).startswith('datetime64') or str(pdf[col].dtype) == 'object':
                try:
                    pdf[col] = pd.to_datetime(pdf[col])
                except Exception:
                    pass
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

@app.route('/api/tables')
def get_tables():
    """Ottiene la lista delle tabelle Delta disponibili"""
    tables = []
    data_dir = "data"
    
    # Cerca tutte le directory che contengono file _delta_log
    for root, dirs, files in os.walk(data_dir):
        if "_delta_log" in dirs:
            table_name = os.path.basename(root)
            try:
                # Carica la tabella per ottenere lo schema
                delta_table = DeltaTable.forPath(spark, root)
                df = delta_table.toDF()
                schema = df.schema.jsonValue()
                tables.append({
                    "name": table_name,
                    "path": root,
                    "columns": [field["name"] for field in schema["fields"]]
                })
            except Exception as e:
                print(f"Errore nel caricare la tabella {table_name}: {str(e)}")
    
    return jsonify(tables)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 