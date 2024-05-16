import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont





dic_namefile_and_text = {"extra sem impulsionamento": "Atuação extrajudicial (sem impulsionamentos há mais de 180 dias). Exceto NFs e PPs.",
                         "ips sem impulsionamento": "Inquéritos Policiais (sem impulsionamentos há mais de 90 dias)",
                         "judi com vista": "Atuação judicial (com mais de 60 dias). Exceto IPs.",
                         "relatório extraj- nf -pp": "Notícias de Fato e Procedimentos Preparatórios fora do prazo"
                         }

def verifica_chave_dic(nome):
    for chave in dic_namefile_and_text.keys():
        if chave in nome:
            return dic_namefile_and_text[chave]



def calculate_column_widths(df, font_size=6, min_col_width=0.5 * inch, max_col_width=1.5 * inch):
    """
    Calculate column widths based on the content of each column.
    """
    col_widths = []
    for col in df.columns:
        max_width = min_col_width
        for item in df[col].astype(str).values:
            width = len(item) * 0.1 * inch * font_size / 10  # Ajuste baseado no tamanho da fonte
            if width > max_width:
                max_width = width
            if max_width > max_col_width:
                max_width = max_col_width
        col_widths.append(max_width)
    return col_widths



def gerador_relatorio_pdf(dfs, df_names, promotoria="teste", filename="relatorio.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()  # Certifique-se de obter os estilos aqui

    today_date = date.today().strftime("%d/%m/%Y")

    header_texts = ["SALA DE ACOMPANHAMENTO VIRTUAL", promotoria, f"Consultas realizadas em {today_date}"]
    header_image = r"img/logo-mprn.png"

    # cabeçalho

    # Adicionar a imagem do cabeçalho
    img = Image(header_image)
    img.drawHeight = 1.0 * inch
    img.drawWidth = 3.0 * inch
    img.hAlign = 'CENTER'
    elements.append(img)
    elements.append(Spacer(1, 0.2 * inch))

    # Adicionar as linhas de texto do cabeçalho
    for text in header_texts:
        paragraph = Paragraph(text, styles['Title'])
        paragraph.hAlign = 'CENTER'
        elements.append(paragraph)
        elements.append(Spacer(1, 0.1 * inch))

        # Adicionar espaço após o cabeçalho
        elements.append(Spacer(0.1, 0.01 * inch))  # Espaço reduzido entre as linhas do cabeçalho

    for df, df_name in zip(dfs, df_names):
        # Adicionar o nome do DataFrame como um parágrafo

        texto = verifica_chave_dic(df_name)

        title = Paragraph(texto, styles['Heading2'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        data = [df.columns.tolist()] + df.values.tolist()
        col_widths = calculate_column_widths(df, font_size=8)  # Calcular as larguras das colunas com base no tamanho da fonte

        # Construir a tabela com fonte menor
        table = Table(data, colWidths=col_widths, repeatRows=1)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 4),  # Ajuste o tamanho da fonte
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))  # Add space between tables

    doc.build(elements)

    return filename

