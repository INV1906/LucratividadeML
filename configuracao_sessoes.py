#!/usr/bin/env python3
"""
Configuração de Sessões - Permite configurar comportamento de sessões simultâneas
"""

class ConfiguracaoSessoes:
    """Configurações para gerenciamento de sessões"""
    
    # Configurações atuais
    PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO = False  # Mude para True para permitir
    MAX_SESSOES_POR_USUARIO = 3  # Máximo de sessões simultâneas por usuário
    TEMPO_EXPIRACAO_SESSAO_HORAS = 24  # Tempo de expiração da sessão
    
    @classmethod
    def deve_permitir_multiplas_sessoes(cls):
        """Verifica se deve permitir múltiplas sessões para o mesmo usuário"""
        return cls.PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO
    
    @classmethod
    def obter_max_sessoes_por_usuario(cls):
        """Retorna o número máximo de sessões por usuário"""
        return cls.MAX_SESSOES_POR_USUARIO
    
    @classmethod
    def obter_tempo_expiracao_horas(cls):
        """Retorna o tempo de expiração em horas"""
        return cls.TEMPO_EXPIRACAO_SESSAO_HORAS

# Exemplo de uso:
# Para permitir múltiplas sessões simultâneas para o mesmo usuário:
# ConfiguracaoSessoes.PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO = True
