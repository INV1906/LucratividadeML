#!/usr/bin/env python3
"""
Script para testar importação rápida de vendas
"""

import requests
import time

def test_importacao_rapida():
    """Testa importação com monitoramento rápido"""
    
    print("🧪 Testando importação com monitoramento rápido...")
    
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
        if response.status_code != 200:
            print("❌ Erro no login")
            return False
        
        print("✅ Login realizado")
        
        # Iniciar importação
        response = session.post("http://localhost:3001/importar/vendas")
        if response.status_code != 200:
            print("❌ Erro na importação")
            return False
        
        print("✅ Importação iniciada")
        
        # Monitorar por 15 segundos
        for i in range(15):
            time.sleep(1)
            response = session.get("http://localhost:3001/importar/status")
            if response.status_code == 200:
                status = response.json()
                vendas_status = status.get("vendas", {})
                print(f"[{i+1:2d}s] {vendas_status.get('status', 'N/A')} - Progresso: {vendas_status.get('progresso', 0)}%")
                
                if not vendas_status.get("ativo", False):
                    print("🏁 Importação finalizada!")
                    print(f"   Status final: {vendas_status.get('status', 'N/A')}")
                    print(f"   Total processado: {vendas_status.get('atual', 0)}")
                    print(f"   Sucessos: {vendas_status.get('sucesso', 0)}")
                    print(f"   Erros: {vendas_status.get('erros', 0)}")
                    break
            else:
                print(f"❌ Erro ao verificar status: {response.status_code}")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    test_importacao_rapida()
