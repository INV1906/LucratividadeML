#!/bin/bash

echo "🚀 DEPLOY DA APLICAÇÃO MERCADOLIVRE NA AWS"
echo "=========================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    error "Não execute como root! Use: sudo su - ec2-user"
    exit 1
fi

log "Iniciando deploy..."

# 1. Atualizar sistema
log "Atualizando sistema..."
sudo yum update -y

# 2. Instalar Python 3.11
log "Instalando Python 3.11..."
sudo yum install python3.11 python3.11-pip -y

# 3. Instalar dependências do sistema
log "Instalando dependências do sistema..."
sudo yum install git nginx -y

# 4. Criar diretório da aplicação
log "Criando diretório da aplicação..."
mkdir -p /home/ec2-user/mercadolivre-app
cd /home/ec2-user/mercadolivre-app

# 5. Instalar dependências Python
log "Instalando dependências Python..."
pip3.11 install -r requirements_aws_clean.txt

# 6. Configurar Nginx
log "Configurando Nginx..."
sudo cp nginx.conf /etc/nginx/conf.d/mercadolivre.conf
sudo systemctl enable nginx
sudo systemctl start nginx

# 7. Configurar serviço systemd
log "Configurando serviço systemd..."
sudo cp mercadolivre-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mercadolivre-app

# 8. Configurar firewall
log "Configurando firewall..."
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# 9. Configurar permissões
log "Configurando permissões..."
sudo chown -R ec2-user:ec2-user /home/ec2-user/mercadolivre-app
chmod +x /home/ec2-user/mercadolivre-app/app_aws.py

log "Deploy concluído!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Configure o arquivo .env com suas credenciais"
echo "2. Execute: sudo systemctl start mercadolivre-app"
echo "3. Verifique status: sudo systemctl status mercadolivre-app"
echo "4. Verifique logs: sudo journalctl -u mercadolivre-app -f"
echo ""
echo "🌐 Sua aplicação estará disponível em:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
