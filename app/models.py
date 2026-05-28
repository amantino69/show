from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class CatalogItem(db.Model):
    """Cadastros auxiliares — segmento, tipo de serviço, origem do lead, etc."""
    __tablename__ = 'catalog_item'

    CATEGORIES = {
        'segment': 'Segmento',
        'service_type': 'Tipo de serviço',
        'lead_source': 'Origem do lead',
    }

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(40), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('category', 'name', name='uq_catalog_category_name'),
    )

    @property
    def category_label(self):
        return self.CATEGORIES.get(self.category, self.category)

    def __repr__(self):
        return f'<CatalogItem {self.category}:{self.name}>'


class ArtistType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    icon = db.Column(db.String(50), nullable=False)  # Classe do ícone FontAwesome
    color = db.Column(db.String(7), nullable=False)  # Cor em hex
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    artists = db.relationship('Artist', backref='artist_type', lazy=True)
    
    def __repr__(self):
        return f'<ArtistType {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_manager = db.Column(db.Boolean, default=False)  # True para empresário
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True)
    display_name = db.Column(db.String(120), nullable=True)
    team_role = db.Column(db.String(40), nullable=True)  # estrategico, operacional, captacao
    phone = db.Column(db.String(20), nullable=True)
    is_active_user = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    google_token = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='user_account', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Artist(db.Model):
    """Assessorado / artista gerenciado pela assessoria."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    stage_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    artist_type_id = db.Column(db.Integer, db.ForeignKey('artist_type.id'), nullable=False)
    genre = db.Column(db.String(50), nullable=True)  # Gênero específico dentro do tipo
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), nullable=False)  # Cor em hex para agenda
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Gestão assessoria (Fase 1 — substitui planilhas)
    client_status = db.Column(db.String(20), default='ativo')  # lead, onboarding, ativo, inativo
    service_type = db.Column(db.String(30), nullable=True)  # legado — use service_type_id
    service_type_id = db.Column(db.Integer, db.ForeignKey('catalog_item.id'), nullable=True)
    niche = db.Column(db.String(120), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    state = db.Column(db.String(2), nullable=True)
    instagram = db.Column(db.String(120), nullable=True)
    onboarding_progress = db.Column(db.Integer, default=0)  # 0-100
    lead_id = db.Column(db.Integer, db.ForeignKey('lead.id'), nullable=True)
    onboarding_data = db.Column(db.Text, nullable=True)  # JSON — campos das planilhas
    entry_date = db.Column(db.Date, nullable=True)

    # Cliente ativo / financeiro (Fase 3)
    monthly_fee = db.Column(db.Numeric(12, 2), nullable=True)
    payment_status = db.Column(db.String(30), default='em_dia')  # em_dia, pendente, atrasado
    payment_due_day = db.Column(db.Integer, nullable=True)  # dia do mês
    current_phase = db.Column(db.String(80), nullable=True)
    strategic_manager = db.Column(db.String(120), nullable=True)
    operational_manager = db.Column(db.String(120), nullable=True)
    
    # Relacionamentos
    events = db.relationship('Event', backref='artist', lazy=True, cascade='all, delete-orphan')
    financial_records = db.relationship('FinancialRecord', backref='artist', lazy=True)
    brand_deals = db.relationship('BrandDeal', backref='artist', lazy=True)
    onboarding_tasks = db.relationship(
        'OnboardingTask', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    contract = db.relationship('ArtistContract', backref='artist', uselist=False, cascade='all, delete-orphan')
    onboarding_documents = db.relationship(
        'OnboardingDocument', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    rate_card_lines = db.relationship(
        'RateCardLine', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    dream_brands = db.relationship(
        'DreamBrand', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    partnership_history = db.relationship(
        'BrandPartnershipHistory', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    goals = db.relationship('ArtistGoal', backref='artist', lazy=True, cascade='all, delete-orphan')
    accesses = db.relationship('ArtistAccess', backref='artist', lazy=True, cascade='all, delete-orphan')
    availability_slots = db.relationship(
        'ArtistAvailability', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    onboarding_meetings = db.relationship(
        'OnboardingMeeting', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    digital_presence = db.relationship(
        'DigitalPresence', backref='artist', lazy=True, cascade='all, delete-orphan'
    )
    service_type_ref = db.relationship('CatalogItem', foreign_keys=[service_type_id])

    def __repr__(self):
        return f'<Artist {self.stage_name}>'

    @property
    def service_type_label(self):
        if self.service_type_ref:
            return self.service_type_ref.name
        return self.service_type or '—'

    @property
    def client_status_label(self):
        labels = {
            'lead': 'Lead',
            'onboarding': 'Onboarding',
            'ativo': 'Ativo',
            'inativo': 'Inativo',
        }
        return labels.get(self.client_status, self.client_status)

    def get_onboarding_data(self):
        if not self.onboarding_data:
            return {}
        try:
            return json.loads(self.onboarding_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_onboarding_data(self, data):
        self.onboarding_data = json.dumps(data, ensure_ascii=False)


class Lead(db.Model):
    """CRM — pipeline de leads (planilha arche_organizacional / Painel Operacional)."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    social_handle = db.Column(db.String(200), nullable=True)  # Instagram / TikTok
    segment = db.Column(db.String(80), nullable=True)  # legado — use segment_id
    service_type = db.Column(db.String(30), nullable=True)
    lead_source = db.Column(db.String(120), nullable=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('catalog_item.id'), nullable=True)
    service_type_id = db.Column(db.Integer, db.ForeignKey('catalog_item.id'), nullable=True)
    lead_source_id = db.Column(db.Integer, db.ForeignKey('catalog_item.id'), nullable=True)
    first_contact_date = db.Column(db.Date, nullable=True)
    diagnostic_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(40), default='novo')  # novo, contato, diagnostico, proposta, negociacao, fechado, perdido
    closed = db.Column(db.Boolean, default=False)
    value = db.Column(db.Numeric(12, 2), nullable=True)
    lost_reason = db.Column(db.Text, nullable=True)
    next_action = db.Column(db.String(300), nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True)
    converted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    artist = db.relationship('Artist', foreign_keys=[artist_id], backref='source_lead')
    segment_ref = db.relationship('CatalogItem', foreign_keys=[segment_id])
    service_type_ref = db.relationship('CatalogItem', foreign_keys=[service_type_id])
    lead_source_ref = db.relationship('CatalogItem', foreign_keys=[lead_source_id])

    @property
    def segment_label(self):
        if self.segment_ref:
            return self.segment_ref.name
        return self.segment or '—'

    @property
    def service_type_label(self):
        if self.service_type_ref:
            return self.service_type_ref.name
        return self.service_type or '—'

    @property
    def lead_source_label(self):
        if self.lead_source_ref:
            return self.lead_source_ref.name
        return self.lead_source or '—'

    STATUS_LABELS = {
        'novo': 'Novo',
        'contato': '1º Contato',
        'diagnostico': 'Diagnóstico',
        'proposta': 'Proposta',
        'negociacao': 'Negociação',
        'fechado': 'Fechado',
        'perdido': 'Perdido',
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    def __repr__(self):
        return f'<Lead {self.name}>'


class BrandDeal(db.Model):
    """Pipeline de marcas / parcerias por assessorado."""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    brand_name = db.Column(db.String(200), nullable=False)
    contact_name = db.Column(db.String(120), nullable=True)
    brand_segment = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default='prospeccao')  # prospeccao, proposta, negociacao, fechado, perdido
    value = db.Column(db.Numeric(12, 2), nullable=True)
    commission_origin = db.Column(db.String(20), default='proprio')  # proprio (10%), viezes (20%)
    next_action = db.Column(db.String(300), nullable=True)
    follow_up_date = db.Column(db.Date, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    STATUS_LABELS = {
        'prospeccao': 'Prospecção',
        'proposta': 'Proposta aberta',
        'negociacao': 'Negociação',
        'fechado': 'Fechado',
        'perdido': 'Perdido',
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    @property
    def commission_rate(self):
        return 20 if self.commission_origin == 'viezes' else 10

    @property
    def commission_amount(self):
        if self.value is None:
            return None
        from decimal import Decimal
        rate = Decimal(self.commission_rate) / Decimal(100)
        return (self.value * rate).quantize(Decimal('0.01'))

    def __repr__(self):
        return f'<BrandDeal {self.brand_name}>'


class OnboardingTemplateTask(db.Model):
    """Template de checklist (planilhas Arché + Painel)."""
    __tablename__ = 'onboarding_template_task'

    id = db.Column(db.Integer, primary_key=True)
    template_key = db.Column(db.String(40), default='viezes_completo', index=True)
    module = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    responsible = db.Column(db.String(120), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<OnboardingTemplateTask {self.title[:30]}>'


class OnboardingTask(db.Model):
    """Tarefas de checklist de onboarding (planilha P7 / templates Arché)."""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    module = db.Column(db.String(80), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    responsible = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default='pendente')
    due_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    STATUS_LABELS = {
        'pendente': 'Pendente',
        'concluido': 'Concluído',
        'em_andamento': 'Em andamento',
        'nao_iniciado': 'Não iniciado',
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    def __repr__(self):
        return f'<OnboardingTask {self.title[:40]}>'


class FinancialRecord(db.Model):
    """Mensalidades e fechamentos de marcas."""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    brand_deal_id = db.Column(db.Integer, db.ForeignKey('brand_deal.id'), nullable=True)
    record_type = db.Column(db.String(30), nullable=False)  # mensalidade, fechamento_marca
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    commission_rate = db.Column(db.Integer, nullable=True)  # 10 ou 20
    commission_amount = db.Column(db.Numeric(12, 2), nullable=True)
    reference_month = db.Column(db.String(7), nullable=True)  # YYYY-MM
    due_date = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(30), default='pendente')  # pendente, pago, atrasado
    paid_at = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    brand_deal = db.relationship('BrandDeal', backref='financial_records')

    PAYMENT_LABELS = {
        'pendente': 'Pendente',
        'pago': 'Pago',
        'atrasado': 'Atrasado',
    }

    @property
    def payment_status_label(self):
        return self.PAYMENT_LABELS.get(self.payment_status, self.payment_status)

    def __repr__(self):
        return f'<FinancialRecord {self.record_type} {self.amount}>'


class ArtistContract(db.Model):
    """Contrato do assessorado (aba Contrato — P7)."""
    __tablename__ = 'artist_contract'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False, unique=True)
    contract_model = db.Column(db.String(80), nullable=True)
    signed_at = db.Column(db.Date, nullable=True)
    validity_end = db.Column(db.Date, nullable=True)
    service_format = db.Column(db.String(120), nullable=True)
    monthly_value = db.Column(db.Numeric(12, 2), nullable=True)
    commission_pct = db.Column(db.String(40), nullable=True)
    payment_method = db.Column(db.String(80), nullable=True)
    due_day = db.Column(db.Integer, nullable=True)
    exclusivity = db.Column(db.String(200), nullable=True)
    notice_period = db.Column(db.String(80), nullable=True)
    forum = db.Column(db.String(120), nullable=True)
    brand_restrictions = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OnboardingDocument(db.Model):
    """Checklist de documentos (contrato) e materiais (mídia kit)."""
    __tablename__ = 'onboarding_document'

    DOC_TYPES = {'contract': 'Contrato & Docs', 'media': 'Mídia Kit'}

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    doc_type = db.Column(db.String(20), default='contract')
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(30), default='pendente')
    received = db.Column(db.Boolean, default=False)
    received_at = db.Column(db.Date, nullable=True)
    responsible = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    STATUS_LABELS = {
        'pendente': 'Pendente',
        'em_andamento': 'Em andamento',
        'concluido': 'Concluído',
    }

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)


