#!/usr/bin/env python3
"""
Sistema de Monitoramento de Tokens e Sincronização de Dados
Verifica periodicamente tokens expirados e sincroniza dados perdidos
"""

import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any
from database import DatabaseManager
from meli_api import MercadoLivreAPI

class TokenMonitor:
    """Monitor de tokens e sincronização de dados"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.api = MercadoLivreAPI()
        self.running = False
        self.monitor_thread = None
        self.check_interval = 300  # 5 minutos
        
    def start_monitoring(self):
        """Inicia o monitoramento em background"""
        if self.running:
            print("⚠️ Monitor já está rodando")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("🔄 Monitor de tokens iniciado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️ Monitor de tokens parado")
    
    def _monitor_loop(self):
        """Loop principal do monitor"""
        while self.running:
            try:
                print(f"🔍 Verificando tokens - {datetime.now().strftime('%H:%M:%S')}")
                
                # Verifica usuários que precisam reautenticar
                self._check_expired_tokens()
                
                # Sincroniza dados perdidos
                self._sync_lost_data()
                
                # Aguarda próxima verificação
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"❌ Erro no monitor: {e}")
                time.sleep(60)  # Aguarda 1 minuto em caso de erro
    
    def _check_expired_tokens(self):
        """Verifica tokens expirados e marca para reautenticação"""
        try:
            conn = self.db.conectar()
            if not conn:
                return
            
            with conn.cursor() as cursor:
                # Busca tokens próximos do vencimento (menos de 10 minutos)
                cursor.execute("""
                    SELECT user_id, created_at, expires_in 
                    FROM tokens 
                    WHERE needs_reauth = 0
                    AND created_at IS NOT NULL 
                    AND expires_in IS NOT NULL
                """)
                
                tokens = cursor.fetchall()
                
                for user_id, created_at, expires_in in tokens:
                    if not created_at or not expires_in:
                        continue
                    
                    # Calcula quando expira
                    expiracao = created_at + timedelta(seconds=expires_in)
                    tempo_restante = (expiracao - datetime.now()).total_seconds()
                    
                    # Se restam menos de 10 minutos, tenta renovar
                    if tempo_restante < 600:  # 10 minutos
                        print(f"🔄 Token próximo do vencimento para user_id {user_id}")
                        
                        # Tenta renovar
                        if not self.api._renovar_token(user_id):
                            print(f"⚠️ Falha ao renovar token para user_id {user_id}")
                            # Marca para reautenticação
                            self.api._marcar_para_reautenticacao(user_id)
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao verificar tokens expirados: {e}")
    
    def _sync_lost_data(self):
        """Sincroniza dados perdidos de usuários que reautenticaram"""
        try:
            conn = self.db.conectar()
            if not conn:
                return
            
            with conn.cursor() as cursor:
                # Busca usuários que precisam sincronizar
                cursor.execute("""
                    SELECT user_id, last_reauth_attempt, last_sync_attempt
                    FROM tokens 
                    WHERE needs_reauth = 1
                    AND last_reauth_attempt IS NOT NULL
                    AND (last_sync_attempt IS NULL OR last_sync_attempt < last_reauth_attempt)
                """)
                
                usuarios_sync = cursor.fetchall()
                
                for user_id, last_reauth, last_sync in usuarios_sync:
                    print(f"🔄 Sincronizando dados perdidos para user_id {user_id}")
                    
                    # Sincroniza dados perdidos
                    if self.api.sincronizar_dados_perdidos(user_id):
                        print(f"✅ Dados sincronizados para user_id {user_id}")
                    else:
                        print(f"❌ Falha na sincronização para user_id {user_id}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Erro ao sincronizar dados perdidos: {e}")
    
    def force_sync_user(self, user_id: int) -> bool:
        """Força sincronização de um usuário específico"""
        try:
            print(f"🔄 Forçando sincronização para user_id {user_id}")
            return self.api.sincronizar_dados_perdidos(user_id)
        except Exception as e:
            print(f"❌ Erro na sincronização forçada: {e}")
            return False
    
    def get_users_needing_reauth(self) -> List[Dict[str, Any]]:
        """Retorna lista de usuários que precisam reautenticar"""
        try:
            conn = self.db.conectar()
            if not conn:
                return []
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id, last_reauth_attempt, needs_reauth
                    FROM tokens 
                    WHERE needs_reauth = 1
                    ORDER BY last_reauth_attempt DESC
                """)
                
                usuarios = []
                for user_id, last_reauth, needs_reauth in cursor.fetchall():
                    usuarios.append({
                        'user_id': user_id,
                        'last_reauth_attempt': last_reauth,
                        'needs_reauth': needs_reauth
                    })
                
                return usuarios
            
        except Exception as e:
            print(f"❌ Erro ao obter usuários para reautenticação: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

# Instância global do monitor
token_monitor = TokenMonitor()

def start_token_monitoring():
    """Inicia o monitoramento de tokens"""
    token_monitor.start_monitoring()

def stop_token_monitoring():
    """Para o monitoramento de tokens"""
    token_monitor.stop_monitoring()

def force_sync_user(user_id: int) -> bool:
    """Força sincronização de um usuário"""
    return token_monitor.force_sync_user(user_id)

def get_users_needing_reauth() -> List[Dict[str, Any]]:
    """Retorna usuários que precisam reautenticar"""
    return token_monitor.get_users_needing_reauth()

if __name__ == "__main__":
    # Teste do monitor
    print("🧪 Testando monitor de tokens...")
    
    monitor = TokenMonitor()
    
    # Testa verificação de tokens
    print("🔍 Verificando tokens expirados...")
    monitor._check_expired_tokens()
    
    # Testa sincronização
    print("🔄 Testando sincronização...")
    monitor._sync_lost_data()
    
    # Lista usuários que precisam reautenticar
    print("👥 Usuários que precisam reautenticar:")
    usuarios = monitor.get_users_needing_reauth()
    for usuario in usuarios:
        print(f"   - User ID: {usuario['user_id']}, Última tentativa: {usuario['last_reauth_attempt']}")
    
    print("✅ Teste concluído!")
