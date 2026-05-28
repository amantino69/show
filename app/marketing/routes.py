from flask import render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.marketing import bp
from app.models import Artist, Event, MediaFile, SocialPost, PressKit, SocialMetrics
from app import db
from datetime import datetime, timedelta
import os
import uuid
from PIL import Image
import mimetypes

# Configurações para upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'avi', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(mimetype):
    if mimetype.startswith('image/'):
        return 'image'
    elif mimetype.startswith('video/'):
        return 'video'
    elif mimetype.startswith('audio/'):
        return 'audio'
    else:
        return 'document'

# =============================================================================
# ROTAS PRINCIPAIS
# =============================================================================

@bp.route('/')
@login_required
def index():
    """Dashboard principal de marketing"""
    # Estatísticas gerais
    total_media = MediaFile.query.count()
    scheduled_posts = SocialPost.query.filter_by(status='scheduled').count()
    published_posts = SocialPost.query.filter_by(status='published').count()
    
    # Posts recentes
    recent_posts = SocialPost.query.order_by(SocialPost.created_at.desc()).limit(5).all()
    
    # Próximos posts agendados
    upcoming_posts = SocialPost.query.filter(
        SocialPost.status == 'scheduled',
        SocialPost.scheduled_datetime >= datetime.utcnow()
    ).order_by(SocialPost.scheduled_datetime).limit(5).all()
    
    # Mídia recente
    recent_media = MediaFile.query.order_by(MediaFile.created_at.desc()).limit(6).all()
    
    return render_template('marketing/dashboard.html',
                         total_media=total_media,
                         scheduled_posts=scheduled_posts,
                         published_posts=published_posts,
                         recent_posts=recent_posts,
                         upcoming_posts=upcoming_posts,
                         recent_media=recent_media)

# =============================================================================
# BANCO DE MÍDIA
# =============================================================================

@bp.route('/media')
@login_required
def media_library():
    """Biblioteca de mídia"""
    file_type = request.args.get('type', 'all')
    artist_id = request.args.get('artist_id', type=int)
    
    query = MediaFile.query
    
    if file_type != 'all':
        query = query.filter_by(file_type=file_type)
    
    if artist_id:
        query = query.filter_by(artist_id=artist_id)
    
    media_files = query.order_by(MediaFile.created_at.desc()).all()
    artists = Artist.query.filter_by(is_active=True).all()
    
    return render_template('marketing/media_library.html',
                         media_files=media_files,
                         artists=artists,
                         current_type=file_type,
                         current_artist=artist_id)

