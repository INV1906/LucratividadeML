#!/usr/bin/env python3
"""
Script para debugar a estrutura de frete da API do Mercado Livre
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI

load_dotenv()

try:
    print('🔍 DEBUGANDO ESTRUTURA DE FRETE DA API')
    print('=' * 50)
    
    # Inicializar API
    api = MercadoLivreAPI()
    
    # Buscar uma venda de exemplo
    user_id = 1305538297
    order_ids = api.obter_todos_ids_vendas(user_id)
    
    if order_ids:
        # Pegar a primeira venda
        venda_id = order_ids[0]
        print(f'📦 Analisando venda: {venda_id}')
        
        # Buscar detalhes da venda
        from database import DatabaseManager
        db = DatabaseManager()
        access_token = db.obter_access_token(user_id)
        venda_data = api.obter_venda_por_id(venda_id, access_token)
        
        if venda_data:
            print('✅ Dados da venda obtidos!')
            
            # Verificar estrutura de shipping
            shipping = venda_data.get('shipping', {})
            print(f'🚚 Estrutura shipping: {shipping}')
            
            # Verificar billing_info
            billing = venda_data.get('billing_info', {})
            print(f'💰 Estrutura billing_info: {billing}')
            
            # Verificar order_items
            order_items = venda_data.get('order_items', [])
            print(f'📦 Total de itens: {len(order_items)}')
            
            if order_items:
                item = order_items[0]
                print(f'📋 Primeiro item: {item}')
                
                # Verificar se há shipping no item
                item_shipping = item.get('shipping', {})
                print(f'🚚 Shipping do item: {item_shipping}')
            
            # Verificar payments
            payments = venda_data.get('payments', [])
            print(f'💳 Total de pagamentos: {len(payments)}')
            
            if payments:
                payment = payments[0]
                print(f'💳 Primeiro pagamento: {payment}')
                
                # Verificar shipping_cost no pagamento
                shipping_cost = payment.get('shipping_cost', {})
                print(f'🚚 Shipping cost no pagamento: {shipping_cost}')
        else:
            print('❌ Erro ao obter dados da venda')
    else:
        print('❌ Nenhuma venda encontrada')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
