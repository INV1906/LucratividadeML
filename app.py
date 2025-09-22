"""
Aplicação Flask para análise de lucratividade do Mercado Livre.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response
import os
import threading
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from database import DatabaseManager
from meli_api import MercadoLivreAPI
from profitability import ProfitabilityCalculator
from auth_manager import AuthManager
from webhook_processor import WebhookProcessor, WebhookLogger
from token_monitor import start_token_monitoring, stop_token_monitoring, get_users_needing_reauth, force_sync_user
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'sua_chave_secreta_aqui')

# Configurar headers de segurança para resolver Mixed Content
@app.after_request
def after_request(response):
    # Permitir carregamento de recursos HTTPS em páginas HTTPS
    response.headers['Content-Security-Policy'] = "upgrade-insecure-requests"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response

# Middleware para lidar com ngrok
@app.before_request
def before_request():
    """Middleware para lidar com headers do ngrok."""
    # Headers para ngrok
    if 'ngrok' in request.host:
        # Log para debug
        print(f"🌐 Requisição ngrok: {request.method} {request.path}")
        print(f"🔗 Host: {request.host}")
        print(f"📋 User-Agent: {request.headers.get('User-Agent', 'N/A')}")

@app.after_request
def after_request(response):
    """Adiciona headers para ngrok e LocalTunnel."""
    if 'ngrok' in request.host:
        response.headers['ngrok-skip-browser-warning'] = 'true'
        response.headers['ngrok-skip-browser-warning'] = 'any'
        response.headers['Access-Control-Allow-Origin'] = '*'
        print(f"✅ Resposta enviada: {response.status_code}")
    elif 'loca.lt' in request.host:
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Inicializa os módulos
db = DatabaseManager()
api = MercadoLivreAPI()
calculator = ProfitabilityCalculator()
auth_manager = AuthManager()
webhook_processor = WebhookProcessor(api, db)
webhook_logger = WebhookLogger(db)

# Decorator para verificar login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Sistema de status de importação global
import_status = {
    'produtos': {
        'ativo': False,
        'progresso': 0,
        'total': 0,
        'atual': 0,
        'status': 'Aguardando...',
        'inicio': None,
        'fim': None,
        'sucesso': 0,
        'erros': 0
    },
    'vendas': {
        'ativo': False,
        'progresso': 0,
        'total': 0,
        'atual': 0,
        'status': 'Aguardando...',
        'inicio': None,
        'fim': None,
        'sucesso': 0,
        'erros': 0
    }
}

# Executor global para threads
executor = ThreadPoolExecutor(max_workers=2)

def processar_produto_individual(mlb, user_id):
    """Processa um produto individual - para uso em paralelo - OTIMIZADO."""
    try:
        detalhes_completos = api.obter_detalhes_completos_produto(mlb, user_id)
        if detalhes_completos:
            if db.salvar_produto_completo(detalhes_completos, user_id):
                return {'sucesso': True, 'mlb': mlb}
            else:
                return {'sucesso': False, 'mlb': mlb, 'erro': 'Falha ao salvar no banco'}
        else:
            return {'sucesso': False, 'mlb': mlb, 'erro': 'Falha ao obter detalhes'}
    except Exception as e:
        return {'sucesso': False, 'mlb': mlb, 'erro': str(e)}

def processar_lote_produtos(mlbs_batch, user_id):
    """Processa um lote de produtos de forma otimizada."""
    resultados = []
    detalhes_batch = []
    
    # Coleta detalhes de todos os produtos do lote
    for mlb in mlbs_batch:
        try:
            detalhes = api.obter_detalhes_completos_produto(mlb, user_id)
            if detalhes:
                detalhes_batch.append(detalhes)
                resultados.append({'sucesso': True, 'mlb': mlb})
            else:
                resultados.append({'sucesso': False, 'mlb': mlb, 'erro': 'Falha ao obter detalhes'})
        except Exception as e:
            resultados.append({'sucesso': False, 'mlb': mlb, 'erro': str(e)})
    
    # Salva todos os produtos do lote de uma vez
    if detalhes_batch:
        try:
            if db.salvar_produtos_lote(detalhes_batch, user_id):
                # Atualiza resultados para sucesso
                for resultado in resultados:
                    if resultado.get('sucesso') and resultado.get('mlb') in [d['produto'].get('id') or d['produto'].get('mlb') for d in detalhes_batch]:
                        resultado['salvo'] = True
            else:
                # Marca todos como falha de salvamento
                for resultado in resultados:
                    if resultado.get('sucesso'):
                        resultado['sucesso'] = False
                        resultado['erro'] = 'Falha ao salvar lote no banco'
        except Exception as e:
            for resultado in resultados:
                if resultado.get('sucesso'):
                    resultado['sucesso'] = False
                    resultado['erro'] = f'Erro ao salvar lote: {str(e)}'
    
    return resultados

def importar_produtos_background(user_id):
    """Função para importar produtos em background."""
    global import_status
    
    try:
        # Inicializa status
        import_status['produtos']['ativo'] = True
        import_status['produtos']['status'] = 'Buscando lista de produtos...'
        import_status['produtos']['inicio'] = datetime.now()
        import_status['produtos']['progresso'] = 0
        import_status['produtos']['atual'] = 0
        import_status['produtos']['sucesso'] = 0
        import_status['produtos']['erros'] = 0
        
        # Importa categorias primeiro (se necessário)
        try:
            access_token = db.obter_access_token(user_id)
            if access_token:
                # Verifica se já existem categorias no banco
                conn = db.conectar()
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT COUNT(*) FROM categorias_mlb")
                        count = cursor.fetchone()[0]
                        if count == 0:
                            print("📋 Importando categorias automaticamente...")
                            categorias = api.obter_categorias_site(access_token, "MLB")
                            if categorias:
                                db.salvar_categorias_mlb(categorias)
                                print(f"✅ {len(categorias)} categorias importadas com sucesso")
                    conn.close()
        except Exception as e:
            print(f"⚠️ Erro ao importar categorias automaticamente: {e}")
        
        # Obtém lista de produtos
        produtos_ids = api.obter_produtos_usuario(user_id)
        
        if not produtos_ids:
            import_status['produtos']['status'] = 'Nenhum produto encontrado'
            import_status['produtos']['ativo'] = False
            import_status['produtos']['fim'] = datetime.now()
            return
        
        import_status['produtos']['total'] = len(produtos_ids)
        import_status['produtos']['status'] = f'Importando {len(produtos_ids)} produtos...'
        
        # Processa produtos em lotes para máxima velocidade
        max_workers = 6  # 6 threads simultâneas para lotes
        tamanho_lote = 5  # 5 produtos por lote
        produtos_processados = 0
        
        # Divide produtos em lotes
        lotes = [produtos_ids[i:i + tamanho_lote] for i in range(0, len(produtos_ids), tamanho_lote)]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submete todos os lotes para processamento paralelo
            future_to_lote = {
                executor.submit(processar_lote_produtos, lote, user_id): lote 
                for lote in lotes
            }
            
            # Processa resultados conforme completam
            for future in as_completed(future_to_lote):
                if not import_status['produtos']['ativo']:  # Permite cancelar
                    break
                
                lote = future_to_lote[future]
                
                try:
                    resultados_lote = future.result()
                    
                    # Processa resultados do lote
                    for resultado in resultados_lote:
                        produtos_processados += 1
                        
                        if resultado['sucesso']:
                            import_status['produtos']['sucesso'] += 1
                        else:
                            import_status['produtos']['erros'] += 1
                            print(f"❌ Erro no produto {resultado.get('mlb', 'N/A')}: {resultado.get('erro', 'Erro desconhecido')}")
                        
                        # Atualiza progresso
                        import_status['produtos']['atual'] = produtos_processados
                        import_status['produtos']['progresso'] = int(produtos_processados / len(produtos_ids) * 100)
                        import_status['produtos']['status'] = f'Processando em lotes: {produtos_processados}/{len(produtos_ids)} produtos'
                    
                except Exception as e:
                    # Marca todos os produtos do lote como erro
                    for mlb in lote:
                        produtos_processados += 1
                        import_status['produtos']['erros'] += 1
                        print(f"❌ Erro no lote: {e}")
                    
                    import_status['produtos']['atual'] = produtos_processados
                    import_status['produtos']['progresso'] = int(produtos_processados / len(produtos_ids) * 100)
                
                # Log a cada 20 produtos (reduzido)
                if produtos_processados % 20 == 0:
                    print(f"💾 {import_status['produtos']['sucesso']}/{len(produtos_ids)} produtos salvos (paralelo)")
        
        # Finaliza
        import_status['produtos']['progresso'] = 100
        import_status['produtos']['status'] = f'Concluído! {import_status["produtos"]["sucesso"]} produtos importados, {import_status["produtos"]["erros"]} erros'
        import_status['produtos']['fim'] = datetime.now()
        
        print(f"✅ Importação concluída: {import_status['produtos']['sucesso']} produtos salvos")
        
    except Exception as e:
        import_status['produtos']['status'] = f'Erro: {str(e)}'
        import_status['produtos']['erros'] += 1
        print(f"❌ Erro na importação: {e}")
    finally:
        import_status['produtos']['ativo'] = False

def importar_vendas_background(user_id):
    """Função para importar vendas em background (estratégia de duas fases)."""
    global import_status
    
    print(f"🚀 Iniciando importar_vendas_background para user_id: {user_id}")
    
    try:
        # Inicializa status
        import_status['vendas']['ativo'] = True
        import_status['vendas']['status'] = 'Buscando IDs das vendas...'
        import_status['vendas']['inicio'] = datetime.now()
        import_status['vendas']['progresso'] = 0
        import_status['vendas']['atual'] = 0
        import_status['vendas']['sucesso'] = 0
        import_status['vendas']['erros'] = 0
        
        # FASE 1: Obter todos os IDs das vendas (rápido)
        print(f"🔍 FASE 1: Buscando todos os IDs de vendas para user_id: {user_id}")
        
        def callback_ids(total_ids, status):
            """Callback para atualizar status durante busca de IDs"""
            import_status['vendas']['status'] = f'Buscando IDs... {status} ({total_ids} encontrados)'
            import_status['vendas']['total'] = total_ids
            import_status['vendas']['progresso'] = min(25, int(total_ids / 200))  # Progresso de 0-25%
        
        order_ids = api.obter_todos_ids_vendas(user_id, callback_ids)
        print(f"📊 IDs encontrados: {len(order_ids)}")
        
        if not order_ids:
            import_status['vendas']['status'] = 'Nenhuma venda encontrada'
            import_status['vendas']['ativo'] = False
            import_status['vendas']['fim'] = datetime.now()
            return
        
        # Atualiza status após fase 1
        import_status['vendas']['total'] = len(order_ids)
        import_status['vendas']['status'] = f'Importando {len(order_ids)} vendas...'
        import_status['vendas']['progresso'] = 25  # 25% após buscar IDs
        
        # FASE 2: Importar cada venda individualmente
        print(f"🔍 FASE 2: Importando {len(order_ids)} vendas uma por uma...")
        
        access_token = api.db.obter_access_token(user_id)
        if not access_token:
            import_status['vendas']['status'] = 'Erro: Token de acesso não encontrado'
            import_status['vendas']['ativo'] = False
            return
        
        # Processa vendas em paralelo otimizado
        print(f"🚀 Iniciando importação paralela de {len(order_ids)} vendas...")
        
        def processar_venda_individual(venda_data):
            """Processa uma venda individual (para uso em paralelo)"""
            try:
                order_id = venda_data.get('id')
                if not order_id:
                    return {'sucesso': False, 'order_id': 'N/A', 'erro': 'ID não encontrado'}
                
                # Salva venda usando nova estrutura
                if db.salvar_venda_completa(venda_data, user_id):
                    return {'sucesso': True, 'order_id': order_id}
                else:
                    return {'sucesso': False, 'order_id': order_id, 'erro': 'Falha ao salvar'}
            except Exception as e:
                return {'sucesso': False, 'order_id': venda_data.get('id', 'N/A'), 'erro': str(e)}
        
        # Configuração de paralelismo otimizada
        max_workers = min(15, len(order_ids))  # Aumentado para 15 threads
        batch_size = 100  # Aumentado para 100 vendas por lote
        
        print(f"⚙️ Configuração: {max_workers} threads, lotes de {batch_size} vendas")
        
        # Processa em lotes para controle de progresso
        total_processed = 0
        for batch_start in range(0, len(order_ids), batch_size):
            if not import_status['vendas']['ativo']:  # Permite cancelar
                break
                
            batch_end = min(batch_start + batch_size, len(order_ids))
            batch_order_ids = order_ids[batch_start:batch_end]
            
            print(f"📦 Processando lote {batch_start//batch_size + 1}: vendas {batch_start + 1}-{batch_end}")
            
            # Busca detalhes das vendas do lote em paralelo
            vendas_detalhadas = api.obter_vendas_paralelo(batch_order_ids, access_token, max_workers)
            
            # Processa salvamento em paralelo
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submete todas as vendas do lote para salvamento
                future_to_venda = {
                    executor.submit(processar_venda_individual, venda): venda 
                    for venda in vendas_detalhadas
                }
                
                # Processa resultados conforme ficam prontos
                for future in as_completed(future_to_venda):
                    if not import_status['vendas']['ativo']:  # Permite cancelar
                        break
                        
                    result = future.result()
                    total_processed += 1
                    
                    if result['sucesso']:
                        import_status['vendas']['sucesso'] += 1
                    else:
                        import_status['vendas']['erros'] += 1
                        print(f"❌ Erro na venda {result['order_id']}: {result.get('erro', 'Erro desconhecido')}")
                    
                    # Atualiza progresso
                    import_status['vendas']['atual'] = total_processed
                    import_status['vendas']['progresso'] = 25 + int(total_processed / len(order_ids) * 75)
                    import_status['vendas']['status'] = f'Processando venda {total_processed}/{len(order_ids)}: {result["order_id"]}'
                    
                    # Log a cada 20 vendas processadas (otimizado)
                    if total_processed % 20 == 0:
                        print(f"💾 {import_status['vendas']['sucesso']}/{total_processed} vendas salvas (Lote atual: {batch_start//batch_size + 1})")
            
            # Pequena pausa entre lotes para não sobrecarregar a API
            if batch_end < len(order_ids):
                time.sleep(0.3)  # Reduzido para acelerar
        
        # Finaliza
        import_status['vendas']['progresso'] = 100
        import_status['vendas']['status'] = f'Concluído! {import_status["vendas"]["sucesso"]} vendas importadas, {import_status["vendas"]["erros"]} erros'
        import_status['vendas']['fim'] = datetime.now()
        
        print(f"✅ Importação de vendas concluída: {import_status['vendas']['sucesso']} vendas salvas")
        
    except Exception as e:
        import_status['vendas']['status'] = f'Erro: {str(e)}'
        import_status['vendas']['erros'] += 1
        print(f"❌ Erro na importação de vendas: {e}")
        import traceback
        traceback.print_exc()
    finally:
        import_status['vendas']['ativo'] = False


@app.route('/', methods=['GET', 'POST'])
def index():
    """Página inicial com sistema de login."""
    if request.method == 'POST':
        data = request.get_json()
        login_type = data.get('type')
        
        if login_type == 'password':
            # Login com senha
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'success': False, 'message': 'Username e senha são obrigatórios'})
            
            usuario = auth_manager.verificar_login(username, password)
            if usuario:
                # Criar sessão
                session_token = auth_manager.criar_sessao(
                    usuario['user_id'], 
                    'password',
                    request.remote_addr,
                    request.headers.get('User-Agent')
                )
                
                if session_token:
                    session['user_id'] = usuario['user_id']
                    session['username'] = usuario['username']
                    session['login_type'] = 'password'
                    session['session_token'] = session_token
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Login realizado com sucesso',
                        'redirect': '/dashboard'
                    })
                else:
                    return jsonify({'success': False, 'message': 'Erro ao criar sessão'})
            else:
                return jsonify({'success': False, 'message': 'Credenciais inválidas'})
        
        elif login_type == 'mercadolivre':
            # Redirecionar para OAuth do Mercado Livre
            return jsonify({
                'success': True,
                'redirect': f"https://auth.mercadolivre.com.br/authorization?response_type=code&client_id={os.getenv('MELI_APP_ID')}&redirect_uri={os.getenv('MELI_REDIRECT_URI')}"
            })
    
    return render_template('index.html')

# ==================== ROTAS DE AUTENTICAÇÃO ====================


@app.route('/logout')
def logout():
    """Logout do usuário."""
    if 'session_token' in session:
        auth_manager.encerrar_sessao(session['session_token'])
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/registrar-auth', methods=['POST'])
@login_required
def registrar_auth():
    """Registra usuário no sistema de autenticação."""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    # Validações
    if not username or not email or not password or not confirm_password:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'Senhas não coincidem'})
    
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Senha deve ter pelo menos 6 caracteres'})
    
    if len(username) < 3:
        return jsonify({'success': False, 'message': 'Username deve ter pelo menos 3 caracteres'})
    
    # Registrar usuário
    user_id = session.get('user_id')
    if auth_manager.criar_usuario_auth(user_id, username, email, password):
        return jsonify({'success': True, 'message': 'Conta criada com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Username já existe ou erro ao criar conta'})

@app.route('/alterar-senha', methods=['POST'])
@login_required
def alterar_senha():
    """Altera senha do usuário."""
    data = request.get_json()
    senha_atual = data.get('senha_atual')
    nova_senha = data.get('nova_senha')
    confirmar_senha = data.get('confirmar_senha')
    
    # Validações
    if not senha_atual or not nova_senha or not confirmar_senha:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
    
    if nova_senha != confirmar_senha:
        return jsonify({'success': False, 'message': 'Nova senha e confirmação não coincidem'})
    
    if len(nova_senha) < 6:
        return jsonify({'success': False, 'message': 'Nova senha deve ter pelo menos 6 caracteres'})
    
    # Alterar senha
    user_id = session.get('user_id')
    if auth_manager.alterar_senha(user_id, senha_atual, nova_senha):
        return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Senha atual incorreta'})

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    """Página de recuperação de senha."""
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email é obrigatório'})
        
        # Gerar código de recuperação
        codigo = auth_manager.gerar_codigo_recuperacao(email)
        if codigo:
            # TODO: Enviar email com código
            print(f"Código de recuperação para {email}: {codigo}")
            return jsonify({
                'success': True, 
                'message': f'Código enviado para {email}',
                'codigo': codigo  # Remover em produção
            })
        else:
            return jsonify({'success': False, 'message': 'Email não encontrado'})
    
    return render_template('esqueci_senha.html')

@app.route('/verificar-codigo', methods=['POST'])
def verificar_codigo():
    """Verifica código de recuperação."""
    data = request.get_json()
    email = data.get('email')
    codigo = data.get('codigo')
    
    if not email or not codigo:
        return jsonify({'success': False, 'message': 'Email e código são obrigatórios'})
    
    user_id = auth_manager.verificar_codigo_recuperacao(email, codigo)
    if user_id:
        return jsonify({'success': True, 'message': 'Código válido', 'user_id': user_id})
    else:
        return jsonify({'success': False, 'message': 'Código inválido ou expirado'})

@app.route('/redefinir-senha', methods=['POST'])
def redefinir_senha():
    """Redefine senha usando código de verificação."""
    data = request.get_json()
    user_id = data.get('user_id')
    codigo = data.get('codigo')
    nova_senha = data.get('nova_senha')
    confirmar_senha = data.get('confirmar_senha')
    
    # Validações
    if not user_id or not codigo or not nova_senha or not confirmar_senha:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'})
    
    if nova_senha != confirmar_senha:
        return jsonify({'success': False, 'message': 'Senhas não coincidem'})
    
    if len(nova_senha) < 6:
        return jsonify({'success': False, 'message': 'Nova senha deve ter pelo menos 6 caracteres'})
    
    # Redefinir senha
    if auth_manager.redefinir_senha(user_id, nova_senha, codigo):
        return jsonify({'success': True, 'message': 'Senha redefinida com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Código inválido ou expirado'})

@app.route('/api/verificar-auth-status')
@login_required
def verificar_auth_status():
    """Verifica se usuário tem conta de autenticação configurada."""
    user_id = session.get('user_id')
    
    conn = auth_manager.conectar()
    if not conn:
        return jsonify({'hasAuth': False})
    
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT username, email FROM usuarios_auth 
                WHERE user_id = %s AND is_active = TRUE
            """, (user_id,))
            
            usuario = cursor.fetchone()
            if usuario:
                return jsonify({
                    'hasAuth': True,
                    'username': usuario['username'],
                    'email': usuario['email']
                })
            else:
                return jsonify({'hasAuth': False})
                
    except Exception as e:
        print(f"Erro ao verificar status de auth: {e}")
        return jsonify({'hasAuth': False})
    finally:
        conn.close()

