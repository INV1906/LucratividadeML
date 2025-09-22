#!/usr/bin/env python3
"""
Script para debugar dados de venda da API
"""

from meli_api import MercadoLivreAPI
from database import DatabaseManager

def debug_venda_data():
    """Verifica os dados que estão vindo da API"""
    
    print("🔍 Verificando dados da API do Mercado Livre...")
    
    try:
        api = MercadoLivreAPI()
        db = DatabaseManager()
        
        # Obter uma venda da API
        vendas = api.obter_vendas_simples(1305538297, 1)
        
        if vendas:
            venda = vendas[0]
            print("📋 Dados da API:")
            print(f"ID: {venda.get('id')}")
            print(f"Status: {venda.get('status')}")
            print(f"Total: {venda.get('total_amount')}")
            print(f"Comprador: {venda.get('buyer', {}).get('nickname')}")
            print(f"Data Aprovação: {venda.get('date_approved')}")
            print(f"Data Criação: {venda.get('date_created')}")
            print()
            
            # Verificar campos de pagamento
            print("💳 Dados de Pagamento:")
            payment = venda.get('payments', [])
            if payment:
                print(f"Payment: {payment[0]}")
            else:
                print("Nenhum dado de pagamento encontrado")
            print()
            
            # Verificar campos de envio
            print("📦 Dados de Envio:")
            shipping = venda.get('shipping', {})
            print(f"Shipping: {shipping}")
            print()
            
            # Verificar billing
            print("💰 Dados de Billing:")
            billing = venda.get('billing', {})
            print(f"Billing: {billing}")
            print()
            
            # Verificar estrutura completa
            print("🔍 Estrutura completa da venda:")
            for key, value in venda.items():
                if isinstance(value, (dict, list)):
                    print(f"  {key}: {type(value).__name__} com {len(value) if hasattr(value, '__len__') else 'N/A'} itens")
                else:
                    print(f"  {key}: {value}")
            
        else:
            print("❌ Nenhuma venda encontrada")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_venda_data()
