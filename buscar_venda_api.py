#!/usr/bin/env python3
"""
Script para buscar a venda específica da API do Mercado Livre
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🔍 BUSCANDO VENDA ESPECÍFICA DA API: 2000009288172661')
    print('=' * 60)
    
    # Inicializar API e Database
    api = MercadoLivreAPI()
    db = DatabaseManager()
    
    user_id = 1305538297
    venda_id = '2000009288172661'
    
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
            payment = payments[0]
            print('💳 PRIMEIRO PAGAMENTO:')
            print(f'   ID: {payment.get("id")}')
            print(f'   Transaction Amount: R$ {payment.get("transaction_amount", 0)}')
            print(f'   Shipping Cost: R$ {payment.get("shipping_cost", 0)}')
            print(f'   Marketplace Fee: R$ {payment.get("marketplace_fee", 0)}')
            print(f'   Total Paid: R$ {payment.get("total_paid_amount", 0)}')
            print()
            
            # Verificar se há dados de shipping no pagamento
            if 'shipping_cost' in payment:
                shipping_cost = payment.get('shipping_cost', 0)
                print(f'🚚 SHIPPING COST NO PAGAMENTO: R$ {shipping_cost}')
            
        # Analisar order_items
        order_items = venda_data.get('order_items', [])
        print(f'📦 TOTAL DE ITENS: {len(order_items)}')
        
        if order_items:
            item = order_items[0]
            print('📦 PRIMEIRO ITEM:')
            print(f'   MLB: {item.get("item", {}).get("id")}')
            print(f'   Título: {item.get("item", {}).get("title")}')
            print(f'   Preço Unitário: R$ {item.get("unit_price", 0)}')
            print(f'   Quantidade: {item.get("quantity", 0)}')
            print(f'   Sale Fee: R$ {item.get("sale_fee", 0)}')
            print()
        
        # Verificar se há dados de frete em outros campos
        print('🔍 VERIFICANDO OUTROS CAMPOS DE FRETE:')
        
        # Verificar se há shipping em outros lugares
        for key, value in venda_data.items():
            if 'shipping' in key.lower() or 'frete' in key.lower() or 'envio' in key.lower():
                print(f'   {key}: {value}')
        
        # Verificar estrutura completa para encontrar custos de frete
        print()
        print('🔍 ESTRUTURA COMPLETA DA VENDA:')
        for key, value in venda_data.items():
            if isinstance(value, dict) and len(str(value)) < 500:
                print(f'   {key}: {value}')
            elif isinstance(value, list) and len(value) > 0:
                print(f'   {key}: [{len(value)} itens]')
                if len(value) > 0 and isinstance(value[0], dict):
                    print(f'      Primeiro item: {value[0]}')
        
    else:
        print('❌ Erro ao obter dados da venda')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
