# 🚀 TUTORIAL COMPLETO AWS PARA INICIANTES

## 📋 **GUIA PASSO A PASSO - PRIMEIRA VEZ NA AWS**

Vou te guiar desde a criação da conta até sua aplicação funcionando online!

---

## 🎯 **ETAPA 1: CRIAR CONTA AWS (10 minutos)**

### **Passo 1.1: Acessar AWS**
1. **Abra seu navegador**
2. **Acesse**: https://aws.amazon.com
3. **Clique em**: "Create an AWS Account" (Criar uma conta AWS)

### **Passo 1.2: Preencher Dados**
1. **Email**: Use um email válido
2. **Senha**: Crie uma senha forte
3. **Nome da conta**: Pode ser seu nome ou empresa
4. **Clique em**: "Continue" (Continuar)

### **Passo 1.3: Informações de Contato**
1. **Nome completo**: Seu nome completo
2. **Endereço**: Seu endereço completo
3. **Cidade**: Sua cidade
4. **Estado**: Seu estado
5. **CEP**: Seu CEP
6. **Telefone**: Seu telefone com DDD
7. **Clique em**: "Create Account and Continue"

### **Passo 1.4: Verificar Telefone**
1. **Escolha**: "Text message (SMS)" ou "Voice call"
2. **Digite seu telefone**: Com código do país (+55 para Brasil)
3. **Clique em**: "Send SMS" ou "Call me now"
4. **Digite o código** recebido
5. **Clique em**: "Verify"

### **Passo 1.5: Escolher Plano de Suporte**
1. **Selecione**: "Basic Support - Free" (Suporte Básico - Gratuito)
2. **Clique em**: "Complete sign up"

### **Passo 1.6: Aguardar Confirmação**
- Aguarde alguns minutos para a conta ser ativada
- Você receberá um email de confirmação

---

## 🎯 **ETAPA 2: CRIAR INSTÂNCIA EC2 (5 minutos)**

### **Passo 2.1: Acessar Console AWS**
1. **Acesse**: https://console.aws.amazon.com
2. **Faça login** com suas credenciais
3. **Procure por**: "EC2" na barra de pesquisa
4. **Clique em**: "EC2" (Elastic Compute Cloud)

### **Passo 2.2: Criar Instância**
1. **Clique em**: "Launch Instance" (Lançar Instância)
2. **Nome da instância**: Digite "mercadolivre-app"

### **Passo 2.3: Escolher AMI (Sistema Operacional)**
1. **Selecione**: "Amazon Linux 2023 AMI" (deve estar selecionado por padrão)
2. **Clique em**: "Select"

### **Passo 2.4: Escolher Tipo de Instância**
1. **Selecione**: "t2.micro" (Free tier eligible)
2. **Clique em**: "Next: Configure Instance Details"

### **Passo 2.5: Configurar Detalhes**
1. **Deixe tudo como padrão**
2. **Clique em**: "Next: Add Storage"

### **Passo 2.6: Configurar Armazenamento**
1. **Deixe 8 GB** (padrão do Free Tier)
2. **Clique em**: "Next: Add Tags"

### **Passo 2.7: Adicionar Tags (Opcional)**
1. **Clique em**: "Next: Configure Security Group"

### **Passo 2.8: Configurar Security Group**
1. **Nome**: "mercadolivre-sg"
2. **Descrição**: "Security group for MercadoLivre app"
3. **Adicione regras**:
   - **Type**: SSH, **Port**: 22, **Source**: My IP
   - **Type**: HTTP, **Port**: 80, **Source**: Anywhere (0.0.0.0/0)
   - **Type**: HTTPS, **Port**: 443, **Source**: Anywhere (0.0.0.0/0)
4. **Clique em**: "Review and Launch"

### **Passo 2.9: Revisar e Lançar**
1. **Revise todas as configurações**
2. **Clique em**: "Launch"

