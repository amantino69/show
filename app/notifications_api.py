from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.models import Event, User, Notification
from app import db
import json

bp = Blueprint('notifications', __name__)

@bp.route('/api/upcoming-events')
@login_required
def upcoming_events():
    """API para retornar eventos próximos do usuário"""
    now = datetime.now()
    upcoming_limit = now + timedelta(days=7)  # Próximos 7 dias
    
    if current_user.is_manager:
        events = Event.query.filter(
            Event.start_datetime.between(now, upcoming_limit),
            Event.status.in_(['agendado', 'em_andamento'])
        ).order_by(Event.start_datetime).all()
    else:
        events = Event.query.filter(
            Event.artist_id == current_user.artist_id,
            Event.start_datetime.between(now, upcoming_limit),
            Event.status.in_(['agendado', 'em_andamento'])
        ).order_by(Event.start_datetime).all()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start_datetime': event.start_datetime.isoformat(),
            'end_datetime': event.end_datetime.isoformat(),
            'location': event.location,
            'artist': event.artist.stage_name,
            'priority': event.priority,
            'status': event.status
        })
    
    return jsonify(events_data)

@bp.route('/api/mark-notification-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Marcar notificação como lida"""
    notification = Notification.query.get_or_404(notification_id)
    
    # Verificar se a notificação pertence ao usuário
    if notification.event.artist_id != current_user.artist_id and not current_user.is_manager:
        return jsonify({'error': 'Acesso negado'}), 403
    
    notification.read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@bp.route('/api/user-notifications')
@login_required
def user_notifications():
    """Obter notificações não lidas do usuário"""
    if current_user.is_manager:
        # Manager vê todas as notificações
        notifications = Notification.query.filter(
            Notification.read == False
        ).order_by(Notification.created_at.desc()).limit(20).all()
    else:
        # Artista vê apenas suas notificações
        notifications = Notification.query.join(Event).filter(
            Event.artist_id == current_user.artist_id,
            Notification.read == False
        ).order_by(Notification.created_at.desc()).limit(20).all()
    
    notifications_data = []
    for notif in notifications:
        notifications_data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'type': notif.notification_type,
            'event_id': notif.event_id,
            'created_at': notif.created_at.isoformat(),
            'priority': notif.priority
        })
    
    return jsonify(notifications_data)

@bp.route('/api/send-test-notification', methods=['POST'])
@login_required
def send_test_notification():
    """Enviar notificação de teste"""
    if not current_user.is_manager:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Criar notificação de teste
    test_notification = {
        'title': 'Teste de Notificação',
        'message': 'Esta é uma notificação de teste do sistema.',
        'type': 'test',
        'priority': 'medium'
    }
    
    # Aqui você pode integrar com serviços como:
    # - Firebase Cloud Messaging (FCM)
    # - OneSignal
    # - Pusher
    # - WebSockets
    
    return jsonify({'success': True, 'message': 'Notificação de teste enviada'})

class NotificationScheduler:
    """Classe para agendar e enviar notificações automáticas"""
    
    @staticmethod
    def schedule_event_notifications(event):
        """Agendar notificações para um evento"""
        from app.models import Notification
        
        # Notificações a serem criadas
        notification_times = [
            {'hours': 24, 'title': 'Evento amanhã'},
            {'hours': 3, 'title': 'Evento em 3 horas'},
            {'minutes': 30, 'title': 'Evento em 30 minutos'}
        ]
        
        for timing in notification_times:
            if 'hours' in timing:
                notification_time = event.start_datetime - timedelta(hours=timing['hours'])
            else:
                notification_time = event.start_datetime - timedelta(minutes=timing['minutes'])
            
            # Só criar se a notificação for futura
            if notification_time > datetime.utcnow():
                notification = Notification(
                    event_id=event.id,
                    title=timing['title'],
                    message=f"{event.title} - {event.artist.stage_name}",
                    notification_type='reminder',
                    scheduled_time=notification_time,
                    priority=event.priority
                )
                db.session.add(notification)
        
        db.session.commit()
    
    @staticmethod
    def send_immediate_notification(event, notification_type, title, message):
        """Enviar notificação imediata"""
        notification = Notification(
            event_id=event.id,
            title=title,
            message=message,
            notification_type=notification_type,
            scheduled_time=datetime.utcnow(),
            sent=True,
            sent_at=datetime.utcnow(),
            priority=event.priority
        )
        db.session.add(notification)
        db.session.commit()
        
        # Aqui você integraria com o serviço de push notifications
        # NotificationScheduler.send_push_notification(notification)
    
    @staticmethod
    def process_pending_notifications():
        """Processar notificações pendentes (executar via cron ou scheduler)"""
        now = datetime.utcnow()
        pending_notifications = Notification.query.filter(
            Notification.sent == False,
            Notification.scheduled_time <= now
        ).all()
        
        for notification in pending_notifications:
            # Enviar notificação
            # NotificationScheduler.send_push_notification(notification)
            
            notification.sent = True
            notification.sent_at = now
        
        db.session.commit()
        return len(pending_notifications)
