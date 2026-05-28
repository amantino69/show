# -*- coding: utf-8 -*-
"""Importadores das abas P7 — Contrato, Mídia Kit, Marcas, Acessos, Reunião."""
from __future__ import annotations

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from app import db
from app.models import (
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
)

WEEKDAY_MAP = {
    'segunda': 0, 'terça': 1, 'terca': 1, 'quarta': 2, 'quinta': 3,
    'sexta': 4, 'sábado': 5, 'sabado': 5, 'domingo': 6,
}

CONTRACT_LABELS = {
    'modelo de contrato': 'contract_model',
    'data de assinatura': 'signed_at',
    'vigência do contrato': 'validity_end',
    'vigência': 'validity_end',
    'formato da assessoria': 'service_format',
    'valor mensal': 'monthly_value',
    'comissão acordada': 'commission_pct',
    'comissão': 'commission_pct',
    'forma de pagamento': 'payment_method',
    'dia de vencimento': 'due_day',
    'cláusula de exclusividade': 'exclusivity',
    'exclusividade': 'exclusivity',
    'prazo de aviso prévio': 'notice_period',
    'aviso prévio': 'notice_period',
    'foro eleito': 'forum',
    'foro': 'forum',
}

MEETING_LABELS = {
    'data da reunião': 'meeting_date',
    'data da reuniao': 'meeting_date',
    'horário': 'meeting_time',
    'horario': 'meeting_time',
    'formato': 'format_type',
    'participantes': 'participants',
    'link da reunião': 'meeting_link',
    'link da reuniao': 'meeting_link',
}


def _cell_str(v):
    if v is None:
        return ''
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).strip()


def _parse_date(v):
    if v is None or v == '':
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = _cell_str(v)
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except ValueError:
            continue
    return None


def _parse_decimal(v):
    if v is None or v == '':
        return None
    if isinstance(v, (int, float, Decimal)):
        return Decimal(str(v))
    s = _cell_str(v).replace('R$', '').replace(' ', '')
    if not s or s in ('—', '-'):
        return None
    if ',' in s:
        s = s.replace('.', '').replace(',', '.')
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _norm_status(raw: str) -> str:
    s = _cell_str(raw).lower()
    if 'conclu' in s:
        return 'concluido'
    if 'andamento' in s:
        return 'em_andamento'
    if 'nao' in s and 'inici' in s:
        return 'nao_iniciado'
    return 'pendente'


def _label_val(row):
    cells = list(row) if row else []
    while cells and cells[0] is None:
        cells = cells[1:]
    if not cells:
        return '', ''
    label = _cell_str(cells[0])
    val = _cell_str(cells[1]) if len(cells) > 1 else ''
    if not val and len(cells) > 2:
        val = _cell_str(cells[2])
    return label, val


def _row_offset(row):
    """Planilhas P7: coluna A vazia ('' ou None) → dados começam em B (índice 1)."""
    if not row:
        return 0
    if len(row) > 1 and (row[0] is None or _cell_str(row[0]) == ''):
        return 1
    return 0


def _cell(row, index, default=''):
    if not row or index >= len(row):
        return default
    return _cell_str(row[index])


def _received_bool(val):
    s = _cell_str(val).lower()
    return s in ('sim', 's', 'yes', '1', 'true', 'x', 'ok', 'recebido')


def _parse_followers(val):
    """Ex.: 12800, 12.8 (milhares), 1.2k, 850000."""
    s = _cell_str(val).lower().replace(',', '.').replace(' ', '')
    if not s:
        return None
    mult = 1
    if s.endswith('k'):
        mult = 1000
        s = s[:-1]
    elif s.endswith('m'):
        mult = 1_000_000
        s = s[:-1]
    try:
        num = float(s)
    except ValueError:
        return None
    if mult == 1 and num < 1000 and '.' in s:
        num *= 1000
    return int(num)


def _parse_int(val, default=5):
    if val is None or _cell_str(val) == '':
        return default
    try:
        return int(float(_cell_str(val)))
    except (ValueError, TypeError):
        return default


def _is_section(label):
    if not label:
        return True
    return label.startswith('  ') or label.endswith(':')


