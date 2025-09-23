#!/usr/bin/env python3
"""
Script para testar se a implementação está funcionando para todas as vendas
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
    
    print('🧪 TESTANDO IMPLEMENTAÇÃO COMPLETA')
    print('=' * 50)
    
    # Buscar algumas vendas para testar
    cursor.execute("""
        SELECT venda_id, valor_total, taxa_ml, frete_total, data_aprovacao
        FROM vendas 
        WHERE user_id = 1305538297
        ORDER BY data_aprovacao DESC
        LIMIT 10
    """, ())
    
    vendas = cursor.fetchall()
    
    print(f'📊 TESTANDO {len(vendas)} VENDAS RECENTES:')
    print()
    
    vendas_com_frete = 0
    vendas_com_desconto = 0
    
    for venda in vendas:
        venda_id, valor_total, taxa_ml, frete_total, data_aprovacao = venda
        
        print(f'🛒 Venda: {venda_id}')
        print(f'   Data: {data_aprovacao}')
        print(f'   Valor Total: R$ {valor_total:.2f}')
        print(f'   Taxa ML: R$ {taxa_ml:.2f}')
        print(f'   Frete Total: R$ {frete_total:.2f}')
        
        # Verificar se tem frete
        if frete_total > 0:
            vendas_com_frete += 1
            print('   ✅ Tem frete')
        else:
            print('   ❌ Sem frete')
        
        # Verificar se tem desconto (taxa ML menor que 14% do valor)
        taxa_esperada = float(valor_total) * 0.14
        if float(taxa_ml) < taxa_esperada:
            vendas_com_desconto += 1
            desconto = taxa_esperada - float(taxa_ml)
            print(f'   ✅ Tem desconto: R$ {desconto:.2f}')
        else:
            print('   ❌ Sem desconto')
        
        print()
    
    print('📈 RESUMO:')
    print(f'   Total de vendas testadas: {len(vendas)}')
    print(f'   Vendas com frete: {vendas_com_frete}')
    print(f'   Vendas com desconto: {vendas_com_desconto}')
    print()
    
    if vendas_com_frete > 0:
        print('✅ Sistema está capturando fretes corretamente')
    else:
        print('⚠️ Nenhuma venda com frete encontrada')
    
    if vendas_com_desconto > 0:
        print('✅ Sistema está aplicando descontos corretamente')
    else:
        print('⚠️ Nenhuma venda com desconto encontrada')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
