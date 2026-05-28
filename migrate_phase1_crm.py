"""
Migração Fase 1 — CRM, pipeline de marcas e campos de assessorado.
Execute: python migrate_phase1_crm.py
"""
import sqlite3
import os

DB_PATH = os.path.join('instance', 'artistas_sistema.db')

ARTIST_COLUMNS = [
    ('client_status', "VARCHAR(20) DEFAULT 'ativo'"),
    ('service_type', 'VARCHAR(30)'),
    ('niche', 'VARCHAR(120)'),
    ('city', 'VARCHAR(80)'),
    ('state', 'VARCHAR(2)'),
    ('instagram', 'VARCHAR(120)'),
    ('onboarding_progress', 'INTEGER DEFAULT 0'),
    ('lead_id', 'INTEGER'),
    ('onboarding_data', 'TEXT'),
    ('entry_date', 'DATE'),
]


def column_exists(cursor, table, column):
    cursor.execute(f'PRAGMA table_info({table})')
    return any(row[1] == column for row in cursor.fetchall())


def table_exists(cursor, table):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cursor.fetchone() is not None


def main():
    if not os.path.exists(DB_PATH):
        print(f'Banco não encontrado: {DB_PATH}')
        print('Execute primeiro: python app.py (cria tabelas) ou python init_db.py')
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for col, typedef in ARTIST_COLUMNS:
        if not column_exists(cur, 'artist', col):
            cur.execute(f'ALTER TABLE artist ADD COLUMN {col} {typedef}')
            print(f'  + artist.{col}')
        else:
            print(f'  = artist.{col} (já existe)')

    cur.execute("UPDATE artist SET client_status = 'ativo' WHERE client_status IS NULL")

    if not table_exists(cur, 'lead'):
        print('Tabelas lead/brand_deal: use db.create_all() via Flask')
        from app import create_app, db
        app = create_app()
        with app.app_context():
            db.create_all()
        print('  + tabelas criadas via SQLAlchemy')
    else:
        print('  = tabela lead já existe')

    conn.commit()
    conn.close()
    print('Migração Fase 1 concluída.')


if __name__ == '__main__':
    main()
