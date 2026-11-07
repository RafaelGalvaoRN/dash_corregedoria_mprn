import datetime
import re
from xml.sax.saxutils import escape

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph, Table, TableStyle

# Estilos de célula: fonte legível (9 pt) com quebra de linha automática
ESTILO_CABECALHO = ParagraphStyle("cab", fontName="Helvetica-Bold", fontSize=9, leading=11,
                                  textColor=colors.white, alignment=TA_CENTER)
ESTILO_CELULA = ParagraphStyle("cel", fontName="Helvetica", fontSize=9, leading=11, alignment=TA_LEFT)
ESTILO_CELULA_CENTRO = ParagraphStyle("cel_c", parent=ESTILO_CELULA, alignment=TA_CENTER)


def formatar_valor(valor):
    """Converte datas para dd/mm/aaaa e trata vazios."""
    if valor is None or (not isinstance(valor, str) and pd.api.types.is_scalar(valor) and pd.isna(valor)):
        return ""
    if isinstance(valor, np.datetime64):
        valor = pd.Timestamp(valor)
    if isinstance(valor, (pd.Timestamp, datetime.datetime, datetime.date)):
        return valor.strftime("%d/%m/%Y")
    texto = str(valor).strip()
    if texto.lower() in ("nan", "nat", "none", "<na>"):
        return ""
    # o app converte as planilhas para texto, então datas chegam como "2026-12-21 00:00:00"
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:[ T]00:00:00)?", texto)
    if m:
        return f"{m.group(3)}/{m.group(2)}/{m.group(1)}"
    return texto


def calcular_larguras(df, largura_total, padding=12):
    """
    Cada coluna recebe no mínimo a largura da sua maior "palavra" (nº de processo, data,
    palavra do cabeçalho), para nada ser cortado no meio. O espaço que sobra na página
    é distribuído para as colunas de texto longo (Classe, Assunto), que quebram linha.
    """
    def w(texto, bold=False):
        return stringWidth(texto, "Helvetica-Bold" if bold else "Helvetica", 9)

    minimos, desejados = [], []
    for col in df.columns:
        valores = [formatar_valor(v) for v in df[col].tolist()]
        palavras_cab = str(col).split() or [""]
        palavras_cel = [p for v in valores for p in v.split()] or [""]
        minimo = max(max(w(p, True) for p in palavras_cab), max(w(p) for p in palavras_cel)) + padding
        desejado = max([w(str(col), True)] + [w(v) for v in valores]) + padding
        minimos.append(minimo)
        desejados.append(max(desejado, minimo))

    if sum(desejados) <= largura_total:
        # cabe tudo em uma linha: distribui a sobra proporcionalmente
        fator = largura_total / sum(desejados)
        return [d * fator for d in desejados]

    sobra = largura_total - sum(minimos)
    if sobra <= 0:
        # caso extremo (muitas colunas): encolhe proporcionalmente
        fator = largura_total / sum(minimos)
        return [m * fator for m in minimos]

    extras = [d - m for d, m in zip(desejados, minimos)]
    total_extra = sum(extras)
    return [m + sobra * e / total_extra for m, e in zip(minimos, extras)]


def montar_tabela(df, largura_total):
    """Tabela com quebra de linha nas células, fonte 9 pt e larguras ajustadas à página."""
    colunas_centralizadas = {i for i, c in enumerate(df.columns)
                             if any(k in str(c).lower() for k in ("ordem", "número", "numero",
                                                                    "prazo", "data", "dias"))}

    cabecalho = [Paragraph(escape(str(c)), ESTILO_CABECALHO) for c in df.columns]
    linhas = []
    for registro in df.itertuples(index=False):
        linhas.append([
            Paragraph(escape(formatar_valor(v)),
                      ESTILO_CELULA_CENTRO if i in colunas_centralizadas else ESTILO_CELULA)
            for i, v in enumerate(registro)
        ])

    tabela = Table([cabecalho] + linhas,
                   colWidths=calcular_larguras(df, largura_total),
                   repeatRows=1)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.beige, colors.whitesmoke]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabela
