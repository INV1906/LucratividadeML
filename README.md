# 📊 Aplicação de Lucratividade do Mercado Livre

Uma aplicação web para análise de lucratividade de vendedores do Mercado Livre, desenvolvida em Python com Flask.

## 🚀 Funcionalidades

- **Análise de lucratividade** por produto e venda
- **Importação automática** de dados do Mercado Livre
- **Dashboard interativo** com métricas principais
- **Cálculo de custos** (produto, embalagem, frete, taxas, impostos)
- **Relatórios visuais** com gráficos

## 🛠️ Tecnologias

- **Backend**: Python 3.8+, Flask
- **Banco de Dados**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **APIs**: Mercado Livre API

## 📋 Pré-requisitos

- Python 3.8 ou superior
- MySQL 5.7 ou superior
- Conta de desenvolvedor no Mercado Livre

## 🔧 Instalação Rápida

### 1. Instale as dependências
```bash
pip install -r requirements.txt
```

### 2. Configure o banco de dados
1. Crie um banco MySQL chamado `sistema_ml`
2. Configure as credenciais no arquivo `.env`

### 3. Configure as variáveis de ambiente
Copie o arquivo `config_exemplo.env` para `.env` e configure:

```env
# Configurações do Mercado Livre
MELI_APP_ID=seu_app_id_aqui
MELI_CLIENT_SECRET=seu_client_secret_aqui
MELI_REDIRECT_URI=http://localhost:5000/callback

# Configurações do Banco de Dados
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha_mysql
DB_NAME=sistema_ml

# Chave secreta do Flask
FLASK_SECRET_KEY=sua_chave_secreta_aqui
```

### 4. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em `http://localhost:5000`

## 🔑 Configuração do Mercado Livre

1. Acesse [https://developers.mercadolibre.com/](https://developers.mercadolibre.com/)
2. Crie uma nova aplicação
3. Configure a URL de callback: `http://localhost:5000/callback`
4. Anote o `App ID` e `Client Secret`

## 📖 Como Usar

1. Acesse `http://localhost:5000`
2. Clique em "Conectar com Mercado Livre"
3. Autorize a aplicação
4. Importe seus produtos e vendas
5. Analise a lucratividade no dashboard

## 🐛 Solução de Problemas

- **Erro de conexão com banco**: Verifique se o MySQL está rodando e as credenciais estão corretas
- **Erro de autenticação**: Verifique se o `App ID` e `Client Secret` estão corretos
- **Erro de importação**: Verifique se o token de acesso é válido

---

**Desenvolvido para vendedores do Mercado Livre** ❤️
