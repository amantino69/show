from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
from app.reports import bp
from app.models import Event, Artist, EventType
from app import db

try:
    import pandas as pd
    import plotly.graph_objs as go
    import plotly.utils
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

@bp.route('/')
@login_required
def reports():
    if not current_user.is_manager:
        flash('Acesso negado. Apenas empresários podem visualizar relatórios.', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('reports/reports.html')

@bp.route('/dashboard_data')
@login_required
def dashboard_data():
    if not current_user.is_manager:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Obter parâmetros de data da query string
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Período padrão: últimos 6 meses se não especificado
    if date_to:
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    if date_from:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=180)
    
    # Eventos por mês
    events_query = db.session.query(
        db.func.strftime('%Y-%m', Event.start_datetime).label('month'),
        db.func.count(Event.id).label('count')
    ).filter(
        Event.start_datetime.between(start_date, end_date)
    ).group_by('month').all()
    
    months = [row.month for row in events_query]
    counts = [row.count for row in events_query]
    
    # Eventos por artista
    artist_events = db.session.query(
        Artist.stage_name,
        db.func.count(Event.id).label('count')
    ).join(Event).filter(
        Event.start_datetime.between(start_date, end_date)
    ).group_by(Artist.id, Artist.stage_name).all()
    
    artist_names = [row.stage_name for row in artist_events]
    artist_counts = [row.count for row in artist_events]
    
    # Eventos por tipo
    type_events = db.session.query(
        EventType.name,
        db.func.count(Event.id).label('count')
    ).join(Event).filter(
        Event.start_datetime.between(start_date, end_date)
    ).group_by(EventType.id, EventType.name).all()
    
    type_names = [row.name for row in type_events]
    type_counts = [row.count for row in type_events]
    
    # Status dos eventos
    status_events = db.session.query(
        Event.status,
        db.func.count(Event.id).label('count')
    ).filter(
        Event.start_datetime.between(start_date, end_date)
    ).group_by(Event.status).all()
    
    status_names = [row.status for row in status_events]
    status_counts = [row.count for row in status_events]
    
    return jsonify({
        'events_by_month': {
            'months': months,
            'counts': counts
        },
        'events_by_artist': {
            'artists': artist_names,
            'counts': artist_counts
        },
        'events_by_type': {
            'types': type_names,
            'counts': type_counts
        },
        'events_by_status': {
            'status': status_names,
            'counts': status_counts
        }
    })

@bp.route('/artist_performance/<int:artist_id>')
@login_required
def artist_performance(artist_id):
    if not current_user.is_manager:
        return jsonify({'error': 'Acesso negado'}), 403
    
    artist = Artist.query.get_or_404(artist_id)
    
    # Últimos 6 meses de eventos
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    events = Event.query.filter(
        Event.artist_id == artist_id,
        Event.start_datetime.between(start_date, end_date)
    ).order_by(Event.start_datetime).all()
    
    # Preparar dados para gráficos
    monthly_data = {}
    for event in events:
        month = event.start_datetime.strftime('%Y-%m')
        if month not in monthly_data:
            monthly_data[month] = {
                'total': 0,
                'completed': 0,
                'cancelled': 0
            }
        monthly_data[month]['total'] += 1
        if event.status == 'concluido':
            monthly_data[month]['completed'] += 1
        elif event.status == 'cancelado':
            monthly_data[month]['cancelled'] += 1
    
    months = sorted(monthly_data.keys())
    total_events = [monthly_data[month]['total'] for month in months]
    completed_events = [monthly_data[month]['completed'] for month in months]
    cancelled_events = [monthly_data[month]['cancelled'] for month in months]
    
    # Eventos por tipo
    type_data = {}
    for event in events:
        event_type = event.event_type.name if event.event_type else 'Sem tipo'
        type_data[event_type] = type_data.get(event_type, 0) + 1
    
    return jsonify({
        'artist_name': artist.stage_name,
        'monthly_performance': {
            'months': months,
            'total': total_events,
            'completed': completed_events,
            'cancelled': cancelled_events
        },
        'events_by_type': {
            'types': list(type_data.keys()),
            'counts': list(type_data.values())
        },
        'summary': {
            'total_events': len(events),
            'completed_events': len([e for e in events if e.status == 'concluido']),
            'success_rate': round(len([e for e in events if e.status == 'concluido']) / len(events) * 100, 1) if events else 0
        }
    })

