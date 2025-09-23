#!/usr/bin/env python3
"""
Script para criar ZIP com scripts RDS para upload manual
"""

import zipfile
import os
from datetime import datetime

print('📦 CRIANDO ZIP COM SCRIPTS RDS')
print('=' * 40)

# Nome do arquivo ZIP
zip_filename = f"scripts_rds_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

# Scripts para incluir
scripts = [
    "test_rds_connection.py",
    "create_database.py", 
    "configurar_app_rds.py"
]

print(f'📋 SCRIPTS PARA INCLUIR:')
for script in scripts:
    if os.path.exists(script):
        print(f'   ✅ {script}')
    else:
        print(f'   ❌ {script} (não encontrado)')
print()

print(f'📦 Criando arquivo: {zip_filename}')
print('=' * 40)

try:
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for script in scripts:
            if os.path.exists(script):
                zipf.write(script)
                print(f'✅ Adicionado: {script}')
            else:
                print(f'⚠️ Pulando: {script} (não encontrado)')
    
    # Verificar tamanho do arquivo
    file_size = os.path.getsize(zip_filename)
    print(f'📊 Tamanho do arquivo: {file_size:,} bytes')
    
    print()
    print('🎉 ZIP CRIADO COM SUCESSO!')
    print('=' * 30)
    print(f'📁 Arquivo: {zip_filename}')
    print()
    print('📋 CONTEÚDO DO ZIP:')
    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        for file_info in zipf.filelist:
            print(f'   📄 {file_info.filename}')
    
    print()
    print('🚀 INSTRUÇÕES PARA UPLOAD:')
    print('=' * 40)
    print('1. 📤 Usar WinSCP ou outro cliente SFTP')
    print('2. 🎯 Conectar ao EC2:')
    print('   Host: 56.124.88.188')
    print('   User: ec2-user')
    print('   Key: mercadolivre-key.pem')
    print('3. 📁 Navegar para: /home/ec2-user/mercadolivre-app/')
    print('4. ⬆️ Fazer upload do arquivo ZIP')
    print('5. 📦 Extrair no EC2:')
    print('   unzip scripts_rds_*.zip')
    print()
    print('🎯 APÓS EXTRAIR:')
    print('=' * 20)
    print('1. 🧪 Testar conexão:')
    print('   python3.11 test_rds_connection.py')
    print()
    print('2. 🗄️ Criar banco:')
    print('   python3.11 create_database.py')
    print()
    print('3. ⚙️ Configurar app:')
    print('   python3.11 configurar_app_rds.py')
    
except Exception as e:
    print(f'❌ ERRO AO CRIAR ZIP: {e}')
    print()
    print('💡 SOLUÇÃO ALTERNATIVA:')
    print('   Copie os arquivos individualmente:')
    for script in scripts:
        if os.path.exists(script):
            print(f'   📄 {script}')
