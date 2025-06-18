FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fetch_news.py .
COPY schema.sql .

CMD ["python", "fetch_news.py"] 