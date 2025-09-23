#!/usr/bin/env python3
"""
Script para reimportar algumas vendas com a correção de frete aplicada
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager

load_dotenv()

try:
    print('🔄 REIMPORTANDO VENDAS COM CORREÇÃO DE FRETE')
    print('=' * 60)
    
    # Inicializar API e Database
    api = MercadoLivreAPI()
    db = DatabaseManager()
    
    user_id = 1305538297
    
    # Obter access token
    access_token = db.obter_access_token(user_id)
    if not access_token:
        print('❌ Erro: Não foi possível obter access token')
        exit()
    
    # Buscar algumas vendas recentes para reimportar
    order_ids = api.obter_todos_ids_vendas(user_id)
    
    if order_ids:
        # Pegar as 5 vendas mais recentes
        vendas_para_reimportar = order_ids[:5]
        
        print(f'📦 Reimportando {len(vendas_para_reimportar)} vendas recentes...')
        
        vendas_com_frete = 0
        total_frete = 0
        
        for i, venda_id in enumerate(vendas_para_reimportar):
            print(f'🔄 Reimportando venda {i+1}/{len(vendas_para_reimportar)}: {venda_id}')
            
            try:
                # Buscar dados da venda
                venda_data = api.obter_venda_por_id(venda_id, access_token)
                
                if venda_data:
                    # Salvar venda com a correção de frete aplicada
                    resultado = db.salvar_venda_com_status(venda_data, user_id)
                    
                    if resultado['sucesso']:
                        # Verificar se o frete foi capturado
                        frete_capturado = resultado.get('frete_total', 0)
                        if frete_capturado > 0:
                            vendas_com_frete += 1
                            total_frete += frete_capturado
                            print(f'   ✅ Frete capturado: R$ {frete_capturado:.2f}')
                        else:
                            print(f'   ℹ️ Frete: R$ 0,00 (frete grátis)')
                    else:
                        print(f'   ❌ Erro ao salvar: {resultado.get("erro", "Erro desconhecido")}')
                else:
                    print(f'   ❌ Erro ao obter dados da venda')
                    
            except Exception as e:
                print(f'   ❌ Erro: {e}')
        
        print()
        print('📊 RESULTADO DA REIMPORTAÇÃO:')
        print(f'   Vendas processadas: {len(vendas_para_reimportar)}')
        print(f'   Vendas com frete > 0: {vendas_com_frete}')
        print(f'   Total de frete capturado: R$ {total_frete:.2f}')
        
        if vendas_com_frete > 0:
            print('✅ CORREÇÃO FUNCIONANDO! Custos de frete foram capturados.')
        else:
            print('ℹ️ Todas as vendas têm frete grátis (R$ 0,00)')
        
    else:
        print('❌ Nenhuma venda encontrada')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