class RateCardLine(db.Model):
    """Tabela de preços — mídia kit."""
    __tablename__ = 'rate_card_line'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    platform = db.Column(db.String(80), nullable=True)
    format_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.String(300), nullable=True)
    amount = db.Column(db.Numeric(12, 2), nullable=True)
    is_combo = db.Column(db.Boolean, default=False)
    includes_repost = db.Column(db.Boolean, default=False)
    delivery_days = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)


class DreamBrand(db.Model):
    """Marcas dos sonhos (TOP 10) — distinto do pipeline CRM."""
    __tablename__ = 'dream_brand'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    brand_name = db.Column(db.String(200), nullable=False)
    segment = db.Column(db.String(120), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    known_contact = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(40), default='lista')
    priority = db.Column(db.Integer, default=5)
    estimated_value = db.Column(db.Numeric(12, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    STATUS_LABELS = {
        'lista': 'Na lista',
        'contato': 'Em contato',
        'negociacao': 'Negociação',
        'fechado': 'Fechado',
    }

    @property
    def is_planilha_placeholder(self):
        import re
        if re.match(r'^Marca \d+ \(a definir\)$', (self.brand_name or '').strip(), re.I):
            return True
        notes = (self.notes or '').lower()
        return 'pré-cadastro importado' in notes or 'importado da planilha' in notes

    def clear_placeholder_if_named(self, new_name: str):
        """Remove marcação de placeholder após preencher nome real."""
        if not new_name:
            return
        import re
        if re.match(r'^Marca \d+ \(a definir\)$', new_name.strip(), re.I):
            return
        notes = (self.notes or '').lower()
        if 'pré-cadastro importado' in notes or 'importado da planilha' in notes:
            self.notes = None


class BrandPartnershipHistory(db.Model):
    """Histórico de parcerias com marcas."""
    __tablename__ = 'brand_partnership_history'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    brand_name = db.Column(db.String(200), nullable=False)
    segment = db.Column(db.String(120), nullable=True)
    period = db.Column(db.String(80), nullable=True)
    format_name = db.Column(db.String(120), nullable=True)
    amount_received = db.Column(db.Numeric(12, 2), nullable=True)
    renewed = db.Column(db.Boolean, default=False)
    contact_name = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)


class ArtistGoal(db.Model):
    """Metas do assessorado."""
    __tablename__ = 'artist_goal'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    period = db.Column(db.String(40), nullable=True)
    goal_text = db.Column(db.String(300), nullable=False)
    indicator = db.Column(db.String(120), nullable=True)
    target_value = db.Column(db.String(80), nullable=True)
    current_value = db.Column(db.String(80), nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='em_andamento')
    notes = db.Column(db.Text, nullable=True)


class ArtistAccess(db.Model):
    """Acessos a ferramentas (restrito à equipe)."""
    __tablename__ = 'artist_access'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    platform = db.Column(db.String(120), nullable=False)
    username_email = db.Column(db.String(200), nullable=True)
    access_secret = db.Column(db.String(500), nullable=True)
    shared_with = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(30), default='ativo')
    access_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)


