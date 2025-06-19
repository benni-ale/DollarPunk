# 🤑 DollarPunk - Dashboard di Analisi Finanziaria

## 📋 Panoramica

DollarPunk è un'applicazione web completa per l'analisi finanziaria che combina dati storici dei prezzi azionari, notizie finanziarie e analisi del sentiment per fornire insights approfonditi su un portafoglio di azioni. L'applicazione è costruita con Streamlit e utilizza API esterne per raccogliere dati in tempo reale.

## 🏗️ Architettura del Sistema

### Componenti Principali

1. **Dashboard Web (Streamlit)**: Interfaccia utente principale con 5 sezioni operative
2. **Fetcher di Notizie**: Raccolta automatica di notizie finanziarie tramite NewsAPI
3. **Analizzatore di Sentiment**: Analisi del sentiment delle notizie tramite FinBERT
4. **Fetcher di Prezzi Storici**: Raccolta dati storici tramite Financial Modeling Prep API
5. **Sistema di Containerizzazione**: Docker per deployment semplificato

### Stack Tecnologico

- **Frontend**: Streamlit 1.29.0
- **Backend**: Python 3.11
- **Machine Learning**: Transformers (FinBERT), PyTorch
- **Visualizzazione**: Plotly 5.18.0
- **Dati**: Pandas, YFinance
- **API**: NewsAPI, Financial Modeling Prep
- **Containerizzazione**: Docker, Docker Compose

## 📁 Struttura del Progetto

```
DollarPunk/
├── app.py                          # Dashboard principale Streamlit
├── fetch_news.py                   # Fetcher di notizie finanziarie
├── sentiment_analysis.py           # Analisi del sentiment con FinBERT
├── fetch_historical_prices.py      # Fetcher di prezzi storici
├── portfolio.json                  # Configurazione portafoglio
├── keywords.json                   # Keywords per ricerca notizie
├── requirements.txt                # Dipendenze Python
├── Dockerfile                      # Configurazione Docker
├── docker-compose.yml              # Orchestrazione container
├── start.sh                        # Script di avvio
├── data/                           # Directory dati
│   ├── historical_prices.csv       # Dati storici prezzi
│   ├── portfolio_news_*.json       # Notizie raccolte
│   └── portfolio_news_*_sentiment.json  # Notizie con sentiment
└── README.md                       # Documentazione
```

## 🚀 Installazione e Setup

### Prerequisiti

