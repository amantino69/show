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
    
    from app.google_auth import bp as google_auth_bp
    app.register_blueprint(google_auth_bp, url_prefix='/auth/google')
    
    # Rota adicional para callback direto (Google OAuth precisa de /callback)
    @app.route('/callback')
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

    # Inicializar scheduler
    if not scheduler.running:
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
    
    return app

# User loader para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

from app import models
