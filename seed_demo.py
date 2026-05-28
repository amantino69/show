# -*- coding: utf-8 -*-
"""
Popula o sistema com dados de DEMONSTRAÇÃO (fictícios).

Usa nomes de artistas brasileiros conhecidos apenas para ilustrar o potencial
da ferramenta — e-mails @demo.viezes.co deixam claro que não são clientes reais.

Uso:
    python seed_catalogs.py          # se ainda não rodou
    python seed_onboarding_templates.py
    python seed_demo.py            # cria a demo
    python seed_demo.py --reset    # remove só dados demo e recria
"""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models import (
    Artist,
    ArtistType,
    BrandDeal,
    CatalogItem,
    DigitalPresence,
    Event,
    EventType,
    FinancialRecord,
    Lead,
    OnboardingTask,
    User,
)
from app.onboarding_service import apply_template_to_artist, recalculate_onboarding_progress
from config import Config

DEMO_MARKER = '[DEMONSTRAÇÃO — dados fictícios]'
DEMO_EMAIL_DOMAIN = '@demo.viezes.co'


def _demo_email(slug: str) -> str:
    return f'{slug}.demo{DEMO_EMAIL_DOMAIN}'


def _ensure_prerequisites():
    """Tipos de artista, eventos e catálogos mínimos."""
    if ArtistType.query.count() == 0:
        from init_db import init_database
        init_database()
        return

    if EventType.query.count() == 0:
        types = [
            ('Show/Performance', '#FF6B6B'),
            ('Entrevista', '#4ECDC4'),
            ('Sessão de Fotos', '#45B7D1'),
            ('Gravação', '#96CEB4'),
            ('Reunião', '#FFEAA7'),
            ('Live/Stream', '#DDA0DD'),
            ('Evento Promocional', '#87CEEB'),
        ]
        for name, color in types:
            db.session.add(EventType(name=name, color=color))
        db.session.commit()

    if CatalogItem.query.filter_by(category='segment').count() == 0:
        import seed_catalogs
        seed_catalogs.seed()


def _type_id(name: str) -> int:
    t = ArtistType.query.filter_by(name=name).first()
    if not t:
        raise RuntimeError(f'Tipo de artista não encontrado: {name}')
    return t.id


def _catalog_id(category: str, name: str) -> int | None:
    item = CatalogItem.query.filter_by(category=category, name=name).first()
    return item.id if item else None


def _event_type_id(name: str) -> int:
    et = EventType.query.filter_by(name=name).first()
    if not et:
        et = EventType.query.first()
    return et.id


def demo_exists() -> bool:
    return Artist.query.filter(Artist.email.like(f'%{DEMO_EMAIL_DOMAIN}')).count() > 0


def purge_demo():
    """Remove apenas registros marcados como demonstração."""
    artists = Artist.query.filter(Artist.email.like(f'%{DEMO_EMAIL_DOMAIN}')).all()
    ids = [a.id for a in artists]
    if ids:
        User.query.filter(User.artist_id.in_(ids)).delete(synchronize_session=False)
        for artist in artists:
            db.session.delete(artist)
    Lead.query.filter(Lead.notes.like(f'{DEMO_MARKER}%')).delete(synchronize_session=False)
    db.session.commit()
    return len(ids)