class ArtistAvailability(db.Model):
    """Agenda semanal / rotina."""
    __tablename__ = 'artist_availability'

    WEEKDAYS = [
        (0, 'Segunda'), (1, 'Terça'), (2, 'Quarta'), (3, 'Quinta'),
        (4, 'Sexta'), (5, 'Sábado'), (6, 'Domingo'),
    ]

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.String(8), nullable=True)
    end_time = db.Column(db.String(8), nullable=True)
    recordings_ok = db.Column(db.Boolean, default=True)
    events_travel = db.Column(db.String(200), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (db.UniqueConstraint('artist_id', 'weekday', name='uq_artist_weekday'),)

    @property
    def weekday_label(self):
        for w, label in self.WEEKDAYS:
            if w == self.weekday:
                return label
        return str(self.weekday)


class OnboardingMeeting(db.Model):
    """Reunião de alinhamento."""
    __tablename__ = 'onboarding_meeting'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    meeting_date = db.Column(db.Date, nullable=True)
    meeting_time = db.Column(db.String(8), nullable=True)
    format_type = db.Column(db.String(40), nullable=True)
    participants = db.Column(db.Text, nullable=True)
    meeting_link = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    agenda_items = db.relationship(
        'MeetingAgendaItem', backref='meeting', lazy=True, cascade='all, delete-orphan'
    )


class MeetingAgendaItem(db.Model):
    __tablename__ = 'meeting_agenda_item'

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('onboarding_meeting.id'), nullable=False)
    topic = db.Column(db.String(300), nullable=False)
    discussed = db.Column(db.Boolean, default=False)
    responsible = db.Column(db.String(120), nullable=True)
    decision = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    sort_order = db.Column(db.Integer, default=0)


