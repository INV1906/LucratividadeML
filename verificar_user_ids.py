#!/usr/bin/env python3
"""
Script para verificar quais user_ids têm dados
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
    
    print('🔍 VERIFICANDO USER_IDS COM DADOS')
    print('=' * 50)
    
    # Verificar user_ids na tabela venda_itens
    cursor.execute("SELECT DISTINCT user_id FROM venda_itens ORDER BY user_id")
    user_ids = cursor.fetchall()
    print(f'👥 User IDs em venda_itens: {[uid[0] for uid in user_ids]}')
    
    # Verificar quantas vendas cada user_id tem
    cursor.execute("""
        SELECT user_id, COUNT(*) as total_vendas
        FROM venda_itens 
        GROUP BY user_id 
        ORDER BY total_vendas DESC
    """)
    vendas_por_user = cursor.fetchall()
    print(f'📊 Vendas por user_id: {vendas_por_user}')
    
    # Verificar categorias por user_id
    cursor.execute("""
        SELECT user_id, COUNT(DISTINCT categoria_nome) as categorias
        FROM venda_itens 
        WHERE categoria_nome IS NOT NULL AND categoria_nome != ''
        GROUP BY user_id 
        ORDER BY categorias DESC
    """)
    categorias_por_user = cursor.fetchall()
    print(f'🏷️ Categorias por user_id: {categorias_por_user}')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
