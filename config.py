"""
Configurações da aplicação de lucratividade do Mercado Livre.
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação."""
    
    # Configurações do Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configurações do Mercado Livre
    MELI_APP_ID = os.getenv('MELI_APP_ID')
    MELI_CLIENT_SECRET = os.getenv('MELI_CLIENT_SECRET')
    MELI_REDIRECT_URI = os.getenv('MELI_REDIRECT_URI', 'https://c1979facbdcd.ngrok-free.app/callback')
    URL_CODE = os.getenv('URL_CODE', 'https://auth.mercadolivre.com.br/authorization')
    URL_OAUTH_TOKEN = os.getenv('URL_OAUTH_TOKEN', 'https://api.mercadolibre.com/oauth/token')
    
    # Configurações do banco de dados
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME', 'mercadolivre_lucratividade')
    
    # Configurações de arquivos
    ARQUIVO_RESPONSE = os.getenv('ARQUIVO_RESPONSE', 'response.json')
    ARQUIVO_PRODUTOS = os.getenv('ARQUIVO_PRODUTOS', 'produtos.json')
    ARQUIVO_VENDAS = os.getenv('ARQUIVO_VENDAS', 'vendas.json')
    
    # Configurações de custos padrão
    CUSTOS_PADRAO = {
        'imposto_perc': 14.0,  # 14% de imposto padrão
        'embalagem_por_item': 5.0,  # R$ 5 por item
        'custo_por_item': 0,  # Será calculado por item
        'custos_extras': 0
    }
    
    # Configurações de paginação
    PRODUTOS_POR_PAGINA = 20
    VENDAS_POR_PAGINA = 50
    
    # Configurações de API
    API_TIMEOUT = 30  # segundos
    MAX_RETRIES = 3

class DevelopmentConfig(Config):
    """Configurações para desenvolvimento."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configurações para produção."""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configurações para testes."""
    DEBUG = True
    TESTING = True
    DB_NAME = 'mercadolivre_lucratividade_test'

# Configuração baseada no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
