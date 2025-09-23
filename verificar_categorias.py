#!/usr/bin/env python3
"""
Script para verificar dados de categorias no banco
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
    
    print('🔍 VERIFICANDO DADOS DE CATEGORIAS')
    print('=' * 50)
    
    # Verificar se há vendas
    cursor.execute('SELECT COUNT(*) FROM vendas')
    total_vendas = cursor.fetchone()[0]
    print(f'📊 Total de vendas: {total_vendas}')
    
    # Verificar se há itens de venda
    cursor.execute('SELECT COUNT(*) FROM venda_itens')
    total_itens = cursor.fetchone()[0]
    print(f'📦 Total de itens de venda: {total_itens}')
    
    # Verificar categorias em venda_itens
    cursor.execute('SELECT COUNT(DISTINCT categoria_nome) FROM venda_itens WHERE categoria_nome IS NOT NULL AND categoria_nome != ""')
    categorias_itens = cursor.fetchone()[0]
    print(f'🏷️ Categorias em venda_itens: {categorias_itens}')
    
    # Verificar produtos
    cursor.execute('SELECT COUNT(*) FROM produtos')
    total_produtos = cursor.fetchone()[0]
    print(f'🛍️ Total de produtos: {total_produtos}')
    
    # Verificar categorias em produtos
    cursor.execute('SELECT COUNT(DISTINCT category) FROM produtos WHERE category IS NOT NULL AND category != ""')
    categorias_produtos = cursor.fetchone()[0]
    print(f'🏷️ Categorias em produtos: {categorias_produtos}')
    
    # Mostrar algumas categorias de exemplo
    cursor.execute('SELECT DISTINCT categoria_nome FROM venda_itens WHERE categoria_nome IS NOT NULL AND categoria_nome != "" LIMIT 5')
    exemplos = cursor.fetchall()
    print(f'📋 Exemplos de categorias: {[e[0] for e in exemplos]}')
    
    # Verificar estrutura da tabela venda_itens
    cursor.execute('DESCRIBE venda_itens')
    estrutura = cursor.fetchall()
    print(f'🏗️ Estrutura venda_itens: {[col[0] for col in estrutura]}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
