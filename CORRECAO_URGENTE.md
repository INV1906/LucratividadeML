# Correção Urgente - Erro de Variável

## ❌ Problema Identificado

**Erro**: `UnboundLocalError: local variable 'conn' referenced before assignment`

**Localização**: `auth_manager.py` - método `criar_sessao`

**Causa**: A variável `conn` não foi inicializada antes do bloco `try`

## ✅ Correção Aplicada

### Arquivo: `auth_manager.py`

**Mudança necessária**: Inicializar `conn = None` antes do bloco `try` em 3 métodos:

1. `criar_sessao()`
2. `verificar_limite_sessoes_usuario()`
3. `encerrar_sessoes_antigas_usuario()`

### Código Corrigido:

```python
def criar_sessao(self, user_id: int, login_type: str, ip_address: str = None, user_agent: str = None) -> str:
    """Cria nova sessão para o usuário."""
    conn = None  # ← ADICIONAR ESTA LINHA
    try:
        # ... resto do código
```

## 🚀 Como Aplicar no Servidor

### 1. Fazer Backup
```bash
sudo cp /var/www/mercadolivre/auth_manager.py /var/www/mercadolivre/auth_manager.py.backup
```

### 2. Parar Serviço
```bash
sudo systemctl stop mercadolivre-app
```

### 3. Fazer Upload do Arquivo Corrigido
Via WinSCP, enviar `auth_manager.py` para `/var/www/mercadolivre/`

### 4. Reiniciar Serviço
```bash
sudo systemctl start mercadolivre-app
```

### 5. Verificar Logs
```bash
sudo journalctl -u mercadolivre-app -f
```

## ✅ Teste de Verificação

Após aplicar a correção, testar:

```bash
curl -X POST http://localhost:5000/debug/limpar-sessoes
```

**Resposta esperada**: `{"message":"Todas as sessões foram limpas","success":true}`

## 📋 Status

- ✅ **Correção identificada e aplicada localmente**
- ✅ **Teste local realizado com sucesso**
- ⏳ **Aguardando aplicação no servidor**

## 🎯 Resultado Esperado

Após a correção:
- ✅ Login via OAuth funcionará corretamente
- ✅ Sistema de sessões operacional
- ✅ Múltiplos usuários funcionando
- ✅ Sincronização correta por usuário
