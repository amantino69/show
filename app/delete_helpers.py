# -*- coding: utf-8 -*-
"""Exclusão em cascata e limpeza de dados de teste."""
import os

from flask import current_app

from app import db
from app.models import (
    Artist,
    ArtistType,
    ArtistAccess,
    ArtistAvailability,
    ArtistContract,
    ArtistGoal,
    BrandDeal,
    BrandPartnershipHistory,
    CatalogItem,
    DigitalPresence,
    DreamBrand,
    Event,
    EventType,
    FinancialRecord,
    Lead,
    MediaFile,
    MeetingAgendaItem,
    Notification,
    OnboardingDocument,
    OnboardingMeeting,
    OnboardingTask,
    OnboardingTemplateTask,
    PressKit,
    RateCardLine,
    SocialMetrics,
    SocialPost,
    User,
)


# Ordem de exclusão em massa (filhos antes dos pais)
PURGE_ORDER = [
    'meeting_agenda_item',
    'notification',
    'financial_record',
    'brand_deal',
    'event',
    'social_metrics',
    'social_post',
    'media_file',
    'press_kit',
    'onboarding_document',
    'rate_card_line',
    'dream_brand',
    'brand_partnership_history',
    'artist_goal',
    'artist_access',
    'artist_availability',
    'digital_presence',
    'onboarding_task',
    'onboarding_meeting',
    'artist_contract',
    'user',
    'artist',
    'lead',
    'onboarding_template_task',
    'catalog_item',
    'artist_type',
    'event_type',
]


TABLE_REGISTRY = {
    'meeting_agenda_item': {
        'label': 'Pauta de reunião (onboarding)',
        'group': 'operacional',
        'model': MeetingAgendaItem,
    },
    'notification': {
        'label': 'Notificações / alertas',
        'group': 'operacional',
        'model': Notification,
    },
    'financial_record': {
        'label': 'Lançamentos financeiros',
        'group': 'operacional',
        'model': FinancialRecord,
    },
    'brand_deal': {
        'label': 'Pipeline de marcas',
        'group': 'operacional',
        'model': BrandDeal,
    },
    'event': {
        'label': 'Eventos',
        'group': 'operacional',
        'model': Event,
    },
    'social_metrics': {
        'label': 'Métricas de redes sociais',
        'group': 'operacional',
        'model': SocialMetrics,
    },
    'social_post': {
        'label': 'Posts de marketing',
        'group': 'operacional',
        'model': SocialPost,
    },
    'media_file': {
        'label': 'Arquivos de mídia',
        'group': 'operacional',
        'model': MediaFile,
    },
    'press_kit': {
        'label': 'Press kits',
        'group': 'operacional',
        'model': PressKit,
    },
    'onboarding_document': {
        'label': 'Documentos de onboarding / contrato',
        'group': 'operacional',
        'model': OnboardingDocument,
    },
    'rate_card_line': {
        'label': 'Tabela de preços (mídia kit)',
        'group': 'operacional',
        'model': RateCardLine,
    },
    'dream_brand': {
        'label': 'Marcas dos sonhos',
        'group': 'operacional',
        'model': DreamBrand,
    },
    'brand_partnership_history': {
        'label': 'Histórico de parcerias',
        'group': 'operacional',
        'model': BrandPartnershipHistory,
    },
    'artist_goal': {
        'label': 'Metas do assessorado',
        'group': 'operacional',
        'model': ArtistGoal,
    },
    'artist_access': {
        'label': 'Acessos e senhas',
        'group': 'operacional',
        'model': ArtistAccess,
    },
    'artist_availability': {
        'label': 'Rotina semanal (disponibilidade)',
        'group': 'operacional',
        'model': ArtistAvailability,
    },
    'digital_presence': {
        'label': 'Presença digital',
        'group': 'operacional',
        'model': DigitalPresence,
    },
    'onboarding_task': {
        'label': 'Tarefas de onboarding',
        'group': 'operacional',
        'model': OnboardingTask,
    },
    'onboarding_meeting': {
        'label': 'Reuniões de onboarding',
        'group': 'operacional',
        'model': OnboardingMeeting,
    },
    'artist_contract': {
        'label': 'Contratos',
        'group': 'operacional',
        'model': ArtistContract,
    },
    'user': {
        'label': 'Usuários (equipe e portal)',
        'group': 'operacional',
        'model': User,
        'protected_note': 'Mantém sua conta e pelo menos um empresário.',
    },
    'artist': {
        'label': 'Assessorados',
        'group': 'operacional',
        'model': Artist,
        'protected_note': 'Remove eventos, CRM, P7 e portal vinculados.',
    },
    'lead': {
        'label': 'Leads do CRM',
        'group': 'operacional',
        'model': Lead,
        'protected_note': 'Assessorados já convertidos permanecem.',
    },
    'onboarding_template_task': {
        'label': 'Modelos de tarefas de onboarding',
        'group': 'config',
        'model': OnboardingTemplateTask,
    },
    'catalog_item': {
        'label': 'Cadastros (segmento, serviço, origem)',
        'group': 'config',
        'model': CatalogItem,
    },
    'artist_type': {
        'label': 'Tipos de artista',
        'group': 'config',
        'model': ArtistType,
        'protected_note': 'Só limpa se não houver assessorados.',
    },
    'event_type': {
        'label': 'Tipos de evento',
        'group': 'config',
        'model': EventType,
        'protected_note': 'Só limpa se não houver eventos.',
    },
}


