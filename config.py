import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Incrementar após mudanças em CSS/templates para invalidar cache do navegador
    ASSET_VERSION = os.environ.get('ASSET_VERSION') or '20260528c'

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///artistas_sistema.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configurações do Google Calendar
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') or '827660682661-ifovus9g3o922ikgemrqtot4d137p329.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET') or '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'
    GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI') or 'http://127.0.0.1:5005/google/callback'
    
    # Cores para artistas (rotativo)
    ARTIST_COLORS = [
        '#FF6B6B',  # Vermelho
        '#4ECDC4',  # Turquesa
        '#45B7D1',  # Azul
        '#96CEB4',  # Verde
        '#FFEAA7',  # Amarelo
        '#DDA0DD',  # Roxo
        '#FFB347',  # Laranja
        '#87CEEB',  # Azul claro
        '#F0E68C',  # Khaki
        '#FF69B4'   # Rosa
    ]
