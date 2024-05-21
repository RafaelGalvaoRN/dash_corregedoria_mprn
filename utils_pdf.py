import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import date
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from icecream import ic

dic_namefile_and_text = {
    "extra sem impulsionamento": "Atuação extrajudicial (sem impulsionamentos há mais de 180 dias). Exceto NFs e PPs.",
    "ips sem impulsionamento": "Inquéritos Policiais (sem impulsionamentos há mais de 90 dias)",
    "judi com vista": "Atuação judicial (com mais de 60 dias). Exceto IPs.",
    "relatório extraj - nf -pp": "Notícias de Fato e Procedimentos Preparatórios fora do prazo"
}


def verifica_chave_dic(nome):
    for chave in dic_namefile_and_text.keys():
        if chave in nome:
            return dic_namefile_and_text[chave]

    return "Nome do arquivo não encontrado"



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


def calcula_indice_percentual_atrado(qtd_passivo, qtd_indices):

    try:
        percentual = (qtd_indices / qtd_passivo) * 100
    except ZeroDivisionError:
        return "Erro: Passivo informado foi zero"

    return round(percentual, 2)


def gerador_relatorio_pdf(dfs, df_names, promotoria="teste", filename="relatorio.pdf",
                          qtd_acervo_jud=0, qtd_acervo_extra=0):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()  # Certifique-se de obter os estilos aqui

    today_date = date.today().strftime("%d/%m/%Y")

    header_texts = ["CORREGEDORIA GERAL DO MPRN", "SALA DE ACOMPANHAMENTO VIRTUAL", promotoria,
                    f"Consultas realizadas em {today_date}"]
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



    passivo_extra = 0
    passivo_jud = 0


    for df, df_name in zip(dfs, df_names):
        # Adicionar o nome do DataFrame como um parágrafo


        texto = verifica_chave_dic(df_name)


        if any(name in df_name.lower() for name in ["extra sem impulsionamento", "relatório extraj"]):
           passivo_extra += len(df.index)
        else:
            passivo_jud += len(df.index)





        title = Paragraph(texto, styles['Heading2'])
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        data = [df.columns.tolist()] + df.values.tolist()
        col_widths = calculate_column_widths(df,
                                             font_size=8)  # Calcular as larguras das colunas com base no tamanho da fonte

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

    if passivo_extra > 0:
        percentual_atraso = calcula_indice_percentual_atrado(qtd_acervo_extra, passivo_extra)


        #CONSTRUÇAO DA COLUNA DE PERCENTUAL
        # Adicionar espaço após o cabeçalho
        elements.append(Spacer(0.1, 0.01 * inch))  # Espaço reduzido entre as linhas do cabeçalho

        paragraph = Paragraph("TABELA DE PERCENTUAL DE ÍNDICE DE ATRASO DO EXTRAJUDICIAL", styles['Heading2'])
        paragraph.hAlign = 'CENTER'
        elements.append(paragraph)

        data =  [['Acervo Total', 'Qtd de Passivo', 'Percentual Atraso %'],
                 [qtd_acervo_extra, passivo_extra, percentual_atraso]  # Adicione seus dados reais aqui
                 ]

        # Largura das colunas (ajuste conforme necessário)
        col_widths = [2 * inch, 2 * inch, 2 * inch]


        # Criação da tabela
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Estilo da tabela
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Ajuste o tamanho da fonte
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

        # Aplicar o estilo à tabela
        table.setStyle(style)

        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))  # Adiciona espaço entre as tabelas

    if passivo_jud > 0:
        percentual_atraso = calcula_indice_percentual_atrado(qtd_acervo_jud, passivo_jud)

        # CONSTRUÇAO DA COLUNA DE PERCENTUAL
        # Adicionar espaço após o cabeçalho
        elements.append(Spacer(0.1, 0.01 * inch))  # Espaço reduzido entre as linhas do cabeçalho

        paragraph = Paragraph("TABELA DE PERCENTUAL DE ÍNDICE DE ATRASO DO JUDICIAL", styles['Heading2'])
        paragraph.hAlign = 'CENTER'
        elements.append(paragraph)

        data = [['Acervo Total', 'Qtd de Passivo', 'Percentual Atraso %'],
                [qtd_acervo_jud, passivo_jud, percentual_atraso]  # Adicione seus dados reais aqui
                ]

        # Largura das colunas (ajuste conforme necessário)
        col_widths = [2 * inch, 2 * inch, 2 * inch]

        # Criação da tabela
        table = Table(data, colWidths=col_widths, repeatRows=1)

        # Estilo da tabela
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),  # Ajuste o tamanho da fonte
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

        # Aplicar o estilo à tabela
        table.setStyle(style)

        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))  # Adiciona espaço entre as tabelas

    doc.build(elements)

    return filename
