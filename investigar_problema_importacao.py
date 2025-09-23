#!/usr/bin/env python3
"""
Script para investigar por que a função de busca de frete não está sendo chamada durante a importação
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🔍 INVESTIGANDO PROBLEMA NA IMPORTAÇÃO')
    print('=' * 60)
    
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
    
    # Buscar dados da venda
    print(f'🔍 Buscando dados da venda {venda_id}...')
    venda_data = api.obter_venda_por_id(venda_id, access_token)
    
    if venda_data:
        print('✅ Dados da venda obtidos!')
        
        # Simular a lógica de salvar_venda_com_status
        print('🧪 SIMULANDO LÓGICA DE IMPORTAÇÃO:')
        
        # Extrair shipping
        shipping = venda_data.get('shipping', {})
        print(f'🚚 Shipping: {shipping}')
        
        # Primeiro tenta buscar no shipping
        frete_total = float(shipping.get('cost', 0))
        print(f'🚚 Frete do shipping: R$ {frete_total:.2f}')
        
        # Se não encontrar no shipping, busca nos pagamentos
        if frete_total == 0:
            payments = venda_data.get('payments', [])
            for payment in payments:
                shipping_cost = payment.get('shipping_cost', 0)
                print(f'💳 Pagamento shipping_cost: R$ {shipping_cost}')
                
                if shipping_cost and shipping_cost > 0:
                    frete_total = float(shipping_cost)
                    print(f'✅ Frete encontrado no pagamento: R$ {frete_total:.2f}')
                    break
        
        # Se ainda não encontrar, busca em billing_info
        if frete_total == 0:
            billing = venda_data.get('billing_info', {})
            if billing:
                shipping_cost = billing.get('shipping_cost', 0)
                print(f'💰 Billing shipping_cost: R$ {shipping_cost}')
                
                if shipping_cost and shipping_cost > 0:
                    frete_total = float(shipping_cost)
                    print(f'✅ Frete encontrado no billing: R$ {frete_total:.2f}')
        
        # Se ainda não encontrar frete, busca na API de shipments
        if frete_total == 0:
            shipping_id = shipping.get('id')
            print(f'🚚 Shipping ID: {shipping_id}')
            
            if shipping_id:
                try:
                    print('🔍 Buscando frete na API de shipments...')
                    frete_data = db._buscar_frete_shipments(shipping_id, user_id)
                    
                    if frete_data:
                        frete_total = float(frete_data)
                        print(f'✅ Frete encontrado na API de shipments: R$ {frete_total:.2f}')
                    else:
                        print('❌ Frete não encontrado na API de shipments')
                        
                except Exception as e:
                    print(f'❌ Erro ao buscar frete na API de shipments: {e}')
            else:
                print('❌ Shipping ID não encontrado')
        
        print(f'🎯 FRETE FINAL: R$ {frete_total:.2f}')
        
        if frete_total == 0:
            print('❌ PROBLEMA: Frete não foi encontrado em nenhuma fonte!')
            print('   Isso explica por que a importação não está funcionando')
        else:
            print('✅ Frete foi encontrado corretamente!')
            print('   O problema pode estar na função salvar_venda_com_status')
    
    else:
        print('❌ Erro ao obter dados da venda')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
