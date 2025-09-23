#!/usr/bin/env python3
"""
Script para testar o deploy da aplicação
"""

import requests
import time
import sys

def test_deployment(ip_publico):
    """Testar se a aplicação está funcionando"""
    
    print(f"🧪 TESTANDO DEPLOY EM: {ip_publico}")
    print("=" * 50)
    
    # URLs para testar
    urls = [
        f"http://{ip_publico}/",
        f"http://{ip_publico}/health",
        f"http://{ip_publico}/login",
    ]
    
    results = []
    
    for url in urls:
        try:
            print(f"🔍 Testando: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ OK - Status: {response.status_code}")
                results.append(True)
            else:
                print(f"❌ ERRO - Status: {response.status_code}")
                results.append(False)
                
        except requests.exceptions.RequestException as e:
            print(f"❌ ERRO - {e}")
            results.append(False)
        
        time.sleep(1)
    
    # Resultado final
    print("\n" + "=" * 50)
    if all(results):
        print("🎉 DEPLOY SUCESSO! Aplicação funcionando!")
        return True
    else:
        print("❌ DEPLOY COM PROBLEMAS! Verifique os logs.")
        return False

def test_database_connection(ip_publico):
    """Testar conexão com banco de dados"""
    
    print(f"\n🗄️ TESTANDO CONEXÃO COM BANCO")
    print("=" * 50)
    
    try:
        response = requests.get(f"http://{ip_publico}/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('database') == 'connected':
                print("✅ Banco de dados conectado!")
                return True
            else:
                print("❌ Banco de dados desconectado!")
                return False
        else:
            print(f"❌ Erro ao testar banco - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar banco: {e}")
        return False

def main():
    """Função principal"""
    
    if len(sys.argv) != 2:
        print("❌ Uso: python test_deployment.py <IP_PUBLICO>")
        print("   Exemplo: python test_deployment.py 18.228.153.23")
        sys.exit(1)
    
    ip_publico = sys.argv[1]
    
    print("🚀 TESTE DE DEPLOY - MERCADOLIVRE APP")
    print("=" * 50)
    
    # Testar aplicação
    app_ok = test_deployment(ip_publico)
    
    # Testar banco
    db_ok = test_database_connection(ip_publico)
    
    # Resultado final
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    print(f"   Aplicação: {'✅ OK' if app_ok else '❌ ERRO'}")
    print(f"   Banco: {'✅ OK' if db_ok else '❌ ERRO'}")
    
    if app_ok and db_ok:
        print("\n🎉 PARABÉNS! Deploy completo e funcionando!")
        print(f"🌐 Acesse: http://{ip_publico}")
    else:
        print("\n❌ Deploy com problemas. Verifique os logs:")
        print("   sudo journalctl -u mercadolivre-app -f")
        print("   sudo systemctl status mercadolivre-app")

if __name__ == "__main__":
    main()
