from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from app import mail, scheduler, db
from app.models import Event, Notification, User

def send_notification_email(event, hours_before):
    """Envia email de notificação para um evento"""
    try:
        subject = f"Lembrete: {event.title} em {hours_before}h"
        
        if hours_before >= 24:
            days = hours_before // 24
            time_text = f"{days} dia(s)" if days > 1 else "1 dia"
        else:
            time_text = f"{hours_before} hora(s)"
        
        body = f"""
        Olá!
        
        Este é um lembrete de que o evento "{event.title}" está agendado para acontecer em {time_text}.
        
        Detalhes do evento:
        • Artista: {event.artist.stage_name}
        • Data/Hora: {event.start_datetime.strftime('%d/%m/%Y às %H:%M')}
        • Local: {event.location or 'Local não informado'}
        • Descrição: {event.description or 'Sem descrição'}
        
        Não esqueça de se preparar!
        
        Sistema de Gerenciamento de Artistas
        """
        
        # Enviar para o artista
        msg_artist = Message(
            subject=subject,
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[event.artist.email],
            body=body
        )
        mail.send(msg_artist)
        
        # Enviar para o empresário (usuários manager)
        managers = User.query.filter_by(is_manager=True).all()
        for manager in managers:
            msg_manager = Message(
                subject=subject,
                sender=current_app.config['MAIL_USERNAME'],
                recipients=[manager.email],
                body=body
            )
            mail.send(msg_manager)
        
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False

def schedule_event_notifications(event):
    """Agenda notificações para um evento"""
    notification_times = [
        (24, "1 dia antes"),    # 1 dia antes
        (2, "2 horas antes"),   # 2 horas antes
        (0.5, "30 minutos antes") # 30 minutos antes
    ]
    
    for hours_before, time_description in notification_times:
        notification_time = event.start_datetime - timedelta(hours=hours_before)
        
        # Só agendar se a notificação for no futuro
        if notification_time > datetime.now():
            # Gerar título e mensagem
            title = f"Lembrete: {event.title}"
            message = f"O evento '{event.title}' com {event.artist.stage_name} está agendado para {event.start_datetime.strftime('%d/%m/%Y às %H:%M')} ({time_description})."
            
            # Criar registro de notificação
            notification = Notification(
                event_id=event.id,
                title=title,
                message=message,
                notification_type='reminder',
                scheduled_time=notification_time,
                priority='medium'
            )
            db.session.add(notification)
            
            # Agendar job no scheduler
            job_id = f"notification_{event.id}_{hours_before}h"
            scheduler.add_job(
                func=send_event_notification,
                trigger='date',
                run_date=notification_time,
                args=[event.id, hours_before],
                id=job_id,
                replace_existing=True
            )
    
    db.session.commit()

def send_event_notification(event_id, hours_before):
    """Função executada pelo scheduler para enviar notificação"""
    from app import create_app
    
    app = create_app()
    with app.app_context():
        event = Event.query.get(event_id)
        if event and event.status != 'cancelado':
            success = send_notification_email(event, hours_before)
            
            # Marcar notificação como enviada
            notification = Notification.query.filter_by(
                event_id=event_id,
                scheduled_time=datetime.now() - timedelta(minutes=5),  # Margem de erro
                sent=False
            ).first()
            
            if notification:
                notification.sent = success
                notification.sent_at = datetime.now()
                db.session.commit()

def cancel_event_notifications(event_id):
    """Cancela todas as notificações de um evento"""
    # Remover jobs do scheduler
    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.id.startswith(f"notification_{event_id}_"):
            scheduler.remove_job(job.id)
    
    # Marcar notificações como canceladas no banco
    notifications = Notification.query.filter_by(event_id=event_id, sent=False).all()
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()

def reschedule_event_notifications(event):
    """Reagenda notificações quando um evento é atualizado"""
    # Cancelar notificações existentes
    cancel_event_notifications(event.id)
    
    # Criar novas notificações
    schedule_event_notifications(event)
