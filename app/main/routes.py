from flask import render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
import os

from app.main import bp
from app.models import Event, Artist, EventType, ArtistType, User, Lead, BrandDeal, OnboardingTask
from app.onboarding_service import (
    ONBOARDING_PROFILE_SECTIONS,
    recalculate_onboarding_progress,
    apply_template_to_artist,
    save_profile_from_form,
)
from app import db
from app.delete_helpers import delete_artist_completely
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
        
        total_artists = Artist.query.filter_by(is_active=True, client_status='ativo').count()
        total_events = Event.query.filter(Event.start_datetime >= datetime.now()).count()

        # KPIs painel operacional (planilha Viezes)
        ops_active_clients = total_artists
        ops_open_proposals = BrandDeal.query.filter(
            BrandDeal.status.in_(['prospeccao', 'proposta', 'negociacao'])
        ).count()
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ops_month_closures = BrandDeal.query.filter(
            BrandDeal.status == 'fechado',
            BrandDeal.closed_at >= month_start,
        ).count()
        today = date.today()
        ops_pending_followups = Lead.query.filter(
            Lead.follow_up_date <= today,
            Lead.closed.is_(False),
            Lead.status != 'perdido',
        ).count() + BrandDeal.query.filter(
            BrandDeal.follow_up_date <= today,
            BrandDeal.status.in_(['prospeccao', 'proposta', 'negociacao']),
        ).count()
        
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
        ops_active_clients = 0
        ops_open_proposals = 0
        ops_month_closures = 0
        ops_pending_followups = 0
    
    # Eventos de hoje
    today = datetime.now().date()
    today_events = [e for e in upcoming_events if e.start_datetime.date() == today]
    
    return render_template('main/dashboard.html',
                         upcoming_events=upcoming_events,
                         today_events=today_events,
                         total_artists=total_artists,
                         total_events=total_events,
                         artist_types=artist_types,
                         type_stats=type_stats,
                         ops_active_clients=ops_active_clients,
                         ops_open_proposals=ops_open_proposals,
                         ops_month_closures=ops_month_closures,
                         ops_pending_followups=ops_pending_followups)

