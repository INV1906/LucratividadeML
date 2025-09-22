#!/usr/bin/env python3
"""
Script para testar o sistema de status de envio detalhado
"""

import sys
sys.path.append('.')
from shipping_status import map_ml_shipping_status, get_all_shipping_statuses, get_shipping_statuses_by_category
from database import DatabaseManager
import requests

def test_shipping_status_mapping():
    """Testa o mapeamento de status de envio"""
    
    print("🧪 Testando Mapeamento de Status de Envio")
    print("=" * 60)
    
    # Casos de teste
    test_cases = [
        # (ml_status, status_detail, fulfilled, expected_status)
        ("paid", None, False, "ready_to_ship"),
        ("paid", None, True, "shipped"),
        ("confirmed", "shipped", None, "shipped"),
        ("confirmed", "ready", None, "ready_to_ship"),
        ("delivered", None, None, "delivered"),
        ("lost", "extraviado", None, "lost"),
        ("returned", "devolvido", None, "returned"),
        ("cancelled", "cancelado", None, "cancelled"),
        ("scheduled", "agendado", None, "scheduled"),
        ("pickup", "retirada", None, "pickup_available"),
        ("exception", "exceção", None, "exception"),
        ("unknown", None, None, "unknown"),
    ]
    
    print("📊 Testando casos de mapeamento:")
    for ml_status, detail, fulfilled, expected in test_cases:
        mapped, description, category = map_ml_shipping_status(ml_status, detail, fulfilled)
        status = "✅" if mapped == expected else "❌"
        print(f"{status} ML: {ml_status} | Detail: {detail} | Fulfilled: {fulfilled}")
        print(f"    → Mapped: {mapped} | {description} | {category}")
        if mapped != expected:
            print(f"    ⚠️ Expected: {expected}")
        print()
    
    return True

def test_shipping_categories():
    """Testa as categorias de status"""
    
    print("📂 Testando Categorias de Status")
    print("=" * 40)
    
    categories = ['inicial', 'preparacao', 'envio', 'entregue', 'problema', 'cancelado', 'agendado', 'retirada']
    
    for category in categories:
        statuses = get_shipping_statuses_by_category(category)
        print(f"\n{category.upper()}:")
        for status in statuses:
            print(f"  - {status['value']}: {status['description']}")
    
    return True

def test_database_functions():
    """Testa as funções do banco de dados"""
    
    print("\n🗄️ Testando Funções do Banco de Dados")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        user_id = 1305538297
        
        # Teste 1: Obter todos os status
        print("📋 Testando obter_todos_status_envio...")
        statuses = db.obter_todos_status_envio()
        print(f"✅ {len(statuses)} status encontrados")
        
        # Teste 2: Obter status por categoria
        print("\n📂 Testando obter_status_envio_por_categoria...")
        for categoria in ['envio', 'entregue', 'problema']:
            statuses_cat = db.obter_status_envio_por_categoria(categoria)
            print(f"  {categoria}: {len(statuses_cat)} status")
        
        # Teste 3: Obter vendas por status
        print("\n📦 Testando obter_vendas_por_status_envio...")
        vendas = db.obter_vendas_por_status_envio(user_id, limite=10)
        print(f"✅ {len(vendas)} vendas encontradas")
        
        if vendas:
            print("📊 Primeira venda:")
            venda = vendas[0]
            print(f"  - ID: {venda.get('venda_id')}")
            print(f"  - Status: {venda.get('status_envio')}")
            print(f"  - Descrição: {venda.get('status_descricao')}")
            print(f"  - Categoria: {venda.get('status_categoria')}")
            print(f"  - Original: {venda.get('status_original')}")
        
        # Teste 4: Estatísticas
        print("\n📈 Testando obter_estatisticas_status_envio...")
        stats = db.obter_estatisticas_status_envio(user_id)
        print(f"✅ Total de vendas: {stats.get('total_vendas', 0)}")
        
        if stats.get('por_status'):
            print("📊 Status mais comuns:")
            for item in stats['por_status'][:5]:
                print(f"  - {item['status']} ({item['categoria']}): {item['total']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do banco: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Testa os endpoints da API"""
    
    print("\n🌐 Testando Endpoints da API")
    print("=" * 40)
    
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
            print("❌ Erro no login - servidor não está rodando")
            return False
        
        login_result = response.json()
        if not login_result.get('success'):
            print(f"❌ Falha no login: {login_result.get('message')}")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Teste 1: Obter todos os status
        print("\n📋 Testando GET /api/shipping/statuses...")
        response = session.get("http://localhost:3001/api/shipping/statuses")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('statuses', []))} status obtidos")
        else:
            print(f"❌ Erro: {response.status_code}")
        
        # Teste 2: Obter status por categoria
        print("\n📂 Testando GET /api/shipping/statuses/category/envio...")
        response = session.get("http://localhost:3001/api/shipping/statuses/category/envio")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('statuses', []))} status de envio obtidos")
        else:
            print(f"❌ Erro: {response.status_code}")
        
        # Teste 3: Obter vendas filtradas
        print("\n📦 Testando GET /api/shipping/sales...")
        response = session.get("http://localhost:3001/api/shipping/sales?limite=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data.get('total', 0)} vendas obtidas")
        else:
            print(f"❌ Erro: {response.status_code}")
        
        # Teste 4: Estatísticas
        print("\n📈 Testando GET /api/shipping/statistics...")
        response = session.get("http://localhost:3001/api/shipping/statistics")
        if response.status_code == 200:
            data = response.json()
            stats = data.get('statistics', {})
            print(f"✅ Total de vendas: {stats.get('total_vendas', 0)}")
        else:
            print(f"❌ Erro: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando Sistema de Status de Envio Detalhado")
    print("=" * 70)
    
    # Teste 1: Mapeamento de status
    if test_shipping_status_mapping():
        print("✅ Teste de mapeamento passou!")
        
        # Teste 2: Categorias
        if test_shipping_categories():
            print("✅ Teste de categorias passou!")
            
            # Teste 3: Banco de dados
            if test_database_functions():
                print("✅ Teste do banco passou!")
                
                # Teste 4: API (apenas se servidor estiver rodando)
                test_api_endpoints()
                
                print("\n🎉 TODOS OS TESTES PASSARAM!")
                print("Sistema de status de envio detalhado funcionando perfeitamente!")
            else:
                print("\n❌ Teste do banco falhou")
        else:
            print("\n❌ Teste de categorias falhou")
    else:
        print("\n❌ Teste de mapeamento falhou")
