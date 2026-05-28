from twilio.rest import Client
import os
from datetime import datetime

class WhatsAppNotifier:
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.whatsapp_from = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
        
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
            self.enabled = True
        else:
            self.enabled = False
            print("Twilio não configurado. Notificações WhatsApp desabilitadas.")
    
    def send_event_reminder(self, event, phone_number, hours_before=3):
        """Enviar lembrete de evento via WhatsApp"""
        if not self.enabled:
            return False
        
        message = f"""
🎵 *Lembrete de Evento*

📅 *{event.title}*
🎤 Artista: {event.artist.stage_name}
📍 Local: {event.location or 'Não informado'}
🕒 Data/Hora: {event.start_datetime.strftime('%d/%m/%Y às %H:%M')}
⏰ Em {hours_before} horas

_Sistema de Gerenciamento de Artistas_
        """.strip()
        
        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.whatsapp_from,
                to=f'whatsapp:{phone_number}'
            )
            return message_instance.sid
        except Exception as e:
            print(f"Erro ao enviar WhatsApp: {e}")
            return False
    
    def send_event_update(self, event, phone_number, update_type='updated'):
        """Enviar atualização de evento via WhatsApp"""
        if not self.enabled:
            return False
        
        icons = {
            'updated': '✏️',
            'cancelled': '❌',
            'postponed': '⏰',
            'confirmed': '✅'
        }
        
        titles = {
            'updated': 'Evento Atualizado',
            'cancelled': 'Evento Cancelado',
            'postponed': 'Evento Adiado',
            'confirmed': 'Evento Confirmado'
        }
        
        message = f"""
{icons.get(update_type, '📢')} *{titles.get(update_type, 'Atualização de Evento')}*

📅 *{event.title}*
🎤 Artista: {event.artist.stage_name}
📍 Local: {event.location or 'Não informado'}
🕒 Data/Hora: {event.start_datetime.strftime('%d/%m/%Y às %H:%M')}
📊 Status: {event.status.title()}

_Sistema de Gerenciamento de Artistas_
        """.strip()
        
        try:
            message_instance = self.client.messages.create(
                body=message,
                from_=self.whatsapp_from,
                to=f'whatsapp:{phone_number}'
            )
            return message_instance.sid
        except Exception as e:
            print(f"Erro ao enviar WhatsApp: {e}")
            return False

# Instância global
whatsapp_notifier = WhatsAppNotifier()
