import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader

from relacao_promotorias import promotoria, promotores
from datetime import datetime
import io

from openpyxl import load_workbook, Workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def append_to_excel_manually(filename, df_membros, df_substituido, sheet_name='Sheet1'):
    # Tentar abrir o arquivo existente, ou criar um novo se não existir
    try:
        workbook = load_workbook(filename)
        sheet = workbook[sheet_name]
    except FileNotFoundError:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = sheet_name

    # Encontrar a última linha preenchida na planilha para continuar adicionando dados
    startrow = sheet.max_row + 1

    # Adicionar os dados de df_membros
    sheet.append(["Promotoria Selecionada", "Promotor", "Antiguidade", "Data Selecionada",
                  "Órgão Ministerial da Última Correicão", "Registro de Pena"])
    for row in dataframe_to_rows(df_membros, index=False, header=False):
        sheet.append(row)

    # Adicionar um espaçamento entre as tabelas
    startrow = sheet.max_row + 2
    sheet.append([])  # Linha em branco para separar

    # Adicionar os dados de df_substituido
    sheet.append(
        ["Informações", "Localização das Informações", "Informação Conceito ou Registro Disciplinar", "Observações"])
    for row in dataframe_to_rows(df_substituido, index=False, header=False):
        sheet.append(row)

    # Salvar o arquivo atualizado
    workbook.save(filename)


# Função para salvar e baixar o arquivo Excel gerado manualmente
def append_to_excel_manually_and_download(df_membros, df_substituido, nome_arquivo, sheet_name='Sheet1'):
    # Criar um buffer de bytes para segurar o arquivo Excel
    output = io.BytesIO()

    # Tentar abrir o arquivo existente, ou criar um novo se não existir
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name

    # Adicionar os dados de df_membros
    sheet.append(["Promotoria Selecionada", "Promotor", "Antiguidade", "Data Selecionada",
                  "Órgão Ministerial da Última Correicão", "Registro de Pena"])
    for row in dataframe_to_rows(df_membros, index=False, header=False):
        sheet.append(row)

    # Adicionar um espaçamento entre as tabelas
    sheet.append([])  # Linha em branco para separar

    # Adicionar os dados de df_substituido
    sheet.append(
        ["Informações", "Localização das Informações", "Informação Conceito ou Registro Disciplinar", "Observações"])
    for row in dataframe_to_rows(df_substituido, index=False, header=False):
        sheet.append(row)

    # Salvar o arquivo no buffer de bytes
    workbook.save(output)

    # Voltar para o início do buffer
    output.seek(0)

    # Criar o botão de download para o arquivo Excel
    st.download_button(label="Download dados tratados como Excel",
                       data=output,
                       file_name=f"{nome_arquivo}_dados_tratados.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def membros_menu():
    promotoria_ordenada = sorted(promotoria)

    promotoria_selecionada = st.selectbox("Escolha o cargo do Candidato", promotoria_ordenada, key="promotoria_tab5")

    promotor = st.selectbox('Escolha o nome do Promotor:', promotores)

    antiguidade = st.number_input("Digite a posição na lista de antiguidade", min_value=1)

    data_selecionada = st.date_input('Data da Última Correição Ordinária', datetime.now().date())

    orgao_ministerial_ultima_correicao = st.selectbox("Escolha o cargo do Candidato", promotoria_ordenada,
                                                      key="orgao_correicao_tab5")

    registro_pena = st.selectbox("Registro de Pena(s) e/ou Procedimento(s) Disciplinare(s)", ['NADA CONSTA', 'CONSTA'])

    return (
    promotoria_selecionada, promotor, antiguidade, data_selecionada, orgao_ministerial_ultima_correicao, registro_pena)


def membros_pdf_extract():
    arquivos = st.file_uploader("Junte os PDF's aqui", type="PDF", accept_multiple_files=True)
    return arquivos


def get_page(texto_page: str, string: str) -> bool:
    if string.lower() in texto_page:
        return True
    return False



def get_value_by_partial_key(dictionary, partial_key):
    for key in dictionary:
        if partial_key in key:
            return dictionary[key]
    return None  # Retorna None se a chave parcial não for encontrada


def get_pages(pdf) -> int:
    reader = PdfReader(pdf)

    return len(reader.pages)


def extract_pdf(pdf, lista_verificacao: list) -> dict:
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
                result[item[0]] = i + 1

    return result


# Função para substituir placeholders pelos valores correspondentes da lista 'campos_preencher'
def substituir_placeholders(dados, campos_preencher):
    for chave, valores in dados.items():
        for i, valor in enumerate(valores):
            for arquivo, descricao, folhas in campos_preencher:
                if '{{' in valor:  # Verifica se há um placeholder no valor
                    # Substitui o placeholder pelo valor correspondente da lista campos_preencher
                    valor = valor.replace(f'{{{{{descricao}}}}}', folhas)
            dados[chave][i] = valor  # Atualiza o valor substituído no dicionário original
    return dados


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