# ——— Assessorados (personagens de demo por categoria) ———
DEMO_ARTISTS = [
    {
        'slug': 'anitta',
        'name': 'Anitta (personagem demo)',
        'stage_name': 'Anitta',
        'type': 'Cantor/Cantora',
        'genre': 'Pop / Funk',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'instagram': '@anitta',
        'status': 'ativo',
        'progress': 100,
        'fee': '15000',
        'niche': 'Pop internacional',
    },
    {
        'slug': 'ludmilla',
        'name': 'Ludmilla (personagem demo)',
        'stage_name': 'Ludmilla',
        'type': 'Cantor/Cantora',
        'genre': 'Pop / R&B',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'instagram': '@ludmilla',
        'status': 'ativo',
        'progress': 100,
        'fee': '12000',
    },
    {
        'slug': 'ivete',
        'name': 'Ivete Sangalo (personagem demo)',
        'stage_name': 'Ivete Sangalo',
        'type': 'Cantor/Cantora',
        'genre': 'Axé / Pop',
        'city': 'Salvador',
        'state': 'BA',
        'instagram': '@ivetesangalo',
        'status': 'ativo',
        'progress': 100,
        'fee': '20000',
    },
    {
        'slug': 'alok',
        'name': 'Alok (personagem demo)',
        'stage_name': 'Alok',
        'type': 'DJ/Produtor',
        'genre': 'Eletrônica',
        'city': 'São Paulo',
        'state': 'SP',
        'instagram': '@alok',
        'status': 'ativo',
        'progress': 100,
        'fee': '18000',
    },
    {
        'slug': 'vintage',
        'name': 'Vintage Culture (personagem demo)',
        'stage_name': 'Vintage Culture',
        'type': 'DJ/Produtor',
        'genre': 'House / Eletrônica',
        'city': 'Curitiba',
        'state': 'PR',
        'instagram': '@vintageculture',
        'status': 'ativo',
        'progress': 100,
        'fee': '14000',
    },
    {
        'slug': 'gisele',
        'name': 'Gisele Bündchen (personagem demo)',
        'stage_name': 'Gisele',
        'type': 'Modelo',
        'genre': 'Moda / Lifestyle',
        'city': 'Horizontina',
        'state': 'RS',
        'instagram': '@gisele',
        'status': 'ativo',
        'progress': 100,
        'fee': '25000',
    },
    {
        'slug': 'isabeli',
        'name': 'Isabeli Fontana (personagem demo)',
        'stage_name': 'Isabeli Fontana',
        'type': 'Modelo',
        'genre': 'Alta costura',
        'city': 'São Paulo',
        'state': 'SP',
        'instagram': '@isabelifontana',
        'status': 'ativo',
        'progress': 100,
        'fee': '16000',
    },
    {
        'slug': 'fernanda',
        'name': 'Fernanda Montenegro (personagem demo)',
        'stage_name': 'Fernanda Montenegro',
        'type': 'Ator/Atriz',
        'genre': 'Teatro / Cinema',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'instagram': '@fernanda_montenegro',
        'status': 'ativo',
        'progress': 100,
        'fee': '11000',
    },
    {
        'slug': 'selton',
        'name': 'Selton Mello (personagem demo)',
        'stage_name': 'Selton Mello',
        'type': 'Ator/Atriz',
        'genre': 'Cinema / Série',
        'city': 'São Paulo',
        'state': 'SP',
        'instagram': '@seltonmello',
        'status': 'ativo',
        'progress': 100,
        'fee': '13000',
    },
    {
        'slug': 'felipe',
        'name': 'Felipe Neto (personagem demo)',
        'stage_name': 'Felipe Neto',
        'type': 'Influenciador Digital',
        'genre': 'Entretenimento / Educação',
        'city': 'São Paulo',
        'state': 'SP',
        'instagram': '@felipenetoreal',
        'status': 'onboarding',
        'progress': 42,
        'fee': '9000',
    },
    {
        'slug': 'bianca',
        'name': 'Bianca Andrade — Boca Rosa (personagem demo)',
        'stage_name': 'Boca Rosa',
        'type': 'Influenciador Digital',
        'genre': 'Beleza / Empreendedorismo',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'instagram': '@bianca',
        'status': 'onboarding',
        'progress': 28,
        'fee': '8500',
    },
    {
        'slug': 'whindersson',
        'name': 'Whindersson Nunes (personagem demo)',
        'stage_name': 'Whindersson',
        'type': 'Comediante',
        'genre': 'Humor / Digital',
        'city': 'Piauí',
        'state': 'PI',
        'instagram': '@whinderssonnunes',
        'status': 'onboarding',
        'progress': 18,
        'fee': '10000',
    },
    {
        'slug': 'tata',
        'name': 'Tatá Werneck (personagem demo)',
        'stage_name': 'Tatá Werneck',
        'type': 'Comediante',
        'genre': 'Humor / TV',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'instagram': '@tatawerneck',
        'status': 'ativo',
        'progress': 100,
        'fee': '12500',
    },
    {
        'slug': 'carlinhos',
        'name': 'Carlinhos de Jesus (personagem demo)',
        'stage_name': 'Carlinhos de Jesus',
        'type': 'Dançarino',
        'genre': 'Jazz / Contemporâneo',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'instagram': '@carlinhosdejesus',
        'status': 'onboarding',
        'progress': 55,
        'fee': '7000',
    },
]

