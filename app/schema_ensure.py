# -*- coding: utf-8 -*-
"""Garante colunas/tabelas mínimas em bancos já existentes (deploy Render)."""
from sqlalchemy import inspect, text

from app import db


USER_COLUMNS = {
    'display_name': 'VARCHAR(120)',
    'team_role': 'VARCHAR(40)',
    'phone': 'VARCHAR(20)',
    'is_active_user': 'BOOLEAN DEFAULT 1',
}


def ensure_schema():
    db.create_all()
    try:
        insp = inspect(db.engine)
    except Exception:
        return

    if 'user' not in insp.get_table_names():
        return

    existing = {c['name'] for c in insp.get_columns('user')}
    dialect = db.engine.dialect.name

    for col, col_type in USER_COLUMNS.items():
        if col in existing:
            continue
        sql = f'ALTER TABLE user ADD COLUMN {col} {col_type}'
        if dialect == 'postgresql':
            sql = f'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS {col} {col_type}'
        try:
            with db.engine.begin() as conn:
                conn.execute(text(sql))
        except Exception as exc:
            db.session.rollback()
            print(f'schema_ensure: ignorando {col}: {exc}')
