#!/usr/bin/env python3
"""
Script para testar conexão com RDS MySQL
"""

import mysql.connector
import os

print('🧪 TESTANDO CONEXÃO COM RDS')
print('=' * 40)

# Configurações do RDS (substitua pelo seu endpoint real)
RDS_HOST = "mercadolivre-db.xxxxxxxxxxxx.sa-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "MercadoLivre2024!"
RDS_PORT = 3306

print(f'🔗 Tentando conectar ao RDS...')
print(f'   Host: {RDS_HOST}')
print(f'   User: {RDS_USER}')
print(f'   Port: {RDS_PORT}')
print()

try:
    # Tentar conexão
    conn = mysql.connector.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        port=RDS_PORT,
        ssl_disabled=False,
        connect_timeout=10
    )
    
    print('✅ CONEXÃO COM RDS BEM-SUCEDIDA!')
    print('🎉 RDS está funcionando perfeitamente!')
    
    # Testar algumas operações básicas
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f'📊 Versão do MySQL: {version[0]}')
    
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print(f'🗄️ Bancos disponíveis: {len(databases)}')
    
    conn.close()
    print('✅ Conexão fechada com sucesso!')
    
except mysql.connector.Error as e:
    print(f'❌ ERRO DE CONEXÃO: {e}')
    print()
    print('🔍 POSSÍVEIS CAUSAS:')
    print('   1. RDS ainda não foi criado')
    print('   2. Endpoint incorreto')
    print('   3. Security Group bloqueando acesso')
    print('   4. Credenciais incorretas')
    print()
    print('💡 SOLUÇÕES:')
    print('   1. Criar RDS MySQL no AWS Console')
    print('   2. Verificar endpoint correto')
    print('   3. Configurar Security Group')
    print('   4. Verificar usuário/senha')
    
except Exception as e:
    print(f'❌ ERRO GERAL: {e}')
    print()
    print('🔍 VERIFICAR:')
    print('   1. mysql-connector-python instalado')
    print('   2. Python funcionando')
    print('   3. Conectividade de rede')

print()
print('🚀 PRÓXIMO PASSO:')
print('   Se a conexão funcionou, execute:')
print('   python3.11 create_database.py')
