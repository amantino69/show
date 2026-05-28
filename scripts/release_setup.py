#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comando de release no Render — roda UMA vez após cada deploy bem-sucedido.

Configure no painel Render (serviço show):
  Settings → Release Command →  python scripts/release_setup.py

Ou deixe SEED_DEMO_ON_START=1 nas variáveis de ambiente (fallback na subida do app).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    from app import create_app, db
    from app.models import User

    print('=== Release setup Viezes ===')

    # Estrutura base + empresário + tipos
    try:
        from init_db import init_database
        init_database()
    except Exception as exc:
        print(f'init_db: {exc}')

    app = create_app()
    with app.app_context():
        db.create_all()

        try:
            import seed_catalogs
            seed_catalogs.seed()
        except Exception as exc:
            print(f'seed_catalogs: {exc}')

        try:
            import seed_onboarding_templates
            seed_onboarding_templates.seed()
        except Exception as exc:
            print(f'seed_onboarding_templates: {exc}')

        from seed_demo import demo_exists, run_seed

        if demo_exists():
            print('Demonstração já existe — seed_demo ignorado.')
        else:
            result = run_seed(reset=False)
            print(
                f'Demonstração criada: {result.get("artists", 0)} assessorados, '
                f'{result.get("leads", 0)} leads, {result.get("deals", 0)} marcas, '
                f'{result.get("events", 0)} eventos.'
            )

        manager = User.query.filter_by(is_manager=True).first()
        if manager:
            print(f'Login empresário: {manager.username}')
        print('=== Release setup concluído ===')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