# ——— Leads no funil (ainda não assessorados) ———
DEMO_LEADS = [
    {
        'name': 'Pablo Vittar (lead demo)',
        'social': '@pabllovittar',
        'segment': 'Cantor/Cantora',
        'service': 'Assessoria',
        'source': 'Instagram',
        'status': 'proposta',
        'value': '8500',
        'next': 'Enviar contrato revisado',
        'days_followup': 3,
    },
    {
        'name': 'Caetano Veloso (lead demo)',
        'social': '@caetanoveloso',
        'segment': 'Cantor/Cantora',
        'service': 'Consultoria',
        'source': 'Indicação',
        'status': 'diagnostico',
        'value': '12000',
        'next': 'Agendar reunião de diagnóstico',
        'days_followup': 7,
    },
    {
        'name': 'Xuxa Meneghel (lead demo)',
        'social': '@xuxameneghel',
        'segment': 'Criador de Conteúdo',
        'service': 'Assessoria',
        'source': 'Evento / Networking',
        'status': 'negociacao',
        'value': '22000',
        'next': 'Alinhar escopo com equipe jurídica',
        'days_followup': 2,
    },
    {
        'name': 'Seu Jorge (lead demo)',
        'social': '@seujorge',
        'segment': 'Cantor/Cantora',
        'service': 'Assessoria',
        'source': 'Prospecção ativa',
        'status': 'contato',
        'value': None,
        'next': 'Primeira call de apresentação',
        'days_followup': 5,
    },
    {
        'name': 'Juliana Paes (lead demo)',
        'social': '@julianapaes',
        'segment': 'Ator/Atriz',
        'service': 'Assessoria',
        'source': 'LinkedIn',
        'status': 'novo',
        'value': None,
        'next': 'Qualificar perfil e necessidade',
        'days_followup': 10,
    },
    {
        'name': 'Gil do Vigor (lead demo)',
        'social': '@gildovigor',
        'segment': 'Influenciador Digital',
        'service': 'Consultoria',
        'source': 'TikTok',
        'status': 'perdido',
        'value': '6000',
        'lost': 'Optou por assessoria interna',
        'next': None,
        'days_followup': None,
    },
]

# ——— Pipeline de marcas (referência por stage_name do artista) ———
DEMO_BRAND_DEALS = [
    ('Anitta', 'Natura', 'prospeccao', '450000', 'viezes', 'Enviar media kit atualizado', 4),
    ('Anitta', 'Spotify Brasil', 'fechado', '280000', 'viezes', None, None),
    ('Ludmilla', 'Itaú', 'negociacao', '320000', 'proprio', 'Call com agência', 6),
    ('Alok', 'Red Bull', 'proposta', '190000', 'viezes', 'Aguardar retorno jurídico', 8),
    ('Gisele', 'Arezzo', 'prospeccao', '510000', 'viezes', 'Marcar café com marca', 12),
    ('Felipe Neto', 'PicPay', 'negociacao', '95000', 'proprio', 'Revisar exclusividade', 3),
    ('Fernanda Montenegro', 'Globo', 'fechado', '75000', 'viezes', None, None),
    ('Vintage Culture', 'Heineken', 'proposta', '140000', 'proprio', 'Enviar rider técnico', 9),
    ('Ivete Sangalo', 'Coca-Cola', 'negociacao', '400000', 'viezes', 'Definir cronograma', 5),
    ('Boca Rosa', 'Sephora', 'prospeccao', '68000', 'proprio', 'Briefing criativo', 14),
]

