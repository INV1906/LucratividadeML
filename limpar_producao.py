#!/usr/bin/env python3
"""
Script para limpar arquivos desnecessários antes da produção
"""

import os
import shutil
import sys

def confirmar_acao(mensagem):
    """Confirma ação com o usuário"""
    resposta = input(f"{mensagem} (s/N): ").lower().strip()
    return resposta in ['s', 'sim', 'y', 'yes']

def remover_arquivos_teste():
    """Remove arquivos de teste"""
    arquivos_teste = [
        'test_*.py',
        'debug_*.py', 
        'create_produtos_table.py',
        'atualizar_traducoes.py',
        'configurar_ngrok.py',
        'test_webhook_page.html',
        'teste_ngrok.html',
        'save/',
        'Dump20250916/',
        'env_example.txt',
        'executar_producao.sh',
        'GUIA_WEBHOOKS.md',
        'resumo_melhorias_frete_taxas.md',
        'EXECUTAR.md'
    ]
    
    print("🗑️ ARQUIVOS DE TESTE E DESENVOLVIMENTO:")
    print("=" * 50)
    
    for arquivo in arquivos_teste:
        if os.path.exists(arquivo):
            if os.path.isdir(arquivo):
                print(f"📁 {arquivo}/ (diretório)")
            else:
                print(f"📄 {arquivo}")
    
    if confirmar_acao("\n❓ Remover estes arquivos?"):
        for arquivo in arquivos_teste:
            if os.path.exists(arquivo):
                try:
                    if os.path.isdir(arquivo):
                        shutil.rmtree(arquivo)
                        print(f"✅ Removido diretório: {arquivo}")
                    else:
                        os.remove(arquivo)
                        print(f"✅ Removido arquivo: {arquivo}")
                except Exception as e:
                    print(f"❌ Erro ao remover {arquivo}: {e}")
        print("\n✅ Limpeza de arquivos concluída!")
    else:
        print("⏭️ Limpeza cancelada pelo usuário")

def configurar_producao():
    """Configura arquivos para produção"""
    print("\n🔧 CONFIGURAÇÕES DE PRODUÇÃO:")
    print("=" * 50)
    
    # Configurar app.py
    if confirmar_acao("❓ Configurar app.py para produção (DEBUG=False)?"):
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Substituir debug=True por variável de ambiente
            conteudo = conteudo.replace(
                "app.run(debug=True, host='0.0.0.0', port=port, ssl_context=ssl_context)",
                "app.run(debug=os.getenv('DEBUG', 'False').lower() == 'true', host='0.0.0.0', port=port, ssl_context=ssl_context)"
            )
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            print("✅ app.py configurado para produção")
        except Exception as e:
            print(f"❌ Erro ao configurar app.py: {e}")
    
    # Configurar config.py
    if confirmar_acao("❓ Remover URLs hardcoded do config.py?"):
        try:
            with open('config.py', 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Remover URL padrão do ngrok
            conteudo = conteudo.replace(
                "MELI_REDIRECT_URI = os.getenv('MELI_REDIRECT_URI', 'https://c1979facbdcd.ngrok-free.app/callback')",
                "MELI_REDIRECT_URI = os.getenv('MELI_REDIRECT_URI')"
            )
            
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write(conteudo)
            
            print("✅ config.py configurado para produção")
        except Exception as e:
            print(f"❌ Erro ao configurar config.py: {e}")

def criar_arquivo_env_producao():
    """Cria arquivo .env.production"""
    print("\n📄 ARQUIVO DE CONFIGURAÇÃO DE PRODUÇÃO:")
    print("=" * 50)
    
    if confirmar_acao("❓ Criar arquivo .env.production?"):
        env_content = """# Configurações de Produção
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=seu_secret_key_super_seguro_aqui

# Banco de Dados
DB_HOST=seu_host_producao
DB_USER=seu_usuario_producao
DB_PASSWORD=sua_senha_producao
DB_NAME=mercadolivre_lucratividade

# Mercado Livre
MELI_APP_ID=seu_app_id
MELI_CLIENT_SECRET=seu_client_secret
MELI_REDIRECT_URI=https://seu_dominio.com/callback

# Configurações de Produção
NGROK_HTTPS=false
PORT=5000
"""
        
        try:
            with open('.env.production', 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ Arquivo .env.production criado")
            print("⚠️  IMPORTANTE: Configure as variáveis antes de usar!")
        except Exception as e:
            print(f"❌ Erro ao criar .env.production: {e}")

def criar_requirements_producao():
    """Cria requirements.txt otimizado para produção"""
    print("\n📦 DEPENDÊNCIAS DE PRODUÇÃO:")
    print("=" * 50)
    
    if confirmar_acao("❓ Criar requirements.txt otimizado para produção?"):
        requirements_content = """# Dependências de Produção
Flask==2.2.5
mysql-connector-python==8.1.0
python-dotenv==1.0.0
requests==2.31.0
Werkzeug==2.2.3
Jinja2==3.1.2
MarkupSafe==2.1.3
itsdangerous==2.1.2
click==8.1.7
blinker==1.6.2

# Servidor de Produção (opcional)
gunicorn==21.2.0
"""
        
        try:
            with open('requirements.production.txt', 'w', encoding='utf-8') as f:
                f.write(requirements_content)
            print("✅ requirements.production.txt criado")
        except Exception as e:
            print(f"❌ Erro ao criar requirements.production.txt: {e}")

def mostrar_resumo():
    """Mostra resumo final"""
    print("\n🎉 LIMPEZA CONCLUÍDA!")
    print("=" * 50)
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Configure as variáveis no .env.production")
    print("2. Configure seu banco de dados de produção")
    print("3. Configure seu domínio de produção")
    print("4. Teste a aplicação em ambiente de produção")
    print("5. Configure SSL/HTTPS")
    print("6. Configure backup automático")
    print("\n🚀 SUA APLICAÇÃO ESTÁ PRONTA PARA PRODUÇÃO!")

def main():
    """Função principal"""
    print("🧹 LIMPEZA PARA PRODUÇÃO")
    print("=" * 50)
    print("Este script irá:")
    print("• Remover arquivos de teste e desenvolvimento")
    print("• Configurar arquivos para produção")
    print("• Criar arquivos de configuração")
    print("• Otimizar dependências")
    print()
    
    if not confirmar_acao("❓ Continuar com a limpeza?"):
        print("⏭️ Operação cancelada pelo usuário")
        return
    
    # Executar limpeza
    remover_arquivos_teste()
    configurar_producao()
    criar_arquivo_env_producao()
    criar_requirements_producao()
    mostrar_resumo()

if __name__ == "__main__":
    main()
