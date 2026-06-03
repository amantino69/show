# -*- coding: utf-8 -*-
"""Garante tabelas e colunas em bancos já existentes (deploy Render)."""
from sqlalchemy import inspect, text

from app import db


def _table_columns(insp, table_name):
    try:
        return {c['name'] for c in insp.get_columns(table_name)}
    except Exception:
        return set()


def _add_column(conn, dialect, table, col, col_type):
    if dialect == 'postgresql':
        sql = f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS {col} {col_type}'
    elif dialect == 'sqlite':
        sql = f'ALTER TABLE {table} ADD COLUMN {col} {col_type}'
    else:
        sql = f'ALTER TABLE {table} ADD COLUMN {col} {col_type}'
    conn.execute(text(sql))


def ensure_schema():
    """Cria tabelas novas e adiciona colunas que faltam em bancos antigos."""
    try:
        db.create_all()
    except Exception as exc:
        print(f'schema_ensure create_all: {exc}')

    try:
        from app.models import User, Artist, Lead, BrandDeal
        insp = inspect(db.engine)
    except Exception as exc:
        print(f'schema_ensure inspect: {exc}')
        return

    dialect = db.engine.dialect.name
    model_tables = {
        User.__tablename__: User,
        Artist.__tablename__: Artist,
        Lead.__tablename__: Lead,
        BrandDeal.__tablename__: BrandDeal,
    }

    for table_name, model in model_tables.items():
        if table_name not in insp.get_table_names():
            continue
        existing = _table_columns(insp, table_name)
        for col in model.__table__.columns:
            if col.name in existing or col.name == 'id':
                continue
            col_type = col.type.compile(dialect=db.engine.dialect)
            try:
                with db.engine.begin() as conn:
                    _add_column(conn, dialect, table_name, col.name, str(col_type))
                print(f'schema_ensure: + {table_name}.{col.name}')
            except Exception as exc:
                print(f'schema_ensure: skip {table_name}.{col.name}: {exc}')

    _ensure_default_manager()


def _ensure_default_manager():
    """Garante usuário empresário se o banco estiver vazio."""
    try:
        from app.models import User
        if User.query.filter_by(is_manager=True).first():
            return
        manager = User(
            username='empresario',
            email='empresario@viezes.co',
            is_manager=True,
        )
        manager.set_password('123456')
        db.session.add(manager)
        db.session.commit()
        print('schema_ensure: usuário empresario criado')
    except Exception as exc:
        db.session.rollback()
        print(f'schema_ensure manager: {exc}')
