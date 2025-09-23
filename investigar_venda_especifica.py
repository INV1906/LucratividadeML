#!/usr/bin/env python3
"""
Script para investigar a venda específica 2000009288172661
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
    
    print('🔍 INVESTIGANDO VENDA ESPECÍFICA: 2000009288172661')
    print('=' * 60)
    
    venda_id = '2000009288172661'
    
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
            print('❌ Nenhum dado de frete encontrado')
        
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
            print('❌ Nenhum dado de pagamento encontrado')
            
    else:
        print('❌ VENDA NÃO ENCONTRADA NO BANCO DE DADOS')
        print('   Isso pode indicar que a venda não foi importada ainda')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
