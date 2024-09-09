from utils_df import *
from utils_graficos import *
from documentacao import textos_documentacao
from utils_pdf import *
from relacao_promotorias import promotoria
from utils_cate import *
from utils_membros import *

st.title("APP - Corregedoria 🗂️ ")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Documentação", "Tratador Específico c/ Gráficos",
                                        "Tratador Múltiplo e Geral", "Relatório Cate", "Info Membros"])

with tab1:
    textos_documentacao()

with tab2:
    st.caption("""
             Com este aplicativo, você será capaz de extrair, transformar e carregar os arquivos com os nomes abaixo:
             \nExtra sem impulsionamento.xlsx
             \nIPs sem Impulsionamento.xlsx
             \nJudi com vista.xlsx
             \nRelatório FinalJ - NF - PP.xlsx
             \n Caso enviado mais de um arquivo do mesmo tipo, as tabelas serão agrupadas                      
             """)

    uploaded_files = st.file_uploader("Escolha o arquivo", accept_multiple_files=True, key="tab2")

    if uploaded_files:
        seletor = uploaded_files[0].name.lower()

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
                select_nf_pp_data_in_df,
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

with tab3:
    st.caption("""
                 Com este aplicativo, você será capaz de enviar múltiplos arquivos sendo eles tratados e disponibilizados zipados ao final através do botão Download  
                 """)

    promotoria_selecionada = st.selectbox("Escolha uma promotoria", promotoria)

    col1, col2 = st.columns(2)

    with col1:
        qtd_acervo_extra = st.number_input("Quantidade de acervo extrajudicial", min_value=0, step=1,
                                           help="Quantidade acervo judicial para cálculo de produtividade")

    with col2:
        qtd_acervo_jud = st.number_input("Quantidade de acervo judicial", min_value=0, step=1,
                                         help="Quantidade acervo extrajudicial para cálculo de produtividade")

    uploaded_files = st.file_uploader("Escolha o arquivo", accept_multiple_files=True, key="tab3.1")

    if uploaded_files:
        dfs = []
        nomes = []

        for arquivo in uploaded_files:

            nome_arquivo = arquivo.name.lower()
            seletor = arquivo.name.lower()
            df = extract_normalize(arquivo)

            if "extra sem impulsionamento" in seletor:
                lista_df_tratado = remove_to_classe(df)
                df_merged = lista_df_tratado

                colunas = ["classe", "número", "prazo legal"]
                functions = [exclude_specific_classes, extract_last_date,
                             lambda df: gerar_dataframe_filtrado(df, colunas), title_case_column]
                df_filtrado = apply_pipeline(df_merged, functions)

                dfs.append(df_filtrado)
                nomes.append(f"{nome_arquivo}_tratado")

            elif "judi com vista" in seletor:
                lista_df_tratado = remove_to_classe(df)
                df_merged = lista_df_tratado

                colunas = ['procedimento', 'classe', 'assunto', 'data registro', 'dias andamento']
                functions = [normalize_columns, filter_df_by_criteria, lambda df: gerar_dataframe_filtrado(df, colunas),
                             title_case_column]

                df_filtrado = apply_pipeline(df_merged, functions)

                dfs.append(df_filtrado)
                nomes.append(f"{nome_arquivo}_tratado")

            elif "relatório extraj" in seletor:

                functions = [
                    remove_nan_columns,
                    remove_empty_columns,
                    rename_duplicate_columns,
                    select_nf_pp_data_in_df,
                    remove_to_classe,
                    remove_nan_columns,
                    normalize_columns
                ]

                lista_df_tratado = apply_pipeline(df, functions)
                df_merged = lista_df_tratado

                colunas_corrigir_formato = ['instauração', '30 dias', '120 dias']

                functions = [nf_pp_fora_prazo, gerar_dataframe_filtrado_extra_nf,
                             lambda df: convert_collum_date(df, colunas_corrigir_formato), title_case_column]

                df_filtrado = apply_pipeline(df_merged, functions)

                dfs.append(df_filtrado)
                nomes.append(f"{nome_arquivo}_tratado")

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

                lista_df_tratado = apply_pipeline(df, functions)
                df_merged = lista_df_tratado

                colunas = ['classe', 'número', 'assunto']
                functions = [lambda df: gerar_dataframe_filtrado(df, colunas), title_case_column]
                df_filtrado = apply_pipeline(df_merged, functions)

                dfs.append(df_filtrado)
                nomes.append(f"{nome_arquivo}_tratado")

            st.write("Finalizado tratamento do arquivo", nome_arquivo)

        pdf_path = gerador_relatorio_pdf(dfs,
                                         nomes,
                                         promotoria=promotoria_selecionada,
                                         qtd_acervo_jud=qtd_acervo_jud,
                                         qtd_acervo_extra=qtd_acervo_extra)

        compactar_e_download(dfs, nomes, pdf_path)

