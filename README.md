# 📊 Aplicação de Lucratividade do Mercado Livre

Uma aplicação web completa para análise de lucratividade de vendedores do Mercado Livre, desenvolvida em Python com Flask.

## 🚀 Funcionalidades

### 📈 Análise de Lucratividade
- **Cálculo automático de margens de lucro** por produto e venda
- **Análise de custos** (produto, embalagem, frete, taxas, impostos)
- **ROI e métricas financeiras** detalhadas
- **Relatórios visuais** com gráficos e dashboards

### 🛒 Gestão de Produtos
- **Importação automática** de produtos do Mercado Livre
- **Análise individual** de cada produto
- **Sugestões de otimização** de preços
- **Controle de estoque** e vendas

### 💰 Gestão de Vendas
- **Importação de vendas** do Mercado Livre
- **Análise de lucratividade** por venda
- **Histórico completo** de transações
- **Métricas de performance** de vendas

### 📊 Dashboard e Relatórios
- **Dashboard interativo** com métricas principais
- **Gráficos e visualizações** em tempo real
- **Análise de tendências** e performance
- **Exportação de relatórios** (PDF, Excel, CSV)

## 🛠️ Tecnologias Utilizadas

- **Backend**: Python 3.8+, Flask
- **Banco de Dados**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Gráficos**: Chart.js
- **APIs**: Mercado Livre API
- **Autenticação**: OAuth 2.0

## 📋 Pré-requisitos

- Python 3.8 ou superior
- MySQL 5.7 ou superior
- Conta de desenvolvedor no Mercado Livre

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd mercadolivre-lucratividade
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
1. Crie um banco MySQL chamado `mercadolivre_lucratividade`
2. Configure as credenciais no arquivo `.env`

### 5. Configure as variáveis de ambiente
Copie o arquivo `env_example.txt` para `.env` e configure:

```env
# Configurações do Mercado Livre
MELI_APP_ID=seu_app_id_aqui
MELI_CLIENT_SECRET=seu_client_secret_aqui
MELI_REDIRECT_URI=http://localhost:5000/callback
URL_CODE=https://auth.mercadolibre.com.br/authorization
URL_OAUTH_TOKEN=https://api.mercadolibre.com/oauth/token

# Configurações do Banco de Dados
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=mercadolivre_lucratividade

# Chave secreta do Flask
FLASK_SECRET_KEY=sua_chave_secreta_aqui
```

### 6. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🔑 Configuração do Mercado Livre

### 1. Crie uma aplicação no Mercado Livre
1. Acesse [https://developers.mercadolibre.com/](https://developers.mercadolibre.com/)
2. Faça login com sua conta do Mercado Livre
3. Crie uma nova aplicação
4. Anote o `App ID` e `Client Secret`

### 2. Configure a URL de callback
- URL de callback: `http://localhost:5000/callback`
- Para produção, use sua URL de domínio

## 📖 Como Usar

### 1. Primeiro Acesso
1. Acesse `http://localhost:5000`
2. Clique em "Conectar com Mercado Livre"
3. Autorize a aplicação
4. Você será redirecionado para o dashboard

### 2. Importar Dados
1. Vá para a página "Importar"
2. Clique em "Importar Produtos" para sincronizar seus produtos
3. Clique em "Importar Vendas" para sincronizar suas vendas
4. Os custos são calculados automaticamente

### 3. Analisar Lucratividade
1. **Dashboard**: Veja um resumo geral da sua performance
2. **Produtos**: Analise a lucratividade de cada produto
3. **Vendas**: Analise a lucratividade de cada venda
4. **Análise**: Veja relatórios avançados e insights

## 📁 Estrutura do Projeto

```
mercadolivre-lucratividade/
├── app.py                 # Aplicação principal Flask
├── database.py           # Gerenciamento do banco de dados
├── meli_api.py          # Integração com API do Mercado Livre
├── profitability.py     # Cálculos de lucratividade
├── requirements.txt     # Dependências Python
├── env_example.txt     # Exemplo de configuração
├── templates/          # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   ├── produtos.html
│   ├── vendas.html
│   ├── analise.html
│   ├── importar.html
│   ├── detalhes_produto.html
│   ├── detalhes_venda.html
│   ├── 404.html
│   └── 500.html
└── README.md
```

## 🔧 Configuração Avançada

### Personalização de Custos
Você pode personalizar os custos editando o arquivo `profitability.py`:

```python
# Exemplo de personalização
custos_padrao = {
    'imposto_perc': 14.0,  # 14% de imposto
    'embalagem_por_item': 5.0,  # R$ 5 por item
    'custo_por_item': 0,  # Será calculado por item
    'custos_extras': 0
}
```

### Configuração do Banco de Dados
A aplicação cria automaticamente as tabelas necessárias na primeira execução.

## 🚀 Deploy em Produção

### 1. Configure variáveis de ambiente
```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=sua_chave_secreta_forte
```

### 2. Configure o servidor web
Recomendamos usar Gunicorn com Nginx:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 3. Configure HTTPS
Para produção, configure SSL/TLS para segurança.

## 🐛 Solução de Problemas

### Erro de conexão com banco de dados
- Verifique se o MySQL está rodando
- Confirme as credenciais no arquivo `.env`
- Verifique se o banco de dados existe

### Erro de autenticação OAuth
- Verifique se o `App ID` e `Client Secret` estão corretos
- Confirme se a URL de callback está configurada corretamente
- Verifique se a aplicação está ativa no Mercado Livre

### Erro de importação de dados
- Verifique se o token de acesso é válido
- Confirme se a conta tem permissões necessárias
- Verifique a conexão com a internet

## 📊 Métricas Calculadas

### Por Produto
- Preço de venda
- Custo total (produto + embalagem + extras)
- Custos de venda (taxas ML + frete + impostos)
- Lucro bruto
- Margem líquida
- ROI (Return on Investment)

### Por Venda
- Receita total
- Custo total da venda
- Lucro líquido
- Margem de lucro
- Análise por item

### Gerais
- Ticket médio
- Total de vendas
- Produtos ativos
- Performance por categoria

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através do email.

## 🔄 Atualizações

### Versão 1.0.0
- ✅ Análise básica de lucratividade
- ✅ Importação de produtos e vendas
- ✅ Dashboard interativo
- ✅ Relatórios visuais
- ✅ Interface responsiva

### Próximas versões
- 🔄 Análise de concorrência
- 🔄 Sugestões automáticas de preços
- 🔄 Integração com outros marketplaces
- 🔄 API REST para integrações
- 🔄 Notificações em tempo real

---

**Desenvolvido com ❤️ para vendedores do Mercado Livre**