def import_p7_extended(artist, sheet_rows_fn, stats):
    path = stats.get('_p7_path')
    if not path:
        return
    import_contract_sheet(artist, sheet_rows_fn(path, 'Contrato', 120), stats)
    import_midiakit_sheet(artist, sheet_rows_fn(path, 'MidiaKit', 120), stats)
    import_marcas_sheet(artist, sheet_rows_fn(path, 'Marcas', 120), stats)
    import_acessos_sheet(artist, sheet_rows_fn(path, 'Acessos', 120), stats)
    import_reuniao_sheet(artist, sheet_rows_fn(path, 'Reuniao', 120), stats)
    import_perfil_digital(artist, sheet_rows_fn(path, 'Perfil', 120), stats)
    profile = stats.get('profile') or {}
    sync_digital_from_profile(artist, profile, stats)


def ensure_dream_brand_slots(artist, min_slots=10):
    """Garante 10 linhas na lista de marcas dos sonhos (planilha TOP 10)."""
    existing = DreamBrand.query.filter_by(artist_id=artist.id).order_by(
        DreamBrand.sort_order
    ).all()
    used_orders = {d.sort_order for d in existing}
    added = 0
    for slot in range(1, min_slots + 1):
        if slot in used_orders:
            continue
        db.session.add(
            DreamBrand(
                artist_id=artist.id,
                brand_name=f'Marca {slot} (a definir)',
                status='lista',
                priority=slot,
                sort_order=slot,
                notes='Pré-cadastro importado da planilha — preencha o nome da marca',
            )
        )
        added += 1
    return added


def sync_digital_from_profile(artist, profile, stats):
    """Sincroniza Instagram/TikTok/YouTube do Perfil e da ficha Arché → presença digital."""
    channels = []
    metrics = profile.get('instagram_metrics') or {}
    if isinstance(metrics, dict) and metrics.get('handle'):
        channels.append(
            {
                'platform': 'Instagram',
                'username': metrics.get('handle'),
                'followers': metrics.get('followers'),
            }
        )

    data = profile if isinstance(profile, dict) else {}
    mapping = [
        ('Instagram', data.get('instagram') or data.get('seguidores_ig'), data.get('seguidores_ig')),
        ('TikTok', data.get('tiktok') or data.get('seguidores_tiktok'), data.get('seguidores_tiktok')),
        ('YouTube', data.get('youtube'), None),
    ]
    for platform, handle, followers_hint in mapping:
        if not handle and not followers_hint:
            continue
        channels.append(
            {
                'platform': platform,
                'username': handle,
                'followers': followers_hint,
            }
        )

    # dedupe por plataforma
    seen = set()
    unique = []
    for ch in channels:
        key = ch['platform'].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(ch)

    synced = 0
    for ch in unique:
        platform = ch['platform']
        row_obj = DigitalPresence.query.filter_by(
            artist_id=artist.id, platform=platform
        ).first()
        if not row_obj:
            row_obj = DigitalPresence(artist_id=artist.id, platform=platform)
            db.session.add(row_obj)
            synced += 1
        if ch.get('username'):
            handle = _cell_str(ch['username'])
            if not handle.startswith('@') and platform == 'Instagram':
                handle = f'@{handle.lstrip("@")}'
            row_obj.username = handle
            if platform == 'Instagram' and handle:
                artist.instagram = handle[:120]
        if ch.get('followers'):
            f = _parse_followers(ch['followers'])
            if f:
                row_obj.followers = f
        if platform == 'Instagram' and data.get('engajamento'):
            row_obj.engagement_pct = _cell_str(data.get('engajamento'))[:20]

    stats['p7_digital_synced'] = synced
    stats['p7_digital_total'] = DigitalPresence.query.filter_by(artist_id=artist.id).count()


