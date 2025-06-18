FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY fetch_news.py .
COPY portfolio.json .
COPY keywords.json .

# Create data directory
RUN mkdir -p data

CMD ["python", "fetch_news.py"] 