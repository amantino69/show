from flask import render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import os

from app.main import bp
from app.models import Event, Artist, EventType, ArtistType, User
from app import db
from config import Config

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    # Eventos próximos (próximos 7 dias)
    next_week = datetime.now() + timedelta(days=7)
    
    if current_user.is_manager:
        # Empresário vê todos os eventos
        upcoming_events = Event.query.filter(
            Event.start_datetime.between(datetime.now(), next_week)
        ).order_by(Event.start_datetime).limit(10).all()
        
        total_artists = Artist.query.filter_by(is_active=True).count()
        total_events = Event.query.filter(Event.start_datetime >= datetime.now()).count()
        
        # Estatísticas por tipo de artista
        artist_types = ArtistType.query.all()
        type_stats = {}
        for artist_type in artist_types:
            count = Artist.query.filter_by(artist_type_id=artist_type.id, is_active=True).count()
            type_stats[artist_type.id] = count
        
    else:
        # Artista vê apenas seus eventos
        upcoming_events = Event.query.filter(
            Event.artist_id == current_user.artist_id,
            Event.start_datetime.between(datetime.now(), next_week)
        ).order_by(Event.start_datetime).limit(10).all()
        
        total_artists = 1  # Só ele mesmo
        total_events = Event.query.filter(
            Event.artist_id == current_user.artist_id,
            Event.start_datetime >= datetime.now()
        ).count()
        
        artist_types = []
        type_stats = {}
    
    # Eventos de hoje
    today = datetime.now().date()
    today_events = [e for e in upcoming_events if e.start_datetime.date() == today]
    
    return render_template('main/dashboard.html',
                         upcoming_events=upcoming_events,
                         today_events=today_events,
                         total_artists=total_artists,
                         total_events=total_events,
                         artist_types=artist_types,
                         type_stats=type_stats)
    
    # Eventos de hoje
    today = datetime.now().date()
    today_events = [e for e in upcoming_events if e.start_datetime.date() == today]
    
    return render_template('main/dashboard.html',
                         upcoming_events=upcoming_events,
                         today_events=today_events,
                         total_artists=total_artists,
                         total_events=total_events,
                         artist_types=artist_types,
                         type_stats=type_stats)

