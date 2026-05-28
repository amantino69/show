# -*- coding: utf-8 -*-
"""Garante usuário administrador julia / 123."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User


def main():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username='julia').first()
        if not user:
            user = User(
                username='julia',
                email='julia@viezes.co',
                is_manager=True,
                is_active_user=True,
                display_name='Julia',
                team_role='estrategico',
            )
            db.session.add(user)
            print('Usuário julia criado.')
        else:
            print('Usuário julia já existia — senha e permissões atualizadas.')

        user.set_password('123')
        user.is_manager = True
        user.is_active_user = True
        user.artist_id = None
        if not user.display_name:
            user.display_name = 'Julia'
        db.session.commit()
        print('Login: julia / 123 (administrador)')


if __name__ == '__main__':
    main()