class DigitalPresence(db.Model):
    """Presença digital por canal."""
    __tablename__ = 'digital_presence'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    platform = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(200), nullable=True)
    followers = db.Column(db.Integer, nullable=True)
    engagement_pct = db.Column(db.String(20), nullable=True)
    avg_reach = db.Column(db.String(80), nullable=True)
    main_audience = db.Column(db.String(200), nullable=True)
    monthly_growth = db.Column(db.String(40), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EventType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(7), nullable=False)
    
    # Relacionamentos
    events = db.relationship('Event', backref='event_type', lazy=True)
    
    def __repr__(self):
        return f'<EventType {self.name}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    event_type_id = db.Column(db.Integer, db.ForeignKey('event_type.id'), nullable=False)
    status = db.Column(db.String(20), default='agendado')  # agendado, em_andamento, concluido, cancelado
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    google_event_id = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    
    # Campos para estatísticas
    actual_start = db.Column(db.DateTime, nullable=True)
    actual_end = db.Column(db.DateTime, nullable=True)
    result_notes = db.Column(db.Text, nullable=True)
    success_rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    
    def __repr__(self):
        return f'<Event {self.title}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # reminder, update, cancellation, test
    scheduled_time = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Campos para diferentes tipos de notificação
    push_notification_sent = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    whatsapp_sent = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    event = db.relationship('Event', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title} for Event {self.event_id}>'


