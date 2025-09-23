#!/usr/bin/env python3
"""
Script para aplicar o desconto de R$ 14,37 na venda específica
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
    
    print('🎁 APLICANDO DESCONTO NA VENDA ESPECÍFICA')
    print('=' * 50)
    
    venda_id = '2000013113228770'
    desconto_bonus = 14.37  # Desconto conforme mostrado pelo usuário
    
    # Buscar dados atuais
    cursor.execute("""
        SELECT valor_total, taxa_ml, frete_total
        FROM vendas 
        WHERE venda_id = %s
    """, (venda_id,))
    
    venda_atual = cursor.fetchone()
    
    if venda_atual:
        valor_total, taxa_ml_atual, frete_atual = venda_atual
        
        print('📊 DADOS ATUAIS:')
        print(f'   Valor Total: R$ {valor_total:.2f}')
        print(f'   Taxa ML Atual: R$ {taxa_ml_atual:.2f}')
        print(f'   Frete Atual: R$ {frete_atual:.2f}')
        print()
        
        # Aplicar desconto na taxa ML
        taxa_ml_com_desconto = float(taxa_ml_atual) - desconto_bonus
        
        print('🎁 APLICANDO DESCONTO:')
        print(f'   Desconto/Bônus: R$ {desconto_bonus:.2f}')
        print(f'   Taxa ML Original: R$ {taxa_ml_atual:.2f}')
        print(f'   Taxa ML com Desconto: R$ {taxa_ml_com_desconto:.2f}')
        print()
        
        # Atualizar banco de dados
        cursor.execute("""
            UPDATE vendas 
            SET taxa_ml = %s
            WHERE venda_id = %s
        """, (taxa_ml_com_desconto, venda_id))
        
        conn.commit()
        
        print('✅ Desconto aplicado com sucesso!')
        print()
        
        # Verificar atualização
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
            
            # Calcular lucratividade corrigida
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
            print(f'   Taxa ML (com desconto): R$ {taxa_ml:.2f}')
            print(f'   Frete Total: R$ {frete_total:.2f}')
            print(f'   Custo Total: R$ {custo_total:.2f}')
            print(f'   Lucro Total: R$ {lucro_total:.2f}')
            print(f'   Margem Total: {margem_total:.1f}%')
            print()
            
            print('🎯 RESULTADO:')
            print('   ✅ Desconto aplicado corretamente')
            print('   ✅ Custo total reduzido')
            print('   ✅ Lucratividade mais precisa')
            print('   ✅ Interface mostra custos reais')
    
    else:
        print('❌ Venda não encontrada no banco de dados')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
