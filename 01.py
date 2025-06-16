import yfinance as yf
import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# 1. Scarica notizie simulate
news = [
    "Stock prices soared today after strong earnings reports.",
    "Markets fell sharply due to global economic uncertainty.",
    "Investors remain neutral ahead of the Fed meeting."
]
dates = ["2024-06-10", "2024-06-11", "2024-06-12"]

# 2. Calcola sentiment con VADER
analyzer = SentimentIntensityAnalyzer()
sentiment_scores = [analyzer.polarity_scores(text)['compound'] for text in news]

sentiment_df = pd.DataFrame({
    'date': pd.to_datetime(dates),
    'sentiment': sentiment_scores
})

# 3. Scarica prezzi azionari (es: Apple)
data = yf.download("AAPL", start="2024-06-09", end="2024-06-14")
data = data.reset_index()  # Reset index first
data = data[['Date', 'Close']]  # Now select columns
data['return'] = np.log(data['Close'] / data['Close'].shift(1))
# 4. Unisci sentiment e rendimento
merged = pd.merge(sentiment_df, data, left_on='date', right_on='Date', how='inner')
print(merged[['date', 'sentiment', 'return']])
