import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from app.models import User
from app import db
from config import Config

# Desabilitar HTTPS em desenvolvimento
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def get_google_credentials(user_id):
    """Obtém as credenciais do Google para um usuário"""
    user = User.query.get(user_id)
    if not user or not user.google_token:
        return None
    
    try:
        token_data = json.loads(user.google_token)
        creds = Credentials.from_authorized_user_info(token_data)
        
        # Verificar se o token precisa ser renovado
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Salvar token atualizado
            user.google_token = creds.to_json()
            db.session.commit()
        
        return creds
    except Exception as e:
        print(f"Erro ao obter credenciais: {e}")
        return None

def create_google_event(event):
    """Cria um evento no Google Calendar do empresário E do artista"""
    from flask_login import current_user
    
    event_ids = []
    
    # 1. CRIAR EVENTO NA AGENDA DO EMPRESÁRIO (quem está criando)
    manager_creds = get_google_credentials(current_user.id)
    if manager_creds:
        try:
            service = build('calendar', 'v3', credentials=manager_creds)
            
            # Configurar evento para o empresário
            google_event = {
                'summary': f"🎵 {event.title} - {event.artist.stage_name}",
                'description': f"""📅 EVENTO: {event.title}
🎤 ARTISTA: {event.artist.stage_name}
📍 LOCAL: {event.location or 'Não informado'}
📝 DESCRIÇÃO: {event.description or 'Sem descrição'}

✨ Criado pelo Sistema de Gerenciamento de Artistas""",
                'location': event.location or '',
                'start': {
                    'dateTime': event.start_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': event.end_datetime.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'colorId': str(hash(event.artist.color) % 11 + 1),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 2 * 24 * 60},  # 2 dias antes
                        {'method': 'email', 'minutes': 1 * 24 * 60},  # 1 dia antes
                        {'method': 'email', 'minutes': 3 * 60},       # 3 horas antes
                        {'method': 'popup', 'minutes': 15},           # 15 min antes
                    ],
                },
                'attendees': [
                    {'email': event.artist.email, 'displayName': event.artist.stage_name},
                    {'email': current_user.email, 'displayName': 'Empresário'},
                ],
            }
            
            created_event = service.events().insert(calendarId='primary', body=google_event).execute()
            event_ids.append(f"manager:{created_event.get('id')}")
            print(f"✅ Evento criado na agenda do empresário: {created_event.get('id')}")
            
        except Exception as e:
            print(f"❌ Erro ao criar evento na agenda do empresário: {e}")
    
    # 2. CRIAR EVENTO NA AGENDA DO ARTISTA (se ele tiver conta Google conectada)
    artist_user = User.query.filter_by(email=event.artist.email).first()
    if artist_user and artist_user.google_token:
        artist_creds = get_google_credentials(artist_user.id)
        if artist_creds:
            try:
                artist_service = build('calendar', 'v3', credentials=artist_creds)
                
                # Configurar evento para o artista
                artist_event = {
                    'summary': f"🎪 {event.title}",
                    'description': f"""🎤 MEU EVENTO: {event.title}
📍 LOCAL: {event.location or 'Não informado'}
📝 DESCRIÇÃO: {event.description or 'Sem descrição'}
👔 EMPRESÁRIO: {current_user.email}

🌟 Minha agenda de apresentações""",
                    'location': event.location or '',
                    'start': {
                        'dateTime': event.start_datetime.isoformat(),
                        'timeZone': 'America/Sao_Paulo',
                    },
                    'end': {
                        'dateTime': event.end_datetime.isoformat(),
                        'timeZone': 'America/Sao_Paulo',
                    },
                    'colorId': str(hash(event.artist.color) % 11 + 1),
                    'reminders': {
                        'useDefault': False,
                        'overrides': [
                            {'method': 'email', 'minutes': 2 * 24 * 60},  # 2 dias antes
                            {'method': 'email', 'minutes': 1 * 24 * 60},  # 1 dia antes
                            {'method': 'email', 'minutes': 3 * 60},       # 3 horas antes
                            {'method': 'popup', 'minutes': 30},           # 30 min antes
                        ],
                    },
                }
                
                artist_created_event = artist_service.events().insert(calendarId='primary', body=artist_event).execute()
                event_ids.append(f"artist:{artist_created_event.get('id')}")
                print(f"✅ Evento criado na agenda do artista: {artist_created_event.get('id')}")
                
            except Exception as e:
                print(f"❌ Erro ao criar evento na agenda do artista: {e}")
        else:
            print(f"⚠️ Artista {event.artist.stage_name} não tem Google Calendar conectado")
    else:
        print(f"⚠️ Artista {event.artist.stage_name} não possui conta no sistema ou Google Calendar")
    
    # Retornar IDs dos eventos criados (separados por vírgula)
    return ",".join(event_ids) if event_ids else None

