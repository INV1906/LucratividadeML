#!/usr/bin/env python3
"""
Script para testar a importação de vendas
"""

import requests
import json
from datetime import datetime

# URL base do sistema
BASE_URL = "http://localhost:3001"

def test_import_vendas():
    """Testa a importação de vendas via API"""
    
    print("🧪 Testando importação de vendas...")
    print("=" * 50)
    
    # Simular login (você precisa ter um usuário logado)
    session = requests.Session()
    
    # Fazer login (ajuste conforme necessário)
    login_data = {
        "type": "password",
        "username": "Contigo",  # Ajuste conforme seu usuário
        "password": "Adeg@33781210"  # Ajuste conforme sua senha
    }
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        response = session.post(f"{BASE_URL}/", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
        
        login_result = response.json()
        if not login_result.get('success'):
            print(f"❌ Falha no login: {login_result.get('message')}")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Testar importação de vendas
        print("\n📦 Iniciando importação de vendas...")
        response = session.post(f"{BASE_URL}/importar/vendas")
        
        if response.status_code != 200:
            print(f"❌ Erro na importação: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
        
        import_result = response.json()
        if not import_result.get('success'):
            print(f"❌ Falha na importação: {import_result.get('message')}")
            return False
        
        print("✅ Importação iniciada com sucesso!")
        print(f"📝 Mensagem: {import_result.get('message')}")
        
        # Verificar status da importação
        print("\n📊 Verificando status da importação...")
        response = session.get(f"{BASE_URL}/importar/status/vendas")
        
        if response.status_code == 200:
            status = response.json()
            print(f"Status: {status.get('status', 'N/A')}")
            print(f"Progresso: {status.get('progresso', 0)}%")
            print(f"Sucessos: {status.get('sucesso', 0)}")
            print(f"Erros: {status.get('erros', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

def test_webhook_vendas():
    """Testa o webhook de vendas"""
    
    print("\n🔔 Testando webhook de vendas...")
    print("=" * 50)
    
    # Dados de exemplo de webhook orders_v2
    webhook_data = {
        "id": f"test_webhook_{int(datetime.now().timestamp())}",
        "resource": "/orders/2000009346906540",  # Venda real do banco
        "user_id": 1305538297,  # Usuário válido do banco
        "topic": "orders_v2",
        "application_id": 1234567890123456,
        "attempts": 1,
        "sent": datetime.now().isoformat() + "Z",
        "received": datetime.now().isoformat() + "Z"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook/mercadolivre",
            json=webhook_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Resposta: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
            return True
        else:
            print("❌ Erro ao processar webhook")
            return False
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        return False

def test_vendas_database():
    """Testa se as vendas estão sendo salvas no banco"""
    
    print("\n🗄️ Testando banco de dados...")
    print("=" * 50)
    
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        
        # Verificar se existem vendas no banco
        vendas = db.obter_vendas_usuario_novo(1305538297)  # Usuário válido do banco
        
        if vendas:
            print(f"✅ Encontradas {len(vendas)} vendas no banco")
            print("📋 Primeiras 3 vendas:")
            for i, venda in enumerate(vendas[:3]):
                print(f"  {i+1}. Pack ID: {venda.get('pack_id', 'N/A')}")
                print(f"     Data: {venda.get('data_aprovacao', 'N/A')}")
                print(f"     Valor: R$ {venda.get('valor_total', 0):.2f}")
                print(f"     Comprador: {venda.get('comprador_nome', 'N/A')}")
                print()
        else:
            print("⚠️ Nenhuma venda encontrada no banco")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

def main():
    """Função principal de teste"""
    
    print("🔧 Teste de Importação de Vendas")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get(BASE_URL, timeout=5)
        print("✅ Servidor está rodando")
    except:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro.")
        return
    
    print()
    
    # Executar testes
    tests = [
        ("Importação via API", test_import_vendas),
        ("Webhook de vendas", test_webhook_vendas),
        ("Banco de dados", test_vendas_database)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema de vendas funcionando corretamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")

if __name__ == "__main__":
    main()
