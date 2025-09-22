#!/usr/bin/env python3
"""
Script para testar busca de todas as vendas
"""

import sys
sys.path.append('.')
from meli_api import MercadoLivreAPI
from database import DatabaseManager

def test_busca_todas_vendas():
    """Testa a busca de todas as vendas"""
    
    print("🧪 Testando busca de TODAS as vendas...")
    print("=" * 60)
    
    try:
        api = MercadoLivreAPI()
        db = DatabaseManager()
        
        user_id = 1305538297
        
        def callback_progresso(total_vendas, status):
            print(f"📊 {status} - Total: {total_vendas}")
        
        print(f"🔍 Buscando todas as vendas para user_id: {user_id}")
        vendas = api.obter_todas_vendas(user_id, callback_progresso)
        
        if vendas:
            print(f"✅ Encontradas {len(vendas)} vendas")
            print(f"📈 Primeira venda: {vendas[0].get('id', 'N/A')}")
            print(f"📈 Última venda: {vendas[-1].get('id', 'N/A')}")
            
            # Verificar se há vendas duplicadas
            ids = [v.get('id') for v in vendas if v.get('id')]
            unique_ids = set(ids)
            print(f"🔍 Vendas únicas: {len(unique_ids)}")
            print(f"🔍 Total de vendas: {len(vendas)}")
            
            if len(unique_ids) != len(vendas):
                print("⚠️ Aviso: Há vendas duplicadas!")
            else:
                print("✅ Nenhuma venda duplicada encontrada")
                
        else:
            print("❌ Nenhuma venda encontrada")
            
        return len(vendas) if vendas else 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 0

def test_importacao_completa():
    """Testa importação completa com todas as vendas"""
    
    print("\n🧪 Testando importação completa...")
    print("=" * 60)
    
    try:
        from app import importar_vendas_background
        
        user_id = 1305538297
        
        print(f"🚀 Iniciando importação completa para user_id: {user_id}")
        importar_vendas_background(user_id)
        
        print("✅ Importação completa executada")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Teste de Busca de Todas as Vendas")
    print("=" * 60)
    
    # Teste 1: Busca de todas as vendas
    total_vendas = test_busca_todas_vendas()
    
    if total_vendas > 0:
        print(f"\n✅ Sucesso! Encontradas {total_vendas} vendas")
        
        # Teste 2: Importação completa (apenas se houver vendas)
        if total_vendas > 100:  # Só testa se houver muitas vendas
            print(f"\n⚠️ Muitas vendas ({total_vendas}). Testando importação...")
            test_importacao_completa()
        else:
            print(f"\n📊 Poucas vendas ({total_vendas}). Teste de importação pulado.")
    else:
        print("\n❌ Nenhuma venda encontrada. Verifique a conexão com a API.")