def update_google_event(event):
    """Atualiza eventos no Google Calendar do empresário E do artista"""
    from flask_login import current_user
    
    if not event.google_event_id:
        return False
    
    success_count = 0
    event_ids = event.google_event_id.split(',')
    
    for event_id_entry in event_ids:
        try:
            # Separar tipo (manager/artist) e ID
            if ':' in event_id_entry:
                event_type, google_id = event_id_entry.split(':', 1)
            else:
                event_type, google_id = 'manager', event_id_entry
            
            # Obter credenciais apropriadas
            if event_type == 'manager':
                creds = get_google_credentials(current_user.id)
            elif event_type == 'artist':
                artist_user = User.query.filter_by(email=event.artist.email).first()
                creds = get_google_credentials(artist_user.id) if artist_user else None
            else:
                continue
            
            if not creds:
                continue
            
            service = build('calendar', 'v3', credentials=creds)
            
            # Buscar evento existente
            existing_event = service.events().get(
                calendarId='primary', 
                eventId=google_id
            ).execute()
            
            # Atualizar campos baseado no tipo
            if event_type == 'manager':
                existing_event['summary'] = f"🎵 {event.title} - {event.artist.stage_name}"
                existing_event['description'] = f"""📅 EVENTO: {event.title}
🎤 ARTISTA: {event.artist.stage_name}
📍 LOCAL: {event.location or 'Não informado'}
📝 DESCRIÇÃO: {event.description or 'Sem descrição'}

✨ Atualizado pelo Sistema de Gerenciamento de Artistas"""
            else:  # artist
                existing_event['summary'] = f"🎪 {event.title}"
                existing_event['description'] = f"""🎤 MEU EVENTO: {event.title}
📍 LOCAL: {event.location or 'Não informado'}
📝 DESCRIÇÃO: {event.description or 'Sem descrição'}
👔 EMPRESÁRIO: {current_user.email}

🌟 Atualizado - Minha agenda de apresentações"""
            
            existing_event['location'] = event.location or ''
            existing_event['start'] = {
                'dateTime': event.start_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            }
            existing_event['end'] = {
                'dateTime': event.end_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            }
            
            service.events().update(
                calendarId='primary', 
                eventId=google_id, 
                body=existing_event
            ).execute()
            
            success_count += 1
            print(f"✅ Evento {event_type} atualizado: {google_id}")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar evento {event_type}: {e}")
    
    return success_count > 0

def delete_google_event(google_event_id):
    """Deleta eventos do Google Calendar do empresário E do artista"""
    from flask_login import current_user
    
    if not google_event_id:
        return False
    
    success_count = 0
    event_ids = google_event_id.split(',')
    
    for event_id_entry in event_ids:
        try:
            # Separar tipo (manager/artist) e ID
            if ':' in event_id_entry:
                event_type, google_id = event_id_entry.split(':', 1)
            else:
                event_type, google_id = 'manager', event_id_entry
            
            # Obter credenciais apropriadas
            if event_type == 'manager':
                creds = get_google_credentials(current_user.id)
            elif event_type == 'artist':
                # Precisaríamos do email do artista, mas como estamos deletando,
                # vamos tentar com as credenciais do empresário
                creds = get_google_credentials(current_user.id)
            else:
                continue
            
            if not creds:
                continue
            
            service = build('calendar', 'v3', credentials=creds)
            service.events().delete(calendarId='primary', eventId=google_id).execute()
            
            success_count += 1
            print(f"✅ Evento {event_type} deletado: {google_id}")
            
        except Exception as e:
            print(f"❌ Erro ao deletar evento {event_type}: {e}")
    
    return success_count > 0
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId='primary', eventId=google_event_id).execute()
        return True
        
    except Exception as e:
        print(f"Erro ao deletar evento do Google Calendar: {e}")
        return False

def setup_google_auth():
    """Configura autenticação do Google"""
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar']
    )
    flow.redirect_uri = Config.GOOGLE_REDIRECT_URI
    return flow
