# Resposta: Sessões Simultâneas

## Resumo da Situação Atual

### ✅ **Duas contas diferentes podem funcionar simultaneamente?**
**SIM** - O sistema permite que usuários diferentes tenham sessões ativas simultaneamente.

### ❌ **Duas pessoas podem usar a mesma conta simultaneamente?**
**NÃO** (por padrão) - O sistema atual encerra a sessão anterior quando uma nova sessão é criada para o mesmo usuário.

## Configurações Disponíveis

### Modo Padrão (Atual)
```python
# Em configuracao_sessoes.py
PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO = False
MAX_SESSOES_POR_USUARIO = 3
TEMPO_EXPIRACAO_SESSAO_HORAS = 24
```

**Comportamento:**
- ✅ Usuários diferentes podem ter sessões simultâneas
- ❌ Mesmo usuário só pode ter 1 sessão ativa
- 🔄 Nova sessão encerra a anterior automaticamente

### Modo Múltiplas Sessões (Opcional)
```python
# Para permitir múltiplas sessões do mesmo usuário:
PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO = True
MAX_SESSOES_POR_USUARIO = 3  # Máximo de 3 sessões simultâneas
TEMPO_EXPIRACAO_SESSAO_HORAS = 24
```

**Comportamento:**
- ✅ Usuários diferentes podem ter sessões simultâneas
- ✅ Mesmo usuário pode ter até 3 sessões simultâneas
- 🔄 Sessões antigas são removidas quando excede o limite

## Como Alterar o Comportamento

### 1. Para Permitir Múltiplas Sessões do Mesmo Usuário

Edite o arquivo `configuracao_sessoes.py`:

```python
class ConfiguracaoSessoes:
    PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO = True  # Mude para True
    MAX_SESSOES_POR_USUARIO = 3  # Ajuste conforme necessário
    TEMPO_EXPIRACAO_SESSAO_HORAS = 24  # Ajuste conforme necessário
```

### 2. Executar Migrações

```bash
python executar_migracoes.py
```

### 3. Reiniciar a Aplicação

```bash
python app.py
```

## Cenários de Uso

### Cenário 1: Uso Individual (Padrão)
- **Usuário A** faz login no navegador 1 → Sessão criada
- **Usuário A** faz login no navegador 2 → Sessão anterior encerrada
- **Usuário B** faz login no navegador 3 → Sessão criada
- **Resultado:** Usuário A (1 sessão) + Usuário B (1 sessão)

### Cenário 2: Uso Compartilhado (Configurável)
- **Usuário A** faz login no navegador 1 → Sessão 1 criada
- **Usuário A** faz login no navegador 2 → Sessão 2 criada
- **Usuário A** faz login no navegador 3 → Sessão 3 criada
- **Usuário A** faz login no navegador 4 → Sessão 1 encerrada (mais antiga)
- **Resultado:** Usuário A (3 sessões ativas)

## Vantagens de Cada Modo

### Modo Padrão (1 sessão por usuário)
- ✅ **Segurança:** Previne uso não autorizado
- ✅ **Simplicidade:** Comportamento previsível
- ✅ **Recursos:** Menor uso de memória/banco
- ❌ **Flexibilidade:** Não permite uso compartilhado

### Modo Múltiplas Sessões
- ✅ **Flexibilidade:** Permite uso em múltiplos dispositivos
- ✅ **Conveniência:** Não desloga outros dispositivos
- ✅ **Produtividade:** Múltiplas pessoas podem usar a mesma conta
- ❌ **Segurança:** Maior risco de uso não autorizado
- ❌ **Complexidade:** Mais difícil de gerenciar

## Recomendações

### Para Uso Pessoal/Individual
- **Use o modo padrão** (1 sessão por usuário)
- Mais seguro e simples

### Para Uso Empresarial/Compartilhado
- **Use o modo múltiplas sessões**
- Configure limite adequado (ex: 3-5 sessões)
- Monitore uso regularmente

### Para Desenvolvimento/Teste
- **Use o modo múltiplas sessões**
- Facilita testes com múltiplos usuários

## Arquivos Modificados

1. `database.py` - Adicionadas tabelas de autenticação
2. `auth_manager.py` - Melhorado gerenciamento de sessões
3. `app.py` - Atualizado para usar configurações
4. `configuracao_sessoes.py` - Arquivo de configuração (novo)
5. `executar_migracoes.py` - Script de migração (novo)

## Próximos Passos

1. Execute as migrações: `python executar_migracoes.py`
2. Teste o comportamento atual
3. Se necessário, altere a configuração em `configuracao_sessoes.py`
4. Reinicie a aplicação
5. Teste novamente
