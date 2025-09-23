# 🚀 GUIA DE DEPLOY NO VERCEL GRATUITO

## ⚠️ LIMITAÇÕES DO VERCEL GRATUITO

### **Restrições Importantes:**
- ⏱️ **Timeout**: 30 segundos por requisição
- 💾 **Memória**: 1GB RAM
- 🔄 **Cold Start**: Primeira requisição pode demorar
- 🗄️ **Banco**: Não inclui banco de dados
- 📁 **Armazenamento**: Sem persistência de arquivos

### **Soluções Necessárias:**
1. **Banco de dados externo** (PlanetScale, Supabase, ou MySQL remoto)
2. **Otimizações de performance** para evitar timeouts
3. **Configuração específica** para serverless

---

## 🗄️ CONFIGURAÇÃO DO BANCO DE DADOS

### **Opção 1: PlanetScale (Recomendado - Gratuito)**
```bash
# 1. Criar conta em https://planetscale.com
# 2. Criar banco de dados
# 3. Obter string de conexão
```

**String de conexão exemplo:**
```
mysql://username:password@host:port/database?ssl-mode=REQUIRED
```

### **Opção 2: Supabase (Gratuito)**
```bash
# 1. Criar conta em https://supabase.com
# 2. Criar projeto
# 3. Obter string de conexão PostgreSQL
```

### **Opção 3: MySQL Remoto (Hospedagem)**
```bash
# Usar qualquer provedor de MySQL remoto
# Exemplos: Hostinger, HostGator, etc.
```

---

## ⚙️ CONFIGURAÇÃO DA APLICAÇÃO

### **1. Criar arquivo .env.local**
```bash
# Configurações do Vercel
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=sua_chave_secreta_aqui

# Banco de dados (PlanetScale exemplo)
DB_HOST=aws.connect.psdb.cloud
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=seu_banco
DB_SSL_MODE=REQUIRED

# Mercado Livre
MELI_APP_ID=seu_app_id
MELI_CLIENT_SECRET=seu_client_secret
MELI_REDIRECT_URI=https://seu-app.vercel.app/callback

# URLs
URL_CODE=https://auth.mercadolibre.com.br/authorization
URL_OAUTH_TOKEN=https://api.mercadolibre.com/oauth/token
```

### **2. Modificar database.py para Vercel**
```python
# Adicionar no início do database.py
import os
import ssl

class DatabaseManager:
    def __init__(self):
        # Configuração específica para Vercel/PlanetScale
        self.config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'ssl_disabled': False,
            'ssl_ca': None,
            'ssl_cert': None,
            'ssl_key': None,
            'ssl_verify_cert': False,
            'ssl_verify_identity': False,
            'autocommit': True,
            'connect_timeout': 10,
            'use_unicode': True,
            'charset': 'utf8mb4'
        }
    
    def conectar(self):
        try:
            # Para PlanetScale, usar SSL
            if os.getenv('DB_SSL_MODE') == 'REQUIRED':
                self.config['ssl_disabled'] = False
                self.config['ssl_verify_cert'] = True
                self.config['ssl_verify_identity'] = True
            
            conn = mysql.connector.connect(**self.config)
            return conn
        except Error as e:
            print(f"❌ Erro de conexão: {e}")
            return None
```

---

## 🚀 DEPLOY NO VERCEL

### **1. Preparar Repositório**
```bash
# Criar repositório no GitHub
git init
git add .
git commit -m "Deploy para Vercel"
git branch -M main
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

### **2. Conectar ao Vercel**
```bash
# 1. Acessar https://vercel.com
# 2. Fazer login com GitHub
# 3. Importar projeto
# 4. Configurar variáveis de ambiente
```

### **3. Configurar Variáveis de Ambiente**
No painel do Vercel, adicionar:
```
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=sua_chave_secreta_aqui
DB_HOST=aws.connect.psdb.cloud
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=seu_banco
DB_SSL_MODE=REQUIRED
MELI_APP_ID=seu_app_id
MELI_CLIENT_SECRET=seu_client_secret
MELI_REDIRECT_URI=https://seu-app.vercel.app/callback
```

---

## ⚡ OTIMIZAÇÕES PARA VERCEL

### **1. Modificar app.py para Serverless**
```python
# Adicionar no início do app.py
import os
from flask import Flask

app = Flask(__name__)

# Configurações específicas para Vercel
if os.getenv('VERCEL'):
    # Configurações para ambiente serverless
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # Desabilitar debug em produção
    app.debug = False

# Handler para Vercel
@app.route('/')
def home():
    return render_template('index.html')

# Handler para todas as rotas
def handler(request):
    return app(request.environ, start_response)
