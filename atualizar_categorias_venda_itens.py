#!/usr/bin/env python3
"""
Script para atualizar categorias na tabela venda_itens
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
    
    print('🔄 ATUALIZANDO CATEGORIAS EM VENDA_ITENS')
    print('=' * 50)
    
    # Verificar quantos itens precisam ser atualizados
    cursor.execute('''
        SELECT COUNT(*) FROM venda_itens vi 
        WHERE vi.categoria_nome IS NULL OR vi.categoria_nome = ""
    ''')
    itens_sem_categoria = cursor.fetchone()[0]
    print(f'📦 Itens sem categoria: {itens_sem_categoria}')
    
    # Atualizar categorias usando dados da tabela produtos
    cursor.execute('''
        UPDATE venda_itens vi
        JOIN produtos p ON p.mlb = vi.item_mlb COLLATE utf8mb4_unicode_ci
        SET vi.categoria_nome = p.category
        WHERE (vi.categoria_nome IS NULL OR vi.categoria_nome = "")
        AND p.category IS NOT NULL AND p.category != ""
    ''')
    
    linhas_afetadas = cursor.rowcount
    print(f'✅ Linhas atualizadas: {linhas_afetadas}')
    
    # Verificar resultado
    cursor.execute('''
        SELECT COUNT(DISTINCT categoria_nome) 
        FROM venda_itens 
        WHERE categoria_nome IS NOT NULL AND categoria_nome != ""
    ''')
    categorias_agora = cursor.fetchone()[0]
    print(f'🏷️ Categorias agora disponíveis: {categorias_agora}')
    
    # Mostrar algumas categorias de exemplo
    cursor.execute('''
        SELECT DISTINCT categoria_nome 
        FROM venda_itens 
        WHERE categoria_nome IS NOT NULL AND categoria_nome != ""
        LIMIT 5
    ''')
    exemplos = cursor.fetchall()
    print(f'📋 Exemplos de categorias: {[e[0] for e in exemplos]}')
    
    conn.commit()
    conn.close()
    
    print('🎉 Atualização concluída!')
    
except Exception as e:
    print(f'❌ Erro: {e}')
