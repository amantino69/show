from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)  # True para empresário
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_token = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='user_account', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stage_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), nullable=False)  # Cor em hex para agenda
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    events = db.relationship('Event', backref='artist', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Artist {self.stage_name}>'

class EventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(7), nullable=False)
    
    # Relacionamentos
    events = db.relationship('Event', backref='event_type', lazy=True)
    
    def __repr__(self):
        return f'<EventType {self.name}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'), nullable=False)
    status = db.Column(db.String(20), default='agendado')  # agendado, em_andamento, concluido, cancelado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    google_event_id = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    
    # Campos para estatísticas
    actual_start = db.Column(db.DateTime, nullable=True)
    actual_end = db.Column(db.DateTime, nullable=True)
    result_notes = db.Column(db.Text, nullable=True)
    success_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    
    def __repr__(self):
        return f'<Event {self.title}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # reminder, update, cancellation, test
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para diferentes tipos de notificação
    push_notification_sent = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    whatsapp_sent = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    event = db.relationship('Event', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title} for Event {self.event_id}>'


# =============================================================================
# MODELOS PARA MARKETING E DIVULGAÇÃO
# =============================================================================

class MediaFile(db.Model):
    """Banco de mídia para fotos, vídeos, releases"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # image, video, audio, document
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # em bytes
    
    # Metadados
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # tags separadas por vírgula
    
    # Relacionamentos
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    
    # Metadados da imagem/vídeo
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # duração em segundos (vídeo/áudio)
    
    # Status e datas
    is_public = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # destaque
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='media_files')
    event = db.relationship('Event', backref='media_files')
    uploader = db.relationship('User', backref='uploaded_files')
    
    def __repr__(self):
        return f'<MediaFile {self.filename}>'

class SocialPost(db.Model):
    """Calendário de posts para redes sociais"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, facebook, twitter, youtube, tiktok
    
    # Agendamento
    scheduled_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    
    # Relacionamentos
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)  # opcional
    media_file_id = db.Column(db.Integer, db.ForeignKey('media_file.id'), nullable=True)
    
    # Métricas (preenchidas após publicação)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    
    # Dados da publicação
    published_at = db.Column(db.DateTime, nullable=True)
    external_post_id = db.Column(db.String(255), nullable=True)  # ID na plataforma externa
    external_url = db.Column(db.String(500), nullable=True)
    
    # Metadados
    hashtags = db.Column(db.String(1000), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    
    # Auditoria
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='social_posts')
    event = db.relationship('Event', backref='social_posts')
    media_file = db.relationship('MediaFile', backref='social_posts')
    creator = db.relationship('User', backref='created_posts')
    
    def __repr__(self):
        return f'<SocialPost {self.title} - {self.platform}>'

class PressKit(db.Model):
    """Press Kit digital para artistas"""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    
    # Informações básicas
    bio_short = db.Column(db.Text, nullable=True)  # bio curta (100-200 palavras)
    bio_long = db.Column(db.Text, nullable=True)   # bio completa
    achievements = db.Column(db.Text, nullable=True)  # conquistas e destaques
    
    # Mídia
    profile_photo_id = db.Column(db.Integer, db.ForeignKey('media_file.id'), nullable=True)
    banner_photo_id = db.Column(db.Integer, db.ForeignKey('media_file.id'), nullable=True)
    
    # Links e contatos
    website = db.Column(db.String(300), nullable=True)
    instagram = db.Column(db.String(300), nullable=True)
    facebook = db.Column(db.String(300), nullable=True)
    youtube = db.Column(db.String(300), nullable=True)
    spotify = db.Column(db.String(300), nullable=True)
    deezer = db.Column(db.String(300), nullable=True)
    apple_music = db.Column(db.String(300), nullable=True)
    
    # Informações técnicas
    technical_rider = db.Column(db.Text, nullable=True)  # rider técnico
    stage_plot = db.Column(db.Text, nullable=True)       # disposição do palco
    
    # Informações comerciais
    booking_contact = db.Column(db.String(200), nullable=True)
    booking_email = db.Column(db.String(200), nullable=True)
    booking_phone = db.Column(db.String(50), nullable=True)
    
    # Configurações
    is_public = db.Column(db.Boolean, default=True)
    template_style = db.Column(db.String(50), default='default')  # tema do press kit
    
    # Auditoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='press_kit', uselist=False)
    profile_photo = db.relationship('MediaFile', foreign_keys=[profile_photo_id])
    banner_photo = db.relationship('MediaFile', foreign_keys=[banner_photo_id])
    
    def __repr__(self):
        return f'<PressKit for {self.artist.stage_name}>'

class SocialMetrics(db.Model):
    """Métricas consolidadas de redes sociais"""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    
    # Métricas de seguimento
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    
    # Métricas de engajamento (período)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_likes = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_shares = db.Column(db.Integer, default=0)
    total_views = db.Column(db.Integer, default=0)
    total_reach = db.Column(db.Integer, default=0)
    
    # Crescimento
    followers_growth = db.Column(db.Integer, default=0)  # variação no período
    engagement_rate = db.Column(db.Float, default=0.0)   # taxa de engajamento
    
    # Metadados
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='social_metrics')
    
    def __repr__(self):
        return f'<SocialMetrics {self.artist.stage_name} - {self.platform}>'
