#!/usr/bin/env python3
"""
Script para testar a API de categorias
"""

import requests
import json

def testar_api_categorias():
    """Testa a API de categorias"""
    
    print('🧪 TESTANDO API DE CATEGORIAS')
    print('=' * 50)
    
    # URL base da aplicação
    base_url = "http://localhost:5000"
    
    # Simular login (você pode precisar ajustar isso)
    session = requests.Session()
    
    try:
        # Tentar fazer login
        login_data = {
            'email': 'test@example.com',  # Ajuste conforme necessário
            'password': 'test123'  # Ajuste conforme necessário
        }
        
        print('🔐 Tentando fazer login...')
        login_response = session.post(f"{base_url}/auth", data=login_data)
        
        if login_response.status_code == 200:
            print('✅ Login realizado com sucesso')
        else:
            print('⚠️ Login falhou, mas continuando com teste...')
        
        # Testar API de categorias
        print('\n📊 Testando API de categorias...')
        categorias_response = session.get(f"{base_url}/api/analise/categorias")
        
        if categorias_response.status_code == 200:
            print('✅ API de categorias funcionando')
            
            try:
                data = categorias_response.json()
                print(f'📋 Dados retornados: {json.dumps(data, indent=2, ensure_ascii=False)}')
                
                if data.get('success'):
                    dados = data.get('dados', {})
                    categorias = dados.get('categorias', [])
                    vendas = dados.get('vendas', [])
                    receitas = dados.get('receitas', [])
                    resumo = dados.get('resumo', {})
                    
                    print(f'🏷️ Categorias encontradas: {len(categorias)}')
                    print(f'📊 Vendas por categoria: {vendas}')
                    print(f'💰 Receitas por categoria: {receitas}')
                    print(f'📈 Resumo: {resumo}')
                    
                    if categorias:
                        print('🎉 Gráfico de categorias deve funcionar agora!')
                    else:
                        print('⚠️ Ainda não há categorias para exibir')
                        
                else:
                    print('❌ API retornou success: false')
                    
            except json.JSONDecodeError as e:
                print(f'❌ Erro ao parsear JSON: {e}')
                print(f'Resposta: {categorias_response.text[:200]}...')
        else:
            print(f'❌ Erro na API de categorias: {categorias_response.status_code}')
            print(f'Resposta: {categorias_response.text[:200]}...')
        
        print('\n🎉 TESTE DE API CONCLUÍDO!')
        
    except requests.exceptions.ConnectionError:
        print('❌ Erro: Não foi possível conectar ao servidor')
        print('   Certifique-se de que o Flask está rodando em http://localhost:5000')
    except Exception as e:
        print(f'❌ Erro inesperado: {e}')

if __name__ == "__main__":
    testar_api_categorias()
