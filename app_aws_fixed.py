#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação MercadoLivre para AWS
Baseado no app.py original
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import requests
import json
import hashlib
import hmac
import base64
from urllib.parse import urlencode, parse_qs
import time
import threading
import uuid
from sqlalchemy import text, and_, or_, desc, asc, func
import logging
from logging.handlers import RotatingFileHandler

# Configuração da aplicação
app = Flask(__name__)

# Configurações básicas
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'sua-chave-secreta-super-segura-aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://admin:senha123@database-1.c8qjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqjqj.sa-east-1.rds.amazonaws.com:3306/sistema_ml')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'connect_timeout': 60,
        'charset': 'utf8mb4'
    }
}

# Configuração de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuração de logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/mercadolivre.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('MercadoLivre startup')

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelos do banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    ml_user_id = db.Column(db.String(50))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    token_expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'ml_user_id': self.ml_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
            'is_admin': self.is_admin
        }

# Configurações do MercadoLivre API
ML_CLIENT_ID = os.getenv('ML_CLIENT_ID', '')
ML_CLIENT_SECRET = os.getenv('ML_CLIENT_SECRET', '')
ML_REDIRECT_URI = os.getenv('ML_REDIRECT_URI', 'http://localhost:5000/callback')

# URLs da API do MercadoLivre
ML_AUTH_URL = "https://auth.mercadolivre.com.br/authorization"
ML_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
ML_API_BASE = "https://api.mercadolibre.com"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_authenticated():
    return 'user_id' in session and session.get('authenticated', False)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('index'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Acesso negado. Você precisa ser administrador.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rotas principais
@app.route('/')
def index():
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    # Gerar state para segurança
    state = str(uuid.uuid4())
    session['oauth_state'] = state
    
    # Parâmetros para autorização
    params = {
        'response_type': 'code',
        'client_id': ML_CLIENT_ID,
        'redirect_uri': ML_REDIRECT_URI,
        'state': state
    }
    
    auth_url = f"{ML_AUTH_URL}?{urlencode(params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Verificar state
    if request.args.get('state') != session.get('oauth_state'):
        flash('Erro de segurança. Tente novamente.', 'error')
        return redirect(url_for('index'))
    
    # Verificar se houve erro
    if 'error' in request.args:
        flash(f'Erro na autorização: {request.args.get("error_description", "Erro desconhecido")}', 'error')
        return redirect(url_for('index'))
    
    # Obter código de autorização
    code = request.args.get('code')
    if not code:
        flash('Código de autorização não recebido.', 'error')
        return redirect(url_for('index'))
    
    try:
        # Trocar código por token
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': ML_CLIENT_ID,
            'client_secret': ML_CLIENT_SECRET,
            'code': code,
            'redirect_uri': ML_REDIRECT_URI
        }
        
        token_response = requests.post(ML_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Obter informações do usuário
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get(f"{ML_API_BASE}/users/me", headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        # Verificar se usuário existe
        user = User.query.filter_by(ml_user_id=str(user_info['id'])).first()
        
        if not user:
            # Criar novo usuário
            user = User(
                username=user_info.get('nickname', f"user_{user_info['id']}"),
                email=user_info.get('email', ''),
                ml_user_id=str(user_info['id'])
            )
            db.session.add(user)
        
        # Atualizar tokens
        user.access_token = token_info['access_token']
        user.refresh_token = token_info.get('refresh_token')
        user.token_expires_at = datetime.utcnow() + timedelta(seconds=token_info.get('expires_in', 21600))
        
        db.session.commit()
        
        # Login do usuário
        session['user_id'] = user.id
        session['authenticated'] = True
        session.pop('oauth_state', None)
        
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('dashboard'))
        
    except requests.RequestException as e:
        app.logger.error(f"Erro na requisição: {e}")
        flash('Erro ao comunicar com o MercadoLivre. Tente novamente.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        app.logger.error(f"Erro no callback: {e}")
        flash('Erro interno. Tente novamente.', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    try:
        # Testar conexão com banco
        db.session.execute(text('SELECT 1'))
        db.session.commit()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500

# Páginas de erro
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Inicializar banco de dados
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Database tables created successfully')
    except Exception as e:
        app.logger.error(f'Error creating database tables: {e}')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
