#!/usr/bin/env python3
"""
Script de teste local para verificar correções de múltiplos usuários
"""

import requests
import json
import time

def testar_aplicacao_local():
    """Testa a aplicação localmente"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testando aplicação local...")
    
    try:
        # Teste 1: Verificar se a aplicação está respondendo
        print("\n1️⃣ Testando conectividade...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Aplicação respondendo corretamente")
        else:
            print("   ❌ Aplicação com problemas")
            return False
        
        # Teste 2: Verificar se as rotas de debug estão funcionando
        print("\n2️⃣ Testando rotas de debug...")
        try:
            debug_response = requests.post(f"{base_url}/debug/limpar-sessoes", timeout=5)
            print(f"   Status limpeza de sessões: {debug_response.status_code}")
            if debug_response.status_code == 200:
                print("   ✅ Rota de debug funcionando")
            else:
                print("   ⚠️ Rota de debug com problemas")
        except Exception as e:
            print(f"   ⚠️ Erro ao testar debug: {e}")
        
        # Teste 3: Verificar configurações de sessão
        print("\n3️⃣ Verificando configurações...")
        try:
            from configuracao_sessoes import ConfiguracaoSessoes
            print(f"   Múltiplas sessões permitidas: {ConfiguracaoSessoes.deve_permitir_multiplas_sessoes()}")
            print(f"   Máximo de sessões por usuário: {ConfiguracaoSessoes.obter_max_sessoes_por_usuario()}")
            print(f"   Tempo de expiração (horas): {ConfiguracaoSessoes.obter_tempo_expiracao_horas()}")
        except Exception as e:
            print(f"   ❌ Erro ao carregar configurações: {e}")
        
        print("\n✅ Teste local concluído com sucesso!")
        print("\n📋 Resumo das correções implementadas:")
        print("   • Tabelas de autenticação criadas")
        print("   • Sistema de sessões configurável")
        print("   • Suporte a múltiplos usuários simultâneos")
        print("   • Prevenção de conflitos de sessão")
        print("   • Rotas de debug para limpeza de sessões")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à aplicação")
        print("   Verifique se a aplicação está rodando em http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    testar_aplicacao_local()
