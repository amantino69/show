from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app.crm import bp
from app import db
from app.models import Lead, BrandDeal, Artist, ArtistType, User, CatalogItem, FinancialRecord
from app.catalog.helpers import get_active_items, apply_lead_catalog_from_form
from app.onboarding_service import apply_template_to_artist
from app.delete_helpers import delete_lead_record
from config import Config


def _deal_form_context(deal=None):
    return {
        'deal': deal,
        'artists': Artist.query.filter_by(is_active=True).order_by(Artist.stage_name).all(),
        'statuses': BrandDeal.STATUS_LABELS,
    }


def _lead_form_context(lead=None):
    return {
        'lead': lead,
        'statuses': Lead.STATUS_LABELS,
        'segments': get_active_items('segment'),
        'service_types': get_active_items('service_type'),
        'lead_sources': get_active_items('lead_source'),
    }


def _manager_required():
    if not current_user.is_manager:
        flash('Acesso restrito à equipe da assessoria.', 'error')
        return False
    return True


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _parse_decimal(value):
    if not value:
        return None
    try:
        cleaned = str(value).strip().replace('R$', '').replace(' ', '')
        if ',' in cleaned:
            cleaned = cleaned.replace('.', '').replace(',', '.')
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


@bp.route('/')
@login_required
def index():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    status_filter = request.args.get('status', '')
    query = Lead.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    leads = query.order_by(Lead.updated_at.desc()).all()

    counts = {s: Lead.query.filter_by(status=s).count() for s in Lead.STATUS_LABELS}
    open_leads = Lead.query.filter(Lead.closed.is_(False), Lead.status != 'perdido').count()

    return render_template(
        'crm/index.html',
        leads=leads,
        counts=counts,
        status_filter=status_filter,
        statuses=Lead.STATUS_LABELS,
        open_leads=open_leads,
    )


@bp.route('/leads/new', methods=['GET', 'POST'])
@login_required
def new_lead():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Informe o nome do lead.', 'error')
            return render_template('crm/lead_form.html', **_lead_form_context())

        lead = Lead(
            name=name,
            social_handle=request.form.get('social_handle', '').strip() or None,
            first_contact_date=_parse_date(request.form.get('first_contact_date')),
            diagnostic_date=_parse_date(request.form.get('diagnostic_date')),
            status=request.form.get('status', 'novo'),
            closed=request.form.get('closed') == 'on',
            value=_parse_decimal(request.form.get('value')),
            lost_reason=request.form.get('lost_reason', '').strip() or None,
            next_action=request.form.get('next_action', '').strip() or None,
            follow_up_date=_parse_date(request.form.get('follow_up_date')),
            notes=request.form.get('notes', '').strip() or None,
        )
        apply_lead_catalog_from_form(lead, request.form)
        db.session.add(lead)
        db.session.commit()
        flash('Lead cadastrado com sucesso.', 'success')
        return redirect(url_for('crm.index'))

    return render_template('crm/lead_form.html', **_lead_form_context())


