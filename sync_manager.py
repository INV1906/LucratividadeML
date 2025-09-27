#!/usr/bin/env python3
"""
Sistema de Sincronização Incremental
Detecta e sincroniza apenas mudanças ocorridas durante períodos offline
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from database import DatabaseManager
from meli_api import MercadoLivreAPI
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncManager:
    """Gerenciador de sincronização incremental"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.api = MercadoLivreAPI()
        self.sync_status = {}
        self.sync_thread = None
        self.running = False
        
    def criar_tabelas_sync(self):
        """Cria tabelas necessárias para controle de sincronização"""
        conn = self.db.conectar()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # Tabela de controle de sincronização por usuário
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sync_control (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        sync_type ENUM('vendas', 'produtos', 'webhooks') NOT NULL,
                        last_sync_at TIMESTAMP NULL,
                        last_successful_sync TIMESTAMP NULL,
                        last_sync_status ENUM('success', 'error', 'partial') DEFAULT 'success',
                        last_error_message TEXT NULL,
                        sync_frequency_minutes INT DEFAULT 15,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_user_sync (user_id, sync_type),
                        INDEX idx_user_active (user_id, is_active),
                        INDEX idx_last_sync (last_sync_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                # Tabela de histórico de sincronizações
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sync_history (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        sync_type ENUM('vendas', 'produtos', 'webhooks') NOT NULL,
                        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP NULL,
                        status ENUM('running', 'success', 'error', 'partial') DEFAULT 'running',
                        items_processed INT DEFAULT 0,
                        items_created INT DEFAULT 0,
                        items_updated INT DEFAULT 0,
                        items_errors INT DEFAULT 0,
                        error_message TEXT NULL,
                        sync_duration_seconds INT NULL,
                        INDEX idx_user_type (user_id, sync_type),
                        INDEX idx_started_at (started_at),
                        INDEX idx_status (status)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                # Tabela de controle de produtos modificados
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS product_changes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        product_id VARCHAR(50) NOT NULL,
                        change_type ENUM('created', 'updated', 'deleted', 'status_changed') NOT NULL,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        old_data JSON NULL,
                        new_data JSON NULL,
                        synced_at TIMESTAMP NULL,
                        INDEX idx_user_product (user_id, product_id),
                        INDEX idx_changed_at (changed_at),
                        INDEX idx_synced (synced_at)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                
                conn.commit()
                logger.info("✅ Tabelas de sincronização criadas com sucesso")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas de sincronização: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def inicializar_sync_usuario(self, user_id: int):
        """Inicializa configuração de sincronização para um usuário"""
        conn = self.db.conectar()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                # Inserir configurações padrão para cada tipo de sync
                sync_types = ['vendas', 'produtos', 'webhooks']
                
                for sync_type in sync_types:
                    cursor.execute("""
                        INSERT IGNORE INTO sync_control 
                        (user_id, sync_type, last_sync_at, last_successful_sync, sync_frequency_minutes)
                        VALUES (%s, %s, NULL, NULL, %s)
                    """, (user_id, sync_type, 15 if sync_type == 'vendas' else 30))
                
                conn.commit()
                logger.info(f"✅ Sincronização inicializada para user_id: {user_id}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar sync para user_id {user_id}: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_ultima_sincronizacao(self, user_id: int, sync_type: str) -> Optional[datetime]:
        """Obtém timestamp da última sincronização bem-sucedida"""
        conn = self.db.conectar()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT last_successful_sync FROM sync_control 
                    WHERE user_id = %s AND sync_type = %s AND is_active = TRUE
                """, (user_id, sync_type))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter última sincronização: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()
    
    def atualizar_ultima_sincronizacao(self, user_id: int, sync_type: str, 
                                     status: str = 'success', error_message: str = None):
        """Atualiza timestamp da última sincronização"""
        conn = self.db.conectar()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                now = datetime.now()
                
                if status == 'success':
                    cursor.execute("""
                        UPDATE sync_control 
                        SET last_sync_at = %s, last_successful_sync = %s, 
                            last_sync_status = 'success', last_error_message = NULL,
                            updated_at = %s
                        WHERE user_id = %s AND sync_type = %s
                    """, (now, now, now, user_id, sync_type))
                else:
                    cursor.execute("""
                        UPDATE sync_control 
                        SET last_sync_at = %s, last_sync_status = %s, 
                            last_error_message = %s, updated_at = %s
                        WHERE user_id = %s AND sync_type = %s
                    """, (now, status, error_message, now, user_id, sync_type))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar sincronização: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def sincronizar_vendas_incremental(self, user_id: int) -> Dict[str, Any]:
        """Sincroniza apenas vendas modificadas desde a última sincronização"""
        logger.info(f"🔄 Iniciando sincronização incremental de vendas para user_id: {user_id}")
        
        # Registrar início da sincronização
        sync_id = self._registrar_inicio_sync(user_id, 'vendas')
        
        try:
            # Obter última sincronização
            ultima_sync = self.obter_ultima_sincronizacao(user_id, 'vendas')
            
            if not ultima_sync:
                logger.info("📅 Primeira sincronização - buscando vendas dos últimos 7 dias")
                data_inicio = datetime.now() - timedelta(days=7)
            else:
                logger.info(f"📅 Sincronizando desde: {ultima_sync}")
                data_inicio = ultima_sync
            
            # Obter token de acesso
            access_token = self.db.obter_access_token(user_id)
            if not access_token:
                raise Exception("Token de acesso não encontrado")
            
            # Buscar vendas modificadas no período
            vendas_modificadas = self._buscar_vendas_periodo(user_id, access_token, data_inicio)
            
            if not vendas_modificadas:
                logger.info("✅ Nenhuma venda modificada encontrada")
                self._registrar_fim_sync(sync_id, 'success', 0, 0, 0, 0)
                self.atualizar_ultima_sincronizacao(user_id, 'vendas', 'success')
                return {'success': True, 'message': 'Nenhuma mudança encontrada', 'items': 0}
            
            # Processar vendas modificadas
            stats = self._processar_vendas_modificadas(user_id, vendas_modificadas)
            
            # Registrar sucesso
            self._registrar_fim_sync(sync_id, 'success', 
                                   stats['total'], stats['created'], 
                                   stats['updated'], stats['errors'])
            self.atualizar_ultima_sincronizacao(user_id, 'vendas', 'success')
            
            logger.info(f"✅ Sincronização concluída: {stats['total']} vendas processadas")
            return {
                'success': True,
                'message': f'Sincronização concluída',
                'items': stats['total'],
                'created': stats['created'],
                'updated': stats['updated'],
                'errors': stats['errors']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização incremental: {e}")
            self._registrar_fim_sync(sync_id, 'error', 0, 0, 0, 0, str(e))
            self.atualizar_ultima_sincronizacao(user_id, 'vendas', 'error', str(e))
            return {'success': False, 'message': str(e)}
    
    def sincronizar_produtos_incremental(self, user_id: int) -> Dict[str, Any]:
        """Sincroniza apenas produtos modificados desde a última sincronização"""
        logger.info(f"🔄 Iniciando sincronização incremental de produtos para user_id: {user_id}")
        
        # Registrar início da sincronização
        sync_id = self._registrar_inicio_sync(user_id, 'produtos')
        
        try:
            # Obter última sincronização
            ultima_sync = self.obter_ultima_sincronizacao(user_id, 'produtos')
            
            if not ultima_sync:
                logger.info("📅 Primeira sincronização - buscando produtos dos últimos 30 dias")
                data_inicio = datetime.now() - timedelta(days=30)
            else:
                logger.info(f"📅 Sincronizando produtos desde: {ultima_sync}")
                data_inicio = ultima_sync
            
            # Obter token de acesso
            access_token = self.db.obter_access_token(user_id)
            if not access_token:
                raise Exception("Token de acesso não encontrado")
            
            # Buscar produtos modificados no período
            produtos_modificados = self._buscar_produtos_periodo(user_id, access_token, data_inicio)
            
            if not produtos_modificados:
                logger.info("✅ Nenhum produto modificado encontrado")
                self._registrar_fim_sync(sync_id, 'success', 0, 0, 0, 0)
                self.atualizar_ultima_sincronizacao(user_id, 'produtos', 'success')
                return {'success': True, 'message': 'Nenhuma mudança encontrada', 'items': 0}
            
            # Processar produtos modificados
            stats = self._processar_produtos_modificados(user_id, produtos_modificados)
            
            # Registrar sucesso
            self._registrar_fim_sync(sync_id, 'success', 
                                   stats['total'], stats['created'], 
                                   stats['updated'], stats['errors'])
            self.atualizar_ultima_sincronizacao(user_id, 'produtos', 'success')
            
            logger.info(f"✅ Sincronização de produtos concluída: {stats['total']} produtos processados")
            return {
                'success': True,
                'message': f'Sincronização de produtos concluída',
                'items': stats['total'],
                'created': stats['created'],
                'updated': stats['updated'],
                'errors': stats['errors']
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na sincronização incremental de produtos: {e}")
            self._registrar_fim_sync(sync_id, 'error', 0, 0, 0, 0, str(e))
            self.atualizar_ultima_sincronizacao(user_id, 'produtos', 'error', str(e))
            return {'success': False, 'message': str(e)}
    
    def _buscar_vendas_periodo(self, user_id: int, access_token: str, 
                              data_inicio: datetime) -> List[Dict[str, Any]]:
        """Busca vendas modificadas em um período específico"""
        try:
            # Converter data para formato da API
            data_str = data_inicio.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Buscar vendas usando a API do Mercado Livre
            url = f"https://api.mercadolibre.com/orders/search"
            params = {
                'seller': user_id,
                'order.date_created.from': data_str,
                'limit': 50,
                'access_token': access_token
            }
            
            import requests
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            vendas = data.get('results', [])
            
            # Buscar detalhes de cada venda
            vendas_detalhadas = []
            for venda_id in vendas:
                try:
                    venda_data = self.api.obter_detalhes_order(venda_id, access_token)
                    if venda_data:
                        vendas_detalhadas.append(venda_data)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao obter detalhes da venda {venda_id}: {e}")
            
            return vendas_detalhadas
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar vendas do período: {e}")
            return []
    
    def _buscar_produtos_periodo(self, user_id: int, access_token: str, 
                                data_inicio: datetime) -> List[Dict[str, Any]]:
        """Busca produtos modificados em um período específico"""
        try:
            # Converter data para formato da API
            data_str = data_inicio.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Buscar produtos usando a API do Mercado Livre
            url = f"https://api.mercadolibre.com/users/{user_id}/items/search"
            params = {
                'offset': 0,
                'limit': 50,
                'access_token': access_token
            }
            
            import requests
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            produtos_ids = data.get('results', [])
            
            # Buscar detalhes de cada produto
            produtos_detalhados = []
            for produto_id in produtos_ids:
                try:
                    produto_data = self.api.obter_detalhes_produto(produto_id, user_id)
                    if produto_data:
                        produtos_detalhados.append(produto_data)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao obter detalhes do produto {produto_id}: {e}")
            
            return produtos_detalhados
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar produtos do período: {e}")
            return []
    
    def _processar_vendas_modificadas(self, user_id: int, vendas: List[Dict[str, Any]]) -> Dict[str, int]:
        """Processa vendas modificadas e atualiza banco de dados"""
        stats = {'total': 0, 'created': 0, 'updated': 0, 'errors': 0}
        
        for venda in vendas:
            try:
                stats['total'] += 1
                
                # Verificar se venda já existe
                venda_existe = self.db.verificar_venda_existe(user_id, venda.get('id'))
                
                if venda_existe:
                    # Atualizar venda existente
                    if self.db.salvar_venda_completa(venda, user_id):
                        stats['updated'] += 1
                    else:
                        stats['errors'] += 1
                else:
                    # Criar nova venda
                    if self.db.salvar_venda_completa(venda, user_id):
                        stats['created'] += 1
                    else:
                        stats['errors'] += 1
                        
            except Exception as e:
                logger.error(f"❌ Erro ao processar venda {venda.get('id')}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def _processar_produtos_modificados(self, user_id: int, produtos: List[Dict[str, Any]]) -> Dict[str, int]:
        """Processa produtos modificados e atualiza banco de dados"""
        stats = {'total': 0, 'created': 0, 'updated': 0, 'errors': 0}
        
        for produto in produtos:
            try:
                stats['total'] += 1
                
                # Verificar se produto já existe
                produto_existe = self.db.verificar_produto_existe(produto.get('id'), user_id)
                
                if produto_existe:
                    # Atualizar produto existente
                    if self.db.salvar_produto_completo(produto, user_id):
                        stats['updated'] += 1
                    else:
                        stats['errors'] += 1
                else:
                    # Criar novo produto
                    if self.db.salvar_produto_completo(produto, user_id):
                        stats['created'] += 1
                    else:
                        stats['errors'] += 1
                        
            except Exception as e:
                logger.error(f"❌ Erro ao processar produto {produto.get('id')}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def _registrar_inicio_sync(self, user_id: int, sync_type: str) -> int:
        """Registra início de uma sincronização"""
        conn = self.db.conectar()
        if not conn:
            return 0
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO sync_history 
                    (user_id, sync_type, started_at, status)
                    VALUES (%s, %s, NOW(), 'running')
                """, (user_id, sync_type))
                
                conn.commit()
                return cursor.lastrowid
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar início de sync: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()
    
    def _registrar_fim_sync(self, sync_id: int, status: str, items_processed: int,
                           items_created: int, items_updated: int, items_errors: int,
                           error_message: str = None):
        """Registra fim de uma sincronização"""
        conn = self.db.conectar()
        if not conn:
            return
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE sync_history 
                    SET completed_at = NOW(), status = %s, items_processed = %s,
                        items_created = %s, items_updated = %s, items_errors = %s,
                        error_message = %s,
                        sync_duration_seconds = TIMESTAMPDIFF(SECOND, started_at, NOW())
                    WHERE id = %s
                """, (status, items_processed, items_created, items_updated, 
                     items_errors, error_message, sync_id))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ Erro ao registrar fim de sync: {e}")
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_status_sincronizacao(self, user_id: int) -> Dict[str, Any]:
        """Obtém status atual da sincronização para um usuário"""
        conn = self.db.conectar()
        if not conn:
            return {}
            
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT sync_type, last_sync_at, last_successful_sync, 
                           last_sync_status, last_error_message, sync_frequency_minutes,
                           is_active
                    FROM sync_control 
                    WHERE user_id = %s
                    ORDER BY sync_type
                """, (user_id,))
                
                sync_status = {}
                for row in cursor.fetchall():
                    sync_status[row['sync_type']] = {
                        'last_sync': row['last_sync_at'],
                        'last_successful': row['last_successful_sync'],
                        'status': row['last_sync_status'],
                        'error': row['last_error_message'],
                        'frequency_minutes': row['sync_frequency_minutes'],
                        'active': row['is_active']
                    }
                
                return sync_status
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter status de sincronização: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()
    
    def iniciar_sincronizacao_automatica(self):
        """Inicia thread de sincronização automática"""
        if self.running:
            logger.warning("⚠️ Sincronização automática já está rodando")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._loop_sincronizacao, daemon=True)
        self.sync_thread.start()
        logger.info("🚀 Sincronização automática iniciada")
    
    def parar_sincronizacao_automatica(self):
        """Para thread de sincronização automática"""
        self.running = False
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        logger.info("🛑 Sincronização automática parada")
    
    def _loop_sincronizacao(self):
        """Loop principal da sincronização automática"""
        logger.info("🔄 Loop de sincronização automática iniciado")
        
        while self.running:
            try:
                # Obter usuários ativos
                usuarios_ativos = self._obter_usuarios_ativos()
                
                # Processar usuários em paralelo
                self._processar_usuarios_paralelo(usuarios_ativos)
                
                # Aguardar antes da próxima verificação
                time.sleep(60)  # Verificar a cada minuto
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de sincronização: {e}")
                time.sleep(60)
        
        logger.info("🛑 Loop de sincronização automática finalizado")
    
    def _processar_usuarios_paralelo(self, usuarios_ativos):
        """Processa usuários em paralelo para sincronização"""
        if not usuarios_ativos:
            return
        
        # Criar threads para cada usuário
        threads = []
        for user_id in usuarios_ativos:
            if not self.running:
                break
            
            thread = threading.Thread(
                target=self._sincronizar_usuario_individual,
                args=(user_id,),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        # Aguardar todas as threads terminarem (com timeout)
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=300)  # 5 minutos timeout por usuário
    
    def _sincronizar_usuario_individual(self, user_id):
        """Sincroniza um usuário individual em thread separada"""
        try:
            # Verificar se precisa sincronizar vendas
            if self._precisa_sincronizar(user_id, 'vendas'):
                logger.info(f"🔄 Sincronizando vendas para user_id: {user_id}")
                self.sincronizar_vendas_incremental(user_id)
            
            # Verificar se precisa sincronizar produtos
            if self._precisa_sincronizar(user_id, 'produtos'):
                logger.info(f"🔄 Sincronizando produtos para user_id: {user_id}")
                self.sincronizar_produtos_incremental(user_id)
                
        except Exception as e:
            logger.error(f"❌ Erro na sincronização para user_id {user_id}: {e}")
    
    def _obter_usuarios_ativos(self) -> List[int]:
        """Obtém lista de usuários com sincronização ativa"""
        conn = self.db.conectar()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT user_id FROM sync_control 
                    WHERE is_active = TRUE
                """)
                
                return [row[0] for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter usuários ativos: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def _precisa_sincronizar(self, user_id: int, sync_type: str) -> bool:
        """Verifica se precisa sincronizar baseado na frequência configurada"""
        conn = self.db.conectar()
        if not conn:
            return False
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT last_sync_at, sync_frequency_minutes, is_active
                    FROM sync_control 
                    WHERE user_id = %s AND sync_type = %s
                """, (user_id, sync_type))
                
                result = cursor.fetchone()
                if not result or not result[2]:  # is_active
                    return False
                
                last_sync, frequency = result[0], result[1]
                
                if not last_sync:
                    return True  # Primeira sincronização
                
                # Verificar se passou o tempo da frequência
                next_sync = last_sync + timedelta(minutes=frequency)
                return datetime.now() >= next_sync
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar necessidade de sincronização: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

# Instância global do SyncManager
sync_manager = None

def inicializar_sync_manager():
    """Inicializa o gerenciador de sincronização global"""
    global sync_manager
    if not sync_manager:
        db = DatabaseManager()
        sync_manager = SyncManager(db)
        sync_manager.criar_tabelas_sync()
    return sync_manager

def obter_sync_manager() -> SyncManager:
    """Obtém instância do gerenciador de sincronização"""
    global sync_manager
    if not sync_manager:
        return inicializar_sync_manager()
    return sync_manager
