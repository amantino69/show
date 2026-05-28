# -*- coding: utf-8 -*-
"""Popula templates de onboarding. Execute: python seed_onboarding_templates.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models import OnboardingTemplateTask

# Template unificado: Painel Operacional + Arché (sem duplicar etapas óbvias)
TASKS = [
    # CAPTAÇÃO E QUALIFICAÇÃO
    ('CAPTAÇÃO', 'Lead registrado no CRM (nome, origem, data, responsável)', 'Julia Viana', 1),
    ('CAPTAÇÃO', 'Canal de entrada identificado', 'Julia Viana', 2),
    ('CAPTAÇÃO', 'Perfil e necessidade avaliados por Julia Viana', 'Julia Viana', 3),
    ('CAPTAÇÃO', 'Reunião com Julia Maria agendada (se qualificado)', 'Julia Viana', 4),
    ('QUALIFICAÇÃO', '1ª conversa realizada e diagnóstico documentado', 'Julia Maria', 5),
    ('QUALIFICAÇÃO', 'Reunião de diagnóstico marcada ou descartada', 'Julia Maria', 6),
    ('QUALIFICAÇÃO', 'Proposta enviada (valor, escopo, prazo)', 'Julia Maria', 7),
    # CONTRATO
    ('CONTRATO & DOCS', 'Contrato enviado para assinatura', 'Julia Maria', 10),
    ('CONTRATO & DOCS', 'Contrato assinado e recebido', 'Julia Maria', 11),
    ('CONTRATO & DOCS', 'Pagamento confirmado', 'Julia Maria', 12),
    ('CONTRATO & DOCS', 'Motivo de não fechamento registrado no CRM (se aplicável)', 'Julia Maria', 13),
    ('CONTRATO & DOCS', 'Contrato gerado conforme condições acordadas', 'Julia Viana', 14),
    ('CONTRATO & DOCS', 'Contrato arquivado no Trello e Google Drive', 'Julia Viana', 15),
    # INÍCIO DO PROJETO
    ('INÍCIO DO PROJETO', 'Grupo oficial de trabalho criado', 'Julia Maria', 20),
    ('INÍCIO DO PROJETO', 'Mensagem de boas-vindas enviada', 'Julia Maria', 21),
    ('INÍCIO DO PROJETO', 'Formulário de onboarding enviado ao cliente', 'Julia Viana', 22),
    ('INÍCIO DO PROJETO', 'Formulário de onboarding preenchido e retornado', 'Cliente', 23),
    ('INÍCIO DO PROJETO', 'Grupo de WhatsApp criado com o assessorado', 'Julia Viana', 24),
    ('INÍCIO DO PROJETO', 'E-mail profissional operacional criado', 'Julia Viana', 25),
    # COLETA DE DADOS
    ('COLETA DE DADOS', 'Histórico profissional levantado', 'Julia Viana', 30),
    ('COLETA DE DADOS', 'Presença digital mapeada', 'Julia Viana', 31),
    ('COLETA DE DADOS', 'Bio completa recebida', 'Julia Viana', 32),
    ('COLETA DE DADOS', 'Posicionamento e nicho definidos', 'Julia Viana', 33),
    ('COLETA DE DADOS', 'Audiência mapeada', 'Julia Viana', 34),
    ('COLETA DE DADOS', 'Histórico de marcas já trabalhadas recebido', 'Julia Viana', 35),
    ('COLETA DE DADOS', 'Tabela de valores recebida e validada', 'Julia Viana', 36),
    ('COLETA DE DADOS', 'Agenda e disponibilidade informadas', 'Julia Viana', 37),
    ('COLETA DE DADOS', 'Metas de curto e longo prazo definidas', 'Julia Maria', 38),
    ('COLETA DE DADOS', 'Marcas dos sonhos listadas', 'Julia Viana', 39),
    # ORGANIZAÇÃO
    ('ORGANIZAÇÃO', 'Organização no Trello', 'Julia Viana', 40),
    ('ORGANIZAÇÃO', 'Pasta criada no Google Drive', 'Julia Viana', 41),
    ('ORGANIZAÇÃO', 'Acesso ao Google Drive compartilhado', 'Julia Viana', 42),
    ('ORGANIZAÇÃO', 'Assessorado cadastrado no CRM principal', 'Julia Viana', 43),
    # MÍDIA KIT
    ('MÍDIA KIT', 'Entrega do Mídia Kit', 'Julia Viana + Rogler', 50),
    ('MÍDIA KIT', 'Briefing de mídia kit enviado para Rogler', 'Julia Viana', 51),
    ('MÍDIA KIT', 'Mídia kit completo (PDF)', 'Rogler', 52),
  # ALINHAMENTO
    ('ALINHAMENTO', 'Reunião de alinhamento fino realizada', 'Julia Maria', 60),
    ('ALINHAMENTO', '1ª reunião oficial de imersão marcada', 'Julia Maria', 61),
    ('ALINHAMENTO', 'Relatório estratégico pós-reunião entregue', 'Julia Maria', 62),
    ('ALINHAMENTO', 'Calendário editorial ativo', 'Julia Viana', 63),
    ('ALINHAMENTO', 'Início das prospecções de marcas', 'Julia Maria', 64),
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        n = 0
        for module, title, resp, order in TASKS:
            exists = OnboardingTemplateTask.query.filter_by(
                template_key='viezes_completo', title=title
            ).first()
            if exists:
                continue
            db.session.add(
                OnboardingTemplateTask(
                    template_key='viezes_completo',
                    module=module,
                    title=title,
                    responsible=resp,
                    sort_order=order,
                )
            )
            n += 1
        db.session.commit()
        total = OnboardingTemplateTask.query.filter_by(template_key='viezes_completo').count()
        print(f'Criados {n} itens. Total template viezes_completo: {total}')


if __name__ == '__main__':
    seed()
