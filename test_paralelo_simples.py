#!/usr/bin/env python3
"""
Script para testar importação paralela de forma simples
"""

import sys
sys.path.append('.')
from meli_api import MercadoLivreAPI
from database import DatabaseManager
import time
import requests

def test_paralelo_simples():
    """Testa paralelismo com dados simulados"""
    
    print("🧪 Testando paralelismo com dados simulados...")
    print("=" * 60)
    
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import random
        
        def processar_item_simulado(item_id):
            """Simula processamento de um item"""
            # Simula tempo de processamento
            time.sleep(random.uniform(0.1, 0.5))
            return {'sucesso': True, 'item_id': item_id, 'tempo': time.time()}
        
        # Teste sequencial
        print("🐌 Teste Sequencial:")
        start_time = time.time()
        
        resultados_sequencial = []
        for i in range(20):
            resultado = processar_item_simulado(f"item_{i}")
            resultados_sequencial.append(resultado)
        
        end_time = time.time()
        duration_sequencial = end_time - start_time
        print(f"   Tempo: {duration_sequencial:.2f} segundos")
        print(f"   Itens processados: {len(resultados_sequencial)}")
        
        # Teste paralelo
        print("\n🚀 Teste Paralelo:")
        start_time = time.time()
        
        resultados_paralelo = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_item = {
                executor.submit(processar_item_simulado, f"item_{i}"): f"item_{i}" 
                for i in range(20)
            }
            
            for future in as_completed(future_to_item):
                resultado = future.result()
                resultados_paralelo.append(resultado)
        
        end_time = time.time()
        duration_paralelo = end_time - start_time
        print(f"   Tempo: {duration_paralelo:.2f} segundos")
        print(f"   Itens processados: {len(resultados_paralelo)}")
        
        # Comparação
        if duration_sequencial > 0 and duration_paralelo > 0:
            speedup = duration_sequencial / duration_paralelo
            print(f"\n⚡ Speedup: {speedup:.2f}x mais rápido")
            print(f"💾 Economia de tempo: {duration_sequencial - duration_paralelo:.2f} segundos")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_importacao_real():
    """Testa importação real se possível"""
    
    print("\n🧪 Testando importação real...")
    print("=" * 60)
    
    try:
        # Simular login
        session = requests.Session()
        login_data = {
            "type": "password",
            "username": "Contigo",
            "password": "Adeg@33781210"
        }
        
        # Fazer login
        response = session.post("http://localhost:3001/", json=login_data)
        
        if response.status_code != 200:
            print("❌ Erro no login")
            return False
        
        login_result = response.json()
        if not login_result.get('success'):
            print("❌ Falha no login")
            return False
        
        print("✅ Login realizado com sucesso!")
        
        # Iniciar importação
        print("📦 Iniciando importação paralela...")
        start_time = time.time()
        
        response = session.post("http://localhost:3001/importar/vendas")
        
        if response.status_code != 200:
            print(f"❌ Erro na importação: {response.status_code}")
            return False
        
        import_result = response.json()
        if not import_result.get('success'):
            print(f"❌ Falha na importação: {import_result.get('message')}")
            return False
        
        print("✅ Importação iniciada com sucesso!")
        
        # Monitorar por 30 segundos
        for i in range(30):
            time.sleep(1)
            response = session.get("http://localhost:3001/importar/status")
            if response.status_code == 200:
                status = response.json()
                vendas_status = status.get('vendas', {})
                
                print(f"[{i+1:2d}s] {vendas_status.get('status', 'N/A')} - "
                      f"Progresso: {vendas_status.get('progresso', 0)}% - "
                      f"Sucessos: {vendas_status.get('sucesso', 0)} - "
                      f"Erros: {vendas_status.get('erros', 0)}")
                
                if not vendas_status.get('ativo', False):
                    end_time = time.time()
                    duration = end_time - start_time
                    print(f"\n🏁 Importação finalizada em {duration:.2f} segundos!")
                    print(f"   Status: {vendas_status.get('status', 'N/A')}")
                    print(f"   Total processado: {vendas_status.get('atual', 0)}")
                    print(f"   Sucessos: {vendas_status.get('sucesso', 0)}")
                    print(f"   Erros: {vendas_status.get('erros', 0)}")
                    break
            else:
                print(f"❌ Erro ao verificar status: {response.status_code}")
                break
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Teste de Importação Paralela")
    print("=" * 60)
    
    # Teste 1: Paralelismo simulado
    if test_paralelo_simples():
        print("\n✅ Paralelismo funcionando!")
        
        # Teste 2: Importação real
        test_importacao_real()
    else:
        print("\n❌ Falha no teste de paralelismo")
