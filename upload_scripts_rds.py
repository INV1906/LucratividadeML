#!/usr/bin/env python3
"""
Script para fazer upload dos scripts RDS para EC2
"""

import os
import subprocess
import sys

print('📤 FAZENDO UPLOAD DOS SCRIPTS RDS PARA EC2')
print('=' * 60)

# Configurações do EC2
EC2_HOST = "56.124.88.188"
EC2_USER = "ec2-user"
EC2_KEY = "C:\\Users\\inv19\\OneDrive - Biopark Educação\\Documentos\\Projetos\\MercadoLivre\\V0.01\\mercadolivre-key.pem"
EC2_PATH = "/home/ec2-user/mercadolivre-app/"

# Scripts para upload
scripts = [
    "test_rds_connection.py",
    "create_database.py",
    "configurar_app_rds.py"
]

print(f'🎯 CONFIGURAÇÕES:')
print(f'   Host: {EC2_HOST}')
print(f'   User: {EC2_USER}')
print(f'   Key: {EC2_KEY}')
print(f'   Path: {EC2_PATH}')
print()

print('📋 SCRIPTS PARA UPLOAD:')
for script in scripts:
    if os.path.exists(script):
        print(f'   ✅ {script}')
    else:
        print(f'   ❌ {script} (não encontrado)')
print()

print('🚀 INICIANDO UPLOAD...')
print('=' * 40)

# Verificar se scp está disponível
try:
    result = subprocess.run(['scp', '--version'], capture_output=True, text=True)
    print('✅ SCP disponível')
except FileNotFoundError:
    print('❌ SCP não encontrado')
    print('💡 Use WinSCP ou outro cliente SFTP')
    print()
    print('📋 ARQUIVOS PARA UPLOAD MANUAL:')
    for script in scripts:
        if os.path.exists(script):
            print(f'   📄 {script}')
    print()
    print('🎯 DESTINO NO EC2:')
    print(f'   {EC2_PATH}')
    sys.exit(1)

# Fazer upload de cada script
for script in scripts:
    if os.path.exists(script):
        print(f'📤 Enviando {script}...')
        try:
            cmd = [
                'scp',
                '-i', EC2_KEY,
                '-o', 'StrictHostKeyChecking=no',
                script,
                f'{EC2_USER}@{EC2_HOST}:{EC2_PATH}'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f'✅ {script} enviado com sucesso!')
            else:
                print(f'❌ Erro ao enviar {script}:')
                print(f'   {result.stderr}')
                
        except Exception as e:
            print(f'❌ Erro ao enviar {script}: {e}')
    else:
        print(f'⚠️ {script} não encontrado, pulando...')

print()
print('🎉 UPLOAD CONCLUÍDO!')
print('=' * 30)
print('✅ Scripts enviados para EC2')
print()
print('🚀 PRÓXIMOS PASSOS NO EC2:')
print('=' * 40)
print('1. 🧪 Testar conexão com RDS')
print('   python3.11 test_rds_connection.py')
print()
print('2. 🗄️ Criar banco de dados')
print('   python3.11 create_database.py')
print()
print('3. ⚙️ Configurar aplicação')
print('   python3.11 configurar_app_rds.py')
print()
print('4. 🔄 Reiniciar aplicação')
print('   sudo systemctl restart flask-app')
print()
print('5. 🌐 Testar aplicação')
print('   http://56.124.88.188')
