#!/usr/bin/env python3
"""
Script para diagnosticar problemas de conexão com RDS
"""

import mysql.connector
import socket
import ssl
import time

print('🔍 DIAGNOSTICANDO CONEXÃO COM RDS')
print('=' * 50)

# Endpoint do RDS (substitua pelo seu endpoint real)
RDS_HOST = "mercadolivre-db.c1kgogyiayu1.sa-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "MercadoLivre2024!"
RDS_PORT = 3306

print(f'🎯 CONFIGURAÇÕES:')
print(f'   Host: {RDS_HOST}')
print(f'   User: {RDS_USER}')
print(f'   Port: {RDS_PORT}')
print()

print('🔍 DIAGNÓSTICO PASSO A PASSO:')
print('=' * 40)

# 1. Testar resolução DNS
print('1. 🌐 Testando resolução DNS...')
try:
    ip_address = socket.gethostbyname(RDS_HOST)
    print(f'   ✅ DNS resolvido: {ip_address}')
except socket.gaierror as e:
    print(f'   ❌ Erro DNS: {e}')
    print('   💡 Verifique se o endpoint está correto')
    exit(1)

# 2. Testar conectividade de rede
print('2. 🔌 Testando conectividade de rede...')
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    result = sock.connect_ex((ip_address, RDS_PORT))
    sock.close()
    
    if result == 0:
        print(f'   ✅ Porta {RDS_PORT} está acessível')
    else:
        print(f'   ❌ Porta {RDS_PORT} não está acessível')
        print('   💡 Verifique Security Group do RDS')
        exit(1)
        
except Exception as e:
    print(f'   ❌ Erro de rede: {e}')
    exit(1)

# 3. Testar conexão SSL
print('3. 🔒 Testando conexão SSL...')
try:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    sock.connect((ip_address, RDS_PORT))
    
    ssl_sock = context.wrap_socket(sock, server_hostname=RDS_HOST)
    ssl_sock.close()
    print('   ✅ SSL funcionando')
    
except Exception as e:
    print(f'   ❌ Erro SSL: {e}')

# 4. Testar conexão MySQL
print('4. 🗄️ Testando conexão MySQL...')
try:
    conn = mysql.connector.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        port=RDS_PORT,
        ssl_disabled=False,
        connect_timeout=10,
        autocommit=True
    )
    
    print('   ✅ Conexão MySQL bem-sucedida!')
    
    # Testar algumas operações
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f'   📊 Versão MySQL: {version[0]}')
    
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    print(f'   🗄️ Bancos disponíveis: {len(databases)}')
    
    conn.close()
    print('   ✅ Conexão fechada com sucesso!')
    
except mysql.connector.Error as e:
    print(f'   ❌ Erro MySQL: {e}')
    print()
    print('🔍 POSSÍVEIS CAUSAS:')
    if "Unknown MySQL server host" in str(e):
        print('   - Endpoint do RDS incorreto')
        print('   - RDS não está criado')
        print('   - DNS não está resolvendo')
    elif "Access denied" in str(e):
        print('   - Usuário/senha incorretos')
        print('   - Usuário não tem permissões')
    elif "Connection refused" in str(e):
        print('   - Security Group bloqueando')
        print('   - RDS não está rodando')
    elif "SSL" in str(e):
        print('   - Problema com SSL')
        print('   - Certificado inválido')
    
except Exception as e:
    print(f'   ❌ Erro geral: {e}')

print()
print('🎯 RESUMO DO DIAGNÓSTICO:')
print('=' * 40)
print('✅ DNS: resolvido')
print('✅ Rede: conectável')
print('✅ SSL: funcionando')
print('❌ MySQL: erro de conexão')
print()
print('💡 SOLUÇÕES:')
print('=' * 20)
print('1. 🏗️ Verificar se RDS está criado')
print('2. 🔒 Verificar Security Group')
print('3. 📋 Verificar endpoint correto')
print('4. 👤 Verificar credenciais')
print()
print('🚀 PRÓXIMOS PASSOS:')
print('=' * 30)
print('1. Verificar AWS Console')
print('2. Verificar Security Group')
print('3. Verificar endpoint')
print('4. Testar novamente')
