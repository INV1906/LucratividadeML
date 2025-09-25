#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import mysql.connector
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class AuthManager:
    """Gerenciador de autenticação do sistema."""
    
    def __init__(self):
        # Configuração usando variáveis de ambiente
        self.config_class = type('Config', (), {
            'SECRET_KEY': os.getenv('FLASK_SECRET_KEY', 'sua_chave_secreta_aqui'),
            'DB_HOST': os.getenv('DB_HOST', 'localhost'),
            'DB_USER': os.getenv('DB_USER', 'root'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
            'DB_NAME': os.getenv('DB_NAME', 'mercadolivre_lucratividade'),
            'DB_PORT': int(os.getenv('DB_PORT', 3306))
        })()
        self.db_config = {
            'host': self.config_class.DB_HOST,
            'user': self.config_class.DB_USER,
            'password': self.config_class.DB_PASSWORD,
            'database': self.config_class.DB_NAME
        }
    
    def conectar(self):
        """Conecta ao banco de dados."""
        try:
            return mysql.connector.connect(**self.db_config)
        except Exception as e:
            print(f"Erro ao conectar ao banco: {e}")
            return None
    
    def gerar_salt(self) -> str:
        """Gera um salt aleatório para hash de senha."""
        return secrets.token_hex(16)
    
    def hash_senha(self, senha: str, salt: str) -> str:
        """Gera hash da senha usando PBKDF2."""
        return hashlib.pbkdf2_hmac('sha256', senha.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    
    def verificar_senha(self, senha: str, hash_senha: str, salt: str) -> bool:
        """Verifica se a senha está correta."""
        return self.hash_senha(senha, salt) == hash_senha
    
    def gerar_codigo_verificacao(self) -> str:
        """Gera código de 6 dígitos para verificação."""
        return ''.join(secrets.choice(string.digits) for _ in range(6))
    
    def criar_usuario_auth(self, user_id: int, username: str, email: str, senha: str) -> bool:
        """Cria usuário no sistema de autenticação."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Verificar se username já existe
                cursor.execute("SELECT id FROM usuarios_auth WHERE username = %s", (username,))
                if cursor.fetchone():
                    return False
                
                # Gerar salt e hash da senha
                salt = self.gerar_salt()
                password_hash = self.hash_senha(senha, salt)
                
                # Inserir usuário
                cursor.execute("""
                    INSERT INTO usuarios_auth (user_id, username, email, password_hash, salt)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, username, email, password_hash, salt))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao criar usuário auth: {e}")
            return False
        finally:
            conn.close()
    
    def verificar_login(self, username: str, senha: str) -> Optional[Dict[str, Any]]:
        """Verifica credenciais de login."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT ua.*, ui.nickname, ui.first_name 
                    FROM usuarios_auth ua
                    JOIN user_info ui ON ua.user_id = ui.user_id
                    WHERE ua.username = %s AND ua.is_active = TRUE
                """, (username,))
                
                usuario = cursor.fetchone()
                if not usuario:
                    return None
                
                # Verificar senha
                if self.verificar_senha(senha, usuario['password_hash'], usuario['salt']):
                    # Atualizar último login
                    cursor.execute("""
                        UPDATE usuarios_auth 
                        SET last_login = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (usuario['id'],))
                    conn.commit()
                    
                    return {
                        'user_id': usuario['user_id'],
                        'username': usuario['username'],
                        'email': usuario['email'],
                        'nickname': usuario['nickname'],
                        'first_name': usuario['first_name']
                    }
                
                return None
                
        except Exception as e:
            print(f"Erro ao verificar login: {e}")
            return None
        finally:
            conn.close()
    
    def alterar_senha(self, user_id: int, senha_atual: str, nova_senha: str) -> bool:
        """Altera senha do usuário."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Buscar dados do usuário
                cursor.execute("""
                    SELECT password_hash, salt FROM usuarios_auth 
                    WHERE user_id = %s
                """, (user_id,))
                
                usuario = cursor.fetchone()
                if not usuario:
                    return False
                
                # Verificar senha atual
                if not self.verificar_senha(senha_atual, usuario[0], usuario[1]):
                    return False
                
                # Gerar novo salt e hash
                novo_salt = self.gerar_salt()
                novo_hash = self.hash_senha(nova_senha, novo_salt)
                
                # Atualizar senha
                cursor.execute("""
                    UPDATE usuarios_auth 
                    SET password_hash = %s, salt = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (novo_hash, novo_salt, user_id))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao alterar senha: {e}")
            return False
        finally:
            conn.close()
    
    def gerar_codigo_recuperacao(self, email: str) -> Optional[str]:
        """Gera código de recuperação de senha."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                # Buscar usuário pelo email
                cursor.execute("""
                    SELECT ua.user_id FROM usuarios_auth ua
                    WHERE ua.email = %s AND ua.is_active = TRUE
                """, (email,))
                
                usuario = cursor.fetchone()
                if not usuario:
                    return None
                
                user_id = usuario[0]
                codigo = self.gerar_codigo_verificacao()
                expires_at = datetime.now() + timedelta(minutes=30)
                
                # Inserir código
                cursor.execute("""
                    INSERT INTO codigos_verificacao (user_id, codigo, tipo, email, expires_at)
                    VALUES (%s, %s, 'password_reset', %s, %s)
                """, (user_id, codigo, email, expires_at))
                
                conn.commit()
                return codigo
                
        except Exception as e:
            print(f"Erro ao gerar código de recuperação: {e}")
            return None
        finally:
            conn.close()
    
    def verificar_codigo_recuperacao(self, email: str, codigo: str) -> Optional[int]:
        """Verifica código de recuperação e retorna user_id."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id FROM codigos_verificacao 
                    WHERE email = %s AND codigo = %s AND tipo = 'password_reset'
                    AND expires_at > NOW() AND used_at IS NULL
                """, (email, codigo))
                
                resultado = cursor.fetchone()
                if resultado:
                    return resultado[0]
                return None
                
        except Exception as e:
            print(f"Erro ao verificar código: {e}")
            return None
        finally:
            conn.close()
    
    def redefinir_senha(self, user_id: int, nova_senha: str, codigo: str) -> bool:
        """Redefine senha usando código de verificação."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Verificar se código é válido
                cursor.execute("""
                    SELECT id FROM codigos_verificacao 
                    WHERE user_id = %s AND codigo = %s AND tipo = 'password_reset'
                    AND expires_at > NOW() AND used_at IS NULL
                """, (user_id, codigo))
                
                if not cursor.fetchone():
                    return False
                
                # Gerar nova senha
                novo_salt = self.gerar_salt()
                novo_hash = self.hash_senha(nova_senha, novo_salt)
                
                # Atualizar senha
                cursor.execute("""
                    UPDATE usuarios_auth 
                    SET password_hash = %s, salt = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                """, (novo_hash, novo_salt, user_id))
                
                # Marcar código como usado
                cursor.execute("""
                    UPDATE codigos_verificacao 
                    SET used_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND codigo = %s AND tipo = 'password_reset'
                """, (user_id, codigo))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao redefinir senha: {e}")
            return False
        finally:
            conn.close()
    
    def criar_sessao(self, user_id: int, login_type: str, ip_address: str = None, user_agent: str = None) -> str:
        """Cria nova sessão para o usuário."""
        conn = None
        try:
            from configuracao_sessoes import ConfiguracaoSessoes
            
            # Verificar se pode criar nova sessão
            if not self.verificar_limite_sessoes_usuario(user_id):
                print(f"❌ Limite de sessões excedido para usuário {user_id}")
                return None
            
            # Encerrar sessões antigas se necessário
            self.encerrar_sessoes_antigas_usuario(user_id)
            
            conn = self.conectar()
            if not conn:
                return None
            
            with conn.cursor() as cursor:
                # Gerar token de sessão
                session_token = secrets.token_urlsafe(32)
                
                # Usar tempo de expiração configurado
                horas_expiracao = ConfiguracaoSessoes.obter_tempo_expiracao_horas()
                expires_at = datetime.now() + timedelta(hours=horas_expiracao)
                
                # Inserir sessão
                cursor.execute("""
                    INSERT INTO sessoes_ativas (user_id, session_token, login_type, expires_at, ip_address, user_agent)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (user_id, session_token, login_type, expires_at, ip_address, user_agent))
                
                conn.commit()
                print(f"✅ Nova sessão criada para usuário {user_id} (expira em {horas_expiracao}h)")
                return session_token
                
        except Exception as e:
            print(f"Erro ao criar sessão: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def verificar_sessao(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Verifica se sessão é válida."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT sa.*, ua.username, ua.email, ui.nickname, ui.first_name
                    FROM sessoes_ativas sa
                    JOIN usuarios_auth ua ON sa.user_id = ua.user_id
                    JOIN user_info ui ON sa.user_id = ui.user_id
                    WHERE sa.session_token = %s AND sa.expires_at > NOW()
                """, (session_token,))
                
                sessao = cursor.fetchone()
                if sessao:
                    # Atualizar última atividade
                    cursor.execute("""
                        UPDATE sessoes_ativas 
                        SET last_activity = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (sessao['id'],))
                    conn.commit()
                    
                    return {
                        'user_id': sessao['user_id'],
                        'username': sessao['username'],
                        'email': sessao['email'],
                        'nickname': sessao['nickname'],
                        'first_name': sessao['first_name'],
                        'login_type': sessao['login_type']
                    }
                
                return None
                
        except Exception as e:
            print(f"Erro ao verificar sessão: {e}")
            return None
        finally:
            conn.close()
    
    def encerrar_sessao(self, session_token: str) -> bool:
        """Encerra sessão do usuário."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM sessoes_ativas 
                    WHERE session_token = %s
                """, (session_token,))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Erro ao encerrar sessão: {e}")
            return False
        finally:
            conn.close()
    
    def verificar_sessao_ativa_usuario(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Verifica se usuário tem sessão ativa e retorna dados da sessão."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT * FROM sessoes_ativas 
                    WHERE user_id = %s AND expires_at > NOW()
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (user_id,))
                
                return cursor.fetchone()
                
        except Exception as e:
            print(f"Erro ao verificar sessão ativa: {e}")
            return None
        finally:
            conn.close()
    
    def verificar_limite_sessoes_usuario(self, user_id: int) -> bool:
        """Verifica se usuário pode criar nova sessão (respeitando limite)"""
        conn = None
        try:
            from configuracao_sessoes import ConfiguracaoSessoes
            
            if not ConfiguracaoSessoes.deve_permitir_multiplas_sessoes():
                return True  # Se não permite múltiplas, sempre pode criar (substitui a anterior)
            
            conn = self.conectar()
            if not conn:
                return False
            
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) FROM sessoes_ativas 
                    WHERE user_id = %s AND expires_at > NOW()
                """, (user_id,))
                
                count = cursor.fetchone()[0]
                max_sessoes = ConfiguracaoSessoes.obter_max_sessoes_por_usuario()
                
                return count < max_sessoes
                
        except Exception as e:
            print(f"Erro ao verificar limite de sessões: {e}")
            return True  # Em caso de erro, permite criar
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def encerrar_sessoes_antigas_usuario(self, user_id: int):
        """Encerra sessões antigas do usuário se exceder o limite"""
        conn = None
        try:
            from configuracao_sessoes import ConfiguracaoSessoes
            
            if not ConfiguracaoSessoes.deve_permitir_multiplas_sessoes():
                return  # Se não permite múltiplas, não precisa encerrar antigas
            
            conn = self.conectar()
            if not conn:
                return
            
            max_sessoes = ConfiguracaoSessoes.obter_max_sessoes_por_usuario()
            
            with conn.cursor() as cursor:
                # Buscar sessões ativas ordenadas por data de criação (mais antigas primeiro)
                cursor.execute("""
                    SELECT id FROM sessoes_ativas 
                    WHERE user_id = %s AND expires_at > NOW()
                    ORDER BY created_at ASC
                """, (user_id,))
                
                sessoes = cursor.fetchall()
                
                # Se exceder o limite, remove as mais antigas
                if len(sessoes) >= max_sessoes:
                    sessoes_para_remover = sessoes[:len(sessoes) - max_sessoes + 1]
                    
                    for sessao_id in sessoes_para_remover:
                        cursor.execute("""
                            DELETE FROM sessoes_ativas WHERE id = %s
                        """, (sessao_id[0],))
                    
                    conn.commit()
                    print(f"Encerradas {len(sessoes_para_remover)} sessões antigas do usuário {user_id}")
                
        except Exception as e:
            print(f"Erro ao encerrar sessões antigas: {e}")
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def limpar_sessoes_expiradas(self):
        """Remove sessões expiradas do banco."""
        conn = self.conectar()
        if not conn:
            return
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM sessoes_ativas 
                    WHERE expires_at <= NOW()
                """)
                
                conn.commit()
                
        except Exception as e:
            print(f"Erro ao limpar sessões expiradas: {e}")
        finally:
            conn.close()
