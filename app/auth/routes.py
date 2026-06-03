from flask import render_template, request, flash, redirect, url_for, current_app
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse as url_parse
from app.auth import bp
from app.models import User, Artist
from app import db
from werkzeug.security import generate_password_hash

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        try:
            user = User.query.filter_by(username=username).first()
        except Exception as exc:
            current_app.logger.exception('Erro ao consultar usuário no login')
            flash('Erro temporário no banco de dados. Tente novamente em instantes.', 'error')
            return render_template('auth/login.html')

        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if user.is_manager:
                    next_page = url_for('main.dashboard')
                else:
                    next_page = url_for('portal.index')
            return redirect(next_page)
        flash('Usuário ou senha inválidos.', 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            flash('Nome de usuário já existe.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email já está cadastrado.', 'error')
            return render_template('auth/register.html')
        
        # Criar novo usuário
        user = User(
            username=username,
            email=email,
            is_manager=(user_type == 'manager')
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Conta criada com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
