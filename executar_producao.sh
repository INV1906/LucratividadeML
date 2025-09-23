#!/bin/bash
# Script para executar aplicação em produção

echo "🚀 Iniciando aplicação em produção..."

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado!"
    echo "📝 Copie .env.example para .env e configure as variáveis"
    exit 1
fi

# Carregar variáveis de ambiente
export $(cat .env | grep -v '^#' | xargs)

# Verificar dependências
echo "📦 Verificando dependências..."
pip install -r requirements.txt

# Verificar banco de dados
echo "🗄️ Verificando banco de dados..."
python -c "
from database import DatabaseManager
db = DatabaseManager()
if db.conectar():
    print('✅ Banco de dados conectado')
    db.criar_tabelas()
    print('✅ Tabelas verificadas/criadas')
else:
    print('❌ Erro ao conectar banco de dados')
    exit(1)
"

# Executar aplicação
echo "🌐 Iniciando servidor..."
gunicorn -w 4 -b 0.0.0.0:8000 app:app
