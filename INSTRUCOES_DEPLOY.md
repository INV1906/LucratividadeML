# Instruções para Deploy no Servidor AWS

## Arquivos Modificados/Criados

### Arquivos que precisam ser enviados via WinSCP:

1. **`database.py`** - Atualizado com tabelas de autenticação
2. **`auth_manager.py`** - Melhorado com gerenciamento de sessões
3. **`app.py`** - Atualizado para usar configurações de sessão
4. **`configuracao_sessoes.py`** - NOVO - Arquivo de configuração
5. **`executar_migracoes.py`** - NOVO - Script de migração

### Arquivos que NÃO precisam ser enviados:
- `teste_local.py` - Apenas para teste local
- `RESPOSTA_SESSOES_SIMULTANEAS.md` - Documentação

## Passos para Deploy

### 1. Fazer Backup (Recomendado)
```bash
# No servidor, fazer backup dos arquivos atuais
sudo cp -r /home/ec2-user/mercadolivre /home/ec2-user/mercadolivre_backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Parar o Serviço
```bash
sudo systemctl stop mercadolivre-app
```

### 3. Fazer Upload dos Arquivos
Via WinSCP, enviar os seguintes arquivos para `/home/ec2-user/mercadolivre/`:
- `database.py`
- `auth_manager.py` 
- `app.py`
- `configuracao_sessoes.py`
- `executar_migracoes.py`

### 4. Executar Migrações no Servidor
```bash
cd /home/ec2-user/mercadolivre
python3 executar_migracoes.py
```

### 5. Verificar Permissões
```bash
sudo chown -R ec2-user:ec2-user /home/ec2-user/mercadolivre
sudo chmod +x /home/ec2-user/mercadolivre/executar_migracoes.py
```

### 6. Reiniciar o Serviço
```bash
sudo systemctl start mercadolivre-app
sudo systemctl status mercadolivre-app
```

### 7. Verificar Logs
```bash
sudo journalctl -u mercadolivre-app -f
```

## Configurações Disponíveis

### Modo Padrão (Atual)
- ✅ Usuários diferentes podem ter sessões simultâneas
- ❌ Mesmo usuário só pode ter 1 sessão ativa
- 🔄 Nova sessão encerra a anterior

### Para Permitir Múltiplas Sessões do Mesmo Usuário
Editar `/home/ec2-user/mercadolivre/configuracao_sessoes.py`:
```python
PERMITIR_MULTIPLAS_SESSOES_MESMO_USUARIO = True
MAX_SESSOES_POR_USUARIO = 3
TEMPO_EXPIRACAO_SESSAO_HORAS = 24
```

Depois reiniciar:
```bash
sudo systemctl restart mercadolivre-app
```

## Verificação de Funcionamento

### 1. Testar Conectividade
```bash
curl http://localhost:5000/
```

### 2. Testar Limpeza de Sessões
```bash
curl -X POST http://localhost:5000/debug/limpar-sessoes
```

### 3. Verificar Logs
```bash
sudo journalctl -u mercadolivre-app --since "5 minutes ago"
```

## Rollback (Se Necessário)

Se algo der errado, restaurar backup:
```bash
sudo systemctl stop mercadolivre-app
sudo rm -rf /home/ec2-user/mercadolivre
sudo mv /home/ec2-user/mercadolivre_backup_* /home/ec2-user/mercadolivre
sudo systemctl start mercadolivre-app
```

## Resumo das Correções

1. **Problema Original**: Sincronização usava dados da primeira conta
2. **Causa**: Sessões não eram gerenciadas corretamente
3. **Solução**: Sistema de sessões robusto com configurações flexíveis
4. **Resultado**: 
   - ✅ Múltiplos usuários simultâneos funcionam
   - ✅ Cada usuário vê apenas seus próprios dados
   - ✅ Sessões são gerenciadas corretamente
   - ✅ Configuração flexível para diferentes cenários
