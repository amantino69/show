from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.finance import bp
from app import db
from app.models import Artist, BrandDeal, FinancialRecord


def _manager_required():
    if not current_user.is_manager:
        flash('Acesso restrito.', 'error')
        return False
    return True


def _parse_decimal(value):
    if not value:
        return None
    try:
        s = str(value).strip().replace('R$', '').replace(' ', '')
        if ',' in s:
            s = s.replace('.', '').replace(',', '.')
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _current_month():
    return datetime.now().strftime('%Y-%m')


@bp.route('/')
@login_required
def index():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    month = request.args.get('month', _current_month())
    records = (
        FinancialRecord.query.filter_by(reference_month=month)
        .order_by(FinancialRecord.created_at.desc())
        .all()
    )

    total_bruto = sum((r.amount or 0) for r in records)
    total_comissao = sum((r.commission_amount or 0) for r in records)
    fechamentos = [r for r in records if r.record_type == 'fechamento_marca' and r.payment_status == 'pago']
    mensalidades = [r for r in records if r.record_type == 'mensalidade']

    closed_deals = sum(
        1
        for d in BrandDeal.query.filter_by(status='fechado').all()
        if d.closed_at and d.closed_at.strftime('%Y-%m') == month
    )

    return render_template(
        'finance/index.html',
        records=records,
        month=month,
        total_bruto=total_bruto,
        total_comissao=total_comissao,
        fechamentos_count=len(fechamentos),
        mensalidades_count=len(mensalidades),
        closed_deals=closed_deals,
    )


@bp.route('/clientes')
@login_required
def clients():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    artists = Artist.query.filter(
        Artist.client_status.in_(['ativo', 'onboarding'])
    ).order_by(Artist.stage_name).all()
    return render_template('finance/clients.html', artists=artists)


@bp.route('/clientes/<int:artist_id>', methods=['GET', 'POST'])
@login_required
def client_detail(artist_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    artist = Artist.query.get_or_404(artist_id)

    if request.method == 'POST':
        artist.monthly_fee = _parse_decimal(request.form.get('monthly_fee'))
        artist.payment_due_day = request.form.get('payment_due_day', type=int)
        artist.payment_status = request.form.get('payment_status', 'em_dia')
        artist.current_phase = request.form.get('current_phase', '').strip() or None
        artist.strategic_manager = request.form.get('strategic_manager', '').strip() or None
        artist.operational_manager = request.form.get('operational_manager', '').strip() or None
        db.session.commit()
        flash('Dados financeiros do assessorado atualizados.', 'success')
        return redirect(url_for('finance.client_detail', artist_id=artist_id))

    records = FinancialRecord.query.filter_by(artist_id=artist_id).order_by(
        FinancialRecord.created_at.desc()
    ).limit(20).all()

    return render_template('finance/client_detail.html', artist=artist, records=records)


@bp.route('/mensalidade/<int:artist_id>', methods=['POST'])
@login_required
def register_monthly_fee(artist_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    artist = Artist.query.get_or_404(artist_id)
    amount = artist.monthly_fee or _parse_decimal(request.form.get('amount'))
    if not amount:
        flash('Defina o valor mensal do assessorado primeiro.', 'error')
        return redirect(url_for('finance.client_detail', artist_id=artist_id))

    month = request.form.get('reference_month', _current_month())
    rec = FinancialRecord(
        artist_id=artist_id,
        record_type='mensalidade',
        description=f'Mensalidade assessoria — {artist.stage_name}',
        amount=amount,
        reference_month=month,
        due_date=_parse_date(request.form.get('due_date')),
        payment_status=request.form.get('payment_status', 'pendente'),
    )
    db.session.add(rec)
    db.session.commit()
    flash('Mensalidade registrada.', 'success')
    return redirect(url_for('finance.index', month=month))


@bp.route('/registro/<int:record_id>/pago', methods=['POST'])
@login_required
def mark_paid(record_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    rec = FinancialRecord.query.get_or_404(record_id)
    rec.payment_status = 'pago'
    rec.paid_at = date.today()
    db.session.commit()
    flash('Marcado como pago.', 'success')
    return redirect(request.referrer or url_for('finance.index'))


@bp.route('/registro/<int:record_id>/excluir', methods=['POST'])
@login_required
def delete_record(record_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    rec = FinancialRecord.query.get_or_404(record_id)
    month = rec.reference_month or _current_month()
    db.session.delete(rec)
    db.session.commit()
    flash('Lançamento excluído.', 'success')
    return redirect(url_for('finance.index', month=month))


@bp.route('/sync-fechamentos', methods=['POST'])
@login_required
def sync_closed_deals():
    """Gera registros financeiros a partir de marcas fechadas no mês."""
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    month = request.form.get('month', _current_month())
    deals = BrandDeal.query.filter_by(status='fechado').all()
    added = 0
    for deal in deals:
        if not deal.closed_at or deal.closed_at.strftime('%Y-%m') != month:
            continue
        exists = FinancialRecord.query.filter_by(
            brand_deal_id=deal.id, record_type='fechamento_marca'
        ).first()
        if exists or not deal.value:
            continue
        rec = FinancialRecord(
            artist_id=deal.artist_id,
            brand_deal_id=deal.id,
            record_type='fechamento_marca',
            description=f'Fechamento — {deal.brand_name}',
            amount=deal.value,
            commission_rate=deal.commission_rate,
            commission_amount=deal.commission_amount,
            reference_month=month,
            payment_status='pendente',
        )
        db.session.add(rec)
        added += 1
    db.session.commit()
    flash(f'{added} fechamento(s) importado(s) do pipeline de marcas.', 'success')
    return redirect(url_for('finance.index', month=month))