@bp.route('/leads/<int:lead_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lead(lead_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    lead = Lead.query.get_or_404(lead_id)

    if request.method == 'POST':
        lead.name = request.form.get('name', '').strip()
        if not lead.name:
            flash('Informe o nome do lead.', 'error')
            return render_template('crm/lead_form.html', **_lead_form_context(lead))

        lead.social_handle = request.form.get('social_handle', '').strip() or None
        apply_lead_catalog_from_form(lead, request.form)
        lead.first_contact_date = _parse_date(request.form.get('first_contact_date'))
        lead.diagnostic_date = _parse_date(request.form.get('diagnostic_date'))
        lead.status = request.form.get('status', lead.status)
        lead.closed = request.form.get('closed') == 'on'
        lead.value = _parse_decimal(request.form.get('value'))
        lead.lost_reason = request.form.get('lost_reason', '').strip() or None
        lead.next_action = request.form.get('next_action', '').strip() or None
        lead.follow_up_date = _parse_date(request.form.get('follow_up_date'))
        lead.notes = request.form.get('notes', '').strip() or None
        db.session.commit()
        flash('Lead atualizado.', 'success')
        return redirect(url_for('crm.index'))

    return render_template('crm/lead_form.html', **_lead_form_context(lead))


@bp.route('/leads/<int:lead_id>/delete', methods=['POST'])
@login_required
def delete_lead(lead_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    lead = Lead.query.get_or_404(lead_id)
    name = lead.name
    delete_lead_record(lead)
    db.session.commit()
    flash(f'Lead "{name}" excluído. O assessorado vinculado (se houver) foi mantido.', 'success')
    return redirect(url_for('crm.index'))


@bp.route('/leads/<int:lead_id>/convert', methods=['POST'])
@login_required
def convert_lead(lead_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    lead = Lead.query.get_or_404(lead_id)
    if lead.artist_id:
        flash('Este lead já foi convertido em assessorado.', 'info')
        return redirect(url_for('main.artist_detail', artist_id=lead.artist_id))

    artist_type = ArtistType.query.first()
    if not artist_type:
        flash('Cadastre ao menos um tipo de artista antes de converter.', 'error')
        return redirect(url_for('crm.edit_lead', lead_id=lead.id))

    stage_name = lead.name.split()[0] if lead.name else f'lead{lead.id}'
    base_username = stage_name.lower().replace(' ', '_')[:40]
    username = base_username
    counter = 1
    while User.query.filter_by(username=username).first():
        username = f'{base_username}_{counter}'
        counter += 1

    email = f'{username}@show.local'
    if Artist.query.filter_by(email=email).first():
        email = f'{username}{lead.id}@show.local'

    colors = Config.ARTIST_COLORS
    color = colors[lead.id % len(colors)]

    artist = Artist(
        name=lead.name,
        stage_name=stage_name,
        email=email,
        artist_type_id=artist_type.id,
        color=color,
        client_status='onboarding',
        service_type_id=lead.service_type_id,
        service_type=lead.service_type,
        instagram=lead.social_handle,
        onboarding_progress=0,
        lead_id=lead.id,
    )
    db.session.add(artist)
    db.session.flush()

    default_password = stage_name.lower().replace(' ', '') + '123'
    user = User(
        username=username,
        email=email,
        is_manager=False,
        artist_id=artist.id,
    )
    user.set_password(default_password)
    db.session.add(user)

    apply_template_to_artist(artist.id, replace=False)

    lead.artist_id = artist.id
    lead.converted_at = datetime.utcnow()
    lead.status = 'fechado'
    lead.closed = True
    db.session.commit()

    flash(
        f'Assessorado criado! Login: {username} / {default_password} — status: Onboarding.',
        'success',
    )
    return redirect(url_for('main.artist_detail', artist_id=artist.id))


@bp.route('/deals')
@login_required
def deals():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    status_filter = request.args.get('status', '')
    artist_id = request.args.get('artist_id', type=int)

    query = BrandDeal.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if artist_id:
        query = query.filter_by(artist_id=artist_id)

    deals_list = query.order_by(BrandDeal.updated_at.desc()).all()
    open_deals = BrandDeal.query.filter(
        BrandDeal.status.in_(['prospeccao', 'proposta', 'negociacao'])
    ).count()

  # pipeline columns for kanban view
    pipeline = {s: [] for s in BrandDeal.STATUS_LABELS}
    for d in BrandDeal.query.order_by(BrandDeal.updated_at.desc()).all():
        pipeline.setdefault(d.status, []).append(d)

    artists = Artist.query.filter_by(is_active=True).order_by(Artist.stage_name).all()

    return render_template(
        'crm/deals.html',
        deals=deals_list,
        open_deals=open_deals,
        pipeline=pipeline,
        statuses=BrandDeal.STATUS_LABELS,
        status_filter=status_filter,
        artist_filter=artist_id,
        artists=artists,
    )


@bp.route('/deals/new', methods=['GET', 'POST'])
@login_required
def new_deal():
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    artists = Artist.query.filter_by(is_active=True).order_by(Artist.stage_name).all()

    if request.method == 'POST':
        artist_id = request.form.get('artist_id', type=int)
        brand_name = request.form.get('brand_name', '').strip()
        if not artist_id or not brand_name:
            flash('Selecione o assessorado e informe a marca.', 'error')
            return render_template('crm/deal_form.html', **_deal_form_context())

        deal = BrandDeal(
            artist_id=artist_id,
            brand_name=brand_name,
            contact_name=request.form.get('contact_name', '').strip() or None,
            brand_segment=request.form.get('brand_segment', '').strip() or None,
            status=request.form.get('status', 'prospeccao'),
            value=_parse_decimal(request.form.get('value')),
            commission_origin=request.form.get('commission_origin', 'proprio'),
            next_action=request.form.get('next_action', '').strip() or None,
            follow_up_date=_parse_date(request.form.get('follow_up_date')),
            notes=request.form.get('notes', '').strip() or None,
        )
        if deal.status == 'fechado':
            deal.closed_at = datetime.utcnow()
        db.session.add(deal)
        db.session.flush()
        _maybe_create_financial_from_deal(deal)
        db.session.commit()
        flash('Proposta cadastrada no pipeline de marcas.', 'success')
        return redirect(url_for('crm.deals'))

    return render_template('crm/deal_form.html', **_deal_form_context())


def _maybe_create_financial_from_deal(deal):
    if deal.status != 'fechado' or not deal.value:
        return
    exists = FinancialRecord.query.filter_by(
        brand_deal_id=deal.id, record_type='fechamento_marca'
    ).first()
    if exists:
        return
    month = (deal.closed_at or datetime.utcnow()).strftime('%Y-%m')
    db.session.add(
        FinancialRecord(
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
    )


@bp.route('/deals/<int:deal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deal(deal_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))

    deal = BrandDeal.query.get_or_404(deal_id)

    if request.method == 'POST':
        deal.artist_id = request.form.get('artist_id', type=int) or deal.artist_id
        deal.brand_name = request.form.get('brand_name', '').strip()
        deal.contact_name = request.form.get('contact_name', '').strip() or None
        deal.brand_segment = request.form.get('brand_segment', '').strip() or None
        old_status = deal.status
        deal.status = request.form.get('status', deal.status)
        deal.value = _parse_decimal(request.form.get('value'))
        deal.commission_origin = request.form.get('commission_origin', 'proprio')
        deal.next_action = request.form.get('next_action', '').strip() or None
        deal.follow_up_date = _parse_date(request.form.get('follow_up_date'))
        deal.notes = request.form.get('notes', '').strip() or None
        if deal.status == 'fechado' and old_status != 'fechado':
            deal.closed_at = datetime.utcnow()
        elif deal.status != 'fechado':
            deal.closed_at = None
        _maybe_create_financial_from_deal(deal)
        db.session.commit()
        flash('Proposta atualizada.', 'success')
        return redirect(url_for('crm.deals'))

    return render_template('crm/deal_form.html', **_deal_form_context(deal))


@bp.route('/deals/<int:deal_id>/delete', methods=['POST'])
@login_required
def delete_deal(deal_id):
    if not _manager_required():
        return redirect(url_for('main.dashboard'))
    deal = BrandDeal.query.get_or_404(deal_id)
    FinancialRecord.query.filter_by(brand_deal_id=deal.id).delete()
    db.session.delete(deal)
    db.session.commit()
    flash('Proposta removida do pipeline.', 'success')
    return redirect(url_for('crm.deals'))
