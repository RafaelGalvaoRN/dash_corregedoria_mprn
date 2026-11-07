import datetime
from functools import partial
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import date
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from icecream import ic
from tabela_pdf import montar_tabela, ESTILO_CELULA

dic_namefile_and_text = {
    "extra sem impulsionamento": "Atuação extrajudicial (sem impulsionamentos há mais de 180 dias). Exceto NFs e PPs.",
    "ips sem impulsionamento": "Inquéritos Policiais (sem impulsionamentos há mais de 180 dias)",
    "judi com vista": "Atuação judicial (com mais de 60 dias). Exceto IPs.",
    "relatório extraj": "Notícias de Fato e Procedimentos Preparatórios fora do prazo"
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


def classificar_arquivo(nome):
    """Indica se o arquivo compõe o passivo extrajudicial ('extra') ou judicial ('jud')."""
    nome = nome.lower()
    if "extra sem impulsionamento" in nome or "relatório extraj" in nome:
        return "extra"
    if "judi com vista" in nome or "ips sem impulsionamento" in nome:
        return "jud"
    return None


def calcular_passivos(dfs, df_names):
    """
    Soma o passivo (quantidade de linhas) por categoria e registra quais categorias
    tiveram arquivo enviado. Os IPs sem impulsionamento compõem o passivo judicial.
    """
    resumo = {"extra": {"enviado": False, "passivo": 0},
              "jud": {"enviado": False, "passivo": 0, "inclui_ips": False}}
    for df, nome in zip(dfs, df_names):
        categoria = classificar_arquivo(nome)
        if categoria is None:
            continue
        resumo[categoria]["enviado"] = True
        resumo[categoria]["passivo"] += len(df.index)
        if "ips sem impulsionamento" in nome.lower():
            resumo["jud"]["inclui_ips"] = True
    return resumo


def calcula_indice_percentual_atrado(qtd_acervo, qtd_passivo):
    """Índice de atraso = passivo / acervo x 100. Retorna None se o acervo não foi informado."""
    if not qtd_acervo:
        return None
    return round(qtd_passivo / qtd_acervo * 100, 2)


def formatar_percentual(valor):
    if valor is None:
        return "Acervo não informado"
    return f"{valor:.2f}".replace(".", ",") + "%"


MARGEM = 2 * cm

ESTILO_CAB_INSTITUICAO = ParagraphStyle("cab_inst", fontName="Helvetica-Bold", fontSize=14, leading=17,
                                        alignment=TA_CENTER)
ESTILO_CAB_SALA = ParagraphStyle("cab_sala", fontName="Helvetica", fontSize=11, leading=14, alignment=TA_CENTER)
ESTILO_CAB_PROMOTORIA = ParagraphStyle("cab_prom", fontName="Helvetica-Bold", fontSize=13, leading=16,
                                       alignment=TA_CENTER, spaceBefore=4)
ESTILO_CAB_DATA = ParagraphStyle("cab_data", fontName="Helvetica", fontSize=9, leading=12, alignment=TA_CENTER,
                                 textColor=colors.grey, spaceAfter=14)
# keepWithNext: o título nunca fica sozinho no pé da página, separado da sua tabela
ESTILO_SECAO = ParagraphStyle("secao", fontName="Helvetica-Bold", fontSize=12, leading=15, spaceBefore=14,
                              spaceAfter=2, keepWithNext=1)
ESTILO_TOTAL = ParagraphStyle("total", fontName="Helvetica", fontSize=9, leading=12, textColor=colors.grey,
                              spaceAfter=6, keepWithNext=1)
ESTILO_VAZIO = ParagraphStyle("vazio", fontName="Helvetica-Oblique", fontSize=10, leading=13, spaceAfter=6)
ESTILO_OBS = ParagraphStyle("obs", fontName="Helvetica-Oblique", fontSize=9, leading=12, spaceBefore=4)


class CanvasNumerado(canvas.Canvas):
    """Canvas que escreve o rodapé com 'Página X de Y' em todas as páginas."""

    def __init__(self, *args, texto_rodape="", **kwargs):
        super().__init__(*args, **kwargs)
        self._paginas = []
        self._texto_rodape = texto_rodape

    def showPage(self):
        self._paginas.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._paginas)
        for estado in self._paginas:
            self.__dict__.update(estado)
            self._desenhar_rodape(total)
            super().showPage()
        super().save()

    def _desenhar_rodape(self, total):
        largura = self._pagesize[0]
        self.saveState()
        self.setStrokeColor(colors.lightgrey)
        self.line(MARGEM, 1.5 * cm, largura - MARGEM, 1.5 * cm)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.grey)
        self.drawString(MARGEM, 1.0 * cm, self._texto_rodape)
        self.drawRightString(largura - MARGEM, 1.0 * cm, f"Página {self._pageNumber} de {total}")
        self.restoreState()


