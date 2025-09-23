#!/usr/bin/env python3
"""
Script para facilitar upload dos arquivos para EC2
"""

import os
import subprocess
import sys

def upload_files_to_ec2():
    print('🚀 UPLOAD DOS ARQUIVOS PARA EC2')
    print('=' * 50)
    
    # IP da instância
    ec2_ip = '56.124.88.188'
    key_file = input('📁 Caminho para o arquivo .pem da chave SSH: ').strip()
    
    if not os.path.exists(key_file):
        print(f'❌ Arquivo de chave não encontrado: {key_file}')
        return
    
    print(f'✅ Chave encontrada: {key_file}')
    print()
    
    # Arquivos essenciais para upload
    essential_files = [
        'app.py',
        'database.py',
        'meli_api.py',
        'webhook_processor.py',
        'webhook_logger.py',
        'token_monitor.py',
        'sync_manager.py',
        'shipping_status.py',
        'translations.py',
        'requirements.txt',
        '.env_ec2',
        'templates/',
        'static/'
    ]
    
    print('📤 ARQUIVOS QUE SERÃO ENVIADOS:')
    for file in essential_files:
        if os.path.exists(file):
            print(f'   ✅ {file}')
        else:
            print(f'   ❌ {file} (não encontrado)')
    
    print()
    confirm = input('🤔 Continuar com o upload? (s/n): ').lower()
    
    if confirm != 's':
        print('❌ Upload cancelado')
        return
    
    print()
    print('📤 INICIANDO UPLOAD...')
    
    # Comando scp para upload
    cmd = [
        'scp',
        '-i', key_file,
        '-r',
        'app.py',
        'database.py',
        'meli_api.py',
        'webhook_processor.py',
        'webhook_logger.py',
        'token_monitor.py',
        'sync_manager.py',
        'shipping_status.py',
        'translations.py',
        'requirements.txt',
        '.env_ec2',
        'templates/',
        'static/',
        f'ec2-user@{ec2_ip}:/home/ec2-user/mercadolivre-app/'
    ]
    
    try:
        print('🔄 Executando comando scp...')
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print('✅ Upload concluído com sucesso!')
        print()
        print('🔧 PRÓXIMOS PASSOS:')
        print('   1. Conectar via SSH:')
        print(f'      ssh -i {key_file} ec2-user@{ec2_ip}')
        print('   2. Renomear .env_ec2 para .env:')
        print('      mv .env_ec2 .env')
        print('   3. Instalar dependências:')
        print('      pip3.11 install -r requirements.txt')
        print('   4. Instalar MySQL:')
        print('      sudo yum install mysql-server -y')
        print('   5. Configurar serviços (Nginx, systemd)')
        print('   6. Testar aplicação:')
        print(f'      http://{ec2_ip}')
        
    except subprocess.CalledProcessError as e:
        print(f'❌ Erro no upload: {e}')
        print('💡 Dica: Verifique se o arquivo .pem tem as permissões corretas:')
        print('   chmod 400 sua-chave.pem')
    except FileNotFoundError:
        print('❌ Comando scp não encontrado')
        print('💡 Dica: Instale o OpenSSH ou use Git Bash no Windows')

if __name__ == '__main__':
    upload_files_to_ec2()
