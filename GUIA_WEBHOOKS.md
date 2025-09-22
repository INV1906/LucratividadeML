# 🔔 Guia de Configuração de Webhooks - Mercado Livre

## 📋 Visão Geral

Os webhooks do Mercado Livre permitem que sua aplicação receba notificações em tempo real sobre mudanças em produtos, pedidos, preços e outros eventos importantes. Isso mantém seus dados sempre atualizados automaticamente.

## 🚀 Funcionalidades Implementadas

### ✅ Endpoints Configurados
- **URL do Webhook**: `https://seu-dominio.com/webhook/mercadolivre`
- **Método**: POST
- **Timeout**: 500ms (requisito do Mercado Livre)
- **Resposta**: HTTP 200 OK

### ✅ Tópicos Suportados
1. **Items** - Mudanças em produtos (preço, estoque, status)
2. **Orders v2** - Mudanças em pedidos (novos pedidos, status)
3. **Price Suggestion** - Sugestões de preço do Mercado Livre
4. **Questions** - Perguntas de compradores

### ✅ Processamento Automático
- **Atualização de Produtos**: Preço, estoque, status, frete
- **Atualização de Pedidos**: Status, valores, comprador
- **Atualização de Sugestões**: Preços sugeridos pelo ML
- **Processamento de Perguntas**: Notificações de perguntas

## 🛠️ Configuração no Mercado Livre

### Passo 1: Acessar o Gerenciador de Aplicativos
1. Vá para: https://developers.mercadolibre.com.br/
2. Faça login com sua conta do Mercado Livre
3. Selecione seu aplicativo

### Passo 2: Configurar Notificações
1. No menu lateral, clique em **"Configuração de notificações"**
2. Cole a URL do webhook: `https://seu-dominio.com/webhook/mercadolivre`
3. Selecione os tópicos de interesse:
   - ✅ **Items** - para mudanças em produtos
   - ✅ **Orders v2** - para mudanças em pedidos
   - ✅ **Price Suggestion** - para sugestões de preço
   - ✅ **Questions** - para perguntas de compradores

### Passo 3: Salvar e Testar
1. Clique em **"Salvar"**
2. Use o botão **"Testar"** para verificar se está funcionando
3. Deve retornar status 200 OK

## 🧪 Testando Localmente

### Usando ngrok (Recomendado)
```bash
# Instalar ngrok
npm install -g ngrok

# Expor sua aplicação
ngrok http 3001

# Use a URL HTTPS fornecida pelo ngrok
# Exemplo: https://abc123.ngrok.io/webhook/mercadolivre
```

### Testando com Script
```bash
# Execute o script de teste
python teste_webhook.py
```

## 📊 Monitoramento

### Logs do Sistema
Os webhooks são processados em background e os logs aparecem no console:

```
🔔 Webhook recebido: {'resource': '/items/MLB123456', 'topic': 'items', ...}
📋 Processando notificação - Tópico: items, Recurso: /items/MLB123456, User: 123456
🔄 Atualizando item: MLB123456
✅ Item MLB123456 atualizado com sucesso
```

### Verificando Funcionamento
1. **Dashboard**: Verifique se os produtos estão sendo atualizados
2. **Logs**: Monitore o console da aplicação
3. **Banco de Dados**: Verifique se os dados estão sendo salvos

## 🔒 Segurança

### Validação de IPs
O sistema valida que as notificações vêm dos IPs oficiais do Mercado Livre:
- `54.88.218.97`
- `18.215.140.160`
- `18.213.114.129`
- `18.206.34.84`

### Timeout e Retry
- **Timeout**: 500ms (requisito do ML)
- **Retry**: Até 3 tentativas em caso de falha
- **Processamento**: Assíncrono para não bloquear a resposta

## 📈 Benefícios

### ✅ Atualizações Automáticas
- Produtos sempre atualizados
- Preços sincronizados
- Estoque em tempo real
- Status de pedidos atualizados

### ✅ Performance
- Não precisa fazer polling constante
- Atualizações instantâneas
- Reduz carga na API do ML

### ✅ Confiabilidade
- Sistema de retry automático
- Logs detalhados
- Validação de dados

## 🚨 Solução de Problemas

### Webhook não está funcionando
1. Verifique se a URL está acessível publicamente
2. Confirme se está usando HTTPS
3. Verifique os logs da aplicação
4. Teste com o script fornecido

### Notificações não chegam
1. Verifique se os tópicos estão habilitados no ML
2. Confirme se a URL está correta
3. Verifique se não há firewall bloqueando

### Erro 500 no webhook
1. Verifique os logs da aplicação
2. Confirme se o banco de dados está funcionando
3. Verifique se o token de acesso é válido

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs da aplicação
2. Execute o script de teste
3. Consulte a documentação do Mercado Livre
4. Verifique se todos os tópicos estão configurados

---

**🎉 Parabéns! Seus webhooks estão configurados e funcionando!**

Agora seus produtos serão sempre atualizados automaticamente com as informações mais recentes do Mercado Livre.
