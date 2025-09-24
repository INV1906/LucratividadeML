# 🚀 GUIA COMPLETO AWS - EC2 + RDS (Para Iniciantes)

## 📋 **VISÃO GERAL**

Este guia vai te ensinar a colocar sua aplicação MercadoLivre na AWS usando:
- **EC2**: Servidor virtual (onde roda sua aplicação)
- **RDS**: Banco de dados MySQL gerenciado pela AWS

**Tempo estimado**: 2-3 horas (primeira vez)
**Custo**: ~$15-20/mês (dentro do free tier)

---

## 🎯 **PASSO 1: PREPARAR SUA APLICAÇÃO**

### 1.1 Criar arquivo ZIP
```bash
# No seu computador, crie um ZIP com estes arquivos:
- app_aws.py
- wsgi.py
- requirements_aws_clean.txt
- nginx.conf
- mercadolivre-app.service
- deploy.sh
- .env_aws_example
- templates/ (pasta completa)
```

### 1.2 Configurar credenciais MercadoLivre
- Acesse: https://developers.mercadolibre.com/
- Crie uma aplicação
- Anote: `App ID` e `Client Secret`

---

## 🌐 **PASSO 2: CONFIGURAR AWS CONSOLE**

### 2.1 Acessar AWS Console
1. Vá para: https://console.aws.amazon.com
2. Faça login com sua conta
3. **IMPORTANTE**: Escolha região **São Paulo (sa-east-1)**

### 2.2 Configurar região
- No canto superior direito, clique na região
- Selecione: **South America (São Paulo) sa-east-1**

---

## 🖥️ **PASSO 3: CRIAR INSTÂNCIA EC2**

### 3.1 Acessar EC2
1. No console AWS, procure por "EC2"
2. Clique em "EC2" nos serviços
3. Clique em "Launch Instance"

### 3.2 Configurar instância
**Nome da instância**: `MercadoLivre-App`

**AMI (Imagem)**:
- Selecione: **Amazon Linux 2023**
- AMI ID: `ami-082daca2e7d60abda` (São Paulo)

**Tipo de instância**:
- Selecione: **t3.micro** (Free Tier)
- 1 vCPU, 1 GB RAM

**Chave de acesso**:
- Clique em "Create new key pair"
- Nome: `mercadolivre-key`
- Tipo: RSA
- Formato: .pem
- **BAIXE O ARQUIVO .pem** (você vai precisar!)

### 3.3 Configurar Security Group
**Nome**: `MercadoLivre-SG`

**Regras de entrada**:
1. **SSH (22)**:
   - Tipo: SSH
   - Protocolo: TCP
   - Porta: 22
   - Origem: Meu IP (0.0.0.0/0 para teste)

2. **HTTP (80)**:
   - Tipo: HTTP
   - Protocolo: TCP
   - Porta: 80
   - Origem: Qualquer lugar (0.0.0.0/0)

3. **HTTPS (443)**:
   - Tipo: HTTPS
   - Protocolo: TCP
   - Porta: 443
   - Origem: Qualquer lugar (0.0.0.0/0)

### 3.4 Configurar armazenamento
- **Tipo**: gp3
- **Tamanho**: 8 GB (Free Tier)
- **Criptografia**: Desabilitada

### 3.5 Lançar instância
1. Clique em "Launch instance"
2. Aguarde o status mudar para "Running"
3. **ANOTE O IP PÚBLICO** (exemplo: 18.228.153.23)

---

## 🗄️ **PASSO 4: CRIAR BANCO RDS**

### 4.1 Acessar RDS
1. No console AWS, procure por "RDS"
2. Clique em "RDS" nos serviços
3. Clique em "Create database"

### 4.2 Configurar banco
**Método de criação**: Standard create

**Engine type**: MySQL
**Version**: MySQL 8.0.35

**Templates**: Free tier

**Configurações**:
- **DB instance identifier**: `mercadolivre-db`
- **Master username**: `admin`
- **Master password**: `SuaSenhaForte123!` (anote esta senha!)

**Tipo de instância**: db.t3.micro (Free Tier)

