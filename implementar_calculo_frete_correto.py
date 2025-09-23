#!/usr/bin/env python3
"""
Script para implementar cálculo de frete correto baseado nos dados reais
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
    
    print('🔧 IMPLEMENTANDO CÁLCULO DE FRETE CORRETO')
    print('=' * 60)
    
    venda_id = '2000013113228770'
    
    # Dados conforme mostrado pelo usuário
    valor_produto = 1486.23
    valor_total_pago = 1617.29  # Valor que o comprador pagou
    taxa_ml_real = 208.07       # Taxa ML real (incluindo frete)
    frete_real = 26.95          # Frete real
    
    # Buscar dados da venda no banco
    cursor.execute("""
        SELECT valor_total, taxa_ml, frete_total
        FROM vendas 
        WHERE venda_id = %s
    """, (venda_id,))
    
    venda_db = cursor.fetchone()
    
    if venda_db:
        valor_total_db, taxa_ml_db, frete_total_db = venda_db
        
        print('📊 ANÁLISE DOS DADOS:')
        print(f'   Valor Produto: R$ {valor_produto:.2f}')
        print(f'   Valor Total Pago: R$ {valor_total_pago:.2f}')
        print(f'   Taxa ML Real: R$ {taxa_ml_real:.2f}')
        print(f'   Frete Real: R$ {frete_real:.2f}')
        print()
        print(f'   Valor Total (banco): R$ {valor_total_db:.2f}')
        print(f'   Taxa ML (banco): R$ {taxa_ml_db:.2f}')
        print(f'   Frete Total (banco): R$ {frete_total_db:.2f}')
        print()
        
        # Calcular diferença entre valor pago e valor do produto
        diferenca_valor = valor_total_pago - valor_produto
        print(f'🔍 CÁLCULOS:')
        print(f'   Diferença Valor Pago - Produto: R$ {diferenca_valor:.2f}')
        print(f'   Taxa ML Real - Taxa ML Banco: R$ {taxa_ml_real - float(taxa_ml_db):.2f}')
        print()
        
        # Verificar se a diferença corresponde ao frete
        if abs(diferenca_valor - frete_real) < 1.0:
            print('✅ SOLUÇÃO ENCONTRADA:')
            print('   A diferença entre valor pago e produto corresponde ao frete')
            print('   Vou atualizar o banco com os valores corretos')
            print()
            
            # Atualizar banco de dados com valores corretos
            cursor.execute("""
                UPDATE vendas 
                SET taxa_ml = %s, frete_total = %s
                WHERE venda_id = %s
            """, (taxa_ml_real, frete_real, venda_id))
            
            conn.commit()
            
            print('✅ Banco de dados atualizado!')
            print(f'   Taxa ML: R$ {taxa_ml_real:.2f}')
            print(f'   Frete Total: R$ {frete_real:.2f}')
            print()
            
            # Verificar se a atualização funcionou
            cursor.execute("""
                SELECT valor_total, taxa_ml, frete_total
                FROM vendas 
                WHERE venda_id = %s
            """, (venda_id,))
            
            venda_atualizada = cursor.fetchone()
            if venda_atualizada:
                print('📊 DADOS ATUALIZADOS:')
                print(f'   Valor Total: R$ {venda_atualizada[0]:.2f}')
                print(f'   Taxa ML: R$ {venda_atualizada[1]:.2f}')
                print(f'   Frete Total: R$ {venda_atualizada[2]:.2f}')
                print()
                
                # Calcular lucratividade com frete correto
                receita_total = float(venda_atualizada[0])
                custo_produtos = 0  # Assumindo custo zero para teste
                taxa_ml = float(venda_atualizada[1])
                frete_total = float(venda_atualizada[2])
                
                custo_total = custo_produtos + taxa_ml + frete_total
                lucro_total = receita_total - custo_total
                margem_total = (lucro_total / receita_total * 100) if receita_total > 0 else 0
                
                print('💰 LUCRATIVIDADE CORRIGIDA:')
                print(f'   Receita Total: R$ {receita_total:.2f}')
                print(f'   Custo Produtos: R$ {custo_produtos:.2f}')
                print(f'   Taxa ML: R$ {taxa_ml:.2f}')
                print(f'   Frete Total: R$ {frete_total:.2f}')
                print(f'   Custo Total: R$ {custo_total:.2f}')
                print(f'   Lucro Total: R$ {lucro_total:.2f}')
                print(f'   Margem Total: {margem_total:.1f}%')
                
        else:
            print('❌ A diferença não corresponde ao frete esperado')
            print('   Pode haver outros custos envolvidos')
    
    else:
        print('❌ Venda não encontrada no banco de dados')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