### **Passo 2.10: Criar Key Pair**
1. **Selecione**: "Create a new key pair"
2. **Nome**: "mercadolivre-key"
3. **Clique em**: "Download Key Pair"
4. **IMPORTANTE**: Salve o arquivo .pem em local seguro
5. **Clique em**: "Launch Instances"

### **Passo 2.11: Aguardar Criação**
1. **Clique em**: "View Instances"
2. **Aguarde** o status mudar para "Running"
3. **Anote o IP público** da instância

---

## 🎯 **ETAPA 3: INSTALAR MYSQL NA EC2 (10 minutos)**

### **Passo 3.1: Conectar via SSH**
1. **Abra terminal** (Windows: PowerShell ou Git Bash)
2. **Navegue** até onde salvou o arquivo .pem
3. **Execute**:
```bash
ssh -i mercadolivre-key.pem ec2-user@SEU_IP_PUBLICO
```

### **Passo 3.2: Atualizar Sistema**
```bash
sudo yum update -y
```

### **Passo 3.3: Instalar MySQL**
```bash
sudo yum install mysql-server -y
```

### **Passo 3.4: Iniciar MySQL**
```bash
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

### **Passo 3.5: Configurar MySQL**
```bash
sudo mysql_secure_installation
```
**Responda**:
- **Set root password?**: Y
- **New password**: Digite uma senha forte (ex: MercadoLivre2024!)
- **Remove anonymous users?**: Y
- **Disallow root login remotely?**: N
- **Remove test database?**: Y
- **Reload privilege tables?**: Y

### **Passo 3.6: Criar Banco de Dados**
```bash
sudo mysql -u root -p
```
**No MySQL, execute**:
```sql
CREATE DATABASE sistema_ml;
CREATE USER 'admin'@'%' IDENTIFIED BY '2154';
GRANT ALL PRIVILEGES ON sistema_ml.* TO 'admin'@'%';
FLUSH PRIVILEGES;
EXIT;
```

---

## 🎯 **ETAPA 4: INSTALAR PYTHON E DEPENDÊNCIAS (5 minutos)**

### **Passo 4.1: Instalar Python**
```bash
sudo yum install python3.11 python3.11-pip -y
```

### **Passo 4.2: Instalar Git**
```bash
sudo yum install git -y
```

### **Passo 4.3: Criar Diretório da Aplicação**
```bash
mkdir -p /home/ec2-user/mercadolivre-app
cd /home/ec2-user/mercadolivre-app
```

---

## 🎯 **ETAPA 5: UPLOAD DOS ARQUIVOS (10 minutos)**

### **Passo 5.1: Download do WinSCP**
1. **Acesse**: https://winscp.net/
2. **Baixe** e instale o WinSCP

### **Passo 5.2: Configurar Conexão**
1. **Abra WinSCP**
2. **Host name**: Seu IP público da EC2
3. **User name**: ec2-user
4. **Private key file**: Selecione seu arquivo .pem
5. **Clique em**: "Login"

### **Passo 5.3: Upload dos Arquivos**
1. **Navegue** até `/home/ec2-user/mercadolivre-app`
2. **Faça upload** do arquivo `mercadolivre_app_ec2.zip`
3. **Aguarde** o upload terminar

### **Passo 5.4: Extrair Arquivos (via SSH)**
```bash
cd /home/ec2-user/mercadolivre-app
unzip mercadolivre_app_ec2.zip
mv .env_ec2 .env
```

---

## 🎯 **ETAPA 6: INSTALAR DEPENDÊNCIAS PYTHON (5 minutos)**

### **Passo 6.1: Instalar Dependências**
```bash
pip3.11 install -r requirements_aws.txt
```

### **Passo 6.2: Verificar Instalação**
```bash
python3.11 --version
pip3.11 list | grep Flask
```

---

## 🎯 **ETAPA 7: CONFIGURAR NGINX (5 minutos)**

### **Passo 7.1: Instalar Nginx**
```bash
sudo yum install nginx -y
```

### **Passo 7.2: Configurar Nginx**
```bash
sudo nano /etc/nginx/conf.d/flask.conf
```

**Cole este conteúdo**:
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Salve**: Ctrl+X, Y, Enter

### **Passo 7.3: Iniciar Nginx**
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 🎯 **ETAPA 8: CONFIGURAR SERVIÇO DA APLICAÇÃO (5 minutos)**

### **Passo 8.1: Criar Serviço**
```bash
sudo nano /etc/systemd/system/flask-app.service
```

**Cole este conteúdo**:
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

**Salve**: Ctrl+X, Y, Enter

### **Passo 8.2: Iniciar Serviço**
```bash
sudo systemctl daemon-reload
sudo systemctl start flask-app
sudo systemctl enable flask-app
```

---

## 🎯 **ETAPA 9: CONFIGURAR FIREWALL (2 minutos)**

### **Passo 9.1: Abrir Portas**
```bash
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