with tab4:
    arquivos = cate_extract()
    if arquivos:
        df_unificado = cate_concatena_xlsx(arquivos)
        qtd = st.number_input("Quantidade de Promotorias a serem disponibilizadas no gráfico", step=1, min_value=1)
        plotar_solicitacoes_por_unidade(df_unificado, qtd)

        if df_unificado is not None:
            promotorias = cate_get_promotoria(df_unificado)
            promotoria_selecionada = st.selectbox("Selecione a Promotoria", promotorias)
            st.write(f"Promotoria selecionada: {promotoria_selecionada}")

            if promotoria_selecionada:
                df_filtrado = cate_filtra_por_promotoria(df_unificado, promotoria_selecionada)
                st.write(f"DataFrame filtrado pela promotoria {promotoria_selecionada}:")

                df_filtrado = converter_colunas_para_datetime(df_filtrado, ["Data Solicitação", "Data Conclusão"])

                st.write(df_filtrado)

                df_excel = cate_to_excel(df_filtrado)
                st.download_button(label="Baixar Excel", data=df_excel, file_name='df_filtrado.xlsx',
                                   mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

with tab5:
    arquivos = membros_pdf_extract()
    if arquivos:

        campos_preencher = []

        for arquivo in arquivos:
            pdf_filename = arquivo.name.lower().strip()

            if "Relatório de CO.pdf".strip().lower() in pdf_filename:
                ultimo_relatorio_correicao = extract_pdf(arquivo, [("pag_inicial",
                                                                    "RELATÓRIO DE CORREIÇÃO ORDINÁRIA DE MEMBRO E EM UNIDADE"),
                                                                   ("pag_final", "(assinado eletronicamente)")])

                comparativo_produtividade = extract_pdf(arquivo, [
                    ("pag_inicial", "TABELA 1 - MOVIMENTAÇÃO PROCESSUAL (JUDICIAL)"),
                    ("pag_final", "TABELA 4 - ATIVIDADES")
                ])

                # st.write("ultimo_relatorio_correicao")
                # st.write(ultimo_relatorio_correicao)
                #
                # st.write("Páginas do Comparativo de Produtividade")
                # st.write(comparativo_produtividade)

                campos_preencher.append((pdf_filename, "Último Relatório de Correição",
                                         f"fls. {ultimo_relatorio_correicao['pag_inicial']}-{ultimo_relatorio_correicao['pag_final']}"))
                campos_preencher.append((pdf_filename, "Comparativo de Produtividade",
                                         f"fls. {comparativo_produtividade['pag_inicial']}-{comparativo_produtividade['pag_final']}"))

            if "EXTRATO_MERECIMENTO BIZAGI".strip().lower() in pdf_filename:
                bizagi_ficha_15 = extract_pdf(arquivo, [
                    ("pag_inicial", "DEMAIS DADOS/DOCUMENTOS RELEVANTES"),
                    ("pag_final", "FICHA 16 – DOCUMENTOS DIVERSOS")
                ])

                # st.write("bizagi_ficha_15")
                # st.write(bizagi_ficha_15)
                campos_preencher.append((pdf_filename, "Bizagi - Ficha 15",
                                         f"fls. {bizagi_ficha_15['pag_inicial']}-{bizagi_ficha_15['pag_final']}"))

                bizagi_ficha_15_16 = extract_pdf(arquivo, [
                    ("pag_inicial", "DEMAIS DADOS/DOCUMENTOS RELEVANTES"),
                    ("pag_final", "FICHA 16 – DOCUMENTOS DIVERSOS")
                ])

                # st.write("bizagi_ficha_15_16")
                # st.write(bizagi_ficha_15_16)
                campos_preencher.append((pdf_filename, "Bizagi - Ficha 15 e 16",
                                         f"fls. {bizagi_ficha_15_16['pag_inicial']}-{bizagi_ficha_15_16['pag_final']}"))

                ficha_3 = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 3 - INSPEÇÕES E CORREIÇÕES"),
                    ("pag_final", "FICHA 5")
                ])

                #
                # st.write("Bizagi - Ficha 3")
                # st.write(ficha_3)
                campos_preencher.append((pdf_filename, "Bizagi - Ficha 3",
                                         f"fls. {ficha_3['pag_inicial']}-{ficha_3['pag_final']}"))

                ficha_6_bizagi = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 6 - MUTIRÕES"),
                    ("pag_final", "FICHA 7")
                ])

                # st.write("ficha_6_bizagi")
                # st.write(ficha_6_bizagi)

                campos_preencher.append((pdf_filename, "Bizagi - Ficha 6",
                                         f"fls. {ficha_6_bizagi['pag_inicial']}-{ficha_6_bizagi['pag_final']}"))

                ficha_11_bizagi = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 11 – CURSOS DE FORMAÇÃO CONTINUADA"),
                    ("pag_final", "FICHA 12")
                ])

                # st.write("ficha_11_bizagi")
                # st.write(ficha_11_bizagi)


                campos_preencher.append((pdf_filename, "Bizagi - Ficha_11",
                                         f"fls. {ficha_11_bizagi['pag_inicial']}-{ficha_11_bizagi['pag_final']}"))

                ficha_12_bizagi = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 12 - cursos oficiais diversos"),
                    ("pag_final", "FICHA 13")
                ])

                # st.write("ficha_12_bizagi")
                # st.write(ficha_12_bizagi)

                campos_preencher.append((pdf_filename, "Bizagi - Ficha 12",
                                         f"fls. {ficha_12_bizagi['pag_inicial']}-{ficha_12_bizagi['pag_final']}"))

                ficha_13_bizagi = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 13 – CURSOS RECONHECIDOS DE APERFEIÇOAMENTO"),
                    ("pag_final", "FICHA 14")
                ])

                # st.write("ficha_13_bizagi")
                # st.write(ficha_13_bizagi)

                campos_preencher.append((pdf_filename, "Bizagi - Ficha 13",
                                         f"fls. {ficha_13_bizagi['pag_inicial']}-{ficha_13_bizagi['pag_final']}"))

                ficha_10_bizagi = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 10 – ESPECIALIZAÇÃO, MESTRADO OU DOUTORADO"),
                    ("pag_final", "FICHA 11")
                ])

                # st.write("ficha_10_bizagi")
                # st.write(ficha_10_bizagi)

                campos_preencher.append((pdf_filename, "Bizagi - Ficha 10",
                                         f"fls. {ficha_10_bizagi['pag_inicial']}-{ficha_10_bizagi['pag_final']}"))

                ficha_8_bizagi = extract_pdf(arquivo, [
                    ("pag_inicial", "FICHA 8 - PUBLICAÇÕES ACADÊMICAS"),
                    ("pag_final", "FICHA 9")
                ])

                # st.write("ficha_8_bizagi")
                # st.write(ficha_8_bizagi)

                campos_preencher.append((pdf_filename, "Bizagi - Ficha 8",
                                         f"fls. {ficha_8_bizagi['pag_inicial']}-{ficha_8_bizagi['pag_final']}"))

            if "certidão da dcog".strip().lower() in pdf_filename:
                certidao_dcog = extract_pdf(arquivo, [
                    ("pag_inicial", "certidão"),
                    ("pag_final", "natal")
                ])
                #
                # st.write("certidao_dcog")
                # st.write(certidao_dcog)



                campos_preencher.append((pdf_filename, "Certidão da Diretoria da Corregedoria-Geral",
                                         f"fls. {certidao_dcog['pag_inicial']}-{certidao_dcog['pag_final']}"))

    if st.button("visualizar"):
        # Convertendo a lista de dados para um DataFrame do Pandas
        df = pd.DataFrame(campos_preencher, columns=["Nome do Arquivo", "Dados", "Páginas"])
        st.markdown("## 📋 Tabela de Informações e Páginas")

        st.table(df)  # Exibe a tabela de maneira agradável no Streamlit


