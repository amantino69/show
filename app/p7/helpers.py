# -*- coding: utf-8 -*-
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import flash, redirect, url_for
from flask_login import current_user

from app.models import (
    Artist,
    ArtistContract,
    OnboardingDocument,
    ArtistAvailability,
)

DEFAULT_CONTRACT_DOCS = [
    'Contrato PDF assinado',
    'RG ou CNH',
    'CPF',
    'Comprovante de residência',
    'Contrato social (se PJ)',
    'Comprovante de pagamento inicial',
]

DEFAULT_MEDIA_MATERIALS = [
    'PDF do mídia kit',
    'Fotos profissionais (mín. 5)',
    'Logo / marca pessoal',
    'Templates de stories',
    'Pitch deck (se aplicável)',
]

DEFAULT_ACCESS_PLATFORMS = [
    'E-mail Viezes',
    'WhatsApp Business',
    'Google Drive',
    'Trello',
    'Instagram Business',
    'TikTok',
    'YouTube Studio',
    'CRM Viezes',
    'Linktree',
    'Canva',
]


def parse_decimal(value):
    if not value:
        return None
    try:
        s = str(value).strip().replace('R$', '').replace(' ', '')
        if ',' in s:
            s = s.replace('.', '').replace(',', '.')
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None


def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def parse_int(value, default=None):
    if value is None or value == '':
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_artist_or_redirect(artist_id, manager_only=False):
    artist = Artist.query.get_or_404(artist_id)
    if manager_only and not current_user.is_manager:
        flash('Acesso restrito à equipe.', 'error')
        return None, redirect(url_for('main.dashboard'))
    if not current_user.is_manager and current_user.artist_id != artist_id:
        flash('Acesso negado.', 'error')
        return None, redirect(url_for('main.dashboard'))
    return artist, None


def ensure_contract_docs(artist_id):
    if OnboardingDocument.query.filter_by(artist_id=artist_id, doc_type='contract').first():
        return
    for i, title in enumerate(DEFAULT_CONTRACT_DOCS):
        from app import db
        db.session.add(
            OnboardingDocument(
                artist_id=artist_id,
                doc_type='contract',
                title=title,
                sort_order=i,
            )
        )


def ensure_media_materials(artist_id):
    if OnboardingDocument.query.filter_by(artist_id=artist_id, doc_type='media').first():
        return
    for i, title in enumerate(DEFAULT_MEDIA_MATERIALS):
        from app import db
        db.session.add(
            OnboardingDocument(
                artist_id=artist_id,
                doc_type='media',
                title=title,
                sort_order=i,
            )
        )


def ensure_access_rows(artist_id):
    from app import db
    from app.models import ArtistAccess

    if ArtistAccess.query.filter_by(artist_id=artist_id).first():
        return
    for i, platform in enumerate(DEFAULT_ACCESS_PLATFORMS):
        db.session.add(
            ArtistAccess(artist_id=artist_id, platform=platform, sort_order=i)
        )


def ensure_weekly_availability(artist_id):
    if ArtistAvailability.query.filter_by(artist_id=artist_id).first():
        return
    from app import db

    for weekday in range(7):
        db.session.add(
            ArtistAvailability(
                artist_id=artist_id,
                weekday=weekday,
                is_available=weekday < 5,
                start_time='09:00',
                end_time='18:00',
            )
        )


def get_or_create_contract(artist_id):
    c = ArtistContract.query.filter_by(artist_id=artist_id).first()
    if not c:
        from app import db
        c = ArtistContract(artist_id=artist_id)
        db.session.add(c)
        db.session.flush()
    return c
