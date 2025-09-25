#!/usr/bin/env python3
"""
Script para criar ZIP com arquivos necessários para deploy
"""

import zipfile
import os
from datetime import datetime

def criar_zip_deploy():
    """Criar ZIP com arquivos necessários para deploy"""
    
    print("📦 CRIANDO ZIP PARA DEPLOY AWS")
    print("=" * 40)
    
    # Arquivos necessários para deploy
    arquivos_deploy = [
        'app_aws.py',
        'wsgi.py',
        'requirements_aws_clean.txt',
        'nginx.conf',
        'mercadolivre-app.service',
        'deploy.sh',
        '.env_aws_example',
        'test_deployment.py',
        'GUIA_COMPLETO_AWS_INICIANTE.md'
    ]
    
    # Pasta templates
    pasta_templates = 'templates'
    
    # Nome do arquivo ZIP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_zip = f"mercadolivre_deploy_{timestamp}.zip"
    
    print(f"📁 Criando: {nome_zip}")
    
    with zipfile.ZipFile(nome_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # Adicionar arquivos principais
        for arquivo in arquivos_deploy:
            if os.path.exists(arquivo):
                zipf.write(arquivo)
                print(f"✅ Adicionado: {arquivo}")
            else:
                print(f"❌ Não encontrado: {arquivo}")
        
        # Adicionar pasta templates
        if os.path.exists(pasta_templates):
            for root, dirs, files in os.walk(pasta_templates):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path)
                    zipf.write(file_path, arc_path)
                    print(f"✅ Adicionado: {arc_path}")
        else:
            print(f"❌ Pasta não encontrada: {pasta_templates}")
    
    # Verificar tamanho do arquivo
    tamanho = os.path.getsize(nome_zip)
    tamanho_mb = tamanho / (1024 * 1024)
    
    print("\n" + "=" * 40)
    print(f"📦 ZIP CRIADO: {nome_zip}")
    print(f"📏 Tamanho: {tamanho_mb:.2f} MB")
    print("\n📋 ARQUIVOS INCLUÍDOS:")
    print("   ✅ app_aws.py - Aplicação principal")
    print("   ✅ wsgi.py - WSGI para Gunicorn")
    print("   ✅ requirements_aws_clean.txt - Dependências")
    print("   ✅ nginx.conf - Configuração Nginx")
    print("   ✅ mercadolivre-app.service - Serviço systemd")
    print("   ✅ deploy.sh - Script de deploy")
    print("   ✅ .env_aws_example - Exemplo de configuração")
    print("   ✅ test_deployment.py - Script de teste")
    print("   ✅ GUIA_COMPLETO_AWS_INICIANTE.md - Guia completo")
    print("   ✅ templates/ - Pasta de templates")
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Siga o GUIA_COMPLETO_AWS_INICIANTE.md")
    print("2. Faça upload do ZIP para sua instância EC2")
    print("3. Execute o deploy.sh")
    print("4. Teste com test_deployment.py")
    
    return nome_zip

if __name__ == "__main__":
    criar_zip_deploy()
