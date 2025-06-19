# 📖 DollarPunk - Guida Utente

## 🎯 Introduzione

Benvenuto in DollarPunk! Questa guida ti accompagnerà nell'utilizzo dell'applicazione per l'analisi finanziaria. DollarPunk combina dati storici dei prezzi azionari, notizie finanziarie e analisi del sentiment per fornirti insights approfonditi sul tuo portafoglio.

## 🚀 Primo Avvio

### Accesso all'Applicazione

1. **Avvia l'applicazione**:
   ```bash
   docker-compose up --build
   ```

2. **Apri il browser** e vai su:
   ```
   http://localhost:8501
   ```

3. **Dashboard principale**: Vedrai l'interfaccia principale con 5 sezioni operative nella sidebar.

## 📊 Sezioni dell'Applicazione

### 1. 📈 Analisi Storica (Historical Analysis)

#### Panoramica
Questa sezione ti permette di analizzare i dati storici dei prezzi azionari con visualizzazioni interattive e statistiche dettagliate.

#### Come Utilizzare

1. **Selezione Stock**:
   - Nella sidebar, usa il menu "Select Stocks" per scegliere le azioni da analizzare
   - Puoi selezionare una o più azioni contemporaneamente

2. **Selezione Metriche**:
   - Scegli le metriche da visualizzare:
     - **Close**: Prezzo di chiusura
     - **Volume**: Volume di scambi
     - **Daily_Return**: Rendimento giornaliero
     - **Volatility**: Volatilità (rolling 20 giorni)
     - **MA50**: Media mobile 50 giorni
     - **MA200**: Media mobile 200 giorni
     - **Volume_MA20**: Media mobile volume 20 giorni

3. **Visualizzazioni**:
   - **Grafici Multi-Metrica**: Ogni metrica viene mostrata in un grafico separato
   - **Legenda Interattiva**: Clicca sui nomi delle serie per mostrare/nascondere
   - **Zoom e Pan**: Usa il mouse per zoomare e spostarti nei grafici

4. **Statistiche Riassuntive**:
   - Tabella con statistiche per ogni stock:
     - Ultimo prezzo
     - Prezzo medio
     - Deviazione standard
     - Prezzo minimo e massimo
     - Volume medio
     - Rendimento medio e volatilità

5. **Matrice di Correlazione**:
   - Visualizza la correlazione tra i prezzi delle azioni selezionate
   - Colori: Rosso (correlazione negativa) → Blu (correlazione positiva)

6. **Tabella Dati Raw**:
   - Filtra per ticker e intervallo di date
   - Visualizza i dati grezzi per analisi dettagliate

#### Interpretazione dei Dati

- **MA50 vs MA200**: Quando MA50 > MA200, trend rialzista
- **Volatilità**: Valori alti indicano maggiore rischio
- **Volume**: Aumenti di volume spesso precedono movimenti di prezzo
- **Correlazione**: Valori vicini a 1 indicano movimenti simili

### 2. 📰 Raccolta Notizie (Fetch News)

#### Panoramica
Questa sezione raccoglie automaticamente le ultime notizie finanziarie per ogni stock nel tuo portafoglio.

#### Come Utilizzare

1. **Verifica Portfolio**:
   - L'applicazione mostra automaticamente i ticker nel tuo portafoglio
   - I ticker sono configurati in `portfolio.json`

2. **Avvia Raccolta**:
   - Clicca su "🚀 Fetch Latest News"
   - L'applicazione inizierà a raccogliere notizie per ogni stock
   - Il processo può richiedere alcuni minuti

3. **Monitoraggio**:
   - Una barra di progresso mostra l'avanzamento
   - Messaggi di successo/errore vengono mostrati al completamento

#### Configurazione Keywords

Per ottimizzare la ricerca notizie, puoi modificare `keywords.json`:

```json
{
  "TSLA": {
    "company": "Tesla",
    "keywords": [
      "Tesla", "Elon Musk", "Cybertruck", "Model S", "Model 3"
    ]
  }
}
```

**Suggerimenti per le Keywords**:
- Includi il nome dell'azienda
- Aggiungi nomi di CEO/leader
- Includi prodotti/servizi principali
- Considera acronimi e nomi alternativi

### 3. 🎭 Analisi Sentiment (Sentiment Analysis)

