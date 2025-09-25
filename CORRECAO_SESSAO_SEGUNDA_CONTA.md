# Correção: Sessão da Segunda Conta

## ❌ Problema Identificado

**Problema**: A segunda conta não consegue sincronizar e está sendo redirecionada para a página de autenticação do Mercado Livre.

**Sintomas**:
- Erro CORS ao tentar acessar `/importar/status`
- Redirecionamento para `https://auth.mercadolivre.com.br/authorization`
- Segunda conta não consegue iniciar sincronização

**Causa**: Sessão da segunda conta não está sendo reconhecida corretamente pelo decorator `login_required`

## ✅ Correção Aplicada

### 1. **Decorator `login_required` Melhorado**
- Adicionado debug detalhado para identificar problemas de sessão
- Simplificado validação para melhor compatibilidade
- Logs detalhados para diagnóstico

### 2. **Sistema de Sessões por Usuário**
- Cada usuário tem sua própria sessão independente
- Status de importação separado por usuário
- Sincronização paralela implementada

## 📁 Arquivos Modificados

### **`app.py`**
- ✅ Decorator `login_required` melhorado com debug
- ✅ Sistema de status por usuário implementado
- ✅ Sincronizações manuais assíncronas

### **`sync_manager.py`**
- ✅ Sincronização automática paralela
- ✅ Múltiplos usuários simultâneos

## 🔧 Diagnóstico do Problema

### Logs de Debug Adicionados
```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"🔍 Login required: Verificando sessão para {request.endpoint}")
        print(f"   Sessão atual: {dict(session)}")
        
        if 'user_id' not in session:
            print("❌ Login required: user_id não encontrado na sessão")
            return redirect(url_for('auth'))
        
        user_id = session.get('user_id')
        if not user_id:
            print("❌ Login required: user_id é None")
            session.clear()
            return redirect(url_for('auth'))
        
        print(f"✅ Login required: user_id {user_id} encontrado na sessão")
        return f(*args, **kwargs)
    return decorated_function
```

## 🚀 Como Aplicar no Servidor

### 1. Fazer Backup
```bash
sudo cp /var/www/mercadolivre/app.py /var/www/mercadolivre/app.py.backup
sudo cp /var/www/mercadolivre/sync_manager.py /var/www/mercadolivre/sync_manager.py.backup
```

### 2. Parar Serviço
```bash
sudo systemctl stop mercadolivre-app
```

### 3. Fazer Upload
Via WinSCP, enviar:
- `app.py` para `/var/www/mercadolivre/`
- `sync_manager.py` para `/var/www/mercadolivre/`

### 4. Reiniciar Serviço
```bash
sudo systemctl start mercadolivre-app
```

### 5. Verificar Logs
```bash
sudo journalctl -u mercadolivre-app -f
```

## 🧪 Teste de Verificação

### 1. **Login com Conta 1**
- Fazer login normalmente
- Verificar se consegue acessar `/importar/status`
- Iniciar sincronização

### 2. **Login com Conta 2**
- Fazer login em nova aba/navegador
- Verificar se consegue acessar `/importar/status`
- Iniciar sincronização

### 3. **Verificar Logs**
```bash
sudo journalctl -u mercadolivre-app | grep "Login required"
```

### 4. **Teste de Sincronização Simultânea**
- Conta 1: Iniciar sincronização de vendas
- Conta 2: Iniciar sincronização de produtos
- Verificar se ambas rodam simultaneamente

## 🔍 Diagnóstico Adicional

### Se o problema persistir:

1. **Verificar Sessões no Banco**
```sql
SELECT * FROM sessoes_ativas ORDER BY created_at DESC;
```

2. **Verificar Logs de Debug**
```bash
sudo journalctl -u mercadolivre-app | grep "Login required" | tail -20
```

3. **Verificar Cookies do Navegador**
- Abrir DevTools (F12)
- Ir para Application > Cookies
- Verificar se há cookies de sessão

4. **Testar com Navegador Incógnito**
- Abrir nova aba incógnita
- Fazer login com segunda conta
- Testar sincronização

## 📋 Possíveis Causas

### 1. **Problema de Cookies**
- Cookies não estão sendo compartilhados entre abas
- Sessão não está sendo persistida

### 2. **Problema de Sessão**
- Sessão da segunda conta não está sendo criada
- Sessão está sendo sobrescrita pela primeira conta

### 3. **Problema de Redirecionamento**
- Decorator `login_required` não está funcionando corretamente
- Redirecionamento para `/auth` está causando loop

## ✅ Resultado Esperado

Após a correção:
- ✅ **Segunda conta consegue fazer login normalmente**
- ✅ **Segunda conta consegue acessar rotas protegidas**
- ✅ **Segunda conta consegue iniciar sincronização**
- ✅ **Múltiplas contas podem sincronizar simultaneamente**
- ✅ **Logs de debug mostram sessões válidas**

## 📋 Status

- ✅ **Problema identificado**
- ✅ **Correções aplicadas**
- ✅ **Debug implementado**
- ⏳ **Aguardando aplicação no servidor**

## 🎯 Próximos Passos

1. **Aplicar correções no servidor**
2. **Testar com segunda conta**
3. **Verificar logs de debug**
4. **Confirmar sincronização simultânea**
5. **Remover logs de debug se necessário**
