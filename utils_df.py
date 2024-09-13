import pandas as pd
import io
import streamlit as st
from zipfile import ZipFile
import os
import tempfile


def convert_collum_date(df, colunas):
    for coluna in colunas:
        df[coluna] = pd.to_datetime(df[coluna], errors='coerce')

        # Após a conversão, você pode então formatar essas colunas como desejar
        df[coluna] = df[coluna].dt.strftime('%d-%m-%Y')

    return df


def apply_pipeline(dataframe, functions):
    for function in functions:
        dataframe = function(dataframe)

    return dataframe


def extract_normalize(uploaded_file):
    df = extract(uploaded_file)

    df = normalize_column_types(df)

    df = normalize_columns(df)  # Normaliza os nomes das colunas
    df = remove_empty_rows(df)
    df = remove_empty_columns(df)
    return df


def extract(file_to_extract):
    if file_to_extract.name.split(".")[-1] == "xlsx":
        extracted_data = pd.read_excel(file_to_extract)
    return extracted_data


# Função para normalizar os nomes das colunas
def normalize_columns(df):
    df.columns = df.columns.str.strip()  # Remove espaços em branco extras
    df.columns = df.columns.str.lower()  # Converte todas as colunas para minúsculas
    return df


def remove_nan_columns(df):
    # Remover colunas cujos nomes começam com 'Unnamed'
    df = df.loc[:, ~df.columns.str.startswith('nan')]
    return df


# Função para remover linhas completamente em branco ou linhas com apenas valores de filtro
def remove_empty_rows(df):
    # Remove linhas completamente em branco
    df = df.dropna(how='all')
    # Remove linhas que contenham apenas valores de filtro
    return df


def normalize_column_types(df):
    # Converte todas as colunas para string para evitar problemas de tipo
    for col in df.columns:
        df[col] = df[col].astype(str)

    return df


def remove_empty_columns(df):
    # Remove colunas completamente em branco
    df = df.dropna(axis=1, how='all')
    return df


