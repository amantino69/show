"""Adiciona tabela catalog_item e FKs em lead/artist. Execute: python migrate_catalog.py"""
import os
import sqlite3

DB_PATH = os.path.join('instance', 'artistas_sistema.db')

LEAD_COLS = [
    ('segment_id', 'INTEGER'),
    ('service_type_id', 'INTEGER'),
    ('lead_source_id', 'INTEGER'),
]
ARTIST_COLS = [('service_type_id', 'INTEGER')]


def column_exists(cur, table, col):
    cur.execute(f'PRAGMA table_info({table})')
    return any(r[1] == col for r in cur.fetchall())


def table_exists(cur, name):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,))
    return cur.fetchone() is not None


def main():
    if not os.path.exists(DB_PATH):
        print('Banco não encontrado. Rode app.py ou init_db.py primeiro.')
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if not table_exists(cur, 'catalog_item'):
        print('Tabela catalog_item será criada via db.create_all()...')
        from app import create_app, db
        app = create_app()
        with app.app_context():
            db.create_all()
        print('  + catalog_item criada')
    else:
        print('  = catalog_item já existe')

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for col, typedef in LEAD_COLS:
        if not column_exists(cur, 'lead', col):
            cur.execute(f'ALTER TABLE lead ADD COLUMN {col} {typedef}')
            print(f'  + lead.{col}')
    for col, typedef in ARTIST_COLS:
        if not column_exists(cur, 'artist', col):
            cur.execute(f'ALTER TABLE artist ADD COLUMN {col} {typedef}')
            print(f'  + artist.{col}')

    conn.commit()
    conn.close()
    print('Migração de cadastros concluída. Execute: python seed_catalogs.py')


if __name__ == '__main__':
    main()