# ——— Eventos (referência por stage_name) ———
DEMO_EVENTS = [
    ('Anitta', 'Show — Festival Demo Verão', 'Show/Performance', 14, 'Allianz Parque — SP', 3),
    ('Alok', 'Live — Lançamento faixa demo', 'Live/Stream', 5, 'Estúdio SP (transmissão)', 2),
    ('Ivete Sangalo', 'Show — Carnaval Demo 2027', 'Show/Performance', 45, 'Salvador — BA', 4),
    ('Gisele', 'Campanha — Sessão foto marca', 'Sessão de Fotos', 10, 'Estúdio Z — SP', 6),
    ('Fernanda Montenegro', 'Entrevista — Podcast Viezes', 'Entrevista', 8, 'Online', 1),
    ('Felipe Neto', 'Gravação — Série documental demo', 'Gravação', 12, 'YouTube Space — SP', 5),
    ('Whindersson', 'Stand-up — Turnê demo Sul', 'Show/Performance', 20, 'Porto Alegre — RS', 3),
    ('Vintage Culture', 'Festival — Sunset Demo Stage', 'Show/Performance', 18, 'Florianópolis — SC', 8),
    ('Tatá Werneck', 'Gravação — Programa humor demo', 'Gravação', 7, 'Globo — RJ', 4),
    ('Ludmilla', 'Evento — Lançamento parceria demo', 'Evento Promocional', 15, 'Hotel Unique — SP', 2),
]


def _seed_artists(colors: list) -> dict[str, Artist]:
    svc_assessoria = _catalog_id('service_type', 'Assessoria')
    created = {}
    today = date.today()

    for i, data in enumerate(DEMO_ARTISTS):
        email = _demo_email(data['slug'])
        if Artist.query.filter_by(email=email).first():
            continue

        artist = Artist(
            name=data['name'],
            stage_name=data['stage_name'],
            email=email,
            phone='(11) 90000-0000',
            artist_type_id=_type_id(data['type']),
            genre=data.get('genre'),
            description=f'{DEMO_MARKER} Personagem fictício para apresentação da plataforma Viezes.',
            color=colors[i % len(colors)],
            client_status=data['status'],
            service_type_id=svc_assessoria,
            service_type='assessoria',
            niche=data.get('niche'),
            city=data.get('city'),
            state=data.get('state'),
            instagram=data.get('instagram'),
            onboarding_progress=data.get('progress', 100),
            entry_date=today - timedelta(days=30 + i * 7),
            monthly_fee=Decimal(data['fee']) if data.get('fee') else None,
            payment_status='em_dia',
            payment_due_day=10,
            strategic_manager='Julia Maria',
            operational_manager='Julia Viana',
            current_phase='Expansão' if data['status'] == 'ativo' else 'Onboarding',
        )
        db.session.add(artist)
        db.session.flush()

        apply_template_to_artist(artist.id, replace=False)
        if data['status'] == 'onboarding' and data.get('progress'):
            tasks = OnboardingTask.query.filter_by(artist_id=artist.id).order_by(
                OnboardingTask.sort_order
            ).all()
            done_count = max(1, int(len(tasks) * data['progress'] / 100))
            for j, task in enumerate(tasks):
                if j < done_count:
                    task.status = 'concluido'
                    task.completed_at = today
            recalculate_onboarding_progress(artist.id)

        if data.get('instagram'):
            handle = data['instagram'].lstrip('@')
            db.session.add(
                DigitalPresence(
                    artist_id=artist.id,
                    platform='Instagram',
                    username=f'@{handle}',
                    followers=1_000_000 + (i * 137_000),
                    engagement_pct='4.2%',
                    main_audience='Brasil — 18-34',
                )
            )

        created[data['stage_name']] = artist

    db.session.commit()
    return created


