#!/usr/bin/env python3
"""
Sistema de Tradução para Português
Traduz todos os textos em inglês para português
"""

from typing import Dict, Any

class PortugueseTranslator:
    """Tradutor para português"""
    
    def __init__(self):
        self.payment_status = self._create_payment_status_translations()
        self.shipping_methods = self._create_shipping_methods_translations()
        self.payment_methods = self._create_payment_methods_translations()
        self.order_status = self._create_order_status_translations()
        self.ui_texts = self._create_ui_texts_translations()
    
    def _create_payment_status_translations(self) -> Dict[str, str]:
        """Traduz status de pagamento"""
        return {
            'approved': 'Aprovado',
            'pending': 'Pendente',
            'in_process': 'Em Processamento',
            'rejected': 'Rejeitado',
            'cancelled': 'Cancelado',
            'refunded': 'Reembolsado',
            'charged_back': 'Estornado',
            'unknown': 'Desconhecido'
        }
    
    def _create_shipping_methods_translations(self) -> Dict[str, str]:
        """Traduz métodos de envio"""
        return {
            'mercadoenvios': 'Mercado Envios',
            'custom': 'Personalizado',
            'me2': 'Mercado Envios 2',
            'fulfillment': 'Fulfillment',
            'cross_docking': 'Cross Docking',
            'unknown': 'Desconhecido'
        }
    
    def _create_payment_methods_translations(self) -> Dict[str, str]:
        """Traduz métodos de pagamento"""
        return {
            'credit_card': 'Cartão de Crédito',
            'debit_card': 'Cartão de Débito',
            'bank_transfer': 'Transferência Bancária',
            'pix': 'PIX',
            'boleto': 'Boleto',
            'mercadopago': 'Mercado Pago',
            'account_money': 'Dinheiro na Conta',
            'unknown': 'Desconhecido'
        }
    
    def _create_order_status_translations(self) -> Dict[str, str]:
        """Traduz status de pedido"""
        return {
            'confirmed': 'Confirmado',
            'payment_required': 'Pagamento Necessário',
            'payment_in_process': 'Pagamento em Processo',
            'paid': 'Pago',
            'cancelled': 'Cancelado',
            'invalid': 'Inválido',
            'unknown': 'Desconhecido'
        }
    
    def _create_ui_texts_translations(self) -> Dict[str, str]:
        """Traduz textos da interface"""
        return {
            'total_sales': 'Total de Vendas',
            'total_products': 'Total de Produtos',
            'shipping_cost': 'Custo de Envio',
            'ml_fee': 'Taxa ML',
            'net_profit': 'Lucro Líquido',
            'profit_margin': 'Margem de Lucro',
            'buyer_name': 'Nome do Comprador',
            'buyer_email': 'Email do Comprador',
            'order_date': 'Data do Pedido',
            'approval_date': 'Data de Aprovação',
            'shipping_date': 'Data de Envio',
            'delivery_date': 'Data de Entrega',
            'tracking_code': 'Código de Rastreamento',
            'carrier': 'Transportadora',
            'delivery_address': 'Endereço de Entrega',
            'shipping_notes': 'Observações de Envio',
            'payment_status': 'Status de Pagamento',
            'shipping_status': 'Status de Envio',
            'order_status': 'Status do Pedido',
            'shipping_method': 'Método de Envio',
            'payment_method': 'Método de Pagamento',
            'product_title': 'Título do Produto',
            'product_quantity': 'Quantidade',
            'unit_price': 'Preço Unitário',
            'total_price': 'Preço Total',
            'category': 'Categoria',
            'notes': 'Observações',
            'last_update': 'Última Atualização'
        }
    
    def translate_payment_status(self, status: str) -> str:
        """Traduz status de pagamento"""
        return self.payment_status.get(status.lower(), status)
    
    def translate_shipping_method(self, method: str) -> str:
        """Traduz método de envio"""
        return self.shipping_methods.get(method.lower(), method)
    
    def translate_payment_method(self, method: str) -> str:
        """Traduz método de pagamento"""
        return self.payment_methods.get(method.lower(), method)
    
    def translate_order_status(self, status: str) -> str:
        """Traduz status de pedido"""
        return self.order_status.get(status.lower(), status)
    
    def translate_ui_text(self, text: str) -> str:
        """Traduz texto da interface"""
        return self.ui_texts.get(text.lower(), text)
    
    def translate_venda_data(self, venda_data: Dict[str, Any]) -> Dict[str, Any]:
        """Traduz dados completos de uma venda"""
        translated = venda_data.copy()
        
        # Traduzir status de pagamento
        if 'payments' in translated and translated['payments']:
            for payment in translated['payments']:
                if 'status' in payment:
                    payment['status_pt'] = self.translate_payment_status(payment['status'])
                if 'payment_method_id' in payment:
                    payment['payment_method_pt'] = self.translate_payment_method(payment['payment_method_id'])
        
        # Traduzir método de envio
        if 'shipping' in translated and translated['shipping']:
            shipping = translated['shipping']
            if 'id' in shipping:
                shipping['shipping_method_pt'] = self.translate_shipping_method(shipping['id'])
        
        # Traduzir status geral
        if 'status' in translated:
            translated['status_pt'] = self.translate_order_status(translated['status'])
        
        return translated

# Instância global do tradutor
translator = PortugueseTranslator()

def translate_payment_status(status: str) -> str:
    """Função helper para traduzir status de pagamento"""
    return translator.translate_payment_status(status)

def translate_shipping_method(method: str) -> str:
    """Função helper para traduzir método de envio"""
    return translator.translate_shipping_method(method)

def translate_payment_method(method: str) -> str:
    """Função helper para traduzir método de pagamento"""
    return translator.translate_payment_method(method)

def translate_order_status(status: str) -> str:
    """Função helper para traduzir status de pedido"""
    return translator.translate_order_status(status)

def translate_venda_data(venda_data: Dict[str, Any]) -> Dict[str, Any]:
    """Função helper para traduzir dados de venda"""
    return translator.translate_venda_data(venda_data)

if __name__ == "__main__":
    # Teste do sistema de tradução
    print("🧪 Testando Sistema de Tradução")
    print("=" * 40)
    
    # Teste de status de pagamento
    print("💳 Status de Pagamento:")
    payment_statuses = ['approved', 'pending', 'rejected', 'cancelled']
    for status in payment_statuses:
        translated = translate_payment_status(status)
        print(f"  {status} → {translated}")
    
    # Teste de métodos de envio
    print("\n📦 Métodos de Envio:")
    shipping_methods = ['mercadoenvios', 'custom', 'me2']
    for method in shipping_methods:
        translated = translate_shipping_method(method)
        print(f"  {method} → {translated}")
    
    # Teste de métodos de pagamento
    print("\n💳 Métodos de Pagamento:")
    payment_methods = ['credit_card', 'pix', 'boleto', 'mercadopago']
    for method in payment_methods:
        translated = translate_payment_method(method)
        print(f"  {method} → {translated}")
    
    print("\n✅ Sistema de tradução funcionando!")