@app.route('/teste-ngrok')
def teste_ngrok():
    """Página para testar se ngrok está funcionando."""
    return render_template('teste_ngrok.html')

@app.route('/teste-callback')
def teste_callback():
    """Testa se o callback está funcionando via ngrok."""
    response = make_response("OK - Ngrok funcionando!")
    response.headers['ngrok-skip-browser-warning'] = 'true'
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/status')
def status():
    """Status da aplicação."""
    response_data = {
        "success": True,
        "message": "Aplicação funcionando!",
        "host": request.host,
        "url": request.url,
        "timestamp": datetime.now().isoformat(),
        "headers": dict(request.headers)
    }
    
    response = make_response(jsonify(response_data))
    response.headers['ngrok-skip-browser-warning'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/auth')
def auth():
    """Inicia processo de autenticação OAuth."""
    auth_url = api.obter_url_autorizacao()
    return redirect(auth_url)

@app.route('/renovar-token')
def renovar_token():
    """Força renovação do token OAuth."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    user_id = session['user_id']
    
    if api._renovar_token(user_id):
        return jsonify({'success': True, 'message': 'Token renovado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Falha ao renovar token'})

@app.route('/api/token/status')
@login_required
def token_status():
    """Retorna status dos tokens do usuário."""
    user_id = session.get('user_id')
    
    # Verifica se precisa reautenticar
    needs_reauth = api.verificar_necessidade_reautenticacao(user_id)
    
    # Busca informações do token
    conn = db.conectar()
    token_info = {}
    
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT created_at, expires_in, needs_reauth, last_reauth_attempt, last_sync_attempt
                    FROM tokens WHERE user_id = %s
                """, (user_id,))
                resultado = cursor.fetchone()
                
                if resultado:
                    created_at, expires_in, needs_reauth_db, last_reauth, last_sync = resultado
                    
                    token_info = {
                        'created_at': created_at.isoformat() if created_at else None,
                        'expires_in': expires_in,
                        'needs_reauth': bool(needs_reauth_db),
                        'last_reauth_attempt': last_reauth.isoformat() if last_reauth else None,
                        'last_sync_attempt': last_sync.isoformat() if last_sync else None
                    }
                    
                    # Calcula tempo restante
                    if created_at and expires_in:
                        from datetime import datetime, timedelta
                        expiracao = created_at + timedelta(seconds=expires_in)
                        tempo_restante = (expiracao - datetime.now()).total_seconds()
                        token_info['tempo_restante_segundos'] = max(0, tempo_restante)
                        token_info['tempo_restante_horas'] = tempo_restante / 3600
        except Exception as e:
            print(f"Erro ao buscar status do token: {e}")
        finally:
            conn.close()
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'needs_reauth': needs_reauth,
        'token_info': token_info
    })

