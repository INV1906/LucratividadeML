#!/usr/bin/env python3
"""
Script para atualizar vendas existentes com traduções em português
"""

import sys
sys.path.append('.')
from database import DatabaseManager
from translations import translate_payment_status, translate_payment_method, translate_shipping_method, translate_order_status
from shipping_status import map_ml_shipping_status

def atualizar_traducoes_vendas():
    """Atualiza todas as vendas existentes com traduções em português"""
    
    print("🔄 Atualizando traduções das vendas existentes...")
    print("=" * 60)
    
    try:
        db = DatabaseManager()
        conn = db.conectar()
        
        with conn.cursor() as cursor:
            # Buscar todas as vendas que precisam de tradução
            cursor.execute("""
                SELECT venda_id, user_id, status_pagamento, payment_method, 
                       shipping_method, status, status_envio, status_envio_categoria
                FROM vendas 
                WHERE status_pagamento_pt IS NULL 
                OR payment_method_pt IS NULL 
                OR shipping_method_pt IS NULL
                LIMIT 1000
            """)
            
            vendas = cursor.fetchall()
            print(f"📦 Encontradas {len(vendas)} vendas para atualizar")
            
            if not vendas:
                print("✅ Todas as vendas já estão traduzidas!")
                return True
            
            atualizadas = 0
            
            for venda in vendas:
                venda_id, user_id, status_pagamento, payment_method, shipping_method, status, status_envio, status_envio_categoria = venda
                
                # Traduzir status de pagamento
                status_pagamento_pt = translate_payment_status(status_pagamento or 'unknown')
                
                # Traduzir método de pagamento
                payment_method_pt = translate_payment_method(payment_method or 'unknown')
                
                # Traduzir método de envio
                shipping_method_pt = translate_shipping_method(shipping_method or 'unknown')
                
                # Traduzir status do pedido
                status_pedido_pt = translate_order_status(status or 'unknown')
                
                # Traduzir status de envio
                status_envio_pt = status_envio or 'unknown'
                if status_envio_pt != 'unknown':
                    _, status_descricao, _ = map_ml_shipping_status(status_envio_pt, '', False)
                    status_envio_pt = status_descricao
                
                # Traduzir categoria de envio
                categoria_envio_pt = status_envio_categoria or 'Indefinido'
                
                # Atualizar venda
                cursor.execute("""
                    UPDATE vendas SET
                        status_pagamento_pt = %s,
                        payment_method_pt = %s,
                        shipping_method_pt = %s,
                        status_pedido_pt = %s,
                        status_envio_pt = %s,
                        categoria_envio_pt = %s
                    WHERE venda_id = %s AND user_id = %s
                """, (
                    status_pagamento_pt, payment_method_pt, shipping_method_pt,
                    status_pedido_pt, status_envio_pt, categoria_envio_pt,
                    venda_id, user_id
                ))
                
                atualizadas += 1
                
                if atualizadas % 100 == 0:
                    print(f"📊 {atualizadas} vendas atualizadas...")
            
            conn.commit()
            print(f"✅ {atualizadas} vendas atualizadas com traduções!")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao atualizar traduções: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

def verificar_traducoes():
    """Verifica se as traduções estão funcionando"""
    
    print("\n🔍 Verificando traduções...")
    print("=" * 40)
    
    try:
        db = DatabaseManager()
        conn = db.conectar()
        
        with conn.cursor() as cursor:
            # Verificar algumas vendas traduzidas
            cursor.execute("""
                SELECT venda_id, status_pagamento, status_pagamento_pt,
                       payment_method, payment_method_pt,
                       shipping_method, shipping_method_pt,
                       status, status_pedido_pt,
                       status_envio, status_envio_pt
                FROM vendas 
                WHERE status_pagamento_pt IS NOT NULL
                LIMIT 5
            """)
            
            vendas = cursor.fetchall()
            
            if vendas:
                print("📊 Exemplos de traduções:")
                for venda in vendas:
                    print(f"\nVenda {venda[0]}:")
                    print(f"  Pagamento: {venda[1]} → {venda[2]}")
                    print(f"  Método Pagamento: {venda[3]} → {venda[4]}")
                    print(f"  Método Envio: {venda[5]} → {venda[6]}")
                    print(f"  Status Pedido: {venda[7]} → {venda[8]}")
                    print(f"  Status Envio: {venda[9]} → {venda[10]}")
            else:
                print("❌ Nenhuma venda traduzida encontrada")
                
    except Exception as e:
        print(f"❌ Erro ao verificar traduções: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("🚀 Atualizando Sistema de Traduções")
    print("=" * 50)
    
    # Atualizar traduções
    if atualizar_traducoes_vendas():
        # Verificar resultado
        verificar_traducoes()
        print("\n🎉 Sistema de traduções atualizado com sucesso!")
    else:
        print("\n❌ Falha ao atualizar traduções")
