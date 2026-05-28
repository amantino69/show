# -*- coding: utf-8 -*-
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.devtools import bp
from app.delete_helpers import get_table_stats, purge_table, purge_all_test_data, TABLE_REGISTRY
from app.backup_service import create_backup, list_backups


def _manager_required():
    if not current_user.is_manager:
        flash('Acesso restrito à equipe.', 'error')
        return False
    return True


@bp.route('/dados-teste')
@login_required
def test_data_index():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    stats = get_table_stats()
    operational = [s for s in stats if s['group'] == 'operacional']
    config = [s for s in stats if s['group'] == 'config']
    total_operational = sum(s['count'] for s in operational)

    recent_backups = list_backups()[:8]

    return render_template(
        'devtools/test_data.html',
        operational=operational,
        config=config,
        total_operational=total_operational,
        recent_backups=recent_backups,
    )


@bp.route('/dados-teste/backup', methods=['POST'])
@login_required
def backup_before_test():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    try:
        info = create_backup(prefix='manual')
        flash(f'Backup salvo: {info["name"]}', 'success')
    except (FileNotFoundError, OSError) as exc:
        flash(f'Erro ao criar backup: {exc}', 'error')

    return redirect(url_for('devtools.test_data_index'))


def _maybe_backup(prefix='pre_limpeza'):
    """Cria backup se solicitado; retorna nome do arquivo ou None."""
    try:
        return create_backup(prefix=prefix)['name']
    except (FileNotFoundError, OSError):
        return None


@bp.route('/dados-teste/tabela/<table_key>/limpar', methods=['POST'])
@login_required
def purge_table_route(table_key):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    if table_key not in TABLE_REGISTRY:
        flash('Tabela inválida.', 'error')
        return redirect(url_for('devtools.test_data_index'))

    backup_name = None
    if request.form.get('auto_backup', 'on') == 'on':
        backup_name = _maybe_backup('pre_limpeza_tabela')

    deleted, err = purge_table(table_key, current_user.id)
    if err:
        db.session.rollback()
        flash(err, 'error')
    else:
        db.session.commit()
        label = TABLE_REGISTRY[table_key]['label']
        msg = f'{label}: {deleted} registro(s) removido(s).'
        if backup_name:
            msg += f' Backup: {backup_name}'
        flash(msg, 'success')

    return redirect(url_for('devtools.test_data_index'))


@bp.route('/dados-teste/limpar-tudo', methods=['POST'])
@login_required
def purge_all_route():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    include_config = request.form.get('include_config') == 'on'
    confirm = request.form.get('confirm_text', '').strip().upper()
    if confirm != 'LIMPAR':
        flash('Digite LIMPAR no campo de confirmação para prosseguir.', 'error')
        return redirect(url_for('devtools.test_data_index'))

    backup_name = None
    if request.form.get('auto_backup', 'on') == 'on':
        backup_name = _maybe_backup('pre_limpeza')

    results = purge_all_test_data(current_user.id, include_config=include_config)
    errors = [r for r in results if r['error']]
    if errors:
        db.session.rollback()
        flash(f'Interrompido em "{errors[0]["label"]}": {errors[0]["error"]}', 'error')
    else:
        total = sum(r['deleted'] for r in results)
        msg = f'Limpeza concluída: {total} registro(s) removidos no total.'
        if backup_name:
            msg += f' Backup: {backup_name}'
        flash(msg, 'success')

    return redirect(url_for('devtools.test_data_index'))
