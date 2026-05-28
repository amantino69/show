from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.main import bp
from app.models import User, Artist, Event, EventType
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
    
    # Eventos de hoje
    today = datetime.now().date()
    today_events = [e for e in upcoming_events if e.start_datetime.date() == today]
    
    return render_template('main/dashboard.html',
                         upcoming_events=upcoming_events,
                         today_events=today_events,
                         total_artists=total_artists,
                         total_events=total_events)

@bp.route('/artists')
@login_required
def artists():
    if not current_user.is_manager:
        flash('Acesso negado. Apenas empresários podem visualizar esta página.', 'error')
        return redirect(url_for('main.dashboard'))
    
    artists = Artist.query.filter_by(is_active=True).all()
    return render_template('main/artists.html', artists=artists)

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
        genre = request.form.get('genre')
        description = request.form.get('description')
        
        # Selecionar cor automaticamente
        artist_count = Artist.query.count()
        color = Config.ARTIST_COLORS[artist_count % len(Config.ARTIST_COLORS)]
        
        artist = Artist(
            name=name,
            stage_name=stage_name,
            email=email,
            phone=phone,
            genre=genre,
            description=description,
            color=color
        )
        
        db.session.add(artist)
        db.session.commit()
        
        flash(f'Artista {stage_name} cadastrado com sucesso!', 'success')
        return redirect(url_for('main.artists'))
    
    return render_template('main/new_artist.html')

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