def import_contract_sheet(artist, rows, stats):
    contract = ArtistContract.query.filter_by(artist_id=artist.id).first()
    if not contract:
        contract = ArtistContract(artist_id=artist.id)
        db.session.add(contract)

    in_docs = False
    doc_count = 0
    OnboardingDocument.query.filter_by(artist_id=artist.id, doc_type='contract').delete()

    for row in rows:
        label, val = _label_val(row)
        if not label:
            continue
        lu = label.upper()
        if 'CHECKLIST DOCUMENTAL' in lu:
            in_docs = True
            continue

        if in_docs:
            off = _row_offset(row)
            c0 = _cell_str(row[off] if len(row) > off else '')
            if not re.match(r'^[\d.]+$', c0):
                continue
            title = _cell_str(row[off + 2]) if len(row) > off + 2 else ''
            if not title or title.upper() == 'DOCUMENTO':
                continue
            doc_count += 1
            db.session.add(
                OnboardingDocument(
                    artist_id=artist.id,
                    doc_type='contract',
                    title=title,
                    status=_norm_status(_cell_str(row[off + 1]) if len(row) > off + 1 else ''),
                    received=_received_bool(row[off + 3]) if len(row) > off + 3 else False,
                    received_at=_parse_date(row[off + 4]) if len(row) > off + 4 else None,
                    notes=_cell_str(row[off + 5]) if len(row) > off + 5 else None,
                    sort_order=doc_count,
                )
            )
            continue

        norm = label.lower().strip()
        for pattern, attr in CONTRACT_LABELS.items():
            if pattern in norm:
                if attr in ('signed_at', 'validity_end'):
                    setattr(contract, attr, _parse_date(val))
                elif attr == 'monthly_value':
                    v = _parse_decimal(val)
                    setattr(contract, attr, v)
                    if v:
                        artist.monthly_fee = v
                elif attr == 'due_day':
                    d = _parse_int(val, None)
                    if d is not None:
                        contract.due_day = d
                        artist.payment_due_day = d
                else:
                    setattr(contract, attr, val or None)
                break

    stats['p7_contract_docs'] = doc_count


def import_midiakit_sheet(artist, rows, stats):
    mode = None
    rate_count = mat_count = 0
    restrictions = []

    RateCardLine.query.filter_by(artist_id=artist.id).delete()
    OnboardingDocument.query.filter_by(artist_id=artist.id, doc_type='media').delete()

    for row in rows:
        line = ' '.join(_cell_str(c) for c in row if c).upper()
        if not line:
            continue
        if 'TABELA DE VALORES' in line:
            mode = 'rates'
            continue
        if 'CHECKLIST DE MATERIAIS' in line or (
            'MATERIAL' in line and 'STATUS' in line and 'RESPONS' in line
        ):
            mode = 'materials'
            continue
        if 'RESTRIÇÕES DE MARCA' in line or 'RESTRICOES DE MARCA' in line:
            mode = 'restrictions'
            continue

        off = _row_offset(row)

        if mode == 'rates':
            platform = _cell_str(row[off]) if len(row) > off else ''
            fmt = _cell_str(row[off + 1]) if len(row) > off + 1 else ''
            if not platform or platform.upper() in ('PLATAFORMA', '#'):
                continue
            if not fmt:
                continue
            rate_count += 1
            db.session.add(
                RateCardLine(
                    artist_id=artist.id,
                    platform=platform,
                    format_name=fmt,
                    description=_cell_str(row[off + 2]) if len(row) > off + 2 else None,
                    amount=_parse_decimal(row[off + 3]) if len(row) > off + 3 else None,
                    is_combo=_received_bool(row[off + 4]) if len(row) > off + 4 else False,
                    includes_repost=_received_bool(row[off + 5]) if len(row) > off + 5 else False,
                    delivery_days=_parse_int(row[off + 6], None) if len(row) > off + 6 else None,
                    notes=_cell_str(row[off + 7]) if len(row) > off + 7 else None,
                    sort_order=rate_count,
                )
            )
            continue

        if mode == 'materials':
            c0 = _cell_str(row[off] if len(row) > off else '')
            if not re.match(r'^[\d.]+$', c0):
                continue
            title = _cell_str(row[off + 2]) if len(row) > off + 2 else ''
            if not title or title.upper() == 'MATERIAL':
                continue
            mat_count += 1
            db.session.add(
                OnboardingDocument(
                    artist_id=artist.id,
                    doc_type='media',
                    title=title,
                    status=_norm_status(_cell_str(row[off + 1]) if len(row) > off + 1 else ''),
                    responsible=_cell_str(row[off + 3]) if len(row) > off + 3 else None,
                    received_at=_parse_date(row[off + 4]) if len(row) > off + 4 else None,
                    sort_order=mat_count,
                )
            )
            continue

        if mode == 'restrictions':
            label, val = _label_val(row)
            if val:
                restrictions.append(val)
            elif label and not _is_section(label):
                restrictions.append(label)

    if restrictions:
        contract = ArtistContract.query.filter_by(artist_id=artist.id).first()
        if not contract:
            contract = ArtistContract(artist_id=artist.id)
            db.session.add(contract)
        contract.brand_restrictions = '\n'.join(restrictions)

    stats['p7_rate_lines'] = rate_count
    stats['p7_media_materials'] = mat_count


