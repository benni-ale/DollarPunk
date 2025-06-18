#!/bin/bash

echo "Updating historical data..."
python fetch_historical_prices.py

echo "Starting Streamlit..."
streamlit run app.py --server.address 0.0.0.0 