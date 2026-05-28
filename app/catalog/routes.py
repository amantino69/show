from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from app.catalog import bp
from app import db
from app.models import CatalogItem, Lead


def _manager_required():
    if not current_user.is_manager:
        flash('Acesso restrito à equipe da assessoria.', 'error')
        return False
    return True


def _valid_category(category):
    if category not in CatalogItem.CATEGORIES:
        abort(404)
    return category


@bp.route('/')
@login_required
def index():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    categories = []
    for key, label in CatalogItem.CATEGORIES.items():
        count = CatalogItem.query.filter_by(category=key, is_active=True).count()
        categories.append({'key': key, 'label': label, 'count': count})

    return render_template('catalog/index.html', categories=categories)


@bp.route('/<category>')
@login_required
def list_items(category):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))
    category = _valid_category(category)

    items = (
        CatalogItem.query.filter_by(category=category)
        .order_by(CatalogItem.sort_order, CatalogItem.name)
        .all()
    )
    return render_template(
        'catalog/list.html',
        category=category,
        category_label=CatalogItem.CATEGORIES[category],
        items=items,
    )


@bp.route('/<category>/new', methods=['GET', 'POST'])
@login_required
def new_item(category):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))
    category = _valid_category(category)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Informe o nome.', 'error')
            return render_template('catalog/form.html', item=None, category=category)

        if CatalogItem.query.filter_by(category=category, name=name).first():
            flash('Já existe um item com este nome.', 'error')
            return render_template('catalog/form.html', item=None, category=category)

        slug = request.form.get('slug', '').strip().lower() or None
        item = CatalogItem(
            category=category,
            name=name,
            slug=slug,
            sort_order=request.form.get('sort_order', type=int) or 0,
            is_active=request.form.get('is_active') == 'on',
        )
        db.session.add(item)
        db.session.commit()
        flash('Cadastro incluído.', 'success')
        return redirect(url_for('catalog.list_items', category=category))

    return render_template('catalog/form.html', item=None, category=category)


@bp.route('/<category>/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(category, item_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))
    category = _valid_category(category)
    item = CatalogItem.query.filter_by(id=item_id, category=category).first_or_404()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Informe o nome.', 'error')
            return render_template('catalog/form.html', item=item, category=category)

        dup = CatalogItem.query.filter(
            CatalogItem.category == category,
            CatalogItem.name == name,
            CatalogItem.id != item.id,
        ).first()
        if dup:
            flash('Já existe outro item com este nome.', 'error')
            return render_template('catalog/form.html', item=item, category=category)

        item.name = name
        item.slug = request.form.get('slug', '').strip().lower() or None
        item.sort_order = request.form.get('sort_order', type=int) or 0
        item.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        flash('Cadastro atualizado.', 'success')
        return redirect(url_for('catalog.list_items', category=category))

    return render_template('catalog/form.html', item=item, category=category)


@bp.route('/<category>/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(category, item_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))
    category = _valid_category(category)
    item = CatalogItem.query.filter_by(id=item_id, category=category).first_or_404()

    in_use = Lead.query.filter(
        (Lead.segment_id == item.id)
        | (Lead.service_type_id == item.id)
        | (Lead.lead_source_id == item.id)
    ).first()
    if in_use:
        item.is_active = False
        db.session.commit()
        flash('Item em uso — foi desativado em vez de excluído.', 'warning')
    else:
        db.session.delete(item)
        db.session.commit()
        flash('Cadastro removido.', 'success')

    return redirect(url_for('catalog.list_items', category=category))
