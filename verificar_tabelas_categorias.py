#!/usr/bin/env python3
"""
Script para verificar tabelas de categorias
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
    
    print('🔍 VERIFICANDO TABELAS DE CATEGORIAS')
    print('=' * 50)
    
    # Verificar tabelas existentes
    cursor.execute('SHOW TABLES LIKE "%categoria%"')
    tabelas_categoria = cursor.fetchall()
    print(f'📋 Tabelas com categoria: {[t[0] for t in tabelas_categoria]}')
    
    # Verificar tabela categorias_mlb se existir
    cursor.execute('SHOW TABLES LIKE "categorias_mlb"')
    if cursor.fetchone():
        cursor.execute('SELECT COUNT(*) FROM categorias_mlb')
        total_categorias_mlb = cursor.fetchone()[0]
        print(f'🏷️ Total de categorias MLB: {total_categorias_mlb}')
        
        # Mostrar algumas categorias de exemplo
        cursor.execute('SELECT id, name FROM categorias_mlb LIMIT 5')
        exemplos = cursor.fetchall()
        print(f'📋 Exemplos categorias MLB: {exemplos}')
    else:
        print('❌ Tabela categorias_mlb não existe')
    
    # Verificar estrutura da tabela produtos
    cursor.execute('DESCRIBE produtos')
    estrutura_produtos = cursor.fetchall()
    print(f'🏗️ Estrutura produtos: {[col[0] for col in estrutura_produtos]}')
    
    # Verificar se há coluna category_name na tabela produtos
    cursor.execute('SHOW COLUMNS FROM produtos LIKE "%name%"')
    colunas_name = cursor.fetchall()
    print(f'📝 Colunas com name em produtos: {[col[0] for col in colunas_name]}')
    
    # Verificar dados de exemplo da tabela produtos
    cursor.execute('SELECT category, category_name FROM produtos WHERE category IS NOT NULL LIMIT 5')
    exemplos_produtos = cursor.fetchall()
    print(f'🛍️ Exemplos produtos (category, category_name): {exemplos_produtos}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
