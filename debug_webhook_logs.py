#!/usr/bin/env python3
"""
Script para debugar logs de webhook
"""

from database import DatabaseManager

def check_webhook_logs():
    """Verifica se os logs de webhook estão sendo registrados"""
    
    print("🔍 Verificando sistema de logs de webhook...")
    
    try:
        db = DatabaseManager()
        conn = db.conectar()
        
        if not conn:
            print("❌ Erro ao conectar no banco")
            return
        
        with conn.cursor() as cursor:
            # Verificar se a tabela existe
            cursor.execute("SHOW TABLES LIKE 'webhook_logs'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("✅ Tabela webhook_logs existe")
                
                # Verificar estrutura
                cursor.execute("DESCRIBE webhook_logs")
                columns = cursor.fetchall()
                print("📋 Estrutura da tabela:")
                for col in columns:
                    print(f"   - {col[0]} ({col[1]})")
                
                # Verificar se há dados
                cursor.execute("SELECT COUNT(*) as total FROM webhook_logs")
                count = cursor.fetchone()
                print(f"\n📊 Total de registros: {count[0]}")
                
                if count[0] > 0:
                    # Mostrar alguns registros
                    cursor.execute("SELECT * FROM webhook_logs ORDER BY processed_at DESC LIMIT 5")
                    logs = cursor.fetchall()
                    print("\n📋 Últimos 5 logs:")
                    for log in logs:
                        print(f"   - ID: {log[0]}, Tópico: {log[2]}, Sucesso: {log[5]}, Data: {log[8]}")
                else:
                    print("⚠️ Nenhum log encontrado na tabela")
                    
                # Verificar se há logs para o usuário específico
                cursor.execute("SELECT COUNT(*) FROM webhook_logs WHERE user_id = 1305538297")
                user_logs = cursor.fetchone()
                print(f"\n👤 Logs para usuário 1305538297: {user_logs[0]}")
                
            else:
                print("❌ Tabela webhook_logs não existe")
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def test_webhook_logging():
    """Testa se o sistema de logging está funcionando"""
    
    print("\n🧪 Testando sistema de logging...")
    
    try:
        from webhook_processor import WebhookProcessor, WebhookLogger
        from meli_api import MercadoLivreAPI
        from database import DatabaseManager
        
        # Criar instâncias
        api = MercadoLivreAPI()
        db = DatabaseManager()
        processor = WebhookProcessor(api, db)
        logger = WebhookLogger(db)
        
        # Simular uma notificação
        from datetime import datetime
        notification_data = {
            "id": f"test_log_{int(datetime.now().timestamp())}",
            "resource": "/orders/2000009346906540",
            "user_id": 1305538297,
            "topic": "orders_v2",
            "application_id": 1234567890123456,
            "attempts": 1,
            "sent": datetime.now().isoformat() + "Z",
            "received": datetime.now().isoformat() + "Z"
        }
        
        print("📝 Testando registro de log...")
        
        # Testar logging manual
        from webhook_processor import WebhookNotification
        from datetime import datetime
        
        notification = WebhookNotification(
            notification_id=notification_data["id"],
            resource=notification_data["resource"],
            user_id=notification_data["user_id"],
            topic=notification_data["topic"],
            application_id=notification_data["application_id"],
            attempts=notification_data["attempts"],
            sent=datetime.fromisoformat(notification_data["sent"].replace('Z', '+00:00')),
            received=datetime.fromisoformat(notification_data["received"].replace('Z', '+00:00'))
        )
        
        # Registrar log de sucesso
        logger.log_webhook_received(notification, True)
        print("✅ Log de sucesso registrado")
        
        # Registrar log de erro
        logger.log_webhook_received(notification, False)
        print("✅ Log de erro registrado")
        
        # Verificar se foram salvos
        logs = db.obter_logs_webhook(1305538297, "orders_v2", 10)
        print(f"📊 Logs encontrados após teste: {len(logs)}")
        
        for log in logs[:3]:
            print(f"   - {log.get('topic')} - {log.get('success')} - {log.get('processed_at')}")
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Debug de Logs de Webhook")
    print("=" * 50)
    
    check_webhook_logs()
    test_webhook_logging()
    
    print("\n🎯 Debug concluído!")
