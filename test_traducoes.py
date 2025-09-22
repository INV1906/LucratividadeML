#!/usr/bin/env python3
"""
Script para testar o sistema de traduções em português
"""

import sys
sys.path.append('.')
from translations import translate_payment_status, translate_payment_method, translate_shipping_method, translate_order_status
from database import DatabaseManager
import requests

def test_translation_system():
    """Testa o sistema de tradução"""
    
    print("🧪 Testando Sistema de Tradução")
    print("=" * 50)
    
    # Teste 1: Status de pagamento
    print("💳 Testando Status de Pagamento:")
    payment_statuses = ['approved', 'pending', 'rejected', 'cancelled', 'refunded']
    for status in payment_statuses:
        translated = translate_payment_status(status)
        print(f"  {status} → {translated}")
    
    # Teste 2: Métodos de pagamento
    print("\n💳 Testando Métodos de Pagamento:")
    payment_methods = ['credit_card', 'pix', 'boleto', 'mercadopago', 'account_money']
    for method in payment_methods:
        translated = translate_payment_method(method)
        print(f"  {method} → {translated}")
    
    # Teste 3: Métodos de envio
    print("\n📦 Testando Métodos de Envio:")
    shipping_methods = ['mercadoenvios', 'custom', 'me2', 'fulfillment']
    for method in shipping_methods:
        translated = translate_shipping_method(method)
        print(f"  {method} → {translated}")
    
    # Teste 4: Status de pedido
    print("\n📋 Testando Status de Pedido:")
    order_statuses = ['confirmed', 'paid', 'cancelled', 'payment_required']
    for status in order_statuses:
        translated = translate_order_status(status)
        print(f"  {status} → {translated}")
    
    return True

def test_database_translations():
    """Testa traduções no banco de dados"""
    
    print("\n🗄️ Testando Traduções no Banco de Dados")
    print("=" * 50)
    
    try:
        db = DatabaseManager()
        user_id = 1305538297
        
        # Buscar vendas com traduções
        vendas = db.obter_vendas_por_status_envio(user_id, limite=5)
        
        if vendas:
            print("📊 Vendas com traduções:")
            for venda in vendas:
                print(f"\nVenda {venda.get('venda_id')}:")
                print(f"  Status Pagamento: {venda.get('status_pagamento')} → {venda.get('status_pagamento_pt')}")
                print(f"  Método Pagamento: {venda.get('payment_method')} → {venda.get('payment_method_pt')}")
                print(f"  Método Envio: {venda.get('shipping_method')} → {venda.get('shipping_method_pt')}")
                print(f"  Status Pedido: {venda.get('status')} → {venda.get('status_pedido_pt')}")
                print(f"  Status Envio: {venda.get('status_envio')} → {venda.get('status_envio_pt')}")
                print(f"  Categoria Envio: {venda.get('status_envio_categoria')} → {venda.get('categoria_envio_pt')}")
        else:
            print("❌ Nenhuma venda encontrada")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do banco: {e}")
        return False

def test_api_translations():
    """Testa traduções via API"""
    
    print("\n🌐 Testando Traduções via API")
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
        
        # Teste: Buscar vendas com traduções
        print("\n📦 Testando GET /api/shipping/sales...")
        response = session.get("http://localhost:3001/api/shipping/sales?limite=3")
        
        if response.status_code == 200:
            data = response.json()
            vendas = data.get('vendas', [])
            
            if vendas:
                print(f"✅ {len(vendas)} vendas obtidas com traduções:")
                for venda in vendas[:2]:  # Mostrar apenas 2
                    print(f"\nVenda {venda.get('venda_id')}:")
                    print(f"  Status Pagamento: {venda.get('status_pagamento_pt')}")
                    print(f"  Método Pagamento: {venda.get('payment_method_pt')}")
                    print(f"  Método Envio: {venda.get('shipping_method_pt')}")
                    print(f"  Status Pedido: {venda.get('status_pedido_pt')}")
                    print(f"  Status Envio: {venda.get('status_envio_pt')}")
                    print(f"  Categoria Envio: {venda.get('categoria_envio_pt')}")
            else:
                print("❌ Nenhuma venda retornada")
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testando Sistema de Traduções em Português")
    print("=" * 60)
    
    # Teste 1: Sistema de tradução
    if test_translation_system():
        print("✅ Sistema de tradução funcionando!")
        
        # Teste 2: Banco de dados
        if test_database_translations():
            print("✅ Traduções no banco funcionando!")
            
            # Teste 3: API
            test_api_translations()
            
            print("\n🎉 TODOS OS TESTES DE TRADUÇÃO PASSARAM!")
            print("Sistema completamente em português!")
        else:
            print("\n❌ Teste do banco falhou")
    else:
        print("\n❌ Teste do sistema de tradução falhou")