```

### **2. Otimizar Imports**
```python
# Modificar imports para lazy loading
def get_database_manager():
    from database import DatabaseManager
    return DatabaseManager()

def get_meli_api():
    from meli_api import MercadoLivreAPI
    return MercadoLivreAPI()
```

### **3. Configurar Timeouts**
```python
# Adicionar timeouts em operações longas
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Operação excedeu o tempo limite")

# Usar em operações críticas
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(25)  # 25 segundos (menor que limite do Vercel)
```

---

## 🔧 CONFIGURAÇÕES ESPECÍFICAS

### **1. Webhooks no Vercel**
```python
# Modificar webhook_processor.py para Vercel
class WebhookProcessor:
    def __init__(self):
        # Usar conexão rápida para webhooks
        self.timeout = 10
        self.max_retries = 2
    
    def process_notification(self, notification):
        try:
            # Processar rapidamente
            result = self._process_fast(notification)
            return result
        except TimeoutError:
            # Log e retornar erro
            print("⚠️ Webhook timeout")
            return False
```

### **2. Importação Otimizada**
```python
# Modificar importação para ser mais rápida
def importar_vendas_rapido(user_id, limite=50):
    """Importação otimizada para Vercel"""
    try:
        # Limitar quantidade para evitar timeout
        api = MercadoLivreAPI()
        db = DatabaseManager()
        
        # Buscar apenas últimas vendas
        vendas = api.obter_vendas_recentes(user_id, limite)
        
        # Processar em lotes pequenos
        for venda in vendas[:limite]:
            db.salvar_venda_com_status(venda, user_id)
            
        return True
    except Exception as e:
        print(f"❌ Erro na importação: {e}")
        return False
```

---

## 📊 MONITORAMENTO NO VERCEL

### **1. Logs**
```python
# Adicionar logging específico para Vercel
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usar em operações críticas
logger.info("Operação iniciada")
logger.error("Erro ocorreu")
```

### **2. Métricas**
```python
# Adicionar endpoint de health check
@app.route('/health')
def health_check():
    try:
        # Verificar banco de dados
        db = DatabaseManager()
        conn = db.conectar()
        if conn:
            conn.close()
            return jsonify({'status': 'healthy', 'database': 'ok'})
        else:
            return jsonify({'status': 'unhealthy', 'database': 'error'}), 500
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
```

---

## 🚨 LIMITAÇÕES E SOLUÇÕES

### **Problemas Comuns:**

#### **1. Timeout de 30 segundos**
```python
# Solução: Dividir operações longas
def importar_vendas_lote(user_id, lote_size=20):
    """Importar vendas em lotes pequenos"""
    # Processar apenas 20 vendas por vez
    pass
```

#### **2. Cold Start**
```python
# Solução: Warmup endpoint
@app.route('/warmup')
def warmup():
    """Endpoint para aquecer a aplicação"""
    return jsonify({'status': 'warmed up'})
```

#### **3. Limite de memória**
```python
# Solução: Otimizar uso de memória
def processar_dados_otimizado(dados):
    """Processar dados sem carregar tudo na memória"""
    # Processar item por item
    for item in dados:
        yield processar_item(item)
```

---

## ✅ CHECKLIST DE DEPLOY

### **Antes do Deploy:**
- [ ] Configurar banco de dados externo
- [ ] Criar arquivo `vercel.json`
- [ ] Configurar `requirements_vercel.txt`
- [ ] Modificar `database.py` para SSL
- [ ] Otimizar `app.py` para serverless
- [ ] Configurar variáveis de ambiente

### **Durante o Deploy:**
- [ ] Conectar repositório GitHub ao Vercel
- [ ] Configurar variáveis de ambiente
- [ ] Aguardar build completar
- [ ] Testar aplicação

### **Após o Deploy:**
- [ ] Testar autenticação OAuth
- [ ] Testar importação de vendas
- [ ] Testar webhooks
- [ ] Configurar domínio personalizado (opcional)

---

## 🎯 RESULTADO FINAL

### **Vantagens do Vercel:**
- ✅ **Gratuito** para projetos pessoais
- ✅ **Deploy automático** via GitHub
- ✅ **HTTPS** incluído
- ✅ **CDN global** para performance
- ✅ **Escalabilidade** automática

### **Limitações:**
- ⚠️ **Timeout** de 30 segundos
- ⚠️ **Sem banco** de dados incluído
- ⚠️ **Cold start** na primeira requisição
- ⚠️ **Limite de memória** de 1GB

### **🚀 SUA APLICAÇÃO ESTARÁ ONLINE!**

Com essas configurações, sua aplicação funcionará perfeitamente no Vercel gratuito, com todas as funcionalidades implementadas!