def rename_duplicate_columns(df):
    # Criar um novo índice para as colunas para garantir unicidade
    cols = pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique():
        # Gerar novos nomes para colunas duplicadas com numeração adequada
        cols[cols == dup] = [f"{dup}_{i + 1}" if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns = cols
    return df


def remove_second_table_intervalos(df):
    # Encontre o índice da linha onde "intervalos" está presente
    intervalos_index = None
    for idx, row in df.iterrows():
        if any('intervalos' in str(value).strip().lower() for value in row.values):
            intervalos_index = idx
            break

    # Mantenha as linhas antes do índice de "intervalos"
    if intervalos_index is not None:
        df = df.loc[:intervalos_index - 1]  # Usa 'loc' para redefinir o DataFrame excluindo as linhas indesejadas

    return df


def process_sections(df):
    # Identificar todas as linhas onde qualquer célula contém a palavra "Classe"
    header_indices = df.index[df.apply(lambda row: row.str.contains('Classe', na=False).any(), axis=1)].tolist()

    # Verificar se há pelo menos um cabeçalho com 'Classe'
    if not header_indices:
        raise ValueError("Não foi encontrada nenhuma linha de cabeçalho com 'Classe'. Verifique o DataFrame.")

    # Função para extrair dados até a primeira linha em branco após o cabeçalho
    def extract_section(df, start_index):
        # Encontrar o índice da primeira linha completamente nula após o cabeçalho
        empty_rows = df[start_index:].isnull().all(axis=1)
        if empty_rows.any():
            end_index = df[start_index:].index[empty_rows][0]
        else:
            end_index = df.shape[0]  # Se não houver linha em branco, usar o final do DataFrame
        return df.iloc[start_index:end_index]

    # Processar seções com base no número de cabeçalhos encontrados
    if len(header_indices) == 1:
        # Se houver apenas um cabeçalho 'Classe'
        section_df = extract_section(df, header_indices[0] + 1)
        return section_df
    else:
        # Se houver mais de um cabeçalho 'Classe'
        combined_df = pd.DataFrame()
        for i in header_indices:
            section_df = extract_section(df, i + 1)
            combined_df = pd.concat([combined_df, section_df], ignore_index=True)

        return combined_df


def select_nf_pp_data_in_df(df, column_index=0):
    # Lista de inícios de tipos de classe válidos
    valid_starts = ['Notícia de Fato', 'Procedimento Preparatório']

    # Filtrar o DataFrame pela coluna especificada, mantendo linhas cujo valor inicie com um dos prefixos válidos
    filtered_df = df[
        df.iloc[:, column_index].apply(lambda x: any(x.startswith(prefix) for prefix in valid_starts if pd.notna(x)))]

    # exclue algumas colunas, em branco
    filtered_df.drop(filtered_df.columns[[1, 2, 4, 6,
                                          8, 9, 11, 12, 15, 16, 18]], axis=1, inplace=True)

    # insere nome das colunas
    column_names = [
        "Classe", "Número Processo", "Instauração", "Última",
        "30 Dias", "120 Dias", "Obervação", "dentro /fora", "dias fora"
    ]

    filtered_df.columns = column_names

    # Converter todas as instâncias da string "nan" para verdadeiro NaN
    filtered_df['Número Processo'] = filtered_df['Número Processo'].replace('nan', pd.NA)

    # ecxclui linhas dos filtros NF e PP
    filtered_df.dropna(subset=['Número Processo'], inplace=True)

    return filtered_df


def remove_to_classe(df):
    classe_index = None
    for idx, row in df.iterrows():
        if 'Classe' in row.values:
            classe_index = idx
            break

    # Elimine as linhas até o índice da classe
    if classe_index is not None:
        # Defina a linha correspondente ao 'classe_index' como os novos nomes das colunas
        df.columns = df.iloc[classe_index]
        # Elimine as linhas até e incluindo o índice da 'Classe'
        df = df.iloc[classe_index + 1:]  # Comece do próximo após 'Classe'
    return df


def filtrar_fora_prazo(df, procedimento, prazo_maximo):
    # Filtra onde o procedimento é 'NF' e os dias estão acima do prazo máximo
    df_filtrado = df[(df['classe'] == procedimento) & (df['dias_nf'] > prazo_maximo)]
    return df_filtrado


def extract_last_date(df):
    # Converter todos os nomes de coluna para minúsculas
    df.columns = [col.lower() for col in df.columns]

    # Extração da data assumindo que está sempre no formato 'dd/mm/yyyy' no final da string
    # A coluna agora é acessada em minúsculas
    df['data do último impulsionamento'] = df['último impulsionamento'].str.extract(r'(\d{2}/\d{2}/\d{4})')

    return df


def nf_pp_fora_prazo(df):
    # Filtra onde o procedimento é 'NF' e os dias estão acima do prazo máximo
    df_filtrado = df[(df['dentro /fora'] == "F")]
    return df_filtrado


def gerar_dataframe_filtrado(df, colunas):
    # Cria um novo dataframe selecionando as colunas desejadas
    df_resultado = df[colunas].copy()

    # Adiciona uma nova coluna 'Número de Ordem' que contém o índice + 1 (para começar de 1 em vez de 0)
    df_resultado['Número de Ordem'] = range(1, len(df_resultado) + 1)

    colunas.insert(0, "Número de Ordem")

    # Reordena as colunas para colocar 'Número de Ordem' como a primeira coluna
    df_resultado = df_resultado[colunas]

    return df_resultado


def title_case_column(df):
    df.columns = df.columns.str.title()
    return df


def gerar_dataframe_filtrado_extra_nf(df):
    # Cria um novo dataframe selecionando as colunas desejadas
    df_resultado = df[['classe', 'número processo', 'instauração',
                       '30 dias', '120 dias', 'dentro /fora', 'dias fora']].copy()

    # Adiciona uma nova coluna 'Número de Ordem' que contém o índice + 1 (para começar de 1 em vez de 0)
    df_resultado['Número de Ordem'] = range(1, len(df_resultado) + 1)

    # Reordena as colunas para colocar 'Número de Ordem' como a primeira coluna
    colunas = ['Número de Ordem', 'classe', 'número processo', 'instauração',
               '30 dias', '120 dias', 'dentro /fora', 'dias fora']
    df_resultado = df_resultado[colunas]

    return df_resultado


def exclude_specific_classes(df):
    classes_to_exclude = [
        'Notícia de Fato',
        'Procedimentos Preparatórios',
        'Procedimento Preparatório',
        'Procedimento Preparatorio',
        'Procedimentos Preparatorios',
        'Procedimento Preparatorio'
    ]

    # Filtra o DataFrame para excluir linhas onde 'Classe' é 'Notícia de Fato' ou 'Procedimentos Preparatórios'
    df_filtered = df[~df['Classe'].isin(classes_to_exclude)]
    return df_filtered


def filter_df_by_criteria(df):
    # Excluir entradas onde 'Classe' é 'Inquérito Policial'
    df = df[df['classe'] != 'Inquérito Policial']

    # Converter 'Dias Andamento' para int antes de filtrar
    # Usar pd.to_numeric para conversão segura, convertendo erros em NaN (que serão filtrados fora)
    df['dias andamento'] = pd.to_numeric(df['dias andamento'], errors='coerce')

    # Incluir apenas entradas onde 'Dias Andamento' é igual ou superior a 60
    df = df[df['dias andamento'] > 60]

    return df


def filter_df_by_ip(df):
    df = df[df['classe'] == "Inquérito Policial"]
    return df


def download_table(df):
    # Criar um buffer de bytes para segurar o arquivo Excel
    output = io.BytesIO()
    # Usar o Pandas para escrever o DataFrame para o buffer como um arquivo Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    # Voltar para o início do buffer
    output.seek(0)

    # Criar o botão de download para o arquivo Excel
    st.download_button(label="Download dados tratados como Excel",
                       data=output,
                       file_name=f"dados_tratados.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def gerar_arquivos_excel(dfs, nomes):
    """Gera arquivos Excel temporários a partir de uma lista de DataFrames."""
    paths = []
    for df, nome in zip(dfs, nomes):
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, f"{nome}.xlsx")
        df.to_excel(path, index=False)
        paths.append(path)
    return paths


def read_excel(file_path: str) -> list:
    df = pd.read_excel(file_path)

    lista = df.iloc[:,1].tolist()

    return lista






def compactar_e_download(dfs, nomes, pdf_path):
    # Criar diretório temporário para guardar os arquivos Excel
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "arquivos_tratados.zip")

    # Criar arquivos Excel dentro do diretório temporário
    paths = [pdf_path]
    for df, nome in zip(dfs, nomes):
        path = os.path.join(temp_dir, f"{nome}.xlsx")
        df.to_excel(path, index=False)
        paths.append(path)

    # Compactar todos os arquivos Excel em um arquivo ZIP
    with ZipFile(zip_path, 'w') as zipf:
        for path in paths:
            zipf.write(path, os.path.basename(path))

    # Oferecer o arquivo ZIP para download
    with open(zip_path, "rb") as fp:
        st.download_button(
            label="Download Todos os Arquivos",
            data=fp,
            file_name="arquivos_tratados.zip",
            mime="application/zip"
        )

    # Limpar os arquivos temporários
    try:
        for path in paths:
            os.remove(path)
        os.rmdir(temp_dir)
    except OSError as e:
        print(f"Erro ao tentar remover o diretório temporário: {e}")


def criar_zip_arquivos(paths):
    """Cria um arquivo ZIP com vários arquivos Excel."""
    zip_path = os.path.join(tempfile.gettempdir(), "dados_tratados.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for file in paths:
            zipf.write(file, os.path.basename(file))
    return zip_path


def download_table_direto(df, nome_arquivo):
    # Criar um buffer de bytes para segurar o arquivo Excel
    output = io.BytesIO()
    # Usar o Pandas para escrever o DataFrame para o buffer como um arquivo Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    # Voltar para o início do buffer
    output.seek(0)

    # Criar o botão de download para o arquivo Excel
    st.download_button(label="Download dados tratados como Excel",
                       data=output,
                       file_name=f"{nome_arquivo}_dados_tratados.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


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