def get_table_stats():
    """Contagem de registros por tabela."""
    stats = []
    for key in PURGE_ORDER:
        meta = TABLE_REGISTRY[key]
        model = meta['model']
        stats.append({
            'key': key,
            'label': meta['label'],
            'group': meta['group'],
            'count': model.query.count(),
            'note': meta.get('protected_note'),
        })
    return stats


def delete_lead_record(lead: Lead) -> None:
    """Remove lead do CRM; assessorado vinculado permanece."""
    if lead.artist_id:
        artist = Artist.query.get(lead.artist_id)
        if artist:
            artist.lead_id = None
    for artist in Artist.query.filter_by(lead_id=lead.id).all():
        artist.lead_id = None
    db.session.delete(lead)


def _remove_media_file_from_disk(media: MediaFile) -> None:
    if not media.file_path:
        return
    full_path = os.path.join(current_app.root_path, 'static', media.file_path.replace('/', os.sep))
    if os.path.isfile(full_path):
        try:
            os.remove(full_path)
        except OSError:
            pass


def delete_media_file_record(media: MediaFile) -> None:
    _remove_media_file_from_disk(media)
    db.session.delete(media)


def delete_artist_completely(artist: Artist) -> None:
    """Remove assessorado e dados relacionados."""
    for deal in list(artist.brand_deals):
        FinancialRecord.query.filter_by(brand_deal_id=deal.id).delete()
        db.session.delete(deal)

    FinancialRecord.query.filter_by(artist_id=artist.id).delete()

    for meeting in OnboardingMeeting.query.filter_by(artist_id=artist.id).all():
        MeetingAgendaItem.query.filter_by(meeting_id=meeting.id).delete()
        db.session.delete(meeting)

    SocialMetrics.query.filter_by(artist_id=artist.id).delete()
    SocialPost.query.filter_by(artist_id=artist.id).delete()

    for media in MediaFile.query.filter_by(artist_id=artist.id).all():
        delete_media_file_record(media)

    PressKit.query.filter_by(artist_id=artist.id).delete()

    for event in Event.query.filter_by(artist_id=artist.id).all():
        Notification.query.filter_by(event_id=event.id).delete()
        db.session.delete(event)

    lead = Lead.query.filter_by(artist_id=artist.id).first()
    if lead:
        lead.artist_id = None

    user = User.query.filter_by(artist_id=artist.id).first()
    if user:
        db.session.delete(user)

    db.session.delete(artist)


def can_delete_user(user: User, current_user_id: int):
    if user.id == current_user_id:
        return False, 'Você não pode excluir sua própria conta.'
    if user.is_manager:
        managers = User.query.filter_by(is_manager=True, is_active_user=True).count()
        if managers <= 1:
            return False, 'Não é possível excluir o único usuário da equipe.'
    return True, ''


def _purge_simple(model):
    deleted = model.query.delete()
    return deleted


