"""
Sistema de Alertas Nativo - Show Manager        try:
            event = Event.query.get(event_id)
            if not event:
                logger.error(f"Evento {event_id} não encontrado")
                return False
            
            # Preparar dados do alerta
            alert_data = {
                'event_id': event_id,
                'event_title': event.title,
                'event_date': event.start_datetime.isoformat(),
                'alert_time': alert_time.isoformat(),
                'alert_type': alert_type,
                'artist_name': event.artist.stage_name,
                'event_location': event.location,
                'created_at': datetime.now().isoformat()
            }cais independentes do Google Calendar
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import plyer
from plyer import notification
import schedule
import logging
from app.models import Event, User, Artist, Notification
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NativeAlertSystem:
    def __init__(self):
        self.alert_file = "alerts_cache.json"
        self.is_running = False
        
    def get_db_session(self):
        """Cria uma sessão de banco de dados independente"""
        try:
            from app import db
            return db.session
        except:
            return None
        
    def create_native_alert(self, event_id: int, alert_time: datetime, alert_type: str = "reminder"):
        """
        Cria um alerta nativo para um evento
        """
        try:
            db_session = self.get_db_session()
            if not db_session:
                logger.error("Não foi possível obter sessão do banco")
                return False
                
            event = db_session.query(Event).get(event_id)
            if not event:
                logger.error(f"Evento {event_id} não encontrado")
                return False
            
            # Preparar dados do alerta
            alert_data = {
                'event_id': event_id,
                'event_title': event.title,
                'event_date': event.date.isoformat(),
                'alert_time': alert_time.isoformat(),
                'alert_type': alert_type,
                'artist_name': event.artist.stage_name,
                'event_location': event.location,
                'created_at': datetime.now().isoformat()
            }
            
            # Salvar no cache local
            self._save_alert_to_cache(alert_data)
            
            # Criar notificação no banco
            notification = Notification(
                event_id=event_id,
                title=f"Alerta: {event.title}",
                message=f"Evento com {event.artist.stage_name} em {event.location}",
                notification_type=alert_type,
                scheduled_time=alert_time,
                priority='high' if alert_type == 'urgent' else 'medium'
            )
            
            db_session.add(notification)
            db_session.commit()
            
            logger.info(f"Alerta criado para evento {event_id} às {alert_time}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {str(e)}")
            if db_session:
                db_session.rollback()
            return False
    
    def _save_alert_to_cache(self, alert_data: Dict):
        """Salva alerta no cache local JSON"""
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
        """
        Mostra notificação nativa do sistema operacional
        """
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Show Manager",
                timeout=timeout,
                app_icon=None  # Você pode adicionar um ícone .ico aqui
            )
            logger.info(f"Notificação mostrada: {title}")
            return True
        except Exception as e:
            logger.error(f"Erro ao mostrar notificação: {str(e)}")
            return False
    
    def check_pending_alerts(self):
        """
        Verifica alertas pendentes e os exibe
        """
        try:
            if not os.path.exists(self.alert_file):
                return
            
            with open(self.alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            current_time = datetime.now()
            alerts_to_remove = []
            
            for i, alert in enumerate(alerts):
                alert_time = datetime.fromisoformat(alert['alert_time'])
                
                # Se chegou a hora do alerta
                if current_time >= alert_time:
                    self._trigger_alert(alert)
                    alerts_to_remove.append(i)
            
            # Remove alertas já executados
            for i in reversed(alerts_to_remove):
                alerts.pop(i)
            
            # Atualiza o arquivo
            with open(self.alert_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Erro ao verificar alertas: {str(e)}")
    
    def _trigger_alert(self, alert: Dict):
        """
        Dispara um alerta específico
        """
        try:
            event_date = datetime.fromisoformat(alert['event_date'])
            
            # Mensagem personalizada baseada no tipo
            if alert['alert_type'] == 'reminder':
                title = f"🎵 Lembrete: {alert['event_title']}"
                message = f"Evento com {alert['artist_name']} em {alert['event_location']}\n📅 {event_date.strftime('%d/%m/%Y às %H:%M')}"
            elif alert['alert_type'] == 'urgent':
                title = f"🚨 URGENTE: {alert['event_title']}"
                message = f"Evento HOJE com {alert['artist_name']}\n📍 {alert['event_location']}\n⏰ {event_date.strftime('%H:%M')}"
            else:
                title = f"📢 {alert['event_title']}"
                message = f"Evento com {alert['artist_name']}"
            
            # Mostrar notificação nativa
            self.show_desktop_notification(title, message, timeout=15)
            
            # Marcar como enviado no banco
            db_session = self.get_db_session()
            if db_session:
                notification = db_session.query(Notification).filter_by(
                    event_id=alert['event_id'],
                    scheduled_time=datetime.fromisoformat(alert['alert_time'])
                ).first()
                
                if notification:
                    notification.sent = True
                    notification.sent_at = datetime.now()
                    notification.push_notification_sent = True
                    db_session.commit()
            
            logger.info(f"Alerta disparado para evento {alert['event_id']}")
            
        except Exception as e:
            logger.error(f"Erro ao disparar alerta: {str(e)}")
    
    def create_automatic_alerts_for_event(self, event_id: int):
        """
        Cria alertas automáticos para um evento:
        - 1 dia antes
        - 2 horas antes
        - 30 minutos antes
        """
        try:
            db_session = self.get_db_session()
            if not db_session:
                return False
                
            event = db_session.query(Event).get(event_id)
            if not event:
                return False
            
            event_datetime = event.start_datetime
            
            # Alertas padrão
            alerts = [
                {
                    'time': event_datetime - timedelta(days=1),
                    'type': 'reminder',
                    'description': '1 dia antes'
                },
                {
                    'time': event_datetime - timedelta(hours=2),
                    'type': 'reminder',
                    'description': '2 horas antes'
                },
                {
                    'time': event_datetime - timedelta(minutes=30),
                    'type': 'urgent',
                    'description': '30 minutos antes'
                }
            ]
            
            created_count = 0
            for alert in alerts:
                # Só criar se o alerta for no futuro
                if alert['time'] > datetime.now():
                    if self.create_native_alert(event_id, alert['time'], alert['type']):
                        created_count += 1
                        logger.info(f"Alerta criado: {alert['description']}")
            
            return created_count > 0
            
        except Exception as e:
            logger.error(f"Erro ao criar alertas automáticos: {str(e)}")
            return False
    
    def start_alert_daemon(self):
        """
        Inicia o daemon que fica verificando alertas
        """
        if self.is_running:
            return
        
        self.is_running = True
        
        def check_alerts():
            while self.is_running:
                try:
                    self.check_pending_alerts()
                    time.sleep(30)  # Verifica a cada 30 segundos
                except Exception as e:
                    logger.error(f"Erro no daemon de alertas: {str(e)}")
                    time.sleep(60)  # Espera mais tempo se houver erro
        
        # Executar em thread separada
        alert_thread = threading.Thread(target=check_alerts, daemon=True)
        alert_thread.start()
        
        logger.info("Daemon de alertas iniciado")
    
    def stop_alert_daemon(self):
        """Para o daemon de alertas"""
        self.is_running = False
        logger.info("Daemon de alertas parado")
    
    def get_upcoming_alerts(self, days: int = 7) -> List[Dict]:
        """
        Retorna alertas programados para os próximos N dias
        """
        try:
            if not os.path.exists(self.alert_file):
                return []
            
            with open(self.alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            current_time = datetime.now()
            future_time = current_time + timedelta(days=days)
            
            upcoming = []
            for alert in alerts:
                alert_time = datetime.fromisoformat(alert['alert_time'])
                if current_time <= alert_time <= future_time:
                    upcoming.append(alert)
            
            # Ordenar por data
            upcoming.sort(key=lambda x: x['alert_time'])
            return upcoming
            
        except Exception as e:
            logger.error(f"Erro ao buscar alertas: {str(e)}")
            return []
    
    def clear_old_alerts(self, days: int = 30):
        """
        Remove alertas antigos do cache
        """
        try:
            if not os.path.exists(self.alert_file):
                return
            
            with open(self.alert_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
            
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # Filtrar alertas recentes
            recent_alerts = [
                alert for alert in alerts 
                if datetime.fromisoformat(alert['alert_time']) > cutoff_time
            ]
            
            with open(self.alert_file, 'w', encoding='utf-8') as f:
                json.dump(recent_alerts, f, indent=2, ensure_ascii=False)
            
            removed_count = len(alerts) - len(recent_alerts)
            if removed_count > 0:
                logger.info(f"Removidos {removed_count} alertas antigos")
                
        except Exception as e:
            logger.error(f"Erro ao limpar alertas: {str(e)}")

# Instância global
native_alert_system = NativeAlertSystem()
