#!/usr/bin/env python3
"""
Script para testar a correção com busca na API de shipments
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🧪 TESTANDO CORREÇÃO COM API DE SHIPMENTS')
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
        
        # Extrair shipping_id
        shipping = venda_data.get('shipping', {})
        shipping_id = shipping.get('id')
        
        print(f'🚚 Shipping ID: {shipping_id}')
        
        if shipping_id:
            # Testar busca na API de shipments
            print(f'🔍 Buscando frete na API de shipments...')
            frete_valor = db._buscar_frete_shipments(shipping_id, user_id)
            
            if frete_valor:
                print(f'✅ Frete encontrado: R$ {frete_valor:.2f}')
                
                # Atualizar banco de dados
                print('💾 Atualizando banco de dados...')
                conn = db.conectar()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE vendas 
                        SET frete_total = %s
                        WHERE venda_id = %s
                    """, (frete_valor, venda_id))
                    conn.commit()
                    conn.close()
                    
                    print('✅ Banco de dados atualizado!')
                    
                    # Verificar atualização
                    conn = db.conectar()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT valor_total, taxa_ml, frete_total
                            FROM vendas 
                            WHERE venda_id = %s
                        """, (venda_id,))
                        
                        venda_atualizada = cursor.fetchone()
                        if venda_atualizada:
                            print('📊 DADOS ATUALIZADOS:')
                            print(f'   Valor Total: R$ {venda_atualizada[0]:.2f}')
                            print(f'   Taxa ML: R$ {venda_atualizada[1]:.2f}')
                            print(f'   Frete Total: R$ {venda_atualizada[2]:.2f}')
                        
                        conn.close()
            else:
                print('❌ Frete não encontrado na API de shipments')
        else:
            print('❌ Shipping ID não encontrado')
    
    else:
        print('❌ Erro ao obter dados da venda')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
