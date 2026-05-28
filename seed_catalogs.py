# -*- coding: utf-8 -*-
"""Popula cadastros auxiliares. Execute: python seed_catalogs.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models import CatalogItem

SEEDS = {
    'segment': [
        ('Artista', None, 1),
        ('Cantor/Cantora', None, 2),
        ('Influenciador Digital', None, 3),
        ('Modelo', None, 4),
        ('Ator/Atriz', None, 5),
        ('Dançarino(a)', None, 6),
        ('DJ / Produtor', None, 7),
        ('Comediante', None, 8),
        ('Artista Visual', None, 9),
        ('Criador de Conteúdo', None, 10),
        ('Outros', None, 99),
    ],
    'service_type': [
        ('Consultoria', 'consultoria', 1),
        ('Assessoria', 'assessoria', 2),
    ],
    'lead_source': [
        ('Indicação', None, 1),
        ('Instagram', None, 2),
        ('TikTok', None, 3),
        ('LinkedIn', None, 4),
        ('Prospecção ativa', None, 5),
        ('Site / Landing page', None, 6),
        ('Evento / Networking', None, 7),
        ('Contato direto (WhatsApp)', None, 8),
        ('Parceria / Agência', None, 9),
        ('Outros', None, 99),
    ],
}


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        created = 0
        for category, items in SEEDS.items():
            for name, slug, order in items:
                exists = CatalogItem.query.filter_by(category=category, name=name).first()
                if exists:
                    continue
                db.session.add(
                    CatalogItem(
                        category=category,
                        name=name,
                        slug=slug,
                        sort_order=order,
                        is_active=True,
                    )
                )
                created += 1
        db.session.commit()
        print(f'Seed concluído: {created} itens criados.')
        for cat in CatalogItem.CATEGORIES:
            n = CatalogItem.query.filter_by(category=cat, is_active=True).count()
            print(f'  {CatalogItem.CATEGORIES[cat]}: {n}')


if __name__ == '__main__':
    seed()
