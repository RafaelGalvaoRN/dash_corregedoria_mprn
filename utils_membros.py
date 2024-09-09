import streamlit as st

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter

def membros_pdf_extract():
    arquivos = st.file_uploader("Junte os PDF's aqui", type="PDF", accept_multiple_files=True)
    return arquivos


def get_page(texto_page: str, string: str) -> bool:
    if string.lower() in texto_page:
        return True
    return False


def extract_pdf(pdf, lista_verificacao: list) -> dict :
    """
    extrai texto de pdf e verifica pagina inicial e pagina final do relatório procurado
    :param pdf: texto a ser extraído
    :param lista_verificacao: lsita com tupla, contendo o tipo da página (inicial ou final) e o texto contido na
    página
    :return: dict contendo os dados encontrados
    """

    # Criando um objeto PdfReader
    reader = PdfReader(pdf)

    # Inicializando uma variável para armazenar o texto extraído
    full_text = ""

    result = {}

    # Iterando sobre todas as páginas do PDF
    for i in range(len(reader.pages)):
        # Obtendo uma página específica do arquivo PDF
        page = reader.pages[i]

        # Extraindo o texto da página
        text = page.extract_text().lower()

        for item in lista_verificacao:
            if get_page(text, item[1]):
                result[item[0]] = i+1

    return result


def preencher_pdf(output_pdf_path, lista_campos):
    """
    Preenche um PDF com campos específicos (números de páginas, etc.)
    :param output_pdf_path: Caminho para o arquivo de saída (PDF preenchido)
    :param lista_campos: Lista com os textos e coordenadas a serem inseridos no PDF
    """
    # Crie um novo PDF com o texto preenchido nos locais desejados
    c = canvas.Canvas(output_pdf_path, pagesize=letter)

    # Iterando sobre a lista de campos e preenchendo o PDF
    for campo in lista_campos:
        texto, x, y = campo  # Texto a ser preenchido e coordenadas
        c.drawString(x, y, texto)  # Posição X, Y no PDF para colocar o texto

    # Finaliza e salva o PDF
    c.save()