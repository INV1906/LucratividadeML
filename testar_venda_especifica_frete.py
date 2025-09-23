#!/usr/bin/env python3
"""
Script para testar especificamente a venda 2000013113228770 com frete
"""

import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'lucratividade_ml')
    )
    
    cursor = conn.cursor()
    
    print('🔍 TESTANDO VENDA ESPECÍFICA COM FRETE: 2000013113228770')
    print('=' * 70)
    
    venda_id = '2000013113228770'
    
    # Verificar se a venda existe no banco
    cursor.execute("""
        SELECT 
            venda_id, pack_id, valor_total, taxa_ml, frete_total, 
            total_produtos, status, data_aprovacao, comprador_nome
        FROM vendas 
        WHERE venda_id = %s
    """, (venda_id,))
    
    venda = cursor.fetchone()
    
    if venda:
        print('✅ VENDA ENCONTRADA NO BANCO:')
        print(f'   Venda ID: {venda[0]}')
        print(f'   Pack ID: {venda[1]}')
        print(f'   Valor Total: R$ {venda[2]:.2f}')
        print(f'   Taxa ML: R$ {venda[3]:.2f}')
        print(f'   Frete Total: R$ {venda[4]:.2f}')
        print(f'   Total Produtos: {venda[5]}')
        print(f'   Status: {venda[6]}')
        print(f'   Data Aprovação: {venda[7]}')
        print(f'   Comprador: {venda[8]}')
        print()
        
        # Verificar itens da venda
        cursor.execute("""
            SELECT item_mlb, item_titulo, quantidade, preco_unitario, preco_total
            FROM venda_itens 
            WHERE venda_id = %s
        """, (venda_id,))
        
        itens = cursor.fetchall()
        print('📦 ITENS DA VENDA:')
        for item in itens:
            print(f'   MLB: {item[0]}')
            print(f'   Título: {item[1]}')
            print(f'   Quantidade: {item[2]}')
            print(f'   Preço Unitário: R$ {item[3]:.2f}')
            print(f'   Preço Total: R$ {item[4]:.2f}')
            print()
        
        # Verificar dados de frete específicos
        cursor.execute("""
            SELECT * FROM venda_fretes 
            WHERE venda_id = %s
        """, (venda_id,))
        
        frete_data = cursor.fetchone()
        if frete_data:
            print('🚚 DADOS DE FRETE:')
            print(f'   {frete_data}')
        else:
            print('❌ Nenhum dado de frete encontrado na tabela venda_fretes')
        
        # Verificar dados de pagamento
        cursor.execute("""
            SELECT * FROM venda_pagamentos 
            WHERE venda_id = %s
        """, (venda_id,))
        
        pagamento_data = cursor.fetchall()
        if pagamento_data:
            print('💳 DADOS DE PAGAMENTO:')
            for pagamento in pagamento_data:
                print(f'   {pagamento}')
        else:
            print('❌ Nenhum dado de pagamento encontrado na tabela venda_pagamentos')
            
    else:
        print('❌ VENDA NÃO ENCONTRADA NO BANCO DE DADOS')
        print('   Isso indica que a venda não foi importada ainda')
        print('   Vou tentar importá-la agora...')
        
        # Tentar importar a venda
        from meli_api import MercadoLivreAPI
        from database import DatabaseManager
        
        api = MercadoLivreAPI()
        db = DatabaseManager()
        
        user_id = 1305538297
        access_token = db.obter_access_token(user_id)
        
        if access_token:
            print(f'✅ Access token obtido: {access_token[:20]}...')
            
            # Buscar dados da venda
            print(f'🔍 Buscando dados da venda {venda_id}...')
            venda_data = api.obter_venda_por_id(venda_id, access_token)
            
            if venda_data:
                print('✅ Dados da venda obtidos!')
                
                # Analisar estrutura de shipping
                shipping = venda_data.get('shipping', {})
                print('🚚 ESTRUTURA SHIPPING:')
                print(f'   {shipping}')
                
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
                
                # Tentar salvar a venda
                print('💾 Salvando venda no banco...')
                resultado = db.salvar_venda_com_status(venda_data, user_id)
                
                if resultado:
                    print('✅ Venda salva com sucesso!')
                    
                    # Verificar novamente no banco
                    cursor.execute("""
                        SELECT venda_id, valor_total, taxa_ml, frete_total
                        FROM vendas 
                        WHERE venda_id = %s
                    """, (venda_id,))
                    
                    venda_salva = cursor.fetchone()
                    if venda_salva:
                        print('📊 DADOS SALVOS:')
                        print(f'   Venda ID: {venda_salva[0]}')
                        print(f'   Valor Total: R$ {venda_salva[1]:.2f}')
                        print(f'   Taxa ML: R$ {venda_salva[2]:.2f}')
                        print(f'   Frete Total: R$ {venda_salva[3]:.2f}')
                else:
                    print('❌ Erro ao salvar venda')
            else:
                print('❌ Erro ao obter dados da venda')
        else:
            print('❌ Erro: Não foi possível obter access token')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