def import_marcas_sheet(artist, rows, stats):
    mode = None
    dream_n = hist_n = goal_n = 0

    DreamBrand.query.filter_by(artist_id=artist.id).delete()
    BrandPartnershipHistory.query.filter_by(artist_id=artist.id).delete()
    ArtistGoal.query.filter_by(artist_id=artist.id).delete()

    for row in rows:
        line = ' '.join(_cell_str(c) for c in row if c).upper()
        if 'MARCAS DOS SONHOS' in line:
            mode = 'dreams'
            continue
        if 'MARCAS JÁ TRABALHADAS' in line or 'JA TRABALHADAS' in line:
            mode = 'history'
            continue
        if 'PERÍODO' in line and 'META' in line and 'INDICADOR' in line:
            mode = 'goals'
            continue
        if 'MARCA' in line and 'SEGMENTO' in line and 'MOTIVO' in line:
            mode = 'dreams'
            continue
        if 'MARCA' in line and ('ANO/PERÍODO' in line or 'ANO/PERIODO' in line):
            mode = 'history'
            continue

        off = _row_offset(row)
        c0 = _cell_str(row[off] if len(row) > off else '')

        if mode == 'dreams':
            slot_num = None
            if re.match(r'^[\d.]+$', c0):
                slot_num = int(float(c0))
                brand = _cell(row, off + 1)
                seg_i, mot_i, known_i, stat_i, pri_i, val_i, obs_i = 2, 3, 4, 5, 6, 7, 8
            else:
                brand = c0
                seg_i, mot_i, known_i, stat_i, pri_i, val_i, obs_i = 1, 2, 3, 4, 5, 6, 7
            if brand.upper() == 'MARCA':
                continue
            if not brand or re.match(r'^\d+\.?$', brand):
                if slot_num is None:
                    continue
                brand = f'Marca {slot_num} (a definir)'
            dream_n += 1
            priority = slot_num if slot_num else dream_n
            db.session.add(
                DreamBrand(
                    artist_id=artist.id,
                    brand_name=brand,
                    segment=_cell_str(row[off + seg_i]) if len(row) > off + seg_i else None,
                    reason=_cell_str(row[off + mot_i]) if len(row) > off + mot_i else None,
                    known_contact=_received_bool(row[off + known_i]) if len(row) > off + known_i else False,
                    status=_cell_str(row[off + stat_i]).lower() or 'lista' if len(row) > off + stat_i else 'lista',
                    priority=_parse_int(row[off + pri_i], priority) if len(row) > off + pri_i else priority,
                    estimated_value=_parse_decimal(row[off + val_i]) if len(row) > off + val_i else None,
                    notes=_cell_str(row[off + obs_i]) if len(row) > off + obs_i else None,
                    sort_order=dream_n,
                )
            )
            continue

        if mode == 'history':
            if re.match(r'^[\d.]+$', c0):
                brand = _cell_str(row[off + 1]) if len(row) > off + 1 else ''
                b = 2
            else:
                brand = c0
                b = 1
            if not brand or brand.upper() == 'MARCA' or re.match(r'^\d+\.$', brand):
                continue
            hist_n += 1
            db.session.add(
                BrandPartnershipHistory(
                    artist_id=artist.id,
                    brand_name=brand,
                    segment=_cell_str(row[off + b]) if len(row) > off + b else None,
                    period=_cell_str(row[off + b + 1]) if len(row) > off + b + 1 else None,
                    format_name=_cell_str(row[off + b + 2]) if len(row) > off + b + 2 else None,
                    amount_received=_parse_decimal(row[off + b + 3]) if len(row) > off + b + 3 else None,
                    renewed=_received_bool(row[off + b + 4]) if len(row) > off + b + 4 else False,
                    contact_name=_cell_str(row[off + b + 5]) if len(row) > off + b + 5 else None,
                    notes=_cell_str(row[off + b + 6]) if len(row) > off + b + 6 else None,
                )
            )
            continue

        if mode == 'goals':
            period = c0
            if not period or period.upper() in ('PERÍODO', 'PERIODO'):
                continue
            goal_text = _cell_str(row[off + 1]) if len(row) > off + 1 else ''
            if not goal_text or goal_text.upper() == 'META':
                continue
            goal_n += 1
            db.session.add(
                ArtistGoal(
                    artist_id=artist.id,
                    period=period,
                    goal_text=goal_text,
                    indicator=_cell_str(row[off + 2]) if len(row) > off + 2 else None,
                    target_value=_cell_str(row[off + 3]) if len(row) > off + 3 else None,
                    current_value=_cell_str(row[off + 4]) if len(row) > off + 4 else None,
                    deadline=_parse_date(row[off + 5]) if len(row) > off + 5 else None,
                    status=_cell_str(row[off + 6]).lower() or 'em_andamento' if len(row) > off + 6 else 'em_andamento',
                    notes=_cell_str(row[off + 7]) if len(row) > off + 7 else None,
                )
            )

    stats['p7_dream_brands'] = dream_n
    stats['p7_dream_slots_added'] = ensure_dream_brand_slots(artist, min_slots=10)
    stats['p7_partnership_history'] = hist_n
    stats['p7_goals'] = goal_n


