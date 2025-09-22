#!/usr/bin/env python3
"""
Script para testar o sistema universal de webhooks do Mercado Livre
"""

import json
import requests
from datetime import datetime
import time

# URL do webhook (ajuste conforme necessário)
WEBHOOK_URL = "http://localhost:3001/webhook/mercadolivre"

def test_webhook_notification(topic, resource, user_id=123456789):
    """Testa uma notificação de webhook"""
    
    # Dados de exemplo baseados na documentação do ML
    notification_data = {
        "id": f"test_{int(time.time())}",
        "resource": resource,
        "user_id": user_id,
        "topic": topic,
        "application_id": 1234567890123456,
        "attempts": 1,
        "sent": datetime.now().isoformat() + "Z",
        "received": datetime.now().isoformat() + "Z"
    }
    
    print(f"🧪 Testando webhook: {topic}")
    print(f"📋 Resource: {resource}")
    print(f"👤 User ID: {user_id}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=notification_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Erro ao processar webhook")
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
    
    print("-" * 50)

def test_all_topics():
    """Testa todos os tópicos suportados"""
    
    print("🚀 Iniciando testes do sistema universal de webhooks")
    print("=" * 60)
    
    # Lista de tópicos para testar
    test_cases = [
        # Orders
        ("orders_v2", "/orders/2195160686"),
        ("orders_feedback", "/orders/2195160686/feedback"),
        
        # Messages
        ("messages", "3f6da1e35ac84f70a24af7360d24c7bc"),
        
        # Items
        ("items", "/items/MLA686791111"),
        
        # Prices
        ("price_suggestion", "suggestions/items/MLA686791111/details"),
        
        # Questions
        ("questions", "/questions/5036111111"),
        
        # Quotations
        ("quotations", "/quotations/5013267"),
        
        # Catalog
        ("catalog_item_competition_status", "/items/MLA686791111/price_to_win"),
        ("catalog_suggestions", "/catalog_suggestions/MLA123456"),
        
        # Shipments
        ("shipments", "/shipments/407323124706"),
        ("fbm_stock_operations", "/stock/fulfillment/operations/9876"),
        ("flex-handshakes", "/flex/sites/MLA/shipments/407323124706/assignment/v1"),
        
        # Promotions
        ("public_offers", "/seller-promotions/offers/1234567"),
        ("public_candidates", "/seller-promotions/candidates/CANDIDATE-MLA1111111111-11111111"),
        
        # VIS Leads
        ("vis_leads", "/vis/leads/14b52fd8-85dc-11eb-8436-2753cb1f9665"),
        ("visit_request", "/api/vis_leads/93a14ee6-0356-4e20-b0c6-f4ad8f80bkikfff"),
        
        # Post Purchase
        ("post_purchase", "post-purchase/v1/claims/5108684499"),
        
        # Others
        ("payments", "/collections/3043111111"),
        ("invoices", "/users/123456789/invoices/INVOICE123"),
        ("leads-credits", "/vis/loan/66e93589-2d10-11ed-ae7f-0aa30fafa621"),
        ("stock-location", "/user-products/USER_PRODUCT123/stock"),
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for topic, resource in test_cases:
        test_webhook_notification(topic, resource)
        time.sleep(1)  # Pausa entre testes
    
    print("=" * 60)
    print(f"🏁 Testes concluídos: {success_count}/{total_count} sucessos")

def test_webhook_with_actions():
    """Testa webhooks com ações específicas"""
    
    print("🎯 Testando webhooks com ações específicas")
    print("=" * 60)
    
    # Teste com actions array
    notification_data = {
        "id": f"test_actions_{int(time.time())}",
        "resource": "/api/vis_leads/93a14ee6-0356-4e20-b0c6-f4ad8f80bfff",
        "user_id": 123456789,
        "topic": "vis_leads",
        "actions": ["whatsapp", "call", "question"],
        "application_id": 1234567890123456,
        "attempts": 1,
        "sent": datetime.now().isoformat() + "Z",
        "received": datetime.now().isoformat() + "Z"
    }
    
    print("🧪 Testando webhook com actions")
    print(f"📋 Actions: {notification_data['actions']}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=notification_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

def test_invalid_webhook():
    """Testa webhook inválido"""
    
    print("❌ Testando webhook inválido")
    print("=" * 60)
    
    # Dados inválidos (sem topic)
    invalid_data = {
        "id": f"test_invalid_{int(time.time())}",
        "resource": "/invalid/resource",
        "user_id": 123456789,
        "application_id": 1234567890123456
    }
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=invalid_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    print("🔧 Sistema de Teste de Webhooks do Mercado Livre")
    print("=" * 60)
    
    # Verificar se o servidor está rodando
    try:
        response = requests.get("http://localhost:3001", timeout=5)
        print("✅ Servidor está rodando")
    except:
        print("❌ Servidor não está rodando. Inicie o servidor primeiro.")
        exit(1)
    
    print()
    
    # Executar testes
    test_all_topics()
    print()
    test_webhook_with_actions()
    print()
    test_invalid_webhook()
    
    print()
    print("🎉 Todos os testes foram executados!")
    print("📊 Verifique o dashboard de webhooks para ver os resultados.")
