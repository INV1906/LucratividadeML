"""
Módulo de gerenciamento do banco de dados para a aplicação de lucratividade do Mercado Livre.
"""

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

# Carrega as variáveis de ambiente
load_dotenv()

class DatabaseManager:
    """Classe para gerenciar conexões e operações do banco de dados."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
    
    def conectar(self) -> Optional[mysql.connector.connection.MySQLConnection]:
        """Estabelece conexão com o banco de dados."""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return conn
        except Error as e:
            print(f'Erro na conexão com o MySQL: {e}')
            return None
    
    def criar_tabelas(self):
        """Cria todas as tabelas necessárias para a aplicação."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Tabela de tokens
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tokens(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        access_token VARCHAR(255),
                        token_type VARCHAR(15),
                        expires_in INT,
                        scope TEXT,
                        user_id INT,
                        refresh_token VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de informações do usuário
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_info(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        user_id INT,
                        nickname VARCHAR(255),
                        first_name VARCHAR(255),
                        email VARCHAR(255),
                        phone VARCHAR(15),
                        points INT,
                        permalink TEXT,
                        status VARCHAR(30),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de produtos (conforme dump original)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS produtos(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        mlb VARCHAR(25),
                        sku INT,
                        title VARCHAR(255),
                        price DECIMAL(10, 2),
                        regular_price DECIMAL(10, 2),
                        avaliable_quantity INT,
                        sold_quantity INT,
                        listing_type_id VARCHAR(25),
                        permalink TEXT,
                        thumbnail TEXT,
                        frete_gratis TINYINT(1),
                        modo_de_envio VARCHAR(18),
                        status VARCHAR(15),
                        category VARCHAR(10),
                        user_id INT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabela de sugestões de preço (conforme dump original)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sugestao_preco(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        mlb VARCHAR(25),
                        preco DECIMAL(10, 2),
                        sugestao DECIMAL(10, 2),
                        menor_preco DECIMAL(10, 2),
                        custo_venda DECIMAL(10, 2),
                        custo_envio DECIMAL(10, 2),
                        data DATETIME
                    )
                """)
                
                # Tabela de custos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custos(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        mlb VARCHAR(25),
                        taxa_fixa_list DECIMAL(10, 2),
                        valor_bruto_comissao DECIMAL(10, 2),
                        tipo VARCHAR(10),
                        custos DECIMAL(10, 2),
                        taxa_fixa_sale DECIMAL(10, 2),
                        bruto_comissao DECIMAL(10, 2),
                        porcentagem_da_comissao INT,
                        imposto DECIMAL(10, 2),
                        embalagem DECIMAL(10, 2),
                        custo DECIMAL(10, 2),
                        extra DECIMAL(10, 2)
                    )
                """)
                
                # Tabela de frete (conforme dump original)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS frete(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        mlb VARCHAR(25),
                        frete DECIMAL(10, 2),
                        peso INT
                    )
                """)
                
                # Tabela orders removida - usando apenas tabela vendas
                
                # Tabelas para sistema de webhooks
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_logs (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        notification_id VARCHAR(100),
                        topic VARCHAR(50) NOT NULL,
                        resource VARCHAR(500),
                        user_id INT,
                        success BOOLEAN DEFAULT FALSE,
                        attempts INT DEFAULT 1,
                        error_message TEXT,
                        raw_data JSON,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_topic (topic),
                        INDEX idx_user_id (user_id),
                        INDEX idx_processed_at (processed_at)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notificacoes_genericas (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        notification_id VARCHAR(100),
                        topic VARCHAR(50) NOT NULL,
                        resource VARCHAR(500),
                        user_id INT,
                        application_id INT,
                        attempts INT DEFAULT 1,
                        sent_at DATETIME,
                        received_at DATETIME,
                        actions JSON,
                        raw_data JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_topic (topic),
                        INDEX idx_user_id (user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS webhook_stats (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT,
                        topic VARCHAR(50),
                        total_received INT DEFAULT 0,
                        total_success INT DEFAULT 0,
                        total_errors INT DEFAULT 0,
                        last_processed DATETIME,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_user_topic (user_id, topic)
                    )
                """)
                
                conn.commit()
                print("Todas as tabelas foram criadas/verificadas com sucesso!")
                
                # Verifica e corrige estrutura das tabelas
                self._verificar_estrutura_produtos(cursor)
                self._verificar_estrutura_tokens(cursor)
                
                return True
                
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def _verificar_estrutura_produtos(self, cursor):
        """Verifica e corrige a estrutura da tabela produtos."""
        try:
            # Verifica se a coluna created_at existe
            cursor.execute("SHOW COLUMNS FROM produtos LIKE 'created_at'")
            has_created_at = cursor.fetchone()
            
            if not has_created_at:
                print("Adicionando coluna created_at à tabela produtos...")
                cursor.execute("""
                    ALTER TABLE produtos 
                    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                """)
                print("Colunas created_at e updated_at adicionadas com sucesso!")
            
            # Verifica e corrige o tipo da coluna sku
            cursor.execute("SHOW COLUMNS FROM produtos WHERE Field = 'sku'")
            sku_column = cursor.fetchone()
            
            if sku_column and ('int' in str(sku_column[1]).lower() if sku_column[1] else False):
                print("Corrigindo tipo da coluna 'sku' de INT para VARCHAR(100)...")
                cursor.execute("ALTER TABLE produtos MODIFY COLUMN sku VARCHAR(100)")
                print("Coluna 'sku' corrigida para VARCHAR(100)!")
            
            # Adicionar colunas para suporte a variações
            print("Adicionando colunas para suporte a variações...")
            
            # Verificar se coluna parent_mlb existe
            cursor.execute("SHOW COLUMNS FROM produtos WHERE Field = 'parent_mlb'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE produtos ADD COLUMN parent_mlb VARCHAR(25) NULL")
                print("Coluna 'parent_mlb' adicionada!")
            
            # Verificar se coluna is_variation existe
            cursor.execute("SHOW COLUMNS FROM produtos WHERE Field = 'is_variation'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE produtos ADD COLUMN is_variation BOOLEAN DEFAULT 0")
                print("Coluna 'is_variation' adicionada!")
            
            # Verificar se coluna variation_attribute existe
            cursor.execute("SHOW COLUMNS FROM produtos WHERE Field = 'variation_attribute'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE produtos ADD COLUMN variation_attribute VARCHAR(100) NULL")
                print("Coluna 'variation_attribute' adicionada!")
            
            # Verificar se coluna variation_value existe
            cursor.execute("SHOW COLUMNS FROM produtos WHERE Field = 'variation_value'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE produtos ADD COLUMN variation_value VARCHAR(100) NULL")
                print("Coluna 'variation_value' adicionada!")
            
            # Verificar se coluna variation_sku existe
            cursor.execute("SHOW COLUMNS FROM produtos WHERE Field = 'variation_sku'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE produtos ADD COLUMN variation_sku VARCHAR(100) NULL")
                print("Coluna 'variation_sku' adicionada!")
            
            print("Colunas para variações adicionadas com sucesso!")
                
        except Error as e:
            print(f"Erro ao verificar estrutura da tabela produtos: {e}")
    
    def _verificar_estrutura_tokens(self, cursor):
        """Verifica e corrige a estrutura da tabela tokens."""
        try:
            # Verifica se as colunas created_at e updated_at existem
            cursor.execute("SHOW COLUMNS FROM tokens LIKE 'created_at'")
            has_created_at = cursor.fetchone()
            
            cursor.execute("SHOW COLUMNS FROM tokens LIKE 'updated_at'")
            has_updated_at = cursor.fetchone()
            
            if not has_created_at or not has_updated_at:
                print("Adicionando colunas created_at e updated_at à tabela tokens...")
                
                if not has_created_at:
                    cursor.execute("ALTER TABLE tokens ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print("Coluna created_at adicionada à tabela tokens!")
                
                if not has_updated_at:
                    cursor.execute("ALTER TABLE tokens ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
                    print("Coluna updated_at adicionada à tabela tokens!")
                
        except Error as e:
            print(f"Erro ao verificar estrutura da tabela tokens: {e}")
    
    def salvar_tokens(self, dados: Dict[str, Any]) -> bool:
        """Salva ou atualiza tokens de acesso."""
        if not dados:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                access_token = dados.get("access_token")
                token_type = dados.get("token_type")
                expires_in = dados.get("expires_in")
                scope = dados.get("scope")
                user_id = dados.get("user_id")
                refresh_token = dados.get("refresh_token")
                
                # Verifica se já existe
                cursor.execute("SELECT user_id FROM tokens WHERE user_id = %s", (user_id,))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Verifica se a coluna updated_at existe antes de usá-la
                    cursor.execute("SHOW COLUMNS FROM tokens LIKE 'updated_at'")
                    has_updated_at = cursor.fetchone()
                    
                    if has_updated_at:
                        # Atualiza com updated_at e created_at
                        query = """
                            UPDATE tokens
                            SET access_token = %s, token_type = %s, expires_in = %s,
                                scope = %s, refresh_token = %s, created_at = NOW(), updated_at = NOW()
                            WHERE user_id = %s
                        """
                    else:
                        # Atualiza com created_at
                        query = """
                            UPDATE tokens
                            SET access_token = %s, token_type = %s, expires_in = %s,
                                scope = %s, refresh_token = %s, created_at = NOW()
                            WHERE user_id = %s
                        """
                    
                    cursor.execute(query, (access_token, token_type, expires_in, scope, refresh_token, user_id))
                    print('Tokens atualizados com sucesso!')
                else:
                    # Insere novo
                    query = """
                        INSERT INTO tokens(access_token, token_type, expires_in, scope, user_id, refresh_token)
                        VALUES(%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (access_token, token_type, expires_in, scope, user_id, refresh_token))
                    print('Novos tokens inseridos com sucesso!')
                
                conn.commit()
                return True
                
        except Error as e:
            print(f"Erro ao salvar tokens: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_access_token(self, user_id: int) -> Optional[str]:
        """Obtém o access token de um usuário, renovando se necessário."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                # Busca token e data de criação
                cursor.execute("""
                    SELECT access_token, created_at, expires_in 
                    FROM tokens 
                    WHERE user_id = %s
                """, (user_id,))
                resultado = cursor.fetchone()
                
                if not resultado:
                    return None
                
                access_token, created_at, expires_in = resultado
                
                # Verifica se o token expirou (com margem de 5 minutos)
                if created_at and expires_in:
                    from datetime import datetime, timedelta
                    expiracao = created_at + timedelta(seconds=expires_in - 300)  # 5 min de margem
                    
                    if datetime.now() > expiracao:
                        print(f"🔄 Token expirado para user_id {user_id}, tentando renovar...")
                        # Tenta renovar o token
                        from meli_api import MercadoLivreAPI
                        api = MercadoLivreAPI()
                        if api._renovar_token(user_id):
                            # Busca o novo token
                            cursor.execute("SELECT access_token FROM tokens WHERE user_id = %s", (user_id,))
                            novo_resultado = cursor.fetchone()
                            return novo_resultado[0] if novo_resultado else access_token
                        else:
                            print(f"❌ Falha ao renovar token para user_id {user_id}")
                            return access_token
                
                return access_token
                
        except Error as e:
            print(f"Erro ao obter access token: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_refresh_token(self, user_id: int) -> Optional[str]:
        """Obtém o refresh token de um usuário."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT refresh_token FROM tokens WHERE user_id = %s", (user_id,))
                resultado = cursor.fetchone()
                return resultado[0] if resultado else None
        except Error as e:
            print(f"Erro ao obter refresh token: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()
    
    def salvar_user_info(self, dados: Dict[str, Any]) -> bool:
        """Salva informações do usuário."""
        if not dados:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                user_id = dados.get('id')
                nickname = dados.get('nickname')
                first_name = dados.get('first_name')
                email = dados.get('email')
                phone = dados.get('phone', {}).get('number')
                points = dados.get('points')
                permalink = dados.get('permalink')
                status = dados.get('status', {}).get('site_status')
                
                # Verifica se já existe
                cursor.execute("SELECT user_id FROM user_info WHERE user_id = %s", (user_id,))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Atualiza
                    query = """
                        UPDATE user_info
                        SET nickname = %s, first_name = %s, email = %s, phone = %s,
                            points = %s, permalink = %s, status = %s, updated_at = NOW()
                        WHERE user_id = %s
                    """
                    cursor.execute(query, (nickname, first_name, email, phone, points, permalink, status, user_id))
                else:
                    # Insere novo
                    query = """
                        INSERT INTO user_info(nickname, first_name, email, phone, points, permalink, status, user_id)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (nickname, first_name, email, phone, points, permalink, status, user_id))
                
                conn.commit()
                return True
                
        except Error as e:
            print(f"Erro ao salvar informações do usuário: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def salvar_produto(self, dados: List[Any], user_id: int) -> bool:
        """Salva informações de um produto."""
        if not dados or len(dados) < 12:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                title, mlb, sku, available_quantity, sold_quantity, listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio, status, category = dados[:12]
                
                # Converte frete_gratis para boolean
                frete_gratis = 1 if frete_gratis == 'true' else 0
                
                # Verifica se já existe
                cursor.execute("SELECT mlb FROM produtos WHERE mlb = %s", (mlb,))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Atualiza
                    query = """
                        UPDATE produtos
                        SET title = %s, sku = %s, avaliable_quantity = %s, sold_quantity = %s,
                            listing_type_id = %s, permalink = %s, thumbnail = %s, frete_gratis = %s,
                            modo_de_envio = %s, status = %s, category = %s, updated_at = NOW()
                        WHERE mlb = %s
                    """
                    cursor.execute(query, (title, sku, available_quantity, sold_quantity, listing_type_id,
                                         permalink, thumbnail, frete_gratis, modo_de_envio, status, category, mlb))
                else:
                    # Insere novo
                    query = """
                        INSERT INTO produtos(title, sku, avaliable_quantity, sold_quantity, listing_type_id,
                                           permalink, thumbnail, frete_gratis, modo_de_envio, status, category, mlb, user_id)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (title, sku, available_quantity, sold_quantity, listing_type_id,
                                         permalink, thumbnail, frete_gratis, modo_de_envio, status, category, mlb, user_id))
                
                conn.commit()
                return True
                
        except Error as e:
            print(f"❌ Erro ao salvar produto {dados[0] if dados else 'desconhecido'}: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def obter_produto_por_mlb(self, mlb: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtém dados de um produto específico pelo MLB."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT * FROM produtos WHERE mlb = %s AND user_id = %s
                """, (mlb, user_id))
                return cursor.fetchone()
        except Error as e:
            print(f"❌ Erro ao obter produto {mlb}: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def salvar_sugestao_preco(self, dados: Dict[str, Any]) -> bool:
        """Salva sugestão de preço no banco."""
        if not dados:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Cria tabela se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sugestao_preco(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        mlb VARCHAR(25),
                        preco DECIMAL(10, 2),
                        sugestao DECIMAL(10, 2),
                        menor_preco DECIMAL(10, 2),
                        custo_venda DECIMAL(10, 2),
                        custo_envio DECIMAL(10, 2),
                        data DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                mlb = dados['mlb']
                preco = dados.get('preco_atual', 0)
                sugestao = dados.get('sugestao')
                menor_preco = dados.get('menor_preco')
                custo_venda = dados.get('custo_venda')
                custo_envio = dados.get('custo_envio')
                
                # Verifica se já existe
                cursor.execute("SELECT mlb FROM sugestao_preco WHERE mlb = %s", (mlb,))
                if cursor.fetchone():
                    # Atualiza
                    cursor.execute("""
                        UPDATE sugestao_preco
                        SET preco = %s, sugestao = %s, menor_preco = %s,
                            custo_venda = %s, custo_envio = %s, updated_at = NOW()
                        WHERE mlb = %s
                    """, (preco, sugestao, menor_preco, custo_venda, custo_envio, mlb))
                else:
                    # Insere novo
                    cursor.execute("""
                        INSERT INTO sugestao_preco
                        (mlb, preco, sugestao, menor_preco, custo_venda, custo_envio)
                        VALUES(%s, %s, %s, %s, %s, %s)
                    """, (mlb, preco, sugestao, menor_preco, custo_venda, custo_envio))
                
                conn.commit()
                return True
                
        except Error as e:
            print(f"❌ Erro ao salvar sugestão de preço: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def salvar_custos(self, dados: Dict[str, Any]) -> bool:
        """Salva custos do produto no banco."""
        if not dados:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Cria tabela se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS custos(
                        id INTEGER PRIMARY KEY AUTO_INCREMENT,
                        mlb VARCHAR(25),
                        taxa_fixa_list DECIMAL(10, 2),
                        valor_bruto_comissao DECIMAL(10, 2),
                        tipo VARCHAR(50),
                        custos DECIMAL(10, 2),
                        taxa_fixa_sale DECIMAL(10, 2),
                        bruto_comissao DECIMAL(10, 2),
                        porcentagem_comissao DECIMAL(5, 2),
                        imposto DECIMAL(10, 2),
                        embalagem DECIMAL(10, 2),
                        custo DECIMAL(10, 2),
                        extra DECIMAL(10, 2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """)
                
                mlb = dados['mlb']
                
                # Verifica se já existe
                cursor.execute("SELECT mlb FROM custos WHERE mlb = %s", (mlb,))
                if cursor.fetchone():
                    # Atualiza
                    cursor.execute("""
                        UPDATE custos
                        SET taxa_fixa_list = %s, valor_bruto_comissao = %s, tipo = %s,
                            custos = %s, taxa_fixa_sale = %s, bruto_comissao = %s,
                            porcentagem_comissao = %s, updated_at = NOW()
                        WHERE mlb = %s
                    """, (
                        dados.get('taxa_fixa_list'),
                        dados.get('valor_bruto_comissao'),
                        dados.get('tipo'),
                        dados.get('custos'),
                        dados.get('taxa_fixa_sale'),
                        dados.get('bruto_comissao'),
                        dados.get('porcentagem_comissao'),
                        mlb
                    ))
                else:
                    # Insere novo
                    cursor.execute("""
                        INSERT INTO custos
                        (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                         taxa_fixa_sale, bruto_comissao, porcentagem_comissao)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        mlb,
                        dados.get('taxa_fixa_list'),
                        dados.get('valor_bruto_comissao'),
                        dados.get('tipo'),
                        dados.get('custos'),
                        dados.get('taxa_fixa_sale'),
                        dados.get('bruto_comissao'),
                        dados.get('porcentagem_comissao')
                    ))
                
                conn.commit()
                return True
                
        except Error as e:
            print(f"❌ Erro ao salvar custos: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def salvar_produto_completo(self, dados_completos: Dict[str, Any], user_id: int) -> bool:
        """Salva produto com todos os dados relacionados (sugestão, custos, frete) - ULTRA OTIMIZADO."""
        if not dados_completos or not dados_completos.get('produto'):
            return False
        
        produto_data = dados_completos['produto']
        sugestao_data = dados_completos.get('sugestao')
        custos_data = dados_completos.get('custos')
        frete_data = dados_completos.get('frete')
        
        mlb = produto_data.get('id')
        if not mlb:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            # Inicia transação para melhor performance
            conn.autocommit = False
            with conn.cursor() as cursor:
                # 1. Salva dados básicos do produto
                title = produto_data.get('title', '').strip()
                if not title:
                    print(f"❌ Título vazio para produto {mlb}")
                    return False
                
                sku = None
                for attr in produto_data.get('attributes', []):
                    if attr.get("id") == "SELLER_SKU":
                        sku_value = attr.get("value_name")
                        if sku_value and sku_value.isdigit():
                            sku = int(sku_value)
                        break
                
                # Obtém preço de venda com validação
                price = float(produto_data.get('price', 0)) if produto_data.get('price') else 0
                regular_price = float(dados_completos.get('preco_regular') or produto_data.get('price', 0)) if (dados_completos.get('preco_regular') or produto_data.get('price')) else price
                
                available_quantity = int(produto_data.get('available_quantity', 0)) if produto_data.get('available_quantity') else 0
                sold_quantity = int(produto_data.get('sold_quantity', 0)) if produto_data.get('sold_quantity') else 0
                listing_type_id = str(produto_data.get('listing_type_id', '')) if produto_data.get('listing_type_id') else ''
                # Validação do permalink para garantir que seja do Mercado Livre
                permalink_raw = produto_data.get('permalink', '')
                if permalink_raw and 'mercadolivre.com.br' in permalink_raw:
                    permalink = str(permalink_raw)
                else:
                    # Se não for do ML ou estiver vazio, usa o link padrão
                    permalink = f"https://produto.mercadolivre.com.br/{mlb}"
                thumbnail = str(produto_data.get('thumbnail', '')) if produto_data.get('thumbnail') else ''
                frete_gratis = 1 if produto_data.get('shipping', {}).get('free_shipping', False) else 0
                modo_de_envio = str(produto_data.get('shipping', {}).get('mode', '')) if produto_data.get('shipping', {}).get('mode') else ''
                status = str(produto_data.get('status', 'active')) if produto_data.get('status') else 'active'
                category = str(produto_data.get('category_id', '')) if produto_data.get('category_id') else ''
                
                # Verifica se produto já existe
                cursor.execute("SELECT mlb FROM produtos WHERE mlb = %s", (mlb,))
                if cursor.fetchone():
                    # Atualiza
                    cursor.execute("""
                        UPDATE produtos
                        SET title = %s, sku = %s, price = %s, regular_price = %s, 
                            avaliable_quantity = %s, sold_quantity = %s, listing_type_id = %s,
                            permalink = %s, thumbnail = %s, frete_gratis = %s, modo_de_envio = %s,
                            status = %s, category = %s, updated_at = NOW()
                        WHERE mlb = %s
                    """, (title, sku, price, regular_price, available_quantity, sold_quantity,
                          listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                          status, category, mlb))
                else:
                    # Insere
                    cursor.execute("""
                        INSERT INTO produtos
                        (mlb, title, sku, price, regular_price, avaliable_quantity, sold_quantity,
                         listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                         status, category, user_id)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (mlb, title, sku, price, regular_price, available_quantity, sold_quantity,
                          listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                          status, category, user_id))
                
                # 2. Salva sugestões de preço (se disponível)
                if sugestao_data:
                    preco_atual = sugestao_data.get("current_price", {}).get("amount", price)
                    sugestao = sugestao_data.get("suggested_price", {}).get("amount")
                    menor_preco = sugestao_data.get("lowest_price", {}).get("amount")
                    custo_venda = sugestao_data.get("costs", {}).get("selling_fees")
                    custo_envio = sugestao_data.get("costs", {}).get("shipping_fees")
                    
                    cursor.execute("SELECT mlb FROM sugestao_preco WHERE mlb = %s", (mlb,))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE sugestao_preco
                            SET preco = %s, sugestao = %s, menor_preco = %s,
                                custo_venda = %s, custo_envio = %s, data = NOW()
                            WHERE mlb = %s
                        """, (preco_atual, sugestao, menor_preco, custo_venda, custo_envio, mlb))
                    else:
                        cursor.execute("""
                            INSERT INTO sugestao_preco
                            (mlb, preco, sugestao, menor_preco, custo_venda, custo_envio, data)
                            VALUES(%s, %s, %s, %s, %s, %s, NOW())
                        """, (mlb, preco_atual, sugestao, menor_preco, custo_venda, custo_envio))
                
                # 3. Salva custos (se disponível)
                if custos_data:
                    taxa_fixa_list = custos_data.get('listing_fee_details', {}).get('fixed_fee')
                    valor_bruto_comissao = custos_data.get('listing_fee_details', {}).get('gross_amount')
                    tipo = custos_data.get('listing_type_name')
                    custos = custos_data.get('sale_fee_amount')
                    taxa_fixa_sale = custos_data.get('sale_fee_details', {}).get('fixed_fee')
                    bruto_comissao = custos_data.get('sale_fee_details', {}).get('gross_amount')
                    porcentagem_comissao = custos_data.get('sale_fee_details', {}).get('percentage_fee')
                    
                    cursor.execute("SELECT mlb FROM custos WHERE mlb = %s", (mlb,))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE custos
                            SET taxa_fixa_list = %s, valor_bruto_comissao = %s, tipo = %s,
                                custos = %s, taxa_fixa_sale = %s, bruto_comissao = %s,
                                porcentagem_da_comissao = %s
                            WHERE mlb = %s
                        """, (taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                              taxa_fixa_sale, bruto_comissao, porcentagem_comissao, mlb))
                    else:
                        cursor.execute("""
                            INSERT INTO custos
                            (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                             taxa_fixa_sale, bruto_comissao, porcentagem_da_comissao)
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                              taxa_fixa_sale, bruto_comissao, porcentagem_comissao))
                
                # 4. Salva frete (se disponível)
                if frete_data:
                    valor_frete = frete_data.get("coverage", {}).get("all_country", {}).get("list_cost", 0)
                    peso = frete_data.get("coverage", {}).get("all_country", {}).get("billable_weight")
                    
                    if frete_gratis:
                        valor_frete = 0
                    
                    cursor.execute("SELECT mlb FROM frete WHERE mlb = %s", (mlb,))
                    if cursor.fetchone():
                        cursor.execute("""
                            UPDATE frete SET frete = %s, peso = %s WHERE mlb = %s
                        """, (valor_frete, peso, mlb))
                    else:
                        cursor.execute("""
                            INSERT INTO frete (mlb, frete, peso) VALUES(%s, %s, %s)
                        """, (mlb, valor_frete, peso))
                
                # Commit da transação
                conn.commit()
                return True
                
        except Error as e:
            # Rollback em caso de erro
            conn.rollback()
            print(f"❌ Erro ao salvar produto completo {mlb}: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def obter_produtos_usuario(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtém todos os produtos de um usuário."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                # Primeiro verifica se a coluna created_at existe
                cursor.execute("SHOW COLUMNS FROM produtos LIKE 'created_at'")
                has_created_at = cursor.fetchone()
                
                if has_created_at:
                    cursor.execute("""
                        SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                               p.thumbnail, c.name as categoria_nome
                        FROM produtos p
                        LEFT JOIN categorias_mlb c ON p.category = c.id
                        WHERE p.user_id = %s ORDER BY p.created_at DESC
                    """, (user_id,))
                else:
                    # Se não tem created_at, usa id
                    cursor.execute("""
                        SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                               p.thumbnail, c.name as categoria_nome
                        FROM produtos p
                        LEFT JOIN categorias_mlb c ON p.category = c.id
                        WHERE p.user_id = %s ORDER BY p.id DESC
                    """, (user_id,))
                return cursor.fetchall()
        except Error as e:
            print(f"Erro ao obter produtos: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_produtos_usuario_paginado(self, user_id: int, page: int, per_page: int) -> List[Dict[str, Any]]:
        """Obtém produtos de um usuário com paginação."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                offset = (page - 1) * per_page
                
                # Primeiro verifica se a coluna created_at existe
                cursor.execute("SHOW COLUMNS FROM produtos LIKE 'created_at'")
                has_created_at = cursor.fetchone()
                
                if has_created_at:
                    cursor.execute("""
                        SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                               p.thumbnail, c.name as categoria_nome
                        FROM produtos p
                        LEFT JOIN categorias_mlb c ON p.category = c.id
                        WHERE p.user_id = %s ORDER BY p.created_at DESC
                        LIMIT %s OFFSET %s
                    """, (user_id, per_page, offset))
                else:
                    # Se não tem created_at, usa id
                    cursor.execute("""
                        SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                               p.thumbnail, c.name as categoria_nome
                        FROM produtos p
                        LEFT JOIN categorias_mlb c ON p.category = c.id
                        WHERE p.user_id = %s ORDER BY p.id DESC
                        LIMIT %s OFFSET %s
                    """, (user_id, per_page, offset))
                return cursor.fetchall()
        except Error as e:
            print(f"Erro ao obter produtos paginados: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def contar_produtos_usuario(self, user_id: int) -> int:
        """Conta o total de produtos de um usuário."""
        conn = self.conectar()
        if not conn:
            return 0
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM produtos WHERE user_id = %s", (user_id,))
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Erro ao contar produtos: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_dados_evolucao_vendas(self, user_id: int, periodo: str = '30d') -> Dict[str, Any]:
        """Obtém dados de evolução de vendas para análise."""
        conn = self.conectar()
        if not conn:
            return {'labels': [], 'vendas': [], 'receitas': [], 'resumo': {'hoje': 0, 'semana': 0, 'mes': 0}}
        
        try:
            with conn.cursor() as cursor:
                # Determinar período
                dias = 30
                if periodo == '7d':
                    dias = 7
                elif periodo == '90d':
                    dias = 90
                
                # Buscar vendas por dia
                cursor.execute("""
                    SELECT 
                        DATE(data_aprovacao) as data_venda,
                        COUNT(*) as vendas,
                        SUM(valor_total) as receita
                    FROM vendas 
                    WHERE user_id = %s 
                    AND data_aprovacao >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND data_aprovacao IS NOT NULL
                    GROUP BY DATE(data_aprovacao)
                    ORDER BY data_venda
                """, (user_id, dias))
                
                vendas_por_dia = cursor.fetchall()
                
                # Buscar resumo
                cursor.execute("""
                    SELECT 
                        COUNT(*) as vendas_hoje,
                        SUM(valor_total) as receita_hoje
                    FROM vendas 
                    WHERE user_id = %s 
                    AND DATE(data_aprovacao) = CURDATE()
                """, (user_id,))
                
                hoje = cursor.fetchone()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as vendas_semana,
                        SUM(valor_total) as receita_semana
                    FROM vendas 
                    WHERE user_id = %s 
                    AND data_aprovacao >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                """, (user_id,))
                
                semana = cursor.fetchone()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as vendas_mes,
                        SUM(valor_total) as receita_mes
                    FROM vendas 
                    WHERE user_id = %s 
                    AND data_aprovacao >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """, (user_id,))
                
                mes = cursor.fetchone()
                
                # Preparar dados para o gráfico
                labels = []
                vendas = []
                receitas = []
                
                # Criar dicionário com dados existentes
                dados_dict = {}
                for data_venda, vendas_count, receita in vendas_por_dia:
                    data_str = data_venda.strftime('%d/%m')
                    dados_dict[data_str] = {'vendas': vendas_count, 'receita': float(receita) if receita else 0}
                
                # Preencher todos os dias do período
                from datetime import datetime, timedelta
                hoje_data = datetime.now()
                for i in range(dias):
                    data = hoje_data - timedelta(days=dias-1-i)
                    data_str = data.strftime('%d/%m')
                    labels.append(data_str)
                    
                    if data_str in dados_dict:
                        vendas.append(dados_dict[data_str]['vendas'])
                        receitas.append(dados_dict[data_str]['receita'])
                    else:
                        vendas.append(0)
                        receitas.append(0)
                
                # Resumo
                resumo = {
                    'hoje': hoje[0] if hoje and hoje[0] else 0,
                    'semana': semana[0] if semana and semana[0] else 0,
                    'mes': mes[0] if mes and mes[0] else 0
                }
                
                return {
                    'labels': labels,
                    'vendas': vendas,
                    'receitas': receitas,
                    'resumo': resumo
                }
                
        except Exception as e:
            print(f"Erro ao obter dados de evolução de vendas: {e}")
            return {'labels': [], 'vendas': [], 'receitas': [], 'resumo': {'hoje': 0, 'semana': 0, 'mes': 0}}
        finally:
            conn.close()

    def obter_dados_categorias_vendas(self, user_id: int) -> Dict[str, Any]:
        """Obtém dados de vendas por categoria para análise."""
        conn = self.conectar()
        if not conn:
            return {'categorias': [], 'vendas': [], 'receitas': [], 'resumo': {'categoria_top': 'N/A', 'total_categorias': 0}}
        
        try:
            with conn.cursor() as cursor:
                # Buscar vendas por categoria
                cursor.execute("""
                    SELECT 
                        COALESCE(c.name, p.category) as categoria_nome,
                        COUNT(*) as vendas,
                        SUM(v.valor_total) as receita
                    FROM vendas v
                    JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                    JOIN produtos p ON p.mlb = vi.item_mlb
                    LEFT JOIN categorias_mlb c ON c.id = p.category
                    WHERE v.user_id = %s
                    AND p.category IS NOT NULL AND p.category != ''
                    GROUP BY p.category, c.name
                    ORDER BY vendas DESC
                    LIMIT 10
                """, (user_id,))
                
                categorias_data = cursor.fetchall()
                
                # Buscar total de categorias
                cursor.execute("""
                    SELECT COUNT(DISTINCT p.category) as total_categorias
                    FROM produtos p
                    WHERE p.user_id = %s
                    AND p.category IS NOT NULL AND p.category != ''
                """, (user_id,))
                
                total_result = cursor.fetchone()
                total_categorias = total_result[0] if total_result else 0
                
                # Preparar dados para o gráfico
                categorias = []
                vendas = []
                receitas = []
                
                for categoria_nome, vendas_count, receita in categorias_data:
                    categorias.append(categoria_nome or 'Sem categoria')
                    vendas.append(vendas_count)
                    receitas.append(float(receita) if receita else 0)
                
                # Resumo
                categoria_top = categorias[0] if categorias else 'N/A'
                
                return {
                    'categorias': categorias,
                    'vendas': vendas,
                    'receitas': receitas,
                    'resumo': {
                        'categoria_top': categoria_top,
                        'total_categorias': total_categorias
                    }
                }
                
        except Exception as e:
            print(f"Erro ao obter dados de categorias: {e}")
            return {'categorias': [], 'vendas': [], 'receitas': [], 'resumo': {'categoria_top': 'N/A', 'total_categorias': 0}}
        finally:
            conn.close()

    def obter_produtos_para_analise(self, user_id: int, sort_column: str = 'sold_quantity', sort_order: str = 'desc') -> List[Dict[str, Any]]:
        """Obtém produtos otimizados para análise (apenas com vendas > 0)."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                # Mapear colunas de ordenação
                column_mapping = {
                    'sold_quantity': 'p.sold_quantity',
                    'price': 'p.price',
                    'margem_liquida': 'margem_liquida',
                    'title': 'p.title',
                    'updated_at': 'p.updated_at'
                }
                
                sort_field = column_mapping.get(sort_column, 'p.sold_quantity')
                sort_direction = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
                
                # Query otimizada para análise - apenas produtos com vendas > 0
                query = f"""
                    SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                           p.thumbnail, p.frete, p.frete_gratis, p.listing_type_id, p.regular_price, p.permalink,
                           COALESCE(c.name, p.category) as categoria_nome, p.created_at, p.updated_at,
                           (SELECT COUNT(*) FROM produtos v WHERE v.parent_mlb = p.mlb AND v.is_variation = 1) as num_variacoes,
                           (
                               CASE 
                                   WHEN p.price > 0 THEN
                                       ROUND(
                                           ((p.price - COALESCE(p.frete, 0) - 
                                             COALESCE(custos.custos, p.price * 0.10) - 
                                             COALESCE(NULLIF(p.custo, 0), custos.custo, 0) - 
                                             COALESCE(NULLIF(p.embalagem, 0), custos.embalagem, 0) - 
                                             (COALESCE(NULLIF(p.imposto, 0), custos.imposto, 0) / 100) * (p.price - COALESCE(p.frete, 0) - COALESCE(custos.custos, p.price * 0.10)) - 
                                             COALESCE(NULLIF(p.extra, 0), custos.extra, 0)) / p.price) * 100, 1
                                       )
                                   ELSE 0
                               END
                           ) as margem_liquida
                    FROM produtos p
                    LEFT JOIN categorias_mlb c ON p.category = c.id
                    LEFT JOIN custos custos ON p.mlb = custos.mlb
                    WHERE p.user_id = %s AND p.is_variation = 0 AND p.sold_quantity > 0
                    ORDER BY {sort_field} {sort_direction}
                    LIMIT 100
                """
                
                cursor.execute(query, [user_id])
                produtos = cursor.fetchall()
                
                # Converter para dicionários
                produtos_com_variacoes = []
                for produto in produtos:
                    margem = float(produto[17]) if produto[17] is not None else 0
                    
                    produto_dict = {
                        'mlb': produto[0],
                        'title': produto[1],
                        'price': float(produto[2]) if produto[2] else 0,
                        'avaliable_quantity': produto[3],
                        'sold_quantity': produto[4],
                        'status': produto[5],
                        'category': produto[6],
                        'thumbnail': produto[7],
                        'frete': float(produto[8]) if produto[8] else 0,
                        'frete_gratis': produto[9],
                        'listing_type_id': produto[10],
                        'regular_price': float(produto[11]) if produto[11] else 0,
                        'permalink': produto[12],
                        'categoria_nome': produto[13],
                        'created_at': produto[14],
                        'updated_at': produto[15],
                        'num_variacoes': produto[16],
                        'margem_liquida': margem
                    }
                    produtos_com_variacoes.append(produto_dict)
                
                return produtos_com_variacoes
                
        except Exception as e:
            print(f"Erro ao obter produtos para análise: {e}")
            return []
        finally:
            conn.close()

    def obter_produtos_com_variacoes(self, user_id: int, pagina: int = 1, itens_por_pagina: int = 20, 
                                    busca: str = None, categoria: str = None, status: str = None, 
                                    sort_column: str = 'updated_at', sort_order: str = 'desc') -> List[Dict[str, Any]]:
        """Obtém produtos agrupados com suas variações."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                # Buscar apenas produtos principais (não variações)
                where_conditions = ["p.user_id = %s", "p.is_variation = 0"]
                params = [user_id]
                
                if busca:
                    where_conditions.append("(p.title LIKE %s OR p.mlb LIKE %s)")
                    params.extend([f"%{busca}%", f"%{busca}%"])
                
                if categoria:
                    where_conditions.append("(c.name = %s OR p.category = %s)")
                    params.extend([categoria, categoria])
                
                if status:
                    where_conditions.append("p.status = %s")
                    params.append(status)
                
                where_clause = " AND ".join(where_conditions)
                
                # Mapear colunas de ordenação
                column_mapping = {
                    'title': 'p.title',
                    'price': 'p.price',
                    'avaliable_quantity': 'p.avaliable_quantity',
                    'sold_quantity': 'p.sold_quantity',
                    'status': 'p.status',
                    'category': 'p.category',
                    'frete': 'p.frete',
                    'listing_type_id': 'p.listing_type_id',
                    'margem_liquida': 'margem_liquida',
                    'updated_at': 'p.updated_at',
                    'created_at': 'p.created_at'
                }
                
                # Validar coluna de ordenação
                sort_field = column_mapping.get(sort_column, 'p.updated_at')
                sort_direction = 'ASC' if sort_order.lower() == 'asc' else 'DESC'
                
                # Query principal com ordenação dinâmica
                if sort_column == 'margem_liquida':
                    # Para ordenação por margem, usar subquery com cálculo completo
                    query = f"""
                        SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                               p.thumbnail, p.frete, p.frete_gratis, p.listing_type_id, p.regular_price, p.permalink,
                               COALESCE(c.name, p.category) as categoria_nome, p.created_at, p.updated_at,
                               (SELECT COUNT(*) FROM produtos v WHERE v.parent_mlb = p.mlb AND v.is_variation = 1) as num_variacoes,
                               (
                                   CASE 
                                       WHEN p.price > 0 THEN
                                           ROUND(
                                               ((p.price - COALESCE(p.frete, 0) - 
                                                 COALESCE(custos.custos, p.price * 0.10) - 
                                                 COALESCE(NULLIF(p.custo, 0), custos.custo, 0) - 
                                                 COALESCE(NULLIF(p.embalagem, 0), custos.embalagem, 0) - 
                                                 (COALESCE(NULLIF(p.imposto, 0), custos.imposto, 0) / 100) * (p.price - COALESCE(p.frete, 0) - COALESCE(custos.custos, p.price * 0.10)) - 
                                                 COALESCE(NULLIF(p.extra, 0), custos.extra, 0)) / p.price) * 100, 1
                                           )
                                       ELSE 0
                                   END
                               ) as margem_liquida
                        FROM produtos p
                        LEFT JOIN categorias_mlb c ON p.category = c.id
                        LEFT JOIN custos custos ON p.mlb = custos.mlb
                        WHERE {where_clause}
                        ORDER BY margem_liquida {sort_direction}
                        LIMIT %s OFFSET %s
                    """
                else:
                    # Para outras ordenações, usar query simples
                    query = f"""
                        SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                               p.thumbnail, p.frete, p.frete_gratis, p.listing_type_id, p.regular_price, p.permalink,
                               COALESCE(c.name, p.category) as categoria_nome, p.created_at, p.updated_at,
                               (SELECT COUNT(*) FROM produtos v WHERE v.parent_mlb = p.mlb AND v.is_variation = 1) as num_variacoes,
                               0 as margem_liquida
                        FROM produtos p
                        LEFT JOIN categorias_mlb c ON p.category = c.id
                        WHERE {where_clause}
                        ORDER BY {sort_field} {sort_direction}
                        LIMIT %s OFFSET %s
                    """
                
                offset = (pagina - 1) * itens_por_pagina
                params.extend([itens_por_pagina, offset])
                
                cursor.execute(query, params)
                produtos = cursor.fetchall()
                
                # Para cada produto, buscar suas variações
                produtos_com_variacoes = []
                for produto in produtos:
                    # Usar margem calculada na query se disponível, senão calcular individualmente
                    if sort_column == 'margem_liquida' and len(produto) > 17:
                        margem = float(produto[17]) if produto[17] is not None else 0
                    else:
                        margem = self._calcular_margem_produto(produto[0], user_id)
                    
                    produto_dict = {
                        'mlb': produto[0],
                        'title': produto[1],
                        'price': float(produto[2]) if produto[2] else 0,
                        'avaliable_quantity': produto[3],
                        'sold_quantity': produto[4],
                        'status': produto[5],
                        'category': produto[6],
                        'thumbnail': produto[7],
                        'frete': float(produto[8]) if produto[8] else 0,
                        'frete_gratis': produto[9],
                        'listing_type_id': produto[10],
                        'regular_price': float(produto[11]) if produto[11] else 0,
                        'permalink': produto[12],
                        'categoria_nome': produto[13],
                        'created_at': produto[14],
                        'updated_at': produto[15],
                        'margem_liquida': margem,
                        'variations': []
                    }
                    
                    # Buscar variações deste produto
                    cursor.execute("""
                        SELECT mlb, title, price, avaliable_quantity, sold_quantity, status,
                               variation_attribute, variation_value, variation_sku, thumbnail
                        FROM produtos
                        WHERE parent_mlb = %s AND user_id = %s AND is_variation = 1
                        ORDER BY variation_value
                    """, (produto[0], user_id))
                    
                    variacoes = cursor.fetchall()
                    for variacao in variacoes:
                        produto_dict['variations'].append({
                            'mlb': variacao[0],
                            'title': variacao[1],
                            'price': float(variacao[2]) if variacao[2] else 0,
                            'avaliable_quantity': variacao[3],
                            'sold_quantity': variacao[4],
                            'status': variacao[5],
                            'variation_attribute': variacao[6],
                            'variation_value': variacao[7],
                            'variation_sku': variacao[8],
                            'thumbnail': variacao[9]
                        })
                    
                    produtos_com_variacoes.append(produto_dict)
                
                return produtos_com_variacoes
                
        except Error as e:
            print(f"Erro ao obter produtos com variações: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()

    def obter_produtos_usuario_filtrado(self, user_id: int, page: int, per_page: int, 
                                       busca: str = '', categoria: str = '', status: str = '') -> List[Dict[str, Any]]:
        """Obtém produtos de um usuário com filtros e paginação."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                offset = (page - 1) * per_page
                
                # Construir query com filtros
                where_conditions = ["user_id = %s"]
                params = [user_id]
                
                if busca:
                    where_conditions.append("(title LIKE %s OR mlb LIKE %s)")
                    params.extend([f"%{busca}%", f"%{busca}%"])
                
                if categoria:
                    where_conditions.append("(c.name = %s OR p.category = %s)")
                    params.extend([categoria, categoria])
                
                if status:
                    where_conditions.append("status = %s")
                    params.append(status)
                
                where_clause = " AND ".join(where_conditions)
                
                # Primeiro verifica se a coluna created_at existe
                cursor.execute("SHOW COLUMNS FROM produtos LIKE 'created_at'")
                has_created_at = cursor.fetchone()
                
                order_by = "created_at DESC" if has_created_at else "id DESC"
                
                query = f"""
                    SELECT p.mlb, p.title, p.price, p.avaliable_quantity, p.sold_quantity, p.status, p.category,
                           p.thumbnail, p.frete, p.frete_gratis, p.listing_type_id, p.regular_price,
                           c.name as categoria_nome
                    FROM produtos p
                    LEFT JOIN categorias_mlb c ON p.category = c.id
                    WHERE {where_clause.replace('user_id = %s', 'p.user_id = %s')}
                    ORDER BY {order_by.replace('created_at', 'p.created_at').replace('id', 'p.id')}
                    LIMIT %s OFFSET %s
                """
                params.extend([per_page, offset])
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except Error as e:
            print(f"Erro ao obter produtos filtrados: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def limpar_produtos_invalidos(self, user_id: int) -> int:
        """Remove produtos com dados inválidos (título vazio ou null)."""
        conn = self.conectar()
        if not conn:
            return 0
        
        try:
            with conn.cursor() as cursor:
                # Remove produtos com título vazio ou null
                cursor.execute("""
                    DELETE FROM produtos 
                    WHERE user_id = %s AND (title IS NULL OR title = '' OR title = 'null')
                """, (user_id,))
                
                produtos_removidos = cursor.rowcount
                conn.commit()
                
                if produtos_removidos > 0:
                    print(f"🧹 Removidos {produtos_removidos} produtos inválidos")
                
                return produtos_removidos
        except Error as e:
            print(f"Erro ao limpar produtos inválidos: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()

    def limpar_todos_produtos_invalidos(self) -> int:
        """Remove TODOS os produtos com dados inválidos de todos os usuários."""
        conn = self.conectar()
        if not conn:
            return 0
        
        try:
            with conn.cursor() as cursor:
                # Remove produtos com título vazio, null ou dados essenciais ausentes
                cursor.execute("""
                    DELETE FROM produtos 
                    WHERE title IS NULL 
                       OR title = '' 
                       OR title = 'null'
                       OR mlb IS NULL 
                       OR mlb = ''
                       OR price IS NULL
                """)
                
                produtos_removidos = cursor.rowcount
                conn.commit()
                
                print(f"🧹 LIMPEZA COMPLETA: Removidos {produtos_removidos} produtos inválidos de todos os usuários")
                
                return produtos_removidos
        except Error as e:
            print(f"Erro ao limpar todos os produtos inválidos: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()

    def atualizar_status_produto(self, mlb: str, user_id: int, novo_status: str) -> bool:
        """Atualiza apenas o status de um produto."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE produtos 
                    SET status = %s, updated_at = NOW()
                    WHERE mlb = %s AND user_id = %s
                """, (novo_status, mlb, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Erro ao atualizar status do produto {mlb}: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def verificar_produto_existe(self, mlb: str, user_id: int) -> bool:
        """Verifica se um produto existe no banco de dados."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id FROM produtos 
                    WHERE mlb = %s AND user_id = %s
                """, (mlb, user_id))
                
                return cursor.fetchone() is not None
        except Error as e:
            print(f"Erro ao verificar produto {mlb}: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def marcar_produto_como_excluido(self, mlb: str, user_id: int) -> bool:
        """Marca um produto como excluído (status = 'deleted')."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE produtos 
                    SET status = 'deleted', updated_at = NOW()
                    WHERE mlb = %s AND user_id = %s
                """, (mlb, user_id))
                
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Erro ao marcar produto {mlb} como excluído: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def obter_produtos_excluidos(self, user_id: int) -> List[Dict[str, Any]]:
        """Obtém produtos marcados como excluídos."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT mlb, title, status, updated_at
                    FROM produtos 
                    WHERE user_id = %s AND status = 'deleted'
                    ORDER BY updated_at DESC
                """, (user_id,))
                
                return cursor.fetchall()
        except Error as e:
            print(f"Erro ao obter produtos excluídos: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()

    def obter_status_produto(self, mlb: str, user_id: int) -> str:
        """Obtém o status atual de um produto no banco de dados."""
        conn = self.conectar()
        if not conn:
            return 'N/A'
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT status FROM produtos 
                    WHERE mlb = %s AND user_id = %s
                """, (mlb, user_id))
                
                result = cursor.fetchone()
                return result[0] if result else 'N/A'
        except Error as e:
            print(f"Erro ao obter status do produto {mlb}: {e}")
            return 'N/A'
        finally:
            if conn.is_connected():
                conn.close()

    def contar_produtos_usuario_filtrado(self, user_id: int, busca: str = '', 
                                       categoria: str = '', status: str = '') -> int:
        """Conta o total de produtos de um usuário com filtros."""
        conn = self.conectar()
        if not conn:
            return 0
        
        try:
            with conn.cursor() as cursor:
                # Construir query com filtros
                where_conditions = ["user_id = %s"]
                params = [user_id]
                
                if busca:
                    where_conditions.append("(title LIKE %s OR mlb LIKE %s)")
                    params.extend([f"%{busca}%", f"%{busca}%"])
                
                if categoria:
                    where_conditions.append("(c.name = %s OR p.category = %s)")
                    params.extend([categoria, categoria])
                
                if status:
                    where_conditions.append("status = %s")
                    params.append(status)
                
                where_clause = " AND ".join(where_conditions)
                query = f"SELECT COUNT(*) FROM produtos WHERE {where_clause}"
                
                cursor.execute(query, params)
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Erro ao contar produtos filtrados: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_categorias_usuario(self, user_id: int) -> List[str]:
        """Obtém todas as categorias únicas de um usuário."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT COALESCE(c.name, p.category) as categoria_nome
                    FROM produtos p
                    LEFT JOIN categorias_mlb c ON p.category = c.id
                    WHERE p.user_id = %s AND (p.category IS NOT NULL AND p.category != '')
                    ORDER BY categoria_nome
                """, (user_id,))
                return [row[0] for row in cursor.fetchall()]
        except Error as e:
            print(f"Erro ao obter categorias: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_vendas_usuario(self, user_id: int, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtém as vendas de um usuário agrupadas por packs."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(v.pack_id, v.venda_id) as pack_id,
                        v.total_produtos,
                        v.valor_total,
                        v.taxa_ml as taxa_total,
                        v.frete_total,
                        v.status,
                        v.data_aprovacao,
                        v.comprador_nome as comprador,
                        GROUP_CONCAT(
                            CONCAT(vi.item_titulo, ' (', vi.quantidade, 'x)') 
                            SEPARATOR ' | '
                        ) as produtos,
                        v.venda_id as ids_venda
                    FROM vendas v
                    LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                    WHERE v.user_id = %s 
                    GROUP BY v.venda_id, v.pack_id, v.total_produtos, v.valor_total, v.taxa_ml, v.frete_total, v.status, v.data_aprovacao, v.comprador_nome
                    ORDER BY v.data_aprovacao DESC
                    LIMIT %s
                """, (user_id, limite))
                return cursor.fetchall()
        except Error as e:
            print(f"Erro ao obter vendas: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_vendas_usuario_paginado(self, user_id: int, page: int, per_page: int) -> List[Dict[str, Any]]:
        """Obtém vendas de um usuário com paginação agrupadas por packs."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                offset = (page - 1) * per_page
                cursor.execute("""
                    SELECT 
                        COALESCE(v.pack_id, v.venda_id) as pack_id,
                        v.total_produtos,
                        v.valor_total,
                        v.taxa_ml as taxa_total,
                        v.frete_total,
                        v.status,
                        v.data_aprovacao,
                        v.comprador_nome as comprador,
                        GROUP_CONCAT(
                            CONCAT(vi.item_titulo, ' (', vi.quantidade, 'x)') 
                            SEPARATOR ' | '
                        ) as produtos,
                        v.venda_id as ids_venda
                    FROM vendas v
                    LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                    WHERE v.user_id = %s 
                    GROUP BY v.venda_id, v.pack_id, v.total_produtos, v.valor_total, v.taxa_ml, v.frete_total, v.status, v.data_aprovacao, v.comprador_nome
                    ORDER BY v.data_aprovacao DESC
                    LIMIT %s OFFSET %s
                """, (user_id, per_page, offset))
                return cursor.fetchall()
        except Error as e:
            print(f"Erro ao obter vendas paginadas: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def contar_vendas_usuario(self, user_id: int) -> int:
        """Conta o total de packs de vendas de um usuário."""
        conn = self.conectar()
        if not conn:
            return 0
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(DISTINCT COALESCE(pack_id, venda_id)) 
                    FROM vendas WHERE user_id = %s
                """, (user_id,))
                return cursor.fetchone()[0]
        except Error as e:
            print(f"Erro ao contar vendas: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()
    
    def atualizar_produto(self, mlb: str, user_id: int, dados: Dict[str, Any]) -> bool:
        """Atualiza os dados de um produto."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Verificar se o produto pertence ao usuário
                cursor.execute("SELECT id FROM produtos WHERE mlb = %s AND user_id = %s", (mlb, user_id))
                if not cursor.fetchone():
                    return False
                
                # Atualizar produto (apenas campos editáveis)
                cursor.execute("""
                    UPDATE produtos 
                    SET price = %s, avaliable_quantity = %s, 
                        status = %s, updated_at = NOW()
                    WHERE mlb = %s AND user_id = %s
                """, (
                    dados.get('price'),
                    dados.get('quantity'),
                    dados.get('status'),
                    mlb,
                    user_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Erro ao atualizar produto: {e}")
            conn.rollback()
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def atualizar_produto_completo(self, mlb: str, user_id: int, dados: Dict[str, Any]) -> bool:
        """Atualiza todos os dados de um produto com informações do Mercado Livre."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Atualizar dados completos do produto
                cursor.execute("""
                    UPDATE produtos 
                    SET title = %s, price = %s, regular_price = %s, 
                        avaliable_quantity = %s, sold_quantity = %s, status = %s,
                        category = %s, thumbnail = %s, listing_type_id = %s,
                        frete = %s, frete_gratis = %s, updated_at = NOW()
                    WHERE mlb = %s AND user_id = %s
                """, (
                    dados.get('title'),
                    dados.get('price'),
                    dados.get('regular_price'),
                    dados.get('avaliable_quantity'),
                    dados.get('sold_quantity'),
                    dados.get('status'),
                    dados.get('category'),
                    dados.get('thumbnail'),
                    dados.get('listing_type_id'),
                    dados.get('frete'),
                    dados.get('frete_gratis'),
                    mlb,
                    user_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        except Error as e:
            print(f"Erro ao atualizar produto completo: {e}")
            conn.rollback()
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def calcular_lucratividade_venda(self, pack_id: str) -> Optional[Dict[str, Any]]:
        """Calcula a lucratividade de um pack específico."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                # Busca todos os itens do pack
                cursor.execute("""
                    SELECT v.*, vi.* FROM vendas v
                    LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                    WHERE COALESCE(v.pack_id, v.venda_id) = %s
                """, (pack_id,))
                itens_venda = cursor.fetchall()
                
                if not itens_venda:
                    return None
                
                # Calcula totais (tratando valores None)
                preco_total = sum(float(item['item_preco_total'] or 0) for item in itens_venda if item.get('item_preco_total') is not None)
                taxa_total = sum(float(item.get('taxa_venda', 0) or 0) for item in itens_venda)
                
                # Busca frete da venda ou calcula baseado nos produtos
                frete = float(itens_venda[0].get('frete', 0) or 0)
                if frete == 0:
                    # Se não tem frete na venda, busca frete dos produtos
                    frete_total = 0
                    for item in itens_venda:
                        item_id = item.get('item_id')
                        if item_id:
                            cursor.execute("SELECT frete FROM frete WHERE mlb = %s", (item_id,))
                            frete_item = cursor.fetchone()
                            if frete_item and frete_item[0]:
                                frete_total += float(frete_item[0])
                    frete = frete_total
                
                # Agrupa produtos para exibição
                produtos = []
                for item in itens_venda:
                    produtos.append({
                        'item_id': item['item_id'],
                        'titulo': item['item_titulo'],
                        'quantidade': item['item_quantidade'],
                        'preco_unitario': item['item_preco_und'],
                        'preco_total': item['item_preco_total'],
                        'taxa_venda': item['taxa_venda']
                    })
                
                return {
                    'pack_id': pack_id,
                    'id_venda': pack_id,  # Para compatibilidade
                    'itens': itens_venda,
                    'produtos': produtos,
                    'preco_total': preco_total,
                    'taxa_total': taxa_total,
                    'frete': frete,
                    'quantidade_itens': len(itens_venda),
                    'comprador': itens_venda[0].get('comprador'),
                    'data_aprovacao': itens_venda[0].get('data_aprovacao'),
                    'status': itens_venda[0].get('status')
                }
                
        except Error as e:
            print(f"Erro ao calcular lucratividade: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()
    
    def salvar_pedido_completo(self, dados_pedido: Dict[str, Any], user_id: int) -> bool:
        """Salva pedido com todos os dados relacionados."""
        if not dados_pedido:
            print("❌ Dados do pedido vazios")
            return False
        
        conn = self.conectar()
        if not conn:
            print("❌ Falha na conexão com banco")
            return False
        
        try:
            with conn.cursor() as cursor:
                # Extrai dados do pedido
                order_id = dados_pedido.get('id')
                if not order_id:
                    print("❌ ID do pedido não encontrado")
                    return False
                
                print(f"🛒 Processando pedido: {order_id}")
                
                # Dados básicos do pedido
                seller_id = dados_pedido.get('seller', {}).get('id')
                payment_info = dados_pedido.get('payments', [{}])[0]
                date_approved = payment_info.get('date_approved')
                last_updated = dados_pedido.get('last_updated')
                buyer_nickname = dados_pedido.get('buyer', {}).get('nickname')
                tags_list = dados_pedido.get('tags', [])
                status_str = ",".join(tags_list)
                envio_id = dados_pedido.get('shipping', {}).get('id')
                pack_id = dados_pedido.get('pack_id')  # Novo campo para packs
                
                # Processa cada item do pedido
                order_items = dados_pedido.get('order_items', [])
                print(f"📦 Itens no pedido: {len(order_items)}")
                
                if not order_items:
                    print("⚠️ Pedido sem itens, pulando...")
                    return False
                
                for item in order_items:
                    item_info = item.get('item', {})
                    print(f"  📦 Item: {item_info.get('id')} - {item_info.get('title')}")
                    
                    # Salva no banco
                    cursor.execute("""
                        INSERT INTO orders (user_id, data_aprovacao, data_atualizacao, id_venda, 
                                          item_id, item_titulo, item_quantidade, item_preco_und, 
                                          item_preco_total, taxa_venda, frete, comprador, status, envio_id, pack_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            data_atualizacao = VALUES(data_atualizacao),
                            item_titulo = VALUES(item_titulo),
                            item_quantidade = VALUES(item_quantidade),
                            item_preco_total = VALUES(item_preco_total),
                            taxa_venda = VALUES(taxa_venda),
                            frete = VALUES(frete),
                            status = VALUES(status),
                            pack_id = VALUES(pack_id)
                    """, (
                        user_id, date_approved, last_updated, order_id,
                        item_info.get('id'), item_info.get('title'),
                        item.get('quantity') or 0, item.get('unit_price') or 0,
                        item.get('total_amount') or 0, item.get('sale_fee') or 0,
                        dados_pedido.get('shipping', {}).get('cost', 0) or 0,
                        buyer_nickname, status_str, envio_id, pack_id
                    ))
                
                conn.commit()
                print(f"✅ Pedido {order_id} salvo com sucesso!")
                return True
                
        except Error as e:
            print(f"❌ Erro ao salvar pedido {order_id}: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    def obter_vendas_usuario_filtrado(self, user_id, page, per_page, busca='', data_inicio='', data_fim=''):
        """Obtém vendas do usuário com filtros e paginação agrupadas por packs."""
        try:
            conn = self.conectar()
            cursor = conn.cursor(dictionary=True)
            
            # Construir query base com agrupamento por packs
            query = """
                SELECT 
                    COALESCE(pack_id, id_venda) as pack_id,
                    COUNT(*) as total_produtos,
                    SUM(COALESCE(item_preco_total, 0)) as valor_total,
                    SUM(COALESCE(taxa_venda, 0)) as taxa_total,
                    SUM(COALESCE(frete, 0)) as frete_total,
                    MAX(status) as status,
                    MAX(data_aprovacao) as data_aprovacao,
                    MAX(comprador) as comprador,
                    GROUP_CONCAT(
                        CONCAT(item_titulo, ' (', item_quantidade, 'x)') 
                        SEPARATOR ' | '
                    ) as produtos,
                    GROUP_CONCAT(DISTINCT id_venda) as ids_venda
                FROM vendas v
                LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                WHERE v.user_id = %s
            """
            params = [user_id]
            
            # Adicionar filtros
            if busca:
                query += " AND (id_venda LIKE %s OR item_titulo LIKE %s OR item_id LIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param])
            
            if data_inicio:
                query += " AND DATE(data_aprovacao) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(data_aprovacao) <= %s"
                params.append(data_fim)
            
            # Adicionar agrupamento, ordenação e paginação
            query += " GROUP BY COALESCE(pack_id, id_venda) ORDER BY data_aprovacao DESC LIMIT %s OFFSET %s"
            offset = (page - 1) * per_page
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            vendas = cursor.fetchall()
            
            return vendas
            
        except Exception as e:
            print(f"Erro ao obter vendas filtradas: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()
    
    def contar_vendas_usuario_filtrado(self, user_id, busca='', data_inicio='', data_fim=''):
        """Conta total de packs de vendas do usuário com filtros."""
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Construir query base para contar packs únicos
            query = """
                SELECT COUNT(DISTINCT COALESCE(pack_id, id_venda)) 
                FROM vendas WHERE user_id = %s
            """
            params = [user_id]
            
            # Adicionar filtros
            if busca:
                query += " AND (id_venda LIKE %s OR item_titulo LIKE %s OR item_id LIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param])
            
            if data_inicio:
                query += " AND DATE(data_aprovacao) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(data_aprovacao) <= %s"
                params.append(data_fim)
            
            cursor.execute(query, params)
            total = cursor.fetchone()[0]
            
            return total
            
        except Exception as e:
            print(f"Erro ao contar vendas filtradas: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()
    
    def calcular_totais_vendas_filtradas(self, user_id, busca='', data_inicio='', data_fim=''):
        """Calcula totais de vendas filtradas agrupadas por packs."""
        try:
            conn = self.conectar()
            cursor = conn.cursor()
            
            # Construir query base para packs
            query = """
                SELECT 
                    COUNT(DISTINCT COALESCE(pack_id, id_venda)) as total_vendas,
                    COALESCE(SUM(item_preco_total), 0) as receita_total,
                    COALESCE(SUM(item_quantidade), 0) as itens_vendidos
                FROM vendas v
                LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                WHERE v.user_id = %s
            """
            params = [user_id]
            
            # Adicionar filtros
            if busca:
                query += " AND (id_venda LIKE %s OR item_titulo LIKE %s OR item_id LIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param])
            
            if data_inicio:
                query += " AND DATE(data_aprovacao) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(data_aprovacao) <= %s"
                params.append(data_fim)
            
            print(f"🔢 Calculando totais com query: {query}")
            print(f"🔢 Parâmetros: {params}")
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            if result:
                total_vendas = result[0] or 0
                receita_total = float(result[1] or 0)
                itens_vendidos = result[2] or 0
                ticket_medio = receita_total / total_vendas if total_vendas > 0 else 0
                
                print(f"📊 Totais calculados: {total_vendas} vendas, R$ {receita_total:.2f} receita, {itens_vendidos} itens, R$ {ticket_medio:.2f} ticket médio")
                
                return {
                    'total_vendas': total_vendas,
                    'receita_total': receita_total,
                    'ticket_medio': ticket_medio,
                    'itens_vendidos': itens_vendidos
                }
            else:
                print("📊 Nenhum resultado encontrado para totais")
                return {
                    'total_vendas': 0,
                    'receita_total': 0,
                    'ticket_medio': 0,
                    'itens_vendidos': 0
                }
            
        except Exception as e:
            print(f"❌ Erro ao calcular totais de vendas: {e}")
            return {
                'total_vendas': 0,
                'receita_total': 0,
                'ticket_medio': 0,
                'itens_vendidos': 0
            }
        finally:
            if 'conn' in locals():
                conn.close()
    
    def salvar_categorias_mlb(self, categorias):
        """Salva categorias do Mercado Livre no banco de dados."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Cria tabela de categorias se não existir
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS categorias_mlb(
                        id VARCHAR(25) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Limpa categorias existentes
                cursor.execute("DELETE FROM categorias_mlb")
                
                # Insere novas categorias
                for categoria in categorias:
                    cursor.execute("""
                        INSERT INTO categorias_mlb (id, name) 
                        VALUES (%s, %s)
                    """, (categoria['id'], categoria['name']))
                
                conn.commit()
                print(f"✅ {len(categorias)} categorias salvas no banco de dados")
                return True
                
        except Exception as e:
            print(f"❌ Erro ao salvar categorias: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_categorias_mlb(self):
        """Obtém categorias do Mercado Livre do banco de dados."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id, name FROM categorias_mlb ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            print(f"❌ Erro ao obter categorias: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()

    def salvar_custos_produto(self, user_id: int, mlb: str, custos: dict):
        """Salva os custos de um produto no banco de dados."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Atualiza os custos do produto
            query = """
                UPDATE produtos 
                SET custo_listagem = %s, 
                    custo_venda = %s, 
                    custo_total = %s,
                    imposto = %s,
                    embalagem = %s,
                    custo = %s,
                    extra = %s,
                    data_atualizacao = NOW()
                WHERE user_id = %s AND mlb = %s
            """
            
            cursor.execute(query, (
                custos.get('custo_listagem', 0),
                custos.get('custo_venda', 0),
                custos.get('custo_total', 0),
                custos.get('imposto', 0),
                custos.get('embalagem', 0),
                custos.get('custo', 0),
                custos.get('extra', 0),
                user_id,
                mlb
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar custos do produto {mlb}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def salvar_custos_api_ml(self, mlb: str, custos_data: dict, user_id: int) -> bool:
        """Salva custos da API do Mercado Livre na tabela custos."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Extrai dados da API
            taxa_fixa_list = custos_data.get('listing_fee_details', {}).get('fixed_fee', 0)
            valor_bruto_comissao = custos_data.get('listing_fee_details', {}).get('gross_amount', 0)
            tipo = custos_data.get('listing_type_name', '')
            custos = custos_data.get('sale_fee_amount', 0)
            taxa_fixa_sale = custos_data.get('sale_fee_details', {}).get('fixed_fee', 0)
            bruto_comissao = custos_data.get('sale_fee_details', {}).get('gross_amount', 0)
            porcentagem_comissao = custos_data.get('sale_fee_details', {}).get('percentage_fee', 0)
            
            # Verifica se já existe
            cursor.execute("SELECT mlb FROM custos WHERE mlb = %s", (mlb,))
            if cursor.fetchone():
                # Atualiza
                cursor.execute("""
                    UPDATE custos
                    SET taxa_fixa_list = %s, valor_bruto_comissao = %s, tipo = %s,
                        custos = %s, taxa_fixa_sale = %s, bruto_comissao = %s,
                        porcentagem_da_comissao = %s
                    WHERE mlb = %s
                """, (taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                      taxa_fixa_sale, bruto_comissao, porcentagem_comissao, mlb))
            else:
                # Insere
                cursor.execute("""
                    INSERT INTO custos
                    (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                     taxa_fixa_sale, bruto_comissao, porcentagem_da_comissao)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                """, (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                      taxa_fixa_sale, bruto_comissao, porcentagem_comissao))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar custos da API para {mlb}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def salvar_produto_com_variacoes(self, produto_data: Dict[str, Any], user_id: int) -> bool:
        """Salva um produto e suas variações no banco de dados."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # 1. Salva produto principal
                mlb = produto_data.get('mlb') or produto_data.get('id')
                
                # Validação robusta dos dados essenciais
                if not mlb:
                    print("❌ MLB não encontrado nos dados do produto")
                    return False
                
                title = produto_data.get('title', '').strip()
                if not title:
                    print(f"❌ Título vazio para produto {mlb}")
                    return False
                
                price = float(produto_data.get('price', 0)) if produto_data.get('price') else 0
                regular_price = float(produto_data.get('regular_price', price)) if produto_data.get('regular_price') else price
                available_quantity = int(produto_data.get('available_quantity', 0)) if produto_data.get('available_quantity') else 0
                sold_quantity = int(produto_data.get('sold_quantity', 0)) if produto_data.get('sold_quantity') else 0
                listing_type_id = str(produto_data.get('listing_type_id', '')) if produto_data.get('listing_type_id') else ''
                # Validação do permalink para garantir que seja do Mercado Livre
                permalink_raw = produto_data.get('permalink', '')
                if permalink_raw and 'mercadolivre.com.br' in permalink_raw:
                    permalink = str(permalink_raw)
                else:
                    # Se não for do ML ou estiver vazio, usa o link padrão
                    permalink = f"https://produto.mercadolivre.com.br/{mlb}"
                thumbnail = str(produto_data.get('thumbnail', '')) if produto_data.get('thumbnail') else ''
                frete_gratis = 1 if produto_data.get('shipping', {}).get('free_shipping', False) else 0
                modo_de_envio = str(produto_data.get('shipping', {}).get('mode', '')) if produto_data.get('shipping', {}).get('mode') else ''
                status = str(produto_data.get('status', 'active')) if produto_data.get('status') else 'active'
                category = str(produto_data.get('category_id', '')) if produto_data.get('category_id') else ''
                
                # Processar frete
                valor_frete = 0
                if produto_data.get('frete'):
                    frete_data = produto_data['frete']
                    if frete_data and isinstance(frete_data, dict):
                        valor_frete = frete_data.get("coverage", {}).get("all_country", {}).get("list_cost", 0)
                        if frete_gratis == 0:
                            valor_frete = 0
                
                # Verificar se produto já existe
                cursor.execute("SELECT id FROM produtos WHERE mlb = %s AND user_id = %s", (mlb, user_id))
                produto_existe = cursor.fetchone()
                
                if produto_existe:
                    # Atualiza produto principal
                    cursor.execute("""
                        UPDATE produtos
                        SET title = %s, price = %s, regular_price = %s, 
                            avaliable_quantity = %s, sold_quantity = %s, listing_type_id = %s,
                            permalink = %s, thumbnail = %s, frete_gratis = %s, modo_de_envio = %s,
                            status = %s, category = %s, frete = %s, is_variation = 0,
                            parent_mlb = NULL, variation_attribute = NULL, variation_value = NULL,
                            variation_sku = NULL, updated_at = NOW()
                        WHERE mlb = %s AND user_id = %s
                    """, (title, price, regular_price, available_quantity, sold_quantity,
                          listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                          status, category, valor_frete, mlb, user_id))
                else:
                    # Insere produto principal
                    cursor.execute("""
                        INSERT INTO produtos
                        (mlb, title, price, regular_price, avaliable_quantity, sold_quantity,
                         listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                         status, category, frete, is_variation, parent_mlb, variation_attribute,
                         variation_value, variation_sku, user_id)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, NULL, NULL, NULL, NULL, %s)
                    """, (mlb, title, price, regular_price, available_quantity, sold_quantity,
                          listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                          status, category, valor_frete, user_id))
                
                # 2. Salva variações se existirem
                variations = produto_data.get('variations', [])
                if variations:
                    for variation in variations:
                        variation_mlb = f"{mlb}-{str(variation.get('id', ''))[-8:]}"
                        variation_title = f"{title} - {variation.get('variation_value', '')}"
                        variation_price = variation.get('price', price)
                        variation_quantity = variation.get('available_quantity', 0)
                        variation_sold = variation.get('sold_quantity', 0)
                        variation_sku = variation.get('variation_sku', '')
                        variation_attribute = variation.get('variation_attribute', '')
                        variation_value = variation.get('variation_value', '')
                        
                        # Verificar se variação já existe
                        cursor.execute("SELECT id FROM produtos WHERE mlb = %s AND user_id = %s", (variation_mlb, user_id))
                        variacao_existe = cursor.fetchone()
                        
                        if variacao_existe:
                            # Atualiza variação
                            cursor.execute("""
                                UPDATE produtos
                                SET title = %s, price = %s, regular_price = %s,
                                    avaliable_quantity = %s, sold_quantity = %s,
                                    variation_attribute = %s, variation_value = %s,
                                    variation_sku = %s, updated_at = NOW()
                                WHERE mlb = %s AND user_id = %s
                            """, (variation_title, variation_price, variation_price,
                                  variation_quantity, variation_sold, variation_attribute,
                                  variation_value, variation_sku, variation_mlb, user_id))
                        else:
                            # Insere variação
                            cursor.execute("""
                                INSERT INTO produtos
                                (mlb, title, price, regular_price, avaliable_quantity, sold_quantity,
                                 listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                                 status, category, frete, is_variation, parent_mlb, variation_attribute,
                                 variation_value, variation_sku, user_id)
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s, %s, %s, %s)
                            """, (variation_mlb, variation_title, variation_price, variation_price,
                                  variation_quantity, variation_sold, listing_type_id, permalink,
                                  thumbnail, frete_gratis, modo_de_envio, status, category, valor_frete,
                                  mlb, variation_attribute, variation_value, variation_sku, user_id))
                
                conn.commit()
                return True
                
        except Error as e:
            print(f"Erro ao salvar produto com variações: {e}")
            conn.rollback()
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def salvar_produtos_lote(self, dados_lote: List[Dict[str, Any]], user_id: int) -> bool:
        """Salva múltiplos produtos de uma vez - ULTRA OTIMIZADO."""
        if not dados_lote:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            conn.autocommit = False
            with conn.cursor() as cursor:
                for dados_completos in dados_lote:
                    if not dados_completos or not dados_completos.get('produto'):
                        continue
                    
                    produto_data = dados_completos['produto']
                    sugestao_data = dados_completos.get('sugestao')
                    custos_data = dados_completos.get('custos')
                    frete_data = dados_completos.get('frete')
                    
                    mlb = produto_data.get('id')
                    if not mlb:
                        continue
                    
                    # 1. Salva dados básicos do produto
                    title = produto_data.get('title')
                    sku = None
                    for attr in produto_data.get('attributes', []):
                        if attr.get("id") == "SELLER_SKU":
                            sku_value = attr.get("value_name")
                            if sku_value and sku_value.isdigit():
                                sku = int(sku_value)
                            break
                    
                    price = produto_data.get('price', 0)
                    regular_price = dados_completos.get('preco_regular') or produto_data.get('price', 0)
                    available_quantity = produto_data.get('available_quantity')
                    sold_quantity = produto_data.get('sold_quantity')
                    listing_type_id = produto_data.get('listing_type_id')
                    permalink = produto_data.get('permalink')
                    thumbnail = produto_data.get('thumbnail')
                    frete_gratis = 1 if produto_data.get('shipping', {}).get('free_shipping', False) else 0
                    modo_de_envio = produto_data.get('shipping', {}).get('mode')
                    status = produto_data.get('status')
                    category = produto_data.get('category_id')
                    
                    # Calcula valor do frete (seguindo lógica do save)
                    valor_frete = 0
                    if frete_data:
                        valor_frete = frete_data.get("coverage", {}).get("all_country", {}).get("list_cost", 0)
                        # Se frete_gratis = 0, força frete = 0 (Frete Grátis) - igual ao save
                        if frete_gratis == 0:
                            valor_frete = 0
                    
                    # Verifica se produto já existe
                    cursor.execute("SELECT mlb FROM produtos WHERE mlb = %s", (mlb,))
                    if cursor.fetchone():
                        # Atualiza
                        cursor.execute("""
                            UPDATE produtos
                            SET title = %s, sku = %s, price = %s, regular_price = %s, 
                                avaliable_quantity = %s, sold_quantity = %s, listing_type_id = %s,
                                permalink = %s, thumbnail = %s, frete_gratis = %s, modo_de_envio = %s,
                                status = %s, category = %s, frete = %s, updated_at = NOW()
                            WHERE mlb = %s
                        """, (title, sku, price, regular_price, available_quantity, sold_quantity,
                              listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                              status, category, valor_frete, mlb))
                    else:
                        # Insere
                        cursor.execute("""
                            INSERT INTO produtos
                            (mlb, title, sku, price, regular_price, avaliable_quantity, sold_quantity,
                             listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                             status, category, frete, user_id)
                            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (mlb, title, sku, price, regular_price, available_quantity, sold_quantity,
                              listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                              status, category, valor_frete, user_id))
                    
                    # 2. Salva sugestões de preço (se disponível)
                    if sugestao_data:
                        preco_atual = sugestao_data.get("current_price", {}).get("amount", price)
                        sugestao = sugestao_data.get("suggested_price", {}).get("amount")
                        menor_preco = sugestao_data.get("lowest_price", {}).get("amount")
                        custo_venda = sugestao_data.get("costs", {}).get("selling_fees")
                        custo_envio = sugestao_data.get("costs", {}).get("shipping_fees")
                        
                        cursor.execute("SELECT mlb FROM sugestao_preco WHERE mlb = %s", (mlb,))
                        if cursor.fetchone():
                            cursor.execute("""
                                UPDATE sugestao_preco
                                SET preco = %s, sugestao = %s, menor_preco = %s,
                                    custo_venda = %s, custo_envio = %s, data = NOW()
                                WHERE mlb = %s
                            """, (preco_atual, sugestao, menor_preco, custo_venda, custo_envio, mlb))
                        else:
                            cursor.execute("""
                                INSERT INTO sugestao_preco
                                (mlb, preco, sugestao, menor_preco, custo_venda, custo_envio, data)
                                VALUES(%s, %s, %s, %s, %s, %s, NOW())
                            """, (mlb, preco_atual, sugestao, menor_preco, custo_venda, custo_envio))
                    
                    # 3. Salva custos (se disponível)
                    if custos_data:
                        taxa_fixa_list = custos_data.get('listing_fee_details', {}).get('fixed_fee')
                        valor_bruto_comissao = custos_data.get('listing_fee_details', {}).get('gross_amount')
                        tipo = custos_data.get('listing_type_name')
                        custos = custos_data.get('sale_fee_amount')
                        taxa_fixa_sale = custos_data.get('sale_fee_details', {}).get('fixed_fee')
                        bruto_comissao = custos_data.get('sale_fee_details', {}).get('gross_amount')
                        porcentagem_comissao = custos_data.get('sale_fee_details', {}).get('percentage_fee')
                        
                        cursor.execute("SELECT mlb FROM custos WHERE mlb = %s", (mlb,))
                        if cursor.fetchone():
                            cursor.execute("""
                                UPDATE custos
                                SET taxa_fixa_list = %s, valor_bruto_comissao = %s, tipo = %s,
                                    custos = %s, taxa_fixa_sale = %s, bruto_comissao = %s,
                                    porcentagem_da_comissao = %s
                                WHERE mlb = %s
                            """, (taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                                  taxa_fixa_sale, bruto_comissao, porcentagem_comissao, mlb))
                        else:
                            cursor.execute("""
                                INSERT INTO custos
                                (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                                 taxa_fixa_sale, bruto_comissao, porcentagem_da_comissao)
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                            """, (mlb, taxa_fixa_list, valor_bruto_comissao, tipo, custos,
                                  taxa_fixa_sale, bruto_comissao, porcentagem_comissao))
                    
                    # 4. Salva frete (se disponível)
                    if frete_data:
                        valor_frete = frete_data.get("coverage", {}).get("all_country", {}).get("list_cost", 0)
                        peso = frete_data.get("coverage", {}).get("all_country", {}).get("billable_weight")
                        
                        if frete_gratis:
                            valor_frete = 0
                        
                        cursor.execute("SELECT mlb FROM frete WHERE mlb = %s", (mlb,))
                        if cursor.fetchone():
                            cursor.execute("""
                                UPDATE frete SET frete = %s, peso = %s WHERE mlb = %s
                            """, (valor_frete, peso, mlb))
                        else:
                            cursor.execute("""
                                INSERT INTO frete (mlb, frete, peso) VALUES(%s, %s, %s)
                            """, (mlb, valor_frete, peso))
                    
                    # 5. Salva variações se existirem
                    variations = dados_completos.get('variations', [])
                    if variations:
                        for variation in variations:
                            variation_mlb = f"{mlb}-{str(variation.get('id', ''))[-8:]}"
                            variation_title = f"{title} - {variation.get('variation_value', '')}"
                            variation_price = variation.get('price', price)
                            variation_quantity = variation.get('available_quantity', 0)
                            variation_sold = variation.get('sold_quantity', 0)
                            variation_sku = variation.get('variation_sku', '')
                            variation_attribute = variation.get('variation_attribute', '')
                            variation_value = variation.get('variation_value', '')
                            
                            # Verificar se variação já existe
                            cursor.execute("SELECT mlb FROM produtos WHERE mlb = %s", (variation_mlb,))
                            if cursor.fetchone():
                                # Atualiza variação
                                cursor.execute("""
                                    UPDATE produtos
                                    SET title = %s, price = %s, regular_price = %s,
                                        avaliable_quantity = %s, sold_quantity = %s,
                                        variation_attribute = %s, variation_value = %s,
                                        variation_sku = %s, updated_at = NOW()
                                    WHERE mlb = %s
                                """, (variation_title, variation_price, variation_price,
                                      variation_quantity, variation_sold, variation_attribute,
                                      variation_value, variation_sku, variation_mlb))
                            else:
                                # Insere variação
                                cursor.execute("""
                                    INSERT INTO produtos
                                    (mlb, title, price, regular_price, avaliable_quantity, sold_quantity,
                                     listing_type_id, permalink, thumbnail, frete_gratis, modo_de_envio,
                                     status, category, frete, is_variation, parent_mlb, variation_attribute,
                                     variation_value, variation_sku, user_id)
                                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s, %s, %s, %s)
                                """, (variation_mlb, variation_title, variation_price, variation_price,
                                      variation_quantity, variation_sold, listing_type_id, permalink,
                                      thumbnail, frete_gratis, modo_de_envio, status, category, valor_frete,
                                      mlb, variation_attribute, variation_value, variation_sku, user_id))
                
                # Commit da transação
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao salvar lote de produtos: {e}")
            conn.rollback()
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def salvar_custos_venda(self, pack_id: str, mlb: str, custos: dict) -> bool:
        """Salva custos específicos de uma venda (pack)."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Insere ou atualiza custos da venda
            cursor.execute("""
                INSERT INTO custos_vendas (pack_id, mlb, imposto, embalagem, custo, extra)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                imposto = VALUES(imposto),
                embalagem = VALUES(embalagem),
                custo = VALUES(custo),
                extra = VALUES(extra),
                data_atualizacao = CURRENT_TIMESTAMP
            """, (
                pack_id,
                mlb,
                custos.get('imposto', 0),
                custos.get('embalagem', 0),
                custos.get('custo', 0),
                custos.get('extra', 0)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar custos da venda {pack_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def obter_custos_venda(self, pack_id: str, mlb: str = None) -> dict:
        """Obtém custos específicos de uma venda (pack)."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            if mlb:
                # Busca custos de um produto específico na venda
                cursor.execute("""
                    SELECT imposto, embalagem, custo, extra
                    FROM custos_vendas
                    WHERE pack_id = %s AND mlb = %s
                """, (pack_id, mlb))
            else:
                # Busca todos os custos da venda
                cursor.execute("""
                    SELECT mlb, imposto, embalagem, custo, extra
                    FROM custos_vendas
                    WHERE pack_id = %s
                """, (pack_id,))
            
            if mlb:
                result = cursor.fetchone()
                return result if result else {}
            else:
                return {row['mlb']: row for row in cursor.fetchall()}
                
        except Exception as e:
            print(f"Erro ao obter custos da venda {pack_id}: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def obter_custos_produto_para_venda(self, mlb: str, pack_id: str = None) -> dict:
        """Obtém custos de um produto, priorizando custos específicos da venda se existirem."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Primeiro tenta buscar custos específicos da venda
            if pack_id:
                cursor.execute("""
                    SELECT imposto, embalagem, custo, extra
                    FROM custos_vendas
                    WHERE pack_id = %s AND mlb = %s
                """, (pack_id, mlb))
                custos_venda = cursor.fetchone()
                
                if custos_venda:
                    return custos_venda
            
            # Se não encontrar custos específicos da venda, busca custos padrão do produto
            cursor.execute("""
                SELECT imposto, embalagem, custo, extra
                FROM produtos
                WHERE mlb = %s
            """, (mlb,))
            custos_produto = cursor.fetchone()
            
            return custos_produto if custos_produto else {}
                
        except Exception as e:
            print(f"Erro ao obter custos do produto {mlb}: {e}")
            return {}
        finally:
            if conn:
                conn.close()

    def salvar_frete_envio_vendas(self, fretes_por_pack: Dict[str, Any]) -> bool:
        """Salva fretes de envio das vendas no banco de dados."""
        if not fretes_por_pack:
            return False
        
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            for pack_id, frete_valor in fretes_por_pack.items():
                if frete_valor is not None:
                    # Atualiza frete na tabela vendas para todas as vendas do pack
                    cursor.execute("""
                        UPDATE vendas 
                        SET frete_total = %s 
                        WHERE pack_id = %s
                    """, (frete_valor, pack_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Erro ao salvar fretes de envio: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def salvar_pedido(self, pedido_data: dict, user_id: int) -> bool:
        """Salva ou atualiza um pedido no banco de dados."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Extrair dados do pedido
                order_id = pedido_data.get('id')
                status = pedido_data.get('status', 'unknown')
                date_created = pedido_data.get('date_created', '')
                date_approved = pedido_data.get('date_approved', '')
                total_amount = pedido_data.get('total_amount', 0)
                
                # Dados do comprador
                buyer = pedido_data.get('buyer', {})
                buyer_id = buyer.get('id', '')
                buyer_nickname = buyer.get('nickname', '')
                
                # Dados do envio
                shipping = pedido_data.get('shipping', {})
                envio_id = shipping.get('id', '')
                frete_valor = shipping.get('cost', 0)
                
                # Função removida - usando apenas tabela vendas
                pass
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao salvar pedido {order_id}: {e}")
            conn.rollback()
            return False
        finally:
            if conn.is_connected():
                conn.close()

    def salvar_sugestao_preco(self, mlb: str, sugestao_data: dict, user_id: int) -> bool:
        """Salva ou atualiza sugestão de preço de um produto."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Extrair dados da sugestão
                preco_atual = sugestao_data.get('current_price', {}).get('amount', 0)
                sugestao = sugestao_data.get('suggested_price', {}).get('amount', 0)
                menor_preco = sugestao_data.get('lowest_price', {}).get('amount', 0)
                custo_venda = sugestao_data.get('costs', {}).get('selling_fees', 0)
                custo_envio = sugestao_data.get('costs', {}).get('shipping_fees', 0)
                
                # Verificar se sugestão já existe
                cursor.execute("SELECT mlb FROM sugestoes_preco WHERE mlb = %s", (mlb,))
                if cursor.fetchone():
                    # Atualizar sugestão existente
                    cursor.execute("""
                        UPDATE sugestoes_preco SET 
                            preco_atual = %s, sugestao = %s, menor_preco = %s,
                            custo_venda = %s, custo_envio = %s, updated_at = NOW()
                        WHERE mlb = %s
                    """, (preco_atual, sugestao, menor_preco, custo_venda, custo_envio, mlb))
                else:
                    # Inserir nova sugestão
                    cursor.execute("""
                        INSERT INTO sugestoes_preco (mlb, user_id, preco_atual, sugestao, 
                                                   menor_preco, custo_venda, custo_envio)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (mlb, user_id, preco_atual, sugestao, menor_preco, custo_venda, custo_envio))
                
                conn.commit()
                return True

        except Exception as e:
            print(f"Erro ao salvar sugestão de preço {mlb}: {e}")
            conn.rollback()
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def _calcular_margem_produto(self, mlb: str, user_id: int) -> float:
        """Calcula a margem líquida de um produto usando a mesma lógica do profitability.py."""
        conn = self.conectar()
        if not conn:
            return 0.0
        
        try:
            with conn.cursor() as cursor:
                # Buscar dados do produto (mesma query do profitability.py)
                cursor.execute("""
                    SELECT price, frete, frete_gratis, custo_listagem, custo_venda, imposto, embalagem, custo, extra
                    FROM produtos 
                    WHERE mlb = %s AND user_id = %s
                """, (mlb, user_id))
                
                result = cursor.fetchone()
                if not result:
                    return 0.0
                
                price, frete, frete_gratis, custo_listagem, custo_venda, imposto, embalagem, custo, extra = result
                if not price or price <= 0:
                    return 0.0
                
                # Converter para float
                price = float(price)
                frete = float(frete) if frete else 0
                frete_gratis = int(frete_gratis) if frete_gratis else 0
                custo_listagem = float(custo_listagem) if custo_listagem else 0
                custo_venda = float(custo_venda) if custo_venda else 0
                imposto_perc = float(imposto) if imposto else 0
                embalagem = float(embalagem) if embalagem else 0
                custo_produto = float(custo) if custo else 0
                extra = float(extra) if extra else 0
                
                # Buscar custos adicionais da tabela custos (se não houver na tabela produtos)
                if imposto_perc == 0 and embalagem == 0 and custo_produto == 0 and extra == 0:
                    cursor.execute("""
                        SELECT imposto, embalagem, custo, extra
                        FROM custos 
                        WHERE mlb = %s
                    """, (mlb,))
                    custos_result = cursor.fetchone()
                    if custos_result:
                        imposto_perc, embalagem, custo_produto, extra = custos_result
                        imposto_perc = float(imposto_perc) if imposto_perc else 0
                        embalagem = float(embalagem) if embalagem else 0
                        custo_produto = float(custo_produto) if custo_produto else 0
                        extra = float(extra) if extra else 0
                
                # Não aplicar valores padrão - usar 0 se não houver valor
                
                # Buscar custos do Mercado Livre da tabela custos (mesma lógica do profitability.py)
                cursor.execute("""
                    SELECT custos FROM custos WHERE mlb = %s
                """, (mlb,))
                custos_ml_result = cursor.fetchone()
                custos_ml = float(custos_ml_result[0]) if custos_ml_result and custos_ml_result[0] else 0
                
                # Se não encontrar na tabela custos, usa 10% como fallback
                if custos_ml == 0:
                    custos_ml = price * 0.10
                
                # Frete é sempre considerado como custo para o vendedor
                # frete_gratis = 1 significa que o cliente não paga, mas o vendedor sim
                
                # Cálculos (mesma lógica do profitability.py)
                base_imposto = price - frete - custos_ml
                imposto_valor = float(imposto_perc / 100) * base_imposto if imposto_perc > 0 else 0
                
                custo_total = custo_produto + embalagem + custos_ml + imposto_valor + frete + extra
                lucro_bruto = price - custo_total
                margem_liquida = (lucro_bruto / price) * 100 if price > 0 else 0
                
                return round(margem_liquida, 1)
                
        except Exception as e:
            print(f"Erro ao calcular margem do produto {mlb}: {e}")
            return 0.0
        finally:
            if conn.is_connected():
                conn.close()

    # ==================== NOVAS FUNÇÕES DE VENDAS ====================
    
    def salvar_venda_completa(self, dados_venda: Dict[str, Any], user_id: int) -> bool:
        """Salva uma venda completa com todos os dados (compatibilidade com importação)."""
        # Usar a função salvar_venda_com_status que é mais completa
        return self.salvar_venda_com_status(dados_venda, user_id)
    
    def _funcao_removida(self, dados_venda: Dict[str, Any], user_id: int) -> bool:
        """Salva uma venda completa com todos os dados."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            venda_id = dados_venda.get('id', '')
            if not venda_id:
                print("❌ Venda sem ID, ignorando...")
                return False
            
            # Dados da venda principal
            pack_id = dados_venda.get('pack_id', '')
            data_aprovacao = dados_venda.get('date_approved', '') or dados_venda.get('date_created', '')
            data_criacao = dados_venda.get('date_created', '') or dados_venda.get('date_approved', '')
            
            # Converte datas vazias para None
            if not data_aprovacao:
                data_aprovacao = None
            if not data_criacao:
                data_criacao = None
            buyer = dados_venda.get('buyer', {})
            comprador_id = buyer.get('id', '')
            comprador_nome = buyer.get('nickname', '')
            comprador_email = buyer.get('email', '')
            status = dados_venda.get('status', '')
            payment = dados_venda.get('payment', {})
            payment_method = payment.get('payment_method_id', '')
            shipping = dados_venda.get('shipping', {})
            shipping_method = shipping.get('method', '')
            
            # Calcula totais
            order_items = dados_venda.get('order_items', [])
            valor_total = 0
            taxa_ml = 0
            frete_total = 0
            total_produtos = 0
            
            # Calcula valor total dos produtos
            for item in order_items:
                preco_unit = float(item.get('unit_price', 0))
                quantidade = int(item.get('quantity', 1))
                preco_total = preco_unit * quantidade
                valor_total += preco_total
                total_produtos += quantidade
            
            # Obtém dados reais de frete e taxas
            frete_total = float(shipping.get('cost', 0))
            
            # Calcula taxa ML baseada nos dados disponíveis
            billing = dados_venda.get('billing_info', {})
            taxa_ml = 0
            
            if billing:
                # Taxa de venda (commission)
                commission = billing.get('commission', {})
                if commission:
                    taxa_ml = float(commission.get('total', 0))
                else:
                    # Fallback: calcula baseado nos itens
                    for item in order_items:
                        item_commission = item.get('commission', {})
                        if item_commission:
                            taxa_ml += float(item_commission.get('total', 0))
                        else:
                            # Taxa aproximada por item
                            preco_unit = float(item.get('unit_price', 0))
                            quantidade = int(item.get('quantity', 1))
                            preco_total = preco_unit * quantidade
                            taxa_ml += preco_total * 0.10  # 10% aproximado
            else:
                # Calcula taxa ML baseada na categoria e valor
                # Taxas reais do Mercado Livre por categoria (2024)
                for item in order_items:
                    preco_unit = float(item.get('unit_price', 0))
                    quantidade = int(item.get('quantity', 1))
                    preco_total = preco_unit * quantidade
                    
                    # Obtém categoria do item
                    categoria_id = item.get('item', {}).get('category_id', '')
                    categoria_nome = item.get('item', {}).get('category_name', '').lower()
                    
                    # Taxa baseada na categoria (valores reais do ML 2024)
                    taxa_item = 0
                    
                    # Categorias específicas com taxas conhecidas
                    if 'eletrônicos' in categoria_nome or 'eletronicos' in categoria_nome or categoria_id.startswith('MLB1000'):
                        taxa_item = preco_total * 0.19  # 19% - Eletrônicos
                    elif 'casa' in categoria_nome or 'jardim' in categoria_nome or categoria_id.startswith('MLB1003'):
                        taxa_item = preco_total * 0.14  # 14% - Casa e Jardim
                    elif 'moda' in categoria_nome or 'roupas' in categoria_nome or categoria_id.startswith('MLB1005'):
                        taxa_item = preco_total * 0.19  # 19% - Moda
                    elif 'esportes' in categoria_nome or 'fitness' in categoria_nome or categoria_id.startswith('MLB1007'):
                        taxa_item = preco_total * 0.14  # 14% - Esportes
                    elif 'livros' in categoria_nome or 'livro' in categoria_nome or categoria_id.startswith('MLB1009'):
                        taxa_item = preco_total * 0.10  # 10% - Livros
                    elif 'bebidas' in categoria_nome or 'vinho' in categoria_nome or 'cerveja' in categoria_nome:
                        taxa_item = preco_total * 0.14  # 14% - Bebidas
                    elif 'alimentação' in categoria_nome or 'alimentacao' in categoria_nome or 'comida' in categoria_nome:
                        taxa_item = preco_total * 0.14  # 14% - Alimentação
                    elif 'beleza' in categoria_nome or 'cosméticos' in categoria_nome or 'cosmeticos' in categoria_nome:
                        taxa_item = preco_total * 0.19  # 19% - Beleza
                    elif 'brinquedos' in categoria_nome or 'jogos' in categoria_nome:
                        taxa_item = preco_total * 0.14  # 14% - Brinquedos
                    elif 'automotivo' in categoria_nome or 'carro' in categoria_nome:
                        taxa_item = preco_total * 0.14  # 14% - Automotivo
                    else:
                        # Taxa baseada no valor do produto (fallback)
                        if preco_total <= 30:
                            taxa_item = preco_total * 0.12  # 12% para produtos muito baratos
                        elif preco_total <= 100:
                            taxa_item = preco_total * 0.14  # 14% para produtos baratos
                        elif preco_total <= 300:
                            taxa_item = preco_total * 0.16  # 16% para produtos médios
                        elif preco_total <= 1000:
                            taxa_item = preco_total * 0.18  # 18% para produtos caros
                        else:
                            taxa_item = preco_total * 0.19  # 19% para produtos muito caros
                    
                    taxa_ml += taxa_item
            
            # Insere venda principal
            cursor.execute("""
                INSERT INTO vendas (
                    user_id, venda_id, pack_id, data_aprovacao, data_criacao,
                    comprador_id, comprador_nome, comprador_email, status,
                    valor_total, taxa_ml, frete_total, total_produtos,
                    payment_method, shipping_method
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    pack_id = VALUES(pack_id),
                    data_aprovacao = VALUES(data_aprovacao),
                    data_criacao = VALUES(data_criacao),
                    comprador_id = VALUES(comprador_id),
                    comprador_nome = VALUES(comprador_nome),
                    comprador_email = VALUES(comprador_email),
                    status = VALUES(status),
                    valor_total = VALUES(valor_total),
                    taxa_ml = VALUES(taxa_ml),
                    frete_total = VALUES(frete_total),
                    total_produtos = VALUES(total_produtos),
                    payment_method = VALUES(payment_method),
                    shipping_method = VALUES(shipping_method),
                    updated_at = CURRENT_TIMESTAMP
            """, (
                user_id, venda_id, pack_id, data_aprovacao, data_criacao,
                comprador_id, comprador_nome, comprador_email, status,
                valor_total, taxa_ml, frete_total, total_produtos,
                payment_method, shipping_method
            ))
            
            # Remove itens antigos da venda
            cursor.execute("DELETE FROM venda_itens WHERE venda_id = %s AND user_id = %s", (venda_id, user_id))
            
            # Insere itens da venda
            for item in order_items:
                item_id = item.get('item', {}).get('id', '')
                item_titulo = item.get('item', {}).get('title', '')
                item_mlb = item.get('item', {}).get('id', '')
                quantidade = int(item.get('quantity', 1))
                preco_unitario = float(item.get('unit_price', 0))
                preco_total = preco_unitario * quantidade
                
                # Categoria
                categoria_id = item.get('item', {}).get('category_id', '')
                categoria_nome = item.get('item', {}).get('category_name', '')
                
                # Variação
                variacao = item.get('item', {}).get('variation', {})
                variacao_id = variacao.get('id', '')
                variacao_nome = variacao.get('name', '')
                
                cursor.execute("""
                    INSERT INTO venda_itens (
                        venda_id, user_id, item_id, item_titulo, item_mlb,
                        quantidade, preco_unitario, preco_total,
                        categoria_id, categoria_nome, variacao_id, variacao_nome
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    venda_id, user_id, item_id, item_titulo, item_mlb,
                    quantidade, preco_unitario, preco_total,
                    categoria_id, categoria_nome, variacao_id, variacao_nome
                ))
            
            # Insere dados de frete se disponível
            if shipping and frete_total > 0:
                frete_id = shipping.get('id', '')
                prazo_entrega = shipping.get('estimated_delivery_time', {}).get('date', '')
                # Converte prazo_entrega para int ou None se vazio
                if prazo_entrega and prazo_entrega.strip():
                    try:
                        prazo_entrega = int(prazo_entrega)
                    except (ValueError, TypeError):
                        prazo_entrega = None
                else:
                    prazo_entrega = None
                peso_total = float(shipping.get('weight', 0))
                dimensoes = f"{shipping.get('dimensions', {}).get('length', 0)}x{shipping.get('dimensions', {}).get('width', 0)}x{shipping.get('dimensions', {}).get('height', 0)}"
                rastreamento = shipping.get('tracking_number', '')
                status_envio = shipping.get('status', '')
                
                cursor.execute("""
                    INSERT INTO venda_fretes (
                        venda_id, user_id, frete_id, metodo_envio, prazo_entrega,
                        valor_frete, peso_total, dimensoes, rastreamento, status_envio
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        metodo_envio = VALUES(metodo_envio),
                        prazo_entrega = VALUES(prazo_entrega),
                        valor_frete = VALUES(valor_frete),
                        peso_total = VALUES(peso_total),
                        dimensoes = VALUES(dimensoes),
                        rastreamento = VALUES(rastreamento),
                        status_envio = VALUES(status_envio)
                """, (
                    venda_id, user_id, frete_id, shipping_method, prazo_entrega,
                    frete_total, peso_total, dimensoes, rastreamento, status_envio
                ))
            
            # Insere dados de pagamento se disponível
            if payment:
                payment_id = payment.get('id', '')
                status_pagamento = payment.get('status', '')
                valor_pago = float(payment.get('total_paid_amount', 0))
                data_pagamento = payment.get('date_paid', '')
                data_aprovacao_pag = payment.get('date_approved', '')
                
                # Converte datas vazias para None
                if not data_pagamento or data_pagamento.strip() == '':
                    data_pagamento = None
                if not data_aprovacao_pag or data_aprovacao_pag.strip() == '':
                    data_aprovacao_pag = None
                taxa_pagamento = float(payment.get('transaction_amount', {}).get('fees', 0))
                parcelas = int(payment.get('installments', 1))
                
                # Dados do pagamento em JSON
                dados_pagamento = {
                    'payment_method_id': payment_method,
                    'payment_type_id': payment.get('payment_type_id', ''),
                    'status_detail': payment.get('status_detail', ''),
                    'currency_id': payment.get('currency_id', 'BRL')
                }
                
                cursor.execute("""
                    INSERT INTO venda_pagamentos (
                        venda_id, user_id, payment_id, metodo_pagamento, status_pagamento,
                        valor_pago, data_pagamento, data_aprovacao, taxa_pagamento,
                        parcelas, dados_pagamento
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        metodo_pagamento = VALUES(metodo_pagamento),
                        status_pagamento = VALUES(status_pagamento),
                        valor_pago = VALUES(valor_pago),
                        data_pagamento = VALUES(data_pagamento),
                        data_aprovacao = VALUES(data_aprovacao),
                        taxa_pagamento = VALUES(taxa_pagamento),
                        parcelas = VALUES(parcelas),
                        dados_pagamento = VALUES(dados_pagamento)
                """, (
                    venda_id, user_id, payment_id, payment_method, status_pagamento,
                    valor_pago, data_pagamento, data_aprovacao_pag, taxa_pagamento,
                    parcelas, json.dumps(dados_pagamento)
                ))
            
            conn.commit()
            return True
            
        except Error as e:
            print(f"❌ Erro ao salvar venda {venda_id}: {e}")
            return False
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_vendas_usuario_novo(self, user_id: int, page: int = 1, per_page: int = 50, 
                                 busca: str = '', data_inicio: str = '', data_fim: str = '', 
                                 status_pagamento: str = '', status_envio: str = '') -> List[Dict[str, Any]]:
        """Obtém vendas do usuário agrupadas por pack_id com filtros e paginação."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Query base - agrupa por pack_id
            query = """
                SELECT 
                    COALESCE(v.pack_id, v.venda_id) as pack_id,
                    COALESCE(v.pack_id, v.venda_id) as pack_id_original,
                    MIN(v.data_aprovacao) as data_aprovacao,
                    MIN(v.data_criacao) as data_criacao,
                    MIN(v.comprador_nome) as comprador_nome,
                    MIN(v.status) as status,
                    SUM(v.valor_total) as valor_total,
                    SUM(v.taxa_ml) as taxa_ml,
                    MIN(v.status_pagamento) as status_pagamento,
                    MIN(v.status_envio) as status_envio,
                    MIN(v.status_pagamento_pt) as status_pagamento_pt,
                    MIN(v.status_envio_pt) as status_envio_pt,
                    MIN(v.payment_method_pt) as payment_method_pt,
                    MIN(v.shipping_method_pt) as shipping_method_pt,
                    MIN(v.data_envio) as data_envio,
                    MIN(v.data_entrega) as data_entrega,
                    MIN(v.codigo_rastreamento) as codigo_rastreamento,
                    MIN(v.transportadora) as transportadora,
                    MIN(v.observacoes) as observacoes,
                    MAX(v.ultima_atualizacao) as ultima_atualizacao,
                    SUM(v.frete_total) as frete_total,
                    SUM(v.total_produtos) as total_produtos,
                    MIN(v.payment_method) as payment_method,
                    MIN(v.shipping_method) as shipping_method,
                    MIN(v.created_at) as created_at,
                    MAX(v.updated_at) as updated_at,
                    COUNT(DISTINCT v.venda_id) as total_vendas,
                    COUNT(DISTINCT vi.item_mlb) as total_mlbs,
                    GROUP_CONCAT(
                        CONCAT(vi.item_titulo, ' (', vi.quantidade, 'x)') 
                        ORDER BY v.data_aprovacao, v.venda_id
                        SEPARATOR ' | '
                    ) as produtos,
                    GROUP_CONCAT(DISTINCT vi.item_mlb ORDER BY vi.item_mlb) as mlbs,
                    GROUP_CONCAT(DISTINCT v.venda_id ORDER BY v.venda_id) as venda_ids
                FROM vendas v
                LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                WHERE v.user_id = %s
            """
            params = [user_id]
            
            # Adicionar filtros
            if busca:
                query += " AND (v.venda_id LIKE %s OR v.pack_id LIKE %s OR v.comprador_nome LIKE %s OR vi.item_titulo LIKE %s OR vi.item_mlb LIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param, busca_param, busca_param])
            
            if data_inicio:
                query += " AND DATE(v.data_aprovacao) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(v.data_aprovacao) <= %s"
                params.append(data_fim)
            
            if status_pagamento:
                query += " AND v.status_pagamento = %s"
                params.append(status_pagamento)
            
            if status_envio:
                query += " AND v.status_envio = %s"
                params.append(status_envio)
            
            # Agrupamento e ordenação por pack
            query += " GROUP BY COALESCE(v.pack_id, v.venda_id) ORDER BY MIN(v.data_aprovacao) DESC"
            
            # Paginação
            offset = (page - 1) * per_page
            query += " LIMIT %s OFFSET %s"
            params.extend([per_page, offset])
            
            cursor.execute(query, params)
            vendas = cursor.fetchall()
            
            # Converte Decimal para float
            for venda in vendas:
                if venda['valor_total']:
                    venda['valor_total'] = float(venda['valor_total'])
                if venda['taxa_ml']:
                    venda['taxa_ml'] = float(venda['taxa_ml'])
                if venda['frete_total']:
                    venda['frete_total'] = float(venda['frete_total'])
            
            return vendas
            
        except Error as e:
            print(f"❌ Erro ao buscar vendas: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def contar_vendas_usuario_novo(self, user_id: int, busca: str = '', 
                                  data_inicio: str = '', data_fim: str = '', 
                                  status_pagamento: str = '', status_envio: str = '') -> int:
        """Conta packs de vendas do usuário com filtros (nova estrutura)."""
        conn = self.conectar()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT COUNT(*) FROM (
                    SELECT COALESCE(v.pack_id, v.venda_id) as pack_id
                    FROM vendas v 
                    LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                    WHERE v.user_id = %s
            """
            params = [user_id]
            
            if busca:
                query += " AND (v.venda_id LIKE %s OR v.comprador_nome LIKE %s OR vi.item_titulo LIKE %s OR vi.item_mlb LIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param, busca_param])
            
            if data_inicio:
                query += " AND DATE(v.data_aprovacao) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(v.data_aprovacao) <= %s"
                params.append(data_fim)
            
            if status_pagamento:
                query += " AND v.status_pagamento = %s"
                params.append(status_pagamento)
            
            if status_envio:
                query += " AND v.status_envio = %s"
                params.append(status_envio)
            
            query += " GROUP BY COALESCE(v.pack_id, v.venda_id)) as subquery"
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
            
        except Error as e:
            print(f"❌ Erro ao contar vendas: {e}")
            return 0
        finally:
            if conn.is_connected():
                conn.close()
    
    def calcular_totais_vendas_novo(self, user_id: int, busca: str = '', 
                                   data_inicio: str = '', data_fim: str = '', 
                                   status_pagamento: str = '', status_envio: str = '') -> Dict[str, Any]:
        """Calcula totais dos packs de vendas filtradas (nova estrutura)."""
        conn = self.conectar()
        if not conn:
            return {'total_vendas': 0, 'valor_total': 0, 'taxa_total': 0, 'frete_total': 0}
        
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    COUNT(*) as total_packs,
                    COALESCE(SUM(valor_total), 0) as valor_total,
                    COALESCE(SUM(taxa_ml), 0) as taxa_total,
                    COALESCE(SUM(frete_total), 0) as frete_total
                FROM (
                    SELECT 
                        COALESCE(v.pack_id, v.venda_id) as pack_id,
                        SUM(v.valor_total) as valor_total,
                        SUM(v.taxa_ml) as taxa_ml,
                        SUM(v.frete_total) as frete_total
                    FROM vendas v
                    LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                    WHERE v.user_id = %s
            """
            params = [user_id]
            
            if busca:
                query += " AND (v.venda_id LIKE %s OR v.comprador_nome LIKE %s OR vi.item_titulo LIKE %s OR vi.item_mlb LIKE %s)"
                busca_param = f"%{busca}%"
                params.extend([busca_param, busca_param, busca_param, busca_param])
            
            if data_inicio:
                query += " AND DATE(v.data_aprovacao) >= %s"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(v.data_aprovacao) <= %s"
                params.append(data_fim)
            
            if status_pagamento:
                query += " AND v.status_pagamento = %s"
                params.append(status_pagamento)
            
            if status_envio:
                query += " AND v.status_envio = %s"
                params.append(status_envio)
            
            query += " GROUP BY COALESCE(v.pack_id, v.venda_id)) as subquery"
            
            cursor.execute(query, params)
            result = cursor.fetchone()
            
            return {
                'total_vendas': result[0] or 0,
                'valor_total': float(result[1]) if result[1] else 0,
                'taxa_total': float(result[2]) if result[2] else 0,
                'frete_total': float(result[3]) if result[3] else 0
            }
            
        except Error as e:
            print(f"❌ Erro ao calcular totais: {e}")
            return {'total_vendas': 0, 'valor_total': 0, 'taxa_total': 0, 'frete_total': 0}
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_detalhes_venda(self, venda_id: str, user_id: int) -> Dict[str, Any]:
        """Obtém detalhes completos de uma venda."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Busca venda principal
            cursor.execute("""
                SELECT * FROM vendas 
                WHERE venda_id = %s AND user_id = %s
            """, (venda_id, user_id))
            
            venda = cursor.fetchone()
            if not venda:
                return {}
            
            # Busca itens da venda
            cursor.execute("""
                SELECT * FROM venda_itens 
                WHERE venda_id = %s AND user_id = %s
                ORDER BY id
            """, (venda_id, user_id))
            
            itens = cursor.fetchall()
            
            # Busca frete da venda
            cursor.execute("""
                SELECT * FROM venda_fretes 
                WHERE venda_id = %s AND user_id = %s
            """, (venda_id, user_id))
            
            frete = cursor.fetchone()
            
            # Busca pagamento da venda
            cursor.execute("""
                SELECT * FROM venda_pagamentos 
                WHERE venda_id = %s AND user_id = %s
            """, (venda_id, user_id))
            
            pagamento = cursor.fetchone()
            
            # Converte Decimal para float
            if venda['valor_total']:
                venda['valor_total'] = float(venda['valor_total'])
            if venda['taxa_ml']:
                venda['taxa_ml'] = float(venda['taxa_ml'])
            if venda['frete_total']:
                venda['frete_total'] = float(venda['frete_total'])
            
            for item in itens:
                if item['preco_unitario']:
                    item['preco_unitario'] = float(item['preco_unitario'])
                if item['preco_total']:
                    item['preco_total'] = float(item['preco_total'])
            
            if frete and frete['valor_frete']:
                frete['valor_frete'] = float(frete['valor_frete'])
            
            if pagamento and pagamento['valor_pago']:
                pagamento['valor_pago'] = float(pagamento['valor_pago'])
            
            return {
                'venda': venda,
                'itens': itens,
                'frete': frete,
                'pagamento': pagamento
            }
            
        except Error as e:
            print(f"❌ Erro ao buscar detalhes da venda: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_detalhes_pack(self, pack_id: str, user_id: int) -> Dict[str, Any]:
        """Obtém detalhes completos de um pack (múltiplas vendas)."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Busca dados do pack
            cursor.execute("""
                SELECT 
                    COALESCE(v.pack_id, v.venda_id) as pack_id,
                    COALESCE(v.pack_id, v.venda_id) as pack_id_original,
                    MIN(v.data_aprovacao) as data_aprovacao,
                    MIN(v.data_criacao) as data_criacao,
                    MIN(v.comprador_nome) as comprador_nome,
                    MIN(v.comprador_id) as comprador_id,
                    MIN(v.status) as status,
                    SUM(v.valor_total) as valor_total,
                    SUM(v.taxa_ml) as taxa_ml,
                    SUM(v.frete_total) as frete_total,
                    SUM(v.total_produtos) as total_produtos,
                    MIN(v.payment_method) as payment_method,
                    MIN(v.shipping_method) as shipping_method,
                    COUNT(DISTINCT v.venda_id) as total_vendas,
                    COUNT(DISTINCT vi.item_mlb) as total_mlbs,
                    GROUP_CONCAT(DISTINCT v.venda_id ORDER BY v.venda_id) as venda_ids
                FROM vendas v
                LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                WHERE (v.pack_id = %s OR v.venda_id = %s) AND v.user_id = %s
                GROUP BY COALESCE(v.pack_id, v.venda_id)
            """, (pack_id, pack_id, user_id))
            
            pack = cursor.fetchone()
            if not pack:
                return {}
            
            # Busca total de compras do comprador
            cursor.execute("""
                SELECT COUNT(DISTINCT COALESCE(pack_id, venda_id)) as total_compras
                FROM vendas 
                WHERE user_id = %s AND comprador_nome = %s
            """, (user_id, pack['comprador_nome']))
            
            total_compras_result = cursor.fetchone()
            pack['total_compras_comprador'] = total_compras_result['total_compras'] if total_compras_result else 0
            
            # Busca todos os itens do pack
            cursor.execute("""
                SELECT 
                    vi.*,
                    v.venda_id,
                    v.data_aprovacao
                FROM venda_itens vi
                JOIN vendas v ON vi.venda_id = v.venda_id AND vi.user_id = v.user_id
                WHERE (v.pack_id = %s OR v.venda_id = %s) AND v.user_id = %s
                ORDER BY v.data_aprovacao, v.venda_id, vi.item_mlb
            """, (pack_id, pack_id, user_id))
            
            itens = cursor.fetchall()
            
            # Busca fretes do pack
            cursor.execute("""
                SELECT 
                    vf.*,
                    v.venda_id
                FROM venda_fretes vf
                JOIN vendas v ON vf.venda_id = v.venda_id AND vf.user_id = v.user_id
                WHERE (v.pack_id = %s OR v.venda_id = %s) AND v.user_id = %s
            """, (pack_id, pack_id, user_id))
            
            fretes = cursor.fetchall()
            
            # Busca pagamentos do pack
            cursor.execute("""
                SELECT 
                    vp.*,
                    v.venda_id
                FROM venda_pagamentos vp
                JOIN vendas v ON vp.venda_id = v.venda_id AND vp.user_id = v.user_id
                WHERE (v.pack_id = %s OR v.venda_id = %s) AND v.user_id = %s
            """, (pack_id, pack_id, user_id))
            
            pagamentos = cursor.fetchall()
            
            # Converte Decimal para float
            if pack['valor_total']:
                pack['valor_total'] = float(pack['valor_total'])
            if pack['taxa_ml']:
                pack['taxa_ml'] = float(pack['taxa_ml'])
            if pack['frete_total']:
                pack['frete_total'] = float(pack['frete_total'])
            
            for item in itens:
                if item['preco_unitario']:
                    item['preco_unitario'] = float(item['preco_unitario'])
                if item['preco_total']:
                    item['preco_total'] = float(item['preco_total'])
            
            for frete in fretes:
                if frete['valor_frete']:
                    frete['valor_frete'] = float(frete['valor_frete'])
            
            for pagamento in pagamentos:
                if pagamento['valor_pago']:
                    pagamento['valor_pago'] = float(pagamento['valor_pago'])
            
            return {
                'pack': pack,
                'itens': itens,
                'fretes': fretes,
                'pagamentos': pagamentos
            }
            
        except Error as e:
            print(f"❌ Erro ao buscar detalhes do pack: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()

    def calcular_lucratividade_pack(self, pack_id: str, user_id: int) -> Dict[str, Any]:
        """Calcula a lucratividade de um pack completo."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Busca dados do pack
            cursor.execute("""
                SELECT 
                    COALESCE(v.pack_id, v.venda_id) as pack_id,
                    SUM(v.valor_total) as valor_total,
                    SUM(v.taxa_ml) as taxa_ml,
                    SUM(v.frete_total) as frete_total,
                    SUM(v.total_produtos) as total_produtos
                FROM vendas v
                WHERE (v.pack_id = %s OR v.venda_id = %s) AND v.user_id = %s
                GROUP BY COALESCE(v.pack_id, v.venda_id)
            """, (pack_id, pack_id, user_id))
            
            pack = cursor.fetchone()
            if not pack:
                return {}
            
            # Busca todos os itens do pack
            cursor.execute("""
                SELECT 
                    vi.item_mlb,
                    vi.item_titulo,
                    vi.quantidade,
                    vi.preco_unitario,
                    vi.preco_total,
                    v.venda_id
                FROM venda_itens vi
                JOIN vendas v ON vi.venda_id = v.venda_id AND vi.user_id = v.user_id
                WHERE (v.pack_id = %s OR v.venda_id = %s) AND v.user_id = %s
                ORDER BY v.data_aprovacao, v.venda_id, vi.item_mlb
            """, (pack_id, pack_id, user_id))
            
            itens = cursor.fetchall()
            
            # Calcula custos e lucratividade para cada item
            total_custo_produtos = 0
            total_custo_adicional = 0
            itens_com_lucratividade = []
            
            for item in itens:
                # Busca custos do produto
                cursor.execute("""
                    SELECT 
                        COALESCE(c.custo, 0) as custo_base,
                        COALESCE(c.imposto, 0) as imposto,
                        COALESCE(c.embalagem, 0) as embalagem,
                        COALESCE(c.extra, 0) as extra
                    FROM custos c
                    WHERE c.mlb = %s
                    ORDER BY c.id DESC
                    LIMIT 1
                """, (item['item_mlb'],))
                
                custos_produto = cursor.fetchone()
                
                # Busca custos específicos da venda (se existirem)
                cursor.execute("""
                    SELECT 
                        COALESCE(cv.imposto, 0) as imposto_venda,
                        COALESCE(cv.embalagem, 0) as embalagem_venda,
                        COALESCE(cv.custo, 0) as custo_venda,
                        COALESCE(cv.extra, 0) as extra_venda
                    FROM custos_vendas cv
                    WHERE cv.pack_id = %s AND cv.mlb = %s
                """, (pack_id, item['item_mlb']))
                
                custos_venda = cursor.fetchone()
                
                # Usa custos específicos da venda se existirem, senão usa custos do produto
                custo_base = float(custos_venda['custo_venda']) if custos_venda and custos_venda['custo_venda'] > 0 else (float(custos_produto['custo_base']) if custos_produto else 0)
                imposto = float(custos_venda['imposto_venda']) if custos_venda and custos_venda['imposto_venda'] > 0 else (float(custos_produto['imposto']) if custos_produto else 0)
                embalagem = float(custos_venda['embalagem_venda']) if custos_venda and custos_venda['embalagem_venda'] > 0 else (float(custos_produto['embalagem']) if custos_produto else 0)
                extra = float(custos_venda['extra_venda']) if custos_venda and custos_venda['extra_venda'] > 0 else (float(custos_produto['extra']) if custos_produto else 0)
                
                # Calcula custos por item
                custo_total_item = (custo_base + imposto + embalagem + extra) * item['quantidade']
                receita_item = float(item['preco_total'])
                lucro_item = receita_item - custo_total_item
                margem_item = (lucro_item / receita_item * 100) if receita_item > 0 else 0
                
                total_custo_produtos += custo_total_item
                
                itens_com_lucratividade.append({
                    'item_mlb': item['item_mlb'],
                    'item_titulo': item['item_titulo'],
                    'quantidade': item['quantidade'],
                    'preco_unitario': float(item['preco_unitario']),
                    'preco_total': receita_item,
                    'custo_base': custo_base,
                    'imposto': imposto,
                    'embalagem': embalagem,
                    'extra': extra,
                    'custo_total': custo_total_item,
                    'lucro': lucro_item,
                    'margem': margem_item,
                    'venda_id': item['venda_id']
                })
            
            # Calcula totais
            receita_total = float(pack['valor_total'])
            taxa_ml = float(pack['taxa_ml'])
            frete_total = float(pack['frete_total'])
            
            # Distribui frete proporcionalmente entre os itens
            frete_por_item = frete_total / len(itens) if itens else 0
            
            # Recalcula com frete incluído
            total_custo_final = total_custo_produtos + taxa_ml + frete_total
            lucro_total = receita_total - total_custo_final
            margem_total = (lucro_total / receita_total * 100) if receita_total > 0 else 0
            
            # Atualiza itens com frete
            for item in itens_com_lucratividade:
                item['frete_proporcional'] = frete_por_item
                item['custo_total_com_frete'] = item['custo_total'] + frete_por_item
                item['lucro_final'] = item['preco_total'] - item['custo_total_com_frete']
                item['margem_final'] = (item['lucro_final'] / item['preco_total'] * 100) if item['preco_total'] > 0 else 0
            
            return {
                'pack_id': pack_id,
                'receita_total': receita_total,
                'custo_produtos': total_custo_produtos,
                'taxa_ml': taxa_ml,
                'frete_total': frete_total,
                'custo_total': total_custo_final,
                'lucro_total': lucro_total,
                'margem_total': margem_total,
                'itens': itens_com_lucratividade
            }
            
        except Error as e:
            print(f"❌ Erro ao calcular lucratividade do pack: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()

    def salvar_venda_com_status(self, dados_venda: Dict[str, Any], user_id: int) -> bool:
        """Salva/atualiza venda com informações de status detalhado."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                # Extrair dados básicos
                venda_id = str(dados_venda.get('id', ''))
                pack_id = str(dados_venda.get('pack_id', venda_id))
                
                # Dados do comprador
                buyer = dados_venda.get('buyer', {})
                comprador_id = str(buyer.get('id', ''))
                comprador_nome = buyer.get('nickname', '')
                comprador_email = buyer.get('email', '')
                
                # Datas
                data_aprovacao = dados_venda.get('date_closed')  # Usar date_closed como data de aprovação
                data_criacao = dados_venda.get('date_created')
                
                # Valores (tratando None)
                valor_total = float(dados_venda.get('total_amount') or 0)
                
                # Calcular taxa ML dos payments
                taxa_ml = 0
                payments = dados_venda.get('payments', [])
                if payments:
                    taxa_ml = float(payments[0].get('marketplace_fee', 0))
                
                frete_total = float(dados_venda.get('shipping_cost') or 0)
                
                # Status detalhado dos payments com tradução
                from translations import translate_payment_status, translate_payment_method, translate_shipping_method
                
                status_pagamento = 'unknown'
                status_pagamento_pt = 'Desconhecido'
                payment_method_pt = 'Desconhecido'
                
                if payments:
                    status_pagamento = payments[0].get('status', 'unknown')
                    status_pagamento_pt = translate_payment_status(status_pagamento)
                    payment_method_pt = translate_payment_method(payments[0].get('payment_method_id', 'unknown'))
                
                # Status de envio detalhado usando o novo sistema
                from shipping_status import map_ml_shipping_status
                
                ml_status = dados_venda.get('status', 'unknown')
                status_detail = dados_venda.get('status_detail', '')
                fulfilled = dados_venda.get('fulfilled', False)
                
                status_envio, status_descricao, status_categoria = map_ml_shipping_status(
                    ml_status, status_detail, fulfilled
                )
                
                # Dados de envio detalhados com tradução
                shipping = dados_venda.get('shipping', {})
                data_envio = None
                data_entrega = None
                codigo_rastreamento = ''
                transportadora = ''
                
                # Extrair informações detalhadas de envio
                codigo_rastreamento_detalhado = shipping.get('tracking_number', '')
                transportadora_detalhada = shipping.get('service_name', '')
                shipping_method_pt = translate_shipping_method(shipping.get('id', 'unknown'))
                
                # Traduzir status do pedido
                status_pedido_pt = translate_order_status(dados_venda.get('status', 'unknown'))
                
                # Endereço de entrega
                receiver_address = dados_venda.get('receiver_address', {})
                endereco_entrega = ''
                if receiver_address:
                    endereco_parts = []
                    if receiver_address.get('address_line'):
                        endereco_parts.append(receiver_address['address_line'])
                    if receiver_address.get('city'):
                        endereco_parts.append(receiver_address['city'])
                    if receiver_address.get('state'):
                        endereco_parts.append(receiver_address['state'])
                    if receiver_address.get('zip_code'):
                        endereco_parts.append(receiver_address['zip_code'])
                    endereco_entrega = ', '.join(endereco_parts)
                
                # Observações detalhadas
                observacoes_envio = f"Status Original: {ml_status}"
                if status_detail:
                    observacoes_envio += f" | Detalhe: {status_detail}"
                if fulfilled is not None:
                    observacoes_envio += f" | Fulfilled: {fulfilled}"
                
                # Observações gerais
                observacoes = f"Status: {dados_venda.get('status', 'unknown')}"
                if dados_venda.get('status_detail'):
                    observacoes += f" | Detalhe: {dados_venda.get('status_detail')}"
                
                # Inserir/atualizar venda principal
                cursor.execute("""
                    INSERT INTO vendas (
                        user_id, venda_id, pack_id, data_aprovacao, data_criacao,
                        comprador_id, comprador_nome, comprador_email, status,
                        valor_total, taxa_ml, frete_total, total_produtos,
                        payment_method, shipping_method, status_pagamento, status_envio,
                        data_envio, data_entrega, codigo_rastreamento, transportadora,
                        observacoes, ultima_atualizacao,
                        status_envio_descricao, status_envio_categoria, status_envio_original,
                        status_envio_detalhe, data_ultima_atualizacao_envio,
                        codigo_rastreamento_detalhado, transportadora_detalhada,
                        endereco_entrega, observacoes_envio,
                        status_pagamento_pt, payment_method_pt, shipping_method_pt,
                        status_pedido_pt, status_envio_pt, categoria_envio_pt
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        pack_id = VALUES(pack_id),
                        data_aprovacao = VALUES(data_aprovacao),
                        data_criacao = VALUES(data_criacao),
                        comprador_id = VALUES(comprador_id),
                        comprador_nome = VALUES(comprador_nome),
                        comprador_email = VALUES(comprador_email),
                        status = VALUES(status),
                        valor_total = VALUES(valor_total),
                        taxa_ml = VALUES(taxa_ml),
                        frete_total = VALUES(frete_total),
                        total_produtos = VALUES(total_produtos),
                        payment_method = VALUES(payment_method),
                        shipping_method = VALUES(shipping_method),
                        status_pagamento = VALUES(status_pagamento),
                        status_envio = VALUES(status_envio),
                        data_envio = VALUES(data_envio),
                        data_entrega = VALUES(data_entrega),
                        codigo_rastreamento = VALUES(codigo_rastreamento),
                        transportadora = VALUES(transportadora),
                        observacoes = VALUES(observacoes),
                        ultima_atualizacao = VALUES(ultima_atualizacao),
                        status_envio_descricao = VALUES(status_envio_descricao),
                        status_envio_categoria = VALUES(status_envio_categoria),
                        status_envio_original = VALUES(status_envio_original),
                        status_envio_detalhe = VALUES(status_envio_detalhe),
                        data_ultima_atualizacao_envio = VALUES(data_ultima_atualizacao_envio),
                        codigo_rastreamento_detalhado = VALUES(codigo_rastreamento_detalhado),
                        transportadora_detalhada = VALUES(transportadora_detalhada),
                        endereco_entrega = VALUES(endereco_entrega),
                        observacoes_envio = VALUES(observacoes_envio),
                        status_pagamento_pt = VALUES(status_pagamento_pt),
                        payment_method_pt = VALUES(payment_method_pt),
                        shipping_method_pt = VALUES(shipping_method_pt),
                        status_pedido_pt = VALUES(status_pedido_pt),
                        status_envio_pt = VALUES(status_envio_pt),
                        categoria_envio_pt = VALUES(categoria_envio_pt),
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_id, venda_id, pack_id, data_aprovacao, data_criacao,
                    comprador_id, comprador_nome, comprador_email, dados_venda.get('status', 'unknown'),
                    valor_total, taxa_ml, frete_total, len(dados_venda.get('order_items', [])),
                    payments[0].get('payment_method_id', '') if payments else '', 
                    shipping.get('id', ''),
                    status_pagamento, status_envio, data_envio, data_entrega,
                    codigo_rastreamento, transportadora, observacoes, dados_venda.get('last_updated'),
                    status_descricao, status_categoria, ml_status, status_detail,
                    dados_venda.get('last_updated'), codigo_rastreamento_detalhado,
                    transportadora_detalhada, endereco_entrega, observacoes_envio,
                    status_pagamento_pt, payment_method_pt, shipping_method_pt,
                    status_pedido_pt, status_descricao, status_categoria
                ))
                
                # Processar itens da venda
                order_items = dados_venda.get('order_items', [])
                if order_items:
                    # Remover itens antigos
                    cursor.execute("DELETE FROM venda_itens WHERE venda_id = %s AND user_id = %s", (venda_id, user_id))
                    
                    # Inserir novos itens
                    for item in order_items:
                        cursor.execute("""
                            INSERT INTO venda_itens (
                                user_id, venda_id, item_id, item_mlb, item_titulo, quantidade,
                                preco_unitario, preco_total, categoria_id
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            user_id, venda_id, item.get('item', {}).get('id', ''),
                            item.get('item', {}).get('id', ''), item.get('item', {}).get('title', ''), 
                            item.get('quantity', 0), float(item.get('unit_price') or 0), 
                            float(item.get('unit_price') or 0) * item.get('quantity', 0),
                            item.get('item', {}).get('category_id', '')
                        ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao salvar venda com status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    # ===== SISTEMA DE STATUS DE ENVIO DETALHADO =====
    
    def obter_vendas_por_status_envio(self, user_id: int, status_envio: str = None, 
                                     categoria: str = None, limite: int = 100) -> List[Dict[str, Any]]:
        """Obtém vendas filtradas por status de envio."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                # Construir query base com traduções
                query = """
                    SELECT v.*, 
                           v.status_envio_descricao as status_descricao,
                           v.status_envio_categoria as status_categoria,
                           v.status_envio_original as status_original,
                           v.status_envio_detalhe as status_detalhe,
                           v.codigo_rastreamento_detalhado as codigo_rastreamento_detalhado,
                           v.transportadora_detalhada as transportadora_detalhada,
                           v.endereco_entrega as endereco_entrega,
                           v.observacoes_envio as observacoes_envio,
                           v.status_pagamento_pt as status_pagamento_pt,
                           v.payment_method_pt as payment_method_pt,
                           v.shipping_method_pt as shipping_method_pt,
                           v.status_pedido_pt as status_pedido_pt,
                           v.status_envio_pt as status_envio_pt,
                           v.categoria_envio_pt as categoria_envio_pt
                    FROM vendas v
                    WHERE v.user_id = %s
                """
                params = [user_id]
                
                # Adicionar filtros
                if status_envio:
                    query += " AND v.status_envio = %s"
                    params.append(status_envio)
                
                if categoria:
                    query += " AND v.status_envio_categoria = %s"
                    params.append(categoria)
                
                # Ordenar e limitar
                query += " ORDER BY v.data_criacao DESC LIMIT %s"
                params.append(limite)
                
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Erro ao buscar vendas por status de envio: {e}")
            return []
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_estatisticas_status_envio(self, user_id: int) -> Dict[str, Any]:
        """Obtém estatísticas de status de envio."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            with conn.cursor() as cursor:
                # Contar por status
                cursor.execute("""
                    SELECT status_envio, status_envio_categoria, COUNT(*) as total
                    FROM vendas 
                    WHERE user_id = %s
                    GROUP BY status_envio, status_envio_categoria
                    ORDER BY total DESC
                """, (user_id,))
                
                status_counts = cursor.fetchall()
                
                # Contar por categoria
                cursor.execute("""
                    SELECT status_envio_categoria, COUNT(*) as total
                    FROM vendas 
                    WHERE user_id = %s
                    GROUP BY status_envio_categoria
                    ORDER BY total DESC
                """, (user_id,))
                
                category_counts = cursor.fetchall()
                
                # Total de vendas
                cursor.execute("SELECT COUNT(*) FROM vendas WHERE user_id = %s", (user_id,))
                total_vendas = cursor.fetchone()[0]
                
                return {
                    'total_vendas': total_vendas,
                    'por_status': [{'status': row[0], 'categoria': row[1], 'total': row[2]} for row in status_counts],
                    'por_categoria': [{'categoria': row[0], 'total': row[1]} for row in category_counts]
                }
                
        except Exception as e:
            print(f"Erro ao obter estatísticas de status de envio: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()
    
    def obter_todos_status_envio(self) -> List[Dict[str, str]]:
        """Obtém todos os status de envio disponíveis."""
        try:
            from shipping_status import get_all_shipping_statuses
            return get_all_shipping_statuses()
        except Exception as e:
            print(f"Erro ao obter status de envio: {e}")
            return []
    
    def obter_status_envio_por_categoria(self, categoria: str) -> List[Dict[str, str]]:
        """Obtém status de envio filtrados por categoria."""
        try:
            from shipping_status import get_shipping_statuses_by_category
            return get_shipping_statuses_by_category(categoria)
        except Exception as e:
            print(f"Erro ao obter status por categoria: {e}")
            return []

    # ===== SISTEMA DE WEBHOOKS =====
    
    def obter_token_usuario(self, user_id: int) -> Optional[str]:
        """Obtém o token de acesso de um usuário."""
        conn = self.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT access_token FROM tokens 
                    WHERE user_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 1
                """, (user_id,))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            print(f"Erro ao obter token do usuário {user_id}: {e}")
            return None
        finally:
            conn.close()
    
    def salvar_notificacao_generica(self, notification) -> bool:
        """Salva uma notificação genérica no banco."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO notificacoes_genericas 
                    (notification_id, topic, resource, user_id, application_id, 
                     attempts, sent_at, received_at, actions, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    notification.notification_id,
                    notification.topic,
                    notification.resource,
                    notification.user_id,
                    notification.application_id,
                    notification.attempts,
                    notification.sent,
                    notification.received,
                    json.dumps(notification.actions) if notification.actions else None,
                    json.dumps(notification.raw_data) if notification.raw_data else None
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao salvar notificação genérica: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def registrar_log_webhook(self, notification_id: str, topic: str, resource: str, 
                            user_id: int, success: bool, attempts: int, 
                            raw_data: Dict[str, Any], error_message: str = None) -> bool:
        """Registra log de processamento de webhook."""
        conn = self.conectar()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO webhook_logs 
                    (notification_id, topic, resource, user_id, success, attempts, 
                     error_message, raw_data)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    notification_id,
                    topic,
                    resource,
                    user_id,
                    success,
                    attempts,
                    error_message,
                    json.dumps(raw_data) if raw_data else None
                ))
                
                # Atualizar estatísticas
                self._atualizar_estatisticas_webhook(cursor, user_id, topic, success)
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao registrar log de webhook: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _atualizar_estatisticas_webhook(self, cursor, user_id: int, topic: str, success: bool):
        """Atualiza estatísticas de webhook."""
        try:
            # Inserir ou atualizar estatísticas
            cursor.execute("""
                INSERT INTO webhook_stats (user_id, topic, total_received, total_success, total_errors, last_processed)
                VALUES (%s, %s, 1, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    total_received = total_received + 1,
                    total_success = total_success + %s,
                    total_errors = total_errors + %s,
                    last_processed = NOW()
            """, (
                user_id, topic, 
                1 if success else 0,  # total_success
                0 if success else 1,  # total_errors
                1 if success else 0,  # total_success (update)
                0 if success else 1   # total_errors (update)
            ))
        except Exception as e:
            print(f"Erro ao atualizar estatísticas de webhook: {e}")
    
    def obter_estatisticas_webhooks(self, user_id: int = None) -> Dict[str, Any]:
        """Obtém estatísticas de webhooks processados."""
        conn = self.conectar()
        if not conn:
            return {}
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                if user_id:
                    cursor.execute("""
                        SELECT topic, total_received, total_success, total_errors, last_processed
                        FROM webhook_stats 
                        WHERE user_id = %s
                        ORDER BY last_processed DESC
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT topic, 
                               SUM(total_received) as total_received,
                               SUM(total_success) as total_success,
                               SUM(total_errors) as total_errors,
                               MAX(last_processed) as last_processed
                        FROM webhook_stats 
                        GROUP BY topic
                        ORDER BY last_processed DESC
                    """)
                
                stats = cursor.fetchall()
                
                # Calcular totais gerais
                total_received = sum(stat['total_received'] for stat in stats)
                total_success = sum(stat['total_success'] for stat in stats)
                total_errors = sum(stat['total_errors'] for stat in stats)
                
                return {
                    'stats_by_topic': stats,
                    'totals': {
                        'total_received': total_received,
                        'total_success': total_success,
                        'total_errors': total_errors,
                        'success_rate': (total_success / total_received * 100) if total_received > 0 else 0
                    }
                }
                
        except Exception as e:
            print(f"Erro ao obter estatísticas de webhooks: {e}")
            return {}
        finally:
            conn.close()
    
    def obter_logs_webhook(self, user_id: int = None, topic: str = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Obtém logs de webhooks com filtros opcionais."""
        conn = self.conectar()
        if not conn:
            return []
        
        try:
            with conn.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM webhook_logs WHERE 1=1"
                params = []
                
                if user_id:
                    query += " AND user_id = %s"
                    params.append(user_id)
                
                if topic:
                    query += " AND topic = %s"
                    params.append(topic)
                
                query += " ORDER BY processed_at DESC LIMIT %s"
                params.append(limit)
                
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Erro ao obter logs de webhook: {e}")
            return []
        finally:
            conn.close()