- Docker e Docker Compose
- Chiavi API per:
  - NewsAPI (https://newsapi.org/)
  - Financial Modeling Prep (https://financialmodelingprep.com/)

### Configurazione

1. **Clona il repository**:
   ```bash
   git clone <repository-url>
   cd DollarPunk
   ```

2. **Crea il file `.env`**:
   ```bash
   NEWS_API_KEY=your_newsapi_key_here
   FMP_KEY=your_financial_modeling_prep_key_here
   ```

3. **Configura il portafoglio** (opzionale):
   Modifica `portfolio.json` per includere i tuoi ticker preferiti:
   ```json
   {
     "stocks": ["TSLA", "AAPL", "NVDA", "MSFT", "GOOGL"]
   }
   ```

4. **Configura le keywords** (opzionale):
   Modifica `keywords.json` per personalizzare la ricerca notizie per ogni stock.

### Avvio con Docker

```bash
# Build e avvio del container
docker-compose up --build

# Accesso all'applicazione
# Apri http://localhost:8501 nel browser
```

### Avvio Locale (senza Docker)

```bash
# Installa dipendenze
pip install -r requirements.txt

# Avvia l'applicazione
streamlit run app.py
```

## 📊 Funzionalità Principali

### 1. 📈 Analisi Storica (Historical Analysis)

**Descrizione**: Analisi completa dei dati storici dei prezzi azionari con visualizzazioni interattive.

**Funzionalità**:
- Grafici multi-metrica (Close, Volume, Daily Return, Volatility, MA50, MA200)
- Filtri per ticker e metriche
- Statistiche riassuntive per ogni stock
- Matrice di correlazione tra prezzi
- Tabella dati raw con filtri temporali

**Metriche Calcolate**:
- `Daily_Return`: Variazione percentuale giornaliera
- `Volatility`: Volatilità rolling 20 giorni
- `MA50`: Media mobile 50 giorni
- `MA200`: Media mobile 200 giorni
- `Volume_MA20`: Media mobile volume 20 giorni

### 2. 📰 Raccolta Notizie (Fetch News)

**Descrizione**: Raccolta automatica di notizie finanziarie per ogni stock nel portafoglio.

**Processo**:
1. Carica ticker da `portfolio.json`
2. Carica keywords da `keywords.json`
3. Esegue query su NewsAPI per ogni stock
4. Salva notizie organizzate per ticker in `data/portfolio_news_YYYYMMDD_HHMMSS.json`

**Configurazione Keywords**:
```json
{
  "TSLA": {
    "company": "Tesla",
    "keywords": ["Tesla", "Elon Musk", "Cybertruck", "Model S"]
  }
}
```

### 3. 🎭 Analisi Sentiment (Sentiment Analysis)

**Descrizione**: Analisi del sentiment delle notizie utilizzando il modello FinBERT.

**Processo**:
1. Carica modello FinBERT pre-addestrato
2. Analizza titolo + descrizione di ogni articolo
3. Calcola probabilità per sentiment (positive, negative, neutral)
4. Salva risultati in file con suffisso `_sentiment.json`

**Output Sentiment**:
```json
{
  "sentiment_positive": 0.85,
  "sentiment_negative": 0.10,
  "sentiment_neutral": 0.05,
  "sentiment_label": "positive"
}
```

### 4. 📊 Visualizzazione Risultati (View Results)

**Descrizione**: Dashboard per visualizzare notizie e sentiment analizzati.

**Funzionalità**:
- Selezione file notizie da analizzare
- Visualizzazione articoli per ticker
- Filtri per sentiment e data
- Calcolo sentiment medio per ticker
- Grafici sentiment over time

### 5. 📈 Confronto Cambiamenti (Compare Changes)

**Descrizione**: Confronto tra diverse sessioni di analisi per tracciare cambiamenti.

**Funzionalità**:
- Selezione di due file di notizie
- Confronto sentiment tra sessioni
- Analisi variazioni percentuali
- Identificazione trend sentiment

## 🔧 Configurazione Avanzata

### Personalizzazione Portfolio

Modifica `portfolio.json` per includere i tuoi stock preferiti:

```json
{
  "stocks": [
    "TSLA", "AAPL", "NVDA", "MSFT", "GOOGL",
    "AMZN", "META", "NFLX", "AMD", "INTC"
  ]
}
```

### Personalizzazione Keywords

Modifica `keywords.json` per ottimizzare la ricerca notizie:

```json
{
  "TSLA": {
    "company": "Tesla Inc.",
    "keywords": [
      "Tesla", "Elon Musk", "Tesla Motors",
      "Cybertruck", "Model S", "Model 3", "Model Y",
      "Tesla Autopilot", "Tesla Energy"
    ]
  }
}
```

### Configurazione Docker

Modifica `docker-compose.yml` per personalizzare risorse:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # CPU cores
      memory: 16G      # RAM massima
    reservations:
      memory: 12G      # RAM minima
```

## 📊 Struttura Dati

### File Notizie (`portfolio_news_*.json`)

```json
{
  "metadata": {
    "generated_at": "2025-01-18T10:45:33.123456",
    "source_api": "NewsAPI",
    "api_version": "v2",
    "stocks_count": 5,
    "total_articles": 47
  },
  "stocks": {
    "TSLA": [
      {
        "title": "Tesla Q4 Earnings Beat Expectations",
        "description": "Tesla reported strong Q4 results...",
        "url": "https://example.com/article",
        "publishedAt": "2025-01-18T09:00:00Z",
        "ticker": "TSLA",
        "company": "Tesla",
        "id": "abc123def456",
        "data_source": {
          "api": "NewsAPI",
          "version": "v2",
          "endpoint": "everything",
          "fetch_timestamp": "2025-01-18T10:45:33.123456"
        }
      }
    ]
  }
}
```

### File Sentiment (`portfolio_news_*_sentiment.json`)

```json
{
  "metadata": { ... },
  "stocks": {
    "TSLA": [
      {
        "title": "Tesla Q4 Earnings Beat Expectations",
        "description": "Tesla reported strong Q4 results...",
        "sentiment_positive": 0.85,
        "sentiment_negative": 0.10,
        "sentiment_neutral": 0.05,
        "sentiment_label": "positive"
      }
    ]
  }
}
```

### Dati Storici (`historical_prices.csv`)

| Date | Ticker | Open | High | Low | Close | Volume | Daily_Return | Volatility | MA50 | MA200 | Volume_MA20 |
|------|--------|------|------|-----|-------|--------|--------------|------------|------|-------|-------------|
| 2025-01-17 | TSLA | 215.50 | 218.30 | 214.20 | 217.80 | 45678900 | 0.0123 | 0.0234 | 220.15 | 198.45 | 42345678 |

## 🔍 Troubleshooting

### Problemi Comuni

1. **Errore API Key**:
   ```
   Error: NEWS_API_KEY not found in .env file
   ```
   **Soluzione**: Verifica che il file `.env` contenga le chiavi API corrette.

2. **Errore Memoria Docker**:
   ```
   Container killed due to memory limit
   ```
   **Soluzione**: Aumenta il limite di memoria in `docker-compose.yml`.

3. **Errore Modello FinBERT**:
   ```
   Error loading FinBERT model
   ```
   **Soluzione**: Verifica connessione internet per download modello.

4. **Nessun Dato Storico**:
   ```
   No historical data found
   ```
   **Soluzione**: Verifica chiave FMP_KEY e connessione API.

### Log e Debug

- **Log Streamlit**: Visibili nel terminale durante l'esecuzione
- **Log Docker**: `docker-compose logs app`
- **File di Output**: Controlla la directory `data/` per file generati

## 🔒 Sicurezza

### Best Practices

1. **API Keys**: Non committare mai le chiavi API nel repository
2. **Environment Variables**: Usa sempre file `.env` per configurazioni sensibili
3. **Docker Volumes**: Monta solo le directory necessarie
4. **Resource Limits**: Imposta limiti appropriati per CPU e memoria

### Configurazione Sicura

```bash
# File .env (non committare)
NEWS_API_KEY=your_secure_key_here
FMP_KEY=your_secure_key_here

# .gitignore
.env
data/
*.log
```

## 📈 Roadmap

### Funzionalità Future

- [ ] **Alerting**: Notifiche per eventi significativi
- [ ] **Backtesting**: Test strategie di trading
- [ ] **Machine Learning**: Predizioni prezzo basate su sentiment
- [ ] **API REST**: Endpoint per integrazione esterna
- [ ] **Database**: Persistenza dati in PostgreSQL
- [ ] **Real-time**: Aggiornamenti in tempo reale
- [ ] **Multi-portfolio**: Gestione multipli portafogli
- [ ] **Export**: Esportazione dati in Excel/CSV

### Miglioramenti Tecnici

- [ ] **Caching**: Cache Redis per performance
- [ ] **Async**: Elaborazione asincrona notizie
- [ ] **Monitoring**: Prometheus/Grafana per metriche
- [ ] **CI/CD**: Pipeline automatizzata
- [ ] **Testing**: Test unitari e integrazione

## 🤝 Contributi

### Come Contribuire

1. Fork del repository
2. Crea branch per feature (`git checkout -b feature/nuova-funzionalita`)
3. Commit delle modifiche (`git commit -am 'Aggiunge nuova funzionalità'`)
4. Push del branch (`git push origin feature/nuova-funzionalita`)
5. Crea Pull Request

### Standard di Codice

- **Python**: PEP 8 compliance
- **Documentazione**: Docstring per tutte le funzioni
- **Testing**: Test per nuove funzionalità
- **Commit**: Messaggi descrittivi in inglese

## 📄 Licenza

Questo progetto è rilasciato sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 👥 Autori

- **Sviluppatore**: [Il tuo nome]
- **Email**: [tua.email@example.com]
- **GitHub**: [@tuo-username]

## 🙏 Ringraziamenti

- **NewsAPI**: Per l'accesso alle notizie finanziarie
- **Financial Modeling Prep**: Per i dati storici dei prezzi
- **Hugging Face**: Per il modello FinBERT
- **Streamlit**: Per il framework web
- **Plotly**: Per le visualizzazioni interattive

---

**Nota**: Questo progetto è a scopo educativo e di ricerca. Non costituisce consiglio finanziario. Sempre fare le proprie ricerche prima di investire. 