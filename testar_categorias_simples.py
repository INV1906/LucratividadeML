#!/usr/bin/env python3
"""
Script para testar categorias com nomes (versão simples)
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
    
    print('🧪 TESTANDO CATEGORIAS COM NOMES (VERSÃO SIMPLES)')
    print('=' * 60)
    
    user_id = 1305538297  # User ID correto com dados
    
    # Buscar vendas por categoria (sem nomes)
    cursor.execute("""
        SELECT 
            vi.categoria_nome,
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
    
    # Buscar nomes das categorias
    cursor.execute("SELECT id, name FROM categorias_mlb")
    categorias_mlb = {row[0]: row[1] for row in cursor.fetchall()}
    
    print(f'📊 Categorias encontradas: {len(categorias_data)}')
    print(f'🏷️ Total de categorias MLB: {len(categorias_mlb)}')
    print()
    
    print('📋 CATEGORIAS COM NOMES:')
    for categoria_codigo, vendas_count, receita in categorias_data:
        categoria_nome = categorias_mlb.get(categoria_codigo, categoria_codigo)
        print(f'   {categoria_nome} ({categoria_codigo}): {vendas_count} vendas, R$ {receita:.2f}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
