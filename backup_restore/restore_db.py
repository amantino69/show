#!/usr/bin/env python3
"""
Script para restaurar o banco de dados SQLite a partir de um backup
"""
import shutil
import os
import sys

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'instance', 'artistas_sistema.db')
BACKUP_DIR = os.path.join(os.path.dirname(__file__), 'backups')

def restore(backup_file):
    backup_path = os.path.join(BACKUP_DIR, backup_file)
    if not os.path.exists(backup_path):
        print('Arquivo de backup não encontrado!')
        return
    shutil.copy2(backup_path, DB_PATH)
    print(f'Banco restaurado com sucesso a partir de: {backup_path}')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Uso: python restore_db.py <nome_do_arquivo_de_backup>')
    else:
        restore(sys.argv[1])
