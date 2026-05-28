# -*- coding: utf-8 -*-
import json
from pathlib import Path
import openpyxl

folder = Path(__file__).resolve().parents[1] / "docs" / "planilhas"
targets = [
    ("arche_organizacional_v2.xlsx", "CRM - Pipeline"),
    ("arche_organizacional_v2.xlsx", "Clientes Ativos"),
    ("Viezes Assessoria - Painel Operacional.xlsx", "CRM — Leads"),
    ("Viezes Assessoria - Painel Operacional.xlsx", "Pipeline — Marcas"),
    ("VIEZES - Onboarding P7.xlsx", "Perfil"),
    ("VIEZES - Onboarding P7.xlsx", "Checklist"),
]

out = {}
for fname, sheet in targets:
    wb = openpyxl.load_workbook(folder / fname, read_only=True, data_only=True)
    ws = wb[sheet]
    rows_with_data = []
    for i, row in enumerate(ws.iter_rows(values_only=True), 1):
        vals = [v for v in row if v is not None and str(v).strip() and str(v).strip() not in ('—', '-')]
        if len(vals) >= 2:
            rows_with_data.append({"row": i, "values": [str(v) for v in vals[:15]]})
    wb.close()
    out[f"{fname}|{sheet}"] = rows_with_data[:30]
    out[f"{fname}|{sheet}_count"] = len(rows_with_data)

Path(__file__).parent.joinpath("_scan_data.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
