#!/usr/bin/env python3
"""
Script para verificar a estrutura real dos dados de frete da API
"""

import mysql.connector
from dotenv import load_dotenv
import os
import json

load_dotenv()

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'lucratividade_ml')
    )
    
    cursor = conn.cursor()
    
    print('🔍 VERIFICANDO ESTRUTURA DE FRETE')
    print('=' * 50)
    
    # Verificar se há dados de frete na tabela venda_fretes
    cursor.execute("SELECT COUNT(*) FROM venda_fretes")
    fretes_count = cursor.fetchone()[0]
    print(f'📦 Registros em venda_fretes: {fretes_count}')
    
    if fretes_count > 0:
        cursor.execute("SELECT * FROM venda_fretes LIMIT 3")
        fretes = cursor.fetchall()
        print(f'📋 Exemplos de fretes:')
        for frete in fretes:
            print(f'   {frete}')
    
    # Verificar estrutura da tabela venda_fretes
    cursor.execute("DESCRIBE venda_fretes")
    estrutura = cursor.fetchall()
    print(f'🏗️ Estrutura venda_fretes: {[col[0] for col in estrutura]}')
    
    # Verificar se há dados de shipping nas vendas (campo observacoes pode ter dados JSON)
    cursor.execute("SELECT venda_id, observacoes FROM vendas WHERE observacoes IS NOT NULL AND observacoes != '' LIMIT 3")
    observacoes = cursor.fetchall()
    print(f'📝 Exemplos de observações:')
    for venda_id, obs in observacoes:
        print(f'   {venda_id}: {obs[:100]}...')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
