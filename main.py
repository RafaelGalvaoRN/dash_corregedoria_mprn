from utils_df import *
from utils_graficos import *
from documentacao import textos_documentacao

st.title("APP - Corregedoria 🗂️ ")

tab1, tab2 = st.tabs(["Documentação", "Aplicação"])

with tab1:
    textos_documentacao()

with tab2:
    st.caption("""
             Com este aplicativo, você será capaz de extrair, transformar e carregar os tipos de arquivo abaixo:
             \n1.xlsx         
             """)

    uploaded_files = st.file_uploader("Escolha o arquivo", accept_multiple_files=True)

    for uploaded_file in uploaded_files:
        # if uploaded_files:
        if uploaded_file:
            name_arquivo = uploaded_file.name.lower
            # seletor = uploaded_files[0].name.lower()
            seletor = uploaded_file.name.lower()

            for processo in uploaded_files:
                lista_dfs = [extract_normalize(processo) for processo in uploaded_files]

            if "extra sem impulsionamento" in seletor:
                lista_df_tratado = [remove_to_classe(processo) for processo in lista_dfs]
                df_merged = pd.concat(lista_df_tratado, axis=0, join="outer", ignore_index=True)


            elif "judi com vista" in seletor:
                lista_df_tratado = [remove_to_classe(processo) for processo in lista_dfs]
                df_merged = pd.concat(lista_df_tratado, axis=0, join="outer", ignore_index=True)


            elif "relatório extraj" in seletor:
                lista_dfs = [extract_normalize(processo) for processo in uploaded_files]

                functions = [
                    remove_nan_columns,
                    remove_empty_columns,
                    rename_duplicate_columns,
                    remove_second_table_intervalos,
                    remove_to_classe,
                    remove_nan_columns,
                    normalize_columns
                ]

                lista_df_tratado = [apply_pipeline(df, functions) for df in lista_dfs]
                df_merged = pd.concat(lista_df_tratado, axis=0, join="outer", ignore_index=True)


            elif "ips sem impulsionamento" in seletor:

                functions = [
                    remove_to_classe,
                    normalize_column_types,
                    normalize_columns,
                    remove_empty_rows,
                    remove_empty_columns,
                    extract_last_date,
                    filter_df_by_ip
                ]

                lista_df_tratado = [apply_pipeline(df, functions) for df in lista_dfs]
                df_merged = pd.concat(lista_df_tratado, axis=0, join="outer", ignore_index=True)

            show_result = st.checkbox("Show Result", value=True)

            if show_result:
                st.header("Tabela Consolidada 📊")
                st.dataframe(df_merged)

                if "extra sem impulsionamento" in seletor:
                    st.header("Tabela Filtrada - extra fora do prazo - sem NF e PP 📊")

                    with st.expander("Clique aqui para mais informações sobre os critérios:"):
                        st.markdown("""
                          - **Exclusões:** Foram excluídos da tabela os itens 'NF' e 'PP', uma vez que a pesquisa no EMP já traz os extras sem impulsionamento.
                          - **Inclusão:** Foi incluído o 'Número de Ordem'.
                          - **Filtragem:** A tabela foi filtrada para mostrar apenas 'Ordem', 'Número de Instauração', 'Prazo Legal'.
                          """)

                    colunas = ["classe", "número", "prazo legal"]
                    functions = [exclude_specific_classes, extract_last_date,
                                 lambda df: gerar_dataframe_filtrado(df, colunas), title_case_column]
                    df_filtrado = apply_pipeline(df_merged, functions)

                    st.dataframe(df_filtrado)

                    st.markdown("---")

                    functions = [exclude_specific_classes, extract_last_date]
                    df_filtrado_grafico = apply_pipeline(df_merged, functions)
                    grafico_procedimento_prazos_ultimo_impulsionamento(df_filtrado_grafico)

                    st.markdown("---")
                    download_table(df_filtrado)

                elif "judi com vista" in seletor:
                    st.header("Tabela Filtrada - Judiciais com mais de 60 dias 📊")
                    st.write(
                        "Foram excluidos da tabela enviada os Inquéritos Policiais e os processos com menos de 60 dias!")

                    colunas = ['procedimento', 'classe', 'assunto', 'data registro', 'dias andamento']
                    functions = [normalize_columns, filter_df_by_criteria, lambda df: gerar_dataframe_filtrado(df, colunas),
                                 title_case_column]

                    df_filtrado = apply_pipeline(df_merged, functions)

                    st.dataframe(df_filtrado)

                    st.markdown("---")
                    grafico_pizza_judiciais(df_filtrado)
                    st.markdown("---")
                    download_table(df_filtrado)


                elif "relatório extraj" in seletor:
                    st.header("Tabela Filtrada NF | PP fora do prazo 📊")

                    with st.expander("Clique aqui para mais informações sobre os critérios:"):
                        st.markdown("""                                    
                                         - **Inclusão:** Foi incluído o 'Número de Ordem'.
                                         - **Filtragem:** A tabela foi filtrada para mostrar apenas 'Ordem', 'Número', 'Instauração', '30 dias', '120 dias', 'DENTRO/FORA', 'DIAS/FORA' .
                                         """)

                    colunas_corrigir_formato = ['instauração', '30 dias', '120 dias']

                    functions = [nf_pp_fora_prazo, gerar_dataframe_filtrado_extra_nf,
                                 lambda df: convert_collum_date(df, colunas_corrigir_formato), title_case_column]

                    df_filtrado = apply_pipeline(df_merged, functions)
                    st.dataframe(df_filtrado)

                    st.markdown("---")

                    functions = [nf_pp_fora_prazo]
                    df_filtrado_grafico = apply_pipeline(df_merged, functions)

                    grafico_procedimento_prazos(df_filtrado_grafico)

                    st.markdown("---")
                    download_table(df_filtrado)

                elif "ips sem impulsionamento" in seletor:
                    st.header("Tabela Consolidada 📊")
                    st.write(
                        "Foram agrupados todos os arquivos que contém processos policiais sem impulsionamento além do prazo legal!")

                    colunas = ['classe', 'número', 'assunto']
                    functions = [lambda df: gerar_dataframe_filtrado(df, colunas), title_case_column]
                    df_filtrado = apply_pipeline(df_merged, functions)
                    st.dataframe(df_filtrado)

                    st.markdown("---")
                    plot_instauracao_per_month(df_merged)
                    st.markdown("---")



                    plot_ultimo_impulsionamento_per_month(df_merged)
                    st.markdown("---")
                    totalize_and_plot_by_subject(df_merged)

                    st.markdown("---")
                    download_table(df_filtrado)
