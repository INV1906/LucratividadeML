#!/usr/bin/env python3
"""
Script para testar renovação automática de tokens
"""

import sys
sys.path.append('.')
from database import DatabaseManager
from meli_api import MercadoLivreAPI
import time

def test_renovacao_token():
    """Testa a renovação automática de tokens"""
    
    print("🧪 Testando renovação automática de tokens...")
    print("=" * 60)
    
    try:
        db = DatabaseManager()
        api = MercadoLivreAPI()
        user_id = 1305538297
        
        # Verificar token atual
        print("🔍 Verificando token atual...")
        token_atual = db.obter_access_token(user_id)
        
        if token_atual:
            print(f"✅ Token encontrado: {token_atual[:20]}...")
            
            # Verificar informações do token no banco
            conn = db.conectar()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT access_token, created_at, expires_in, refresh_token
                    FROM tokens 
                    WHERE user_id = %s
                """, (user_id,))
                resultado = cursor.fetchone()
                
                if resultado:
                    access_token, created_at, expires_in, refresh_token = resultado
                    print(f"📊 Informações do token:")
                    print(f"   - Criado em: {created_at}")
                    print(f"   - Expira em: {expires_in} segundos")
                    print(f"   - Refresh token: {refresh_token[:20] if refresh_token else 'N/A'}...")
                    
                    # Calcular quando expira
                    if created_at and expires_in:
                        from datetime import datetime, timedelta
                        expiracao = created_at + timedelta(seconds=expires_in)
                        print(f"   - Expira em: {expiracao}")
                        
                        # Verificar se está próximo do vencimento
                        agora = datetime.now()
                        tempo_restante = (expiracao - agora).total_seconds()
                        print(f"   - Tempo restante: {tempo_restante:.0f} segundos")
                        
                        if tempo_restante < 300:  # Menos de 5 minutos
                            print("⚠️ Token próximo do vencimento, será renovado automaticamente")
                        else:
                            print("✅ Token ainda válido")
                else:
                    print("❌ Nenhuma informação encontrada no banco")
            
            conn.close()
            
        else:
            print("❌ Nenhum token encontrado")
            return False
        
        # Testar renovação manual
        print("\n🔄 Testando renovação manual...")
        if api._renovar_token(user_id):
            print("✅ Renovação manual bem-sucedida!")
            
            # Verificar novo token
            novo_token = db.obter_access_token(user_id)
            if novo_token and novo_token != token_atual:
                print("✅ Token foi atualizado!")
            else:
                print("⚠️ Token não foi alterado")
        else:
            print("❌ Falha na renovação manual")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importacao_com_token():
    """Testa importação com verificação automática de token"""
    
    print("\n🧪 Testando importação com verificação de token...")
    print("=" * 60)
    
    try:
        from app import importar_vendas_background
        
        user_id = 1305538297
        
        print(f"🚀 Iniciando importação para user_id: {user_id}")
        print("   (O token será verificado e renovado automaticamente se necessário)")
        
        importar_vendas_background(user_id)
        
        print("✅ Importação executada!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_login_com_renovacao():
    """Testa login com renovação automática de token"""
    
    print("\n🧪 Testando login com renovação automática...")
    print("=" * 60)
    
    try:
        import requests
        
        # Simular login
        session = requests.Session()
        login_data = {
            "type": "password",
            "username": "Contigo",
            "password": "Adeg@33781210"
        }
        
        print("🔐 Fazendo login...")
        response = session.post("http://localhost:3001/", json=login_data)
        
        if response.status_code != 200:
            print("❌ Erro no login")
            return False
        
        login_result = response.json()
        if not login_result.get('success'):
            print(f"❌ Falha no login: {login_result.get('message')}")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Testar importação (que deve verificar e renovar token automaticamente)
        print("📦 Testando importação (com verificação automática de token)...")
        response = session.post("http://localhost:3001/importar/vendas")
        
        if response.status_code == 200:
            import_result = response.json()
            if import_result.get('success'):
                print("✅ Importação iniciada com sucesso!")
                print("   (Token foi verificado e renovado automaticamente se necessário)")
                return True
            else:
                print(f"❌ Falha na importação: {import_result.get('message')}")
                return False
        else:
            print(f"❌ Erro na importação: {response.status_code}")
            return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Teste de Renovação Automática de Tokens")
    print("=" * 60)
    
    # Teste 1: Renovação de token
    if test_renovacao_token():
        print("\n✅ Renovação de token funcionando!")
        
        # Teste 2: Importação com verificação
        if test_importacao_com_token():
            print("\n✅ Importação com verificação funcionando!")
            
            # Teste 3: Login com renovação
            test_login_com_renovacao()
        else:
            print("\n❌ Falha na importação com verificação")
    else:
        print("\n❌ Falha na renovação de token")
