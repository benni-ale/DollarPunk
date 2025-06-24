# 🚀 DollarPunk - Sistema di Raccolta Massiva Dati

## 📋 Panoramica

**DollarPunk** è un sistema ottimizzato per raccogliere **1 milione di articoli** finanziari in modo efficiente. Utilizza Docker per un deployment semplice e veloce.

### ✨ Caratteristiche Principali

- **🎯 Obiettivo**: 1,000,000+ articoli distinti
- **🗄️ Storage**: Database SQLite ottimizzato
- **🔄 Deduplicazione**: Automatica per URL
- **📊 GUI**: Streamlit semplificata con 4 sezioni
- **🐳 Docker**: Deployment containerizzato
- **📈 Progress Tracking**: Monitoraggio in tempo reale

## 🚀 Avvio Rapido con Docker

### Prerequisiti

- **Docker Desktop** installato
- **NewsAPI key** (gratuita su https://newsapi.org/)

### 1. Clona e Configura

```bash
git clone <repository-url>
cd DollarPunk
```

### 2. Configura API Key

Crea il file `.env`:
```bash
NEWS_API_KEY=your_newsapi_key_here
FMP_KEY=your_financial_modeling_prep_key_here  # Opzionale
```

### 3. Avvia con Docker

**Windows:**
```bash
start_docker.bat
```

**Linux/Mac:**
```bash
chmod +x start_docker.sh
./start_docker.sh
```

**Manuale:**
```bash
docker-compose up --build
```

### 4. Accedi all'Applicazione

Apri http://localhost:8501 nel browser

## 📱 Utilizzo

### 4 Sezioni Principali

#### 1. 📰 Mass News Collection
- **Progress tracking** verso 1M articoli
- **Configurazione raccolta** (tickers, date, fonti)
- **Avvio raccolta massiva** con progress bar
- **Risultati in tempo reale**

#### 2. 📊 Data Analytics
- **Grafici articoli per ticker**
- **Trend temporali** di raccolta
- **Statistiche dettagliate**
- **Preview articoli recenti**

#### 3. ⚙️ Configuration
- **Gestione portfolio** (aggiungi/rimuovi tickers)
- **Gestione keywords** (modifica JSON)
- **Salvataggio configurazioni**

#### 4. 📋 Recent Activity
- **Log query recenti**
- **Performance tracking**
- **Grafici performance**

## 🎯 Strategia per 1M Articoli

### Raccolta Incrementale

1. **Giornaliera**: 30 giorni × 5 tickers × 50 articoli = 7,500 articoli
2. **Settimanale**: 52 settimane × 10 tickers × 100 articoli = 52,000 articoli
3. **Mensile**: 12 mesi × 20 tickers × 200 articoli = 48,000 articoli
4. **Storica**: Raccolta retroattiva per 2 anni = ~500,000 articoli

### Ottimizzazioni

- **Deduplicazione automatica** per URL
- **Rate limiting** intelligente (1-2 secondi tra richieste)
- **Storage efficiente** con indici SQLite
- **Progress tracking** in tempo reale

## 🐳 Comandi Docker

### Gestione Container

```bash
# Avvia applicazione
docker-compose up -d

# Visualizza log
docker-compose logs -f

# Ferma applicazione
docker-compose down

# Rebuild e riavvia
docker-compose up --build -d

# Accesso al container
docker-compose exec dollarpunk bash
```

### Backup Dati

```bash
# Backup database
docker cp dollarpunk:/app/data/news_database.db ./backup/

# Backup configurazioni
docker cp dollarpunk:/app/portfolio.json ./backup/
docker cp dollarpunk:/app/keywords.json ./backup/
```

## 📊 Monitoraggio

### Metriche Chiave

- **Total Articles**: Articoli totali nel database
- **Target**: 1,000,000 articoli
- **Progress**: Percentuale completamento
- **Tickers**: Numero tickers con dati

### Dashboard Analytics

- **Articles by Ticker**: Distribuzione per stock
- **Collection Over Time**: Trend temporali
- **Query Performance**: Efficienza raccolta
- **Recent Activity**: Log ultime operazioni

## 🔧 Configurazione

### Portfolio (portfolio.json)
```json
{
  "stocks": [
    "TSLA", "AAPL", "NVDA", "MSFT", "GOOGL",
    "AMZN", "META", "NFLX", "AMD", "INTC"
  ]
}
```

### Keywords (keywords.json)
```json
{
  "TSLA": {
    "company": "Tesla",
    "keywords": ["Tesla", "Elon Musk", "Cybertruck", "Model S"]
  },
  "AAPL": {
    "company": "Apple", 
    "keywords": ["Apple", "iPhone", "Tim Cook", "MacBook"]
  }
}
```

## 🚨 Troubleshooting

### Errori Comuni

1. **Porta 8501 occupata**
   ```bash
   # Cambia porta in docker-compose.yml
   ports:
     - "8502:8501"  # Usa porta 8502
   ```

2. **Database locked**
   ```bash
   # Rimuovi lock file
   rm data/news_database.db-journal
   ```

3. **Rate limiting**
   ```bash
   # Aumenta delay in app_simplified.py
   delay = 2.0  # secondi
   ```

### Log e Debug

```bash
# Log applicazione
docker-compose logs -f dollarpunk

# Accesso database
docker-compose exec dollarpunk sqlite3 data/news_database.db

# Statistiche articoli
docker-compose exec dollarpunk sqlite3 data/news_database.db "SELECT ticker, COUNT(*) FROM articles GROUP BY ticker;"
```

## 📈 Roadmap

### Fase 2: Analisi Avanzata
- **Sentiment analysis** automatica
- **Topic modeling** delle notizie
- **Correlazione** sentiment-prezzi
- **Alert system** per eventi significativi

### Fase 3: Machine Learning
- **Modelli predittivi** basati su sentiment
- **Classificazione** automatica notizie
- **Anomaly detection** per eventi anomali
- **Recommendation system** per trading

### Fase 4: Scalabilità
- **Database PostgreSQL** per volumi maggiori
- **API REST** per integrazione esterna
- **Real-time streaming** di notizie
- **Distributed processing** con Apache Kafka

## 📞 Supporto

Per problemi o domande:
1. Controlla i log: `docker-compose logs -f`
2. Verifica configurazione in `.env`, `portfolio.json`, `keywords.json`
3. Controlla spazio disco: `docker system df`

---

**🎯 Obiettivo: 1,000,000 articoli raccolti!** 