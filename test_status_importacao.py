#!/usr/bin/env python3
"""
Script para testar o sistema de status de importação
"""

import requests
import time
import json

def test_importacao_com_status():
    """Testa importação com monitoramento de status"""
    
    print("🧪 Testando importação com status em tempo real...")
    print("=" * 60)
    
    # Simular login
    session = requests.Session()
    login_data = {
        "type": "password",
        "username": "Contigo",
        "password": "Adeg@33781210"
    }
    
    try:
        # Fazer login
        print("🔐 Fazendo login...")
        response = session.post("http://localhost:3001/", json=login_data)
        
        if response.status_code != 200:
            print(f"❌ Erro no login: {response.status_code}")
            return False
        
        login_result = response.json()
        if not login_result.get('success'):
            print(f"❌ Falha no login: {login_result.get('message')}")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Verificar status inicial
        print("\n📊 Status inicial:")
        response = session.get("http://localhost:3001/importar/status")
        if response.status_code == 200:
            status = response.json()
            vendas_status = status.get('vendas', {})
            print(f"   Vendas ativo: {vendas_status.get('ativo', False)}")
            print(f"   Vendas status: {vendas_status.get('status', 'N/A')}")
        
        # Iniciar importação de vendas
        print("\n📦 Iniciando importação de vendas...")
        response = session.post("http://localhost:3001/importar/vendas")
        
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
        
        # Monitorar status da importação
        print("\n📊 Monitorando status da importação...")
        print("-" * 60)
        
        for i in range(30):  # Monitorar por até 30 segundos
            time.sleep(1)
            
            # Verificar status
            response = session.get("http://localhost:3001/importar/status")
            if response.status_code == 200:
                status = response.json()
                vendas_status = status.get('vendas', {})
                
                print(f"[{i+1:2d}s] {vendas_status.get('status', 'N/A')} - "
                      f"Progresso: {vendas_status.get('progresso', 0)}% - "
                      f"Sucessos: {vendas_status.get('sucesso', 0)} - "
                      f"Erros: {vendas_status.get('erros', 0)}")
                
                # Se não está mais ativo, parar monitoramento
                if not vendas_status.get('ativo', False):
                    print(f"\n🏁 Importação finalizada!")
                    print(f"   Status: {vendas_status.get('status', 'N/A')}")
                    print(f"   Total processado: {vendas_status.get('atual', 0)}")
                    print(f"   Sucessos: {vendas_status.get('sucesso', 0)}")
                    print(f"   Erros: {vendas_status.get('erros', 0)}")
                    break
            else:
                print(f"❌ Erro ao verificar status: {response.status_code}")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_status_api_direto():
    """Testa a API de status diretamente"""
    
    print("\n🔍 Testando API de status diretamente...")
    
    try:
        response = requests.get("http://localhost:3001/importar/status")
        
        if response.status_code == 200:
            status = response.json()
            print("✅ API de status funcionando")
            print(f"📊 Status atual:")
            print(f"   Produtos ativo: {status.get('produtos', {}).get('ativo', False)}")
            print(f"   Vendas ativo: {status.get('vendas', {}).get('ativo', False)}")
            print(f"   Vendas status: {status.get('vendas', {}).get('status', 'N/A')}")
            print(f"   Vendas progresso: {status.get('vendas', {}).get('progresso', 0)}%")
            return True
        else:
            print(f"❌ Erro na API de status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar API: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Teste do Sistema de Status de Importação")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        print("✅ Servidor está rodando")
    except:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro.")
        exit(1)
    
    print()
    
    # Executar testes
    tests = [
        ("API de Status", test_status_api_direto),
        ("Importação com Status", test_importacao_com_status)
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
        print("🎉 Todos os testes passaram! Sistema de status funcionando perfeitamente.")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
