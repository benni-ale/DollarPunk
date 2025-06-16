from pyspark.sql import SparkSession
import pandas as pd
import json

spark = (SparkSession.builder
    .appName("ReadDelta")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate())

df = spark.read.format("delta").load("data/delta_table_AAPL")

# Mostra schema e prime righe delle colonne principali
print("\n=== SCHEMA DELTA TABLE ===")
df.printSchema()

print("\n=== PRIME RIGHE (ticker, timestamp) ===")
df.select("ticker", "timestamp").show(truncate=False)

# Decodifica e visualizza la colonna news come tabella Pandas (prime 3 news)
print("\n=== ESEMPIO NEWS (prime 3) ===")
first_row = df.select("news").first()
if first_row and first_row.news:
    news_list = json.loads(first_row.news)
    if isinstance(news_list, list) and len(news_list) > 0:
        news_df = pd.DataFrame(news_list[:3])
        print(news_df[[c for c in news_df.columns if c in ["title", "publishedAt", "source", "url"]]])
    else:
        print("Nessuna news trovata.")
else:
    print("Colonna news vuota.")

# Decodifica e visualizza la colonna stock_data come tabella Pandas (prime 5 righe)
print("\n=== ESEMPIO STOCK DATA (prime 5) ===")
first_row = df.select("stock_data").first()
if first_row and first_row.stock_data:
    stock_list = json.loads(first_row.stock_data)
    if isinstance(stock_list, list) and len(stock_list) > 0:
        stock_df = pd.DataFrame(stock_list[:5])
        print(stock_df)
    else:
        print("Nessun dato stock trovato.")
else:
    print("Colonna stock_data vuota.") 