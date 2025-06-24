@echo off
echo 🚀 Avvio DollarPunk - Sistema di Raccolta Massiva Dati
echo ==================================================

REM Verifica se Docker è installato
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker non è installato. Installa Docker Desktop prima di continuare.
    pause
    exit /b 1
)

REM Verifica se Docker Compose è installato
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose non è installato. Installa Docker Desktop prima di continuare.
    pause
    exit /b 1
)

REM Verifica se il file .env esiste
if not exist .env (
    echo ⚠️  File .env non trovato. Creazione template...
    (
        echo # Configurazione API Keys
        echo NEWS_API_KEY=your_newsapi_key_here
        echo FMP_KEY=your_financial_modeling_prep_key_here
    ) > .env
    echo 📝 Creato file .env template. Modifica con le tue API keys prima di continuare.
    echo 🔑 Ottieni la tua NewsAPI key su: https://newsapi.org/
    pause
    exit /b 1
)

REM Verifica se le API keys sono configurate
findstr "your_newsapi_key_here" .env >nul
if not errorlevel 1 (
    echo ❌ Configura le tue API keys nel file .env prima di continuare.
    echo 🔑 Ottieni la tua NewsAPI key su: https://newsapi.org/
    pause
    exit /b 1
)

echo ✅ Configurazione verificata

REM Crea directory data se non esiste
if not exist data mkdir data

REM Build e avvio container
echo 🔨 Building Docker image...
docker-compose build

echo 🚀 Avvio container...
docker-compose up -d

echo ⏳ Attendo che l'applicazione sia pronta...
timeout /t 5 /nobreak >nul

echo ✅ Applicazione avviata!
echo 🌐 Apri http://localhost:8501 nel tuo browser
echo.
echo 📊 Per monitorare i log:
echo    docker-compose logs -f
echo.
echo 🛑 Per fermare l'applicazione:
echo    docker-compose down
echo.
pause 