@bp.route('/media/upload', methods=['GET', 'POST'])
@login_required
def upload_media():
    """Upload de arquivos de mídia"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Gerar nome único
            filename = secure_filename(file.filename)
            unique_filename = str(uuid.uuid4()) + '_' + filename
            
            # Criar diretório se não existir
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'media')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Obter informações do arquivo
            file_size = os.path.getsize(file_path)
            mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
            file_type = get_file_type(mime_type)
            
            # Metadados de imagem
            width, height = None, None
            if file_type == 'image':
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                except:
                    pass
            
            # Salvar no banco
            media_file = MediaFile(
                filename=unique_filename,
                original_filename=filename,
                file_path=f'uploads/media/{unique_filename}',
                file_type=file_type,
                mime_type=mime_type,
                file_size=file_size,
                width=width,
                height=height,
                title=request.form.get('title', ''),
                description=request.form.get('description', ''),
                tags=request.form.get('tags', ''),
                artist_id=request.form.get('artist_id') or None,
                event_id=request.form.get('event_id') or None,
                uploaded_by=current_user.id
            )
            
            db.session.add(media_file)
            db.session.commit()
            
            flash('Arquivo enviado com sucesso!', 'success')
            return redirect(url_for('marketing.media_library'))
        else:
            flash('Tipo de arquivo não permitido', 'error')
    
    artists = Artist.query.filter_by(is_active=True).all()
    events = Event.query.filter(Event.start_datetime >= datetime.utcnow()).all()
    
    return render_template('marketing/upload_media.html', artists=artists, events=events)

# =============================================================================
# CALENDÁRIO DE POSTS
# =============================================================================

@bp.route('/posts')
@login_required
def social_posts():
    """Lista de posts para redes sociais"""
    status = request.args.get('status', 'all')
    platform = request.args.get('platform', 'all')
    
    query = SocialPost.query
    
    if status != 'all':
        query = query.filter_by(status=status)
    
    if platform != 'all':
        query = query.filter_by(platform=platform)
    
    posts = query.order_by(SocialPost.scheduled_datetime.desc()).all()
    
    platforms = ['instagram', 'facebook', 'twitter', 'youtube', 'tiktok']
    statuses = ['draft', 'scheduled', 'published', 'failed']
    
    return render_template('marketing/social_posts.html',
                         posts=posts,
                         platforms=platforms,
                         statuses=statuses,
                         current_status=status,
                         current_platform=platform)

@bp.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_social_post():
    """Criar novo post para redes sociais"""
    if request.method == 'POST':
        try:
            # Verificar campos obrigatórios
            title = request.form.get('title')
            content = request.form.get('content')
            platform = request.form.get('platform')
            scheduled_datetime_str = request.form.get('scheduled_datetime')
            artist_id = request.form.get('artist_id')
            
            if not all([title, content, platform, scheduled_datetime_str, artist_id]):
                missing = []
                if not title: missing.append("Título")
                if not content: missing.append("Conteúdo")
                if not platform: missing.append("Plataforma")
                if not scheduled_datetime_str: missing.append("Data e Hora")
                if not artist_id: missing.append("Artista")
                
                flash(f'Por favor, preencha os seguintes campos obrigatórios: {", ".join(missing)}', 'error')
                return redirect(url_for('marketing.new_social_post'))
            
            # Converter datetime
            try:
                scheduled_datetime = datetime.strptime(scheduled_datetime_str, '%Y-%m-%dT%H:%M')
            except ValueError as e:
                flash(f'Formato de data e hora inválido: {str(e)}. Use o formato YYYY-MM-DDThh:mm', 'error')
                return redirect(url_for('marketing.new_social_post'))
            
            # Criar post
            post = SocialPost(
                title=title,
                content=content,
                platform=platform,
                scheduled_datetime=scheduled_datetime,
                artist_id=artist_id,
                event_id=request.form.get('event_id') or None,
                media_file_id=request.form.get('media_file_id') or None,
                hashtags=request.form.get('hashtags', ''),
                location=request.form.get('location', ''),
                status=request.form.get('status', 'draft'),
                created_by=current_user.id
            )
            
            print(f"Tentando criar post: {title}, para artista: {artist_id}, em {scheduled_datetime}")
            db.session.add(post)
            db.session.commit()
            
            flash('Post criado com sucesso!', 'success')
            return redirect(url_for('marketing.social_posts'))
        except Exception as e:
            db.session.rollback()
            import traceback
            print(f"ERRO ao criar post: {str(e)}")
            traceback.print_exc()
            flash(f'Erro ao criar post: {str(e)}', 'error')
            return redirect(url_for('marketing.new_social_post'))
    
    artists = Artist.query.filter_by(is_active=True).all()
    events = Event.query.filter(Event.start_datetime >= datetime.utcnow()).all()
    media_files = MediaFile.query.filter_by(file_type='image').order_by(MediaFile.created_at.desc()).limit(20).all()
    
    # Passar a data atual para o template
    now = datetime.utcnow()
    from datetime import timedelta
    
    return render_template('marketing/new_post.html',
                         artists=artists,
                         events=events,
                         media_files=media_files,
                         now=now,
                         timedelta=timedelta)

@bp.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_social_post(post_id):
    """Editar post existente"""
    post = SocialPost.query.get_or_404(post_id)
    
    if request.method == 'POST':
        try:
            # Verificar campos obrigatórios
            title = request.form.get('title')
            content = request.form.get('content')
            platform = request.form.get('platform')
            artist_id = request.form.get('artist_id')
            
            if not all([title, content, platform, artist_id]):
                flash('Por favor, preencha todos os campos obrigatórios', 'error')
                return redirect(url_for('marketing.edit_social_post', post_id=post_id))
            
            post.title = title
            post.content = content
            post.platform = platform
            post.status = request.form.get('status')
            post.hashtags = request.form.get('hashtags', '')
            post.location = request.form.get('location', '')
            post.artist_id = artist_id
            post.event_id = request.form.get('event_id') or None
            post.media_file_id = request.form.get('media_file_id') or None
            
            # Atualizar métricas para posts publicados
            if post.status == 'published':
                post.likes = request.form.get('likes', post.likes)
                post.comments = request.form.get('comments', post.comments)
                post.shares = request.form.get('shares', post.shares)
                post.views = request.form.get('views', post.views)
            
            # Só atualiza a data agendada se estiver no formato correto
            scheduled_datetime = request.form.get('scheduled_datetime')
            if scheduled_datetime:
                try:
                    post.scheduled_datetime = datetime.strptime(scheduled_datetime, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Formato de data e hora inválido. A data não foi alterada.', 'warning')
            
            db.session.commit()
            
            flash('Post atualizado com sucesso!', 'success')
            return redirect(url_for('marketing.social_posts'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar post: {str(e)}', 'error')
            return redirect(url_for('marketing.edit_social_post', post_id=post_id))
    
    artists = Artist.query.filter_by(is_active=True).all()
    events = Event.query.filter(Event.start_datetime >= datetime.utcnow()).all()
    media_files = MediaFile.query.filter_by(file_type='image').order_by(MediaFile.created_at.desc()).limit(20).all()
    
    # Formatar a data para o formato do input datetime-local
    scheduled_datetime_str = post.scheduled_datetime.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('marketing/edit_post.html',
                         post=post,
                         artists=artists,
                         events=events,
                         media_files=media_files,
                         scheduled_datetime=scheduled_datetime_str)

@bp.route('/media/<int:media_id>/delete', methods=['POST'])
@login_required
def delete_media(media_id):
    """Excluir arquivo de mídia."""
    from app.delete_helpers import delete_media_file_record

    media = MediaFile.query.get_or_404(media_id)
    delete_media_file_record(media)
    db.session.commit()
    flash('Arquivo removido.', 'success')
    return redirect(url_for('marketing.media_library'))


@bp.route('/press-kit/<int:artist_id>/delete', methods=['POST'])
@login_required
def delete_press_kit(artist_id):
    """Excluir press kit do assessorado."""
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('marketing.press_kits'))

    kit = PressKit.query.filter_by(artist_id=artist_id).first()
    if kit:
        db.session.delete(kit)
        db.session.commit()
        flash('Press kit removido.', 'success')
    else:
        flash('Nenhum press kit para este assessorado.', 'info')
    return redirect(url_for('marketing.press_kits'))


@bp.route('/metrics/<int:metric_id>/delete', methods=['POST'])
@login_required
def delete_social_metrics(metric_id):
    """Excluir métricas de rede social."""
    metric = SocialMetrics.query.get_or_404(metric_id)
    db.session.delete(metric)
    db.session.commit()
    flash('Métricas removidas.', 'success')
    return redirect(url_for('marketing.social_metrics'))


@bp.route('/posts/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_social_post(post_id):
    """Excluir post"""
    post = SocialPost.query.get_or_404(post_id)
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post excluído com sucesso!', 'success')
    return redirect(url_for('marketing.social_posts'))

# =============================================================================
# PRESS KIT
# =============================================================================

@bp.route('/press-kit')
@login_required
def press_kits():
    """Lista de press kits"""
    press_kits = PressKit.query.join(Artist).filter(Artist.is_active == True).all()
    return render_template('marketing/press_kits.html', press_kits=press_kits)

@bp.route('/press-kit/<int:artist_id>')
def view_press_kit(artist_id):
    """Visualizar press kit público"""
    artist = Artist.query.get_or_404(artist_id)
    press_kit = PressKit.query.filter_by(artist_id=artist_id).first()
    
    if not press_kit or not press_kit.is_public:
        flash('Press kit não encontrado ou não público', 'error')
        return redirect(url_for('marketing.press_kits'))
    
    # Eventos recentes e próximos
    recent_events = Event.query.filter(
        Event.artist_id == artist_id,
        Event.start_datetime <= datetime.utcnow()
    ).order_by(Event.start_datetime.desc()).limit(5).all()
    
    upcoming_events = Event.query.filter(
        Event.artist_id == artist_id,
        Event.start_datetime >= datetime.utcnow()
    ).order_by(Event.start_datetime).limit(5).all()
    
    # Mídia do artista
    media_files = MediaFile.query.filter_by(
        artist_id=artist_id,
        is_public=True
    ).order_by(MediaFile.created_at.desc()).limit(12).all()
    
    return render_template('marketing/press_kit_public.html',
                         artist=artist,
                         press_kit=press_kit,
                         recent_events=recent_events,
                         upcoming_events=upcoming_events,
                         media_files=media_files)

@bp.route('/press-kit/<int:artist_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_press_kit(artist_id):
    """Editar press kit"""
    artist = Artist.query.get_or_404(artist_id)
    press_kit = PressKit.query.filter_by(artist_id=artist_id).first()
    
    if not press_kit:
        press_kit = PressKit(artist_id=artist_id)
        db.session.add(press_kit)
    
    if request.method == 'POST':
        press_kit.bio_short = request.form.get('bio_short', '')
        press_kit.bio_long = request.form.get('bio_long', '')
        press_kit.achievements = request.form.get('achievements', '')
        press_kit.website = request.form.get('website', '')
        press_kit.instagram = request.form.get('instagram', '')
        press_kit.facebook = request.form.get('facebook', '')
        press_kit.youtube = request.form.get('youtube', '')
        press_kit.spotify = request.form.get('spotify', '')
        press_kit.deezer = request.form.get('deezer', '')
        press_kit.apple_music = request.form.get('apple_music', '')
        press_kit.technical_rider = request.form.get('technical_rider', '')
        press_kit.stage_plot = request.form.get('stage_plot', '')
        press_kit.booking_contact = request.form.get('booking_contact', '')
        press_kit.booking_email = request.form.get('booking_email', '')
        press_kit.booking_phone = request.form.get('booking_phone', '')
        press_kit.is_public = bool(request.form.get('is_public'))
        press_kit.template_style = request.form.get('template_style', 'default')
        press_kit.profile_photo_id = request.form.get('profile_photo_id') or None
        press_kit.banner_photo_id = request.form.get('banner_photo_id') or None
        
        db.session.commit()
        
        flash('Press kit atualizado com sucesso!', 'success')
        return redirect(url_for('marketing.view_press_kit', artist_id=artist_id))
    
    # Fotos disponíveis
    photos = MediaFile.query.filter_by(
        artist_id=artist_id,
        file_type='image'
    ).order_by(MediaFile.created_at.desc()).all()
    
    return render_template('marketing/edit_press_kit.html',
                         artist=artist,
                         press_kit=press_kit,
                         photos=photos)

# =============================================================================
# MÉTRICAS E RELATÓRIOS
# =============================================================================

@bp.route('/metrics')
@login_required
def social_metrics():
    """Dashboard de métricas de redes sociais"""
    # Métricas por artista
    artists = Artist.query.filter_by(is_active=True).all()
    metrics_data = {}
    
    for artist in artists:
        metrics = SocialMetrics.query.filter_by(artist_id=artist.id).all()
        metrics_data[artist.id] = {
            'artist': artist,
            'platforms': {}
        }
        
        for metric in metrics:
            metrics_data[artist.id]['platforms'][metric.platform] = metric
    
    # Posts mais engajados
    top_posts = SocialPost.query.filter_by(status='published').order_by(
        (SocialPost.likes + SocialPost.comments + SocialPost.shares).desc()
    ).limit(10).all()
    
    return render_template('marketing/metrics.html',
                         metrics_data=metrics_data,
                         top_posts=top_posts)

@bp.route('/metrics/add', methods=['POST'])
@login_required
def add_social_metrics():
    """Adicionar novas métricas de redes sociais"""
    artist_id = request.form.get('artist_id')
    platform = request.form.get('platform')
    
    # Verificar se já existe métrica para este artista/plataforma
    existing = SocialMetrics.query.filter_by(
        artist_id=artist_id,
        platform=platform
    ).first()
    
    if existing:
        flash('Já existem métricas para este artista nesta plataforma. Por favor, atualize as existentes.', 'warning')
        return redirect(url_for('marketing.social_metrics'))
    
    # Criar nova métrica
    try:
        period_start = datetime.strptime(request.form.get('period_start'), '%Y-%m-%d').date()
        period_end = datetime.strptime(request.form.get('period_end'), '%Y-%m-%d').date()
        
        new_metric = SocialMetrics(
            artist_id=artist_id,
            platform=platform,
            followers_count=request.form.get('followers_count', 0),
            following_count=request.form.get('following_count', 0),
            posts_count=request.form.get('posts_count', 0),
            period_start=period_start,
            period_end=period_end,
            total_likes=request.form.get('total_likes', 0),
            total_comments=request.form.get('total_comments', 0),
            total_shares=request.form.get('total_shares', 0),
            followers_growth=request.form.get('followers_growth', 0),
            engagement_rate=0.0  # Calcular abaixo
        )
        
        # Calcular taxa de engajamento
        if int(new_metric.followers_count) > 0:
            total_engagement = int(new_metric.total_likes) + int(new_metric.total_comments) + int(new_metric.total_shares)
            new_metric.engagement_rate = (total_engagement / float(new_metric.followers_count)) * 100
        
        db.session.add(new_metric)
        db.session.commit()
        
        flash('Métricas adicionadas com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao adicionar métricas: {str(e)}', 'error')
    
    return redirect(url_for('marketing.social_metrics'))

@bp.route('/metrics/update/<int:metric_id>', methods=['POST'])
@login_required
def update_social_metrics(metric_id):
    """Atualizar métricas existentes"""
    metric = SocialMetrics.query.get_or_404(metric_id)
    
    try:
        period_start = datetime.strptime(request.form.get('period_start'), '%Y-%m-%d').date()
        period_end = datetime.strptime(request.form.get('period_end'), '%Y-%m-%d').date()
        
        metric.followers_count = request.form.get('followers_count', 0)
        metric.posts_count = request.form.get('posts_count', 0)
        metric.period_start = period_start
        metric.period_end = period_end
        metric.total_likes = request.form.get('total_likes', 0)
        metric.total_comments = request.form.get('total_comments', 0)
        metric.total_shares = request.form.get('total_shares', 0)
        metric.followers_growth = request.form.get('followers_growth', 0)
        metric.collected_at = datetime.utcnow()
        
        # Calcular taxa de engajamento
        if int(metric.followers_count) > 0:
            total_engagement = int(metric.total_likes) + int(metric.total_comments) + int(metric.total_shares)
            metric.engagement_rate = (total_engagement / float(metric.followers_count)) * 100
        
        db.session.commit()
        flash('Métricas atualizadas com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar métricas: {str(e)}', 'error')
    
    return redirect(url_for('marketing.social_metrics'))

# =============================================================================
# API ENDPOINTS
# =============================================================================

@bp.route('/api/calendar-posts')
@login_required
def api_calendar_posts():
    """API para feed do calendário de posts"""
    start = request.args.get('start')
    end = request.args.get('end')
    
    query = SocialPost.query
    
    if start:
        query = query.filter(SocialPost.scheduled_datetime >= datetime.fromisoformat(start))
    if end:
        query = query.filter(SocialPost.scheduled_datetime <= datetime.fromisoformat(end))
    
    posts = query.all()
    
    events = []
    for post in posts:
        color = {
            'draft': '#6c757d',
            'scheduled': '#007bff',
            'published': '#28a745',
            'failed': '#dc3545'
        }.get(post.status, '#6c757d')
        
        events.append({
            'id': post.id,
            'title': f'[{post.platform.upper()}] {post.title}',
            'start': post.scheduled_datetime.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'status': post.status,
                'platform': post.platform,
                'artist': post.artist.stage_name
            }
        })
    
    return jsonify(events)
