#!/usr/bin/env python3
"""
Test rapido per verificare che il sistema Docker funzioni
"""

import os
import sys
import json
from dotenv import load_dotenv

def test_basic_setup():
    """Test base del setup"""
    print("🔧 Test Setup Base...")
    
    # Test file essenziali
    required_files = [
        'app_simplified.py',
        'portfolio.json', 
        'keywords.json',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} mancante")
            return False
    
    return True

def test_config_files():
    """Test file di configurazione"""
    print("\n📋 Test File Configurazione...")
    
    # Test portfolio.json
    try:
        with open('portfolio.json', 'r') as f:
            portfolio = json.load(f)
        stocks = portfolio.get('stocks', [])
        print(f"✅ Portfolio: {len(stocks)} stocks configurati")
    except Exception as e:
        print(f"❌ Errore portfolio.json: {e}")
        return False
    
    # Test keywords.json
    try:
        with open('keywords.json', 'r') as f:
            keywords = json.load(f)
        print(f"✅ Keywords: {len(keywords)} tickers configurati")
    except Exception as e:
        print(f"❌ Errore keywords.json: {e}")
        return False
    
    return True

def test_docker_files():
    """Test file Docker"""
    print("\n🐳 Test File Docker...")
    
    # Test Dockerfile
    with open('Dockerfile', 'r') as f:
        dockerfile = f.read()
        if 'streamlit' in dockerfile and 'app_simplified.py' in dockerfile:
            print("✅ Dockerfile configurato correttamente")
        else:
            print("❌ Dockerfile non configurato correttamente")
            return False
    
    # Test docker-compose.yml
    with open('docker-compose.yml', 'r') as f:
        compose = f.read()
        if 'dollarpunk' in compose and '8501' in compose:
            print("✅ docker-compose.yml configurato correttamente")
        else:
            print("❌ docker-compose.yml non configurato correttamente")
            return False
    
    return True

def test_env_setup():
    """Test setup ambiente"""
    print("\n🌍 Test Setup Ambiente...")
    
    # Test .env
    if os.path.exists('.env'):
        load_dotenv()
        news_key = os.getenv('NEWS_API_KEY')
        if news_key and news_key != 'your_newsapi_key_here':
            print("✅ .env configurato con API key")
        else:
            print("⚠️  .env presente ma API key non configurata")
    else:
        print("⚠️  .env non trovato - verrà creato automaticamente")
    
    return True

def main():
    """Esegue tutti i test"""
    print("🚀 DollarPunk - Test Rapido Setup Docker")
    print("=" * 50)
    
    tests = [
        ("Setup Base", test_basic_setup),
        ("Configurazione", test_config_files),
        ("Docker Files", test_docker_files),
        ("Ambiente", test_env_setup)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} fallito")
        except Exception as e:
            print(f"❌ {test_name} crash: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Risultati: {passed}/{total} test superati")
    
    if passed == total:
        print("🎉 Setup pronto per Docker!")
        print("\n🚀 Per avviare:")
        print("   Windows: start_docker.bat")
        print("   Linux/Mac: ./start_docker.sh")
        print("   Manuale: docker-compose up --build")
    else:
        print("⚠️  Alcuni test falliti. Controlla la configurazione.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 