#### Panoramica
Questa sezione analizza il sentiment delle notizie raccolte utilizzando il modello FinBERT, specializzato in analisi finanziaria.

#### Come Utilizzare

1. **Selezione File**:
   - Scegli il file di notizie da analizzare dal menu a tendina
   - I file sono nominati con timestamp: `portfolio_news_YYYYMMDD_HHMMSS.json`

2. **Avvia Analisi**:
   - Clicca su "🧠 Run Sentiment Analysis"
   - Il processo può richiedere 5-10 minuti per file grandi
   - Il modello FinBERT viene caricato automaticamente

3. **Risultati**:
   - Un nuovo file viene creato con suffisso `_sentiment.json`
   - Ogni articolo include:
     - `sentiment_positive`: Probabilità sentiment positivo (0-1)
     - `sentiment_negative`: Probabilità sentiment negativo (0-1)
     - `sentiment_neutral`: Probabilità sentiment neutro (0-1)
     - `sentiment_label`: Etichetta predominante

#### Interpretazione Sentiment

- **Positivo (>0.6)**: Notizie favorevoli per il prezzo
- **Negativo (>0.6)**: Notizie sfavorevoli per il prezzo
- **Neutro**: Notizie bilanciate o non significative
- **Score Composto**: `sentiment_positive - sentiment_negative`

### 4. 📊 Visualizzazione Risultati (View Results)

#### Panoramica
Questa sezione ti permette di esplorare le notizie analizzate e i loro sentiment scores.

#### Come Utilizzare

1. **Selezione File**:
   - Scegli un file con sentiment dal menu a tendina
   - I file hanno suffisso `_sentiment.json`

2. **Filtri**:
   - **Ticker**: Seleziona specifiche azioni
   - **Sentiment**: Filtra per tipo di sentiment
   - **Data**: Seleziona intervallo temporale

3. **Visualizzazioni**:
   - **Lista Articoli**: Visualizza tutti gli articoli con sentiment
   - **Sentiment Medio**: Score medio per ogni ticker
   - **Distribuzione**: Grafico della distribuzione sentiment
   - **Timeline**: Evoluzione sentiment nel tempo

4. **Dettagli Articolo**:
   - Clicca su un articolo per vedere dettagli completi
   - Include titolo, descrizione, URL, sentiment scores

#### Metriche Utili

- **Sentiment Medio per Ticker**: Indica il sentiment generale per ogni stock
- **Distribuzione**: Mostra se le notizie sono prevalentemente positive/negative
- **Trend Temporale**: Identifica cambiamenti nel sentiment nel tempo

### 5. 📈 Confronto Cambiamenti (Compare Changes)

#### Panoramica
Questa sezione ti permette di confrontare sentiment tra diverse sessioni di analisi.

#### Come Utilizzare

1. **Selezione File**:
   - Scegli due file di sentiment da confrontare
   - File 1: Baseline (es. analisi precedente)
   - File 2: Corrente (es. analisi attuale)

2. **Analisi Confronto**:
   - **Variazioni Percentuali**: Cambiamenti nei sentiment scores
   - **Nuovi Articoli**: Articoli presenti solo nel file corrente
   - **Articoli Rimossi**: Articoli presenti solo nel file baseline

3. **Metriche di Confronto**:
   - **Delta Sentiment**: Differenza nei sentiment scores
   - **Trend**: Direzione del cambiamento (miglioramento/peggioramento)
   - **Stabilità**: Consistenza dei sentiment nel tempo

#### Interpretazione Confronti

- **Sentiment Migliorato**: Potenziale segnale rialzista
- **Sentiment Peggiorato**: Potenziale segnale ribassista
- **Stabilità**: Nessun cambiamento significativo
- **Volatilità**: Cambiamenti rapidi nel sentiment

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

Ottimizza la ricerca notizie modificando `keywords.json`:

```json
{
  "TSLA": {
    "company": "Tesla Inc.",
    "keywords": [
      "Tesla", "Elon Musk", "Tesla Motors",
      "Cybertruck", "Model S", "Model 3", "Model Y",
      "Tesla Autopilot", "Tesla Energy"
    ]
  },
  "AAPL": {
    "company": "Apple Inc.",
    "keywords": [
      "Apple", "iPhone", "Tim Cook", "MacBook",
      "iOS", "App Store", "Apple Vision Pro",
      "Apple Watch", "iPad"
    ]
  }
}
```

