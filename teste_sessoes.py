#!/usr/bin/env python3
"""
Teste para verificar se as sessões estão funcionando corretamente
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def testar_sessoes():
    print("🧪 Testando gerenciamento de sessões...\n")
    
    # 1. Testar login com primeira conta
    print("1️⃣ Testando login com primeira conta...")
    try:
        response = requests.post(f"{BASE_URL}/", json={
            'type': 'mercadolivre'
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Redirecionamento para OAuth funcionando")
            else:
                print(f"   ❌ Erro: {data.get('message')}")
        else:
            print("   ❌ Erro: Status não é 200")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    # 2. Testar rota de debug de sessões
    print("\n2️⃣ Testando rota de debug de sessões...")
    try:
        response = requests.post(f"{BASE_URL}/debug/limpar-sessoes")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Rota de debug funcionando")
            else:
                print(f"   ❌ Erro: {data.get('message')}")
        else:
            print("   ❌ Erro: Status não é 200")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    # 3. Testar rota protegida sem sessão
    print("\n3️⃣ Testando rota protegida sem sessão...")
    try:
        response = requests.get(f"{BASE_URL}/importar/status")
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirecionamento para autenticação funcionando")
        else:
            print(f"   ❌ Erro: Esperado redirecionamento 302, recebido {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    # 4. Testar rota de status de sincronização sem sessão
    print("\n4️⃣ Testando rota de status de sincronização sem sessão...")
    try:
        response = requests.get(f"{BASE_URL}/api/sync/status")
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirecionamento para autenticação funcionando")
        else:
            print(f"   ❌ Erro: Esperado redirecionamento 302, recebido {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro inesperado: {e}")
    
    print("\n✅ Teste de sessões concluído!")

if __name__ == "__main__":
    testar_sessoes()