**Armazenamento**:
- **Storage type**: General Purpose SSD (gp2)
- **Allocated storage**: 20 GB
- **Storage autoscaling**: Desabilitado

### 4.3 Configurar conectividade
**VPC**: Default VPC
**Subnet group**: default
**Public access**: Yes (para facilitar conexão inicial)

**VPC security groups**: Create new
- **Security group name**: `mercadolivre-rds-sg`

**Database port**: 3306

### 4.4 Configurar autenticação
**Database authentication**: Password authentication

### 4.5 Configurar backup
**Backup retention period**: 7 days
**Backup window**: No preference
**Maintenance window**: No preference

### 4.6 Criar banco
1. Clique em "Create database"
2. Aguarde status mudar para "Available" (5-10 minutos)
3. **ANOTE O ENDPOINT** (exemplo: mercadolivre-db.xxxxx.rds.amazonaws.com)

---

## 🔒 **PASSO 5: CONFIGURAR SECURITY GROUPS**

### 5.1 Configurar RDS Security Group
1. Vá para EC2 → Security Groups
2. Encontre: `mercadolivre-rds-sg`
3. Clique em "Edit inbound rules"
4. Adicione regra:
   - **Type**: MySQL/Aurora
   - **Protocol**: TCP
   - **Port**: 3306
   - **Source**: `mercadolivre-SG` (Security Group do EC2)

### 5.2 Verificar EC2 Security Group
1. Encontre: `MercadoLivre-SG`
2. Verifique se tem as regras SSH, HTTP e HTTPS

---

## 📤 **PASSO 6: UPLOAD DA APLICAÇÃO**

### 6.1 Conectar via SSH
```bash
# No seu computador (Windows):
# Use o Git Bash ou PowerShell

# Navegue até a pasta onde está o arquivo .pem
cd C:\caminho\para\sua\chave

# Conectar ao EC2
ssh -i mercadolivre-key.pem ec2-user@SEU_IP_PUBLICO
```

### 6.2 Upload dos arquivos
**Opção A: WinSCP (Recomendado para Windows)**
1. Baixe WinSCP: https://winscp.net/
2. Configure:
   - **Host**: Seu IP público do EC2
   - **Username**: ec2-user
   - **Key file**: Seu arquivo .pem
3. Conecte e faça upload dos arquivos para `/home/ec2-user/`

**Opção B: SCP (Linha de comando)**
```bash
# No seu computador
scp -i mercadolivre-key.pem -r pasta-da-aplicacao ec2-user@SEU_IP_PUBLICO:/home/ec2-user/
```

---

## ⚙️ **PASSO 7: CONFIGURAR APLICAÇÃO NO EC2**

### 7.1 Conectar via SSH
```bash
ssh -i mercadolivre-key.pem ec2-user@SEU_IP_PUBLICO
```

### 7.2 Preparar ambiente
```bash
# Criar diretório da aplicação
mkdir -p /home/ec2-user/mercadolivre-app
cd /home/ec2-user/mercadolivre-app

# Mover arquivos (se necessário)
mv ../arquivos-da-aplicacao/* .

# Dar permissão de execução
chmod +x deploy.sh
```

### 7.3 Configurar arquivo .env
```bash
# Copiar arquivo de exemplo
cp .env_aws_example .env

# Editar arquivo
nano .env
```

**Conteúdo do arquivo .env**:
```env
# Configurações da Aplicação
FLASK_ENV=production
DEBUG=False
FLASK_SECRET_KEY=sua_chave_secreta_muito_forte_aqui_123456789

# Configurações do MercadoLivre
MELI_APP_ID=seu_app_id_do_mercadolivre
MELI_CLIENT_SECRET=seu_client_secret_do_mercadolivre
MELI_REDIRECT_URI=http://SEU_IP_PUBLICO/callback

# Configurações do Banco de Dados RDS
DB_HOST=seu_endpoint_rds.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=SuaSenhaForte123!
DB_NAME=sistema_ml
DB_PORT=3306

# Configurações de Produção
HOST=0.0.0.0
PORT=5000
```

### 7.4 Executar deploy
```bash
# Executar script de deploy
./deploy.sh
```

