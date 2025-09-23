#!/usr/bin/env python3
"""
Script para testar a importação simulada e ver se a função está sendo chamada
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🧪 TESTANDO IMPORTAÇÃO SIMULADA')
    print('=' * 50)
    
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
        
        # Simular chamada da função salvar_venda_com_status
        print('💾 Simulando salvar_venda_com_status...')
        
        try:
            # Chamar a função diretamente
            resultado = db.salvar_venda_com_status(venda_data, user_id)
            
            if resultado:
                print('✅ Função executada com sucesso!')
                
                # Verificar se o frete foi salvo
                conn = db.conectar()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT frete_total FROM vendas WHERE venda_id = %s
                    """, (venda_id,))
                    
                    frete_salvo = cursor.fetchone()[0]
                    print(f'📊 Frete salvo no banco: R$ {frete_salvo:.2f}')
                    
                    if frete_salvo > 0:
                        print('✅ Frete foi salvo corretamente!')
                    else:
                        print('❌ Frete não foi salvo!')
                        print('   Há um problema na função salvar_venda_com_status')
                    
                    conn.close()
            else:
                print('❌ Função retornou False')
                
        except Exception as e:
            print(f'❌ Erro ao executar salvar_venda_com_status: {e}')
            import traceback
            traceback.print_exc()
    
    else:
        print('❌ Erro ao obter dados da venda')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
