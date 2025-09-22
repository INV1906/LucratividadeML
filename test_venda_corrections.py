#!/usr/bin/env python3
"""
Script para testar correções nos dados de venda
"""

from meli_api import MercadoLivreAPI
from database import DatabaseManager

def test_venda_corrections():
    """Testa se as correções nos dados de venda funcionaram"""
    
    print("🧪 Testando correção dos dados de venda...")
    
    try:
        api = MercadoLivreAPI()
        db = DatabaseManager()
        
        # Obter uma venda da API
        vendas = api.obter_vendas_simples(1305538297, 1)
        
        if vendas:
            venda = vendas[0]
            print("📋 Testando salvamento com dados corrigidos...")
            
            # Salvar venda com dados corrigidos
            success = db.salvar_venda_completa(venda, 1305538297)
            
            if success:
                print("✅ Venda salva com sucesso!")
                
                # Verificar dados salvos
                vendas_salvas = db.obter_vendas_usuario_novo(1305538297)
                if vendas_salvas:
                    venda_salva = vendas_salvas[0]
                    print("\n📊 Dados salvos:")
                    print(f"   Pack ID: {venda_salva.get('pack_id')}")
                    print(f"   Comprador: {venda_salva.get('comprador_nome')}")
                    print(f"   Status Pagamento: {venda_salva.get('status_pagamento')}")
                    print(f"   Status Envio: {venda_salva.get('status_envio')}")
                    print(f"   Data Aprovação: {venda_salva.get('data_aprovacao')}")
                    print(f"   Valor Total: R$ {venda_salva.get('valor_total', 0):.2f}")
                    print(f"   Taxa ML: R$ {venda_salva.get('taxa_ml', 0):.2f}")
                    print(f"   Frete: R$ {venda_salva.get('frete_total', 0):.2f}")
                    print(f"   Payment Method: {venda_salva.get('payment_method')}")
                    print(f"   Shipping Method: {venda_salva.get('shipping_method')}")
            else:
                print("❌ Erro ao salvar venda")
        else:
            print("❌ Nenhuma venda encontrada")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_venda_corrections()
