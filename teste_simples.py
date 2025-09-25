#!/usr/bin/env python3
"""
Teste simples para verificar o problema de sessão
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def testar_rota_simples():
    print("🧪 Testando rota simples...")
    
    # Testar rota sem login_required
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Rota /: Status {response.status_code}")
    except Exception as e:
        print(f"   Erro na rota /: {e}")
    
    # Testar rota com login_required
    try:
        response = requests.get(f"{BASE_URL}/importar/status")
        print(f"   Rota /importar/status: Status {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        if response.status_code == 302:
            print(f"   Location: {response.headers.get('Location')}")
    except Exception as e:
        print(f"   Erro na rota /importar/status: {e}")

if __name__ == "__main__":
    testar_rota_simples()