@app.route('/api/token/sync', methods=['POST'])
@login_required
def sync_user_data():
    """Força sincronização de dados perdidos do usuário."""
    user_id = session.get('user_id')
    
    if force_sync_user(user_id):
        return jsonify({'success': True, 'message': 'Dados sincronizados com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Falha na sincronização'})

@app.route('/api/token/users-needing-reauth')
@login_required
def users_needing_reauth():
    """Retorna usuários que precisam reautenticar (admin only)."""
    # Verificar se é admin (implementar lógica de permissão)
    usuarios = get_users_needing_reauth()
    
    return jsonify({
        'success': True,
        'usuarios': usuarios,
        'total': len(usuarios)
    })

@app.route('/api/token/start-monitor', methods=['POST'])
@login_required
def start_monitor():
    """Inicia o monitor de tokens (admin only)."""
    try:
        start_token_monitoring()
        return jsonify({'success': True, 'message': 'Monitor de tokens iniciado!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao iniciar monitor: {e}'})

@app.route('/api/token/stop-monitor', methods=['POST'])
@login_required
def stop_monitor():
    """Para o monitor de tokens (admin only)."""
    try:
        stop_token_monitoring()
        return jsonify({'success': True, 'message': 'Monitor de tokens parado!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao parar monitor: {e}'})

# ===== APIs DE STATUS DE ENVIO =====

