from flask import redirect, url_for, session, flash, request, current_app
from flask_login import login_required, current_user
from app.google_auth import bp
from app.google_calendar import setup_google_auth
from app.models import User
from app import db
import json

@bp.route('/authorize')
@login_required
def authorize():
    """Inicia o processo de autorização do Google"""
    try:
        flow = setup_google_auth()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        session['state'] = state
        return redirect(authorization_url)
    except Exception as e:
        flash(f'Erro ao iniciar autorização: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

@bp.route('/callback')
def callback():
    """Processa o retorno da autorização do Google"""
    try:
        if 'state' not in session:
            flash('Erro: Estado da sessão não encontrado', 'error')
            return redirect(url_for('main.dashboard'))
        
        flow = setup_google_auth()
        flow.fetch_token(authorization_response=request.url)
        
        # Salvar token do usuário
        if current_user.is_authenticated:
            credentials = flow.credentials
            current_user.google_token = credentials.to_json()
            db.session.commit()
            
            flash('Google Calendar conectado com sucesso!', 'success')
        else:
            flash('Usuário não autenticado', 'error')
        
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        flash(f'Erro na autorização: {str(e)}', 'error')
        return redirect(url_for('main.dashboard'))

# Rota alternativa para callback direto
@bp.route('/../../callback')  
def callback_direct():
    """Rota alternativa para callback direto"""
    return callback()

@bp.route('/disconnect')
@login_required
def disconnect():
    """Desconecta o Google Calendar"""
    try:
        current_user.google_token = None
        db.session.commit()
        flash('Google Calendar desconectado', 'info')
    except Exception as e:
        flash(f'Erro ao desconectar: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))
