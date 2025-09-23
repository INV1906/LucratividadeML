#!/usr/bin/env python3
"""
Script para preparar arquivos para upload manual para EC2
"""

import os
import shutil
import zipfile

def prepare_files_for_upload():
    print('🚀 PREPARANDO ARQUIVOS PARA UPLOAD MANUAL')
    print('=' * 60)
    
    # Criar diretório temporário
    temp_dir = 'ec2_upload'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Arquivos essenciais
    essential_files = [
        'app.py',
        'database.py', 
        'meli_api.py',
        'webhook_processor.py',
        'token_monitor.py',
        'sync_manager.py',
        'shipping_status.py',
        'translations.py',
        'requirements.txt',
        '.env_ec2'
    ]
    
    # Diretórios essenciais
    essential_dirs = [
        'templates'
    ]
    
    print('📦 COPIANDO ARQUIVOS...')
    
    # Copiar arquivos
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir)
            print(f'   ✅ {file}')
        else:
            print(f'   ❌ {file} (não encontrado)')
    
    # Copiar diretórios
    for dir_name in essential_dirs:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, os.path.join(temp_dir, dir_name))
            print(f'   ✅ {dir_name}/')
        else:
            print(f'   ❌ {dir_name}/ (não encontrado)')
    
    # Criar arquivo ZIP
    zip_file = 'mercadolivre_app_ec2.zip'
    print(f'📦 Criando arquivo ZIP: {zip_file}')
    
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    print(f'✅ Arquivo ZIP criado: {zip_file}')
    
    # Limpar diretório temporário
    shutil.rmtree(temp_dir)
    
    print()
    print('📋 INSTRUÇÕES PARA UPLOAD:')
    print()
    print('1. 📤 UPLOAD DO ARQUIVO ZIP:')
    print('   # Opção 1: Usar WinSCP (recomendado para Windows)')
    print('   # - Baixar WinSCP: https://winscp.net/')
    print('   # - Conectar com:')
    print('   #   Host: 56.124.88.188')
    print('   #   Username: ec2-user')
    print('   #   Key file: sua-chave.pem')
    print('   # - Fazer upload do arquivo mercadolivre_app_ec2.zip')
    print()
    print('   # Opção 2: Usar scp (se disponível)')
    print('   scp -i sua-chave.pem mercadolivre_app_ec2.zip ec2-user@56.124.88.188:/home/ec2-user/')
    print()
    print('2. 🔧 CONECTAR VIA SSH:')
    print('   ssh -i sua-chave.pem ec2-user@56.124.88.188')
    print()
    print('3. 📁 EXTRAIR ARQUIVOS:')
    print('   cd /home/ec2-user')
    print('   unzip mercadolivre_app_ec2.zip')
    print('   mv mercadolivre_app_ec2 mercadolivre-app')
    print('   cd mercadolivre-app')
    print('   mv .env_ec2 .env')
    print()
    print('4. 🐍 INSTALAR PYTHON E DEPENDÊNCIAS:')
    print('   sudo yum update -y')
    print('   sudo yum install python3.11 python3.11-pip -y')
    print('   pip3.11 install -r requirements.txt')
    print()
    print('5. 🗄️ INSTALAR MYSQL:')
    print('   sudo yum install mysql-server -y')
    print('   sudo systemctl start mysqld')
    print('   sudo systemctl enable mysqld')
    print('   sudo mysql_secure_installation')
    print()
    print('6. 🔧 CONFIGURAR MYSQL:')
    print('   sudo mysql -u root -p')
    print('   # No MySQL:')
    print('   CREATE DATABASE sistema_ml;')
    print('   CREATE USER "admin"@"%" IDENTIFIED BY "2154";')
    print('   GRANT ALL PRIVILEGES ON sistema_ml.* TO "admin"@"%";')
    print('   FLUSH PRIVILEGES;')
    print('   EXIT;')
    print()
    print('7. 🌐 CONFIGURAR NGINX:')
    print('   sudo yum install nginx -y')
    print('   sudo nano /etc/nginx/conf.d/flask.conf')
    print('   # Adicionar configuração do Nginx')
    print()
    print('8. 🔧 CONFIGURAR SERVIÇO:')
    print('   sudo nano /etc/systemd/system/flask-app.service')
    print('   # Adicionar configuração do serviço')
    print()
    print('9. 🚀 INICIAR SERVIÇOS:')
    print('   sudo systemctl daemon-reload')
    print('   sudo systemctl start nginx')
    print('   sudo systemctl enable nginx')
    print('   sudo systemctl start flask-app')
    print('   sudo systemctl enable flask-app')
    print()
    print('10. 🔥 CONFIGURAR FIREWALL:')
    print('    sudo firewall-cmd --permanent --add-port=80/tcp')
    print('    sudo firewall-cmd --permanent --add-port=443/tcp')
    print('    sudo firewall-cmd --reload')
    print()
    print('11. ✅ VERIFICAR STATUS:')
    print('    sudo systemctl status nginx')
    print('    sudo systemctl status flask-app')
    print('    sudo systemctl status mysqld')
    print()
    print('12. 🌐 TESTAR APLICAÇÃO:')
    print('    # Acessar no navegador:')
    print('    http://56.124.88.188')
    print()
    print('⚠️ IMPORTANTE:')
    print('   - Certifique-se de que o Security Group da EC2 tem as portas 22, 80 e 443 abertas')
    print('   - O arquivo ZIP contém todos os arquivos necessários')
    print('   - Após o upload, siga os passos acima na ordem')

if __name__ == '__main__':
    prepare_files_for_upload()
