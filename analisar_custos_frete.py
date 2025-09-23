#!/usr/bin/env python3
"""
Script para analisar custos de frete em vendas existentes
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
    
    print('🔍 ANALISANDO CUSTOS DE FRETE EM VENDAS EXISTENTES')
    print('=' * 60)
    
    # Verificar vendas com valores altos (que podem ter frete)
    cursor.execute("""
        SELECT 
            venda_id, valor_total, taxa_ml, frete_total, 
            data_aprovacao, comprador_nome
        FROM vendas 
        WHERE valor_total > 1000
        ORDER BY valor_total DESC
        LIMIT 10
    """)
    
    vendas_altas = cursor.fetchall()
    
    print('📊 VENDAS COM VALORES ALTOS (> R$ 1000):')
    for venda in vendas_altas:
        print(f'   {venda[0]}: R$ {venda[1]:.2f} | Taxa: R$ {venda[2]:.2f} | Frete: R$ {venda[3]:.2f} | {venda[4]}')
    print()
    
    # Verificar se há vendas com taxa_ml alta (que podem incluir custos de frete)
    cursor.execute("""
        SELECT 
            venda_id, valor_total, taxa_ml, frete_total,
            (taxa_ml / valor_total * 100) as percentual_taxa
        FROM vendas 
        WHERE taxa_ml > 100
        ORDER BY taxa_ml DESC
        LIMIT 10
    """)
    
    vendas_taxa_alta = cursor.fetchall()
    
    print('📊 VENDAS COM TAXA ML ALTA (> R$ 100):')
    for venda in vendas_taxa_alta:
        print(f'   {venda[0]}: Valor R$ {venda[1]:.2f} | Taxa R$ {venda[2]:.2f} ({venda[4]:.1f}%) | Frete R$ {venda[3]:.2f}')
    print()
    
    # Verificar estrutura da tabela venda_pagamentos
    cursor.execute("DESCRIBE venda_pagamentos")
    estrutura_pagamentos = cursor.fetchall()
    print('🏗️ ESTRUTURA TABELA venda_pagamentos:')
    for coluna in estrutura_pagamentos:
        print(f'   {coluna[0]}: {coluna[1]}')
    print()
    
    # Verificar se há dados na tabela venda_pagamentos
    cursor.execute("SELECT COUNT(*) FROM venda_pagamentos")
    total_pagamentos = cursor.fetchone()[0]
    print(f'📊 Total de registros em venda_pagamentos: {total_pagamentos}')
    
    if total_pagamentos > 0:
        cursor.execute("SELECT * FROM venda_pagamentos LIMIT 3")
        exemplos_pagamentos = cursor.fetchall()
        print('📋 Exemplos de pagamentos:')
        for pagamento in exemplos_pagamentos:
            print(f'   {pagamento}')
    
    # Verificar se há campos relacionados a frete nas tabelas
    cursor.execute("SHOW TABLES")
    tabelas = cursor.fetchall()
    
    print()
    print('🔍 VERIFICANDO TABELAS RELACIONADAS A FRETE:')
    for tabela in tabelas:
        nome_tabela = tabela[0]
        if 'frete' in nome_tabela.lower() or 'shipping' in nome_tabela.lower() or 'envio' in nome_tabela.lower():
            cursor.execute(f"DESCRIBE {nome_tabela}")
            estrutura = cursor.fetchall()
            print(f'📋 {nome_tabela}:')
            for coluna in estrutura:
                print(f'   {coluna[0]}: {coluna[1]}')
            print()
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
