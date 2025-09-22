#!/usr/bin/env python3
"""
Script para debugar problemas na importação de vendas
"""

from meli_api import MercadoLivreAPI
from database import DatabaseManager

def test_vendas_api():
    """Testa a API de vendas"""
    print("🧪 Testando API de vendas...")
    
    try:
        api = MercadoLivreAPI()
        db = DatabaseManager()
        
        # Testar obter_vendas_simples
        print("📦 Testando obter_vendas_simples...")
        vendas = api.obter_vendas_simples(1305538297, 5)
        
        if vendas:
            print(f"✅ Encontradas {len(vendas)} vendas")
            print("📋 Primeira venda:")
            venda = vendas[0]
            print(f"   - ID: {venda.get('id', 'N/A')}")
            print(f"   - Status: {venda.get('status', 'N/A')}")
            print(f"   - Total: {venda.get('total_amount', 'N/A')}")
            print(f"   - Comprador: {venda.get('buyer', {}).get('nickname', 'N/A')}")
            
            # Testar salvar_venda_completa
            print("\n💾 Testando salvar_venda_completa...")
            success = db.salvar_venda_completa(venda, 1305538297)
            if success:
                print("✅ Venda salva com sucesso!")
                
                # Verificar se foi salva no banco
                print("\n🔍 Verificando se foi salva no banco...")
                vendas_salvas = db.obter_vendas_usuario_novo(1305538297)
                if vendas_salvas:
                    print(f"✅ Encontradas {len(vendas_salvas)} vendas no banco")
                    venda_salva = vendas_salvas[0]
                    print(f"   - Pack ID: {venda_salva.get('pack_id', 'N/A')}")
                    print(f"   - Data: {venda_salva.get('data_aprovacao', 'N/A')}")
                    print(f"   - Valor: R$ {venda_salva.get('valor_total', 0):.2f}")
                else:
                    print("❌ Nenhuma venda encontrada no banco")
            else:
                print("❌ Erro ao salvar venda")
        else:
            print("❌ Nenhuma venda encontrada")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def test_webhook_with_valid_user():
    """Testa webhook com usuário válido"""
    print("\n🔔 Testando webhook com usuário válido...")
    
    import requests
    from datetime import datetime
    
    webhook_data = {
        "id": f"test_webhook_{int(datetime.now().timestamp())}",
        "resource": "/orders/2195160686",
        "user_id": 1305538297,  # Usuário válido
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
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📝 Resposta: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Erro ao processar webhook")
            
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")

if __name__ == "__main__":
    print("🔧 Debug de Importação de Vendas")
    print("=" * 50)
    
    test_vendas_api()
    test_webhook_with_valid_user()
    
    print("\n🎯 Debug concluído!")
