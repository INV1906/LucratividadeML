"""
Módulo para cálculos de lucratividade e análise financeira.
"""

from typing import Dict, List, Optional, Any
from decimal import Decimal
from database import DatabaseManager
from meli_api import MercadoLivreAPI

class ProfitabilityCalculator:
    """Classe para cálculos de lucratividade e análise financeira."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.api = MercadoLivreAPI()
    
    def calcular_lucratividade_produto(self, mlb: str, custos_adicionais: Dict[str, float] = None) -> Optional[Dict[str, Any]]:
        """
        Calcula a lucratividade de um produto específico.
        
        Args:
            mlb: ID do produto no Mercado Livre
            custos_adicionais: Dicionário com custos adicionais (imposto_perc, embalagem, custo, extra)
        
        Returns:
            Dicionário com análise de lucratividade
        """
        conn = self.db.conectar()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                # Busca dados do produto
                cursor.execute("""
                    SELECT p.price, p.title, p.mlb, p.category, c.name as categoria_nome, 
                           p.avaliable_quantity, p.status, p.listing_type_id, p.frete, p.frete_gratis, p.thumbnail, p.permalink
                    FROM produtos p 
                    LEFT JOIN categorias_mlb c ON p.category = c.id
                    WHERE p.mlb = %s
                """, (mlb,))
                produto = cursor.fetchone()
                
                if not produto:
                    return None
                
                price, title, mlb, category, categoria_nome, avaliable_quantity, status, listing_type_id, frete, frete_gratis, thumbnail, permalink = produto
                
                # Busca custos do produto da tabela produtos
                cursor.execute("""
                    SELECT custo_listagem, custo_venda, imposto, embalagem, custo, extra
                    FROM produtos WHERE mlb = %s
                """, (mlb,))
                custos_produto = cursor.fetchone()
                
                # Busca custos adicionais da tabela custos
                cursor.execute("""
                    SELECT custos FROM custos WHERE mlb = %s
                """, (mlb,))
                custos_ml_result = cursor.fetchone()
                custos_ml = custos_ml_result[0] if custos_ml_result else 0
                
                # Frete já foi buscado da tabela produtos
                
                # Usa custos do banco ou custos fornecidos
                if custos_produto:
                    custo_listagem, custo_venda, imposto_perc, embalagem, custo_produto, extra = custos_produto
                else:
                    custo_listagem = 0
                    custo_venda = 0
                    imposto_perc = 0
                    embalagem = 0
                    custo_produto = 0
                    extra = 0
                
                # Sobrescreve com custos adicionais se fornecidos
                if custos_adicionais:
                    imposto_perc = custos_adicionais.get('imposto_perc', imposto_perc)
                    embalagem = custos_adicionais.get('embalagem', embalagem)
                    custo_produto = custos_adicionais.get('custo', custo_produto)
                    extra = custos_adicionais.get('extra', extra)
                
                # Converte para float
                price = float(price or 0)
                custos_ml = float(custos_ml) if custos_ml else 0
                frete = float(frete) if frete else 0
                imposto_perc = float(imposto_perc) if imposto_perc else 0
                embalagem = float(embalagem) if embalagem else 0
                custo_produto = float(custo_produto) if custo_produto else 0
                extra = float(extra) if extra else 0
                
                # Frete é sempre considerado como custo para o vendedor
                # frete_gratis = 1 significa que o cliente não paga, mas o vendedor sim
                
                # Cálculos
                base_imposto = price - frete - custos_ml
                imposto_valor = float(imposto_perc / 100) * base_imposto if imposto_perc > 0 else 0
                
                custo_total = custo_produto + embalagem + custos_ml + imposto_valor + frete + extra
                lucro_bruto = price - custo_total
                margem_liquida = (lucro_bruto / price) * 100 if price > 0 else 0
                
                return {
                    'mlb': mlb,
                    'title': title,
                    'category': categoria_nome or category,
                    'preco_venda': price,
                    'quantidade_disponivel': avaliable_quantity,
                    'status': status,
                    'listing_type_id': listing_type_id,
                    'thumbnail': thumbnail,
                    'permalink': permalink,
                    'comissao_ml': custos_ml,
                    'taxa_listagem': 0,  # Não temos essa informação separada
                    'frete': frete,
                    'imposto_percentual': imposto_perc,
                    'imposto': imposto_valor,
                    'custo_produto': custo_produto,
                    'embalagem': embalagem,
                    'extra': extra,
                    'custo_total': custo_total,
                    'lucro_bruto': lucro_bruto,
                    'margem_liquida': margem_liquida,
                    'roi': (lucro_bruto / custo_total) * 100 if custo_total > 0 else 0
                }
                
        except Exception as e:
            print(f"Erro ao calcular lucratividade: {e}")
            return None
        finally:
            if conn.is_connected():
                conn.close()
    
    def calcular_lucratividade_venda(self, pack_id: str, custos_adicionais: Dict[str, float] = None) -> Optional[Dict[str, Any]]:
        """
        Calcula a lucratividade de um pack específico.
        
        Args:
            pack_id: ID do pack
            custos_adicionais: Dicionário com custos adicionais por item
        
        Returns:
            Dicionário com análise de lucratividade do pack
        """
        dados_venda = self.db.calcular_lucratividade_venda(pack_id)
        if not dados_venda:
            return None
        
        itens = dados_venda['itens']
        preco_total = dados_venda['preco_total']
        taxa_total = dados_venda['taxa_total']
        frete = dados_venda['frete']
        
        # Usa custos padrão se não fornecidos
        if not custos_adicionais:
            custos_adicionais = {
                'imposto_perc': 14.0,  # 14% de imposto padrão
                'embalagem_por_item': 5.0,  # R$ 5 por item
                'custo_por_item': 0,  # Será calculado por item
                'custos_extras': 0
            }
        
        # Calcula custos por item
        custo_total_venda = 0.0
        itens_analisados = []
        
        for item in itens:
            item_id = item['item_id']
            quantidade = item['quantidade'] or 0
            preco_item = float(item['preco_total'] or 0)
            
            # Busca custos específicos da venda primeiro, depois custos padrão do produto
            custos_item = self.db.obter_custos_produto_para_venda(item_id, pack_id)
            
            if custos_item:
                # Usa custos específicos da venda
                imposto_perc = float(custos_item.get('imposto', 0))
                embalagem_item = float(custos_item.get('embalagem', 0))
                custo_produto = float(custos_item.get('custo', 0))
                custos_extras_item = float(custos_item.get('extra', 0))
            else:
                # Fallback para custos padrão
                imposto_perc = custos_adicionais.get('imposto_perc', 14.0)
                embalagem_item = float(custos_adicionais.get('embalagem_por_item', 5.0)) * quantidade
                custo_produto = custos_adicionais.get('custo_por_item', 0)
                custos_extras_item = float(custos_adicionais.get('custos_extras', 0))
            
            # Calcula custos do item
            custo_item = float(custo_produto) * quantidade
            
            # Imposto sobre o valor do item
            base_imposto = preco_item - (taxa_total / len(itens)) - (frete / len(itens))
            imposto_item = float(imposto_perc / 100) * base_imposto
            
            custo_total_item = float(custo_item + embalagem_item + (taxa_total / len(itens)) + imposto_item + (frete / len(itens)) + custos_extras_item)
            lucro_item = preco_item - custo_total_item
            margem_item = (lucro_item / preco_item) * 100 if preco_item > 0 else 0
            
            item_analisado = {
                'item_id': item_id,
                'titulo': item['item_titulo'],
                'quantidade': quantidade,
                'preco_total': preco_item,
                'custo_produto': custo_item,
                'embalagem': embalagem_item,
                'taxa_ml': taxa_total / len(itens),
                'imposto': imposto_item,
                'frete': frete / len(itens),
                'custos_extras': custos_extras_item,
                'custo_total': custo_total_item,
                'lucro': lucro_item,
                'margem': margem_item
            }
            
            itens_analisados.append(item_analisado)
            custo_total_venda += custo_total_item
        
        lucro_total = preco_total - custo_total_venda
        margem_total = (lucro_total / preco_total) * 100 if preco_total > 0 else 0
        
        return {
            'pack_id': pack_id,
            'id_venda': pack_id,  # Para compatibilidade
            'preco_total_venda': preco_total,
            'taxa_total_ml': taxa_total,
            'frete_total': frete,
            'custo_total_venda': custo_total_venda,
            'lucro_total': lucro_total,
            'margem_total': margem_total,
            'quantidade_itens': len(itens),
            'produtos': dados_venda.get('produtos', []),
            'itens': itens_analisados,
            'comprador': dados_venda.get('comprador'),
            'data_aprovacao': dados_venda.get('data_aprovacao'),
            'status': dados_venda.get('status'),
            'resumo': {
                'receita_bruta': preco_total,
                'custos_diretos': custo_total_venda - taxa_total - frete,
                'taxas_ml': taxa_total,
                'frete': frete,
                'lucro_liquido': lucro_total,
                'margem_liquida': margem_total
            }
        }
    
    def obter_analise_geral_usuario(self, user_id: int, periodo_dias: int = 30) -> Dict[str, Any]:
        """
        Obtém análise geral de lucratividade de um usuário.
        
        Args:
            user_id: ID do usuário
            periodo_dias: Período em dias para análise
        
        Returns:
            Dicionário com análise geral
        """
        conn = self.db.conectar()
        if not conn:
            return {}
        
        try:
            with conn.cursor() as cursor:
                # Busca vendas do período (se período for 0, busca todas as vendas)
                if periodo_dias > 0:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_vendas,
                            SUM(valor_total) as receita_total,
                            SUM(taxa_ml) as taxa_total,
                            SUM(frete_total) as frete_total,
                            AVG(valor_total) as ticket_medio
                        FROM vendas 
                        WHERE user_id = %s 
                        AND data_aprovacao >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    """, (user_id, periodo_dias))
                    
                    vendas = cursor.fetchone()
                else:
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_vendas,
                            SUM(valor_total) as receita_total,
                            SUM(taxa_ml) as taxa_total,
                            SUM(frete_total) as frete_total,
                            AVG(valor_total) as ticket_medio
                        FROM vendas 
                        WHERE user_id = %s
                    """, (user_id,))
                    vendas = cursor.fetchone()
                
                # Busca produtos ativos
                cursor.execute("""
                    SELECT COUNT(*) as total_produtos
                    FROM produtos 
                    WHERE user_id = %s AND status = 'active'
                """, (user_id,))
                
                produtos = cursor.fetchone()
                
                # Busca produtos com maior margem
                cursor.execute("""
                    SELECT p.mlb, p.title, p.price, p.sold_quantity
                    FROM produtos p
                    WHERE p.user_id = %s AND p.status = 'active'
                    ORDER BY p.sold_quantity DESC
                    LIMIT 5
                """, (user_id,))
                
                top_produtos = cursor.fetchall()
                
                # Busca vendas por dia para o gráfico
                cursor.execute("""
                    SELECT 
                        DATE(data_aprovacao) as data_venda,
                        COUNT(*) as vendas_dia,
                        SUM(valor_total) as receita_dia
                    FROM vendas 
                    WHERE user_id = %s 
                    AND data_aprovacao >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(data_aprovacao)
                    ORDER BY data_venda ASC
                """, (user_id, periodo_dias))
                
                vendas_por_dia = cursor.fetchall()
                
                # Calcula totais com tratamento de None
                total_vendas = vendas[0] or 0
                receita_total = float(vendas[1]) if vendas[1] else 0
                taxa_total = float(vendas[2]) if vendas[2] else 0
                frete_total = float(vendas[3]) if vendas[3] else 0
                ticket_medio = float(vendas[4]) if vendas[4] else 0
                
                print(f"📊 Análise geral - Vendas: {total_vendas}, Receita: R$ {receita_total:.2f}, Ticket: R$ {ticket_medio:.2f}")
                
                return {
                    'periodo_dias': periodo_dias,
                    'total_vendas': total_vendas,
                    'receita_total': receita_total,
                    'taxa_total': taxa_total,
                    'frete_total': frete_total,
                    'ticket_medio': ticket_medio,
                    'total_produtos_ativos': produtos[0] or 0,
                    'vendas_por_dia': [
                        {
                            'data': item[0].strftime('%Y-%m-%d') if item[0] else '',
                            'vendas': item[1] or 0,
                            'receita': float(item[2]) if item[2] else 0
                        }
                        for item in vendas_por_dia
                    ],
                    'top_produtos': [
                        {
                            'mlb': item[0],
                            'title': item[1],
                            'price': float(item[2]) if item[2] else 0,
                            'sold_quantity': item[3] or 0
                        }
                        for item in top_produtos
                    ],
                    'receita_liquida_estimada': receita_total - taxa_total - frete_total
                }
                
        except Exception as e:
            print(f"Erro ao obter análise geral: {e}")
            return {}
        finally:
            if conn.is_connected():
                conn.close()
    
    def sugerir_otimizacoes(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Sugere otimizações avançadas baseadas em análise profunda dos dados do usuário.
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Lista de sugestões de otimização priorizadas
        """
        sugestoes = []
        
        conn = self.db.conectar()
        if not conn:
            return sugestoes
        
        try:
            with conn.cursor() as cursor:
                # 1. ANÁLISE DE LUCRATIVIDADE
                sugestoes.extend(self._analisar_lucratividade(cursor, user_id))
                
                # 2. ANÁLISE DE PREÇOS COMPETITIVOS
                sugestoes.extend(self._analisar_precos_competitivos(cursor, user_id))
                
                # 3. ANÁLISE DE ESTOQUE E VENDAS
                sugestoes.extend(self._analisar_estoque_vendas(cursor, user_id))
                
                # 4. ANÁLISE DE FRETE (removida)
                # sugestoes.extend(self._analisar_frete(cursor, user_id))
                
                # 5. ANÁLISE DE PRODUTOS INATIVOS
                sugestoes.extend(self._analisar_produtos_inativos(cursor, user_id))
                
                # 6. ANÁLISE DE SAZONALIDADE
                sugestoes.extend(self._analisar_sazonalidade(cursor, user_id))
                
                # 7. ANÁLISE DE CUSTOS
                sugestoes.extend(self._analisar_custos(cursor, user_id))
                
                # Ordenar sugestões por prioridade
                sugestoes.sort(key=lambda x: x.get('prioridade', 5), reverse=True)
                
        except Exception as e:
            print(f"Erro ao gerar sugestões: {e}")
        finally:
            if conn.is_connected():
                conn.close()
        
        return sugestoes[:8]  # Retorna apenas as 8 melhores sugestões
    
    def _analisar_lucratividade(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa lucratividade dos produtos e sugere otimizações."""
        sugestoes = []
        
        # Produtos com baixa margem de lucro
        cursor.execute("""
            SELECT p.mlb, p.title, p.price, p.sold_quantity, p.status,
                   COALESCE(c.custo, 0) as custo_produto,
                   COALESCE(c.embalagem, 0) as embalagem,
                   COALESCE(c.extra, 0) as extra,
                   COALESCE(c.imposto, 0) as imposto,
                   COALESCE(p.frete, 0) as frete,
                   (p.price - COALESCE(c.custo, 0) - COALESCE(c.embalagem, 0) - 
                    COALESCE(c.extra, 0) - COALESCE(c.imposto, 0) - COALESCE(p.frete, 0)) / p.price as margem
            FROM produtos p
            LEFT JOIN custos c ON c.mlb = p.mlb
            WHERE p.user_id = %s AND p.status = 'active' AND p.price > 0
            AND p.title IS NOT NULL AND p.title != '' AND p.mlb IS NOT NULL AND p.mlb != ''
            AND (p.price - COALESCE(c.custo, 0) - COALESCE(c.embalagem, 0) - 
                 COALESCE(c.extra, 0) - COALESCE(c.imposto, 0) - COALESCE(p.frete, 0)) / p.price < 0.1
            ORDER BY margem ASC
            LIMIT 5
        """, (user_id,))
        
        produtos_baixa_margem = cursor.fetchall()
        
        if produtos_baixa_margem:
            sugestoes.append({
                'tipo': 'baixa_margem',
                'titulo': '⚠️ Produtos com Margem Baixa',
                'descricao': f'{len(produtos_baixa_margem)} produtos com margem inferior a 10%. Considere revisar preços ou custos.',
                'prioridade': 9,
                'produtos': [
                    {
                        'mlb': item[0],
                        'title': item[1],
                        'price': float(item[2]) if item[2] else 0,
                        'margem': round(float(item[10]) * 100, 1) if item[10] else 0
                    }
                    for item in produtos_baixa_margem
                ]
            })
        
        return sugestoes
    
    def _analisar_precos_competitivos(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa preços em relação às sugestões do Mercado Livre."""
        sugestoes = []
        
        # Produtos com preço muito acima da sugestão
        cursor.execute("""
            SELECT p.mlb, p.title, p.price, sp.sugestao, sp.menor_preco
            FROM produtos p
            JOIN sugestoes_preco sp ON sp.mlb = p.mlb
            WHERE p.user_id = %s AND p.status = 'active' 
            AND p.title IS NOT NULL AND p.title != '' AND p.mlb IS NOT NULL AND p.mlb != ''
            AND p.price > sp.sugestao * 1.2
            ORDER BY (p.price - sp.sugestao) / sp.sugestao DESC
            LIMIT 5
        """, (user_id,))
        
        produtos_preco_alto = cursor.fetchall()
        
        if produtos_preco_alto:
            sugestoes.append({
                'tipo': 'preco_alto',
                'titulo': '📈 Preços Acima da Sugestão',
                'descricao': f'{len(produtos_preco_alto)} produtos com preço 20% acima da sugestão do ML. Considere ajustar.',
                'prioridade': 8,
                'produtos': [
                    {
                        'mlb': item[0],
                        'title': item[1],
                        'preco_atual': float(item[2]) if item[2] else 0,
                        'sugestao': float(item[3]) if item[3] else 0,
                        'diferenca': round(((item[2] - item[3]) / item[3]) * 100, 1) if item[3] > 0 else 0
                    }
                    for item in produtos_preco_alto
                ]
            })
        
        return sugestoes
    
    def _analisar_estoque_vendas(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa estoque e padrões de vendas."""
        sugestoes = []
        
        # Produtos com estoque baixo e alta demanda
        cursor.execute("""
            SELECT mlb, title, price, avaliable_quantity, sold_quantity
            FROM produtos 
            WHERE user_id = %s AND status = 'active' 
            AND title IS NOT NULL AND title != '' AND mlb IS NOT NULL AND mlb != ''
            AND avaliable_quantity < 5 AND sold_quantity > 10
            ORDER BY sold_quantity DESC
            LIMIT 5
        """, (user_id,))
        
        produtos_estoque_baixo = cursor.fetchall()
        
        if produtos_estoque_baixo:
            sugestoes.append({
                'tipo': 'estoque_baixo',
                'titulo': '📦 Estoque Baixo - Alta Demanda',
                'descricao': f'{len(produtos_estoque_baixo)} produtos com estoque baixo mas alta demanda. Reabasteça urgentemente!',
                'prioridade': 9,
                'produtos': [
                    {
                        'mlb': item[0],
                        'title': item[1],
                        'estoque': item[3] or 0,
                        'vendas': item[4] or 0
                    }
                    for item in produtos_estoque_baixo
                ]
            })
        
        return sugestoes
    
    def _analisar_frete(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa estratégias de frete."""
        sugestoes = []
        
        # Produtos sem frete grátis com preço alto
        cursor.execute("""
            SELECT mlb, title, price, frete
            FROM produtos 
            WHERE user_id = %s AND status = 'active' 
            AND title IS NOT NULL AND title != '' AND mlb IS NOT NULL AND mlb != ''
            AND (frete_gratis = 0 OR frete > 0) AND price > 100
            ORDER BY price DESC
            LIMIT 5
        """, (user_id,))
        
        produtos_sem_frete_gratis = cursor.fetchall()
        
        if produtos_sem_frete_gratis:
            sugestoes.append({
                'tipo': 'frete_gratis',
                'titulo': '🚚 Oportunidade de Frete Grátis',
                'descricao': f'Produtos acima de R$ 100 sem frete grátis. Considere oferecer frete grátis para aumentar vendas.',
                'prioridade': 6,
                'produtos': [
                    {
                        'mlb': item[0],
                        'title': item[1],
                        'price': float(item[2]) if item[2] else 0,
                        'frete': float(item[3]) if item[3] else 0
                    }
                    for item in produtos_sem_frete_gratis
                ]
            })
        
        return sugestoes
    
    def _analisar_produtos_inativos(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa produtos inativos e pausados."""
        sugestoes = []
        
        # Produtos pausados
        cursor.execute("""
            SELECT COUNT(*) FROM produtos 
            WHERE user_id = %s AND status = 'paused'
        """, (user_id,))
        
        produtos_pausados = cursor.fetchone()[0]
        
        if produtos_pausados > 0:
            sugestoes.append({
                'tipo': 'produtos_pausados',
                'titulo': '⏸️ Produtos Pausados',
                'descricao': f'Você tem {produtos_pausados} produtos pausados. Reative os que ainda são relevantes.',
                'prioridade': 4,
                'quantidade': produtos_pausados
            })
        
        return sugestoes
    
    def _analisar_sazonalidade(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa padrões sazonais de vendas."""
        sugestoes = []
        
        # Produtos com vendas concentradas em períodos específicos
        cursor.execute("""
            SELECT p.mlb, p.title, p.sold_quantity, p.updated_at
            FROM produtos p
            WHERE p.user_id = %s AND p.status = 'active' 
            AND p.title IS NOT NULL AND p.title != '' AND p.mlb IS NOT NULL AND p.mlb != ''
            AND p.sold_quantity > 20
            AND p.updated_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY p.sold_quantity DESC
            LIMIT 3
        """, (user_id,))
        
        produtos_tendencia = cursor.fetchall()
        
        if produtos_tendencia:
            sugestoes.append({
                'tipo': 'tendencia',
                'titulo': '📈 Produtos em Tendência',
                'descricao': f'Produtos com alta performance recente. Aproveite o momentum!',
                'prioridade': 7,
                'produtos': [
                    {
                        'mlb': item[0],
                        'title': item[1],
                        'vendas': item[2] or 0
                    }
                    for item in produtos_tendencia
                ]
            })
        
        return sugestoes
    
    def _analisar_custos(self, cursor, user_id: int) -> List[Dict[str, Any]]:
        """Analisa custos e sugere otimizações."""
        sugestoes = []
        
        # Produtos sem custos cadastrados
        cursor.execute("""
            SELECT COUNT(*) FROM produtos p
            LEFT JOIN custos c ON c.mlb = p.mlb
            WHERE p.user_id = %s AND c.mlb IS NULL AND p.status = 'active'
        """, (user_id,))
        
        produtos_sem_custos = cursor.fetchone()[0]
        
        if produtos_sem_custos > 0:
            sugestoes.append({
                'tipo': 'custos_faltando',
                'titulo': '💰 Custos Não Cadastrados',
                'descricao': f'Cadastre custos para {produtos_sem_custos} produtos ativos para análise precisa de lucratividade.',
                'prioridade': 8,
                'quantidade': produtos_sem_custos
            })
        
        return sugestoes
    
