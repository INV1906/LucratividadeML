#!/usr/bin/env python3
"""
Script para criar banco de dados no RDS
"""

import mysql.connector
import os

print('🗄️ CRIANDO BANCO DE DADOS NO RDS')
print('=' * 40)

# Configurações do RDS (substitua pelo seu endpoint real)
RDS_HOST = "mercadolivre-db.xxxxxxxxxxxx.sa-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "MercadoLivre2024!"
RDS_PORT = 3306
DB_NAME = "sistema_ml"

print(f'🔗 Conectando ao RDS...')
print(f'   Host: {RDS_HOST}')
print(f'   User: {RDS_USER}')
print(f'   Database: {DB_NAME}')
print()

try:
    # Conectar ao RDS
    conn = mysql.connector.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        port=RDS_PORT,
        ssl_disabled=False,
        connect_timeout=10
    )
    
    print('✅ Conectado ao RDS com sucesso!')
    
    cursor = conn.cursor()
    
    # Criar banco de dados
    print(f'🏗️ Criando banco de dados: {DB_NAME}')
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f'✅ Banco {DB_NAME} criado com sucesso!')
    
    # Selecionar o banco
    cursor.execute(f"USE {DB_NAME}")
    print(f'✅ Banco {DB_NAME} selecionado!')
    
    # Verificar se foi criado
    cursor.execute("SELECT DATABASE()")
    current_db = cursor.fetchone()
    print(f'📊 Banco atual: {current_db[0]}')
    
    # Listar tabelas (deve estar vazio inicialmente)
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f'📋 Tabelas existentes: {len(tables)}')
    
    conn.close()
    print('✅ Conexão fechada com sucesso!')
    
    print()
    print('🎉 BANCO DE DADOS CRIADO COM SUCESSO!')
    print('=' * 50)
    print('✅ RDS: conectado')
    print(f'✅ Banco: {DB_NAME}')
    print('✅ Pronto para usar')
    print()
    print('🚀 PRÓXIMO PASSO:')
    print('   Configurar aplicação para usar RDS')
    print('   nano /home/ec2-user/mercadolivre-app/.env')
    
except mysql.connector.Error as e:
    print(f'❌ ERRO DE BANCO DE DADOS: {e}')
    print()
    print('🔍 POSSÍVEIS CAUSAS:')
    print('   1. RDS não está criado')
    print('   2. Endpoint incorreto')
    print('   3. Permissões insuficientes')
    print('   4. Security Group bloqueando')
    
except Exception as e:
    print(f'❌ ERRO GERAL: {e}')
    print()
    print('🔍 VERIFICAR:')
    print('   1. Conexão com RDS')
    print('   2. Credenciais corretas')
    print('   3. Permissões do usuário')
