"""
Rotas para sistema de alertas nativos
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import Event, Notification, db
from app.alert_system import native_alert_system

alerts_bp = Blueprint('alerts', __name__, url_prefix='/alerts')

@alerts_bp.route('/')
@login_required
def index():
    """Página principal de alertas"""
    # Buscar próximos alertas
    upcoming_alerts = native_alert_system.get_upcoming_alerts(days=14)
    
    # Buscar notificações do banco
    notifications = Notification.query.filter_by(sent=False).order_by(Notification.scheduled_time).limit(10).all()
    
    return render_template('alerts/index.html', 
                         upcoming_alerts=upcoming_alerts,
                         notifications=notifications)

@alerts_bp.route('/create/<int:event_id>')
@login_required
def create_alert_form(event_id):
    """Formulário para criar alerta personalizado"""
    event = Event.query.get_or_404(event_id)
    return render_template('alerts/create.html', event=event)

@alerts_bp.route('/create', methods=['POST'])
@login_required
def create_alert():
    """Criar novo alerta"""
    try:
        event_id = int(request.form.get('event_id'))
        alert_datetime = datetime.strptime(
            request.form.get('alert_datetime'), 
            '%Y-%m-%dT%H:%M'
        )
        alert_type = request.form.get('alert_type', 'reminder')
        
        success = native_alert_system.create_native_alert(
            event_id=event_id,
            alert_time=alert_datetime,
            alert_type=alert_type
        )
        
        if success:
            flash('Alerta criado com sucesso!', 'success')
        else:
            flash('Erro ao criar alerta.', 'error')
            
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('alerts.index'))

@alerts_bp.route('/auto-create/<int:event_id>')
@login_required
def auto_create_alerts(event_id):
    """Criar alertas automáticos para um evento"""
    try:
        success = native_alert_system.create_automatic_alerts_for_event(event_id)
        
        if success:
            flash('Alertas automáticos criados!', 'success')
        else:
            flash('Erro ao criar alertas automáticos.', 'error')
            
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('events.events'))

@alerts_bp.route('/test')
@login_required
def test_notification():
    """Testar notificação nativa"""
    try:
        success = native_alert_system.show_desktop_notification(
            title="🎵 Teste - Show Manager",
            message="Este é um teste do sistema de alertas nativos!"
        )
        
        if success:
            flash('Notificação de teste enviada!', 'success')
        else:
            flash('Erro ao enviar notificação de teste.', 'error')
            
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('alerts.index'))

@alerts_bp.route('/api/upcoming')
@login_required
def api_upcoming_alerts():
    """API para buscar próximos alertas"""
    try:
        days = int(request.args.get('days', 7))
        alerts = native_alert_system.get_upcoming_alerts(days=days)
        
        return jsonify({
            'success': True,
            'alerts': alerts
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@alerts_bp.route('/api/notifications')
@login_required
def api_notifications():
    """API para buscar notificações do banco"""
    try:
        notifications = Notification.query.filter_by(sent=False).order_by(Notification.scheduled_time).all()
        
        notifications_data = []
        for notif in notifications:
            notifications_data.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'scheduled_time': notif.scheduled_time.isoformat(),
                'priority': notif.priority,
                'event_title': notif.event.title,
                'artist_name': notif.event.artist.stage_name
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@alerts_bp.route('/start-daemon')
@login_required
def start_daemon():
    """Iniciar daemon de alertas"""
    try:
        native_alert_system.start_alert_daemon()
        flash('Daemon de alertas iniciado!', 'success')
    except Exception as e:
        flash(f'Erro ao iniciar daemon: {str(e)}', 'error')
    
    return redirect(url_for('alerts.index'))

@alerts_bp.route('/stop-daemon')
@login_required
def stop_daemon():
    """Parar daemon de alertas"""
    try:
        native_alert_system.stop_alert_daemon()
        flash('Daemon de alertas parado!', 'info')
    except Exception as e:
        flash(f'Erro ao parar daemon: {str(e)}', 'error')
    
    return redirect(url_for('alerts.index'))
