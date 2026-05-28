"""
Migração Fase 2 — onboarding templates, financeiro, pipeline marcas.
Execute: python migrate_phase2.py
"""
import os
import sqlite3

DB_PATH = os.path.join('instance', 'artistas_sistema.db')

ARTIST_COLUMNS = [
    ('monthly_fee', 'NUMERIC(12, 2)'),
    ('payment_status', "VARCHAR(30) DEFAULT 'em_dia'"),
    ('payment_due_day', 'INTEGER'),
    ('current_phase', 'VARCHAR(80)'),
    ('strategic_manager', 'VARCHAR(120)'),
    ('operational_manager', 'VARCHAR(120)'),
]

BRAND_DEAL_COLUMNS = [
    ('brand_segment', 'VARCHAR(120)'),
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
        print('Execute primeiro: py app.py ou python init_db.py')
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for col, typedef in ARTIST_COLUMNS:
        if not column_exists(cur, 'artist', col):
            cur.execute(f'ALTER TABLE artist ADD COLUMN {col} {typedef}')
            print(f'  + artist.{col}')
        else:
            print(f'  = artist.{col} (já existe)')

    if table_exists(cur, 'brand_deal'):
        for col, typedef in BRAND_DEAL_COLUMNS:
            if not column_exists(cur, 'brand_deal', col):
                cur.execute(f'ALTER TABLE brand_deal ADD COLUMN {col} {typedef}')
                print(f'  + brand_deal.{col}')
            else:
                print(f'  = brand_deal.{col} (já existe)')
    else:
        print('  ! tabela brand_deal ausente — rode db.create_all()')

    new_tables = ['onboarding_template_task', 'financial_record']
    missing = [t for t in new_tables if not table_exists(cur, t)]
    conn.commit()
    conn.close()

    if missing:
        print(f'Criando tabelas via SQLAlchemy: {", ".join(missing)}')
        from app import create_app, db

        app = create_app()
        with app.app_context():
            db.create_all()
        print('  + tabelas criadas')
    else:
        print('  = onboarding_template_task e financial_record já existem')

    print('Migração Fase 2 concluída.')


if __name__ == '__main__':
    main()
