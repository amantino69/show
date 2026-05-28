# Como liberar acesso às planilhas para o Show

O sistema **não conecta automaticamente** ao Google Drive. Para importar todos os dados, use uma das opções abaixo.

## Opção A — Exportar Excel (recomendado)

Para cada planilha no Google Sheets:

1. Abra a planilha
2. **Arquivo → Fazer download → Microsoft Excel (.xlsx)**
3. Salve em `d:\show\docs\planilhas\` com estes nomes:

| Arquivo sugerido | Planilha original |
|------------------|-------------------|
| `01_onboarding_arche.xlsx` | arche_onboarding_v2 |
| `02_onboarding_p7.xlsx` | VIEZES - Onboarding P7 |
| `03_organizacional.xlsx` | arche_organizacional_v2 |
| `04_painel_operacional.xlsx` | Viezes Assessoria - Painel Operacional |

Avise quando os arquivos estiverem na pasta — o script de importação (Fase 1b) será executado em seguida.

## Opção B — Link público somente leitura

1. No Google Sheets: **Compartilhar**
2. **Acesso geral** → **Qualquer pessoa com o link** → **Leitor**
3. Envie os mesmos 4 links (já enviados)

> Links só com “visualização” às vezes bloqueiam exportação automática; o Excel é mais confiável.

## Opção C — Compartilhar com conta de serviço

Se no futuro houver integração via API Google, será necessária uma conta Google com acesso **Editor** ou **Leitor** às pastas.

---

## O que já está no sistema (Fase 1)

- **CRM** — `/crm` — cadastro e funil de leads
- **Converter lead** → assessorado em onboarding
- **Pipeline de marcas** — `/crm/deals`
- **Dashboard** — KPIs: ativos, propostas, fechamentos do mês, follow-ups
- **Assessorados** — filtro por status (ativo / onboarding / inativo)

## Importar planilhas para o banco

Com os `.xlsx` em `docs/planilhas/`:

```powershell
cd d:\show
.\venv\Scripts\activate
python migrate_phase1_crm.py
python scripts/import_planilhas.py
py app.py
```

Login empresário: `empresario` / `123456`

### Abas importadas (P7)

| Aba | Destino no sistema |
|-----|-------------------|
| Dashboard | progresso, data entrada, nome |
| Perfil | ficha Arché (chaves mapeadas) + presença digital por canal |
| Checklist | tarefas de onboarding |
| Contrato | `ArtistContract` + documentos |
| MidiaKit | tabela de preços + materiais + restrições |
| Marcas | marcas dos sonhos, histórico, metas |
| Acessos | ferramentas + agenda semanal |
| Reuniao | reunião de alinhamento + pauta |

**Extras:** as 10 linhas de *Marcas dos sonhos* são pré-cadastradas mesmo vazias na planilha; Instagram/TikTok/YouTube da aba Perfil sincronizam para *Presença digital* (seguidores `12.8` → 12.800).

Nomes aceitos do arquivo: `VIEZES - Onboarding P7.xlsx` ou `02_onboarding_p7.xlsx`

### Resultado da última importação

- **P7 (Pedro Henrique)** — assessorado criado/atualizado com **38 tarefas** de onboarding e **35%** de progresso
- **CRM / Clientes / Pipeline** — planilhas estão com **templates vazios** (só cabeçalhos); nada a importar até a cliente preencher

Ver onboarding: **Assessorados → P7 → Onboarding**
