# -*- coding: utf-8 -*-
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.team import bp
from app.models import User, Artist
from app.delete_helpers import can_delete_user

TEAM_ROLES = {
    'estrategico': 'Estratégico (Julia Maria)',
    'operacional': 'Operacional (Juju)',
    'captacao': 'Captação (Julia Viana)',
    'outro': 'Outro',
}


def _manager_required():
    if not current_user.is_manager:
        flash('Acesso restrito.', 'error')
        return False
    return True


@bp.route('/')
@login_required
def index():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    users = User.query.order_by(User.is_manager.desc(), User.username).all()
    managers_count = User.query.filter_by(is_manager=True, is_active_user=True).count()
    return render_template(
        'team/index.html',
        users=users,
        roles=TEAM_ROLES,
        managers_count=managers_count,
    )


@bp.route('/novo', methods=['GET', 'POST'])
@login_required
def new_user():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    artists = Artist.query.filter_by(is_active=True).order_by(Artist.stage_name).all()

    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not email or not password:
            flash('Preencha usuário, e-mail e senha.', 'error')
            return render_template(
        'team/form.html',
        user=None,
        artists=artists,
        roles=TEAM_ROLES,
        can_delete=False,
        delete_reason='',
    )

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Usuário ou e-mail já existe.', 'error')
            return render_template(
        'team/form.html',
        user=None,
        artists=artists,
        roles=TEAM_ROLES,
        can_delete=False,
        delete_reason='',
    )

        is_manager = request.form.get('user_type') == 'manager'
        artist_id = request.form.get('artist_id', type=int) if not is_manager else None

        user = User(
            username=username,
            email=email,
            is_manager=is_manager,
            artist_id=artist_id,
            display_name=request.form.get('display_name', '').strip() or None,
            team_role=request.form.get('team_role', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            is_active_user=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Usuário criado.', 'success')
        return redirect(url_for('team.index'))

    return render_template(
        'team/form.html',
        user=None,
        artists=artists,
        roles=TEAM_ROLES,
        can_delete=False,
        delete_reason='',
    )


@bp.route('/<int:user_id>/editar', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    artists = Artist.query.filter_by(is_active=True).order_by(Artist.stage_name).all()

    if request.method == 'POST':
        user.email = request.form.get('email', '').strip()
        user.display_name = request.form.get('display_name', '').strip() or None
        user.team_role = request.form.get('team_role', '').strip() or None
        user.phone = request.form.get('phone', '').strip() or None
        user.is_active_user = request.form.get('is_active_user') == 'on'
        if request.form.get('user_type') == 'manager':
            user.is_manager = True
            user.artist_id = None
        else:
            user.is_manager = False
            user.artist_id = request.form.get('artist_id', type=int)
        new_pass = request.form.get('password', '').strip()
        if new_pass:
            user.set_password(new_pass)
        db.session.commit()
        flash('Usuário atualizado.', 'success')
        return redirect(url_for('team.index'))

    can_delete, delete_reason = can_delete_user(user, current_user.id)
    return render_template(
        'team/form.html',
        user=user,
        artists=artists,
        roles=TEAM_ROLES,
        can_delete=can_delete,
        delete_reason=delete_reason,
    )


@bp.route('/<int:user_id>/excluir', methods=['POST'])
@login_required
def delete_user(user_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    ok, reason = can_delete_user(user, current_user.id)
    if not ok:
        flash(reason, 'error')
        return redirect(url_for('team.edit_user', user_id=user_id))

    username = user.username
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuário "{username}" excluído.', 'success')
    return redirect(url_for('team.index'))