# =============================================================================
# MODELOS PARA MARKETING E DIVULGAÇÃO
# =============================================================================

class MediaFile(db.Model):
    """Banco de mídia para fotos, vídeos, releases"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # image, video, audio, document
    mime_type = db.Column(db.String(100), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # em bytes
    
    # Metadados
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # tags separadas por vírgula
    
    # Relacionamentos
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    
    # Metadados da imagem/vídeo
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Integer, nullable=True)  # duração em segundos (vídeo/áudio)
    
    # Status e datas
    is_public = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)  # destaque
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='media_files')
    event = db.relationship('Event', backref='media_files')
    uploader = db.relationship('User', backref='uploaded_files')
    
    def __repr__(self):
        return f'<MediaFile {self.filename}>'

class SocialPost(db.Model):
    """Calendário de posts para redes sociais"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, facebook, twitter, youtube, tiktok
    
    # Agendamento
    scheduled_datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    
    # Relacionamentos
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)  # opcional
    media_file_id = db.Column(db.Integer, db.ForeignKey('media_file.id'), nullable=True)
    
    # Métricas (preenchidas após publicação)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    reach = db.Column(db.Integer, default=0)
    
    # Dados da publicação
    published_at = db.Column(db.DateTime, nullable=True)
    external_post_id = db.Column(db.String(255), nullable=True)  # ID na plataforma externa
    external_url = db.Column(db.String(500), nullable=True)
    
    # Metadados
    hashtags = db.Column(db.String(1000), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    
    # Auditoria
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='social_posts')
    event = db.relationship('Event', backref='social_posts')
    media_file = db.relationship('MediaFile', backref='social_posts')
    creator = db.relationship('User', backref='created_posts')
    
    def __repr__(self):
        return f'<SocialPost {self.title} - {self.platform}>'

class PressKit(db.Model):
    """Press Kit digital para artistas"""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    
    # Informações básicas
    bio_short = db.Column(db.Text, nullable=True)  # bio curta (100-200 palavras)
    bio_long = db.Column(db.Text, nullable=True)   # bio completa
    achievements = db.Column(db.Text, nullable=True)  # conquistas e destaques
    
    # Mídia
    profile_photo_id = db.Column(db.Integer, db.ForeignKey('media_file.id'), nullable=True)
    banner_photo_id = db.Column(db.Integer, db.ForeignKey('media_file.id'), nullable=True)
    
    # Links e contatos
    website = db.Column(db.String(300), nullable=True)
    instagram = db.Column(db.String(300), nullable=True)
    facebook = db.Column(db.String(300), nullable=True)
    youtube = db.Column(db.String(300), nullable=True)
    spotify = db.Column(db.String(300), nullable=True)
    deezer = db.Column(db.String(300), nullable=True)
    apple_music = db.Column(db.String(300), nullable=True)
    
    # Informações técnicas
    technical_rider = db.Column(db.Text, nullable=True)  # rider técnico
    stage_plot = db.Column(db.Text, nullable=True)       # disposição do palco
    
    # Informações comerciais
    booking_contact = db.Column(db.String(200), nullable=True)
    booking_email = db.Column(db.String(200), nullable=True)
    booking_phone = db.Column(db.String(50), nullable=True)
    
    # Configurações
    is_public = db.Column(db.Boolean, default=True)
    template_style = db.Column(db.String(50), default='default')  # tema do press kit
    
    # Auditoria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='press_kit', uselist=False)
    profile_photo = db.relationship('MediaFile', foreign_keys=[profile_photo_id])
    banner_photo = db.relationship('MediaFile', foreign_keys=[banner_photo_id])
    
    def __repr__(self):
        return f'<PressKit for {self.artist.stage_name}>'

class SocialMetrics(db.Model):
    """Métricas consolidadas de redes sociais"""
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    
    # Métricas de seguimento
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    
    # Métricas de engajamento (período)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    total_likes = db.Column(db.Integer, default=0)
    total_comments = db.Column(db.Integer, default=0)
    total_shares = db.Column(db.Integer, default=0)
    total_views = db.Column(db.Integer, default=0)
    total_reach = db.Column(db.Integer, default=0)
    
    # Crescimento
    followers_growth = db.Column(db.Integer, default=0)  # variação no período
    engagement_rate = db.Column(db.Float, default=0.0)   # taxa de engajamento
    
    # Metadados
    collected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    artist = db.relationship('Artist', backref='social_metrics')
    
    def __repr__(self):
        return f'<SocialMetrics {self.artist.stage_name} - {self.platform}>'
