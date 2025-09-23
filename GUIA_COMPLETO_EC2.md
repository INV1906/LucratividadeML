# 🚀 GUIA COMPLETO PARA CONFIGURAR APLICAÇÃO NA EC2

## ✅ **ARQUIVO ZIP CRIADO COM SUCESSO!**

O arquivo `mercadolivre_app_ec2.zip` (168KB) contém todos os arquivos necessários para sua aplicação.

---

## 📋 **SUAS CREDENCIAIS**

```
MELI_APP_ID: 51467849418990
MELI_CLIENT_SECRET: KQGTjuxX0LfXVTw9MIVLYtykiTuWWniT
MELI_REDIRECT_URI: http://56.124.88.188/callback
DB_HOST: 127.0.0.1
DB_USER: root
DB_PASSWORD: 2154
DB_NAME: sistema_ml
```

---

## 🖥️ **SUA INSTÂNCIA EC2**

```
IP Público: 56.124.88.188
DNS: ec2-56-124-88-188.sa-east-1.compute.amazonaws.com
Tipo: t3.micro
Região: sa-east-1 (São Paulo)
```

---

## 📤 **PASSO 1: UPLOAD DO ARQUIVO ZIP**

### **Opção A: WinSCP (Recomendado para Windows)**

1. **Baixar WinSCP**: https://winscp.net/
2. **Instalar e abrir WinSCP**
3. **Configurar conexão**:
   - **Host**: `56.124.88.188`
   - **Username**: `ec2-user`
   - **Key file**: Seu arquivo `.pem` da chave SSH
4. **Conectar**
5. **Fazer upload** do arquivo `mercadolivre_app_ec2.zip` para `/home/ec2-user/`

### **Opção B: scp (se disponível)**

```bash
scp -i sua-chave.pem mercadolivre_app_ec2.zip ec2-user@56.124.88.188:/home/ec2-user/
```

---

## 🔧 **PASSO 2: CONECTAR VIA SSH**

```bash
ssh -i sua-chave.pem ec2-user@56.124.88.188
```

---

## 📁 **PASSO 3: EXTRAIR ARQUIVOS**

```bash
cd /home/ec2-user
unzip mercadolivre_app_ec2.zip
mv mercadolivre_app_ec2 mercadolivre-app
cd mercadolivre-app
mv .env_ec2 .env
```

---

## 🐍 **PASSO 4: INSTALAR PYTHON E DEPENDÊNCIAS**

```bash
# Atualizar sistema
sudo yum update -y

# Instalar Python 3.11
sudo yum install python3.11 python3.11-pip -y

# Instalar dependências Python
pip3.11 install -r requirements.txt
```

---

## 🗄️ **PASSO 5: INSTALAR E CONFIGURAR MYSQL**

```bash
# Instalar MySQL
sudo yum install mysql-server -y

# Iniciar MySQL
sudo systemctl start mysqld
sudo systemctl enable mysqld

# Configurar MySQL
sudo mysql_secure_installation
# Siga as instruções na tela
```

### **Configurar Banco de Dados**

```bash
# Conectar ao MySQL
sudo mysql -u root -p

# No MySQL, execute:
CREATE DATABASE sistema_ml;
CREATE USER "admin"@"%" IDENTIFIED BY "2154";
GRANT ALL PRIVILEGES ON sistema_ml.* TO "admin"@"%";
FLUSH PRIVILEGES;
EXIT;
```

---

## 🌐 **PASSO 6: CONFIGURAR NGINX**

```bash
# Instalar Nginx
sudo yum install nginx -y

# Configurar Nginx
sudo nano /etc/nginx/conf.d/flask.conf
```

**Conteúdo do arquivo `/etc/nginx/conf.d/flask.conf`:**

```nginx
server {
    listen 80;
    server_name 56.124.88.188;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔧 **PASSO 7: CONFIGURAR SERVIÇO SYSTEMD**

```bash
# Criar serviço
sudo nano /etc/systemd/system/flask-app.service
```

**Conteúdo do arquivo `/etc/systemd/system/flask-app.service`:**

```ini
[Unit]
Description=Flask App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/mercadolivre-app
Environment=PATH=/usr/bin/python3.11
ExecStart=/usr/bin/python3.11 app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🚀 **PASSO 8: INICIAR SERVIÇOS**

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Iniciar serviços
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl start flask-app
sudo systemctl enable flask-app
```

---

## 🔥 **PASSO 9: CONFIGURAR FIREWALL**

```bash
# Abrir portas
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## ✅ **PASSO 10: VERIFICAR STATUS**

```bash
# Verificar status dos serviços
sudo systemctl status nginx
sudo systemctl status flask-app
sudo systemctl status mysqld

# Verificar logs da aplicação
sudo journalctl -u flask-app -f
```

---

## 🌐 **PASSO 11: TESTAR APLICAÇÃO**

Acesse no navegador:
```
http://56.124.88.188
```

---

## ⚠️ **IMPORTANTE: SECURITY GROUPS**

Certifique-se de que sua instância EC2 tem as portas abertas:

1. **AWS Console** > **EC2** > **Security Groups**
2. **Encontrar** o security group da sua instância
3. **Editar** "Inbound rules"
4. **Adicionar regras**:
   - **Type**: SSH, **Port**: 22, **Source**: 0.0.0.0/0
   - **Type**: HTTP, **Port**: 80, **Source**: 0.0.0.0/0
   - **Type**: HTTPS, **Port**: 443, **Source**: 0.0.0.0/0

---

## 🔍 **TROUBLESHOOTING**

### **Se a aplicação não carregar:**

```bash
# Verificar logs
sudo journalctl -u flask-app -f

# Verificar se a aplicação está rodando
ps aux | grep python

# Verificar se a porta 5000 está aberta
netstat -tlnp | grep 5000

# Verificar se o Nginx está rodando
sudo systemctl status nginx
```

### **Se o MySQL não conectar:**

```bash
# Verificar se o MySQL está rodando
sudo systemctl status mysqld

# Verificar se a porta 3306 está aberta
netstat -tlnp | grep 3306

# Testar conexão
mysql -u root -p -e "SHOW DATABASES;"
```

---

## 🎯 **RESUMO DOS PASSOS**

1. ✅ **Upload do arquivo ZIP** (WinSCP ou scp)
2. ✅ **Conectar via SSH**
3. ✅ **Extrair arquivos**
4. ✅ **Instalar Python e dependências**
5. ✅ **Instalar e configurar MySQL**
6. ✅ **Configurar Nginx**
7. ✅ **Configurar serviço systemd**
8. ✅ **Iniciar serviços**
9. ✅ **Configurar firewall**
10. ✅ **Verificar status**
11. ✅ **Testar aplicação**

---

## ⏱️ **TEMPO ESTIMADO**

**Total: 30-45 minutos**

---

## 🎉 **RESULTADO FINAL**

Sua aplicação estará rodando em:
```
http://56.124.88.188
```

Com todas as funcionalidades:
- ✅ **Importação de vendas**
- ✅ **Webhooks do Mercado Livre**
- ✅ **Análise de lucratividade**
- ✅ **Status de envio detalhado**
- ✅ **Sincronização automática**
- ✅ **Renovação automática de tokens**
- ✅ **Relatórios em CSV/Excel/PDF**

---

## 🚀 **SUA APLICAÇÃO ESTARÁ ONLINE!**

Agora você tem controle total sobre seu servidor e pode escalar conforme necessário! 🎉