def _seed_leads():
    today = date.today()
    count = 0
    for data in DEMO_LEADS:
        if Lead.query.filter_by(name=data['name']).first():
            continue
        seg_id = _catalog_id('segment', data['segment'])
        svc_id = _catalog_id('service_type', data['service'])
        src_id = _catalog_id('lead_source', data['source'])
        follow = today + timedelta(days=data['days_followup']) if data.get('days_followup') else None

        lead = Lead(
            name=data['name'],
            social_handle=data.get('social'),
            segment=data['segment'],
            segment_id=seg_id,
            service_type=data['service'].lower(),
            service_type_id=svc_id,
            lead_source=data['source'],
            lead_source_id=src_id,
            first_contact_date=today - timedelta(days=20),
            status=data['status'],
            closed=data['status'] in ('fechado', 'perdido'),
            value=Decimal(data['value']) if data.get('value') else None,
            lost_reason=data.get('lost'),
            next_action=data.get('next'),
            follow_up_date=follow,
            notes=f'{DEMO_MARKER} Lead de exemplo para o funil CRM.',
        )
        db.session.add(lead)
        count += 1
    db.session.commit()
    return count


def _seed_brand_deals(artists: dict[str, Artist]):
    today = date.today()
    count = 0
    for stage, brand, status, value, origin, next_act, days_fu in DEMO_BRAND_DEALS:
        artist = artists.get(stage) or Artist.query.filter_by(stage_name=stage).first()
        if not artist:
            continue
        if BrandDeal.query.filter_by(artist_id=artist.id, brand_name=brand).first():
            continue
        deal = BrandDeal(
            artist_id=artist.id,
            brand_name=brand,
            contact_name='Equipe de parcerias (demo)',
            brand_segment='Marcas — demo',
            status=status,
            value=Decimal(value),
            commission_origin=origin,
            next_action=next_act,
            follow_up_date=today + timedelta(days=days_fu) if days_fu else None,
            closed_at=datetime.utcnow() if status == 'fechado' else None,
            notes=f'{DEMO_MARKER} Negócio fictício para ilustrar pipeline de marcas.',
        )
        db.session.add(deal)
        db.session.flush()

        if status == 'fechado':
            db.session.add(
                FinancialRecord(
                    artist_id=artist.id,
                    brand_deal_id=deal.id,
                    record_type='fechamento_marca',
                    description=f'Fechamento demo — {brand}',
                    amount=deal.value,
                    commission_rate=deal.commission_rate,
                    commission_amount=deal.commission_amount,
                    reference_month=today.strftime('%Y-%m'),
                    payment_status='pago',
                    paid_at=today,
                    notes=DEMO_MARKER,
                )
            )
        count += 1
    db.session.commit()
    return count


def _seed_events(artists: dict[str, Artist]):
    now = datetime.utcnow()
    count = 0
    for stage, title, et_name, days_ahead, location, hours in DEMO_EVENTS:
        artist = artists.get(stage) or Artist.query.filter_by(stage_name=stage).first()
        if not artist:
            continue
        start = now + timedelta(days=days_ahead, hours=10)
        end = start + timedelta(hours=hours)
        if Event.query.filter_by(artist_id=artist.id, title=title).first():
            continue
        db.session.add(
            Event(
                title=title,
                description=f'{DEMO_MARKER} Evento de exemplo na agenda.',
                start_datetime=start,
                end_datetime=end,
                location=location,
                artist_id=artist.id,
                event_type_id=_event_type_id(et_name),
                status='agendado',
                priority='high' if 'Show' in title else 'medium',
            )
        )
        count += 1
    db.session.commit()
    return count


