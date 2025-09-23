#!/usr/bin/env python3
"""
Script para verificar o estado da venda após nova importação
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
    
    print('🔍 VERIFICANDO VENDA APÓS NOVA IMPORTAÇÃO')
    print('=' * 60)
    
    venda_id = '2000013113228770'
    
    # Verificar dados atuais
    cursor.execute("""
        SELECT venda_id, valor_total, taxa_ml, frete_total, data_aprovacao, updated_at
        FROM vendas 
        WHERE venda_id = %s
    """, (venda_id,))
    
    venda_atual = cursor.fetchone()
    
    if venda_atual:
        venda_id_db, valor_total, taxa_ml, frete_total, data_aprovacao, updated_at = venda_atual
        
        print('📊 DADOS ATUAIS:')
        print(f'   Venda ID: {venda_id_db}')
        print(f'   Valor Total: R$ {valor_total:.2f}')
        print(f'   Taxa ML: R$ {taxa_ml:.2f}')
        print(f'   Frete Total: R$ {frete_total:.2f}')
        print(f'   Data Aprovação: {data_aprovacao}')
        print(f'   Última Atualização: {updated_at}')
        print()
        
        # Verificar se os dados estão corretos
        if frete_total == 0:
            print('❌ PROBLEMA: Frete está como R$ 0,00 novamente!')
            print('   A nova importação sobrescreveu os dados corrigidos')
            print()
            
            # Aplicar correção novamente
            print('🔧 APLICANDO CORREÇÃO NOVAMENTE...')
            
            # Buscar frete na API de shipments
            from database import DatabaseManager
            db = DatabaseManager()
            
            # Obter shipping_id da venda
            cursor.execute("""
                SELECT venda_id FROM vendas WHERE venda_id = %s
            """, (venda_id,))
            
            if cursor.fetchone():
                # Buscar dados da venda da API
                from meli_api import MercadoLivreAPI
                api = MercadoLivreAPI()
                
                user_id = 1305538297
                access_token = db.obter_access_token(user_id)
                
                if access_token:
                    venda_data = api.obter_venda_por_id(venda_id, access_token)
                    
                    if venda_data:
                        shipping = venda_data.get('shipping', {})
                        shipping_id = shipping.get('id')
                        
                        if shipping_id:
                            print(f'🚚 Buscando frete para shipping_id: {shipping_id}')
                            
                            # Buscar frete na API de shipments
                            frete_valor = db._buscar_frete_shipments(shipping_id, user_id)
                            
                            if frete_valor:
                                print(f'✅ Frete encontrado: R$ {frete_valor:.2f}')
                                
                                # Atualizar banco
                                cursor.execute("""
                                    UPDATE vendas 
                                    SET frete_total = %s
                                    WHERE venda_id = %s
                                """, (frete_valor, venda_id))
                                
                                conn.commit()
                                
                                print('✅ Banco atualizado com frete correto!')
                                
                                # Verificar atualização
                                cursor.execute("""
                                    SELECT frete_total FROM vendas WHERE venda_id = %s
                                """, (venda_id,))
                                
                                frete_atualizado = cursor.fetchone()[0]
                                print(f'📊 Frete atualizado: R$ {frete_atualizado:.2f}')
                                
                            else:
                                print('❌ Frete não encontrado na API de shipments')
                        else:
                            print('❌ Shipping ID não encontrado')
                    else:
                        print('❌ Erro ao obter dados da venda da API')
                else:
                    print('❌ Erro ao obter access token')
        else:
            print('✅ Frete está correto!')
    
    else:
        print('❌ Venda não encontrada no banco de dados')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
