#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuração de Webhooks do Mercado Livre
==========================================

Este arquivo contém as configurações e instruções para configurar
os webhooks do Mercado Livre no seu aplicativo.

URL do Webhook: https://seu-dominio.com/webhook/mercadolivre
"""

# Tópicos de notificação configurados
WEBHOOK_TOPICS = {
    'items': {
        'description': 'Mudanças em produtos (preço, estoque, status)',
        'enabled': True,
        'priority': 'high'
    },
    'orders_v2': {
        'description': 'Mudanças em pedidos (novos pedidos, status)',
        'enabled': True,
        'priority': 'high'
    },
    'price_suggestion': {
        'description': 'Sugestões de preço do Mercado Livre',
        'enabled': True,
        'priority': 'medium'
    },
    'questions': {
        'description': 'Perguntas de compradores',
        'enabled': True,
        'priority': 'low'
    }
}

# Configurações de processamento
WEBHOOK_SETTINGS = {
    'timeout': 500,  # ms - tempo máximo para responder (requisito do ML)
    'retry_attempts': 3,  # tentativas de reprocessamento
    'batch_size': 10,  # processar em lotes
    'log_level': 'INFO'  # DEBUG, INFO, WARNING, ERROR
}

# IPs permitidos do Mercado Livre (para validação de segurança)
ML_ALLOWED_IPS = [
    '54.88.218.97',
    '18.215.140.160', 
    '18.213.114.129',
    '18.206.34.84'
]

# Instruções de configuração
CONFIGURATION_INSTRUCTIONS = """
CONFIGURAÇÃO DE WEBHOOKS NO MERCADO LIVRE
==========================================

1. Acesse o Gerenciador de Aplicativos do Mercado Livre:
   https://developers.mercadolibre.com.br/

2. Selecione seu aplicativo e vá em "Configuração de notificações"

3. Configure a URL de callback:
   https://seu-dominio.com/webhook/mercadolivre

4. Selecione os tópicos de interesse:
   ✅ Items - para mudanças em produtos
   ✅ Orders v2 - para mudanças em pedidos  
   ✅ Price Suggestion - para sugestões de preço
   ✅ Questions - para perguntas de compradores

5. Salve as configurações

6. Teste o webhook usando o Postman:
   - Importe a coleção fornecida pelo Mercado Livre
   - Envie uma notificação de teste
   - Verifique se retorna status 200

IMPORTANTE:
- A URL deve ser HTTPS e acessível publicamente
- O endpoint deve responder em menos de 500ms
- Use ngrok para testes locais: ngrok http 3001
"""

def get_webhook_url(base_url: str) -> str:
    """Retorna a URL completa do webhook."""
    return f"{base_url}/webhook/mercadolivre"

def is_valid_topic(topic: str) -> bool:
    """Verifica se o tópico é válido e habilitado."""
    return topic in WEBHOOK_TOPICS and WEBHOOK_TOPICS[topic]['enabled']

def get_topic_priority(topic: str) -> str:
    """Retorna a prioridade do tópico."""
    return WEBHOOK_TOPICS.get(topic, {}).get('priority', 'low')

def should_process_immediately(topic: str) -> bool:
    """Determina se o tópico deve ser processado imediatamente."""
    return get_topic_priority(topic) == 'high'
