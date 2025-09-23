#!/usr/bin/env python3
"""
Script para adaptar o código para Supabase (PostgreSQL)
"""

print('🔧 ADAPTANDO CÓDIGO PARA SUPABASE (POSTGRESQL)')
print('=' * 60)

print('📋 MUDANÇAS NECESSÁRIAS:')
print()

print('1. 📦 INSTALAR DEPENDÊNCIA:')
print('   pip install psycopg2-binary')
print()

print('2. 🔄 MODIFICAR database.py:')
print('   - Trocar mysql.connector por psycopg2')
print('   - Adaptar queries SQL')
print('   - Configurar SSL')
print()

print('3. ⚙️ CONFIGURAR VARIÁVEIS:')
print('   DB_HOST=db.xxxxxxxxxxxx.supabase.co')
print('   DB_USER=postgres')
print('   DB_PASSWORD=sua_senha')
print('   DB_NAME=postgres')
print('   DB_PORT=5432')
print('   DB_SSL_MODE=REQUIRED')
print()

print('4. 🔧 QUERIES SQL:')
print('   - LIMIT -> LIMIT (igual)')
print('   - AUTO_INCREMENT -> SERIAL')
print('   - DATETIME -> TIMESTAMP')
print('   - VARCHAR -> TEXT')
print()

print('✅ VANTAGENS DO SUPABASE:')
print('   - 500MB gratuito')
print('   - PostgreSQL (mais robusto)')
print('   - Interface web excelente')
print('   - API REST incluída')
print('   - SSL automático')
print('   - Backup automático')
print()

print('⚠️ DESVANTAGENS:')
print('   - Precisa adaptar código')
print('   - PostgreSQL (não MySQL)')
print('   - Algumas queries diferentes')
print()

print('🎯 RECOMENDAÇÃO:')
print('   Supabase é a melhor opção gratuita!')
print('   Vale a pena adaptar o código.')
print()

print('🚀 PRÓXIMOS PASSOS:')
print('   1. Criar conta no Supabase')
print('   2. Criar projeto')
print('   3. Obter string de conexão')
print('   4. Adaptar database.py')
print('   5. Configurar no Vercel')
print('   6. Deploy da aplicação')
print()

print('⏱️ TEMPO ESTIMADO: 20 minutos')
print('🎉 RESULTADO: Aplicação online com banco gratuito!')
