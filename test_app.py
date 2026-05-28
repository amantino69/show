#!/usr/bin/env python3
"""
Script simplificado para iniciar o sistema
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Criar aplicação Flask simples para teste
app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensões
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Importar modelos
from app.models import User, Artist, EventType

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rotas básicas para teste
@app.route('/')
def index():
    return '''
    <h1>Sistema de Gerenciamento de Artistas</h1>
    <p>Sistema funcionando corretamente!</p>
    <p><a href="/login">Fazer Login</a></p>
    '''

@app.route('/login')
def login():
    return '''
    <h2>Login</h2>
    <form method="post" action="/do_login">
        <p>Usuário: <input type="text" name="username" value="empresario"></p>
        <p>Senha: <input type="password" name="password" value="123456"></p>
        <p><input type="submit" value="Entrar"></p>
    </form>
    '''

@app.route('/do_login', methods=['POST'])
def do_login():
    from flask import request, redirect, flash
    from flask_login import login_user
    
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        login_user(user)
        return redirect('/dashboard')
    else:
        return 'Login inválido! <a href="/login">Tentar novamente</a>'

@app.route('/dashboard')
def dashboard():
    from flask_login import login_required, current_user
    
    @login_required
    def protected_dashboard():
        return f'''
        <h2>Dashboard</h2>
        <p>Bem-vindo, {current_user.username}!</p>
        <p>Tipo: {'Empresário' if current_user.is_manager else 'Artista'}</p>
        <p><a href="/logout">Sair</a></p>
        '''
    
    return protected_dashboard()

@app.route('/logout')
def logout():
    from flask_login import logout_user
    logout_user()
    return 'Logout realizado! <a href="/">Voltar ao início</a>'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("🚀 Sistema iniciado em: http://localhost:5000")
        print("👤 Login padrão: empresario / 123456")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
