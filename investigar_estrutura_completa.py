#!/usr/bin/env python3
"""
Script para investigar a estrutura completa da API em busca do custo de frete
"""

import os
from dotenv import load_dotenv
from meli_api import MercadoLivreAPI
from database import DatabaseManager
import json

load_dotenv()

try:
    print('🔍 INVESTIGANDO ESTRUTURA COMPLETA DA API')
    print('=' * 70)
    
    # Inicializar API e Database
    api = MercadoLivreAPI()
    db = DatabaseManager()
    
    user_id = 1305538297
    venda_id = '2000013113228770'
    
    # Obter access token
    access_token = db.obter_access_token(user_id)
    if not access_token:
        print('❌ Erro: Não foi possível obter access token')
        exit()
    
    # Buscar dados da venda
    venda_data = api.obter_venda_por_id(venda_id, access_token)
    
    if venda_data:
        print('✅ Dados da venda obtidos!')
        print()
        
        # Salvar estrutura completa em arquivo para análise
        with open('estrutura_venda_completa.json', 'w', encoding='utf-8') as f:
            json.dump(venda_data, f, indent=2, ensure_ascii=False)
        
        print('💾 Estrutura completa salva em estrutura_venda_completa.json')
        print()
        
        # Analisar campos específicos que podem conter custos de frete
        print('🔍 ANALISANDO CAMPOS ESPECÍFICOS:')
        
        # Verificar se há campos relacionados a custos
        campos_custo = []
        def buscar_campos_custo(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        buscar_campos_custo(value, current_path)
                    elif any(palavra in key.lower() for palavra in ['cost', 'fee', 'tax', 'charge', 'tarifa', 'custo', 'taxa']):
                        campos_custo.append((current_path, value))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    buscar_campos_custo(item, current_path)
        
        buscar_campos_custo(venda_data)
        
        print('💰 CAMPOS RELACIONADOS A CUSTOS:')
        for campo, valor in campos_custo:
            print(f'   {campo}: {valor}')
        print()
        
        # Verificar se há campos relacionados a shipping/envio
        campos_shipping = []
        def buscar_campos_shipping(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        buscar_campos_shipping(value, current_path)
                    elif any(palavra in key.lower() for palavra in ['shipping', 'frete', 'envio', 'delivery', 'entrega']):
                        campos_shipping.append((current_path, value))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    buscar_campos_shipping(item, current_path)
        
        buscar_campos_shipping(venda_data)
        
        print('🚚 CAMPOS RELACIONADOS A SHIPPING/ENVIO:')
        for campo, valor in campos_shipping:
            print(f'   {campo}: {valor}')
        print()
        
        # Verificar se há campos relacionados a marketplace/mercado
        campos_marketplace = []
        def buscar_campos_marketplace(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        buscar_campos_marketplace(value, current_path)
                    elif any(palavra in key.lower() for palavra in ['marketplace', 'mercado', 'ml', 'commission', 'comissao']):
                        campos_marketplace.append((current_path, valor))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    buscar_campos_marketplace(item, current_path)
        
        buscar_campos_marketplace(venda_data)
        
        print('🏪 CAMPOS RELACIONADOS A MARKETPLACE/MERCADO:')
        for campo, valor in campos_marketplace:
            print(f'   {campo}: {valor}')
        print()
        
        # Verificar valores específicos que podem ser o custo de frete
        print('🔍 VERIFICANDO VALORES ESPECÍFICOS:')
        
        # Procurar por valores próximos a 26.95
        valores_interessantes = []
        def buscar_valores_interessantes(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, (dict, list)):
                        buscar_valores_interessantes(value, current_path)
                    elif isinstance(value, (int, float)) and 20 <= value <= 30:
                        valores_interessantes.append((current_path, value))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    buscar_valores_interessantes(item, current_path)
        
        buscar_valores_interessantes(venda_data)
        
        print('💰 VALORES ENTRE 20 E 30 (possível custo de frete):')
        for campo, valor in valores_interessantes:
            print(f'   {campo}: {valor}')
        
    else:
        print('❌ Erro ao obter dados da venda')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
