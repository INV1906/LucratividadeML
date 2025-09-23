#!/usr/bin/env python3
"""
Script para testar a funcionalidade de exportação de relatórios
"""

import requests
import json
import os
from datetime import datetime

def testar_exportacao_relatorios():
    """Testa a funcionalidade de exportação de relatórios"""
    
    print("🧪 TESTANDO EXPORTAÇÃO DE RELATÓRIOS")
    print("=" * 50)
    
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
        
        print("🔐 Tentando fazer login...")
        login_response = session.post(f"{base_url}/auth", data=login_data)
        
        if login_response.status_code == 200:
            print("✅ Login realizado com sucesso")
        else:
            print("⚠️ Login falhou, mas continuando com teste...")
        
        # Testar exportação CSV
        print("\n📊 Testando exportação CSV...")
        csv_response = session.get(f"{base_url}/api/exportar/relatorio/csv")
        
        if csv_response.status_code == 200:
            print("✅ Exportação CSV funcionando")
            
            # Salvar arquivo CSV
            filename = f"teste_relatorio_csv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'wb') as f:
                f.write(csv_response.content)
            print(f"📁 Arquivo CSV salvo: {filename}")
        else:
            print(f"❌ Erro na exportação CSV: {csv_response.status_code}")
            print(f"Resposta: {csv_response.text}")
        
        # Testar exportação Excel
        print("\n📈 Testando exportação Excel...")
        excel_response = session.get(f"{base_url}/api/exportar/relatorio/excel")
        
        if excel_response.status_code == 200:
            print("✅ Exportação Excel funcionando")
            
            # Salvar arquivo Excel
            filename = f"teste_relatorio_excel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            with open(filename, 'wb') as f:
                f.write(excel_response.content)
            print(f"📁 Arquivo Excel salvo: {filename}")
        else:
            print(f"❌ Erro na exportação Excel: {excel_response.status_code}")
            print(f"Resposta: {excel_response.text}")
        
        # Testar exportação PDF
        print("\n📄 Testando exportação PDF...")
        pdf_response = session.get(f"{base_url}/api/exportar/relatorio/pdf")
        
        if pdf_response.status_code == 200:
            print("✅ Exportação PDF funcionando")
            
            # Salvar arquivo PDF
            filename = f"teste_relatorio_pdf_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(pdf_response.content)
            print(f"📁 Arquivo PDF salvo: {filename}")
        else:
            print(f"❌ Erro na exportação PDF: {pdf_response.status_code}")
            print(f"Resposta: {pdf_response.text}")
        
        # Testar formato inválido
        print("\n🚫 Testando formato inválido...")
        invalid_response = session.get(f"{base_url}/api/exportar/relatorio/invalid")
        
        if invalid_response.status_code == 200:
            response_data = invalid_response.json()
            if not response_data.get('success', True):
                print("✅ Validação de formato funcionando")
            else:
                print("❌ Validação de formato não funcionando")
        else:
            print(f"✅ Validação de formato funcionando (status {invalid_response.status_code})")
        
        print("\n🎉 TESTE DE EXPORTAÇÃO CONCLUÍDO!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Certifique-se de que o Flask está rodando em http://localhost:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_exportacao_relatorios()
