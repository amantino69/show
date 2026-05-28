# -*- coding: utf-8 -*-
from datetime import date

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.p7 import bp
from app.p7.helpers import (
    get_artist_or_redirect,
    parse_decimal,
    parse_date,
    parse_int,
    ensure_contract_docs,
    ensure_media_materials,
    ensure_access_rows,
    ensure_weekly_availability,
    get_or_create_contract,
)
from app.models import (
    Artist,
    ArtistContract,
    OnboardingDocument,
    RateCardLine,
    DreamBrand,
    BrandPartnershipHistory,
    ArtistGoal,
    ArtistAccess,
    ArtistAvailability,
    OnboardingMeeting,
    MeetingAgendaItem,
    DigitalPresence,
    OnboardingTask,
    BrandDeal,
)


def _nav_context(artist, active):
    return {'artist': artist, 'active_tab': active}


@bp.route('/<int:artist_id>/gestao')
@login_required
def hub(artist_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir
    tasks_done = sum(
        1 for t in artist.onboarding_tasks if t.status == 'concluido'
    )
    tasks_total = len(artist.onboarding_tasks)
    return render_template(
        'p7/hub.html',
        artist=artist,
        tasks_done=tasks_done,
        tasks_total=tasks_total,
        dream_count=len(artist.dream_brands),
        dream_placeholders=sum(
            1 for d in artist.dream_brands if d.is_planilha_placeholder
        ),
        deals_open=BrandDeal.query.filter(
            BrandDeal.artist_id == artist_id,
            BrandDeal.status.in_(['prospeccao', 'proposta', 'negociacao']),
        ).count(),
    )


# --- Contrato ---
@bp.route('/<int:artist_id>/contrato', methods=['GET', 'POST'])
@login_required
def contrato(artist_id):
    artist, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir

    contract = get_or_create_contract(artist_id)
    ensure_contract_docs(artist_id)
    db.session.commit()

    if request.method == 'POST':
        if request.form.get('action') == 'contract':
            contract.contract_model = request.form.get('contract_model', '').strip() or None
            contract.signed_at = parse_date(request.form.get('signed_at'))
            contract.validity_end = parse_date(request.form.get('validity_end'))
            contract.service_format = request.form.get('service_format', '').strip() or None
            contract.monthly_value = parse_decimal(request.form.get('monthly_value'))
            contract.commission_pct = request.form.get('commission_pct', '').strip() or None
            contract.payment_method = request.form.get('payment_method', '').strip() or None
            contract.due_day = parse_int(request.form.get('due_day'))
            contract.exclusivity = request.form.get('exclusivity', '').strip() or None
            contract.notice_period = request.form.get('notice_period', '').strip() or None
            contract.forum = request.form.get('forum', '').strip() or None
            contract.brand_restrictions = request.form.get('brand_restrictions', '').strip() or None
            contract.notes = request.form.get('notes', '').strip() or None
            artist.monthly_fee = contract.monthly_value or artist.monthly_fee
            artist.payment_due_day = contract.due_day or artist.payment_due_day
            flash('Dados do contrato salvos.', 'success')
        elif request.form.get('action') == 'add_doc':
            title = request.form.get('title', '').strip()
            if title:
                db.session.add(
                    OnboardingDocument(
                        artist_id=artist_id,
                        doc_type='contract',
                        title=title,
                    )
                )
        elif request.form.get('action') == 'update_doc':
            doc = OnboardingDocument.query.get_or_404(
                request.form.get('doc_id', type=int)
            )
            doc.status = request.form.get('status', doc.status)
            doc.received = request.form.get('received') == 'on'
            doc.received_at = parse_date(request.form.get('received_at'))
            doc.notes = request.form.get('notes', '').strip() or None
        db.session.commit()
        return redirect(url_for('p7.contrato', artist_id=artist_id))

    docs = OnboardingDocument.query.filter_by(
        artist_id=artist_id, doc_type='contract'
    ).order_by(OnboardingDocument.sort_order).all()

    return render_template(
        'p7/contrato.html',
        **_nav_context(artist, 'contrato'),
        contract=contract,
        docs=docs,
    )


@bp.route('/<int:artist_id>/contrato/doc/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_contract_doc(artist_id, doc_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    doc = OnboardingDocument.query.filter_by(
        id=doc_id, artist_id=artist_id, doc_type='contract'
    ).first_or_404()
    db.session.delete(doc)
    db.session.commit()
    return redirect(url_for('p7.contrato', artist_id=artist_id))


# --- Mídia Kit ---
@bp.route('/<int:artist_id>/midia-kit', methods=['GET', 'POST'])
@login_required
def midia_kit(artist_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir
    if not current_user.is_manager:
        flash('Somente a equipe pode editar o mídia kit.', 'error')
        return redirect(url_for('p7.hub', artist_id=artist_id))

    ensure_media_materials(artist_id)
    db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add_rate':
            db.session.add(
                RateCardLine(
                    artist_id=artist_id,
                    platform=request.form.get('platform', '').strip() or None,
                    format_name=request.form.get('format_name', '').strip() or None,
                    description=request.form.get('description', '').strip() or None,
                    amount=parse_decimal(request.form.get('amount')),
                    is_combo=request.form.get('is_combo') == 'on',
                    includes_repost=request.form.get('includes_repost') == 'on',
                    delivery_days=parse_int(request.form.get('delivery_days')),
                    notes=request.form.get('notes', '').strip() or None,
                )
            )
        elif action == 'add_material':
            title = request.form.get('title', '').strip()
            if title:
                db.session.add(
                    OnboardingDocument(
                        artist_id=artist_id, doc_type='media', title=title
                    )
                )
        elif action == 'update_material':
            doc = OnboardingDocument.query.get_or_404(
                request.form.get('doc_id', type=int)
            )
            doc.status = request.form.get('status', doc.status)
            doc.responsible = request.form.get('responsible', '').strip() or None
            doc.received_at = parse_date(request.form.get('received_at'))
            doc.notes = request.form.get('notes', '').strip() or None
        elif action == 'restrictions':
            contract = get_or_create_contract(artist_id)
            contract.brand_restrictions = request.form.get(
                'brand_restrictions', ''
            ).strip() or None
        db.session.commit()
        return redirect(url_for('p7.midia_kit', artist_id=artist_id))

    rates = RateCardLine.query.filter_by(artist_id=artist_id).order_by(
        RateCardLine.sort_order
    ).all()
    materials = OnboardingDocument.query.filter_by(
        artist_id=artist_id, doc_type='media'
    ).order_by(OnboardingDocument.sort_order).all()
    contract = ArtistContract.query.filter_by(artist_id=artist_id).first()

    return render_template(
        'p7/midia_kit.html',
        **_nav_context(artist, 'midia_kit'),
        rates=rates,
        materials=materials,
        restrictions=contract.brand_restrictions if contract else '',
    )


@bp.route('/<int:artist_id>/midia-kit/rate/<int:line_id>/delete', methods=['POST'])
@login_required
def delete_rate(artist_id, line_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    line = RateCardLine.query.filter_by(id=line_id, artist_id=artist_id).first_or_404()
    db.session.delete(line)
    db.session.commit()
    return redirect(url_for('p7.midia_kit', artist_id=artist_id))


# --- Marcas ---
@bp.route('/<int:artist_id>/marcas', methods=['GET', 'POST'])
@login_required
def marcas(artist_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir

    if request.method == 'POST' and current_user.is_manager:
        action = request.form.get('action')
        if action == 'add_dream':
            name = request.form.get('brand_name', '').strip()
            if name:
                db.session.add(
                    DreamBrand(
                        artist_id=artist_id,
                        brand_name=name,
                        segment=request.form.get('segment', '').strip() or None,
                        reason=request.form.get('reason', '').strip() or None,
                        known_contact=request.form.get('known_contact') == 'on',
                        status=request.form.get('status', 'lista'),
                        priority=parse_int(request.form.get('priority'), 5),
                        estimated_value=parse_decimal(
                            request.form.get('estimated_value')
                        ),
                        notes=request.form.get('notes', '').strip() or None,
                    )
                )
        elif action == 'add_history':
            name = request.form.get('brand_name', '').strip()
            if name:
                db.session.add(
                    BrandPartnershipHistory(
                        artist_id=artist_id,
                        brand_name=name,
                        segment=request.form.get('segment', '').strip() or None,
                        period=request.form.get('period', '').strip() or None,
                        format_name=request.form.get('format_name', '').strip() or None,
                        amount_received=parse_decimal(
                            request.form.get('amount_received')
                        ),
                        renewed=request.form.get('renewed') == 'on',
                        contact_name=request.form.get('contact_name', '').strip() or None,
                        notes=request.form.get('notes', '').strip() or None,
                    )
                )
        elif action == 'add_goal':
            text = request.form.get('goal_text', '').strip()
            if text:
                db.session.add(
                    ArtistGoal(
                        artist_id=artist_id,
                        period=request.form.get('period', '').strip() or None,
                        goal_text=text,
                        indicator=request.form.get('indicator', '').strip() or None,
                        target_value=request.form.get('target_value', '').strip() or None,
                        current_value=request.form.get('current_value', '').strip() or None,
                        deadline=parse_date(request.form.get('deadline')),
                        status=request.form.get('status', 'em_andamento'),
                        notes=request.form.get('notes', '').strip() or None,
                    )
                )
        elif action == 'bulk_rename_dreams':
            updated = 0
            for key in request.form:
                if not key.startswith('dream_name_'):
                    continue
                try:
                    dream_id = int(key.replace('dream_name_', ''))
                except ValueError:
                    continue
                new_name = request.form.get(key, '').strip()
                if not new_name:
                    continue
                dream = DreamBrand.query.filter_by(
                    id=dream_id, artist_id=artist_id
                ).first()
                if not dream:
                    continue
                dream.clear_placeholder_if_named(new_name)
                dream.brand_name = new_name
                seg_key = f'dream_segment_{dream_id}'
                if seg_key in request.form:
                    dream.segment = request.form.get(seg_key, '').strip() or None
                updated += 1
            flash(f'{updated} marca(s) atualizada(s).', 'success')
        elif action == 'update_dream':
            dream_id = request.form.get('dream_id', type=int)
            new_name = request.form.get('brand_name', '').strip()
            dream = DreamBrand.query.filter_by(
                id=dream_id, artist_id=artist_id
            ).first_or_404()
            if new_name:
                dream.clear_placeholder_if_named(new_name)
                dream.brand_name = new_name
            dream.segment = request.form.get('segment', '').strip() or None
            dream.status = request.form.get('status', dream.status)
            dream.priority = parse_int(request.form.get('priority'), dream.priority)
            dream.reason = request.form.get('reason', '').strip() or None
            dream.estimated_value = parse_decimal(request.form.get('estimated_value'))
            flash('Marca atualizada.', 'success')
        db.session.commit()
        return redirect(url_for('p7.marcas', artist_id=artist_id))

    dreams = DreamBrand.query.filter_by(artist_id=artist_id).order_by(
        DreamBrand.priority, DreamBrand.sort_order
    ).all()
    history = BrandPartnershipHistory.query.filter_by(artist_id=artist_id).all()
    goals = ArtistGoal.query.filter_by(artist_id=artist_id).all()

    placeholders = [d for d in dreams if d.is_planilha_placeholder]

    return render_template(
        'p7/marcas.html',
        **_nav_context(artist, 'marcas'),
        dreams=dreams,
        placeholders=placeholders,
        placeholder_count=len(placeholders),
        history=history,
        goals=goals,
        dream_statuses=DreamBrand.STATUS_LABELS,
        can_edit=current_user.is_manager,
    )


@bp.route('/<int:artist_id>/marcas/dream/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_dream(artist_id, item_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    item = DreamBrand.query.filter_by(id=item_id, artist_id=artist_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('p7.marcas', artist_id=artist_id))


# --- Acessos ---
@bp.route('/<int:artist_id>/acessos', methods=['GET', 'POST'])
@login_required
def acessos(artist_id):
    artist, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir

    ensure_access_rows(artist_id)
    db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update':
            acc = ArtistAccess.query.get_or_404(request.form.get('access_id', type=int))
            acc.username_email = request.form.get('username_email', '').strip() or None
            acc.access_secret = request.form.get('access_secret', '').strip() or None
            acc.shared_with = request.form.get('shared_with', '').strip() or None
            acc.status = request.form.get('status', 'ativo')
            acc.access_date = parse_date(request.form.get('access_date'))
            acc.notes = request.form.get('notes', '').strip() or None
        elif action == 'add':
            platform = request.form.get('platform', '').strip()
            if platform:
                db.session.add(ArtistAccess(artist_id=artist_id, platform=platform))
        db.session.commit()
        return redirect(url_for('p7.acessos', artist_id=artist_id))

    rows = ArtistAccess.query.filter_by(artist_id=artist_id).order_by(
        ArtistAccess.sort_order
    ).all()

    return render_template(
        'p7/acessos.html', **_nav_context(artist, 'acessos'), accesses=rows
    )


# --- Reunião ---
@bp.route('/<int:artist_id>/reuniao', methods=['GET', 'POST'])
@login_required
def reuniao(artist_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir

    if request.method == 'POST' and current_user.is_manager:
        action = request.form.get('action')
        if action == 'save_meeting':
            mid = request.form.get('meeting_id', type=int)
            if mid:
                meeting = OnboardingMeeting.query.filter_by(
                    id=mid, artist_id=artist_id
                ).first_or_404()
            else:
                meeting = OnboardingMeeting(artist_id=artist_id)
                db.session.add(meeting)
            meeting.meeting_date = parse_date(request.form.get('meeting_date'))
            meeting.meeting_time = request.form.get('meeting_time', '').strip() or None
            meeting.format_type = request.form.get('format_type', '').strip() or None
            meeting.participants = request.form.get('participants', '').strip() or None
            meeting.meeting_link = request.form.get('meeting_link', '').strip() or None
            meeting.notes = request.form.get('notes', '').strip() or None
            db.session.flush()
            if not mid:
                return redirect(
                    url_for('p7.reuniao', artist_id=artist_id, meeting_id=meeting.id)
                )
        elif action == 'add_agenda':
            meeting = OnboardingMeeting.query.filter_by(
                id=request.form.get('meeting_id', type=int), artist_id=artist_id
            ).first_or_404()
            topic = request.form.get('topic', '').strip()
            if topic:
                db.session.add(
                    MeetingAgendaItem(
                        meeting_id=meeting.id,
                        topic=topic,
                        responsible=request.form.get('responsible', '').strip() or None,
                    )
                )
        elif action == 'update_agenda':
            item = MeetingAgendaItem.query.get_or_404(
                request.form.get('item_id', type=int)
            )
            item.discussed = request.form.get('discussed') == 'on'
            item.decision = request.form.get('decision', '').strip() or None
            item.responsible = request.form.get('responsible', '').strip() or None
            item.notes = request.form.get('notes', '').strip() or None
        db.session.commit()
        return redirect(
            url_for(
                'p7.reuniao',
                artist_id=artist_id,
                meeting_id=request.form.get('meeting_id', type=int),
            )
        )

    meeting_id = request.args.get('meeting_id', type=int)
    meetings = OnboardingMeeting.query.filter_by(artist_id=artist_id).order_by(
        OnboardingMeeting.meeting_date.desc()
    ).all()
    current = None
    if meeting_id:
        current = OnboardingMeeting.query.filter_by(
            id=meeting_id, artist_id=artist_id
        ).first()
    elif meetings:
        current = meetings[0]

    return render_template(
        'p7/reuniao.html',
        **_nav_context(artist, 'reuniao'),
        meetings=meetings,
        meeting=current,
        can_edit=current_user.is_manager,
    )


@bp.route('/<int:artist_id>/reuniao/new', methods=['POST'])
@login_required
def new_meeting(artist_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    m = OnboardingMeeting(artist_id=artist_id, meeting_date=date.today())
    db.session.add(m)
    db.session.commit()
    return redirect(url_for('p7.reuniao', artist_id=artist_id, meeting_id=m.id))


# --- Rotina semanal ---
@bp.route('/<int:artist_id>/rotina', methods=['GET', 'POST'])
@login_required
def rotina(artist_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir

    ensure_weekly_availability(artist_id)
    db.session.commit()

    if request.method == 'POST':
        if not current_user.is_manager and current_user.artist_id != artist_id:
            flash('Sem permissão.', 'error')
            return redirect(url_for('p7.rotina', artist_id=artist_id))

        for slot in ArtistAvailability.query.filter_by(artist_id=artist_id).all():
            prefix = f'day_{slot.weekday}_'
            slot.is_available = request.form.get(prefix + 'available') == 'on'
            slot.start_time = request.form.get(prefix + 'start', '').strip() or None
            slot.end_time = request.form.get(prefix + 'end', '').strip() or None
            slot.recordings_ok = request.form.get(prefix + 'recordings') == 'on'
            slot.events_travel = request.form.get(prefix + 'travel', '').strip() or None
            slot.notes = request.form.get(prefix + 'notes', '').strip() or None
        db.session.commit()
        flash('Rotina semanal atualizada.', 'success')
        return redirect(url_for('p7.rotina', artist_id=artist_id))

    slots = ArtistAvailability.query.filter_by(artist_id=artist_id).order_by(
        ArtistAvailability.weekday
    ).all()

    return render_template(
        'p7/rotina.html',
        **_nav_context(artist, 'rotina'),
        slots=slots,
        weekdays=ArtistAvailability.WEEKDAYS,
        can_edit=current_user.is_manager or current_user.artist_id == artist_id,
    )


# --- Presença digital ---
@bp.route('/<int:artist_id>/presenca-digital', methods=['GET', 'POST'])
@login_required
def presenca_digital(artist_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir

    if request.method == 'POST':
        if not current_user.is_manager and current_user.artist_id != artist_id:
            flash('Sem permissão.', 'error')
            return redirect(url_for('p7.presenca_digital', artist_id=artist_id))

        action = request.form.get('action')
        if action == 'add':
            platform = request.form.get('platform', '').strip()
            if platform:
                db.session.add(
                    DigitalPresence(
                        artist_id=artist_id,
                        platform=platform,
                        username=request.form.get('username', '').strip() or None,
                        followers=parse_int(request.form.get('followers')),
                        engagement_pct=request.form.get('engagement_pct', '').strip() or None,
                        avg_reach=request.form.get('avg_reach', '').strip() or None,
                        main_audience=request.form.get('main_audience', '').strip() or None,
                        monthly_growth=request.form.get('monthly_growth', '').strip() or None,
                        notes=request.form.get('notes', '').strip() or None,
                    )
                )
        elif action == 'update':
            row = DigitalPresence.query.get_or_404(
                request.form.get('row_id', type=int)
            )
            row.username = request.form.get('username', '').strip() or None
            row.followers = parse_int(request.form.get('followers'))
            row.engagement_pct = request.form.get('engagement_pct', '').strip() or None
            row.avg_reach = request.form.get('avg_reach', '').strip() or None
            row.main_audience = request.form.get('main_audience', '').strip() or None
            row.monthly_growth = request.form.get('monthly_growth', '').strip() or None
            row.notes = request.form.get('notes', '').strip() or None
        db.session.commit()
        return redirect(url_for('p7.presenca_digital', artist_id=artist_id))

    rows = DigitalPresence.query.filter_by(artist_id=artist_id).order_by(
        DigitalPresence.platform
    ).all()

    return render_template(
        'p7/presenca.html',
        **_nav_context(artist, 'presenca'),
        rows=rows,
        can_edit=current_user.is_manager or current_user.artist_id == artist_id,
    )


@bp.route('/<int:artist_id>/presenca-digital/<int:row_id>/delete', methods=['POST'])
@login_required
def delete_presenca(artist_id, row_id):
    artist, redir = get_artist_or_redirect(artist_id)
    if redir:
        return redir
    if not current_user.is_manager and current_user.artist_id != artist_id:
        return redirect(url_for('main.dashboard'))
    row = DigitalPresence.query.filter_by(id=row_id, artist_id=artist_id).first_or_404()
    db.session.delete(row)
    db.session.commit()
    return redirect(url_for('p7.presenca_digital', artist_id=artist_id))


@bp.route('/<int:artist_id>/marcas/historico/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_partnership_history(artist_id, item_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    item = BrandPartnershipHistory.query.filter_by(id=item_id, artist_id=artist_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Histórico removido.', 'success')
    return redirect(url_for('p7.marcas', artist_id=artist_id))


@bp.route('/<int:artist_id>/marcas/meta/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_goal(artist_id, item_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    item = ArtistGoal.query.filter_by(id=item_id, artist_id=artist_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Meta removida.', 'success')
    return redirect(url_for('p7.marcas', artist_id=artist_id))


@bp.route('/<int:artist_id>/acessos/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_access(artist_id, item_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    item = ArtistAccess.query.filter_by(id=item_id, artist_id=artist_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Acesso removido.', 'success')
    return redirect(url_for('p7.acessos', artist_id=artist_id))


@bp.route('/<int:artist_id>/reuniao/<int:meeting_id>/delete', methods=['POST'])
@login_required
def delete_meeting(artist_id, meeting_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    meeting = OnboardingMeeting.query.filter_by(id=meeting_id, artist_id=artist_id).first_or_404()
    MeetingAgendaItem.query.filter_by(meeting_id=meeting.id).delete()
    db.session.delete(meeting)
    db.session.commit()
    flash('Reunião removida.', 'success')
    return redirect(url_for('p7.reuniao', artist_id=artist_id))


@bp.route('/<int:artist_id>/reuniao/agenda/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_agenda_item(artist_id, item_id):
    _, redir = get_artist_or_redirect(artist_id, manager_only=True)
    if redir:
        return redir
    item = MeetingAgendaItem.query.get_or_404(item_id)
    meeting = OnboardingMeeting.query.filter_by(
        id=item.meeting_id, artist_id=artist_id
    ).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Item da pauta removido.', 'success')
    return redirect(url_for('p7.reuniao', artist_id=artist_id, meeting_id=meeting.id))
