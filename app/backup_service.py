# -*- coding: utf-8 -*-
"""Backup do banco SQLite."""
import os
import shutil
from datetime import datetime

from flask import current_app


def _project_root():
    return os.path.abspath(os.path.join(current_app.root_path, '..'))


def get_db_path():
    """Caminho absoluto do arquivo .db."""
    uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///artistas_sistema.db')
    if uri.startswith('sqlite:///'):
        rel = uri.replace('sqlite:///', '')
        if os.path.isabs(rel):
            return rel
        return os.path.join(_project_root(), 'instance', os.path.basename(rel))
    raise RuntimeError('Backup automático suportado apenas para SQLite.')


def get_backup_dir():
    path = os.path.join(_project_root(), 'backup_restore', 'backups')
    os.makedirs(path, exist_ok=True)
    return path


def list_backups():
    backup_dir = get_backup_dir()
    if not os.path.isdir(backup_dir):
        return []
    files = [
        f for f in os.listdir(backup_dir)
        if f.endswith('.db') and os.path.isfile(os.path.join(backup_dir, f))
    ]
    result = []
    for name in sorted(files, reverse=True):
        full = os.path.join(backup_dir, name)
        result.append({
            'name': name,
            'path': full,
            'size_mb': round(os.path.getsize(full) / (1024 * 1024), 2),
            'mtime': datetime.fromtimestamp(os.path.getmtime(full)),
        })
    return result


def create_backup(prefix='manual'):
    """
    Copia o banco para backup_restore/backups/.
    prefix: manual | auto | pre_limpeza
  """
    db_path = get_db_path()
    if not os.path.isfile(db_path):
        raise FileNotFoundError(f'Banco não encontrado: {db_path}')

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'artistas_sistema_{prefix}_{timestamp}.db'
    backup_path = os.path.join(get_backup_dir(), backup_name)
    shutil.copy2(db_path, backup_path)

    return {
        'name': backup_name,
        'path': backup_path,
        'created_at': datetime.now(),
    }
