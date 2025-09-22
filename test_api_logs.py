#!/usr/bin/env python3
"""
Script para testar API de logs de webhook
"""

import requests

def test_api_logs():
    """Testa se a API de logs está funcionando"""
    
    print("🧪 Testando API de logs de webhook...")
    
    # Simular login
    session = requests.Session()
    login_data = {
        "type": "password",
        "username": "Contigo",
        "password": "Adeg@33781210"
    }
    
    try:
        # Fazer login
        response = session.post("http://localhost:3001/", json=login_data)
        if response.status_code == 200:
            print("✅ Login realizado")
            
            # Testar API de logs
            response = session.get("http://localhost:3001/api/webhook/logs")
            print(f"📊 Status da API: {response.status_code}")
            
            if response.status_code == 200:
                logs = response.json()
                print(f"📋 Logs retornados: {len(logs)}")
                
                for log in logs[:3]:
                    print(f"   - {log.get('topic')} - {log.get('success')} - {log.get('processed_at')}")
            else:
                print(f"❌ Erro na API: {response.text}")
        else:
            print("❌ Erro no login")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_api_logs()