---

## 🎯 **ETAPA 10: TESTAR APLICAÇÃO (3 minutos)**

### **Passo 10.1: Verificar Status**
```bash
sudo systemctl status nginx
sudo systemctl status flask-app
sudo systemctl status mysqld
```

### **Passo 10.2: Verificar Logs**
```bash
sudo journalctl -u flask-app -f
```

### **Passo 10.3: Testar no Navegador**
1. **Abra seu navegador**
2. **Acesse**: http://SEU_IP_PUBLICO
3. **Verifique** se a aplicação carrega

---

## 🎯 **ETAPA 11: CONFIGURAR SSL (OPCIONAL - 10 minutos)**

### **Passo 11.1: Instalar Certbot**
```bash
sudo yum install certbot python3-certbot-nginx -y
```

### **Passo 11.2: Obter Certificado**
```bash
sudo certbot --nginx -d SEU_IP_PUBLICO
```

### **Passo 11.3: Configurar Renovação**
```bash
sudo crontab -e
```
**Adicione esta linha**:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## ✅ **CHECKLIST FINAL**

### **Verificar se tudo está funcionando:**
- [ ] ✅ Conta AWS criada
- [ ] ✅ Instância EC2 rodando
- [ ] ✅ MySQL instalado e configurado
- [ ] ✅ Python instalado
- [ ] ✅ Arquivos da aplicação uploadados
- [ ] ✅ Dependências instaladas
- [ ] ✅ Nginx configurado e rodando
- [ ] ✅ Serviço da aplicação rodando
- [ ] ✅ Firewall configurado
- [ ] ✅ Aplicação acessível no navegador

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Se a aplicação não carregar:**
```bash
# Verificar logs
sudo journalctl -u flask-app -f

# Verificar se a aplicação está rodando
ps aux | grep python

# Verificar se a porta 5000 está aberta
netstat -tlnp | grep 5000

# Reiniciar serviços
sudo systemctl restart flask-app
sudo systemctl restart nginx
```

### **Se MySQL não conectar:**
```bash
# Verificar se MySQL está rodando
sudo systemctl status mysqld

# Testar conexão
mysql -u root -p -e "SHOW DATABASES;"

# Reiniciar MySQL
sudo systemctl restart mysqld
```

### **Se não conseguir conectar via SSH:**
1. **Verifique** se o Security Group tem a porta 22 aberta
2. **Verifique** se o arquivo .pem tem as permissões corretas
3. **Tente** conectar de outro IP

---

## 🎉 **PARABÉNS!**

### **Sua aplicação está online!**

**Acesse**: http://SEU_IP_PUBLICO

**Funcionalidades disponíveis**:
- ✅ Login com Mercado Livre
- ✅ Importação de vendas
- ✅ Análise de lucratividade
- ✅ Relatórios Excel/PDF
- ✅ Webhooks funcionais
- ✅ Status de envio detalhado

---

## 📞 **PRECISA DE AJUDA?**

Se encontrar algum problema:
1. **Verifique** os logs da aplicação
2. **Confirme** se todos os serviços estão rodando
3. **Teste** cada etapa individualmente
4. **Consulte** a seção de solução de problemas

**Sua aplicação está pronta para produção!** 🚀
