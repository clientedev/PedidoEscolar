from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from models import AcquisitionRequest, StatusChange, User
import io

def generate_request_pdf(request_obj):
    """Gera PDF para um pedido específico"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center
        textColor=colors.darkblue
    )
    
    # Estilo para seções
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Cabeçalho
    story.append(Paragraph("Escola Morvan Figueiredo", title_style))
    story.append(Paragraph("Sistema de Controle de Aquisições", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Título do pedido
    story.append(Paragraph(f"Pedido de Aquisição #{request_obj.id}", section_style))
    story.append(Spacer(1, 12))
    
    # Informações básicas
    info_data = [
        ['Título:', request_obj.title],
        ['Status:', request_obj.get_status_display()],
        ['Valor Estimado:', f'R$ {request_obj.estimated_value:.2f}' if request_obj.estimated_value else 'Não informado'],
        ['Valor Final:', f'R$ {request_obj.final_value:.2f}' if request_obj.final_value else 'Não informado'],
        ['Criado por:', request_obj.creator.full_name],
        ['Responsável:', request_obj.responsible.full_name if request_obj.responsible else 'Não definido'],
        ['Data de criação:', request_obj.created_at.strftime('%d/%m/%Y às %H:%M')],
        ['Última atualização:', request_obj.updated_at.strftime('%d/%m/%Y às %H:%M')]
    ]
    
    info_table = Table(info_data, colWidths=[2.2*inch, 3.8*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Descrição
    story.append(Paragraph("Descrição", section_style))
    description_text = request_obj.description.replace('\n', '<br/>')
    story.append(Paragraph(description_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Observações
    if request_obj.observations:
        story.append(Paragraph("Observações", section_style))
        observations_text = request_obj.observations.replace('\n', '<br/>')
        story.append(Paragraph(observations_text, styles['Normal']))
        story.append(Spacer(1, 15))
    
    # Anexos
    if request_obj.attachments.count() > 0:
        story.append(Paragraph("Anexos", section_style))
        attachment_data = [['Nome do Arquivo', 'Tamanho', 'Data de Upload', 'Enviado por']]
        
        for attachment in request_obj.attachments:
            file_size = f"{attachment.file_size / 1024:.1f} KB" if attachment.file_size else "N/A"
            attachment_data.append([
                attachment.original_filename,
                file_size,
                attachment.upload_date.strftime('%d/%m/%Y'),
                attachment.uploaded_by.full_name
            ])
        
        attachment_table = Table(attachment_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 1.8*inch])
        attachment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(attachment_table)
        story.append(Spacer(1, 20))
    
    # Histórico de status
    story.append(Paragraph("Histórico de Alterações", section_style))
    status_history = StatusChange.query.filter_by(request_id=request_obj.id).order_by(StatusChange.change_date.desc()).all()
    
    if status_history:
        history_data = [['Data/Hora', 'Status Anterior', 'Novo Status', 'Alterado por', 'Comentários']]
        
        for change in status_history:
            old_status = change.get_old_status_display() if change.old_status else 'Criado'
            new_status = change.get_new_status_display()
            comments = change.comments if change.comments else '-'
            
            history_data.append([
                change.change_date.strftime('%d/%m/%Y %H:%M'),
                old_status,
                new_status,
                change.changed_by_user.full_name,
                comments
            ])
        
        history_table = Table(history_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.5*inch, 1.4*inch])
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(history_table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_general_report(requests=None):
    """Gera relatório geral do sistema ou relatório filtrado"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        alignment=1,
        textColor=colors.darkblue
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    # Cabeçalho
    story.append(Paragraph("Escola Morvan Figueiredo", title_style))
    story.append(Paragraph("Relatório Geral de Aquisições", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Obter dados dos pedidos
    if requests is None:
        requests = AcquisitionRequest.query.all()
    
    # Estatísticas gerais
    total_requests = len(requests)
    total_users = User.query.filter_by(is_active=True).count()
    
    stats_data = [
        ['Total de Pedidos:', str(total_requests)],
        ['Usuários Ativos:', str(total_users)],
        ['Data do Relatório:', datetime.now().strftime('%d/%m/%Y às %H:%M')]
    ]
    
    story.append(Paragraph("Estatísticas Gerais", section_style))
    stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 20))
    
    # Pedidos por status
    story.append(Paragraph("Distribuição por Status", section_style))
    status_counts = {}
    for status_code, status_name in AcquisitionRequest.STATUS_CHOICES:
        count = sum(1 for req in requests if req.status == status_code)
        status_counts[status_name] = count
    
    status_data = [['Status', 'Quantidade', 'Percentual']]
    for status_name, count in status_counts.items():
        percentage = (count / total_requests * 100) if total_requests > 0 else 0
        status_data.append([status_name, str(count), f"{percentage:.1f}%"])
    
    status_table = Table(status_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(status_table)
    story.append(Spacer(1, 20))
    
    # Lista dos pedidos (filtrados se aplicável)
    report_title = "Lista de Pedidos Filtrados" if len(requests) < AcquisitionRequest.query.count() else "Lista Completa de Pedidos"
    story.append(Paragraph(report_title, section_style))
    
    if requests:
        request_data = [['ID', 'Título', 'Status', 'Criado por', 'Responsável', 'Data']]
        
        for req in requests:
            responsible = req.responsible.full_name if req.responsible else 'Não definido'
            request_data.append([
                f"#{req.id}",
                req.title[:40] + "..." if len(req.title) > 40 else req.title,
                req.get_status_display(),
                req.creator.full_name,
                responsible,
                req.created_at.strftime('%d/%m/%Y')
            ])
        
        request_table = Table(request_data, colWidths=[0.5*inch, 2.2*inch, 1*inch, 1.3*inch, 1.3*inch, 0.8*inch])
        request_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(request_table)
    
    # Rodapé
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=1,
        textColor=colors.grey
    )
    story.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", footer_style))
    story.append(Paragraph("Escola Morvan Figueiredo - Sistema de Controle de Aquisições", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer