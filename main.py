import streamlit as st
import pandas as pd
from utils_df import *
from utils_graficos import *

st.title("APP - Corregedoria 🗂️ ")

st.caption("""
         Com este aplicativo, você será capaz de extrair, transformar e carregar os tipos de arquivo abaixo:
         \n1.xlsx         
         """)

tipo_analise = st.radio("Escolha um arquivo ou mais de um arquivo (analise de IP's", ["Análise Simples", "Análise de IP"])


uploaded_file = False
if tipo_analise == "Análise Simples":
    uploaded_file = st.file_uploader("Escolha o arquivo", accept_multiple_files=False)

if tipo_analise == "Análise de IP":
    uploaded_file = st.file_uploader("Escolha o arquivo", accept_multiple_files=True)


if tipo_analise == "Análise Simples" and uploaded_file:
    df = extract(uploaded_file)

    df = normalize_column_types(df)

    df = normalize_columns(df)  # Normaliza os nomes das colunas
    df = remove_empty_rows(df)
    df = remove_empty_columns(df)

    if "extra sem impulsionamento" in uploaded_file.name.lower():
        df = remove_to_classe(df)

    elif "judi com vista" in uploaded_file.name.lower():
        df = remove_to_classe(df)

    elif "relatório extraj" in uploaded_file.name.lower():
        df = remove_to_classe(df)
        df = remove_second_table_intervalos(df)
        df = rename_duplicate_columns(df)
        df = remove_nan_columns(df)

    remove_duplicates = st.selectbox("Remover valores duplicados ?", ["Sim", "Não"])
    remove_nulls = st.selectbox("Remover valores branco/nulos ?", ["Não", "Sim"])

    if remove_duplicates == "Sim":
        df.drop_duplicates(inplace=True)

    if remove_nulls == "Sim":
        df.dropna(how="all", inplace=True)

    show_result = st.checkbox("Show Result", value=True)

    if show_result:
        st.header("Tabela Consolidada 📊")
        st.dataframe(df)

        if "extra sem impulsionamento" in uploaded_file.name.lower():
            st.header("Tabela Filtrada - extra fora do prazo - sem NF e PP 📊")
            st.write("Foram excluidos da tabela enviada as NF e PP, uma vez que a pesquisa no emp já traz os extras sem impulsionamento!")
            df_filtrado = exclude_specific_classes(df)
            st.dataframe(df_filtrado)
            download_table(df_filtrado)

        elif "judi com vista" in uploaded_file.name.lower():
            st.header("Tabela Filtrada - Judiciais com mais de 60 dias 📊")
            st.write(
                "Foram excluidos da tabela enviada os Inquéritos Policiais e os processos com menos de 60 dias!")
            df_filtrado = filter_df_by_criteria(df)
            st.dataframe(df_filtrado)
            download_table(df_filtrado)



        elif "relatório extraj" in uploaded_file.name.lower():
            st.header("Tabela Filtrada NF | PP fora do prazo 📊")
            df_filtrado = nf_pp_fora_prazo(df)
            st.dataframe(df_filtrado)
            download_table(df_filtrado)

if tipo_analise == "Análise de IP" and uploaded_file:
    dataframes = []
    for ip in uploaded_file:
        df = extract(ip)
        df = remove_to_classe(df)
        df = normalize_column_types(df)
        df = normalize_columns(df)  # Normaliza os nomes das colunas
        df = remove_empty_rows(df)
        df = remove_empty_columns(df)
        dataframes.append(df)

    df_merged = pd.concat(dataframes, axis=0, join="outer", ignore_index=True)

    remove_duplicates = st.selectbox("Remover valores duplicados ?", ["Sim", "Não"])
    remove_nulls = st.selectbox("Remover valores branco/nulos ?", ["Não", "Sim"])

    if remove_duplicates == "Sim":
        df.drop_duplicates(inplace=True)

    if remove_nulls == "Sim":
        df.dropna(how="all", inplace=True)

    show_result = st.checkbox("Show Result", value=True)

    if show_result:
        st.header("Tabela Consolidada 📊")
        st.write(
            "Foram agrupados todos os arquivos que contém processos policiais sem impulsionamento além do prazo legal!")
        st.dataframe(df_merged)
        plot_instauracao_per_month(df_merged)
        totalize_and_plot_by_subject(df_merged)