def import_acessos_sheet(artist, rows, stats):
    mode = None
    acc_n = avail_n = 0

    for row in rows:
        line = ' '.join(_cell_str(c) for c in row if c).upper()
        if 'ACESSOS CRIADOS' in line:
            mode = 'access'
            continue
        if 'FERRAMENTA' in line and 'USUÁRIO' in line and 'SENHA' in line:
            mode = 'access'
            continue
        if 'AGENDA E DISPONIBILIDADE' in line:
            mode = 'agenda'
            continue
        if 'DIA DA SEMANA' in line and 'DISPON' in line:
            mode = 'agenda'
            continue

        label, val = _label_val(row)
        off = _row_offset(row)

        if mode == 'access':
            platform = label if label and not _is_section(label) else ''
            if not platform and len(row) > off:
                platform = _cell_str(row[off])
            if not platform or 'FERRAMENTA' in platform.upper():
                continue
            existing = ArtistAccess.query.filter_by(
                artist_id=artist.id, platform=platform
            ).first()
            if existing:
                existing.username_email = val or existing.username_email
                if len(row) > off + 2:
                    existing.access_secret = _cell_str(row[off + 2]) or None
                if len(row) > off + 3:
                    existing.shared_with = _cell_str(row[off + 3]) or None
            else:
                acc_n += 1
                db.session.add(
                    ArtistAccess(
                        artist_id=artist.id,
                        platform=platform,
                        username_email=val or None,
                        access_secret=_cell_str(row[off + 2]) if len(row) > off + 2 else None,
                        shared_with=_cell_str(row[off + 3]) if len(row) > off + 3 else None,
                        status=_cell_str(row[off + 4]).lower() or 'ativo' if len(row) > off + 4 else 'ativo',
                        access_date=_parse_date(row[off + 5]) if len(row) > off + 5 else None,
                        notes=_cell_str(row[off + 6]) if len(row) > off + 6 else None,
                        sort_order=acc_n,
                    )
                )
            continue

        if mode == 'agenda':
            day_name = label or (_cell_str(row[off]) if len(row) > off else '')
            if not day_name or day_name.upper() == 'DIA DA SEMANA':
                continue
            wd = next((n for k, n in WEEKDAY_MAP.items() if k in day_name.lower()), None)
            if wd is None:
                continue
            slot = ArtistAvailability.query.filter_by(artist_id=artist.id, weekday=wd).first()
            if not slot:
                slot = ArtistAvailability(artist_id=artist.id, weekday=wd)
                db.session.add(slot)
            avail_raw = val or (_cell_str(row[off + 1]) if len(row) > off + 1 else '')
            slot.is_available = _cell_str(avail_raw).lower() not in ('não', 'nao', 'n', 'no')
            slot.start_time = _cell_str(row[off + 2])[:8] if len(row) > off + 2 else slot.start_time
            slot.end_time = _cell_str(row[off + 3])[:8] if len(row) > off + 3 else slot.end_time
            if len(row) > off + 4:
                slot.recordings_ok = _cell_str(row[off + 4]).lower() not in ('não', 'nao', 'n')
            slot.events_travel = _cell_str(row[off + 5]) if len(row) > off + 5 else None
            slot.notes = _cell_str(row[off + 6]) if len(row) > off + 6 else None
            avail_n += 1

    stats['p7_accesses'] = acc_n
    stats['p7_availability'] = avail_n


