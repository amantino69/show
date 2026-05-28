# -*- coding: utf-8 -*-
"""Lógica de onboarding: progresso, templates e formulário."""
from datetime import datetime

from app import db
from app.models import Artist, OnboardingTask, OnboardingTemplateTask

ONBOARDING_PROFILE_SECTIONS = [
    {
        'id': 'identificacao',
        'title': 'Identificação & Contato',
        'fields': [
            ('nome_completo', 'Nome completo', 'text'),
            ('nome_artistico', 'Nome artístico', 'text'),
            ('segmento', 'Segmento', 'text'),
            ('nicho', 'Nicho específico', 'text'),
            ('cidade_estado', 'Cidade e Estado', 'text'),
            ('instagram', 'Instagram', 'text'),
            ('tiktok', 'TikTok', 'text'),
            ('youtube', 'YouTube', 'text'),
            ('whatsapp', 'WhatsApp', 'text'),
            ('email', 'E-mail', 'email'),
            ('tipo_servico', 'Tipo de serviço contratado', 'text'),
        ],
    },
    {
        'id': 'historico',
        'title': 'Histórico & Trajetória',
        'fields': [
            ('tempo_area', 'Há quanto tempo atua na área?', 'textarea'),
            ('como_comecou', 'Como começou na carreira?', 'textarea'),
            ('conquistas', 'Principais conquistas', 'textarea'),
            ('destaques', 'Projetos de maior destaque', 'textarea'),
            ('assessoria_anterior', 'Já teve assessoria antes?', 'textarea'),
            ('diferencial', 'O que diferencia você no nicho?', 'textarea'),
        ],
    },
    {
        'id': 'digital',
        'title': 'Presença Digital',
        'fields': [
            ('seguidores_ig', 'Seguidores Instagram', 'text'),
            ('seguidores_tiktok', 'Seguidores TikTok', 'text'),
            ('engajamento', 'Engajamento médio', 'text'),
            ('frequencia_posts', 'Frequência de postagem', 'text'),
            ('tipo_conteudo', 'Tipo de conteúdo', 'text'),
            ('identidade_visual', 'Identidade visual definida?', 'text'),
            ('linha_editorial', 'Linha editorial definida?', 'text'),
        ],
    },
    {
        'id': 'metas',
        'title': 'Metas & Objetivos',
        'fields': [
            ('meta_3m', 'Metas 3 meses', 'textarea'),
            ('meta_6m', 'Metas 6 meses', 'textarea'),
            ('meta_1a', 'Metas 1 ano', 'textarea'),
            ('north_star', 'Sonho grande (North Star)', 'textarea'),
            ('persona', 'Público-alvo / persona', 'textarea'),
            ('meta_financeira', 'Meta financeira', 'text'),
        ],
    },
    {
        'id': 'parcerias',
        'title': 'Parcerias & Monetização',
        'fields': [
            ('parcerias_ativas', 'Parcerias / publis ativas', 'textarea'),
            ('parcerias_interesse', 'Tipos de parceria de interesse', 'textarea'),
            ('monetizacao', 'Como monetiza hoje?', 'textarea'),
            ('cache_medio', 'Valor médio de cachê', 'text'),
            ('cnpj_mei', 'CNPJ / MEI', 'text'),
        ],
    },
    {
        'id': 'operacional',
        'title': 'Operacional & Logística',
        'fields': [
            ('disponibilidade_reunioes', 'Disponibilidade para reuniões', 'text'),
            ('horario_contato', 'Melhor horário para contato', 'text'),
            ('ferramentas', 'Ferramentas que já usa', 'text'),
            ('equipe_apoio', 'Equipe própria de apoio', 'text'),
            ('preferencia_reuniao', 'Prefere reuniões por', 'text'),
        ],
    },
]


def recalculate_onboarding_progress(artist_id):
    tasks = OnboardingTask.query.filter_by(artist_id=artist_id).all()
    if not tasks:
        return 0
    done = sum(1 for t in tasks if t.status == 'concluido')
    pct = int(round(100 * done / len(tasks)))
    artist = Artist.query.get(artist_id)
    if artist:
        artist.onboarding_progress = pct
    return pct