### 7.5 Iniciar aplicação
```bash
# Iniciar serviço
sudo systemctl start mercadolivre-app

# Verificar status
sudo systemctl status mercadolivre-app

# Ver logs
sudo journalctl -u mercadolivre-app -f
```

---

## 🧪 **PASSO 8: TESTAR APLICAÇÃO**

### 8.1 Verificar se está funcionando
1. Abra navegador
2. Vá para: `http://SEU_IP_PUBLICO`
3. Deve aparecer a página inicial

### 8.2 Testar health check
```bash
# No EC2
curl http://localhost:5000/health

# Deve retornar:
# {"status": "healthy", "database": "connected", ...}
```

### 8.3 Verificar logs
```bash
# Ver logs da aplicação
sudo journalctl -u mercadolivre-app -f

# Ver logs do Nginx
sudo tail -f /var/log/nginx/access.log
```

---

## 🔧 **PASSO 9: CONFIGURAR MERCADOLIVRE**

### 9.1 Atualizar redirect URI
1. Vá para: https://developers.mercadolibre.com/
2. Edite sua aplicação
3. Adicione: `http://SEU_IP_PUBLICO/callback`

### 9.2 Testar integração
1. Acesse sua aplicação
2. Faça login/registro
3. Teste a conexão com MercadoLivre

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### Problema: Não consegue conectar SSH
**Solução**:
1. Verifique se o Security Group permite SSH (porta 22)
2. Verifique se está usando o IP público correto
3. Verifique se o arquivo .pem tem permissões corretas:
   ```bash
   chmod 400 mercadolivre-key.pem
   ```

### Problema: Aplicação não carrega
**Solução**:
1. Verifique se o serviço está rodando:
   ```bash
   sudo systemctl status mercadolivre-app
   ```
2. Verifique logs:
   ```bash
   sudo journalctl -u mercadolivre-app -f
   ```
3. Verifique se o Nginx está rodando:
   ```bash
   sudo systemctl status nginx
   ```

### Problema: Erro de conexão com banco
**Solução**:
1. Verifique se o RDS está "Available"
2. Verifique se o Security Group do RDS permite conexão do EC2
3. Teste conexão manual:
   ```bash
   mysql -h SEU_ENDPOINT_RDS -u admin -p
   ```

### Problema: Erro 502 Bad Gateway
**Solução**:
1. Verifique se a aplicação está rodando na porta 5000
2. Verifique configuração do Nginx
3. Reinicie serviços:
   ```bash
   sudo systemctl restart mercadolivre-app
   sudo systemctl restart nginx
   ```

---

## 💰 **CONTROLE DE CUSTOS**

### Monitoramento
1. Vá para: AWS Console → Billing
2. Configure alertas de cobrança
3. Monitore uso diário

### Otimizações
- Use instâncias t3.micro (Free Tier)
- Configure parada automática em horários não utilizados
- Use RDS db.t3.micro (Free Tier)

---

## 📞 **SUPORTE**

### Comandos úteis
```bash
# Ver status dos serviços
sudo systemctl status mercadolivre-app nginx

# Reiniciar serviços
sudo systemctl restart mercadolivre-app nginx

# Ver logs em tempo real
sudo journalctl -u mercadolivre-app -f

# Verificar espaço em disco
df -h

# Verificar uso de memória
free -h

# Verificar processos
ps aux | grep python
```

### Arquivos importantes
- **Logs da aplicação**: `/var/log/mercadolivre-app.log`
- **Logs do Nginx**: `/var/log/nginx/`
- **Configuração**: `/home/ec2-user/mercadolivre-app/.env`
- **Serviço**: `/etc/systemd/system/mercadolivre-app.service`

---

## ✅ **CHECKLIST FINAL**

- [ ] EC2 criada e rodando
- [ ] RDS criado e disponível
- [ ] Security Groups configurados
- [ ] Aplicação enviada para EC2
- [ ] Arquivo .env configurado
- [ ] Deploy executado com sucesso
- [ ] Serviços iniciados
- [ ] Aplicação acessível via navegador
- [ ] MercadoLivre configurado
- [ ] Testes realizados

**🎉 PARABÉNS! Sua aplicação está no ar!**
