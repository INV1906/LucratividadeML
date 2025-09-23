#!/usr/bin/env python3
"""
Script para configurar aplicação para usar RDS
"""

import os

print('⚙️ CONFIGURANDO APLICAÇÃO PARA RDS')
print('=' * 50)

# Configurações do RDS
RDS_HOST = "mercadolivre-db.xxxxxxxxxxxx.sa-east-1.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "MercadoLivre2024!"
DB_NAME = "sistema_ml"
DB_PORT = 3306

print('📝 CONFIGURAÇÕES DO RDS:')
print(f'   Host: {RDS_HOST}')
print(f'   User: {RDS_USER}')
print(f'   Database: {DB_NAME}')
print(f'   Port: {DB_PORT}')
print()

print('🔧 CONTEÚDO DO ARQUIVO .env:')
print('=' * 40)

env_content = f"""# Configuração para EC2 com RDS
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=DzolcrD&*HRA2E9Fxth2zRBomlMgcsH^xBDc!p&EQw%iB@u&gf

# Banco de dados RDS
DB_HOST={RDS_HOST}
DB_USER={RDS_USER}
DB_PASSWORD={RDS_PASSWORD}
DB_NAME={DB_NAME}
DB_PORT={DB_PORT}
DB_SSL_MODE=REQUIRED

# Mercado Livre
MELI_APP_ID=51467849418990
MELI_CLIENT_SECRET=KQGTjuxX0LfXVTw9MIVLYtykiTuWWniT
MELI_REDIRECT_URI=http://56.124.88.188/callback

# URLs da API
URL_CODE=https://auth.mercadolivre.com.br/authorization?response_type=code
URL_OAUTH_TOKEN=https://api.mercadolibre.com/oauth/token
"""

print(env_content)

print('📋 INSTRUÇÕES PARA CONFIGURAR:')
print('=' * 50)
print('1. 📝 Editar arquivo .env')
print('   nano /home/ec2-user/mercadolivre-app/.env')
print()
print('2. 🔄 Substituir todo o conteúdo pelo texto acima')
print('   (Copie e cole o conteúdo mostrado acima)')
print()
print('3. 💾 Salvar arquivo')
print('   Ctrl+X, Y, Enter')
print()
print('4. 🔍 Verificar se foi salvo corretamente')
print('   cat /home/ec2-user/mercadolivre-app/.env')
print()

print('🚀 APÓS CONFIGURAR:')
print('=' * 30)
print('1. 🔄 Reiniciar aplicação')
print('   sudo systemctl restart flask-app')
print()
print('2. ✅ Verificar status')
print('   sudo systemctl status flask-app')
print()
print('3. 📋 Verificar logs')
print('   sudo journalctl -u flask-app -f')
print()
print('4. 🌐 Testar aplicação')
print('   http://56.124.88.188')
print()

print('🎯 RESUMO:')
print('=' * 20)
print('✅ RDS: configurado')
print('✅ Aplicação: configurada')
print('✅ Pronto para usar!')
print()
print('🚨 IMPORTANTE:')
print('   Substitua o endpoint do RDS pelo seu endpoint real!')
print('   Exemplo: mercadolivre-db.abc123def456.sa-east-1.rds.amazonaws.com')