@bp.route('/artists')
@login_required
def artists():
    if not current_user.is_manager:
        flash('Acesso negado. Apenas empresários podem visualizar esta página.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Buscar artistas com seus tipos
    status_filter = request.args.get('status', '')
    query = Artist.query.filter_by(is_active=True)
    if status_filter:
        query = query.filter_by(client_status=status_filter)
    artists = query.order_by(Artist.stage_name).all()
    artist_types = ArtistType.query.all()
    
    # Estatísticas por tipo
    type_stats = {}
    for artist_type in artist_types:
        count = Artist.query.filter_by(artist_type_id=artist_type.id, is_active=True).count()
        type_stats[artist_type.id] = count
    
    return render_template('main/artists.html',
                         artists=artists,
                         status_filter=status_filter,
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
    
    onboarding_tasks = []
    if current_user.is_manager:
        onboarding_tasks = OnboardingTask.query.filter_by(artist_id=artist_id).order_by(
            OnboardingTask.sort_order
        ).all()

    return render_template(
        'main/artist_detail.html',
        artist=artist,
        events=events,
        onboarding_tasks=onboarding_tasks,
    )


@bp.route('/artists/<int:artist_id>/onboarding', methods=['GET', 'POST'])
@login_required
def artist_onboarding(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    if not current_user.is_manager and current_user.artist_id != artist_id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    can_edit = current_user.is_manager

    if request.method == 'POST' and request.form.get('form_type') == 'profile':
        save_profile_from_form(artist, request.form)
        db.session.commit()
        flash('Ficha de onboarding salva.', 'success')
        return redirect(url_for('main.artist_onboarding', artist_id=artist_id))

    tasks = OnboardingTask.query.filter_by(artist_id=artist_id).order_by(
        OnboardingTask.sort_order
    ).all()
    done = sum(1 for t in tasks if t.status == 'concluido')
    total = len(tasks) or 1
    recalculate_onboarding_progress(artist_id)
    db.session.commit()

    modules = {}
    for t in tasks:
        mod = t.module or 'Geral'
        modules.setdefault(mod, []).append(t)

    profile = artist.get_onboarding_data()
    return render_template(
        'main/artist_onboarding.html',
        artist=artist,
        tasks=tasks,
        modules=modules,
        done=done,
        total=total,
        profile=profile,
        sections=ONBOARDING_PROFILE_SECTIONS,
        statuses=OnboardingTask.STATUS_LABELS,
        can_edit=can_edit,
    )


@bp.route('/artists/<int:artist_id>/onboarding/apply-template', methods=['POST'])
@login_required
def onboarding_apply_template(artist_id):
    if not current_user.is_manager:
        return redirect(url_for('main.dashboard'))
    replace = request.form.get('replace') == '1'
    added = apply_template_to_artist(artist_id, replace=replace)
    db.session.commit()
    flash(f'Template aplicado: {added} tarefa(s) adicionada(s).', 'success')
    return redirect(url_for('main.artist_onboarding', artist_id=artist_id))


@bp.route('/artists/<int:artist_id>/onboarding/tasks', methods=['POST'])
@login_required
def onboarding_task_create(artist_id):
    if not current_user.is_manager:
        return redirect(url_for('main.dashboard'))
    title = request.form.get('title', '').strip()
    if not title:
        flash('Informe o título da tarefa.', 'error')
        return redirect(url_for('main.artist_onboarding', artist_id=artist_id))
    max_order = db.session.query(db.func.max(OnboardingTask.sort_order)).filter_by(
        artist_id=artist_id
    ).scalar() or 0
    task = OnboardingTask(
        artist_id=artist_id,
        module=request.form.get('module', '').strip() or None,
        title=title,
        responsible=request.form.get('responsible', '').strip() or None,
        status=request.form.get('status', 'pendente'),
        sort_order=max_order + 1,
    )
    db.session.add(task)
    recalculate_onboarding_progress(artist_id)
    db.session.commit()
    flash('Tarefa adicionada.', 'success')
    return redirect(url_for('main.artist_onboarding', artist_id=artist_id))


@bp.route('/artists/<int:artist_id>/onboarding/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def onboarding_task_update(artist_id, task_id):
    if not current_user.is_manager:
        return redirect(url_for('main.dashboard'))
    task = OnboardingTask.query.filter_by(id=task_id, artist_id=artist_id).first_or_404()
    new_status = request.form.get('status')
    if new_status in OnboardingTask.STATUS_LABELS:
        task.status = new_status
        if new_status == 'concluido':
            task.completed_at = datetime.utcnow().date()
        else:
            task.completed_at = None
    if 'title' in request.form:
        task.title = request.form.get('title', task.title).strip()
    if 'responsible' in request.form:
        task.responsible = request.form.get('responsible', '').strip() or None
    if 'notes' in request.form:
        task.notes = request.form.get('notes', '').strip() or None
    recalculate_onboarding_progress(artist_id)
    db.session.commit()
    flash('Tarefa atualizada.', 'success')
    return redirect(url_for('main.artist_onboarding', artist_id=artist_id))


@bp.route('/artists/<int:artist_id>/onboarding/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def onboarding_task_toggle(artist_id, task_id):
    if not current_user.is_manager:
        return redirect(url_for('main.dashboard'))
    task = OnboardingTask.query.filter_by(id=task_id, artist_id=artist_id).first_or_404()
    if task.status == 'concluido':
        task.status = 'pendente'
        task.completed_at = None
    else:
        task.status = 'concluido'
        task.completed_at = datetime.utcnow().date()
    recalculate_onboarding_progress(artist_id)
    db.session.commit()
    return redirect(url_for('main.artist_onboarding', artist_id=artist_id))


@bp.route('/artists/<int:artist_id>/onboarding/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def onboarding_task_delete(artist_id, task_id):
    if not current_user.is_manager:
        return redirect(url_for('main.dashboard'))
    task = OnboardingTask.query.filter_by(id=task_id, artist_id=artist_id).first_or_404()
    db.session.delete(task)
    recalculate_onboarding_progress(artist_id)
    db.session.commit()
    flash('Tarefa removida.', 'success')
    return redirect(url_for('main.artist_onboarding', artist_id=artist_id))

@bp.route('/artists/<int:artist_id>/delete', methods=['POST'])
@login_required
def delete_artist(artist_id):
    artist = Artist.query.get_or_404(artist_id)
    if not current_user.is_manager:
        flash('Apenas empresários podem excluir artistas.', 'error')
        return redirect(url_for('main.artist_detail', artist_id=artist_id))

    name = artist.stage_name
    delete_artist_completely(artist)
    db.session.commit()
    flash(f'Assessorado "{name}" e dados vinculados foram excluídos.', 'success')
    return redirect(url_for('main.artists'))

@bp.route('/backup', methods=['GET'])
@login_required
def backup_db():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    from app.backup_service import create_backup

    try:
        info = create_backup(prefix='manual')
    except FileNotFoundError as exc:
        flash(str(exc), 'error')
        return redirect(url_for('main.backup_restore'))

    flash(f'Backup realizado: {info["name"]}', 'success')
    return send_file(info['path'], as_attachment=True, download_name=info['name'])


@bp.route('/backup/download/<path:filename>')
@login_required
def download_backup(filename):
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    from app.backup_service import get_backup_dir

    safe_name = os.path.basename(filename)
    backup_path = os.path.join(get_backup_dir(), safe_name)
    if not os.path.isfile(backup_path):
        flash('Backup não encontrado.', 'error')
        return redirect(url_for('main.backup_restore'))

    return send_file(backup_path, as_attachment=True, download_name=safe_name)


@bp.route('/restore', methods=['POST'])
@login_required
def restore_db():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    from app.backup_service import get_backup_dir, get_db_path, create_backup

    backup_file = os.path.basename(request.form.get('backup_file', ''))
    backup_path = os.path.join(get_backup_dir(), backup_file)
    db_path = get_db_path()

    import shutil
    if not backup_file or not os.path.exists(backup_path):
        flash('Arquivo de backup não encontrado!', 'error')
        return redirect(url_for('main.backup_restore'))
    
    try:
        create_backup(prefix='antes_restore')
    except (FileNotFoundError, OSError):
        pass

    shutil.copy2(backup_path, db_path)
    flash('Banco restaurado com sucesso!', 'success')
    return redirect(url_for('main.backup_restore'))

@bp.route('/backup_restore', methods=['GET'])
@login_required
def backup_restore():
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))

    from app.backup_service import list_backups

    return render_template('main/backup_restore.html', backup_files=list_backups())

@bp.route('/artists/<int:artist_id>/credentials')
@login_required
def artist_credentials(artist_id):
    if not current_user.is_manager:
        flash('Acesso negado.', 'error')
        return redirect(url_for('main.dashboard'))
    
    artist = Artist.query.get_or_404(artist_id)
    user = User.query.filter_by(artist_id=artist_id).first()
    
    if not user:
        flash('Este artista ainda não possui credenciais de acesso.', 'warning')
        return redirect(url_for('main.artist_detail', artist_id=artist_id))
    
    # Para segurança, não retornamos a senha real - apenas confirmamos que existe
    credentials = {
        'username': user.username,
        'email': user.email,
        'has_password': True,
        'created_at': user.created_at if hasattr(user, 'created_at') else None
    }
    
    return render_template('main/artist_credentials.html', artist=artist, credentials=credentials)