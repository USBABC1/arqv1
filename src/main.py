import os
import logging
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from database import db
from routes.user import user_bp
from routes.analysis import analysis_bp

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente
load_dotenv()

# Criar aplicação Flask
app = Flask(__name__, static_folder='static')

# Configurar CORS para permitir todas as origens
CORS(app, origins=os.getenv('CORS_ORIGINS', '*'))

# Configuração da aplicação
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a-default-secret-key-that-should-be-changed')

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(analysis_bp, url_prefix='/api')

# Configuração do banco de dados com tratamento robusto de erros
database_url = os.getenv('DATABASE_URL')
if database_url:
    try:
        # Configuração otimizada para Supabase
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_timeout': 30,
            'pool_size': 10,
            'max_overflow': 20,
            'connect_args': {
                'sslmode': 'require',
                'connect_timeout': 30,
                'application_name': 'ARQV2_DeepSeek_App',
                'options': '-c timezone=UTC'
            }
        }
        
        db.init_app(app)
        
        with app.app_context():
            try:
                # Teste de conexão mais robusto
                from sqlalchemy import text
                result = db.session.execute(text('SELECT version()'))
                version_info = result.fetchone()
                logger.info(f"✅ Conexão com Supabase estabelecida com sucesso!")
                logger.info(f"📊 Versão PostgreSQL: {version_info[0] if version_info else 'Desconhecida'}")
                
                # Verificar se as tabelas existem
                tables_check = db.session.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('analyses', 'analysis_templates')
                """))
                existing_tables = [row[0] for row in tables_check.fetchall()]
                logger.info(f"📋 Tabelas encontradas: {existing_tables}")
                
                if 'analyses' not in existing_tables:
                    logger.warning("⚠️ Tabela 'analyses' não encontrada. Execute as migrações do Supabase.")
                
            except Exception as e:
                logger.warning(f"⚠️ Erro na verificação do banco de dados: {e}")
                logger.info("🔄 Aplicação funcionará com funcionalidades limitadas")
                
    except Exception as e:
        logger.error(f"❌ Erro na configuração do banco de dados: {e}")
        logger.info("🔄 Aplicação funcionará sem persistência de dados")
else:
    logger.warning("⚠️ DATABASE_URL não encontrada. Executando sem funcionalidades de banco de dados.")

# Verificar configuração das APIs
def check_api_configuration():
    """Verifica se as APIs estão configuradas corretamente"""
    apis_status = {}
    
    # Verificar DeepSeek API
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key and deepseek_key.startswith('sk-'):
        apis_status['deepseek'] = 'configured'
        logger.info("🤖 DeepSeek API configurada")
    else:
        apis_status['deepseek'] = 'not_configured'
        logger.warning("⚠️ DeepSeek API não configurada")
    
    # Verificar Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    if supabase_url and supabase_key:
        apis_status['supabase'] = 'configured'
        logger.info("🗄️ Supabase configurado")
    else:
        apis_status['supabase'] = 'not_configured'
        logger.warning("⚠️ Supabase não configurado")
    
    return apis_status

# Verificar configuração na inicialização
api_status = check_api_configuration()

# Rota de health check aprimorada
@app.route('/health')
def health_check():
    """Health check com informações detalhadas do sistema"""
    
    # Status das APIs
    deepseek_status = api_status.get('deepseek', 'not_configured')
    supabase_status = api_status.get('supabase', 'not_configured')
    database_status = 'configured' if database_url else 'not_configured'
    
    # Verificar conectividade do banco
    db_connection_status = 'disconnected'
    if database_url:
        try:
            with app.app_context():
                from sqlalchemy import text
                db.session.execute(text('SELECT 1'))
                db_connection_status = 'connected'
        except Exception as e:
            logger.error(f"Erro na verificação de conectividade do DB: {e}")
            db_connection_status = 'error'
    
    # Status geral do sistema
    overall_status = 'healthy'
    if deepseek_status == 'not_configured' or db_connection_status == 'error':
        overall_status = 'degraded'
    
    return jsonify({
        'status': overall_status,
        'message': 'UP Lançamentos - Arqueologia do Avatar com DeepSeek AI',
        'services': {
            'deepseek_ai': deepseek_status,
            'supabase': supabase_status,
            'database': database_status,
            'db_connection': db_connection_status
        },
        'version': '2.1.0',
        'environment': os.getenv('FLASK_ENV', 'development'),
        'timestamp': os.popen('date').read().strip(),
        'features': {
            'web_search': True,
            'ai_analysis': deepseek_status == 'configured',
            'data_persistence': db_connection_status == 'connected',
            'real_time_research': True
        }
    })

# Rota para informações do sistema
@app.route('/api/system/info')
def system_info():
    """Informações detalhadas do sistema"""
    return jsonify({
        'app_name': 'UP Lançamentos - Arqueologia do Avatar',
        'version': '2.1.0',
        'ai_model': 'DeepSeek R1 Distill Llama 70B',
        'features': [
            'Análise ultra-detalhada de avatar',
            'Pesquisa em tempo real na internet',
            'Análise competitiva avançada',
            'Projeções baseadas em dados reais',
            'Plano de ação executável'
        ],
        'supported_niches': [
            'Marketing Digital',
            'Neuroeducação',
            'Fitness e Bem-estar',
            'Desenvolvimento Pessoal',
            'Finanças e Investimentos',
            'Saúde e Medicina',
            'Educação Online',
            'Consultoria Empresarial'
        ]
    })

# Rota para servir arquivos estáticos e SPA
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve arquivos estáticos e SPA"""
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Tratamento de erros aprimorado
@app.errorhandler(404)
def not_found(error):
    """Handler para erro 404"""
    return jsonify({
        'error': 'Recurso não encontrado',
        'message': 'O endpoint solicitado não existe',
        'status_code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erro 500"""
    logger.error(f"Erro interno: {error}")
    return jsonify({
        'error': 'Erro interno do servidor',
        'message': 'Ocorreu um erro inesperado. Tente novamente.',
        'status_code': 500
    }), 500

@app.errorhandler(400)
def bad_request(error):
    """Handler para erro 400"""
    return jsonify({
        'error': 'Requisição inválida',
        'message': 'Os dados enviados são inválidos',
        'status_code': 400
    }), 400

@app.errorhandler(429)
def rate_limit_exceeded(error):
    """Handler para erro 429"""
    return jsonify({
        'error': 'Limite de requisições excedido',
        'message': 'Muitas requisições. Tente novamente em alguns minutos.',
        'status_code': 429
    }), 429

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    logger.info(f"🚀 Iniciando UP Lançamentos na porta {port}")
    logger.info(f"🔧 Modo debug: {debug}")
    logger.info(f"🌐 Ambiente: {os.getenv('FLASK_ENV', 'development')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)