def apply_template_to_artist(artist_id, template_key='viezes_completo', replace=False):
    """Copia tarefas do template para o assessorado."""
    templates = (
        OnboardingTemplateTask.query.filter_by(template_key=template_key, is_active=True)
        .order_by(OnboardingTemplateTask.sort_order)
        .all()
    )
    if not templates:
        return 0

    if replace:
        OnboardingTask.query.filter_by(artist_id=artist_id).delete()

    existing_titles = {
        t.title
        for t in OnboardingTask.query.filter_by(artist_id=artist_id).all()
    }
    added = 0
    for tpl in templates:
        if tpl.title in existing_titles:
            continue
        task = OnboardingTask(
            artist_id=artist_id,
            module=tpl.module,
            title=tpl.title,
            responsible=tpl.responsible,
            status='pendente',
            sort_order=tpl.sort_order,
        )
        db.session.add(task)
        added += 1
    recalculate_onboarding_progress(artist_id)
    return added


# Mapeamento de labels da planilha P7/Arché → chaves do formulário
PLANILHA_PROFILE_MAP = {
    'nome completo': 'nome_completo',
    'nome artístico': 'nome_artistico',
    'nome artístico / @': 'nome_artistico',
    'segmento': 'segmento',
    'nicho específico': 'nicho',
    'nicho': 'nicho',
    'cidade / estado': 'cidade_estado',
    'cidade e estado': 'cidade_estado',
    'instagram': 'instagram',
    'tiktok': 'tiktok',
    'youtube': 'youtube',
    'whatsapp': 'whatsapp',
    'e-mail profissional': 'email',
    'e-mail pessoal': 'email',
    'e-mail': 'email',
    'tipo de serviço contratado': 'tipo_servico',
    'tipo de serviço': 'tipo_servico',
    'há quanto tempo atua na área': 'tempo_area',
    'como começou na carreira': 'como_comecou',
    'principais conquistas': 'conquistas',
    'projetos de maior destaque': 'destaques',
    'já teve assessoria': 'assessoria_anterior',
    'o que diferencia você': 'diferencial',
    'seguidores instagram': 'seguidores_ig',
    'engajamento médio': 'engajamento',
    'frequência de postagem': 'frequencia_posts',
    'frequência atual de postagem': 'frequencia_posts',
    'tipo de conteúdo': 'tipo_conteudo',
    'identidade visual': 'identidade_visual',
    'linha editorial': 'linha_editorial',
    'metas 3 meses': 'meta_3m',
    'metas 6 meses': 'meta_6m',
    'metas 1 ano': 'meta_1a',
    'sonho grande': 'north_star',
    'público-alvo': 'persona',
    'parcerias / publis': 'parcerias_ativas',
    'tipos de parceria': 'parcerias_interesse',
    'como monetiza': 'monetizacao',
    'valor médio de cachê': 'cache_medio',
    'cnpj / mei': 'cnpj_mei',
    'disponibilidade para reuniões': 'disponibilidade_reunioes',
    'melhor horário para contato': 'horario_contato',
    'ferramentas que já usa': 'ferramentas',
    'equipe própria': 'equipe_apoio',
    'prefere reuniões por': 'preferencia_reuniao',
}


def _normalize_label(label: str) -> str:
    return label.strip().lower().replace('::', ' ').split('::')[-1].strip()


def map_planilha_profile_to_canonical(profile: dict) -> dict:
    """Converte chaves importadas da planilha para IDs do formulário Arché."""
    out = dict(profile)
    for key, val in list(profile.items()):
        if not val or not isinstance(val, str):
            continue
        norm = _normalize_label(key)
        for pattern, field_id in PLANILHA_PROFILE_MAP.items():
            if pattern in norm or norm in pattern:
                if field_id not in out or not out.get(field_id):
                    out[field_id] = val
                break
    return out


def save_profile_from_form(artist, form):
    data = artist.get_onboarding_data()
    for section in ONBOARDING_PROFILE_SECTIONS:
        for field_id, _label, _ftype in section['fields']:
            val = form.get(f'profile_{field_id}', '').strip()
            if val:
                data[field_id] = val
            elif field_id in data:
                del data[field_id]
    artist.set_onboarding_data(data)
    # sync core artist fields
    if data.get('nome_completo'):
        artist.name = data['nome_completo'][:100]
    if data.get('nome_artistico'):
        artist.stage_name = data['nome_artistico'][:100]
    if data.get('email'):
        artist.email = data['email'][:120]
    if data.get('whatsapp'):
        artist.phone = data['whatsapp'][:20]
    if data.get('nicho'):
        artist.niche = data['nicho'][:120]
    if data.get('instagram'):
        artist.instagram = data['instagram'][:120]
