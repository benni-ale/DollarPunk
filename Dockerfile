FROM python:3.11-slim

# Imposta directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia codice applicazione
COPY app_simplified.py .
COPY portfolio.json .
COPY keywords.json .
COPY test_collection.py .

# Crea directory per i dati
RUN mkdir -p data

# Esponi porta Streamlit
EXPOSE 8501

# Comando di avvio
CMD ["streamlit", "run", "app_simplified.py", "--server.port=8501", "--server.address=0.0.0.0"] 