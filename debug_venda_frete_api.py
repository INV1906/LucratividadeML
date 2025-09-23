#!/usr/bin/env python3
"""
Script para debugar a estrutura de frete da venda específica da API
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🔍 DEBUGANDO ESTRUTURA DE FRETE DA VENDA: 2000013113228770')
    print('=' * 70)
    
    # Inicializar API e Database
    api = MercadoLivreAPI()
    db = DatabaseManager()
    
    user_id = 1305538297
    venda_id = '2000013113228770'
    
    # Obter access token
    access_token = db.obter_access_token(user_id)
    if not access_token:
        print('❌ Erro: Não foi possível obter access token')
        exit()
    
    print(f'✅ Access token obtido: {access_token[:20]}...')
    
    # Buscar dados da venda
    print(f'🔍 Buscando dados da venda {venda_id}...')
    venda_data = api.obter_venda_por_id(venda_id, access_token)
    
    if venda_data:
        print('✅ Dados da venda obtidos!')
        print()
        
        # Analisar estrutura de shipping
        shipping = venda_data.get('shipping', {})
        print('🚚 ESTRUTURA SHIPPING:')
        print(f'   {shipping}')
        print()
        
        # Analisar billing_info
        billing = venda_data.get('billing_info', {})
        print('💰 ESTRUTURA BILLING_INFO:')
        print(f'   {billing}')
        print()
        
        # Analisar payments
        payments = venda_data.get('payments', [])
        print(f'💳 TOTAL DE PAGAMENTOS: {len(payments)}')
        
        if payments:
            for i, payment in enumerate(payments):
                print(f'💳 PAGAMENTO {i+1}:')
                print(f'   ID: {payment.get("id")}')
                print(f'   Transaction Amount: R$ {payment.get("transaction_amount", 0)}')
                print(f'   Shipping Cost: R$ {payment.get("shipping_cost", 0)}')
                print(f'   Marketplace Fee: R$ {payment.get("marketplace_fee", 0)}')
                print(f'   Total Paid: R$ {payment.get("total_paid_amount", 0)}')
                print()
                
                # Verificar todos os campos do pagamento
                print(f'   📋 TODOS OS CAMPOS DO PAGAMENTO:')
                for key, value in payment.items():
                    if 'shipping' in key.lower() or 'frete' in key.lower() or 'envio' in key.lower():
                        print(f'      {key}: {value}')
                print()
        
        # Analisar order_items
        order_items = venda_data.get('order_items', [])
        print(f'📦 TOTAL DE ITENS: {len(order_items)}')
        
        if order_items:
            for i, item in enumerate(order_items):
                print(f'📦 ITEM {i+1}:')
                print(f'   MLB: {item.get("item", {}).get("id")}')
                print(f'   Título: {item.get("item", {}).get("title")}')
                print(f'   Preço Unitário: R$ {item.get("unit_price", 0)}')
                print(f'   Quantidade: {item.get("quantity", 0)}')
                print(f'   Sale Fee: R$ {item.get("sale_fee", 0)}')
                print()
                
                # Verificar shipping no item
                item_shipping = item.get('shipping', {})
                if item_shipping:
                    print(f'   🚚 SHIPPING DO ITEM: {item_shipping}')
                print()
        
        # Verificar estrutura completa para encontrar custos de frete
        print('🔍 VERIFICANDO TODOS OS CAMPOS DE FRETE:')
        
        def buscar_frete_recursivo(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        buscar_frete_recursivo(value, current_path)
                    elif 'shipping' in key.lower() or 'frete' in key.lower() or 'envio' in key.lower():
                        print(f'   {current_path}: {value}')
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    buscar_frete_recursivo(item, current_path)
        
        buscar_frete_recursivo(venda_data)
        
        # Simular a lógica atual de extração de frete
        print()
        print('🧪 SIMULANDO LÓGICA ATUAL DE EXTRAÇÃO DE FRETE:')
        
        # Primeiro tenta buscar no shipping
        frete_total = float(shipping.get('cost', 0))
        print(f'🚚 Frete do shipping: R$ {frete_total:.2f}')
        
        # Se não encontrar no shipping, busca nos pagamentos
        if frete_total == 0:
            for i, payment in enumerate(payments):
                shipping_cost = payment.get('shipping_cost', 0)
                print(f'💳 Pagamento {i+1}: shipping_cost = R$ {shipping_cost}')
                
                if shipping_cost and shipping_cost > 0:
                    frete_total = float(shipping_cost)
                    print(f'✅ Frete encontrado no pagamento: R$ {frete_total:.2f}')
                    break
        
        # Se ainda não encontrar, busca em billing_info
        if frete_total == 0:
            if billing:
                shipping_cost = billing.get('shipping_cost', 0)
                print(f'💰 Shipping cost no billing: R$ {shipping_cost}')
                
                if shipping_cost and shipping_cost > 0:
                    frete_total = float(shipping_cost)
                    print(f'✅ Frete encontrado no billing: R$ {frete_total:.2f}')
        
        print(f'🎯 FRETE FINAL CALCULADO: R$ {frete_total:.2f}')
        
        if frete_total == 0:
            print('❌ PROBLEMA: Frete não foi encontrado em nenhuma fonte!')
            print('   Preciso investigar onde está o custo de R$ 26,95')
        else:
            print('✅ Frete foi encontrado corretamente!')
        
    else:
        print('❌ Erro ao obter dados da venda')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
