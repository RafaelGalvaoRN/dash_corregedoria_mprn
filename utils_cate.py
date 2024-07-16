import pandas as pd
import streamlit as st
from io import BytesIO



def cate_extract():
    arquivos = st.file_uploader("Junte seu arquivo XLS aqui", type="xlsx", accept_multiple_files=True)
    return arquivos


def cate_concatena_xlsx(arquivos):
    lista_dfs = [pd.read_excel(arquivo) for arquivo in arquivos]

    df_unificado = pd.concat(lista_dfs)

    return df_unificado


def cate_get_promotoria(df):
    promotorias = df['Unidade Solicitante'].unique()
    return list(promotorias)


def cate_filtra_por_promotoria(df, promotoria_selecionada):
    df_filtrado = df[df['Unidade Solicitante'] == promotoria_selecionada]
    return df_filtrado



def cate_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data