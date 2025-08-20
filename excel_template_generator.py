from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from models import User, AcquisitionRequest
import io

def generate_import_template():
    """Gera o modelo Excel para importação em lote de pedidos"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Modelo de Importação"
    
    # Header styling
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                   top=Side(style='thin'), bottom=Side(style='thin'))
    
    # Headers
    headers = [
        "Título*", "Descrição*", "Status*", "Data da Solicitação*",
        "Valor Estimado", "Valor Final", "Responsável (Nome)", "Observações"
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = border
        
        # Set column width
        if header in ["Título*", "Descrição*"]:
            ws.column_dimensions[get_column_letter(col)].width = 40
        elif header == "Observações":
            ws.column_dimensions[get_column_letter(col)].width = 30
        else:
            ws.column_dimensions[get_column_letter(col)].width = 20
    
    # Add example rows
    example_data = [
        [
            "Compra de Material de Escritório",
            "Aquisição de canetas, papéis e materiais básicos para o escritório administrativo",
            "orcamento",
            "2025-08-20",
            "150.00",
            "",
            "Edson Lemes",
            "Urgente para início do semestre"
        ],
        [
            "Equipamento de Informática",
            "Computadores para laboratório de informática - 10 unidades",
            "fase_compra",
            "2025-08-15",
            "25000.00",
            "24500.00",
            "Edson Lemes",
            ""
        ]
    ]
    
    for row_idx, row_data in enumerate(example_data, 2):
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=value)
            cell.border = border
            
            # Light background for examples
            cell.fill = PatternFill(start_color="F0F8FF", end_color="F0F8FF", fill_type="solid")
    
    # Add instructions sheet
    ws_instructions = wb.create_sheet("Instruções")
    
    instructions = [
        ["INSTRUÇÕES PARA IMPORTAÇÃO EM LOTE", ""],
        ["", ""],
        ["1. Campos obrigatórios (marcados com *):", ""],
        ["   • Título: Nome do pedido (mínimo 5 caracteres)", ""],
        ["   • Descrição: Descrição detalhada (mínimo 10 caracteres)", ""],
        ["   • Status: Deve ser um dos valores abaixo:", ""],
        ["   • Data da Solicitação: Formato AAAA-MM-DD (ex: 2025-08-20)", ""],
        ["     - orcamento (Orçamento)", ""],
        ["     - fase_compra (Fase de Compra)", ""],
        ["     - a_caminho (A Caminho)", ""],
        ["     - finalizado (Finalizado)", ""],
        ["", ""],
        ["2. Campos opcionais:", ""],
        ["   • Valor Estimado: Valor em formato numérico (ex: 100.50)", ""],
        ["   • Valor Final: Valor em formato numérico (ex: 95.00)", ""],
        ["   • Responsável: Nome completo do usuário responsável", ""],
        ["   • Observações: Comentários adicionais", ""],
        ["", ""],
        ["3. Observações importantes:", ""],
        ["   • Remova as linhas de exemplo antes de importar", ""],
        ["   • Valores monetários devem usar ponto como separador decimal", ""],
        ["   • Datas devem estar no formato AAAA-MM-DD", ""],
        ["   • Se o responsável não for encontrado, o campo ficará vazio", ""],
        ["   • Máximo de 100 pedidos por importação", ""],
        ["", ""],
        ["4. Status disponíveis:", ""]
    ]
    
    # Add status list to instructions
    for status_code, status_name in AcquisitionRequest.STATUS_CHOICES:
        instructions.append([f"   • {status_code}: {status_name}", ""])
    
    for row_idx, (col1, col2) in enumerate(instructions, 1):
        ws_instructions.cell(row=row_idx, column=1, value=col1)
        ws_instructions.cell(row=row_idx, column=2, value=col2)
        
        if row_idx == 1:  # Title
            ws_instructions.cell(row=row_idx, column=1).font = Font(bold=True, size=14)
        elif col1.startswith(("1.", "2.", "3.", "4.")):  # Section headers
            ws_instructions.cell(row=row_idx, column=1).font = Font(bold=True)
    
    # Set column widths for instructions
    ws_instructions.column_dimensions['A'].width = 60
    ws_instructions.column_dimensions['B'].width = 20
    
    return wb

def process_import_file(file_path, current_user):
    """Processa o arquivo Excel importado e retorna lista de pedidos para criação"""
    from openpyxl import load_workbook
    
    try:
        wb = load_workbook(file_path)
        ws = wb.active
        
        pedidos = []
        erros = []
        
        # Skip header row
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
            if not any(row):  # Skip empty rows
                continue
                
            titulo, descricao, status, data_solicitacao, valor_estimado, valor_final, responsavel_nome, observacoes = row[:8]
            
            # Validate required fields
            if not titulo or len(str(titulo).strip()) < 5:
                erros.append(f"Linha {row_idx}: Título é obrigatório e deve ter pelo menos 5 caracteres")
                continue
                
            if not descricao or len(str(descricao).strip()) < 10:
                erros.append(f"Linha {row_idx}: Descrição é obrigatória e deve ter pelo menos 10 caracteres")
                continue
                
            if not status or status not in [s[0] for s in AcquisitionRequest.STATUS_CHOICES]:
                erros.append(f"Linha {row_idx}: Status inválido. Use: {', '.join([s[0] for s in AcquisitionRequest.STATUS_CHOICES])}")
                continue
                
            # Validate and parse date
            try:
                if data_solicitacao:
                    from datetime import datetime
                    if isinstance(data_solicitacao, str):
                        data_parsed = datetime.strptime(data_solicitacao, '%Y-%m-%d').date()
                    else:
                        data_parsed = data_solicitacao
                else:
                    erros.append(f"Linha {row_idx}: Data da solicitação é obrigatória")
                    continue
            except (ValueError, TypeError):
                erros.append(f"Linha {row_idx}: Data inválida '{data_solicitacao}'. Use formato AAAA-MM-DD")
                continue
            
            # Find responsible user
            responsible_id = None
            if responsavel_nome:
                responsible = User.query.filter_by(full_name=responsavel_nome.strip()).first()
                if responsible:
                    responsible_id = responsible.id
                else:
                    erros.append(f"Linha {row_idx}: Responsável '{responsavel_nome}' não encontrado (será deixado vazio)")
            
            # Parse values
            try:
                valor_estimado_parsed = float(valor_estimado) if valor_estimado else None
            except (ValueError, TypeError):
                valor_estimado_parsed = None
                if valor_estimado:
                    erros.append(f"Linha {row_idx}: Valor estimado inválido '{valor_estimado}' (será ignorado)")
            
            try:
                valor_final_parsed = float(valor_final) if valor_final else None
            except (ValueError, TypeError):
                valor_final_parsed = None
                if valor_final:
                    erros.append(f"Linha {row_idx}: Valor final inválido '{valor_final}' (será ignorado)")
            
            pedidos.append({
                'titulo': str(titulo).strip(),
                'descricao': str(descricao).strip(),
                'status': status,
                'data_solicitacao': data_parsed,
                'valor_estimado': valor_estimado_parsed,
                'valor_final': valor_final_parsed,
                'responsible_id': responsible_id,
                'observacoes': str(observacoes).strip() if observacoes else None,
                'linha': row_idx
            })
            
            # Limit to 100 requests
            if len(pedidos) >= 100:
                erros.append("Limitado a 100 pedidos por importação. Pedidos excedentes foram ignorados.")
                break
        
        return pedidos, erros
        
    except Exception as e:
        return [], [f"Erro ao processar arquivo: {str(e)}"]