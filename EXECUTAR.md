# 🚀 Como Executar a Aplicação

## ⚡ Início Rápido

### 1. Configuração Automática
```bash
python setup.py
```

### 2. Configuração Manual

#### Instalar dependências:
```bash
pip install -r requirements.txt
```

#### Configurar banco de dados:
1. Crie um banco MySQL: `mercadolivre_lucratividade`
2. Configure o arquivo `.env` com suas credenciais

#### Executar aplicação:
```bash
python app.py
```

## 🔧 Configuração Detalhada

### 1. Banco de Dados MySQL

```sql
CREATE DATABASE mercadolivre_lucratividade;
CREATE USER 'meli_user'@'localhost' IDENTIFIED BY 'sua_senha';
GRANT ALL PRIVILEGES ON mercadolivre_lucratividade.* TO 'meli_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Arquivo .env

```env
# Configurações do Mercado Livre
MELI_APP_ID=seu_app_id_aqui
MELI_CLIENT_SECRET=seu_client_secret_aqui
MELI_REDIRECT_URI=http://localhost:5000/callback

# Configurações do Banco de Dados
DB_HOST=localhost
DB_USER=meli_user
DB_PASSWORD=sua_senha
DB_NAME=mercadolivre_lucratividade

# Chave secreta do Flask
FLASK_SECRET_KEY=sua_chave_secreta_forte_aqui
```

### 3. Aplicação no Mercado Livre

1. Acesse: https://developers.mercadolibre.com/
2. Crie uma nova aplicação
3. Configure a URL de callback: `http://localhost:5000/callback`
4. Copie o App ID e Client Secret para o arquivo `.env`

## 🌐 Acessando a Aplicação

1. Execute: `python app.py`
2. Acesse: http://localhost:5000
3. Clique em "Conectar com Mercado Livre"
4. Autorize a aplicação
5. Comece a usar!

## 📊 Funcionalidades Principais

### Dashboard
- Visão geral das vendas
- Métricas de performance
- Gráficos interativos

### Produtos
- Lista de todos os produtos
- Análise individual de lucratividade
- Filtros e busca

### Vendas
- Histórico de vendas
- Análise de lucratividade por venda
- Métricas de performance

### Análise
- Relatórios avançados
- Gráficos de tendências
- Meta de vendas

### Importar
- Sincronização com Mercado Livre
- Importação de produtos e vendas
- Atualização automática de dados

## 🐛 Solução de Problemas

### Erro de conexão com banco
```bash
# Verificar se MySQL está rodando
sudo service mysql start  # Linux
brew services start mysql  # Mac
net start mysql  # Windows
```

### Erro de dependências
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt
```

### Erro de permissões
```bash
# Dar permissões de execução
chmod +x setup.py
chmod +x exemplo_uso.py
```

## 🔄 Atualizações

Para atualizar a aplicação:
```bash
git pull origin main
pip install --upgrade -r requirements.txt
python app.py
```

## 📱 Acesso Mobile

A aplicação é responsiva e funciona em dispositivos móveis:
- Acesse pelo navegador do celular
- Interface adaptada para touch
- Gráficos otimizados para mobile

## 🔒 Segurança

- Tokens OAuth seguros
- Dados criptografados
- Conexão HTTPS recomendada para produção
- Backup regular do banco de dados

## 📈 Performance

- Cache de dados da API
- Consultas otimizadas
- Interface responsiva
- Carregamento assíncrono

---

**🎯 Pronto para começar! Sua análise de lucratividade está a um clique de distância.**
