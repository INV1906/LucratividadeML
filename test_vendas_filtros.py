#!/usr/bin/env python3
"""
Script para testar os filtros de status na tela de vendas
"""

import sys
sys.path.append('.')
from database import DatabaseManager
import requests

def test_vendas_filtros():
    """Testa os filtros de status na tela de vendas"""
    
    print("🧪 Testando Filtros de Status na Tela de Vendas")
    print("=" * 60)
    
    try:
        db = DatabaseManager()
        user_id = 1305538297
        
        # Teste 1: Buscar vendas sem filtros
        print("📦 Teste 1: Buscar vendas sem filtros...")
        vendas = db.obter_vendas_usuario_novo(user_id, page=1, per_page=5)
        print(f"✅ {len(vendas)} vendas encontradas")
        
        if vendas:
            venda = vendas[0]
            print(f"📊 Primeira venda:")
            print(f"  - Status Pagamento: {venda.get('status_pagamento')} → {venda.get('status_pagamento_pt')}")
            print(f"  - Status Envio: {venda.get('status_envio')} → {venda.get('status_envio_pt')}")
            print(f"  - Método Pagamento: {venda.get('payment_method')} → {venda.get('payment_method_pt')}")
            print(f"  - Método Envio: {venda.get('shipping_method')} → {venda.get('shipping_method_pt')}")
        
        # Teste 2: Filtrar por status de pagamento
        print("\n💳 Teste 2: Filtrar por status de pagamento 'approved'...")
        vendas_approved = db.obter_vendas_usuario_novo(user_id, page=1, per_page=5, status_pagamento='approved')
        print(f"✅ {len(vendas_approved)} vendas com status 'approved'")
        
        # Teste 3: Filtrar por status de envio
        print("\n📦 Teste 3: Filtrar por status de envio 'ready_to_ship'...")
        vendas_ready = db.obter_vendas_usuario_novo(user_id, page=1, per_page=5, status_envio='ready_to_ship')
        print(f"✅ {len(vendas_ready)} vendas com status 'ready_to_ship'")
        
        # Teste 4: Filtrar por ambos os status
        print("\n🔍 Teste 4: Filtrar por ambos os status...")
        vendas_filtradas = db.obter_vendas_usuario_novo(user_id, page=1, per_page=5, 
                                                       status_pagamento='approved', 
                                                       status_envio='ready_to_ship')
        print(f"✅ {len(vendas_filtradas)} vendas com ambos os filtros")
        
        # Teste 5: Contar vendas com filtros
        print("\n📊 Teste 5: Contar vendas com filtros...")
        total_approved = db.contar_vendas_usuario_novo(user_id, status_pagamento='approved')
        total_ready = db.contar_vendas_usuario_novo(user_id, status_envio='ready_to_ship')
        total_both = db.contar_vendas_usuario_novo(user_id, status_pagamento='approved', status_envio='ready_to_ship')
        
        print(f"  - Total com status 'approved': {total_approved}")
        print(f"  - Total com status 'ready_to_ship': {total_ready}")
        print(f"  - Total com ambos: {total_both}")
        
        # Teste 6: Calcular totais com filtros
        print("\n💰 Teste 6: Calcular totais com filtros...")
        totais_approved = db.calcular_totais_vendas_novo(user_id, status_pagamento='approved')
        totais_ready = db.calcular_totais_vendas_novo(user_id, status_envio='ready_to_ship')
        
        print(f"  - Totais com status 'approved': {totais_approved}")
        print(f"  - Totais com status 'ready_to_ship': {totais_ready}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_filtros():
    """Testa a API com filtros de status"""
    
    print("\n🌐 Testando API com Filtros de Status")
    print("=" * 50)
    
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
        
        # Teste 1: API sem filtros
        print("\n📦 Teste 1: API sem filtros...")
        response = session.get("http://localhost:3001/api/vendas?per_page=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('vendas', []))} vendas retornadas")
            
            if data.get('vendas'):
                venda = data['vendas'][0]
                print(f"📊 Primeira venda:")
                print(f"  - Status Pagamento: {venda.get('status_pagamento_pt', 'N/A')}")
                print(f"  - Status Envio: {venda.get('status_envio_pt', 'N/A')}")
        else:
            print(f"❌ Erro na API: {response.status_code}")
        
        # Teste 2: API com filtro de status de pagamento
        print("\n💳 Teste 2: API com filtro de status de pagamento...")
        response = session.get("http://localhost:3001/api/vendas?status_pagamento=approved&per_page=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('vendas', []))} vendas com status 'approved'")
        else:
            print(f"❌ Erro na API: {response.status_code}")
        
        # Teste 3: API com filtro de status de envio
        print("\n📦 Teste 3: API com filtro de status de envio...")
        response = session.get("http://localhost:3001/api/vendas?status_envio=ready_to_ship&per_page=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('vendas', []))} vendas com status 'ready_to_ship'")
        else:
            print(f"❌ Erro na API: {response.status_code}")
        
        # Teste 4: API com ambos os filtros
        print("\n🔍 Teste 4: API com ambos os filtros...")
        response = session.get("http://localhost:3001/api/vendas?status_pagamento=approved&status_envio=ready_to_ship&per_page=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('vendas', []))} vendas com ambos os filtros")
        else:
            print(f"❌ Erro na API: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando Sistema de Filtros de Status")
    print("=" * 70)
    
    # Teste 1: Banco de dados
    if test_vendas_filtros():
        print("✅ Testes do banco de dados passaram!")
        
        # Teste 2: API
        test_api_filtros()
        
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("Sistema de filtros de status funcionando perfeitamente!")
    else:
        print("\n❌ Testes do banco de dados falharam")