def _seed_financial_monthly(artists: dict[str, Artist]):
    """Mensalidades dos assessorados ativos."""
    month = date.today().strftime('%Y-%m')
    count = 0
    for artist in artists.values():
        if artist.client_status != 'ativo' or not artist.monthly_fee:
            continue
        exists = FinancialRecord.query.filter_by(
            artist_id=artist.id,
            record_type='mensalidade',
            reference_month=month,
        ).first()
        if exists:
            continue
        db.session.add(
            FinancialRecord(
                artist_id=artist.id,
                record_type='mensalidade',
                description=f'Mensalidade demo — {month}',
                amount=artist.monthly_fee,
                reference_month=month,
                due_date=date.today().replace(day=artist.payment_due_day or 10),
                payment_status='pago' if artist.stage_name in ('Anitta', 'Gisele') else 'pendente',
                notes=DEMO_MARKER,
            )
        )
        count += 1
    db.session.commit()
    return count


def run_seed(reset: bool = False) -> dict:
    """Executa o seed dentro de um app_context já ativo. Retorna resumo."""
    db.create_all()
    _ensure_prerequisites()

    if reset:
        removed = purge_demo()
    else:
        removed = 0

    if demo_exists() and not reset:
        return {'skipped': True, 'removed': removed}

    colors = Config.ARTIST_COLORS
    artists = _seed_artists(colors)
    n_leads = _seed_leads()
    all_artists = {
        a.stage_name: a
        for a in Artist.query.filter(Artist.email.like(f'%{DEMO_EMAIL_DOMAIN}')).all()
    }
    n_deals = _seed_brand_deals(all_artists)
    n_events = _seed_events(all_artists)
    n_fin = _seed_financial_monthly(all_artists)

    return {
        'skipped': False,
        'removed': removed,
        'artists': len(artists),
        'leads': n_leads,
        'deals': n_deals,
        'events': n_events,
        'financial': n_fin,
    }


def seed_demo(reset: bool = False):
    app = create_app()
    with app.app_context():
        result = run_seed(reset=reset)

        if result.get('skipped'):
            print('Dados de demonstração já existem. Use --reset para recriar.')
            return

        if result['removed']:
            print(f'Removidos {result["removed"]} assessorado(s) demo e leads associados.')

        print('Criando assessorados demo...')
        print(f'  → {result["artists"]} assessorado(s)')
        print('Criando leads no funil...')
        print(f'  → {result["leads"]} lead(s)')
        print('Criando pipeline de marcas...')
        print(f'  → {result["deals"]} negócio(s) com marcas')
        print('Criando eventos na agenda...')
        print(f'  → {result["events"]} evento(s)')
        print('Criando lançamentos financeiros...')
        print(f'  → {result["financial"]} mensalidade(s) demo')

        print()
        print('✓ Demonstração criada com sucesso!')
        print(f'  Todos os e-mails terminam em {DEMO_EMAIL_DOMAIN}')
        print(f'  Marcador: {DEMO_MARKER}')
        print()
        print('Explore no sistema:')
        print('  • Dashboard — KPIs e visão geral')
        print('  • CRM (/crm) — leads Pablo Vittar, Xuxa, Caetano…')
        print('  • Pipeline marcas (/crm/deals)')
        print('  • Assessorados — Anitta, Alok, Gisele… (fictícios)')
        print('  • Agenda / Eventos — shows e gravações demo')
        print('  • Financeiro — mensalidades e fechamentos')
        print()
        print('Para remover: python seed_demo.py --reset')


def main():
    parser = argparse.ArgumentParser(description='Seed de demonstração Viezes')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Remove dados demo existentes e recria',
    )
    args = parser.parse_args()
    seed_demo(reset=args.reset)


if __name__ == '__main__':
    main()
