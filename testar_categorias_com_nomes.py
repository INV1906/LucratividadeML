#!/usr/bin/env python3
"""
Script para testar se as categorias estão sendo retornadas com nomes
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
    
    print('🧪 TESTANDO CATEGORIAS COM NOMES')
    print('=' * 50)
    
    # Simular a consulta da função obter_dados_categorias_vendas
    user_id = 1  # Assumindo user_id = 1
    
    cursor.execute("""
        SELECT 
            COALESCE(
                (SELECT name FROM categorias_mlb WHERE id = vi.categoria_nome LIMIT 1),
                vi.categoria_nome, 
                'Sem categoria'
            ) as categoria_nome,
            COUNT(*) as vendas,
            SUM(vi.preco_total) as receita
        FROM venda_itens vi
        WHERE vi.user_id = %s
        AND vi.categoria_nome IS NOT NULL AND vi.categoria_nome != ''
        GROUP BY vi.categoria_nome
        ORDER BY vendas DESC
        LIMIT 10
    """, (user_id,))
    
    categorias_data = cursor.fetchall()
    
    print(f'📊 Categorias encontradas: {len(categorias_data)}')
    print()
    
    for categoria_nome, vendas, receita in categorias_data:
        print(f'🏷️ {categoria_nome}: {vendas} vendas, R$ {receita:.2f}')
    
    # Verificar se há categorias sem nome (apenas código)
    cursor.execute("""
        SELECT 
            vi.categoria_nome,
            c.name,
            COUNT(*) as vendas
        FROM venda_itens vi
        LEFT JOIN categorias_mlb c ON c.id = vi.categoria_nome
        WHERE vi.user_id = %s
        AND vi.categoria_nome IS NOT NULL AND vi.categoria_nome != ''
        AND c.name IS NULL
        GROUP BY vi.categoria_nome
        LIMIT 5
    """, (user_id,))
    
    categorias_sem_nome = cursor.fetchall()
    
    if categorias_sem_nome:
        print()
        print('⚠️ Categorias sem nome encontradas:')
        for codigo, nome, vendas in categorias_sem_nome:
            print(f'   {codigo}: {vendas} vendas (nome: {nome})')
    else:
        print()
        print('✅ Todas as categorias têm nomes!')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
