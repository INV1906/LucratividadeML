#!/usr/bin/env python3
"""
Script para testar logging de webhook
"""

import requests
from datetime import datetime

def test_webhook_logging():
    """Testa se o webhook está registrando logs corretamente"""
    
    print("🔔 Testando webhook com logging...")
    
    # Usar uma venda real do banco
    webhook_data = {
        "id": f"test_webhook_log_{int(datetime.now().timestamp())}",
        "resource": "/orders/2000009346906540",  # Venda real do banco
        "user_id": 1305538297,  # Usuário válido do banco
        "topic": "orders_v2",
        "application_id": 1234567890123456,
        "attempts": 1,
        "sent": datetime.now().isoformat() + "Z",
        "received": datetime.now().isoformat() + "Z"
    }
    
    try:
        response = requests.post(
            "http://localhost:3001/webhook/mercadolivre",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Resposta: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
            
            # Verificar se foi salvo no banco
            from database import DatabaseManager
            db = DatabaseManager()
            logs = db.obter_logs_webhook(1305538297, "orders_v2", 5)
            print(f"📊 Logs encontrados: {len(logs)}")
            
            for log in logs:
                print(f"   - {log.get('topic')} - Sucesso: {log.get('success')} - {log.get('processed_at')}")
        else:
            print("❌ Erro ao processar webhook")
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")

if __name__ == "__main__":
    test_webhook_logging()
