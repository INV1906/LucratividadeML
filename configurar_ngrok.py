#!/usr/bin/env python3
"""
Script para configurar ngrok com as configurações corretas.
"""

import subprocess
import sys
import time
import requests
import json

def verificar_ngrok():
    """Verifica se o ngrok está instalado."""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ngrok encontrado: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ngrok não encontrado")
            return False
    except FileNotFoundError:
        print("❌ Ngrok não está instalado")
        print("📥 Baixe em: https://ngrok.com/download")
        return False

def obter_url_ngrok():
    """Obtém a URL atual do ngrok."""
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels')
        if response.status_code == 200:
            data = response.json()
            for tunnel in data['tunnels']:
                if tunnel['proto'] == 'https':
                    url = tunnel['public_url']
                    print(f"✅ URL do ngrok encontrada: {url}")
                    return url
        return None
    except requests.exceptions.RequestException:
        print("❌ Não foi possível conectar ao ngrok")
        return None

def iniciar_ngrok(porta=5000):
    """Inicia o ngrok na porta especificada."""
    print(f"🚀 Iniciando ngrok na porta {porta}...")
    
    # Comando para iniciar ngrok
    cmd = ['ngrok', 'http', str(porta), '--log=stdout']
    
    try:
        # Inicia ngrok em background
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Aguarda um momento para ngrok inicializar
        time.sleep(3)
        
        # Verifica se ngrok está rodando
        url = obter_url_ngrok()
        if url:
            print(f"✅ Ngrok iniciado com sucesso!")
            print(f"🌐 URL pública: {url}")
            print(f"🔗 URL de callback: {url}/callback")
            print("\n📋 Atualize seu arquivo .env com:")
            print(f"MELI_REDIRECT_URI={url}/callback")
            return url
        else:
            print("❌ Falha ao obter URL do ngrok")
            return None
            
    except Exception as e:
        print(f"❌ Erro ao iniciar ngrok: {e}")
        return None

def configurar_aplicacao_ml(ngrok_url):
    """Fornece instruções para configurar a aplicação no Mercado Livre."""
    print("\n🔧 Configure sua aplicação no Mercado Livre:")
    print("1. Acesse: https://developers.mercadolibre.com/")
    print("2. Vá em 'Suas aplicações'")
    print("3. Edite sua aplicação")
    print(f"4. Configure a URL de callback: {ngrok_url}/callback")
    print("5. Salve as alterações")

def main():
    """Função principal."""
    print("🔧 Configurador do Ngrok para Mercado Livre")
    print("=" * 50)
    
    # Verifica se ngrok está instalado
    if not verificar_ngrok():
        return
    
    # Verifica se ngrok já está rodando
    url_existente = obter_url_ngrok()
    if url_existente:
        print("ℹ️  Ngrok já está rodando")
        configurar_aplicacao_ml(url_existente)
        return
    
    # Inicia ngrok
    porta = input("Digite a porta da aplicação Flask (padrão: 5000): ").strip()
    if not porta:
        porta = 5000
    else:
        try:
            porta = int(porta)
        except ValueError:
            print("❌ Porta inválida, usando 5000")
            porta = 5000
    
    url = iniciar_ngrok(porta)
    if url:
        configurar_aplicacao_ml(url)
        
        print("\n⚠️  IMPORTANTE:")
        print("1. Mantenha este terminal aberto enquanto usa a aplicação")
        print("2. Atualize o arquivo .env com a nova URL")
        print("3. Reinicie a aplicação Flask")
        print("4. Configure a URL no painel do Mercado Livre")
        
        input("\nPressione Enter para finalizar...")
    
if __name__ == "__main__":
    main()
