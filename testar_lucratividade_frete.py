#!/usr/bin/env python3
"""
Script para testar se o frete está sendo incluído no cálculo de lucratividade
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
    
    print('🧪 TESTANDO LUCRATIVIDADE COM FRETE')
    print('=' * 50)
    
    # Buscar um pack com frete para testar
    cursor.execute("""
        SELECT 
            COALESCE(pack_id, venda_id) as pack_id,
            SUM(valor_total) as valor_total,
            SUM(taxa_ml) as taxa_ml,
            SUM(frete_total) as frete_total,
            COUNT(*) as total_vendas
        FROM vendas 
        WHERE frete_total > 0
        GROUP BY COALESCE(pack_id, venda_id)
        ORDER BY frete_total DESC
        LIMIT 1
    """)
    
    pack_data = cursor.fetchone()
    
    if not pack_data:
        print('❌ Nenhum pack com frete encontrado')
        conn.close()
        exit()
    
    pack_id, valor_total, taxa_ml, frete_total, total_vendas = pack_data
    
    print(f'📦 Pack ID: {pack_id}')
    print(f'💰 Valor Total: R$ {valor_total:.2f}')
    print(f'📊 Taxa ML: R$ {taxa_ml:.2f}')
    print(f'🚚 Frete Total: R$ {frete_total:.2f}')
    print(f'📈 Total Vendas: {total_vendas}')
    print()
    
    # Simular o cálculo de lucratividade
    from database import DatabaseManager
    db = DatabaseManager()
    
    user_id = 1305538297  # User ID com dados
    
    print('🔍 CALCULANDO LUCRATIVIDADE...')
    lucratividade = db.calcular_lucratividade_pack(pack_id, user_id)
    
    if lucratividade:
        print('✅ Lucratividade calculada com sucesso!')
        print()
        print('📊 RESULTADOS:')
        print(f'   Receita Total: R$ {lucratividade["receita_total"]:.2f}')
        print(f'   Custo Produtos: R$ {lucratividade["custo_produtos"]:.2f}')
        print(f'   Taxa ML: R$ {lucratividade["taxa_ml"]:.2f}')
        print(f'   Frete Total: R$ {lucratividade["frete_total"]:.2f}')
        print(f'   Custo Total: R$ {lucratividade["custo_total"]:.2f}')
        print(f'   Lucro Total: R$ {lucratividade["lucro_total"]:.2f}')
        print(f'   Margem Total: {lucratividade["margem_total"]:.1f}%')
        print()
        
        # Verificar se o frete está incluído no custo total
        custo_esperado = lucratividade["custo_produtos"] + lucratividade["taxa_ml"] + lucratividade["frete_total"]
        diferenca = abs(lucratividade["custo_total"] - custo_esperado)
        
        if diferenca < 0.01:  # Tolerância para arredondamentos
            print('✅ FRETE ESTÁ SENDO INCLUÍDO CORRETAMENTE!')
            print(f'   Custo Total = Custo Produtos + Taxa ML + Frete Total')
            print(f'   R$ {lucratividade["custo_total"]:.2f} = R$ {lucratividade["custo_produtos"]:.2f} + R$ {lucratividade["taxa_ml"]:.2f} + R$ {lucratividade["frete_total"]:.2f}')
        else:
            print('❌ PROBLEMA: Frete não está sendo incluído corretamente!')
            print(f'   Diferença: R$ {diferenca:.2f}')
        
        print()
        print('📋 ITENS DO PACK:')
        for i, item in enumerate(lucratividade["itens"][:3]):  # Mostrar apenas os primeiros 3
            print(f'   {i+1}. {item["item_titulo"][:50]}...')
            print(f'      Preço: R$ {item["preco_total"]:.2f}')
            print(f'      Custo: R$ {item["custo_total"]:.2f}')
            print(f'      Frete Proporcional: R$ {item["frete_proporcional"]:.2f}')
            print(f'      Custo com Frete: R$ {item["custo_total_com_frete"]:.2f}')
            print(f'      Lucro Final: R$ {item["lucro_final"]:.2f}')
            print(f'      Margem Final: {item["margem_final"]:.1f}%')
            print()
    else:
        print('❌ Erro ao calcular lucratividade')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