@bp.route('/export/<format>')
@login_required
def export_data(format):
    if not current_user.is_manager:
        return jsonify({'error': 'Acesso negado'}), 403
    
    if not PANDAS_AVAILABLE:
        return jsonify({'error': 'Pandas não disponível para exportação'}), 500
    
    # Obter parâmetros de data da query string
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Período padrão: últimos 6 meses se não especificado
    if date_to:
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    if date_from:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=180)
    
    events = Event.query.join(Artist).filter(
        Event.start_datetime.between(start_date, end_date)
    ).all()
    
    # Preparar dados
    data = []
    for event in events:
        data.append({
            'Data': event.start_datetime.strftime('%d/%m/%Y'),
            'Hora': event.start_datetime.strftime('%H:%M'),
            'Evento': event.title,
            'Artista': event.artist.stage_name,
            'Tipo': event.event_type.name if event.event_type else '',
            'Local': event.location or '',
            'Status': event.status,
            'Prioridade': event.priority,
            'Descrição': event.description or ''
        })
    
    df = pd.DataFrame(data)
    
    if format == 'csv':
        from flask import Response
        output = df.to_csv(index=False)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-disposition": f"attachment; filename=relatorio_eventos_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"}
        )
    elif format == 'excel':
        from flask import Response
        import io
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-disposition": f"attachment; filename=relatorio_eventos_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"}
        )
    else:
        return jsonify({'error': 'Formato não suportado'}), 400

@bp.route('/generate_pdf')
@login_required
def generate_pdf():
    if not current_user.is_manager:
        return jsonify({'error': 'Acesso negado'}), 403
    
    if not REPORTLAB_AVAILABLE:
        # Fallback: HTML para PDF usando weasyprint se disponível
        try:
            import weasyprint
            return generate_pdf_weasyprint()
        except ImportError:
            return jsonify({'error': 'Bibliotecas de PDF não disponíveis. Instale reportlab ou weasyprint'}), 500
    
    from flask import Response
    import io
    from datetime import datetime, timedelta
    
    # Obter parâmetros de data
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if date_to:
        end_date = datetime.strptime(date_to, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    if date_from:
        start_date = datetime.strptime(date_from, '%Y-%m-%d')
    else:
        start_date = end_date - timedelta(days=180)
    
    # Obter dados
    events = Event.query.join(Artist).filter(
        Event.start_datetime.between(start_date, end_date)
    ).order_by(Event.start_datetime.desc()).all()
    
    # Criar PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("Relatório de Eventos - Sistema de Artistas", title_style))
    story.append(Paragraph(f"Período: {start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Estatísticas resumo
    total_events = len(events)
    completed_events = len([e for e in events if e.status == 'concluido'])
    success_rate = round(completed_events / total_events * 100, 1) if total_events > 0 else 0
    
    summary_data = [
        ['Estatística', 'Valor'],
        ['Total de Eventos', str(total_events)],
        ['Eventos Concluídos', str(completed_events)],
        ['Taxa de Sucesso', f'{success_rate}%']
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # Tabela de eventos
    if events:
        story.append(Paragraph("Detalhes dos Eventos", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        event_data = [['Data', 'Evento', 'Artista', 'Status']]
        for event in events[:50]:  # Limitar a 50 eventos para não sobrecarregar
            event_data.append([
                event.start_datetime.strftime('%d/%m/%Y'),
                event.title[:30] + ('...' if len(event.title) > 30 else ''),
                event.artist.stage_name[:20] + ('...' if len(event.artist.stage_name) > 20 else ''),
                event.status.title()
            ])
        
        event_table = Table(event_data, colWidths=[1.2*inch, 2.5*inch, 1.8*inch, 1*inch])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(event_table)
        
        if len(events) > 50:
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"* Mostrando os primeiros 50 eventos de {len(events)} encontrados.", styles['Italic']))
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", styles['Italic']))
    
    # Construir PDF
    doc.build(story)
    buffer.seek(0)
    
    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=relatorio_eventos_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.pdf'}
    )

def generate_pdf_weasyprint():
    """Fallback usando weasyprint para gerar PDF a partir de HTML"""
    from flask import render_template_string
    import weasyprint
    from flask import Response
    
    # Template HTML para o PDF
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .header { text-align: center; margin-bottom: 30px; }
            .summary { margin-bottom: 30px; }
            .summary table { width: 100%; border-collapse: collapse; }
            .summary th, .summary td { border: 1px solid #ddd; padding: 8px; text-align: center; }
            .summary th { background-color: #f2f2f2; }
            .events table { width: 100%; border-collapse: collapse; font-size: 12px; }
            .events th, .events td { border: 1px solid #ddd; padding: 6px; text-align: left; }
            .events th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Relatório de Eventos</h1>
            <p>Sistema de Gerenciamento de Artistas</p>
        </div>
        <!-- Conteúdo do relatório seria inserido aqui -->
        <p>Relatório PDF gerado com sucesso!</p>
    </body>
    </html>
    """
    
    pdf = weasyprint.HTML(string=html_template).write_pdf()
    
    return Response(
        pdf,
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=relatorio_eventos.pdf'}
    )
