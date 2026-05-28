from app.models import CatalogItem


def get_active_items(category):
    return (
        CatalogItem.query.filter_by(category=category, is_active=True)
        .order_by(CatalogItem.sort_order, CatalogItem.name)
        .all()
    )


def sync_lead_catalog_fields(lead):
    """Copia nomes dos cadastros para colunas legadas (listagens/import)."""
    lead.segment = lead.segment_ref.name if lead.segment_ref else lead.segment
    lead.service_type = (
        lead.service_type_ref.slug or lead.service_type_ref.name.lower()
        if lead.service_type_ref
        else lead.service_type
    )
    lead.lead_source = lead.lead_source_ref.name if lead.lead_source_ref else lead.lead_source


def apply_lead_catalog_from_form(lead, form):
    seg_id = form.get('segment_id', type=int)
    svc_id = form.get('service_type_id', type=int)
    src_id = form.get('lead_source_id', type=int)
    lead.segment_id = seg_id or None
    lead.service_type_id = svc_id or None
    lead.lead_source_id = src_id or None
    sync_lead_catalog_fields(lead)
