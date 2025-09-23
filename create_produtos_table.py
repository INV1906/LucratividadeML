#!/usr/bin/env python3
"""
Script para criar tabela de produtos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager

def criar_tabela_produtos():
    """Cria tabela de produtos"""
    print("🔄 Criando tabela de produtos...")
    
    db = DatabaseManager()
    conn = db.conectar()
    
    if not conn:
        print("❌ Erro de conexão com banco de dados")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Criar tabela de produtos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    produto_id VARCHAR(50) NOT NULL,
                    titulo VARCHAR(500) NOT NULL,
                    categoria_id VARCHAR(50),
                    preco DECIMAL(10,2) DEFAULT 0,
                    moeda VARCHAR(10) DEFAULT 'BRL',
                    quantidade_disponivel INT DEFAULT 0,
                    quantidade_vendida INT DEFAULT 0,
                    condicao VARCHAR(50) DEFAULT 'new',
                    status VARCHAR(50) DEFAULT 'active',
                    permalink TEXT,
                    thumbnail TEXT,
                    data_criacao TIMESTAMP NULL,
                    data_modificacao TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_user_produto (user_id, produto_id),
                    INDEX idx_user_status (user_id, status),
                    INDEX idx_categoria (categoria_id),
                    INDEX idx_data_modificacao (data_modificacao)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            conn.commit()
            print("✅ Tabela de produtos criada com sucesso")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela de produtos: {e}")
        return False
    finally:
        if conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("🚀 CRIANDO TABELA DE PRODUTOS")
    print("=" * 40)
    
    if criar_tabela_produtos():
        print("\n✅ TABELA DE PRODUTOS CRIADA COM SUCESSO!")
        print("   • Estrutura completa para produtos")
        print("   • Índices otimizados para consultas")
        print("   • Suporte a múltiplos usuários")
        print("   • Campos de auditoria (created_at, updated_at)")
    else:
        print("\n❌ ERRO AO CRIAR TABELA DE PRODUTOS!")
        sys.exit(1)
