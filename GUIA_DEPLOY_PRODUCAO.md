# 🚀 GUIA DE DEPLOY PARA PRODUÇÃO

## 📋 CHECKLIST PRÉ-DEPLOY

### ✅ **1. Limpeza de Código**
```bash
# Execute o script de limpeza
python limpar_producao.py
```

### ✅ **2. Configurações de Produção**
- [ ] Configurar `.env.production`
- [ ] Configurar banco de dados de produção
- [ ] Configurar domínio de produção
- [ ] Configurar SSL/HTTPS

### ✅ **3. Testes Finais**
- [ ] Testar autenticação OAuth
- [ ] Testar importação de vendas
- [ ] Testar webhooks
- [ ] Testar sincronização incremental

---

## 🖥️ CONFIGURAÇÃO DO SERVIDOR

### **Requisitos Mínimos**
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Python**: 3.11+
- **RAM**: 2GB mínimo, 4GB recomendado
- **CPU**: 2 cores mínimo
- **Disco**: 20GB mínimo
- **Banco**: MySQL 8.0+ ou MariaDB 10.6+

### **Instalação de Dependências**
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Instalar MySQL
sudo apt install mysql-server -y

# Instalar Nginx
sudo apt install nginx -y

# Instalar Git
sudo apt install git -y
```

---

## 🗄️ CONFIGURAÇÃO DO BANCO DE DADOS

### **1. Criar Banco e Usuário**
```sql
-- Conectar ao MySQL
sudo mysql -u root -p

-- Criar banco de dados
CREATE DATABASE mercadolivre_lucratividade CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar usuário
CREATE USER 'ml_user'@'localhost' IDENTIFIED BY 'senha_super_segura';

-- Conceder permissões
GRANT ALL PRIVILEGES ON mercadolivre_lucratividade.* TO 'ml_user'@'localhost';
FLUSH PRIVILEGES;

-- Sair
EXIT;
```

### **2. Configurar MySQL**
```bash
# Configurar segurança
sudo mysql_secure_installation

# Configurar para aceitar conexões
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

Adicionar/modificar:
```ini
[mysqld]
bind-address = 0.0.0.0
max_connections = 200
innodb_buffer_pool_size = 1G
```

```bash
# Reiniciar MySQL
sudo systemctl restart mysql
sudo systemctl enable mysql
```

---

## 📦 DEPLOY DA APLICAÇÃO

### **1. Preparar Ambiente**
```bash
# Criar usuário para a aplicação
sudo adduser --system --group mlapp
sudo mkdir -p /opt/mlapp
sudo chown mlapp:mlapp /opt/mlapp

# Clonar código
cd /opt/mlapp
sudo -u mlapp git clone https://github.com/seu-usuario/seu-repositorio.git .

# Criar ambiente virtual
sudo -u mlapp python3.11 -m venv venv
sudo -u mlapp ./venv/bin/pip install --upgrade pip
```

### **2. Instalar Dependências**
```bash
# Instalar dependências de produção
sudo -u mlapp ./venv/bin/pip install -r requirements.production.txt

# Ou instalar manualmente
sudo -u mlapp ./venv/bin/pip install Flask==2.2.5 mysql-connector-python==8.1.0 python-dotenv==1.0.0 requests==2.31.0 gunicorn==21.2.0
```

### **3. Configurar Aplicação**
```bash
# Copiar configurações
sudo -u mlapp cp .env.production .env

# Editar configurações
sudo -u mlapp nano .env
```

Configurar variáveis:
```bash
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=sua_chave_super_segura_aqui
DB_HOST=localhost
DB_USER=ml_user
DB_PASSWORD=senha_super_segura
DB_NAME=mercadolivre_lucratividade
MELI_APP_ID=seu_app_id
MELI_CLIENT_SECRET=seu_client_secret
MELI_REDIRECT_URI=https://seu-dominio.com/callback
PORT=5000
```

### **4. Criar Serviço Systemd**
```bash
sudo nano /etc/systemd/system/mlapp.service
```

Conteúdo:
```ini
[Unit]
Description=MercadoLivre Lucratividade App
After=network.target mysql.service

[Service]
Type=exec
User=mlapp
Group=mlapp
WorkingDirectory=/opt/mlapp
Environment=PATH=/opt/mlapp/venv/bin
ExecStart=/opt/mlapp/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl enable mlapp
sudo systemctl start mlapp
sudo systemctl status mlapp
```

---

## 🌐 CONFIGURAÇÃO DO NGINX

### **1. Configurar Site**
```bash
sudo nano /etc/nginx/sites-available/mlapp
```

