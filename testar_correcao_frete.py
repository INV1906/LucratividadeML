#!/usr/bin/env python3
"""
Script para testar a correção do frete com uma venda existente
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🧪 TESTANDO CORREÇÃO DO FRETE')
    print('=' * 50)
    
    # Inicializar API e Database
    api = MercadoLivreAPI()
    db = DatabaseManager()
    
    user_id = 1305538297
    
    # Obter access token
    access_token = db.obter_access_token(user_id)
    if not access_token:
        print('❌ Erro: Não foi possível obter access token')
        exit()
    
    # Buscar uma venda existente para testar
    order_ids = api.obter_todos_ids_vendas(user_id)
    
    if order_ids:
        # Pegar uma venda recente
        venda_id = order_ids[0]
        print(f'📦 Testando com venda: {venda_id}')
        
        # Buscar dados da venda
        venda_data = api.obter_venda_por_id(venda_id, access_token)
        
        if venda_data:
            print('✅ Dados da venda obtidos!')
            
            # Simular a lógica corrigida de extração de frete
            shipping = venda_data.get('shipping', {})
            frete_total = float(shipping.get('cost', 0))
            
            print(f'🚚 Frete do shipping: R$ {frete_total:.2f}')
            
            # Se não encontrar no shipping, busca nos pagamentos
            if frete_total == 0:
                payments = venda_data.get('payments', [])
                print(f'💳 Total de pagamentos: {len(payments)}')
                
                for i, payment in enumerate(payments):
                    shipping_cost = payment.get('shipping_cost', 0)
                    print(f'   Pagamento {i+1}: shipping_cost = R$ {shipping_cost}')
                    
                    if shipping_cost and shipping_cost > 0:
                        frete_total = float(shipping_cost)
                        print(f'✅ Frete encontrado no pagamento: R$ {frete_total:.2f}')
                        break
            
            # Se ainda não encontrar, busca em billing_info
            if frete_total == 0:
                billing = venda_data.get('billing_info', {})
                print(f'💰 Billing info: {billing}')
                
                if billing:
                    shipping_cost = billing.get('shipping_cost', 0)
                    print(f'   Shipping cost no billing: R$ {shipping_cost}')
                    
                    if shipping_cost and shipping_cost > 0:
                        frete_total = float(shipping_cost)
                        print(f'✅ Frete encontrado no billing: R$ {frete_total:.2f}')
            
            print(f'🎯 FRETE FINAL CALCULADO: R$ {frete_total:.2f}')
            
            # Verificar se há outros campos que podem conter custos de frete
            print()
            print('🔍 VERIFICANDO OUTROS CAMPOS DE FRETE:')
            
            # Verificar estrutura completa para encontrar custos de frete
            for key, value in venda_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if 'shipping' in sub_key.lower() or 'frete' in sub_key.lower() or 'envio' in sub_key.lower():
                            print(f'   {key}.{sub_key}: {sub_value}')
                elif isinstance(value, list) and len(value) > 0:
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            for sub_key, sub_value in item.items():
                                if 'shipping' in sub_key.lower() or 'frete' in sub_key.lower() or 'envio' in sub_key.lower():
                                    print(f'   {key}[{i}].{sub_key}: {sub_value}')
        
        else:
            print('❌ Erro ao obter dados da venda')
    else:
        print('❌ Nenhuma venda encontrada')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