### Variabili d'Ambiente

Crea un file `.env` per configurare le API:

```bash
# Chiavi API (obbligatorie)
NEWS_API_KEY=your_newsapi_key_here
FMP_KEY=your_financial_modeling_prep_key_here

# Configurazioni opzionali
DEBUG=False
LOG_LEVEL=INFO
```

## 📈 Strategie di Utilizzo

### Workflow Consigliato

1. **Setup Iniziale**:
   - Configura il tuo portfolio in `portfolio.json`
   - Personalizza le keywords in `keywords.json`
   - Ottieni le chiavi API necessarie

2. **Analisi Quotidiana**:
   - Avvia con "📈 Historical Analysis" per vedere i trend
   - Usa "📰 Fetch News" per raccogliere notizie recenti
   - Esegui "🎭 Analyze Sentiment" per analizzare le notizie
   - Visualizza risultati con "📊 View Results"

3. **Analisi Settimanale**:
   - Usa "📈 Compare Changes" per confrontare con analisi precedenti
   - Identifica trend nel sentiment
   - Valuta l'impatto delle notizie sui prezzi

### Strategie di Trading

#### Basate su Sentiment
- **Sentiment Positivo + Trend Rialzista**: Potenziale opportunità di acquisto
- **Sentiment Negativo + Trend Ribassista**: Considera vendita o short
- **Sentiment Misto**: Mantieni posizione neutrale

#### Basate su Correlazione
- **Alta Correlazione**: Diversifica con settori diversi
- **Bassa Correlazione**: Buona diversificazione
- **Correlazione Negativa**: Hedge naturale

#### Basate su Volatilità
- **Alta Volatilità**: Considera opzioni o stop-loss
- **Bassa Volatilità**: Opportunità per strategie direzionali

## 🚨 Troubleshooting

### Problemi Comuni

#### 1. "No historical data found"
**Causa**: Mancano i dati storici o chiave API non valida
**Soluzione**:
- Verifica la chiave FMP_KEY nel file `.env`
- Controlla la connessione internet
- Riavvia l'applicazione

#### 2. "Error fetching news"
**Causa**: Problemi con NewsAPI o chiave non valida
**Soluzione**:
- Verifica la chiave NEWS_API_KEY
- Controlla il limite di richieste giornaliere
- Verifica la connessione internet

#### 3. "Error loading FinBERT model"
**Causa**: Problemi di download del modello
**Soluzione**:
- Verifica la connessione internet
- Aumenta la memoria Docker se necessario
- Riavvia l'applicazione

#### 4. "Container killed due to memory limit"
**Causa**: Memoria insufficiente per il modello ML
**Soluzione**:
- Aumenta il limite di memoria in `docker-compose.yml`
- Chiudi altre applicazioni
- Usa un sistema con più RAM

### Log e Debug

#### Visualizzazione Log
```bash
# Log Docker
docker-compose logs app

# Log in tempo reale
docker-compose logs -f app
```

#### File di Output
Controlla la directory `data/` per:
- `historical_prices.csv`: Dati storici prezzi
- `portfolio_news_*.json`: Notizie raccolte
- `portfolio_news_*_sentiment.json`: Notizie con sentiment

## 📚 Risorse Aggiuntive

### Documentazione API
- **NewsAPI**: https://newsapi.org/docs
- **Financial Modeling Prep**: https://financialmodelingprep.com/developer/docs

### Modello FinBERT
- **Paper**: https://arxiv.org/abs/1908.10063
- **Hugging Face**: https://huggingface.co/ProsusAI/finbert

### Streamlit
- **Documentazione**: https://docs.streamlit.io
- **Gallery**: https://streamlit.io/gallery

## 🤝 Supporto

### Come Ottenere Aiuto

1. **Documentazione**: Consulta questa guida e i file README.md
2. **Issues**: Apri un issue su GitHub per bug o feature requests
3. **Community**: Partecipa alle discussioni del progetto

### Contributi

Se vuoi contribuire al progetto:
1. Fork del repository
2. Crea un branch per la tua feature
3. Implementa le modifiche
4. Crea una Pull Request

---

**Nota Importante**: DollarPunk è uno strumento di analisi e ricerca. Non costituisce consiglio finanziario. Sempre fare le proprie ricerche e consultare professionisti prima di investire. 