#!/usr/bin/env python3
"""
Script para backup do banco de dados SQLite
"""
import shutil
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'artistas_sistema.db')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')
os.makedirs(BACKUP_DIR, exist_ok=True)

def backup():
    if not os.path.exists(DB_PATH):
        print('Banco de dados não encontrado!')
        return
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'artistas_sistema_backup_{timestamp}.db')
    shutil.copy2(DB_PATH, backup_file)
    print(f'Backup realizado com sucesso: {backup_file}')

if __name__ == '__main__':
    backup()
