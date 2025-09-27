"""
Sistema Universal de Processamento de Webhooks do Mercado Livre
Processa todos os tópicos disponíveis do ML de forma inteligente
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TopicCategory(Enum):
    """Categorias de tópicos do Mercado Livre"""
    ORDERS = "orders"
    MESSAGES = "messages"
    ITEMS = "items"
    PRICES = "prices"
    QUESTIONS = "questions"
    QUOTATIONS = "quotations"
    CATALOG = "catalog"
    SHIPMENTS = "shipments"
    PROMOTIONS = "promotions"
    VIS_LEADS = "vis_leads"
    POST_PURCHASE = "post_purchase"
    OTHERS = "others"

@dataclass
class WebhookNotification:
    """Estrutura padronizada para notificações de webhook"""
    notification_id: str
    resource: str
    user_id: int
    topic: str
    application_id: int
    attempts: int
    sent: datetime
    received: datetime
    actions: Optional[List[str]] = None
    raw_data: Optional[Dict[str, Any]] = None

class WebhookProcessor:
    """Processador universal de webhooks do Mercado Livre"""
    
    def __init__(self, meli_api, db_manager):
        self.meli_api = meli_api
        self.db_manager = db_manager
        self.webhook_logger = WebhookLogger(db_manager)
        self.topic_processors = self._initialize_topic_processors()
        
    def _initialize_topic_processors(self) -> Dict[str, callable]:
        """Inicializa os processadores específicos para cada tópico"""
        return {
            # Orders
            'orders_v2': self._process_orders_v2,
            'orders_feedback': self._process_orders_feedback,
            
            # Messages
            'messages': self._process_messages,
            
            # Items
            'items': self._process_items,
            
            # Prices
            'price_suggestion': self._process_price_suggestion,
            
            # Questions
            'questions': self._process_questions,
            
            # Quotations
            'quotations': self._process_quotations,
            
            # Catalog
            'catalog_item_competition_status': self._process_catalog_competition,
            'catalog_suggestions': self._process_catalog_suggestions,
            
            # Shipments
            'shipments': self._process_shipments,
            'fbm_stock_operations': self._process_fbm_stock_operations,
            'flex-handshakes': self._process_flex_handshakes,
            
            # Promotions
            'public_offers': self._process_public_offers,
            'public_candidates': self._process_public_candidates,
            
            # VIS Leads
            'vis_leads': self._process_vis_leads,
            'visit_request': self._process_visit_request,
            
            # Post Purchase
            'post_purchase': self._process_post_purchase,
            
            # Others
            'payments': self._process_payments,
            'invoices': self._process_invoices,
            'leads-credits': self._process_leads_credits,
            'stock-location': self._process_stock_location,
        }
    
    def process_notification(self, notification_data: Dict[str, Any]) -> bool:
        """
        Processa uma notificação de webhook de forma universal
        
        Args:
            notification_data: Dados da notificação recebida
            
        Returns:
            bool: True se processado com sucesso, False caso contrário
        """
        try:
            # Parse da notificação
            notification = self._parse_notification(notification_data)
            if not notification:
                logger.error("Falha ao fazer parse da notificação")
                return False
            
            # Log da notificação recebida
            logger.info(f"Processando notificação: {notification.topic} - {notification.resource}")
            
            # Verificar se temos processador para este tópico
            processor = self.topic_processors.get(notification.topic)
            if not processor:
                logger.warning(f"Nenhum processador encontrado para tópico: {notification.topic}")
                return self._process_unknown_topic(notification)
            
            # Processar a notificação
            success = processor(notification)
            
            # Log do resultado no banco de dados
            self.webhook_logger.log_webhook_received(notification, success)
            
            # Log do resultado
            if success:
                logger.info(f"Notificação processada com sucesso: {notification.topic}")
            else:
                logger.error(f"Falha ao processar notificação: {notification.topic}")
            
            return success
            
        except Exception as e:
            logger.error(f"Erro ao processar notificação: {e}")
            return False
    
    def _parse_notification(self, data: Dict[str, Any]) -> Optional[WebhookNotification]:
        """Faz parse da notificação para estrutura padronizada"""
        try:
            # Parse das datas com valores padrão
            sent_str = data.get('sent', '')
            received_str = data.get('received', '')
            
            # Se não houver data, usar data atual
            if sent_str:
                try:
                    sent = datetime.fromisoformat(sent_str.replace('Z', '+00:00'))
                except:
                    sent = datetime.now()
            else:
                sent = datetime.now()
                
            if received_str:
                try:
                    received = datetime.fromisoformat(received_str.replace('Z', '+00:00'))
                except:
                    received = datetime.now()
            else:
                received = datetime.now()
            
            return WebhookNotification(
                notification_id=data.get('_id', data.get('id', '')),
                resource=data.get('resource', ''),
                user_id=int(data.get('user_id', 0)),
                topic=data.get('topic', ''),
                application_id=int(data.get('application_id', 0)),
                attempts=int(data.get('attempts', 1)),
                sent=sent,
                received=received,
                actions=data.get('actions', []),
                raw_data=data
            )
        except Exception as e:
            logger.error(f"Erro ao fazer parse da notificação: {e}")
            return None
    
    def _process_unknown_topic(self, notification: WebhookNotification) -> bool:
        """Processa tópicos desconhecidos de forma genérica"""
        try:
            logger.info(f"Processando tópico desconhecido: {notification.topic}")
            
            # Salvar notificação genérica no banco
            self.db_manager.salvar_notificacao_generica(notification)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar tópico desconhecido: {e}")
            return False
    
    # ===== PROCESSADORES ESPECÍFICOS =====
    
    def _process_orders_v2(self, notification: WebhookNotification) -> bool:
        """Processa notificações de orders_v2 (vendas)"""
        try:
            # Verificar se usuário precisa reautenticar (mas não bloquear webhook)
            if self.meli_api.verificar_necessidade_reautenticacao(notification.user_id):
                logger.warning(f"Usuário {notification.user_id} precisa reautenticar - processando webhook mesmo assim")
                # Não retornar False aqui, continuar processamento
            
            # Extrair order_id do resource
            order_id = notification.resource.split('/')[-1]
            
            # Obter token do usuário (com renovação automática)
            user_token = self.db_manager.obter_access_token(notification.user_id)
            if not user_token:
                logger.error(f"Token não encontrado para usuário {notification.user_id}")
                return False
            
            # Obter detalhes completos da venda
            venda_data = self.meli_api.obter_detalhes_order(order_id, user_token)
            if not venda_data:
                logger.warning(f"Falha ao obter detalhes da venda {order_id} - pode ser venda inexistente ou token inválido")
                # Mesmo sem dados da venda, registrar o webhook como recebido
                return True
            
            # Salvar venda com status
            success = self.db_manager.salvar_venda_completa(venda_data, notification.user_id)
            
            if success:
                logger.info(f"Venda {order_id} processada com sucesso")
            else:
                logger.warning(f"Falha ao salvar venda {order_id} no banco de dados")
            
            return True  # Sempre retornar True para webhooks, mesmo com erros
            
        except Exception as e:
            logger.error(f"Erro ao processar orders_v2: {e}")
            return False
    
    def _process_orders_feedback(self, notification: WebhookNotification) -> bool:
        """Processa notificações de feedback de vendas"""
        try:
            logger.info(f"Processando feedback de venda: {notification.resource}")
            # Implementar lógica específica para feedback
            return True
        except Exception as e:
            logger.error(f"Erro ao processar orders_feedback: {e}")
            return False
    
    def _process_messages(self, notification: WebhookNotification) -> bool:
        """Processa notificações de mensagens"""
        try:
            logger.info(f"Processando mensagem: {notification.resource}")
            # Implementar lógica específica para mensagens
            return True
        except Exception as e:
            logger.error(f"Erro ao processar messages: {e}")
            return False
    
    def _process_items(self, notification: WebhookNotification) -> bool:
        """Processa notificações de itens/produtos"""
        try:
            logger.info(f"Processando item: {notification.resource}")
            # Implementar lógica específica para itens
            return True
        except Exception as e:
            logger.error(f"Erro ao processar items: {e}")
            return False
    
    def _process_price_suggestion(self, notification: WebhookNotification) -> bool:
        """Processa sugestões de preço"""
        try:
            logger.info(f"Processando sugestão de preço: {notification.resource}")
            # Implementar lógica específica para sugestões de preço
            return True
        except Exception as e:
            logger.error(f"Erro ao processar price_suggestion: {e}")
            return False
    
    def _process_questions(self, notification: WebhookNotification) -> bool:
        """Processa notificações de perguntas"""
        try:
            logger.info(f"Processando pergunta: {notification.resource}")
            # Implementar lógica específica para perguntas
            return True
        except Exception as e:
            logger.error(f"Erro ao processar questions: {e}")
            return False
    
    def _process_quotations(self, notification: WebhookNotification) -> bool:
        """Processa notificações de cotações"""
        try:
            logger.info(f"Processando cotação: {notification.resource}")
            # Implementar lógica específica para cotações
            return True
        except Exception as e:
            logger.error(f"Erro ao processar quotations: {e}")
            return False
    
    def _process_catalog_competition(self, notification: WebhookNotification) -> bool:
        """Processa notificações de competição de catálogo"""
        try:
            logger.info(f"Processando competição de catálogo: {notification.resource}")
            # Implementar lógica específica para competição
            return True
        except Exception as e:
            logger.error(f"Erro ao processar catalog_competition: {e}")
            return False
    
    def _process_catalog_suggestions(self, notification: WebhookNotification) -> bool:
        """Processa sugestões de catálogo"""
        try:
            logger.info(f"Processando sugestão de catálogo: {notification.resource}")
            # Implementar lógica específica para sugestões de catálogo
            return True
        except Exception as e:
            logger.error(f"Erro ao processar catalog_suggestions: {e}")
            return False
    
    def _process_shipments(self, notification: WebhookNotification) -> bool:
        """Processa notificações de envios"""
        try:
            logger.info(f"Processando envio: {notification.resource}")
            # Implementar lógica específica para envios
            return True
        except Exception as e:
            logger.error(f"Erro ao processar shipments: {e}")
            return False
    
    def _process_fbm_stock_operations(self, notification: WebhookNotification) -> bool:
        """Processa operações de estoque FBM"""
        try:
            logger.info(f"Processando operação FBM: {notification.resource}")
            # Implementar lógica específica para FBM
            return True
        except Exception as e:
            logger.error(f"Erro ao processar fbm_stock_operations: {e}")
            return False
    
    def _process_flex_handshakes(self, notification: WebhookNotification) -> bool:
        """Processa handshakes flex"""
        try:
            logger.info(f"Processando flex handshake: {notification.resource}")
            # Implementar lógica específica para flex handshakes
            return True
        except Exception as e:
            logger.error(f"Erro ao processar flex_handshakes: {e}")
            return False
    
    def _process_public_offers(self, notification: WebhookNotification) -> bool:
        """Processa ofertas públicas"""
        try:
            logger.info(f"Processando oferta pública: {notification.resource}")
            # Implementar lógica específica para ofertas públicas
            return True
        except Exception as e:
            logger.error(f"Erro ao processar public_offers: {e}")
            return False
    
    def _process_public_candidates(self, notification: WebhookNotification) -> bool:
        """Processa candidatos públicos"""
        try:
            logger.info(f"Processando candidato público: {notification.resource}")
            # Implementar lógica específica para candidatos
            return True
        except Exception as e:
            logger.error(f"Erro ao processar public_candidates: {e}")
            return False
    
    def _process_vis_leads(self, notification: WebhookNotification) -> bool:
        """Processa leads VIS"""
        try:
            logger.info(f"Processando lead VIS: {notification.resource}")
            # Implementar lógica específica para leads VIS
            return True
        except Exception as e:
            logger.error(f"Erro ao processar vis_leads: {e}")
            return False
    
    def _process_visit_request(self, notification: WebhookNotification) -> bool:
        """Processa solicitações de visita"""
        try:
            logger.info(f"Processando solicitação de visita: {notification.resource}")
            # Implementar lógica específica para visitas
            return True
        except Exception as e:
            logger.error(f"Erro ao processar visit_request: {e}")
            return False
    
    def _process_post_purchase(self, notification: WebhookNotification) -> bool:
        """Processa notificações pós-compra"""
        try:
            logger.info(f"Processando pós-compra: {notification.resource}")
            # Implementar lógica específica para pós-compra
            return True
        except Exception as e:
            logger.error(f"Erro ao processar post_purchase: {e}")
            return False
    
    def _process_payments(self, notification: WebhookNotification) -> bool:
        """Processa notificações de pagamentos"""
        try:
            logger.info(f"Processando pagamento: {notification.resource}")
            # Implementar lógica específica para pagamentos
            return True
        except Exception as e:
            logger.error(f"Erro ao processar payments: {e}")
            return False
    
    def _process_invoices(self, notification: WebhookNotification) -> bool:
        """Processa notificações de faturas"""
        try:
            logger.info(f"Processando fatura: {notification.resource}")
            # Implementar lógica específica para faturas
            return True
        except Exception as e:
            logger.error(f"Erro ao processar invoices: {e}")
            return False
    
    def _process_leads_credits(self, notification: WebhookNotification) -> bool:
        """Processa créditos de leads"""
        try:
            logger.info(f"Processando crédito de lead: {notification.resource}")
            # Implementar lógica específica para créditos
            return True
        except Exception as e:
            logger.error(f"Erro ao processar leads_credits: {e}")
            return False
    
    def _process_stock_location(self, notification: WebhookNotification) -> bool:
        """Processa notificações de localização de estoque"""
        try:
            logger.info(f"Processando localização de estoque: {notification.resource}")
            # Implementar lógica específica para estoque
            return True
        except Exception as e:
            logger.error(f"Erro ao processar stock_location: {e}")
            return False

class WebhookLogger:
    """Sistema de logging e monitoramento de webhooks"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
    
    def log_webhook_received(self, notification: WebhookNotification, success: bool):
        """Registra o recebimento e processamento de um webhook"""
        try:
            self.db_manager.registrar_log_webhook(
                notification_id=notification.notification_id,
                topic=notification.topic,
                resource=notification.resource,
                user_id=notification.user_id,
                success=success,
                attempts=notification.attempts,
                raw_data=notification.raw_data
            )
        except Exception as e:
            logger.error(f"Erro ao registrar log de webhook: {e}")
    
    def get_webhook_stats(self, user_id: int = None) -> Dict[str, Any]:
        """Obtém estatísticas de webhooks processados"""
        try:
            return self.db_manager.obter_estatisticas_webhooks(user_id)
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de webhooks: {e}")
            return {}
