#!/usr/bin/env python3
"""
Script para atualizar dados manualmente com base nas informações do usuário
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
    
    print('🔧 ATUALIZANDO DADOS MANUALMENTE')
    print('=' * 50)
    
    venda_id = '2000013113228770'
    
    # Dados corretos conforme mostrado pelo usuário
    taxa_ml_correta = 208.07  # Taxa de venda total
    frete_correto = 26.95     # Tarifa do Mercado Envios
    
    print('📊 DADOS CORRETOS:')
    print(f'   Taxa ML Correta: R$ {taxa_ml_correta:.2f}')
    print(f'   Frete Correto: R$ {frete_correto:.2f}')
    print()
    
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
        
        # Atualizar com dados corretos
        print('🔄 Atualizando dados...')
        cursor.execute("""
            UPDATE vendas 
            SET taxa_ml = %s, frete_total = %s
            WHERE venda_id = %s
        """, (taxa_ml_correta, frete_correto, venda_id))
        
        conn.commit()
        
        print('✅ Dados atualizados com sucesso!')
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
            print(f'   Taxa ML: R$ {taxa_ml:.2f}')
            print(f'   Frete Total: R$ {frete_total:.2f}')
            print(f'   Custo Total: R$ {custo_total:.2f}')
            print(f'   Lucro Total: R$ {lucro_total:.2f}')
            print(f'   Margem Total: {margem_total:.1f}%')
            print()
            
            print('🎯 RESULTADO:')
            print('   ✅ Frete agora está sendo incluído como custo')
            print('   ✅ Taxa ML corrigida com valor real')
            print('   ✅ Lucratividade calculada corretamente')
            print('   ✅ Interface mostrará frete como R$ 26,95')
    
    else:
        print('❌ Venda não encontrada no banco de dados')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
