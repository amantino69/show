# -*- coding: utf-8 -*-
"""
Importa dados das planilhas em docs/planilhas para o banco Show.
Uso: python scripts/import_planilhas.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import openpyxl
from sqlalchemy import or_
from app import create_app, db
from app.models import Lead, Artist, ArtistType, User, BrandDeal, OnboardingTask
from config import Config

PLANILHAS = ROOT / "docs" / "planilhas"

P7_FILE_NAMES = (
    "VIEZES - Onboarding P7.xlsx",
    "02_onboarding_p7.xlsx",
)


def _cell_str(v):
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v).strip()


def _parse_date(v):
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = _cell_str(v)
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s[:10], fmt).date()
        except ValueError:
            continue
    return None


def _parse_decimal(v):
    if v is None or v == "":
        return None
    if isinstance(v, (int, float, Decimal)):
        return Decimal(str(v))
    s = _cell_str(v).replace("R$", "").replace(" ", "")
    if not s or s in ("—", "-"):
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None


def _norm_status(raw: str) -> str:
    s = _cell_str(raw).lower()
    if "conclu" in s:
        return "concluido"
    if "andamento" in s:
        return "em_andamento"
    if "nao" in s and "inici" in s:
        return "nao_iniciado"
    return "pendente"


def _find_header_row(rows, markers):
    for i, row in enumerate(rows):
        line = " ".join(_cell_str(c).upper() for c in row if c)
        if all(m.upper() in line for m in markers):
            return i, row
    return None, None


def _p7_workbook_path():
    for name in P7_FILE_NAMES:
        p = PLANILHAS / name
        if p.exists():
            return p
    return None


def _sheet_rows(path: Path, sheet_name: str, max_row=500):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(max_row=max_row, values_only=True))
    wb.close()
    return rows


def _get_or_create_artist_type():
    t = ArtistType.query.filter_by(name="Influenciador Digital").first()
    if not t:
        t = ArtistType.query.first()
    if not t:
        raise RuntimeError("Nenhum tipo de artista no banco. Execute init_db.py primeiro.")
    return t


def _ensure_user(artist: Artist, username: str, email: str, password: str):
    user = User.query.filter_by(artist_id=artist.id).first()
    if user:
        return user
    base = username
    n = 1
    while User.query.filter_by(username=username).first():
        username = f"{base}_{n}"
        n += 1
    user = User(username=username, email=email, is_manager=False, artist_id=artist.id)
    user.set_password(password)
    db.session.add(user)
    return user


def import_crm_pipeline(stats: dict):
    path = PLANILHAS / "arche_organizacional_v2.xlsx"
    if not path.exists():
        return
    rows = _sheet_rows(path, "CRM - Pipeline")
    hi, header = _find_header_row(rows, ["NOME", "PERFIL"])
    if hi is None:
        return
    col = {_cell_str(h).upper(): i for i, h in enumerate(header) if h}

    def col_val(row, *names):
        for n in names:
            for k, i in col.items():
                if n in k:
                    return row[i] if i < len(row) else None
        return None

    count = 0
    for row in rows[hi + 1 :]:
        name = _cell_str(col_val(row, "NOME", "PERFIL"))
        if not name or name.isdigit():
            continue
        social = _cell_str(col_val(row, "INSTAGRAM", "TIK"))
        existing = Lead.query.filter_by(name=name).first()
        if existing:
            continue
        fechou = _cell_str(col_val(row, "FECHOU")).lower()
        lead = Lead(
            name=name,
            social_handle=social or None,
            segment=_cell_str(col_val(row, "SEGMENTO")) or None,
            service_type=_cell_str(col_val(row, "TIPO", "SERVI")).lower() or None,
            lead_source=_cell_str(col_val(row, "ORIGEM")) or None,
            first_contact_date=_parse_date(col_val(row, "1º", "1O", "CONTATO")),
            diagnostic_date=_parse_date(col_val(row, "DIAGN")),
            status=_cell_str(col_val(row, "STATUS")).lower() or "novo",
            closed=fechou in ("sim", "s", "yes", "1", "true", "x"),
            value=_parse_decimal(col_val(row, "VALOR")),
            lost_reason=_cell_str(col_val(row, "MOTIVO")) or None,
            next_action=_cell_str(col_val(row, "PRÓXIMA", "PROXIMA")) or None,
        )
        db.session.add(lead)
        count += 1
    stats["leads_pipeline"] = count


def import_crm_leads_painel(stats: dict):
    path = PLANILHAS / "Viezes Assessoria - Painel Operacional.xlsx"
    if not path.exists():
        return
    rows = _sheet_rows(path, "CRM — Leads")
    hi, header = _find_header_row(rows, ["NOME"])
    if hi is None:
        return
    count = 0
    for row in rows[hi + 1 :]:
        name = _cell_str(row[0]) if row else ""
        if not name or name.upper() == "NOME":
            continue
        if Lead.query.filter_by(name=name).first():
            continue
        lead = Lead(
            name=name,
            segment=_cell_str(row[1]) if len(row) > 1 else None,
            lead_source=_cell_str(row[2]) if len(row) > 2 else None,
            status=_cell_str(row[3]).lower() if len(row) > 3 else "novo",
            notes=_cell_str(row[7]) if len(row) > 7 else None,
            first_contact_date=_parse_date(row[6]) if len(row) > 6 else None,
        )
        db.session.add(lead)
        count += 1
    stats["leads_painel"] = count


def import_clientes_ativos(stats: dict):
    path = PLANILHAS / "arche_organizacional_v2.xlsx"
    rows = _sheet_rows(path, "Clientes Ativos")
    hi, header = _find_header_row(rows, ["CLIENTE", "PERFIL"])
    if hi is None:
        return
    artist_type = _get_or_create_artist_type()
    colors = Config.ARTIST_COLORS
    count = 0
    for row in rows[hi + 1 :]:
        if not row:
            continue
        name = _cell_str(row[1]) if len(row) > 1 else _cell_str(row[0] if row else "")
        if not name or name.isdigit() or name.upper().startswith("CLIENTE"):
            continue
        stage = name.split("-")[-1].strip() if "-" in name else name.split()[0]
        artist = Artist.query.filter(
            or_(Artist.stage_name == stage, Artist.name == name)
        ).first()
        if not artist:
            email = f"{stage.lower().replace(' ', '_')}@show.local"
            artist = Artist(
                name=name,
                stage_name=stage[:100],
                email=email,
                artist_type_id=artist_type.id,
                color=colors[count % len(colors)],
                client_status="ativo",
                service_type=_cell_str(row[3]).lower() if len(row) > 3 else None,
                entry_date=_parse_date(row[4]) if len(row) > 4 else None,
            )
            db.session.add(artist)
            db.session.flush()
            _ensure_user(artist, stage.lower().replace(" ", "_")[:40], email, f"{stage.lower()}123")
            count += 1
        else:
            artist.client_status = "ativo"
    stats["clientes_ativos"] = count


def import_pipeline_marcas(stats: dict):
    path = PLANILHAS / "Viezes Assessoria - Painel Operacional.xlsx"
    rows = _sheet_rows(path, "Pipeline — Marcas")
    hi, header = _find_header_row(rows, ["ASSESSORADO", "MARCA"])
    if hi is None:
        return
    count = 0
    for row in rows[hi + 1 :]:
        assessorado = _cell_str(row[0]) if row else ""
        marca = _cell_str(row[1]) if len(row) > 1 else ""
        if not assessorado or not marca or "TOTAL" in assessorado.upper():
            continue
        artist = Artist.query.filter(
            or_(
                Artist.stage_name.ilike(f"%{assessorado}%"),
                Artist.name.ilike(f"%{assessorado}%"),
            )
        ).first()
        if not artist:
            continue
        if BrandDeal.query.filter_by(artist_id=artist.id, brand_name=marca).first():
            continue
        origem = _cell_str(row[4]).lower() if len(row) > 4 else ""
        commission = "viezes" if "viezes" in origem or "20" in origem else "proprio"
        deal = BrandDeal(
            artist_id=artist.id,
            brand_name=marca,
            contact_name=_cell_str(row[2]) if len(row) > 2 else None,
            status=_cell_str(row[5]).lower() if len(row) > 5 else "prospeccao",
            value=_parse_decimal(row[7]) if len(row) > 7 else None,
            commission_origin=commission,
            next_action=_cell_str(row[8]) if len(row) > 8 else None,
        )
        db.session.add(deal)
        count += 1
    stats["brand_deals"] = count


def import_p7_onboarding(stats: dict):
    path = _p7_workbook_path()
    if not path:
        stats["p7_skipped"] = "planilha P7 não encontrada em docs/planilhas/"
        return

    # Dashboard — progresso e data entrada
    dash = _sheet_rows(path, "Dashboard", max_row=30)
    progress_pct = 36
    entry_date = None
    full_name = "Pedro Henrique Marçal Oliveira"
    stage_name = "P7"
    for row in dash:
        vals = [_cell_str(c) for c in row if c is not None]
        if "ASSESSORADO" in " ".join(vals).upper():
            for v in vals:
                if "P7" in v or "Pedro" in v:
                    full_name = v.replace("ASSESSORADO:", "").strip(" :/")
                    if "-" in v:
                        parts = v.split("-")
                        stage_name = parts[-1].strip()
        if len(vals) >= 2 and vals[0] == "Em andamento":
            try:
                progress_pct = int(float(vals[1]) * 100)
            except (ValueError, TypeError):
                pass
        for v in vals:
            d = _parse_date(v)
            if d and d.year > 2020:
                entry_date = d

    def _label_val(row):
        """Planilhas Viezes usam coluna B/C (índice 1/2)."""
        cells = list(row) if row else []
        while cells and (cells[0] is None or _cell_str(cells[0]) == ""):
            cells = cells[1:]
        if not cells:
            return "", ""
        label = _cell_str(cells[0])
        val = _cell_str(cells[1]) if len(cells) > 1 else ""
        if not val and len(cells) > 2:
            val = _cell_str(cells[2])
        return label, val

    profile_rows = _sheet_rows(path, "Perfil", max_row=120)
    profile = {}
    current_section = ""
    for row in profile_rows:
        label, val = _label_val(row)
        if not label:
            continue
        if label.startswith("  ") and not val:
            current_section = label.strip()
            continue
        if val and label not in ("PLATAFORMA", "#"):
            key = f"{current_section}::{label}" if current_section else label
            profile[key] = val
        if label == "Nome completo" and val:
            full_name = val
        if "artístico" in label.lower() and val:
            stage_name = val.replace("@", "").strip()
        if label.lower() == "instagram":
            off = 1 if row and _cell_str(row[0]) == "" else 0
            handle = val or (_cell_str(row[off + 1]) if len(row) > off + 1 else "")
            followers = _cell_str(row[off + 2]) if len(row) > off + 2 else ""
            if handle or followers:
                profile["instagram_metrics"] = {
                    "handle": handle,
                    "followers": followers,
                }

    artist_type = _get_or_create_artist_type()
    artist = Artist.query.filter(
        or_(Artist.stage_name.ilike(stage_name), Artist.name.ilike(f"%{full_name}%"))
    ).first()

    email = profile.get("E-mail profissional") or profile.get("E-mail pessoal") or "p7@viezes.com.br"
    email = email.replace(",", ".")

    phone = profile.get("Telefone", "")
    city_state = profile.get("Cidade / Estado", "Belo Horizonte")

    if not artist:
        colors = Config.ARTIST_COLORS
        artist = Artist(
            name=full_name,
            stage_name=stage_name,
            email=email,
            phone=phone or None,
            artist_type_id=artist_type.id,
            color=colors[0],
            client_status="onboarding",
            service_type="assessoria",
            city=city_state.split("/")[0].strip() if city_state else None,
            state=city_state.split("/")[-1].strip()[:2] if "/" in city_state else None,
            instagram=profile.get("instagram_metrics", {}).get("handle", "@pe7dro"),
            onboarding_progress=progress_pct,
            entry_date=entry_date,
        )
        db.session.add(artist)
        db.session.flush()
        _ensure_user(artist, "p7", email, "p7123")
        stats["p7_created"] = True
    else:
        stats["p7_created"] = False

    artist.name = full_name
    artist.stage_name = stage_name
    artist.email = email
    artist.phone = phone or artist.phone
    artist.client_status = "onboarding"
    artist.onboarding_progress = progress_pct
    artist.entry_date = entry_date or artist.entry_date
    artist.service_type = "assessoria"
    from app.onboarding_service import map_planilha_profile_to_canonical

    canonical_profile = map_planilha_profile_to_canonical(profile)
    artist.set_onboarding_data(canonical_profile)
    stats["profile"] = {**profile, **canonical_profile}

    # Checklist
    rows = _sheet_rows(path, "Checklist", max_row=200)
    OnboardingTask.query.filter_by(artist_id=artist.id).delete()
    module = ""
    order = 0
    task_count = 0
    for row in rows:
        if not row:
            continue
        cells = [c for c in row if c is not None]
        if not cells:
            continue
        # Coluna B costuma ser o primeiro valor útil
        offset = 0
        if row[0] is None and len(row) > 1:
            offset = 1
        c0 = _cell_str(row[offset] if len(row) > offset else "")
        if c0.startswith("  ") and not re.match(r"^[\d.]+$", c0):
            module = c0.strip()
            continue
        if not re.match(r"^[\d.]+$", c0):
            continue
        status_raw = _cell_str(row[offset + 1]) if len(row) > offset + 1 else ""
        title = _cell_str(row[offset + 2]) if len(row) > offset + 2 else ""
        if not title:
            continue
        responsible = _cell_str(row[offset + 3]) if len(row) > offset + 3 else None
        notes = _cell_str(row[offset + 6]) if len(row) > offset + 6 else None
        order += 1
        task = OnboardingTask(
            artist_id=artist.id,
            module=module or None,
            title=title,
            responsible=responsible,
            status=_norm_status(status_raw),
            notes=notes,
            sort_order=order,
        )
        db.session.add(task)
        task_count += 1

    stats["p7_tasks"] = task_count
    stats["p7_progress"] = progress_pct
    stats["_p7_path"] = path

    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from import_p7_sheets import import_p7_extended

    import_p7_extended(artist, _sheet_rows, stats)


def main():
    if not PLANILHAS.exists():
        print(f"Pasta não encontrada: {PLANILHAS}")
        return 1

    app = create_app()
    stats = {}
    with app.app_context():
        db.create_all()
        import_crm_pipeline(stats)
        import_crm_leads_painel(stats)
        import_clientes_ativos(stats)
        import_pipeline_marcas(stats)
        import_p7_onboarding(stats)
        db.session.commit()

    stats.pop("_p7_path", None)
    stats.pop("profile", None)
    print("Importação concluída:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