@bp.route('/artists')
@login_required
def artists():
    if not current_user.is_manager:
        flash('Acesso negado. Apenas empresários podem visualizar esta página.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Buscar artistas com seus tipos
    artists = Artist.query.filter_by(is_active=True).all()
    artist_types = ArtistType.query.all()
    
    # Estatísticas por tipo
    type_stats = {}
    for artist_type in artist_types:
        count = Artist.query.filter_by(artist_type_id=artist_type.id, is_active=True).count()
        type_stats[artist_type.id] = count
    
    return render_template('main/artists.html', 
                         artists=artists, 
                         artist_types=artist_types,
                         type_stats=type_stats)

@bp.route('/artists/new', methods=['GET', 'POST'])
@login_required
def new_artist():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        stage_name = request.form.get('stage_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        artist_type_id = request.form.get('artist_type_id')
        genre = request.form.get('genre')
        description = request.form.get('description')
        
        # Validar tipo de artista
        if not artist_type_id:
            flash('Por favor, selecione um tipo de artista.', 'error')
            artist_types = ArtistType.query.all()
            return render_template('main/new_artist.html', artist_types=artist_types)
        
        # Selecionar cor automaticamente
        artist_count = Artist.query.count()
        color = Config.ARTIST_COLORS[artist_count % len(Config.ARTIST_COLORS)]
        
        artist = Artist(
            name=name,
            stage_name=stage_name,
            email=email,
            phone=phone,
            artist_type_id=artist_type_id,
            genre=genre,
            description=description,
            color=color
        )
        
        db.session.add(artist)
        db.session.flush()  # Para obter o ID do artista
        
        # Criar conta de usuário para o artista
        username = stage_name.lower().replace(' ', '_') if stage_name else name.lower().replace(' ', '_')
        # Verificar se username já existe e adicionar número se necessário
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        # Senha padrão: nome do artista sem espaços + 123
        default_password = (stage_name or name).lower().replace(' ', '') + '123'
        
        user = User(
            username=username,
            email=email,
            is_manager=False,
            artist_id=artist.id
        )
        user.set_password(default_password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Artista cadastrado com sucesso! Credenciais: {username} / {default_password}', 'success')
        return redirect(url_for('main.artists'))
    
    artist_types = ArtistType.query.all()
    return render_template('main/new_artist.html', artist_types=artist_types)

@bp.route('/artists/<int:artist_id>')
@login_required
def artist_detail(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    
    # Verificar permissões: empresário vê todos, artista só vê o próprio
    if not current_user.is_manager and current_user.artist_id != artist_id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Buscar eventos do artista
    events = Event.query.filter_by(artist_id=artist_id).order_by(Event.start_datetime.desc()).all()
    
    return render_template('main/artist_detail.html', artist=artist, events=events)

# Adicionar rota para exclusão de artista
@bp.route('/artists/<int:artist_id>/delete', methods=['POST'])
@login_required
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    if not current_user.is_manager:
        flash('Apenas empresários podem excluir artistas.', 'error')
        return redirect(url_for('main.artist_detail', artist_id=artist_id))
    # Excluir eventos e notificações relacionados
    from app.models import Event, Notification
    events = Event.query.filter_by(artist_id=artist.id).all()
    for event in events:
        Notification.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)
    db.session.delete(artist)
    db.session.commit()
    flash('Artista excluído com sucesso!', 'success')
    return redirect(url_for('main.artists'))

# Adicionar rotas para backup/restore
@bp.route('/backup', methods=['GET'])
@login_required
def backup_db():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/artistas_sistema.db')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'artistas_sistema_backup_{timestamp}.db'
    backup_path = os.path.join(os.path.dirname(__file__), f'../../backup_restore/backups/{backup_name}')
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    import shutil
    shutil.copy2(db_path, backup_path)
    flash(f'Backup realizado: {backup_name}', 'success')
    return send_file(backup_path, as_attachment=True)

@bp.route('/restore', methods=['POST'])
@login_required
def restore_db():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    backup_file = request.form.get('backup_file')
    backup_path = os.path.join(os.path.dirname(__file__), f'../../backup_restore/backups/{backup_file}')
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/artistas_sistema.db')
    import shutil
    if not os.path.exists(backup_path):
        flash('Arquivo de backup não encontrado!', 'error')
        return redirect(url_for('main.backup_restore'))
    shutil.copy2(backup_path, db_path)
    flash('Banco restaurado com sucesso!', 'success')
    return redirect(url_for('main.backup_restore'))

@bp.route('/backup_restore', methods=['GET'])
@login_required
def backup_restore():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    backup_dir = os.path.join(os.path.dirname(__file__), '../../backup_restore/backups')
    backups = []
    if os.path.exists(backup_dir):
        backups = sorted(os.listdir(backup_dir), reverse=True)
    return render_template('main/backup_restore.html', backups=backups)
        artist_types = ArtistType.query.all()
        type_stats = {}
        for artist_type in artist_types:
            count = Artist.query.filter_by(artist_type_id=artist_type.id, is_active=True).count()
            type_stats[artist_type.id] = count
        
    else:
        # Artista vê apenas seus eventos
        upcoming_events = Event.query.filter(
            Event.artist_id == current_user.artist_id,
            Event.start_datetime.between(datetime.now(), next_week)
        ).order_by(Event.start_datetime).limit(10).all()
        
        total_artists = 1  # Só ele mesmo
        total_events = Event.query.filter(
            Event.artist_id == current_user.artist_id,
            Event.start_datetime >= datetime.now()
        ).count()
        
        artist_types = []
        type_stats = {}
    
    # Eventos de hoje
    today = datetime.now().date()
    today_events = [e for e in upcoming_events if e.start_datetime.date() == today]
    
    return render_template('main/dashboard.html',
                         upcoming_events=upcoming_events,
                         today_events=today_events,
                         total_artists=total_artists,
                         total_events=total_events,
                         artist_types=artist_types,
                         type_stats=type_stats)

@bp.route('/artists')
@login_required
def artists():
    if not current_user.is_manager:
        flash('Acesso negado. Apenas empresários podem visualizar esta página.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Buscar artistas com seus tipos
    artists = Artist.query.filter_by(is_active=True).all()
    artist_types = ArtistType.query.all()
    
    # Estatísticas por tipo
    type_stats = {}
    for artist_type in artist_types:
        count = Artist.query.filter_by(artist_type_id=artist_type.id, is_active=True).count()
        type_stats[artist_type.id] = count
    
    return render_template('main/artists.html', 
                         artists=artists, 
                         artist_types=artist_types,
                         type_stats=type_stats)

@bp.route('/artists/new', methods=['GET', 'POST'])
@login_required
def new_artist():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        stage_name = request.form.get('stage_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        artist_type_id = request.form.get('artist_type_id')
        genre = request.form.get('genre')
        description = request.form.get('description')
        
        # Validar tipo de artista
        if not artist_type_id:
            flash('Por favor, selecione um tipo de artista.', 'error')
            artist_types = ArtistType.query.all()
            return render_template('main/new_artist.html', artist_types=artist_types)
        
        # Selecionar cor automaticamente
        artist_count = Artist.query.count()
        color = Config.ARTIST_COLORS[artist_count % len(Config.ARTIST_COLORS)]
        
        artist = Artist(
            name=name,
            stage_name=stage_name,
            email=email,
            phone=phone,
            artist_type_id=artist_type_id,
            genre=genre,
            description=description,
            color=color
        )
        
        db.session.add(artist)
        db.session.commit()
        
        flash(f'Artista {stage_name} cadastrado com sucesso!', 'success')
        return redirect(url_for('main.artists'))
    
    # GET request - mostrar formulário
    artist_types = ArtistType.query.all()
    return render_template('main/new_artist.html', artist_types=artist_types)

@bp.route('/artists/<int:artist_id>')
@login_required
def artist_detail(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    
    # Verificar permissão
    if not current_user.is_manager and current_user.artist_id != artist_id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Eventos do artista
    events = Event.query.filter_by(artist_id=artist_id).order_by(Event.start_datetime.desc()).all()
    
    # Estatísticas
    total_events = len(events)
    completed_events = len([e for e in events if e.status == 'concluido'])
    upcoming_events = len([e for e in events if e.start_datetime > datetime.now()])
    
    return render_template('main/artist_detail.html',
                         artist=artist,
                         events=events,
                         total_events=total_events,
                         completed_events=completed_events,
                         upcoming_events=upcoming_events)

@bp.route('/artists/<int:artist_id>/delete', methods=['POST'])
@login_required
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    if not current_user.is_manager:
        flash('Apenas empresários podem excluir artistas.', 'error')
        return redirect(url_for('main.artist_detail', artist_id=artist_id))
    # Excluir eventos e notificações relacionados
    from app.models import Event, Notification
    events = Event.query.filter_by(artist_id=artist.id).all()
    for event in events:
        Notification.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)
    db.session.delete(artist)
    db.session.commit()
    flash('Artista excluído com sucesso!', 'success')
    return redirect(url_for('main.artists'))

@bp.route('/backup', methods=['GET'])
@login_required
def backup_db():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/artistas_sistema.db')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'artistas_sistema_backup_{timestamp}.db'
    backup_path = os.path.join(os.path.dirname(__file__), f'../../backup_restore/backups/{backup_name}')
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(db_path, backup_path)
    flash(f'Backup realizado: {backup_name}', 'success')
    return send_file(backup_path, as_attachment=True)

@bp.route('/restore', methods=['POST'])
@login_required
def restore_db():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    backup_file = request.form.get('backup_file')
    backup_path = os.path.join(os.path.dirname(__file__), f'../../backup_restore/backups/{backup_file}')
    db_path = os.path.join(os.path.dirname(__file__), '../../instance/artistas_sistema.db')
    if not os.path.exists(backup_path):
        flash('Arquivo de backup não encontrado!', 'error')
        return redirect(url_for('main.backup_restore'))
    shutil.copy2(backup_path, db_path)
    flash('Banco restaurado com sucesso!', 'success')
    return redirect(url_for('main.backup_restore'))

@bp.route('/backup_restore', methods=['GET'])
@login_required
def backup_restore():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    backup_dir = os.path.join(os.path.dirname(__file__), '../../backup_restore/backups')
    backups = []
    if os.path.exists(backup_dir):
        backups = sorted(os.listdir(backup_dir), reverse=True)
    return render_template('main/backup_restore.html', backups=backups)
