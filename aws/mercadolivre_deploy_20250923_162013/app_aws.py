#!/usr/bin/env python3
"""
Aplicação MercadoLivre - Versão AWS
Configurada para rodar em EC2 com RDS
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, timedelta
import logging

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurações
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'chave-padrao-mudar-em-producao')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configurações do MercadoLivre
MELI_APP_ID = os.getenv('MELI_APP_ID')
MELI_CLIENT_SECRET = os.getenv('MELI_CLIENT_SECRET')
MELI_REDIRECT_URI = os.getenv('MELI_REDIRECT_URI')

# Modelos do Banco de Dados
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    meli_user_id = db.Column(db.String(50), nullable=True)
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meli_id = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=True)
    profit = db.Column(db.Float, nullable=True)
    profit_margin = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.String(50), nullable=True)
    permalink = db.Column(db.String(500), nullable=True)
    thumbnail = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meli_order_id = db.Column(db.String(50), unique=True, nullable=False)
    product_id = db.Column(db.String(50), nullable=False)
    product_title = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=True)
    profit = db.Column(db.Float, nullable=True)
    profit_margin = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    buyer_id = db.Column(db.String(50), nullable=True)
    shipping_cost = db.Column(db.Float, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas da Aplicação
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Usuário já existe')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado')
            return render_template('register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Usuário criado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Estatísticas básicas
    total_products = Product.query.filter_by(user_id=current_user.id).count()
    total_sales = Sale.query.filter_by(user_id=current_user.id).count()
    
    # Produtos mais lucrativos
    top_products = Product.query.filter_by(
        user_id=current_user.id
    ).order_by(Product.profit.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         total_products=total_products,
                         total_sales=total_sales,
                         top_products=top_products)

@app.route('/callback')
@login_required
def callback():
    """Callback do MercadoLivre OAuth"""
    code = request.args.get('code')
    if not code:
        flash('Erro na autorização do MercadoLivre')
        return redirect(url_for('dashboard'))
    
    # Trocar código por token
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': MELI_APP_ID,
        'client_secret': MELI_CLIENT_SECRET,
        'code': code,
        'redirect_uri': MELI_REDIRECT_URI
    }
    
    try:
        response = requests.post('https://api.mercadolibre.com/oauth/token', data=token_data)
        if response.status_code == 200:
            token_info = response.json()
            
            # Salvar tokens no usuário
            current_user.access_token = token_info['access_token']
            current_user.refresh_token = token_info.get('refresh_token')
            current_user.token_expires = datetime.utcnow() + timedelta(seconds=token_info['expires_in'])
            
            # Obter informações do usuário
            user_info_response = requests.get(
                f"https://api.mercadolibre.com/users/me?access_token={token_info['access_token']}"
            )
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                current_user.meli_user_id = user_info['id']
            
            db.session.commit()
            flash('Conta MercadoLivre conectada com sucesso!')
        else:
            flash('Erro ao conectar com MercadoLivre')
    except Exception as e:
        logger.error(f"Erro no callback: {e}")
        flash('Erro interno ao conectar com MercadoLivre')
    
    return redirect(url_for('dashboard'))

@app.route('/produtos')
@login_required
def produtos():
    products = Product.query.filter_by(user_id=current_user.id).all()
    return render_template('produtos.html', products=products)

@app.route('/vendas')
@login_required
def vendas():
    sales = Sale.query.filter_by(user_id=current_user.id).all()
    return render_template('vendas.html', sales=sales)

@app.route('/analise')
@login_required
def analise():
    # Análise de lucratividade
    products = Product.query.filter_by(user_id=current_user.id).all()
    
    total_investment = sum(p.cost or 0 for p in products)
    total_revenue = sum(p.price for p in products)
    total_profit = sum(p.profit or 0 for p in products)
    
    avg_profit_margin = sum(p.profit_margin or 0 for p in products) / len(products) if products else 0
    
    return render_template('analise.html',
                         total_investment=total_investment,
                         total_revenue=total_revenue,
                         total_profit=total_profit,
                         avg_profit_margin=avg_profit_margin,
                         products=products)

@app.route('/health')
def health_check():
    """Endpoint de health check para AWS"""
    try:
        # Testar conexão com banco
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Inicializar banco de dados
def init_db():
    """Inicializar banco de dados"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("Banco de dados inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar banco: {e}")
            raise

if __name__ == '__main__':
    # Verificar variáveis de ambiente
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Variáveis de ambiente faltando: {missing_vars}")
        exit(1)
    
    # Inicializar banco
    init_db()
    
    # Executar aplicação
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Iniciando aplicação em {host}:{port}")
    app.run(host=host, port=port, debug=debug)
