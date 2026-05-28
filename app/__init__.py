from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
import atexit

# Inicialização das extensões
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Registrar blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')
    
    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    
    from app.alerts.routes import alerts_bp
    app.register_blueprint(alerts_bp, url_prefix='/alerts')
    
    from app.marketing import bp as marketing_bp
    app.register_blueprint(marketing_bp, url_prefix='/marketing')

    from app.crm import bp as crm_bp
    app.register_blueprint(crm_bp, url_prefix='/crm')

    from app.catalog import bp as catalog_bp
    app.register_blueprint(catalog_bp, url_prefix='/cadastros')

    from app.finance import bp as finance_bp
    app.register_blueprint(finance_bp, url_prefix='/financeiro')

    from app.p7 import bp as p7_bp
    app.register_blueprint(p7_bp)

    from app.team import bp as team_bp
    app.register_blueprint(team_bp)

    from app.portal import bp as portal_bp
    app.register_blueprint(portal_bp)

    from app.devtools import bp as devtools_bp
    app.register_blueprint(devtools_bp)
    
    from app.google_auth import bp as google_auth_bp
    app.register_blueprint(google_auth_bp, url_prefix='/google')
    
    # Rota adicional para callback direto (Google OAuth precisa de /google/callback)
    @app.route('/google/callback')
    def google_callback():
        from app.google_auth.routes import callback
        return callback()
    
    # Adicionar filtros customizados para templates
    @app.template_filter('format_date')
    def format_date_filter(date_string):
        """Formatar data no formato brasileiro"""
        try:
            from datetime import datetime
            if isinstance(date_string, str):
                # Parse da string de data
                if 'T' in date_string:
                    date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
                else:
                    date_obj = datetime.strptime(date_string, '%Y-%m-%d')
                return date_obj.strftime('%d/%m/%Y')
            elif hasattr(date_string, 'strftime'):
                return date_string.strftime('%d/%m/%Y')
            return str(date_string)
        except:
            return str(date_string)
    
    @app.template_filter('format_datetime')
    def format_datetime_filter(datetime_string):
        """Formatar data e hora no formato brasileiro"""
        try:
            from datetime import datetime
            if isinstance(datetime_string, str):
                # Parse da string de datetime
                if 'T' in datetime_string:
                    datetime_obj = datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
                else:
                    datetime_obj = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
                return datetime_obj.strftime('%d/%m/%Y às %H:%M')
            elif hasattr(datetime_string, 'strftime'):
                return datetime_string.strftime('%d/%m/%Y às %H:%M')
            return str(datetime_string)
        except:
            return str(datetime_string)

    @app.context_processor
    def inject_globals():
        return {'asset_version': app.config.get('ASSET_VERSION', '1')}

    @app.route('/__version')
    def app_version():
        from flask import jsonify
        return jsonify({
            'asset_version': app.config.get('ASSET_VERSION'),
            'login_template': 'standalone-v2',
        })

    # Inicializar scheduler
    if not scheduler.running:
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())

    _maybe_seed_demo_on_start(app)

    return app


def _maybe_seed_demo_on_start(app):
    """Carrega dados de demonstração na subida se configurado e ainda não existirem."""
    if not app.config.get('SEED_DEMO_ON_START'):
        return
    with app.app_context():
        try:
            from seed_demo import demo_exists, run_seed
            if demo_exists():
                return
            result = run_seed(reset=False)
            app.logger.info(
                'Demo seed on start: %s assessorados, %s leads',
                result.get('artists', 0),
                result.get('leads', 0),
            )
        except Exception as exc:
            app.logger.exception('Falha ao carregar demo no startup: %s', exc)

# User loader para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

from app import models
