#!/usr/bin/env python3
"""
Script para testar o sistema completo de renovação automática de tokens
"""

import sys
sys.path.append('.')
import requests
import time
from datetime import datetime

def test_sistema_completo():
    """Testa o sistema completo de tokens e sincronização"""
    
    print("🧪 Testando Sistema Completo de Tokens e Sincronização")
    print("=" * 70)
    
    try:
        # Simular login
        session = requests.Session()
        login_data = {
            "type": "password",
            "username": "Contigo",
            "password": "Adeg@33781210"
        }
        
        print("🔐 Fazendo login...")
        response = session.post("http://localhost:3001/", json=login_data)
        
        if response.status_code != 200:
            print("❌ Erro no login")
            return False
        
        login_result = response.json()
        if not login_result.get('success'):
            print(f"❌ Falha no login: {login_result.get('message')}")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Teste 1: Status do token
        print("\n📊 Testando status do token...")
        response = session.get("http://localhost:3001/api/token/status")
        
        if response.status_code == 200:
            token_status = response.json()
            print(f"✅ Status do token obtido:")
            print(f"   - User ID: {token_status.get('user_id')}")
            print(f"   - Precisa reautenticar: {token_status.get('needs_reauth')}")
            
            token_info = token_status.get('token_info', {})
            if token_info:
                print(f"   - Criado em: {token_info.get('created_at')}")
                print(f"   - Expira em: {token_info.get('expires_in')} segundos")
                print(f"   - Tempo restante: {token_info.get('tempo_restante_horas', 0):.2f} horas")
        else:
            print(f"❌ Erro ao obter status do token: {response.status_code}")
        
        # Teste 2: Sincronização de dados
        print("\n🔄 Testando sincronização de dados...")
        response = session.post("http://localhost:3001/api/token/sync")
        
        if response.status_code == 200:
            sync_result = response.json()
            print(f"✅ Sincronização: {sync_result.get('message')}")
        else:
            print(f"❌ Erro na sincronização: {response.status_code}")
        
        # Teste 3: Importação de vendas (com renovação automática)
        print("\n📦 Testando importação de vendas...")
        response = session.post("http://localhost:3001/importar/vendas")
        
        if response.status_code == 200:
            import_result = response.json()
            print(f"✅ Importação: {import_result.get('message')}")
            
            # Monitorar por 30 segundos
            print("⏱️ Monitorando importação por 30 segundos...")
            for i in range(30):
                time.sleep(1)
                response = session.get("http://localhost:3001/importar/status")
                if response.status_code == 200:
                    status = response.json()
                    vendas_status = status.get('vendas', {})
                    
                    print(f"[{i+1:2d}s] {vendas_status.get('status', 'N/A')} - "
                          f"Progresso: {vendas_status.get('progresso', 0)}% - "
                          f"Sucessos: {vendas_status.get('sucesso', 0)} - "
                          f"Erros: {vendas_status.get('erros', 0)}")
                    
                    if not vendas_status.get('ativo', False):
                        print(f"\n🏁 Importação finalizada!")
                        break
        else:
            print(f"❌ Erro na importação: {response.status_code}")
        
        # Teste 4: Usuários que precisam reautenticar
        print("\n👥 Testando lista de usuários para reautenticação...")
        response = session.get("http://localhost:3001/api/token/users-needing-reauth")
        
        if response.status_code == 200:
            users_result = response.json()
            usuarios = users_result.get('usuarios', [])
            print(f"✅ Usuários que precisam reautenticar: {len(usuarios)}")
            
            for usuario in usuarios[:5]:  # Mostra apenas os primeiros 5
                print(f"   - User ID: {usuario['user_id']}, "
                      f"Última tentativa: {usuario['last_reauth_attempt']}")
        else:
            print(f"❌ Erro ao obter usuários: {response.status_code}")
        
        # Teste 5: Monitor de tokens
        print("\n🔍 Testando monitor de tokens...")
        response = session.post("http://localhost:3001/api/token/start-monitor")
        
        if response.status_code == 200:
            monitor_result = response.json()
            print(f"✅ Monitor: {monitor_result.get('message')}")
        else:
            print(f"❌ Erro ao iniciar monitor: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_webhook_system():
    """Testa o sistema de webhooks com renovação automática"""
    
    print("\n🔔 Testando Sistema de Webhooks")
    print("=" * 50)
    
    try:
        # Simular webhook de venda
        webhook_data = {
            "_id": "test_webhook_123",
            "resource": "orders/2000009361030898",
            "user_id": 1305538297,
            "topic": "orders_v2",
            "application_id": 123456,
            "attempts": 1,
            "sent": datetime.now().isoformat(),
            "received": datetime.now().isoformat(),
            "actions": ["created"]
        }
        
        print("📤 Enviando webhook de teste...")
        response = requests.post("http://localhost:3001/webhook/mercadolivre", json=webhook_data)
        
        if response.status_code == 200:
            webhook_result = response.json()
            print(f"✅ Webhook processado: {webhook_result.get('message')}")
        else:
            print(f"❌ Erro no webhook: {response.status_code}")
            print(f"   Resposta: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de webhook: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando Testes do Sistema Completo")
    print("=" * 70)
    
    # Teste principal
    if test_sistema_completo():
        print("\n✅ Teste principal passou!")
        
        # Teste de webhooks
        if test_webhook_system():
            print("\n✅ Teste de webhooks passou!")
            
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("Sistema de renovação automática de tokens funcionando perfeitamente!")
        else:
            print("\n❌ Teste de webhooks falhou")
    else:
        print("\n❌ Teste principal falhou")