@app.route('/api/shipping/statuses')
@login_required
def get_shipping_statuses():
    """Retorna todos os status de envio disponíveis."""
    try:
        statuses = db.obter_todos_status_envio()
        return jsonify({
            'success': True,
            'statuses': statuses
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter status: {e}'})

@app.route('/api/shipping/statuses/category/<categoria>')
@login_required
def get_shipping_statuses_by_category(categoria):
    """Retorna status de envio por categoria."""
    try:
        statuses = db.obter_status_envio_por_categoria(categoria)
        return jsonify({
            'success': True,
            'categoria': categoria,
            'statuses': statuses
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter status: {e}'})

@app.route('/api/shipping/sales')
@login_required
def get_sales_by_shipping_status():
    """Retorna vendas filtradas por status de envio."""
    user_id = session.get('user_id')
    status_envio = request.args.get('status')
    categoria = request.args.get('categoria')
    limite = int(request.args.get('limite', 100))
    
    try:
        vendas = db.obter_vendas_por_status_envio(user_id, status_envio, categoria, limite)
        
        # Adicionar traduções para cada venda
        for venda in vendas:
            venda['status_pagamento_pt'] = venda.get('status_pagamento_pt', 'Desconhecido')
            venda['payment_method_pt'] = venda.get('payment_method_pt', 'Desconhecido')
            venda['shipping_method_pt'] = venda.get('shipping_method_pt', 'Desconhecido')
            venda['status_pedido_pt'] = venda.get('status_pedido_pt', 'Desconhecido')
            venda['status_envio_pt'] = venda.get('status_envio_pt', 'Desconhecido')
            venda['categoria_envio_pt'] = venda.get('categoria_envio_pt', 'Indefinido')
        
        return jsonify({
            'success': True,
            'vendas': vendas,
            'total': len(vendas),
            'filtros': {
                'status_envio': status_envio,
                'categoria': categoria,
                'limite': limite
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter vendas: {e}'})

@app.route('/api/shipping/statistics')
@login_required
def get_shipping_statistics():
    """Retorna estatísticas de status de envio."""
    user_id = session.get('user_id')
    
    try:
        stats = db.obter_estatisticas_status_envio(user_id)
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao obter estatísticas: {e}'})


@app.route('/callback')
def callback():
    """Callback OAuth do Mercado Livre."""
    # Log para debug
    print(f"🔗 Callback recebido - Host: {request.host}")
    print(f"📋 Args: {dict(request.args)}")
    
    code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state')
    
    print(f"🔑 Code: {code[:20]}..." if code else "❌ Sem código")
    print(f"🏷️  State: {state}")
    
    if error:
        print(f"❌ Erro OAuth: {error}")
        flash(f'Erro na autenticação: {error}', 'error')
        return redirect(url_for('index'))
    
    if not code:
        print("❌ Código não fornecido")
        flash('Erro na autenticação: código não fornecido', 'error')
        return redirect(url_for('index'))
    
    try:
        print("🔄 Trocando código por token...")
        # Troca código por token
        token_data = api.trocar_codigo_por_token(code)
        
        if not token_data:
            print("❌ Falha ao obter token")
            flash('Erro ao obter token de acesso', 'error')
            return redirect(url_for('index'))
        
        print(f"✅ Token obtido! Dados: {list(token_data.keys())}")
        
        user_id = token_data.get('user_id')
        if user_id:
            print(f"👤 User ID: {user_id}")
            session['user_id'] = user_id
            session['access_token'] = token_data.get('access_token')
            flash('🎉 Autenticação realizada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        
        print("❌ User ID não encontrado no token")
        flash('Erro ao obter ID do usuário', 'error')
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"💥 Erro no callback: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Erro na autenticação: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    
    # Limpa produtos inválidos automaticamente
    produtos_removidos = db.limpar_produtos_invalidos(user_id)
    if produtos_removidos > 0:
        flash(f'Foram removidos {produtos_removidos} produtos com dados inválidos', 'info')
    
    # Obtém análise geral
    analise_geral = calculator.obter_analise_geral_usuario(user_id, 30)
    
    # Obtém produtos
    produtos = db.obter_produtos_usuario(user_id)
    
    # Obtém vendas recentes
    vendas = db.obter_vendas_usuario(user_id, 10)
    
    # Obtém sugestões
    sugestoes = calculator.sugerir_otimizacoes(user_id)
    
    return render_template('dashboard.html', 
                         analise=analise_geral,
                         produtos=produtos,
                         vendas=vendas,
                         sugestoes=sugestoes)

@app.route('/limpar-produtos-null', methods=['POST'])
def limpar_produtos_null():
    """Remove todos os produtos null/inválidos do banco."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    try:
        # Limpa produtos inválidos do usuário atual
        produtos_removidos = db.limpar_produtos_invalidos(session['user_id'])
        
        if produtos_removidos > 0:
            flash(f'✅ Limpeza concluída! {produtos_removidos} produtos inválidos foram removidos.', 'success')
        else:
            flash('✅ Nenhum produto inválido encontrado. Banco de dados já está limpo!', 'info')
            
    except Exception as e:
        flash(f'❌ Erro durante a limpeza: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/sincronizar-status', methods=['POST'])
def sincronizar_status():
    """Força sincronização do status dos produtos com o Mercado Livre."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    try:
        user_id = session['user_id']
        produtos_atualizados = 0
        
        # Busca todos os produtos do usuário
        produtos = db.obter_produtos_usuario(user_id)
        
        for produto in produtos:
            mlb = produto.get('mlb')
            if mlb:
                try:
                    # Busca dados atualizados do Mercado Livre
                    produto_data = api.obter_detalhes_produto(mlb, user_id)
                    if produto_data:
                        # Log detalhado do status
                        status_atual = produto.get('status', 'N/A')
                        novo_status = produto_data.get('status', 'active')
                        
                        print(f"🔍 Verificando {mlb}:")
                        print(f"   - Status local: {status_atual}")
                        print(f"   - Status ML: {novo_status}")
                        print(f"   - Dados completos: {produto_data}")
                        
                        if novo_status != status_atual:
                            db.atualizar_status_produto(mlb, user_id, novo_status)
                            produtos_atualizados += 1
                            print(f"🔄 Status atualizado para {mlb}: {status_atual} → {novo_status}")
                        else:
                            print(f"✅ Status já sincronizado para {mlb}: {novo_status}")
                except Exception as e:
                    print(f"❌ Erro ao atualizar {mlb}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        if produtos_atualizados > 0:
            flash(f'✅ Sincronização concluída! {produtos_atualizados} produtos foram atualizados.', 'success')
        else:
            flash('✅ Todos os produtos já estão sincronizados!', 'info')
            
    except Exception as e:
        flash(f'❌ Erro durante a sincronização: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('dashboard'))

@app.route('/produtos-excluidos')
def produtos_excluidos():
    """Página para visualizar produtos excluídos."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    produtos_excluidos = db.obter_produtos_excluidos(user_id)
    
    return render_template('produtos_excluidos.html', 
                         produtos_excluidos=produtos_excluidos)

@app.route('/alterar-status-massa', methods=['POST'])
def alterar_status_massa():
    """Altera o status de múltiplos produtos em massa."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        data = request.get_json()
        mlbs = data.get('mlbs', [])
        novo_status = data.get('status')
        user_id = session['user_id']
        
        if not mlbs or not novo_status:
            return jsonify({'success': False, 'message': 'Dados inválidos'})
        
        if novo_status not in ['active', 'paused']:
            return jsonify({'success': False, 'message': 'Status inválido'})
        
        produtos_alterados = 0
        
        for mlb in mlbs:
            try:
                # Atualizar no Mercado Livre
                if api.atualizar_status_produto(mlb, novo_status, user_id):
                    # Atualizar no banco local
                    if db.atualizar_status_produto(mlb, user_id, novo_status):
                        produtos_alterados += 1
                        print(f"✅ Status alterado para {mlb}: {novo_status}")
                    else:
                        print(f"❌ Erro ao atualizar status no banco para {mlb}")
                else:
                    print(f"❌ Erro ao atualizar status no ML para {mlb}")
            except Exception as e:
                print(f"❌ Erro ao processar {mlb}: {e}")
                continue
        
        return jsonify({
            'success': True, 
            'message': f'Status alterado para {produtos_alterados} produto(s)',
            'alterados': produtos_alterados
        })
        
    except Exception as e:
        print(f"❌ Erro na alteração em massa: {e}")
        return jsonify({'success': False, 'message': str(e)})


@app.route('/produtos')
def produtos():
    """Página de produtos com paginação e filtros."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 20 produtos por página
    
    # Parâmetros de filtro
    busca = request.args.get('busca', '').strip()
    categoria = request.args.get('categoria', '').strip()
    status = request.args.get('status', '').strip()
    
    # Obtém produtos com variações e filtros
    produtos_paginados = db.obter_produtos_com_variacoes(user_id, page, per_page, busca, categoria, status)
    total_produtos = db.contar_produtos_usuario_filtrado(user_id, busca, categoria, status)
    
    # Calcula informações de paginação
    total_pages = (total_produtos + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('produtos.html', 
                         produtos=produtos_paginados,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         total_produtos=total_produtos,
                         filtros={'busca': busca, 'categoria': categoria, 'status': status})

@app.route('/teste-produtos')
def teste_produtos():
    """Rota de teste para verificar se os produtos estão sendo exibidos."""
    if 'user_id' not in session:
        return "ERRO: Usuário não está logado na sessão"
    
    user_id = session['user_id']
    
    # Obtém produtos com variações
    produtos_paginados = db.obter_produtos_com_variacoes(user_id, 1, 20)
    total_produtos = db.contar_produtos_usuario_filtrado(user_id)
    
    return render_template('teste_template.html', 
                         produtos=produtos_paginados,
                         total_produtos=total_produtos)

@app.route('/produto/<mlb>')
def detalhes_produto(mlb):
    """Detalhes de um produto específico."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    
    # Calcula lucratividade
    lucratividade = calculator.calcular_lucratividade_produto(mlb)
    
    return render_template('detalhes_produto.html', 
                         produto=mlb, 
                         lucratividade=lucratividade)

@app.route('/produto/editar', methods=['POST'])
def editar_produto():
    """Edita um produto."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        dados = request.get_json()
        mlb = dados.get('mlb')
        user_id = session['user_id']
        
        if not mlb:
            return jsonify({'success': False, 'message': 'MLB não fornecido'})
        
        # Inicializar API do Mercado Livre
        api = MercadoLivreAPI()
        
        # Sincronizar alterações com o Mercado Livre
        sucesso_ml = True
        erros_ml = []
        
        # Atualizar preço se fornecido
        if 'price' in dados and dados['price'] is not None:
            try:
                preco_float = float(dados['price'])
                if not api.atualizar_preco_produto(mlb, preco_float, user_id):
                    sucesso_ml = False
                    erros_ml.append("Erro ao atualizar preço no Mercado Livre")
            except (ValueError, TypeError) as e:
                sucesso_ml = False
                erros_ml.append(f"Preço inválido: {e}")
        
        # Atualizar quantidade se fornecida
        if 'quantity' in dados and dados['quantity'] is not None:
            try:
                quantidade_int = int(dados['quantity'])
                if not api.atualizar_quantidade_produto(mlb, quantidade_int, user_id):
                    sucesso_ml = False
                    erros_ml.append("Erro ao atualizar quantidade no Mercado Livre")
            except (ValueError, TypeError) as e:
                sucesso_ml = False
                erros_ml.append(f"Quantidade inválida: {e}")
        
        # Atualizar status se fornecido
        if 'status' in dados and dados['status'] is not None:
            if not api.atualizar_status_produto(mlb, dados['status'], user_id):
                sucesso_ml = False
                erros_ml.append("Erro ao atualizar status no Mercado Livre")
        
        # Atualizar produto no banco local
        sucesso_banco = db.atualizar_produto(mlb, user_id, dados)
        
        if sucesso_banco and sucesso_ml:
            return jsonify({'success': True, 'message': 'Produto atualizado com sucesso no banco e no Mercado Livre'})
        elif sucesso_banco and not sucesso_ml:
            return jsonify({'success': True, 'message': f'Produto atualizado no banco, mas houve erros no Mercado Livre: {", ".join(erros_ml)}'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao atualizar produto no banco'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/categorias')
def api_categorias():
    """API para buscar categorias únicas dos produtos."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        categorias = db.obter_categorias_usuario(user_id)
        return jsonify({'success': True, 'categorias': categorias})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/produto/<mlb>')
def api_produto(mlb):
    """Retorna dados de um produto específico e atualiza do Mercado Livre."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        
        # Buscar dados atualizados do Mercado Livre
        api = MercadoLivreAPI()
        dados_completos = api.obter_detalhes_completos_produto(mlb, user_id)
        
        if dados_completos and dados_completos.get('produto'):
            # Extrair dados do produto da estrutura aninhada
            produto_data = dados_completos['produto']
            
            # Processar dados para o formato esperado pelo banco
            dados_atualizados = {
                'title': produto_data.get('title', ''),
                'price': produto_data.get('price', 0),
                'regular_price': produto_data.get('original_price', produto_data.get('price', 0)),
                'avaliable_quantity': produto_data.get('available_quantity', 0),
                'sold_quantity': produto_data.get('sold_quantity', 0),
                'status': produto_data.get('status', 'active'),
                'category': produto_data.get('category_id', ''),
                'thumbnail': produto_data.get('thumbnail', ''),
                'listing_type_id': produto_data.get('listing_type_id', ''),
                'frete': 0,  # Será calculado baseado no frete_gratis
                'frete_gratis': 1 if produto_data.get('shipping', {}).get('free_shipping', False) else 0
            }
            
            # Processar dados de frete seguindo a mesma lógica da importação
            valor_frete = 0
            if dados_completos.get('frete'):
                frete_data = dados_completos['frete']
                if frete_data and isinstance(frete_data, dict):
                    # Usar a mesma lógica da importação
                    valor_frete = frete_data.get("coverage", {}).get("all_country", {}).get("list_cost", 0)
                    # Se frete_gratis = 0, força frete = 0 (Frete Grátis) - igual ao save
                    if dados_atualizados['frete_gratis'] == 0:
                        valor_frete = 0
            
            dados_atualizados['frete'] = valor_frete
            
            # Atualizar produto no banco com dados mais recentes
            db.atualizar_produto_completo(mlb, user_id, dados_atualizados)
            
            # Buscar dados atualizados do banco
            produto = db.obter_produto_por_mlb(mlb, user_id)
            
            if produto:
                return jsonify({'success': True, 'produto': produto, 'message': 'Produto atualizado com sucesso'})
            else:
                return jsonify({'success': False, 'message': 'Erro ao buscar produto atualizado'})
        else:
            # Se não conseguir atualizar, retorna dados do banco
            produto = db.obter_produto_por_mlb(mlb, user_id)
            if produto:
                return jsonify({'success': True, 'produto': produto, 'message': 'Dados do banco (não foi possível atualizar)'})
            else:
                return jsonify({'success': False, 'message': 'Produto não encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/produtos')
def api_produtos():
    """API para buscar produtos com filtros e paginação."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 20, type=int)
        
        # Parâmetros de filtro
        busca = request.args.get('busca', '').strip()
        categoria = request.args.get('categoria', '').strip()
        status = request.args.get('status', '').strip()
        
        # Parâmetros de ordenação
        sort_column = request.args.get('sort', 'updated_at').strip()
        sort_order = request.args.get('order', 'desc').strip()
        
        # Se for uma requisição para análise (limit=1000), usar função otimizada
        if per_page >= 1000:
            produtos = db.obter_produtos_para_analise(user_id, sort_column, sort_order)
            total_produtos = len(produtos)
        else:
            # Para listagem normal, usar paginação
            produtos = db.obter_produtos_com_variacoes(user_id, page, per_page, busca, categoria, status, sort_column, sort_order)
            total_produtos = db.contar_produtos_usuario_filtrado(user_id, busca, categoria, status)
        
        # Calcula informações de paginação
        total_pages = (total_produtos + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
        
        # Converter decimal.Decimal para float para serialização JSON
        produtos_serializados = []
        for produto in produtos:
            produto_serializado = {}
            for key, value in produto.items():
                if hasattr(value, 'quantize'):  # É um decimal.Decimal
                    produto_serializado[key] = float(value)
                else:
                    produto_serializado[key] = value
            produtos_serializados.append(produto_serializado)
        
        return jsonify({
            'success': True,
            'produtos': produtos_serializados,
            'pagination': {
                'page': page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_page': prev_page,
                'next_page': next_page,
                'total_produtos': total_produtos
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/vendas')
def api_vendas():
    """API para buscar vendas com filtros e paginação."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Parâmetros de filtro
        busca = request.args.get('busca', '').strip()
        data_inicio = request.args.get('data_inicio', '').strip()
        data_fim = request.args.get('data_fim', '').strip()
        status_pagamento = request.args.get('status_pagamento', '').strip()
        status_envio = request.args.get('status_envio', '').strip()
        
        # Obtém vendas com filtros e paginação (nova estrutura)
        print(f"🔍 Buscando vendas para user_id: {user_id}, page: {page}, busca: '{busca}', data_inicio: '{data_inicio}', data_fim: '{data_fim}', status_pagamento: '{status_pagamento}', status_envio: '{status_envio}'")
        vendas = db.obter_vendas_usuario_novo(user_id, page, per_page, busca, data_inicio, data_fim, status_pagamento, status_envio)
        total_vendas = db.contar_vendas_usuario_novo(user_id, busca, data_inicio, data_fim, status_pagamento, status_envio)
        print(f"📊 Encontradas {len(vendas)} vendas de {total_vendas} total")
        
        # Calcula totais de todas as vendas filtradas (nova estrutura)
        totais = db.calcular_totais_vendas_novo(user_id, busca, data_inicio, data_fim, status_pagamento, status_envio)
        
        # Calcula informações de paginação
        total_pages = (total_vendas + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        prev_page = page - 1 if has_prev else None
        next_page = page + 1 if has_next else None
        
        return jsonify({
            'success': True,
            'vendas': vendas,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_page': prev_page,
                'next_page': next_page,
                'total': total_vendas
            },
            'totais': totais
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/vendas')
def vendas():
    """Página de vendas com paginação."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = 25  # 25 vendas por página
    
    # Obtém vendas com paginação
    vendas_paginadas = db.obter_vendas_usuario_paginado(user_id, page, per_page)
    total_vendas = db.contar_vendas_usuario(user_id)
    
    # Calcula informações de paginação
    total_pages = (total_vendas + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    prev_page = page - 1 if has_prev else None
    next_page = page + 1 if has_next else None
    
    return render_template('vendas.html', 
                         vendas=vendas_paginadas,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         prev_page=prev_page,
                         next_page=next_page,
                         total_vendas=total_vendas)

@app.route('/venda/<id_venda>')
def detalhes_venda(id_venda):
    """Detalhes de uma venda específica."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    # Calcula lucratividade da venda
    lucratividade = calculator.calcular_lucratividade_venda(id_venda)
    
    return render_template('detalhes_venda.html', 
                         venda_id=id_venda,
                         lucratividade=lucratividade)

@app.route('/analise')
def analise():
    """Página de análise avançada."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    
    # Importa categorias automaticamente em background
    try:
        access_token = db.obter_access_token(user_id)
        if access_token:
            # Verifica se já existem categorias no banco
            conn = db.conectar()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) FROM categorias_mlb")
                    count = cursor.fetchone()[0]
                    if count == 0:
                        print("📋 Importando categorias automaticamente...")
                        categorias = api.obter_categorias_mlb(access_token)
                        if categorias:
                            db.salvar_categorias_mlb(categorias)
                            print(f"✅ {len(categorias)} categorias importadas com sucesso")
                conn.close()
    except Exception as e:
        print(f"⚠️ Erro ao importar categorias automaticamente: {e}")
    
    # Obtém análise geral (busca todos os dados disponíveis)
    analise_geral = calculator.obter_analise_geral_usuario(user_id, 0)
    
    return render_template('analise.html', 
                         analise=analise_geral)

@app.route('/importar')
def importar():
    """Página de importação de dados."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    return render_template('importar.html')

@app.route('/importar/produtos', methods=['POST'])
def importar_produtos():
    """Inicia importação de produtos em background."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    user_id = session['user_id']
    
    # Verifica se já há uma importação ativa
    if import_status['produtos']['ativo']:
        return jsonify({
            'success': False, 
            'message': 'Já existe uma importação de produtos em andamento!'
        })
    
    # Verifica se o token ainda é válido
    access_token = db.obter_access_token(user_id)
    if not access_token:
        return jsonify({
            'success': False, 
            'message': 'Token de acesso não encontrado. Faça login novamente.',
            'redirect': '/auth'
        })
    
    print(f"🔑 Iniciando importação em background para user_id: {user_id}")
    
    # Inicia importação em thread separada
    thread = threading.Thread(target=importar_produtos_background, args=(user_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True, 
        'message': 'Importação iniciada! Acompanhe o progresso na tela.'
    })

@app.route('/importar/status')
def status_importacao():
    """Retorna status atual das importações."""
    return jsonify(import_status)

@app.route('/importar/cancelar/<tipo>')
def cancelar_importacao(tipo):
    """Cancela uma importação em andamento."""
    if tipo in import_status:
        import_status[tipo]['ativo'] = False
        import_status[tipo]['status'] = 'Cancelado pelo usuário'
        import_status[tipo]['fim'] = datetime.now()
        return jsonify({'success': True, 'message': f'Importação de {tipo} cancelada'})
    return jsonify({'success': False, 'message': 'Tipo de importação inválido'})

@app.route('/importar/vendas', methods=['POST'])
def importar_vendas():
    """Inicia importação de vendas em background."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    user_id = session['user_id']
    
    # Verifica se já há uma importação ativa
    if import_status['vendas']['ativo']:
        return jsonify({
            'success': False, 
            'message': 'Já existe uma importação de vendas em andamento!'
        })
    
    # Verifica se o token ainda é válido
    access_token = db.obter_access_token(user_id)
    if not access_token:
        return jsonify({
            'success': False, 
            'message': 'Token de acesso não encontrado. Faça login novamente.',
            'redirect': '/auth'
        })
    
    print(f"🔑 Iniciando importação de vendas em background para user_id: {user_id}")
    
    # Inicia importação usando threading tradicional com melhor gerenciamento
    def run_import():
        try:
            importar_vendas_background(user_id)
        except Exception as e:
            print(f"❌ Erro na thread de importação: {e}")
            import traceback
            traceback.print_exc()
    
    thread = threading.Thread(target=run_import, daemon=True)
    thread.start()
    print(f"🧵 Thread de importação iniciada: {thread.name}")
    
    return jsonify({
        'success': True, 
        'message': 'Importação de vendas iniciada! Acompanhe o progresso na tela.'
    })

@app.route('/api/vendas/detalhes/<venda_id>')
def api_detalhes_venda(venda_id):
    """API para buscar detalhes completos de uma venda."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        detalhes = db.obter_detalhes_venda(venda_id, user_id)
        
        if not detalhes:
            return jsonify({'success': False, 'message': 'Venda não encontrada'})
        
        return jsonify({
            'success': True,
            'detalhes': detalhes
        })
        
    except Exception as e:
        print(f"❌ Erro na API de detalhes da venda: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/packs/detalhes/<pack_id>')
def api_detalhes_pack(pack_id):
    """API para buscar detalhes completos de um pack."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        detalhes = db.obter_detalhes_pack(pack_id, user_id)
        
        if not detalhes:
            return jsonify({'success': False, 'message': 'Pack não encontrado'})
        
        return jsonify({
            'success': True,
            'detalhes': detalhes
        })
        
    except Exception as e:
        print(f"❌ Erro na API de detalhes do pack: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/detalhes-pack/<pack_id>')
def detalhes_pack(pack_id):
    """Página específica para detalhes da venda/pack."""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    try:
        user_id = session['user_id']
        detalhes = db.obter_detalhes_pack(pack_id, user_id)
        
        if not detalhes:
            flash('Venda não encontrada', 'error')
            return redirect(url_for('vendas'))
        
        return render_template('detalhes_venda.html', 
                             detalhes=detalhes, 
                             pack_id=pack_id)
        
    except Exception as e:
        print(f"❌ Erro ao carregar detalhes da venda: {e}")
        flash('Erro ao carregar detalhes da venda', 'error')
        return redirect(url_for('vendas'))

@app.route('/api/lucratividade/<mlb>')
def api_lucratividade_produto(mlb):
    """API para calcular lucratividade de um produto."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    custos = request.args.get('custos', '{}')
    try:
        import json
        custos_dict = json.loads(custos)
    except:
        custos_dict = {}
    
    lucratividade = calculator.calcular_lucratividade_produto(mlb, custos_dict)
    
    if lucratividade:
        return jsonify(lucratividade)
    else:
        return jsonify({'error': 'Produto não encontrado'}), 404

@app.route('/api/lucratividade-venda/<pack_id>')
def api_lucratividade_venda(pack_id):
    """API para calcular lucratividade de um pack."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    custos = request.args.get('custos', '{}')
    try:
        import json
        custos_dict = json.loads(custos)
    except:
        custos_dict = {}
    
    lucratividade = calculator.calcular_lucratividade_venda(pack_id, custos_dict)
    
    if lucratividade:
        return jsonify(lucratividade)
    else:
        return jsonify({'error': 'Pack não encontrado'}), 404

@app.route('/api/lucratividade-pack/<pack_id>')
def api_lucratividade_pack(pack_id):
    """API para calcular lucratividade de um pack usando nova função."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    try:
        user_id = session['user_id']
        lucratividade = db.calcular_lucratividade_pack(pack_id, user_id)
        
        if not lucratividade:
            return jsonify({'success': False, 'message': 'Pack não encontrado'})
        
        return jsonify({
            'success': True,
            'lucratividade': lucratividade
        })
        
    except Exception as e:
        print(f"❌ Erro na API de lucratividade do pack: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'})

@app.route('/api/custos-venda/<pack_id>', methods=['POST'])
def api_salvar_custos_venda(pack_id):
    """API para salvar custos específicos de uma venda."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        custos_por_produto = data.get('custos', {})
        
        # Salva custos para cada produto da venda
        for mlb, custos in custos_por_produto.items():
            db.salvar_custos_venda(pack_id, mlb, custos)
        
        return jsonify({'success': True, 'message': 'Custos salvos com sucesso'})
        
    except Exception as e:
        print(f"Erro ao salvar custos da venda {pack_id}: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/custos-produto/<mlb>', methods=['GET', 'POST'])
def api_custos_produto(mlb):
    """API para obter e salvar custos de um produto."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    user_id = session['user_id']
    
    if request.method == 'GET':
        # Obtém custos atuais do produto
        try:
            conn = db.conectar()
            if not conn:
                return jsonify({'success': False, 'message': 'Erro de conexão'})
            
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT custo_listagem, custo_venda, custo_total, 
                           imposto, embalagem, custo, extra
                    FROM produtos 
                    WHERE user_id = %s AND mlb = %s
                """, (user_id, mlb))
                
                produto = cursor.fetchone()
                if produto:
                    return jsonify({
                        'success': True,
                        'custos': {
                            'custo_listagem': float(produto.get('custo_listagem', 0) or 0),
                            'custo_venda': float(produto.get('custo_venda', 0) or 0),
                            'custo_total': float(produto.get('custo_total', 0) or 0),
                            'imposto': float(produto.get('imposto', 0) or 0),
                            'embalagem': float(produto.get('embalagem', 0) or 0),
                            'custo': float(produto.get('custo', 0) or 0),
                            'extra': float(produto.get('extra', 0) or 0)
                        }
                    })
                else:
                    return jsonify({'success': False, 'message': 'Produto não encontrado'})
                    
        except Exception as e:
            print(f"Erro ao obter custos do produto: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'})
        finally:
            if conn:
                conn.close()
    
    elif request.method == 'POST':
        # Salva custos do produto
        try:
            data = request.get_json()
            custos = data.get('custos', {})
            
            # Valida dados
            imposto = float(custos.get('imposto', 0))
            embalagem = float(custos.get('embalagem', 0))
            custo = float(custos.get('custo', 0))
            extra = float(custos.get('extra', 0))
            
            # Calcula custos totais
            custo_listagem = float(custos.get('custo_listagem', 0))
            custo_venda = float(custos.get('custo_venda', 0))
            custo_total = custo + embalagem + custo_listagem + custo_venda + extra
            
            # Salva no banco
            success = db.salvar_custos_produto(user_id, mlb, {
                'custo_listagem': custo_listagem,
                'custo_venda': custo_venda,
                'custo_total': custo_total,
                'imposto': imposto,
                'embalagem': embalagem,
                'custo': custo,
                'extra': extra
            })
            
            if success:
                return jsonify({'success': True, 'message': 'Custos salvos com sucesso'})
            else:
                return jsonify({'success': False, 'message': 'Erro ao salvar custos'})
                
        except Exception as e:
            print(f"Erro ao salvar custos do produto: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'})

@app.route('/api/sugestao-preco/<mlb>')
def api_sugestao_preco(mlb):
    """API para obter sugestão de preço do Mercado Livre."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    user_id = session['user_id']
    access_token = db.obter_access_token(user_id)
    
    if not access_token:
        return jsonify({'success': False, 'message': 'Token de acesso não encontrado'})
    
    try:
        # Busca sugestão de preço na API do Mercado Livre
        sugestao = api.obter_sugestao_preco(mlb, access_token)
        
        if sugestao:
            return jsonify({
                'success': True,
                'preco_atual': sugestao.get('preco_atual', 0),
                'sugestao': sugestao.get('sugestao', 0),
                'menor_preco': sugestao.get('menor_preco', 0),
                'custo_venda': sugestao.get('custo_venda', 0),
                'custo_envio': sugestao.get('custo_envio', 0)
            })
        else:
            return jsonify({'success': False, 'message': 'Sugestão não encontrada'})
            
    except Exception as e:
        print(f"Erro ao obter sugestão de preço: {e}")
        return jsonify({'success': False, 'message': 'Erro interno'})

@app.route('/api/analise/evolucao-vendas')
def api_evolucao_vendas():
    """API para dados de evolução das vendas."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    user_id = session['user_id']
    periodo = request.args.get('periodo', '30d')
    
    try:
        dados = db.obter_dados_evolucao_vendas(user_id, periodo)
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        print(f"Erro ao obter evolução de vendas: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/api/produtos/preview')
def api_produtos_preview():
    """API para prévia dos produtos."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    user_id = session['user_id']

    try:
        # Busca produtos do banco de dados diretamente
        conn = db.conectar()
        if not conn:
            return jsonify({'error': 'Erro de conexão'}), 500
        
        with conn.cursor(dictionary=True) as cursor:
            # Busca produtos com nome da categoria
            cursor.execute("""
                SELECT p.mlb, p.title, p.price, p.status, p.category, c.name as categoria_nome
                FROM produtos p
                LEFT JOIN categorias_mlb c ON p.category = c.id
                WHERE p.user_id = %s
                ORDER BY p.id DESC
                LIMIT 50
            """, (user_id,))
            produtos_preview = cursor.fetchall()
            
            # Conta total de produtos
            cursor.execute("SELECT COUNT(*) as total FROM produtos WHERE user_id = %s", (user_id,))
            total = cursor.fetchone()['total']
        
        if not produtos_preview:
            return jsonify({'success': False, 'message': 'Nenhum produto encontrado'})
        
        return jsonify({
            'success': True,
            'produtos': produtos_preview,
            'total': total
        })
        
    except Exception as e:
        print(f"Erro ao buscar preview de produtos: {e}")
        return jsonify({'error': 'Erro interno'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/vendas/preview')
def api_vendas_preview():
    """API para prévia das vendas agrupadas por packs."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    user_id = session['user_id']

    try:
        # Busca vendas do banco de dados agrupadas por pack
        conn = db.conectar()
        if not conn:
            return jsonify({'error': 'Erro de conexão'}), 500
        
        with conn.cursor(dictionary=True) as cursor:
            # Busca vendas agrupadas por pack_id
            cursor.execute("""
                SELECT 
                    COALESCE(pack_id, id_venda) as pack_id,
                    COUNT(*) as total_produtos,
                    SUM(COALESCE(item_preco_total, 0)) as valor_total,
                    SUM(COALESCE(taxa_venda, 0)) as taxa_total,
                    SUM(COALESCE(frete, 0)) as frete_total,
                    MAX(status) as status,
                    MAX(data_aprovacao) as data_aprovacao,
                    MAX(comprador) as comprador,
                    GROUP_CONCAT(
                        CONCAT(item_titulo, ' (', item_quantidade, 'x)') 
                        SEPARATOR ' | '
                    ) as produtos
                FROM vendas v
                LEFT JOIN venda_itens vi ON v.venda_id = vi.venda_id AND v.user_id = vi.user_id
                WHERE v.user_id = %s
                GROUP BY v.venda_id, v.pack_id
                ORDER BY v.data_aprovacao DESC
                LIMIT 50
            """, (user_id,))
            vendas_agrupadas = cursor.fetchall()
            
            # Conta total de packs únicos
            cursor.execute("""
                SELECT COUNT(DISTINCT COALESCE(pack_id, venda_id)) as total 
                FROM vendas WHERE user_id = %s
            """, (user_id,))
            total = cursor.fetchone()['total']
        
        if not vendas_agrupadas:
            return jsonify({'success': False, 'message': 'Nenhuma venda encontrada'})
        
        return jsonify({
            'success': True,
            'vendas': vendas_agrupadas,
            'total': total
        })
        
    except Exception as e:
        print(f"Erro ao buscar preview de vendas: {e}")
        return jsonify({'error': 'Erro interno'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/custos/preview')
def api_custos_preview():
    """API para prévia dos custos."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    user_id = session['user_id']
    
    try:
        # Busca custos do usuário
        conn = db.conectar()
        if not conn:
            return jsonify({'error': 'Erro de conexão'}), 500
        
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT c.mlb, c.custos as custos_ml, c.tipo, c.porcentagem_da_comissao,
                       p.title, p.custo_listagem, p.custo_venda, p.imposto, p.embalagem, p.custo, p.extra,
                       f.frete
                FROM custos c
                LEFT JOIN produtos p ON c.mlb = p.mlb
                LEFT JOIN frete f ON c.mlb = f.mlb
                WHERE p.user_id = %s
                ORDER BY c.id DESC
                LIMIT 50
            """, (user_id,))
            custos = cursor.fetchall()
        
        if not custos:
            return jsonify({'success': False, 'message': 'Nenhum custo encontrado'})
        
        return jsonify({
            'success': True,
            'custos': custos,
            'total': len(custos)
        })
        
    except Exception as e:
        print(f"Erro ao buscar preview de custos: {e}")
        return jsonify({'error': 'Erro interno'}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/api/analise/categorias')
def api_analise_categorias():
    """API para dados de vendas por categoria."""
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    user_id = session['user_id']
    
    try:
        dados = db.obter_dados_categorias_vendas(user_id)
        
        return jsonify({
            'success': True,
            'dados': dados
        })
        
    except Exception as e:
        print(f"Erro ao obter dados de categorias: {e}")
        return jsonify({'error': 'Erro interno'}), 500

@app.route('/importar/categorias', methods=['POST'])
def importar_categorias():
    """Importa categorias do Mercado Livre."""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})
    
    user_id = session['user_id']
    access_token = db.obter_access_token(user_id)
    
    if not access_token:
        return jsonify({'success': False, 'message': 'Token de acesso não encontrado'})
    
    try:
        # Verifica se já existem categorias no banco
        conn = db.conectar()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM categorias_mlb")
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f"📋 Categorias já existem no banco ({count} categorias), pulando importação")
                    return jsonify({
                        'success': True, 
                        'message': f'Categorias já existem ({count} categorias)'
                    })
            conn.close()
        
        # Obtém categorias do Mercado Livre
        categorias = api.obter_categorias_site(access_token, "MLB")
        
        if not categorias:
            return jsonify({'success': False, 'message': 'Nenhuma categoria encontrada'})
        
        # Salva no banco de dados
        if db.salvar_categorias_mlb(categorias):
            return jsonify({
                'success': True, 
                'message': f'{len(categorias)} categorias importadas com sucesso!'
            })
        else:
            return jsonify({'success': False, 'message': 'Erro ao salvar categorias'})
            
    except Exception as e:
        print(f"Erro ao importar categorias: {e}")
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

@app.route('/perfil')
def perfil():
    """Página de perfil do usuário."""
    if 'user_id' not in session:
        flash('Você precisa fazer login primeiro', 'warning')
        return redirect(url_for('index'))
    
    user_id = session['user_id']
    access_token = db.obter_access_token(user_id)
    
    if not access_token:
        flash('Token de acesso não encontrado', 'error')
        return redirect(url_for('index'))
    
    try:
        # Obtém informações do usuário
        user_info = api.obter_informacoes_usuario(access_token)
        
        if not user_info:
            flash('Erro ao carregar informações do perfil', 'error')
            return redirect(url_for('dashboard'))
        
        # Obtém estatísticas do banco de dados
        conn = db.conectar()
        stats = {}
        if conn:
            try:
                with conn.cursor() as cursor:
                    # Total de produtos
                    cursor.execute("SELECT COUNT(*) FROM produtos WHERE user_id = %s", (user_id,))
                    stats['total_produtos'] = cursor.fetchone()[0] or 0
                    
                    # Total de vendas
                    cursor.execute("SELECT COUNT(*) FROM vendas WHERE user_id = %s", (user_id,))
                    stats['total_vendas'] = cursor.fetchone()[0] or 0
                    
                    # Receita total
                    cursor.execute("SELECT SUM(valor_total) FROM vendas WHERE user_id = %s", (user_id,))
                    stats['receita_total'] = float(cursor.fetchone()[0] or 0)
                    
                    # Produtos ativos
                    cursor.execute("SELECT COUNT(*) FROM produtos WHERE user_id = %s AND status = 'active'", (user_id,))
                    stats['produtos_ativos'] = cursor.fetchone()[0] or 0
                    
                    # Produtos pausados
                    cursor.execute("SELECT COUNT(*) FROM produtos WHERE user_id = %s AND status = 'paused'", (user_id,))
                    stats['produtos_pausados'] = cursor.fetchone()[0] or 0
                    
            except Exception as e:
                print(f"Erro ao obter estatísticas: {e}")
            finally:
                conn.close()
        
        return render_template('perfil.html', 
                             user_info=user_info['user_info'],
                             reputation=user_info['reputation'],
                             sales_info=user_info['sales_info'],
                             seller_reputation=user_info['seller_reputation'],
                             stats=stats)
        
    except Exception as e:
        print(f"Erro ao carregar perfil: {e}")
        flash('Erro ao carregar informações do perfil', 'error')
        return redirect(url_for('dashboard'))


@app.errorhandler(404)
def not_found(error):
    """Página 404."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Página 500."""
    return render_template('500.html'), 500

# ============================================================================
# WEBHOOKS DO MERCADO LIVRE
# ============================================================================

@app.route('/webhook/mercadolivre', methods=['POST'])
def webhook_mercadolivre():
    """Endpoint universal para receber webhooks do Mercado Livre."""
    try:
        # Log da notificação recebida
        notification_data = request.get_json()
        print(f"🔔 Webhook recebido: {notification_data.get('topic', 'unknown')} - {notification_data.get('resource', 'N/A')}")
        
        # Validar se é uma notificação válida
        if not notification_data or 'topic' not in notification_data:
            print("❌ Notificação inválida: sem campo 'topic'")
            return jsonify({'status': 'error', 'message': 'Notificação inválida'}), 400
        
        # Processar notificação usando o sistema universal
        success = webhook_processor.process_notification(notification_data)
        
        if success:
            print(f"✅ Webhook processado com sucesso: {notification_data.get('topic')}")
            return jsonify({'status': 'success', 'message': 'Notificação processada com sucesso'}), 200
        else:
            print(f"❌ Falha ao processar webhook: {notification_data.get('topic')}")
            return jsonify({'status': 'error', 'message': 'Falha ao processar notificação'}), 500
        
    except Exception as e:
        print(f"❌ Erro ao processar webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/webhook/stats')
@login_required
def webhook_stats():
    """API para obter estatísticas de webhooks."""
    try:
        user_id = session.get('user_id')
        stats = db.obter_estatisticas_webhooks(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/webhook/logs')
@login_required
def webhook_logs():
    """API para obter logs de webhooks."""
    try:
        user_id = session.get('user_id')
        topic = request.args.get('topic')
        limit = int(request.args.get('limit', 100))
        
        logs = db.obter_logs_webhook(user_id, topic, limit)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/webhooks')
@login_required
def webhooks():
    """Tela de monitoramento de webhooks."""
    return render_template('webhooks.html')

@app.route('/test-webhooks')
@login_required
def test_webhooks():
    """Tela de teste de webhooks."""
    return render_template('test_webhook_page.html')

def processar_notificacao_webhook(notification_data):
    """Processa notificação webhook em background."""
    try:
        topic = notification_data.get('topic')
        resource = notification_data.get('resource')
        user_id = notification_data.get('user_id')
        
        print(f"📋 Processando notificação - Tópico: {topic}, Recurso: {resource}, User: {user_id}")
        
        # Processar baseado no tópico
        if topic == 'items':
            processar_notificacao_item(resource, user_id)
        elif topic == 'orders_v2':
            processar_notificacao_venda(resource, user_id)
        elif topic == 'price_suggestion':
            processar_notificacao_sugestao_preco(resource, user_id)
        elif topic == 'questions':
            processar_notificacao_pergunta(resource, user_id)
        else:
            print(f"⚠️ Tópico não processado: {topic}")
            
    except Exception as e:
        print(f"❌ Erro ao processar notificação: {e}")

def processar_notificacao_item(resource, user_id):
    """Processa notificação de mudança em item - ATUALIZADO PARA CAPTURAR TODAS AS MUDANÇAS."""
    try:
        # Extrair MLB do resource (ex: /items/MLA686791111)
        if '/items/' in resource:
            mlb = resource.split('/items/')[-1]
            print(f"🔄 Processando mudança no item: {mlb}")
            
            # Buscar access token do usuário
            access_token = db.obter_access_token(user_id)
            if not access_token:
                print(f"❌ Token não encontrado para usuário: {user_id}")
                return
            
            # Verificar se produto existe no banco local
            produto_existe = db.verificar_produto_existe(mlb, user_id)
            
            # Buscar dados atualizados do Mercado Livre
            api = MercadoLivreAPI()
            produto_data = api.obter_detalhes_completos_produto(mlb, user_id)
            
            if produto_data and produto_data.get('produto'):
                # Produto existe no ML - atualizar dados
                produto_info = produto_data.get('produto', {})
                
                # Validar dados essenciais
                if not produto_info.get('title') or not produto_info.get('id'):
                    print(f"❌ Dados incompletos para item {mlb}: título ou ID ausente")
                    return
                
                # Log das mudanças detectadas
                print(f"📊 Atualizando produto {mlb}:")
                print(f"   - Título: {produto_info.get('title', 'N/A')[:50]}...")
                print(f"   - Preço: R$ {produto_info.get('price', 0)}")
                print(f"   - Status: {produto_info.get('status', 'N/A')}")
                print(f"   - Estoque: {produto_info.get('available_quantity', 0)}")
                print(f"   - Frete Grátis: {produto_info.get('shipping', {}).get('free_shipping', False)}")
                print(f"   - Dados completos da API: {produto_info}")
                
                # Verificar status atual no banco
                status_atual_banco = db.obter_status_produto(mlb, user_id)
                novo_status = produto_info.get('status', 'active')
                print(f"   - Status no banco: {status_atual_banco}")
                print(f"   - Status da API: {novo_status}")
                
                # Salvar/atualizar produto com TODOS os dados
                success = db.salvar_produto_com_variacoes(produto_info, user_id)
                if success:
                    print(f"✅ Item {mlb} atualizado com sucesso - TODOS os campos sincronizados")
                else:
                    print(f"❌ Erro ao salvar item {mlb}")
                    
            elif produto_existe:
                # Produto não existe mais no ML mas existe localmente - marcar como excluído
                print(f"🗑️ Produto {mlb} foi excluído do Mercado Livre - marcando como excluído")
                db.marcar_produto_como_excluido(mlb, user_id)
                print(f"✅ Produto {mlb} marcado como excluído")
            else:
                print(f"⚠️ Produto {mlb} não encontrado no ML e não existe localmente")
                
    except Exception as e:
        print(f"❌ Erro ao processar notificação de item: {e}")
        import traceback
        traceback.print_exc()

def processar_notificacao_venda(resource, user_id):
    """Processa notificação de mudança em venda (orders_v2)."""
    try:
        # Extrair ID da venda do resource (ex: /orders/2195160686)
        if '/orders/' in resource:
            order_id = resource.split('/orders/')[-1]
            print(f"🛒 Processando venda: {order_id}")
            
            # Buscar access token do usuário
            access_token = db.obter_access_token(user_id)
            if not access_token:
                print(f"❌ Token não encontrado para usuário: {user_id}")
                return
            
            # Buscar detalhes completos da venda
            api = MercadoLivreAPI()
            venda_data = api.obter_detalhes_venda_completa(order_id, access_token)
            
            if venda_data:
                # Salvar/atualizar venda com status detalhado
                success = db.salvar_venda_com_status(venda_data, user_id)
                if success:
                    print(f"✅ Venda {order_id} atualizada com sucesso")
                    print(f"   📊 Status: {venda_data.get('status', 'N/A')}")
                    print(f"   💳 Pagamento: {venda_data.get('payment_status', 'N/A')}")
                    print(f"   📦 Envio: {venda_data.get('shipping_status', 'N/A')}")
                else:
                    print(f"❌ Erro ao salvar venda {order_id}")
            else:
                print(f"❌ Dados da venda {order_id} não encontrados")
                
    except Exception as e:
        print(f"❌ Erro ao processar notificação de venda: {e}")
        import traceback
        traceback.print_exc()

def processar_notificacao_pedido(resource, user_id):
    """Processa notificação de mudança em pedido (mantido para compatibilidade)."""
    # Redirecionar para a nova função de venda
    processar_notificacao_venda(resource, user_id)

def processar_notificacao_sugestao_preco(resource, user_id):
    """Processa notificação de sugestão de preço."""
    try:
        # Extrair MLB do resource (ex: suggestions/items/MLA686791111/details)
        if '/suggestions/items/' in resource:
            mlb = resource.split('/suggestions/items/')[-1].split('/details')[0]
            print(f"💰 Atualizando sugestão de preço: {mlb}")
            
            # Buscar access token do usuário
            access_token = db.obter_access_token(user_id)
            if not access_token:
                print(f"❌ Token não encontrado para usuário: {user_id}")
                return
            
            # Atualizar sugestão de preço
            api = MercadoLivreAPI()
            sugestao_data = api.obter_sugestao_preco(mlb, access_token)
            
            if sugestao_data:
                # Salvar/atualizar sugestão
                success = db.salvar_sugestao_preco(mlb, sugestao_data, user_id)
                if success:
                    print(f"✅ Sugestão de preço {mlb} atualizada com sucesso")
                else:
                    print(f"❌ Erro ao salvar sugestão de preço {mlb}")
            else:
                print(f"❌ Dados da sugestão de preço {mlb} não encontrados")
                
    except Exception as e:
        print(f"❌ Erro ao processar notificação de sugestão de preço: {e}")

def processar_notificacao_pergunta(resource, user_id):
    """Processa notificação de pergunta."""
    try:
        # Extrair ID da pergunta do resource (ex: /questions/5036111111)
        if '/questions/' in resource:
            question_id = resource.split('/questions/')[-1]
            print(f"❓ Processando pergunta: {question_id}")
            
            # Aqui você pode implementar lógica para processar perguntas
            # Por exemplo, salvar em uma tabela de perguntas
            print(f"✅ Pergunta {question_id} processada")
                
    except Exception as e:
        print(f"❌ Erro ao processar notificação de pergunta: {e}")

if __name__ == '__main__':
    # Cria tabelas se não existirem
    db.criar_tabelas()
    
    # Inicia monitor de tokens automaticamente
    try:
        start_token_monitoring()
        print("🔄 Monitor de tokens iniciado automaticamente")
    except Exception as e:
        print(f"⚠️ Erro ao iniciar monitor de tokens: {e}")

    # Obtém porta do ambiente ou usa 3001 como padrão
    port = int(os.getenv('PORT', 3001))
    
    # Configurar para HTTPS quando usando ngrok
    ssl_context = None
    if os.getenv('NGROK_HTTPS') == 'true':
        ssl_context = 'adhoc'  # Gera certificado auto-assinado
    
    # Inicia aplicação
    app.run(debug=True, host='0.0.0.0', port=port, ssl_context=ssl_context)