Conteúdo:
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    # Redirecionar para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com www.seu-dominio.com;

    # Certificado SSL
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Configurações de segurança
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Proxy para aplicação
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Arquivos estáticos (se houver)
    location /static {
        alias /opt/mlapp/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/mlapp_access.log;
    error_log /var/log/nginx/mlapp_error.log;
}
```

### **2. Ativar Site**
```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/mlapp /etc/nginx/sites-enabled/

# Remover site padrão
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔒 CONFIGURAÇÃO SSL

### **1. Instalar Certbot**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### **2. Obter Certificado**
```bash
# Substituir seu-dominio.com pelo seu domínio real
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

### **3. Renovação Automática**
```bash
# Testar renovação
sudo certbot renew --dry-run

# Configurar cron para renovação automática
sudo crontab -e
```

Adicionar linha:
```bash
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 MONITORAMENTO E LOGS

### **1. Configurar Logs**
```bash
# Criar diretório de logs
sudo mkdir -p /var/log/mlapp
sudo chown mlapp:mlapp /var/log/mlapp

# Configurar rotação de logs
sudo nano /etc/logrotate.d/mlapp
```

Conteúdo:
```
/var/log/mlapp/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 mlapp mlapp
    postrotate
        systemctl reload mlapp
    endscript
}
```

### **2. Monitoramento**
```bash
# Verificar status dos serviços
sudo systemctl status mlapp
sudo systemctl status nginx
sudo systemctl status mysql

# Verificar logs
sudo journalctl -u mlapp -f
sudo tail -f /var/log/nginx/mlapp_error.log
```

---

## 🔄 BACKUP E MANUTENÇÃO

### **1. Script de Backup**
```bash
sudo nano /opt/backup_mlapp.sh
```

Conteúdo:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="mercadolivre_lucratividade"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco de dados
mysqldump -u ml_user -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# Backup dos arquivos da aplicação
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz /opt/mlapp

# Remover backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

```bash
# Tornar executável
sudo chmod +x /opt/backup_mlapp.sh

# Configurar cron para backup diário
sudo crontab -e
```

Adicionar linha:
```bash
0 2 * * * /opt/backup_mlapp.sh
```

### **2. Atualizações**
```bash
# Script de atualização
sudo nano /opt/update_mlapp.sh
```

Conteúdo:
```bash
#!/bin/bash
cd /opt/mlapp

# Backup antes da atualização
/opt/backup_mlapp.sh

# Atualizar código
sudo -u mlapp git pull origin main

# Atualizar dependências
sudo -u mlapp ./venv/bin/pip install -r requirements.production.txt

# Reiniciar aplicação
sudo systemctl restart mlapp

echo "Atualização concluída"
```

---

## ✅ VERIFICAÇÃO FINAL

### **1. Testes de Funcionamento**
```bash
# Verificar se todos os serviços estão rodando
sudo systemctl status mlapp nginx mysql

# Testar conectividade
curl -I https://seu-dominio.com

# Verificar logs
sudo journalctl -u mlapp --since "1 hour ago"
```

### **2. Configurações do Mercado Livre**
- [ ] Atualizar URL de callback no painel do ML
- [ ] Testar autenticação OAuth
- [ ] Configurar webhooks
- [ ] Testar importação de dados

### **3. Monitoramento Contínuo**
- [ ] Configurar alertas de erro
- [ ] Monitorar performance
- [ ] Verificar backups
- [ ] Atualizar dependências regularmente

---

## 🆘 SOLUÇÃO DE PROBLEMAS

### **Problemas Comuns**

#### **1. Aplicação não inicia**
```bash
# Verificar logs
sudo journalctl -u mlapp -f

# Verificar configurações
sudo -u mlapp cat /opt/mlapp/.env

# Verificar dependências
sudo -u mlapp ./venv/bin/pip list
```

#### **2. Erro de banco de dados**
```bash
# Verificar conexão
mysql -u ml_user -p -h localhost mercadolivre_lucratividade

# Verificar permissões
sudo mysql -u root -p
SHOW GRANTS FOR 'ml_user'@'localhost';
```

#### **3. Erro de SSL**
```bash
# Verificar certificado
sudo certbot certificates

# Renovar certificado
sudo certbot renew --force-renewal
```

---

## 🎉 CONCLUSÃO

Sua aplicação está agora configurada para produção com:

- ✅ **Servidor robusto** com Nginx + Gunicorn
- ✅ **SSL/HTTPS** configurado
- ✅ **Banco de dados** otimizado
- ✅ **Backup automático** configurado
- ✅ **Monitoramento** de logs
- ✅ **Segurança** implementada

**Sua aplicação está PRONTA PARA PRODUÇÃO!** 🚀
