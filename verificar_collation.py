#!/usr/bin/env python3
"""
Script para verificar collation das tabelas
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
    
    print('🔍 VERIFICANDO COLLATION DAS TABELAS')
    print('=' * 50)
    
    # Verificar collation da tabela venda_itens
    cursor.execute("SHOW TABLE STATUS LIKE 'venda_itens'")
    status_venda_itens = cursor.fetchone()
    print(f'📊 Collation venda_itens: {status_venda_itens[14] if status_venda_itens else "N/A"}')
    
    # Verificar collation da tabela categorias_mlb
    cursor.execute("SHOW TABLE STATUS LIKE 'categorias_mlb'")
    status_categorias = cursor.fetchone()
    print(f'🏷️ Collation categorias_mlb: {status_categorias[14] if status_categorias else "N/A"}')
    
    # Verificar collation das colunas específicas
    cursor.execute("SHOW FULL COLUMNS FROM venda_itens WHERE Field = 'categoria_nome'")
    col_venda_itens = cursor.fetchone()
    print(f'📝 Collation categoria_nome: {col_venda_itens[2] if col_venda_itens else "N/A"}')
    
    cursor.execute("SHOW FULL COLUMNS FROM categorias_mlb WHERE Field = 'id'")
    col_categorias_id = cursor.fetchone()
    print(f'📝 Collation categorias_mlb.id: {col_categorias_id[2] if col_categorias_id else "N/A"}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
