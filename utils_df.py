import pandas as pd
import streamlit as st
import io


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
        cols[cols == dup] = [f"{dup}_{i+1}" if i != 0 else dup for i in range(sum(cols == dup))]
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
    df_filtrado = df[(df['Dentro /Fora'] == "F")]
    return df_filtrado


def exclude_specific_classes(df):
    # Filtra o DataFrame para excluir linhas onde 'Classe' é 'Notícia de Fato' ou 'Procedimentos Preparatórios'
    df_filtered = df[~df['Classe'].isin(['Notícia de Fato', 'Procedimentos Preparatórios'])]
    return df_filtered


def filter_df_by_criteria(df):
    # Excluir entradas onde 'Classe' é 'Inquérito Policial'
    df = df[df['Classe'] != 'Inquérito Policial']

    # Converter 'Dias Andamento' para int antes de filtrar
    # Usar pd.to_numeric para conversão segura, convertendo erros em NaN (que serão filtrados fora)
    df['Dias Andamento'] = pd.to_numeric(df['Dias Andamento'], errors='coerce')


    # Incluir apenas entradas onde 'Dias Andamento' é igual ou superior a 60
    df = df[df['Dias Andamento'] >= 60]

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
                       file_name="dados_tratados.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")