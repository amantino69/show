from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.events import bp
from app.models import Event, Artist, EventType, Notification
from app import db
from app.google_calendar import create_google_event, update_google_event, delete_google_event
from app.notifications import schedule_event_notifications

@bp.route('/')
@login_required
def events():
    if current_user.is_manager:
        events = Event.query.join(Artist).order_by(Event.start_datetime.desc()).all()
    else:
        events = Event.query.filter_by(artist_id=current_user.artist_id).order_by(Event.start_datetime.desc()).all()
    
    return render_template('events/events.html', events=events)

@bp.route('/calendar')
@login_required
def calendar():
    return render_template('events/calendar.html')

@bp.route('/api/events')
@login_required
def api_events():
    if current_user.is_manager:
        events = Event.query.join(Artist).all()
    else:
        events = Event.query.filter_by(artist_id=current_user.artist_id).all()
    
    event_list = []
    for event in events:
        event_list.append({
            'id': event.id,
            'title': f"{event.title} - {event.artist.stage_name}",
            'start': event.start_datetime.isoformat(),
            'end': event.end_datetime.isoformat(),
            'backgroundColor': event.artist.color,
            'borderColor': event.artist.color,
            'textColor': '#ffffff',
            'extendedProps': {
                'description': event.description,
                'location': event.location,
                'status': event.status,
                'artist': event.artist.stage_name,
                'type': event.event_type.name if event.event_type else ''
            }
        })
    
    return jsonify(event_list)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_event():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_datetime = datetime.fromisoformat(request.form.get('start_datetime'))
        end_datetime = datetime.fromisoformat(request.form.get('end_datetime'))
        location = request.form.get('location')
        artist_id = request.form.get('artist_id')
        event_type_id = request.form.get('event_type_id')
        priority = request.form.get('priority', 'medium')
        
        # Verificar permissão
        if not current_user.is_manager and int(artist_id) != current_user.artist_id:
            flash('Você só pode criar eventos para si mesmo.', 'error')
            return redirect(url_for('events.events'))
        
        event = Event(
            title=title,
            description=description,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            artist_id=artist_id,
            event_type_id=event_type_id,
            priority=priority
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Criar evento no Google Calendar
        try:
            from dev_config import ENABLE_GOOGLE_CALENDAR
            if ENABLE_GOOGLE_CALENDAR:
                google_event_id = create_google_event(event)
                if google_event_id:
                    event.google_event_id = google_event_id
                    db.session.commit()
                    
                    # Contar quantos eventos foram criados
                    event_count = len(google_event_id.split(','))
                    if event_count > 1:
                        flash(f'🎉 Evento sincronizado com Google Calendar! Criado na agenda do empresário e do artista ({event_count} agendas)', 'success')
                    else:
                        flash('🎉 Evento sincronizado com Google Calendar! Criado na agenda do empresário', 'success')
                else:
                    flash('Evento criado no sistema, mas não foi possível sincronizar com Google Calendar', 'warning')
            else:
                flash('Evento criado! (Google Calendar desabilitado no modo desenvolvimento)', 'info')
        except Exception as e:
            flash(f'Evento criado, mas erro no Google Calendar: {str(e)}', 'warning')
        
        # Agendar notificações
        schedule_event_notifications(event)
        
        # Criar alertas nativos automáticos
        try:
            from app.alert_system import native_alert_system
            created_alerts = native_alert_system.create_automatic_alerts_for_event(event.id)
            if created_alerts:
                flash('🔔 Alertas nativos criados automaticamente!', 'info')
        except Exception as e:
            print(f"Erro ao criar alertas automáticos: {e}")
        
        flash('Evento criado com sucesso!', 'success')
        return redirect(url_for('events.events'))
    
    # GET request
    if current_user.is_manager:
        artists = Artist.query.filter_by(is_active=True).all()
    else:
        artists = [current_user.artist] if current_user.artist else []
    
    event_types = EventType.query.all()
    
    return render_template('events/new_event.html', artists=artists, event_types=event_types)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Verificar permissão
    if not current_user.is_manager and event.artist_id != current_user.artist_id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('events.events'))
    
    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.start_datetime = datetime.fromisoformat(request.form.get('start_datetime'))
        event.end_datetime = datetime.fromisoformat(request.form.get('end_datetime'))
        event.location = request.form.get('location')
        event.status = request.form.get('status')
        event.priority = request.form.get('priority')
        event.notes = request.form.get('notes')
        
        # Atualizar artist_id apenas se o usuário for manager
        if current_user.is_manager:
            artist_id = request.form.get('artist_id')
            if artist_id:
                event.artist_id = int(artist_id)
        
        # Atualizar event_type_id
        event_type_id = request.form.get('event_type_id')
        if event_type_id:
            event.event_type_id = int(event_type_id)
        
        # Atualizar campos de avaliação se o evento estiver concluído
        if event.status == 'concluido':
            success_rating = request.form.get('success_rating')
            if success_rating:
                event.success_rating = int(success_rating)
            event.result_notes = request.form.get('result_notes')
        
        event.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Atualizar evento no Google Calendar
        try:
            if event.google_event_id:
                update_google_event(event)
        except Exception as e:
            flash(f'Erro ao atualizar evento no Google Calendar: {str(e)}', 'warning')
        
        flash('Evento atualizado com sucesso!', 'success')
        return redirect(url_for('events.events'))
    
    if current_user.is_manager:
        artists = Artist.query.filter_by(is_active=True).all()
    else:
        artists = [current_user.artist] if current_user.artist else []
    
    event_types = EventType.query.all()
    
    return render_template('events/edit_event.html', event=event, artists=artists, event_types=event_types)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Verificar permissão
    if not current_user.is_manager and event.artist_id != current_user.artist_id:
        flash('Acesso negado.', 'error')
        return redirect(url_for('events.events'))
    
    # Deletar do Google Calendar
    try:
        if event.google_event_id:
            delete_google_event(event.google_event_id)
    except Exception as e:
        flash(f'Erro ao deletar evento do Google Calendar: {str(e)}', 'warning')
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Evento deletado com sucesso!', 'success')
    return redirect(url_for('events.events'))
