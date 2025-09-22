#!/usr/bin/env python3
"""
Script para testar importação paralela de vendas
"""

import sys
sys.path.append('.')
from meli_api import MercadoLivreAPI
from database import DatabaseManager
import time
import requests

def test_importacao_paralela_pequena():
    """Testa importação paralela com poucas vendas"""
    
    print("🧪 Testando importação paralela (poucas vendas)...")
    print("=" * 60)
    
    try:
        api = MercadoLivreAPI()
        db = DatabaseManager()
        user_id = 1305538297
        
        # Buscar alguns IDs primeiro
        print("🔍 Buscando IDs de vendas...")
        order_ids = api.obter_todos_ids_vendas(user_id)
        
        if not order_ids:
            print("❌ Nenhum ID encontrado para testar")
            return False
        
        # Testar apenas as primeiras 20 vendas
        test_ids = order_ids[:20]
        print(f"🔍 Testando importação paralela de {len(test_ids)} vendas...")
        
        access_token = api.db.obter_access_token(user_id)
        if not access_token:
            print("❌ Token de acesso não encontrado")
            return False
        
        # Teste de busca paralela
        print("\n📦 Testando busca paralela...")
        start_time = time.time()
        
        vendas_detalhadas = api.obter_vendas_paralelo(test_ids, access_token, max_workers=10)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Busca paralela concluída em {duration:.2f} segundos")
        print(f"📊 {len(vendas_detalhadas)}/{len(test_ids)} vendas encontradas")
        
        # Teste de salvamento paralelo
        print("\n💾 Testando salvamento paralelo...")
        start_time = time.time()
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def processar_venda_individual(venda_data):
            try:
                order_id = venda_data.get('id')
                if db.salvar_venda_completa(venda_data, user_id):
                    return {'sucesso': True, 'order_id': order_id}
                else:
                    return {'sucesso': False, 'order_id': order_id, 'erro': 'Falha ao salvar'}
            except Exception as e:
                return {'sucesso': False, 'order_id': venda_data.get('id', 'N/A'), 'erro': str(e)}
        
        sucessos = 0
        erros = 0
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_venda = {
                executor.submit(processar_venda_individual, venda): venda 
                for venda in vendas_detalhadas
            }
            
            for future in as_completed(future_to_venda):
                result = future.result()
                if result['sucesso']:
                    sucessos += 1
                else:
                    erros += 1
                    print(f"❌ Erro na venda {result['order_id']}: {result.get('erro', 'Erro desconhecido')}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Salvamento paralelo concluído em {duration:.2f} segundos")
        print(f"📊 Sucessos: {sucessos}, Erros: {erros}")
        
        return sucessos > 0
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importacao_completa_paralela():
    """Testa importação completa com paralelismo"""
    
    print("\n🧪 Testando importação completa paralela...")
    print("=" * 60)
    
    try:
        from app import importar_vendas_background
        
        user_id = 1305538297
        
        print(f"🚀 Iniciando importação completa paralela para user_id: {user_id}")
        start_time = time.time()
        
        importar_vendas_background(user_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Importação completa paralela executada em {duration:.2f} segundos")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_comparison():
    """Compara performance entre métodos"""
    
    print("\n📊 Comparação de Performance")
    print("=" * 60)
    
    try:
        api = MercadoLivreAPI()
        user_id = 1305538297
        
        # Buscar alguns IDs
        order_ids = api.obter_todos_ids_vendas(user_id)
        if not order_ids:
            print("❌ Nenhum ID encontrado")
            return
        
        # Testar com 10 vendas
        test_ids = order_ids[:10]
        access_token = api.db.obter_access_token(user_id)
        
        if not access_token:
            print("❌ Token não encontrado")
            return
        
        print(f"🔍 Testando com {len(test_ids)} vendas...")
        
        # Método sequencial
        print("\n🐌 Método Sequencial:")
        start_time = time.time()
        
        vendas_sequencial = []
        for order_id in test_ids:
            venda = api.obter_venda_por_id(order_id, access_token)
            if venda:
                vendas_sequencial.append(venda)
        
        end_time = time.time()
        duration_sequencial = end_time - start_time
        print(f"   Tempo: {duration_sequencial:.2f} segundos")
        print(f"   Vendas encontradas: {len(vendas_sequencial)}")
        
        # Método paralelo
        print("\n🚀 Método Paralelo:")
        start_time = time.time()
        
        vendas_paralelo = api.obter_vendas_paralelo(test_ids, access_token, max_workers=10)
        
        end_time = time.time()
        duration_paralelo = end_time - start_time
        print(f"   Tempo: {duration_paralelo:.2f} segundos")
        print(f"   Vendas encontradas: {len(vendas_paralelo)}")
        
        # Comparação
        if duration_sequencial > 0 and duration_paralelo > 0:
            speedup = duration_sequencial / duration_paralelo
            print(f"\n⚡ Speedup: {speedup:.2f}x mais rápido")
            print(f"💾 Economia de tempo: {duration_sequencial - duration_paralelo:.2f} segundos")
        
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")

if __name__ == "__main__":
    print("🔧 Teste de Importação Paralela")
    print("=" * 60)
    
    # Teste 1: Importação paralela pequena
    if test_importacao_paralela_pequena():
        print("\n✅ Importação paralela funcionando!")
        
        # Teste 2: Comparação de performance
        test_performance_comparison()
        
        # Teste 3: Importação completa (apenas se houver poucas vendas)
        print("\n⚠️ Testando importação completa...")
        test_importacao_completa_paralela()
    else:
        print("\n❌ Falha na importação paralela")