def import_reuniao_sheet(artist, rows, stats):
    meeting = OnboardingMeeting.query.filter_by(artist_id=artist.id).first()
    if not meeting:
        meeting = OnboardingMeeting(artist_id=artist.id)
        db.session.add(meeting)
        db.session.flush()

    in_agenda = False
    agenda_n = 0
    for item in list(meeting.agenda_items):
        db.session.delete(item)

    for row in rows:
        label, val = _label_val(row)
        lu = (label or '').upper()
        row_line = ' '.join(_cell_str(c) for c in row if c).upper()
        if 'PAUTAS DA REUNIÃO' in lu or 'PAUTAS DA REUNIAO' in lu:
            in_agenda = True
            continue
        if 'PAUTA' in row_line and 'DISCUTIDO' in row_line:
            in_agenda = True
            continue

        if in_agenda:
            off = _row_offset(row)
            c0 = _cell_str(row[off] if len(row) > off else '')
            if not re.match(r'^[\d.]+$', c0):
                continue
            topic = _cell_str(row[off + 1]) if len(row) > off + 1 else ''
            if not topic or topic.upper() == 'PAUTA':
                continue
            discussed_raw = _cell_str(row[off + 2]) if len(row) > off + 2 else ''
            agenda_n += 1
            db.session.add(
                MeetingAgendaItem(
                    meeting_id=meeting.id,
                    topic=topic,
                    discussed=discussed_raw.lower() in ('sim', 's', 'yes', 'x'),
                    responsible=_cell_str(row[off + 3]) if len(row) > off + 3 else None,
                    decision=_cell_str(row[off + 4]) if len(row) > off + 4 else None,
                    notes=_cell_str(row[off + 5]) if len(row) > off + 5 else None,
                    sort_order=agenda_n,
                )
            )
            continue

        norm = (label or '').lower().strip()
        for pattern, attr in MEETING_LABELS.items():
            if pattern in norm:
                if attr == 'meeting_date':
                    meeting.meeting_date = _parse_date(val)
                else:
                    setattr(meeting, attr, val or None)
                break

    stats['p7_meeting_agenda'] = agenda_n


def import_perfil_digital(artist, rows, stats):
    """Aba Perfil → tabela REDES SOCIAIS & AUDIÊNCIA."""
    in_table = False
    created = 0
    updated = 0
    header_map = {}
    known_platforms = {
        'INSTAGRAM', 'TIKTOK', 'YOUTUBE', 'TWITTER', 'PINTEREST',
        'LINKEDIN', 'KWAI', 'OUTRO', 'FACEBOOK',
    }

    for row in rows:
        line = ' '.join(_cell_str(c) for c in row if c).upper()
        if 'REDES SOCIAIS' in line or (
            'PLATAFORMA' in line and 'SEGUIDOR' in line
        ):
            in_table = True
            if 'PLATAFORMA' in line:
                header_map = {
                    _cell_str(h).upper(): i for i, h in enumerate(row) if h is not None
                }
            continue
        if 'BIO E POSICIONAMENTO' in line or 'DADOS BANC' in line:
            in_table = False
            continue
        if not in_table:
            continue

        off = _row_offset(row)
        platform = _cell(row, off)
        if not platform or platform.upper() in ('PLATAFORMA', '#'):
            continue
        plat_up = platform.upper().split('/')[0].strip()
        if plat_up not in known_platforms and 'TWITTER' not in plat_up:
            if not any(p in plat_up for p in ('INSTAGRAM', 'TIKTOK', 'YOUTUBE')):
                continue

        def col(name):
            for k, i in header_map.items():
                if name in k:
                    return _cell(row, i)
            return ''

        username = col('USUÁRIO') or col('USUARIO') or _cell(row, off + 1)
        followers = _parse_followers(col('SEGUIDOR') or _cell(row, off + 2))

        row_obj = DigitalPresence.query.filter_by(
            artist_id=artist.id, platform=platform
        ).first()
        is_new = row_obj is None
        if is_new:
            row_obj = DigitalPresence(artist_id=artist.id, platform=platform)
            db.session.add(row_obj)
            created += 1
        else:
            updated += 1

        if username:
            row_obj.username = username
            if 'INSTAGRAM' in plat_up:
                artist.instagram = username[:120]
        if followers:
            row_obj.followers = followers
        eng = col('ENGAJ')
        if eng:
            row_obj.engagement_pct = eng[:20]
        reach = col('ALCANCE')
        if reach:
            row_obj.avg_reach = reach
        aud = col('PÚBLICO') or col('PUBLICO')
        if aud:
            row_obj.main_audience = aud
        growth = col('CRESC')
        if growth:
            row_obj.monthly_growth = growth
        obs = col('OBS')
        if obs:
            row_obj.notes = obs

    stats['p7_digital_presence'] = created
    stats['p7_digital_updated'] = updated
