#!/usr/bin/env python3
"""
Sistema de Status de Envio Detalhado do Mercado Livre
Mapeia todos os status possíveis de envio e entrega
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum

class ShippingStatus(Enum):
    """Status de envio do Mercado Livre"""
    
    # Status iniciais
    PENDING = "pending"                    # Pendente
    CONFIRMED = "confirmed"                # Confirmado
    READY_TO_SHIP = "ready_to_ship"       # Pronto para envio
    
    # Status de envio
    SHIPPED = "shipped"                    # Enviado
    IN_TRANSIT = "in_transit"              # Em trânsito
    OUT_FOR_DELIVERY = "out_for_delivery"  # Saiu para entrega
    
    # Status de entrega
    DELIVERED = "delivered"                # Entregue
    DELIVERED_TO_RECEIVER = "delivered_to_receiver"  # Entregue ao destinatário
    
    # Status de problemas
    LOST = "lost"                          # Extraviado
    RETURNED = "returned"                  # Devolvido
    RETURNED_TO_SENDER = "returned_to_sender"  # Devolvido ao remetente
    DAMAGED = "damaged"                    # Danificado
    
    # Status de cancelamento
    CANCELLED = "cancelled"                # Cancelado
    CANCELLED_BY_BUYER = "cancelled_by_buyer"  # Cancelado pelo comprador
    CANCELLED_BY_SELLER = "cancelled_by_seller"  # Cancelado pelo vendedor
    
    # Status especiais
    SCHEDULED = "scheduled"                # Agendado para envio
    PICKUP_AVAILABLE = "pickup_available"  # Disponível para retirada
    PICKED_UP = "picked_up"                # Retirado
    EXCEPTION = "exception"                # Exceção
    UNKNOWN = "unknown"                    # Desconhecido

class ShippingStatusMapper:
    """Mapeador de status de envio do Mercado Livre"""
    
    def __init__(self):
        self.status_mapping = self._create_status_mapping()
        self.status_descriptions = self._create_status_descriptions()
        self.status_categories = self._create_status_categories()
    
    def _create_status_mapping(self) -> Dict[str, str]:
        """Cria mapeamento de status do ML para status padronizados"""
        return {
            # Status do ML para status padronizados
            'pending': 'pending',
            'confirmed': 'confirmed', 
            'ready_to_ship': 'ready_to_ship',
            'shipped': 'shipped',
            'in_transit': 'in_transit',
            'out_for_delivery': 'out_for_delivery',
            'delivered': 'delivered',
            'delivered_to_receiver': 'delivered',
            'lost': 'lost',
            'returned': 'returned',
            'returned_to_sender': 'returned',
            'damaged': 'damaged',
            'cancelled': 'cancelled',
            'cancelled_by_buyer': 'cancelled',
            'cancelled_by_seller': 'cancelled',
            'scheduled': 'scheduled',
            'pickup_available': 'pickup_available',
            'picked_up': 'picked_up',
            'exception': 'exception',
            
            # Status antigos/compatibilidade
            'paid': 'ready_to_ship',
            'fulfilled': 'shipped',
            'not_delivered': 'exception',
            'delivery_failed': 'exception',
            'in_warehouse': 'ready_to_ship',
            'processing': 'confirmed',
            'preparing': 'confirmed',
        }
    
    def _create_status_descriptions(self) -> Dict[str, str]:
        """Cria descrições em português para cada status"""
        return {
            'pending': 'Pendente',
            'confirmed': 'Confirmado',
            'ready_to_ship': 'Pronto para Envio',
            'shipped': 'Enviado',
            'in_transit': 'Em Trânsito',
            'out_for_delivery': 'Saiu para Entrega',
            'delivered': 'Entregue',
            'lost': 'Extraviado',
            'returned': 'Devolvido',
            'damaged': 'Danificado',
            'cancelled': 'Cancelado',
            'scheduled': 'Agendado',
            'pickup_available': 'Disponível para Retirada',
            'picked_up': 'Retirado',
            'exception': 'Exceção',
            'unknown': 'Desconhecido'
        }
    
    def _create_status_categories(self) -> Dict[str, str]:
        """Cria categorias para agrupamento de status"""
        return {
            'pending': 'Inicial',
            'confirmed': 'Inicial',
            'ready_to_ship': 'Preparação',
            'shipped': 'Envio',
            'in_transit': 'Envio',
            'out_for_delivery': 'Envio',
            'delivered': 'Entregue',
            'lost': 'Problema',
            'returned': 'Problema',
            'damaged': 'Problema',
            'cancelled': 'Cancelado',
            'scheduled': 'Agendado',
            'pickup_available': 'Retirada',
            'picked_up': 'Retirada',
            'exception': 'Problema',
            'unknown': 'Indefinido'
        }
    
    def map_shipping_status(self, ml_status: str, status_detail: str = None, fulfilled: bool = None) -> Tuple[str, str, str]:
        """
        Mapeia status do Mercado Livre para status padronizado
        
        Args:
            ml_status: Status principal da venda
            status_detail: Detalhe do status (opcional)
            fulfilled: Se a venda foi cumprida (opcional)
            
        Returns:
            Tuple[str, str, str]: (status_padronizado, descricao, categoria)
        """
        # Normalizar status
        ml_status = ml_status.lower() if ml_status else 'unknown'
        status_detail = status_detail.lower() if status_detail else ''
        
        # Lógica especial para status complexos
        if ml_status == 'paid' and fulfilled:
            mapped_status = 'shipped'
        elif ml_status == 'paid' and not fulfilled:
            mapped_status = 'ready_to_ship'
        elif ml_status == 'confirmed' and 'shipped' in status_detail:
            mapped_status = 'shipped'
        elif ml_status == 'confirmed' and 'ready' in status_detail:
            mapped_status = 'ready_to_ship'
        elif 'lost' in status_detail or 'extraviado' in status_detail:
            mapped_status = 'lost'
        elif 'returned' in status_detail or 'devolvido' in status_detail:
            mapped_status = 'returned'
        elif 'damaged' in status_detail or 'danificado' in status_detail:
            mapped_status = 'damaged'
        elif 'cancelled' in status_detail or 'cancelado' in status_detail:
            mapped_status = 'cancelled'
        elif 'scheduled' in status_detail or 'agendado' in status_detail:
            mapped_status = 'scheduled'
        elif 'pickup' in status_detail or 'retirada' in status_detail:
            mapped_status = 'pickup_available'
        elif 'exception' in status_detail or 'exceção' in status_detail:
            mapped_status = 'exception'
        else:
            # Usar mapeamento padrão
            mapped_status = self.status_mapping.get(ml_status, 'unknown')
        
        # Obter descrição e categoria
        description = self.status_descriptions.get(mapped_status, 'Status desconhecido')
        category = self.status_categories.get(mapped_status, 'indefinido')
        
        return mapped_status, description, category
    
    def get_all_statuses(self) -> List[Dict[str, str]]:
        """Retorna lista de todos os status disponíveis"""
        statuses = []
        for status in ShippingStatus:
            status_value = status.value
            statuses.append({
                'value': status_value,
                'description': self.status_descriptions.get(status_value, ''),
                'category': self.status_categories.get(status_value, 'indefinido')
            })
        return statuses
    
    def get_statuses_by_category(self, category: str) -> List[Dict[str, str]]:
        """Retorna status filtrados por categoria"""
        return [
            status for status in self.get_all_statuses()
            if status['category'] == category
        ]
    
    def get_status_info(self, status: str) -> Dict[str, str]:
        """Retorna informações completas de um status"""
        return {
            'value': status,
            'description': self.status_descriptions.get(status, 'Status desconhecido'),
            'category': self.status_categories.get(status, 'indefinido')
        }

# Instância global do mapeador
shipping_mapper = ShippingStatusMapper()

def map_ml_shipping_status(ml_status: str, status_detail: str = None, fulfilled: bool = None) -> Tuple[str, str, str]:
    """Função helper para mapear status de envio"""
    return shipping_mapper.map_shipping_status(ml_status, status_detail, fulfilled)

def get_shipping_status_info(status: str) -> Dict[str, str]:
    """Função helper para obter informações de status"""
    return shipping_mapper.get_status_info(status)

def get_all_shipping_statuses() -> List[Dict[str, str]]:
    """Função helper para obter todos os status"""
    return shipping_mapper.get_all_statuses()

def get_shipping_statuses_by_category(category: str) -> List[Dict[str, str]]:
    """Função helper para obter status por categoria"""
    return shipping_mapper.get_statuses_by_category(category)

if __name__ == "__main__":
    # Teste do sistema de status
    print("🧪 Testando Sistema de Status de Envio")
    print("=" * 50)
    
    # Teste de mapeamento
    test_cases = [
        ("paid", None, True),
        ("paid", None, False),
        ("confirmed", "shipped", None),
        ("confirmed", "ready", None),
        ("delivered", None, None),
        ("lost", "extraviado", None),
        ("returned", "devolvido", None),
        ("cancelled", "cancelado", None),
    ]
    
    for ml_status, detail, fulfilled in test_cases:
        mapped, description, category = map_ml_shipping_status(ml_status, detail, fulfilled)
        print(f"ML: {ml_status} | Detail: {detail} | Fulfilled: {fulfilled}")
        print(f"  → Mapped: {mapped} | {description} | {category}")
        print()
    
    # Teste de categorias
    print("📊 Status por Categoria:")
    categories = ['inicial', 'preparacao', 'envio', 'entregue', 'problema', 'cancelado']
    for category in categories:
        statuses = get_shipping_statuses_by_category(category)
        print(f"\n{category.upper()}:")
        for status in statuses:
            print(f"  - {status['value']}: {status['description']}")
