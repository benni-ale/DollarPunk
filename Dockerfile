FROM python:3.11-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages one by one to better handle dependencies
RUN pip install --no-cache-dir \
    newsapi-python==0.2.7 \
    python-dotenv==1.0.1 \
    requests==2.31.0 \
    tqdm==4.66.1 \
    streamlit==1.29.0 \
    transformers==4.35.2 \
    plotly==5.18.0 \
    yfinance==0.2.36 \
    pandas==2.1.4 \
    && pip install --no-cache-dir torch==2.1.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy application files
COPY . .

# Create data directory and ensure it's writable
RUN mkdir -p data && chmod 777 data

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"] 