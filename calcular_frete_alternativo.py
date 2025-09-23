#!/usr/bin/env python3
"""
Script para calcular frete baseado na diferença entre taxa ML esperada e retornada
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
    
    print('🧮 CALCULANDO FRETE ALTERNATIVO')
    print('=' * 50)
    
    venda_id = '2000013113228770'
    
    # Dados da venda conforme mostrado pelo usuário
    valor_produto = 1486.23
    taxa_ml_esperada = 208.07  # Conforme mostrado pelo usuário
    frete_esperado = 26.95     # Conforme mostrado pelo usuário
    desconto_bonus = 14.37     # Conforme mostrado pelo usuário
    
    # Buscar dados da venda no banco
    cursor.execute("""
        SELECT valor_total, taxa_ml, frete_total
        FROM vendas 
        WHERE venda_id = %s
    """, (venda_id,))
    
    venda_db = cursor.fetchone()
    
    if venda_db:
        valor_total_db, taxa_ml_db, frete_total_db = venda_db
        
        print('📊 DADOS DA VENDA:')
        print(f'   Valor Produto (usuário): R$ {valor_produto:.2f}')
        print(f'   Valor Total (banco): R$ {valor_total_db:.2f}')
        print(f'   Taxa ML Esperada (usuário): R$ {taxa_ml_esperada:.2f}')
        print(f'   Taxa ML (banco): R$ {taxa_ml_db:.2f}')
        print(f'   Frete Esperado (usuário): R$ {frete_esperado:.2f}')
        print(f'   Frete Total (banco): R$ {frete_total_db:.2f}')
        print()
        
        # Calcular diferenças
        diferenca_taxa = taxa_ml_esperada - float(taxa_ml_db)
        print(f'🔍 ANÁLISE:')
        print(f'   Diferença na Taxa ML: R$ {diferenca_taxa:.2f}')
        print(f'   Frete Esperado: R$ {frete_esperado:.2f}')
        print(f'   Desconto/Bônus: R$ {desconto_bonus:.2f}')
        print()
        
        # Verificar se o frete pode estar incluído na taxa ML
        if abs(diferenca_taxa - frete_esperado) < 1.0:  # Tolerância de R$ 1,00
            print('✅ POSSÍVEL SOLUÇÃO:')
            print('   O custo de frete pode estar incluído na taxa ML')
            print('   Taxa ML real = Taxa ML da API + Custo de Frete')
            print()
            
            # Propor correção
            taxa_ml_corrigida = taxa_ml_db + frete_esperado
            print(f'💡 CORREÇÃO PROPOSTA:')
            print(f'   Taxa ML Corrigida: R$ {taxa_ml_corrigida:.2f}')
            print(f'   Frete Separado: R$ {frete_esperado:.2f}')
            print()
            
            # Atualizar banco de dados
            print('🔄 Atualizando banco de dados...')
            cursor.execute("""
                UPDATE vendas 
                SET taxa_ml = %s, frete_total = %s
                WHERE venda_id = %s
            """, (taxa_ml_corrigida, frete_esperado, venda_id))
            
            conn.commit()
            
            print('✅ Banco de dados atualizado!')
            print(f'   Taxa ML: R$ {taxa_ml_corrigida:.2f}')
            print(f'   Frete Total: R$ {frete_esperado:.2f}')
            
        else:
            print('❌ A diferença não corresponde ao custo de frete esperado')
            print('   Pode haver outros fatores envolvidos')
    
    else:
        print('❌ Venda não encontrada no banco de dados')
    
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
