import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import cv2

def setup_directories():
    """Cria diretórios necessários"""
    os.makedirs('models', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('temp', exist_ok=True)

def generate_pdf_report(results, os_data):  # CORREÇÃO: Mudar ordem dos parâmetros
    """Gera relatório PDF com os resultados"""
    setup_directories()
    # Nome do arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"reports/relatorio_betoneiras_{timestamp}.pdf"
    
    # Criar documento
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    title = Paragraph("RELATÓRIO DE DEVOLUÇÃO DE BETONEIRAS", title_style)
    story.append(title)
    
    # Dados da O.S.
    story.append(Paragraph("DADOS DA ORDEM DE SERVIÇO", styles['Heading2']))
    
    # CORREÇÃO: Usar get() para evitar KeyError
    os_info = [
        ["Funcionário:", os_data.get('funcionario', 'N/A')],
        ["Número da O.S.:", os_data.get('numero_os', 'N/A')],
        ["Cliente:", os_data.get('cliente', 'N/A')],
        ["Data do Cadastro:", os_data.get('data_cadastro', 'N/A')],
        ["Quantidade Esperada:", str(os_data.get('quantidade_esperada', 0))]
    ]
    
    os_table = Table(os_info, colWidths=[2*inch, 3*inch])
    os_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(os_table)
    story.append(Spacer(1, 20))
    
    # Resultados da detecção
    story.append(Paragraph("RESULTADOS DA DETECÇÃO", styles['Heading2']))
    
    detected_count = results.get('total_detected', 0)
    expected_count = os_data.get('quantidade_esperada', 0)
    
    status = "✅ OK - Quantidade correta" if detected_count == expected_count else "❌ INCONSISTENTE - Quantidade incorreta"
    
    detection_info = [
        ["Betoneiras Detectadas:", str(detected_count)],
        ["Betoneiras Esperadas:", str(expected_count)],
        ["Status:", status]
    ]
    
    detection_table = Table(detection_info, colWidths=[2*inch, 3*inch])
    detection_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(detection_table)
    story.append(Spacer(1, 20))
    
    # Lista de betoneiras detectadas
    betoneiras = results.get('betoneiras', [])
    if betoneiras:
        story.append(Paragraph("BETONEIRAS DETECTADAS", styles['Heading3']))
        
        betoneiras_data = [["ID", "Confiança", "Cor"]]
        for bet in betoneiras:
            betoneiras_data.append([
                bet.get('id', 'N/A'),
                f"{bet.get('conf', 0):.2f}",
                bet.get('cor', 'N/A')
            ])
        
        bet_table = Table(betoneiras_data, colWidths=[1*inch, 1.5*inch, 1.5*inch])
        bet_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(bet_table)
        story.append(Spacer(1, 20))
    
    # Imagem processada
    processed_image = results.get('processed_image')
    temp_img_path = None
    
    if processed_image is not None:
        story.append(Paragraph("IMAGEM PROCESSADA", styles['Heading3']))
        
        # Salvar imagem temporariamente
        temp_img_path = f"temp/processed_{timestamp}.jpg"
        try:
            cv2.imwrite(temp_img_path, processed_image)
            
            # Adicionar imagem ao PDF
            if os.path.exists(temp_img_path):
                img = Image(temp_img_path, width=6*inch, height=4.5*inch)
                story.append(img)
        except Exception as e:
            print(f"⚠️ Erro ao salvar imagem para PDF: {e}")
    
    # Rodapé
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    footer = Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", footer_style)
    story.append(footer)
    
    # Gerar PDF
    try:
        doc.build(story)
        
        # Limpar arquivo temporário
        if temp_img_path and os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        
        return pdf_filename
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF: {e}")
        return None