def _texto_quantidade(qtd):
    return f"Total: {qtd} procedimento" + ("" if qtd == 1 else "s")


def _estilo_tabela_simples():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])


def gerador_relatorio_pdf(dfs, df_names, promotoria="teste", filename="relatorio.pdf",
                          qtd_acervo_jud=0, qtd_acervo_extra=0):
    agora = datetime.datetime.now()
    texto_rodape = f"Corregedoria-Geral do MPRN · {promotoria} · gerado em {agora.strftime('%d/%m/%Y %H:%M')}"

    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=MARGEM, rightMargin=MARGEM,
                            topMargin=1.5 * cm, bottomMargin=2.2 * cm,
                            title=f"Relatório Corregedoria - {promotoria}")
    elements = []
    styles = getSampleStyleSheet()

    # ---------------- cabeçalho ----------------
    img = Image(r"img/logo-mprn.png")
    altura_logo = 0.8 * inch
    img.drawWidth = altura_logo * img.imageWidth / img.imageHeight  # mantém a proporção do logo
    img.drawHeight = altura_logo
    img.hAlign = 'CENTER'
    elements.append(img)
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(Paragraph("CORREGEDORIA GERAL DO MPRN", ESTILO_CAB_INSTITUICAO))
    elements.append(Paragraph("SALA DE ACOMPANHAMENTO VIRTUAL", ESTILO_CAB_SALA))
    elements.append(Paragraph(escape(str(promotoria)), ESTILO_CAB_PROMOTORIA))
    elements.append(Paragraph(f"Consultas realizadas em {agora.strftime('%d/%m/%Y')}", ESTILO_CAB_DATA))

    # ---------------- resumo ----------------
    resumo = calcular_passivos(dfs, df_names)
    indices = []
    for chave, rotulo, acervo in [("extra", "Extrajudicial", qtd_acervo_extra),
                                  ("jud", "Judicial", qtd_acervo_jud)]:
        if resumo[chave]["enviado"]:
            passivo = resumo[chave]["passivo"]
            indices.append((chave, rotulo, acervo, passivo, calcula_indice_percentual_atrado(acervo, passivo)))

    elements.append(Paragraph("RESUMO", ESTILO_SECAO))
    dados_resumo = [["Seção", "Procedimentos"]]
    for df, df_name in zip(dfs, df_names):
        dados_resumo.append([Paragraph(escape(verifica_chave_dic(df_name)), ESTILO_CELULA), len(df.index)])
    for _, rotulo, _, _, percentual in indices:
        dados_resumo.append([Paragraph(f"<b>Índice de atraso {rotulo.lower()}</b>", ESTILO_CELULA),
                             formatar_percentual(percentual)])
    tabela_resumo = Table(dados_resumo, colWidths=[doc.width * 0.72, doc.width * 0.28], repeatRows=1)
    estilo_resumo = _estilo_tabela_simples()
    estilo_resumo.add('ALIGN', (0, 0), (0, 0), 'LEFT')
    tabela_resumo.setStyle(estilo_resumo)
    elements.append(tabela_resumo)

    # ---------------- seções ----------------
    for df, df_name in zip(dfs, df_names):
        elements.append(Paragraph(escape(verifica_chave_dic(df_name)), ESTILO_SECAO))
        elements.append(Paragraph(_texto_quantidade(len(df.index)), ESTILO_TOTAL))

        if df.empty:
            elements.append(Paragraph("Nenhum procedimento encontrado.", ESTILO_VAZIO))
        else:
            # tabela com fonte 9 pt, quebra de linha nas células e larguras ajustadas à página
            elements.append(montar_tabela(df, doc.width))

    # ---------------- índices de atraso ----------------
    for chave, rotulo, acervo, passivo, percentual in indices:
        elements.append(Paragraph(f"TABELA DE PERCENTUAL DE ÍNDICE DE ATRASO DO {rotulo.upper()}", ESTILO_SECAO))

        data = [['Acervo Total', 'Qtd de Passivo', 'Índice de Atraso'],
                [acervo if acervo else "Não informado", passivo, formatar_percentual(percentual)]]
        table = Table(data, colWidths=[doc.width / 3] * 3, repeatRows=1)
        table.setStyle(_estilo_tabela_simples())
        elements.append(table)

        if chave == "jud" and resumo["jud"]["inclui_ips"]:
            elements.append(Paragraph("Obs.: o passivo judicial inclui os Inquéritos Policiais sem impulsionamento.",
                                      ESTILO_OBS))

    doc.build(elements, canvasmaker=partial(CanvasNumerado, texto_rodape=texto_rodape))

    return filename
