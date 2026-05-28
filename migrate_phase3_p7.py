"""
Migração Fase 3 — módulos P7, equipe e presença digital.
Execute: python migrate_phase3_p7.py
"""
import os
import sqlite3

DB_PATH = os.path.join('instance', 'artistas_sistema.db')

USER_COLUMNS = [
    ('display_name', 'VARCHAR(120)'),
    ('team_role', 'VARCHAR(40)'),
    ('phone', 'VARCHAR(20)'),
    ('is_active_user', 'BOOLEAN DEFAULT 1'),
]

NEW_TABLES = [
    'artist_contract',
    'onboarding_document',
    'rate_card_line',
    'dream_brand',
    'brand_partnership_history',
    'artist_goal',
    'artist_access',
    'artist_availability',
    'onboarding_meeting',
    'meeting_agenda_item',
    'digital_presence',
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
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for col, typedef in USER_COLUMNS:
        if not column_exists(cur, 'user', col):
            cur.execute(f'ALTER TABLE user ADD COLUMN {col} {typedef}')
            print(f'  + user.{col}')
        else:
            print(f'  = user.{col} (já existe)')

    conn.commit()
    conn.close()

    missing = []
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for t in NEW_TABLES:
        if not table_exists(cur, t):
            missing.append(t)
    conn.close()

    if missing:
        print(f'Criando tabelas: {", ".join(missing)}')
        from app import create_app, db

        app = create_app()
        with app.app_context():
            db.create_all()
        print('  + tabelas criadas')
    else:
        print('  = todas as tabelas P7 já existem')

    print('Migração Fase 3 concluída.')


if __name__ == '__main__':
    main()
