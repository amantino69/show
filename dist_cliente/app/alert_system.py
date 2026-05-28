"""
Sistema de Alertas Nativo - Show Manager (Versão Simplificada)
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict
from plyer import notification
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NativeAlertSystem:
    def __init__(self):
        self.alert_file = "alerts_cache.json"
        self.is_running = False
        
    def create_native_alert(self, event_id: int, alert_time: datetime, alert_type: str = "reminder"):
        """Cria um alerta nativo para um evento"""
        try:
            # Import tardio para evitar circular imports
            from app.models import Event, Notification
            from app import db
            
            event = Event.query.get(event_id)
            if not event:
                logger.error(f"Evento {event_id} não encontrado")
                return False
            
            # Dados do alerta
            alert_data = {
                'event_id': event_id,
                'event_title': event.title,
                'event_date': event.start_datetime.isoformat(),
                'alert_time': alert_time.isoformat(),
                'alert_type': alert_type,
                'artist_name': event.artist.stage_name,
                'event_location': event.location or "Local não informado",
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no cache local
            self._save_alert_to_cache(alert_data)
            
            # Criar notificação no banco
            notification_obj = Notification(
                event_id=event_id,
                title=f"Alerta: {event.title}",
                message=f"Evento com {event.artist.stage_name}",
                notification_type=alert_type,
                scheduled_time=alert_time,
                priority='high' if alert_type == 'urgent' else 'medium'
            )
            
            db.session.add(notification_obj)
            db.session.commit()
            
            logger.info(f"Alerta criado para evento {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {str(e)}")
            return False
    
    def _save_alert_to_cache(self, alert_data: Dict):
        """Salva alerta no cache local"""
        try:
            alerts = []
            if os.path.exists(self.alert_file):
                with open(self.alert_file, 'r', encoding='utf-8') as f:
                    alerts = json.load(f)
            
            alerts.append(alert_data)
            
            with open(self.alert_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
    
    def show_desktop_notification(self, title: str, message: str, timeout: int = 10):
        """Mostra notificação nativa"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Show Manager",
                timeout=timeout,
                app_icon=None
            )
            logger.info(f"Notificação mostrada: {title}")
            return True
        except Exception as e:
            logger.error(f"Erro ao mostrar notificação: {str(e)}")
            return False
    
    def create_automatic_alerts_for_event(self, event_id: int):
        """Cria alertas automáticos para um evento"""
        try:
            from app.models import Event
            
            event = Event.query.get(event_id)
            if not event:
                return False
            
            event_datetime = event.start_datetime
            
            # Alertas padrão
            alerts = [
                (event_datetime - timedelta(days=1), 'reminder', '1 dia antes'),
                (event_datetime - timedelta(hours=2), 'reminder', '2 horas antes'),
                (event_datetime - timedelta(minutes=30), 'urgent', '30 minutos antes')
            ]
            
            created_count = 0
            for alert_time, alert_type, description in alerts:
                if alert_time > datetime.now():
                    if self.create_native_alert(event_id, alert_time, alert_type):
                        created_count += 1
                        logger.info(f"Alerta criado: {description}")
            
            return created_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao criar alertas automáticos: {str(e)}")
            return False
    
    def check_pending_alerts(self):
        """Verifica alertas pendentes"""
        try:
            if not os.path.exists(self.alert_file):
                return
            
            with open(self.alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            current_time = datetime.now()
            alerts_to_remove = []
            
            for i, alert in enumerate(alerts):
                alert_time = datetime.fromisoformat(alert['alert_time'])
                
                if current_time >= alert_time:
                    self._trigger_alert(alert)
                    alerts_to_remove.append(i)
            
            # Remove alertas processados
            for i in reversed(alerts_to_remove):
                alerts.pop(i)
            
            # Atualiza arquivo
            with open(self.alert_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {str(e)}")
    
    def _trigger_alert(self, alert: Dict):
        """Dispara um alerta"""
        try:
            event_date = datetime.fromisoformat(alert['event_date'])
            
            if alert['alert_type'] == 'reminder':
                title = f"🎵 Lembrete: {alert['event_title']}"
                message = f"Evento com {alert['artist_name']}\n📅 {event_date.strftime('%d/%m/%Y às %H:%M')}"
            elif alert['alert_type'] == 'urgent':
                title = f"🚨 URGENTE: {alert['event_title']}"
                message = f"Evento com {alert['artist_name']}\n⏰ {event_date.strftime('%H:%M')}"
            else:
                title = f"📢 {alert['event_title']}"
                message = f"Evento com {alert['artist_name']}"
            
            self.show_desktop_notification(title, message, timeout=15)
            
            # Tentar marcar como enviado no banco
            try:
                from app.models import Notification
                from app import db
                
                notification_obj = Notification.query.filter_by(
                    event_id=alert['event_id'],
                    scheduled_time=datetime.fromisoformat(alert['alert_time'])
                ).first()
                
                if notification_obj:
                    notification_obj.sent = True
                    notification_obj.sent_at = datetime.now()
                    notification_obj.push_notification_sent = True
                    db.session.commit()
            except Exception:
                pass  # Se falhar, não é crítico
            
            logger.info(f"Alerta disparado para evento {alert['event_id']}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar alerta: {str(e)}")
    
    def start_alert_daemon(self):
        """Inicia daemon de verificação"""
        if self.is_running:
            return
        
        self.is_running = True
        
        def check_loop():
            while self.is_running:
                try:
                    self.check_pending_alerts()
                    time.sleep(30)
                except Exception as e:
                    logger.error(f"Erro no daemon: {str(e)}")
                    time.sleep(60)
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
        logger.info("Daemon de alertas iniciado")
    
    def stop_alert_daemon(self):
        """Para daemon"""
        self.is_running = False
        logger.info("Daemon de alertas parado")
    
    def get_upcoming_alerts(self, days: int = 7) -> List[Dict]:
        """Retorna próximos alertas"""
        try:
            if not os.path.exists(self.alert_file):
                return []
            
            with open(self.alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            current_time = datetime.now()
            future_time = current_time + timedelta(days=days)
            
            upcoming = [
                alert for alert in alerts
                if current_time <= datetime.fromisoformat(alert['alert_time']) <= future_time
            ]
            
            upcoming.sort(key=lambda x: x['alert_time'])
            return upcoming
            
        except Exception as e:
            logger.error(f"Erro ao buscar alertas: {str(e)}")
            return []

# Instância global
native_alert_system = NativeAlertSystem()
