#!/bin/bash

echo "🚀 Avvio DollarPunk - Sistema di Raccolta Massiva Dati"
echo "=================================================="

# Verifica se Docker è installato
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non è installato. Installa Docker prima di continuare."
    exit 1
fi

# Verifica se Docker Compose è installato
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non è installato. Installa Docker Compose prima di continuare."
    exit 1
fi

# Verifica se il file .env esiste
if [ ! -f .env ]; then
    echo "⚠️  File .env non trovato. Creazione template..."
    cat > .env << EOF
# Configurazione API Keys
NEWS_API_KEY=your_newsapi_key_here
FMP_KEY=your_financial_modeling_prep_key_here
EOF
    echo "📝 Creato file .env template. Modifica con le tue API keys prima di continuare."
    echo "🔑 Ottieni la tua NewsAPI key su: https://newsapi.org/"
    exit 1
fi

# Verifica se le API keys sono configurate
if grep -q "your_newsapi_key_here" .env; then
    echo "❌ Configura le tue API keys nel file .env prima di continuare."
    echo "🔑 Ottieni la tua NewsAPI key su: https://newsapi.org/"
    exit 1
fi

echo "✅ Configurazione verificata"

# Crea directory data se non esiste
mkdir -p data

# Build e avvio container
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Avvio container..."
docker-compose up -d

echo "⏳ Attendo che l'applicazione sia pronta..."
sleep 5

# Verifica se l'applicazione è in esecuzione
if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
    echo "✅ Applicazione avviata con successo!"
    echo "🌐 Apri http://localhost:8501 nel tuo browser"
    echo ""
    echo "📊 Per monitorare i log:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Per fermare l'applicazione:"
    echo "   docker-compose down"
else
    echo "⚠️  Applicazione in avvio... prova ad aprire http://localhost:8501"
fi 