def purge_table(table_key: str, current_user_id: int):
    """
    Limpa todos os registros de uma tabela.
    Retorna (deleted_count, error_message).
    """
    if table_key not in TABLE_REGISTRY:
        return 0, 'Tabela desconhecida.'

    try:
        if table_key == 'meeting_agenda_item':
            return _purge_simple(MeetingAgendaItem), None

        if table_key == 'notification':
            return _purge_simple(Notification), None

        if table_key == 'financial_record':
            return _purge_simple(FinancialRecord), None

        if table_key == 'brand_deal':
            FinancialRecord.query.filter(FinancialRecord.brand_deal_id.isnot(None)).delete()
            return _purge_simple(BrandDeal), None

        if table_key == 'event':
            Notification.query.delete()
            return _purge_simple(Event), None

        if table_key == 'social_metrics':
            return _purge_simple(SocialMetrics), None

        if table_key == 'social_post':
            return _purge_simple(SocialPost), None

        if table_key == 'media_file':
            count = 0
            for media in MediaFile.query.all():
                delete_media_file_record(media)
                count += 1
            return count, None

        if table_key == 'press_kit':
            return _purge_simple(PressKit), None

        if table_key == 'onboarding_document':
            return _purge_simple(OnboardingDocument), None

        if table_key == 'rate_card_line':
            return _purge_simple(RateCardLine), None

        if table_key == 'dream_brand':
            return _purge_simple(DreamBrand), None

        if table_key == 'brand_partnership_history':
            return _purge_simple(BrandPartnershipHistory), None

        if table_key == 'artist_goal':
            return _purge_simple(ArtistGoal), None

        if table_key == 'artist_access':
            return _purge_simple(ArtistAccess), None

        if table_key == 'artist_availability':
            return _purge_simple(ArtistAvailability), None

        if table_key == 'digital_presence':
            return _purge_simple(DigitalPresence), None

        if table_key == 'onboarding_task':
            return _purge_simple(OnboardingTask), None

        if table_key == 'onboarding_meeting':
            MeetingAgendaItem.query.delete()
            return _purge_simple(OnboardingMeeting), None

        if table_key == 'artist_contract':
            return _purge_simple(ArtistContract), None

        if table_key == 'user':
            deleted = 0
            for user in User.query.all():
                ok, _ = can_delete_user(user, current_user_id)
                if ok:
                    db.session.delete(user)
                    deleted += 1
            return deleted, None

        if table_key == 'artist':
            artists = Artist.query.all()
            for artist in artists:
                delete_artist_completely(artist)
            return len(artists), None

        if table_key == 'lead':
            Artist.query.update({Artist.lead_id: None}, synchronize_session=False)
            Lead.query.update({Lead.artist_id: None}, synchronize_session=False)
            return _purge_simple(Lead), None

        if table_key == 'onboarding_template_task':
            return _purge_simple(OnboardingTemplateTask), None

        if table_key == 'catalog_item':
            return _purge_simple(CatalogItem), None

        if table_key == 'artist_type':
            if Artist.query.count() > 0:
                return 0, 'Existem assessorados vinculados a tipos de artista. Exclua os assessorados antes.'
            return _purge_simple(ArtistType), None

        if table_key == 'event_type':
            if Event.query.count() > 0:
                return 0, 'Existem eventos vinculados. Exclua os eventos antes.'
            return _purge_simple(EventType), None

        return 0, 'Sem handler para esta tabela.'

    except Exception as exc:
        db.session.rollback()
        return 0, str(exc)


def purge_all_test_data(current_user_id: int, include_config: bool = False):
    """
    Limpa dados operacionais (e opcionalmente configuração).
    Retorna lista de {key, label, deleted, error}.
    """
    keys = list(PURGE_ORDER)
    if not include_config:
        keys = [k for k in keys if TABLE_REGISTRY[k]['group'] == 'operacional']

    results = []
    for key in keys:
        deleted, err = purge_table(key, current_user_id)
        results.append({
            'key': key,
            'label': TABLE_REGISTRY[key]['label'],
            'deleted': deleted,
            'error': err,
        })
        if err:
            db.session.rollback()
            return results
        db.session.commit()
    return results
