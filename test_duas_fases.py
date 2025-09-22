#!/usr/bin/env python3
"""
Script para testar importação em duas fases
"""

import sys
sys.path.append('.')
from meli_api import MercadoLivreAPI
from database import DatabaseManager
import time

def test_busca_ids():
    """Testa a busca de IDs (fase 1)"""
    
    print("🧪 Testando FASE 1: Busca de IDs...")
    print("=" * 60)
    
    try:
        api = MercadoLivreAPI()
        user_id = 1305538297
        
        def callback_progresso(total_ids, status):
            print(f"📊 {status} - Total: {total_ids}")
        
        print(f"🔍 Buscando todos os IDs para user_id: {user_id}")
        start_time = time.time()
        
        order_ids = api.obter_todos_ids_vendas(user_id, callback_progresso)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if order_ids:
            print(f"✅ Encontrados {len(order_ids)} IDs em {duration:.2f} segundos")
            print(f"📈 Primeiro ID: {order_ids[0]}")
            print(f"📈 Último ID: {order_ids[-1]}")
            
            # Verificar se há IDs duplicados
            unique_ids = set(order_ids)
            print(f"🔍 IDs únicos: {len(unique_ids)}")
            print(f"🔍 Total de IDs: {len(order_ids)}")
            
            if len(unique_ids) != len(order_ids):
                print("⚠️ Aviso: Há IDs duplicados!")
            else:
                print("✅ Nenhum ID duplicado encontrado")
                
            return order_ids
        else:
            print("❌ Nenhum ID encontrado")
            return []
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return []

def test_importacao_individual():
    """Testa importação individual de algumas vendas (fase 2)"""
    
    print("\n🧪 Testando FASE 2: Importação individual...")
    print("=" * 60)
    
    try:
        api = MercadoLivreAPI()
        db = DatabaseManager()
        user_id = 1305538297
        
        # Buscar alguns IDs primeiro
        order_ids = api.obter_todos_ids_vendas(user_id)
        
        if not order_ids:
            print("❌ Nenhum ID encontrado para testar")
            return False
        
        # Testar apenas as primeiras 5 vendas
        test_ids = order_ids[:5]
        print(f"🔍 Testando importação de {len(test_ids)} vendas...")
        
        access_token = api.db.obter_access_token(user_id)
        if not access_token:
            print("❌ Token de acesso não encontrado")
            return False
        
        sucessos = 0
        erros = 0
        
        for i, order_id in enumerate(test_ids):
            print(f"📦 Processando venda {i+1}/{len(test_ids)}: {order_id}")
            
            # Buscar detalhes da venda
            venda = api.obter_venda_por_id(order_id, access_token)
            
            if venda:
                # Salvar venda
                if db.salvar_venda_completa(venda, user_id):
                    sucessos += 1
                    print(f"  ✅ Venda {order_id} salva com sucesso")
                else:
                    erros += 1
                    print(f"  ❌ Erro ao salvar venda {order_id}")
            else:
                erros += 1
                print(f"  ❌ Erro ao buscar detalhes da venda {order_id}")
        
        print(f"\n📊 Resultado do teste:")
        print(f"   Sucessos: {sucessos}")
        print(f"   Erros: {erros}")
        
        return sucessos > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importacao_completa():
    """Testa importação completa com duas fases"""
    
    print("\n🧪 Testando importação completa (duas fases)...")
    print("=" * 60)
    
    try:
        from app import importar_vendas_background
        
        user_id = 1305538297
        
        print(f"🚀 Iniciando importação completa para user_id: {user_id}")
        start_time = time.time()
        
        importar_vendas_background(user_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Importação completa executada em {duration:.2f} segundos")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Teste de Importação em Duas Fases")
    print("=" * 60)
    
    # Teste 1: Busca de IDs
    order_ids = test_busca_ids()
    
    if order_ids:
        print(f"\n✅ FASE 1: Sucesso! Encontrados {len(order_ids)} IDs")
        
        # Teste 2: Importação individual (apenas algumas vendas)
        if test_importacao_individual():
            print("\n✅ FASE 2: Sucesso! Importação individual funcionando")
            
            # Teste 3: Importação completa (apenas se houver poucas vendas)
            if len(order_ids) <= 100:  # Só testa se houver poucas vendas
                print(f"\n⚠️ Poucas vendas ({len(order_ids)}). Testando importação completa...")
                test_importacao_completa()
            else:
                print(f"\n📊 Muitas vendas ({len(order_ids)}). Teste de importação completa pulado.")
        else:
            print("\n❌ FASE 2: Falha na importação individual")
    else:
        print("\n❌ FASE 1: Falha na busca de IDs")
