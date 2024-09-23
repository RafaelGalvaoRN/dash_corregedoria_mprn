import pprint

import pandas as pd

from utils_df import *
from utils_graficos import *
from documentacao import textos_documentacao
from utils_pdf import *
from relacao_promotorias import dados_fixos
from utils_cate import *
from utils_membros import *
from pypdf import PdfMerger


def pdf_merger_files(lista: list, output_pdf='merged.pdf'):
    merger = PdfMerger()

    for pdf in lista:
        merger.append(pdf)

    merger.write(output_pdf)
    merger.close()

    return output_pdf


st.set_page_config(page_title="APP - Corregedoria MPRN", page_icon="🗂️",
                   menu_items={
                       'About': "rafael.galvao@mprn.mp.br"
                   }
                   )

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
    cargo_do_candidato, membro, posicao_lista_antiguidade, ultima_correicao_ordinaria, orgao_ministerial_ultima_correicao = membros_menu()

    arquivos = membros_pdf_extract()

    if arquivos:
        if len(arquivos) < 4:
            st.error("Necessário colocar ao menos 4 arquivos em pdf")

        elif len(arquivos) >= 4:
            campos_preencher = []

            qtd_pages_pdf_file = {}
            qtd_pages_pdf_file["sumario"] = 2

            # vai ser somado 1 a todas as páginas pelo índice
            # após, vai ser somado  onumero de página às páginas iniciais e finais, pelos documentos anteriores,
            # na seguinte sequencia de documentos:
            # """1. Certidão da DCOG
            # 2. EXTRATO_MERECIMENTO BIZAGI
            # 3. Relatório de CO
            # 4. Comparativo Promotorias"""

            # emprego da func get_value_by_partial_key para pegar value sem ter que passar_todo o nome do arquivo

            for arquivo in arquivos:
                nome_arquivo = arquivo.name.lower().strip().replace(".pdf", "")
                qtd_pages_pdf_file[nome_arquivo] = get_pages(arquivo)

            for arquivo in arquivos:
                pdf_filename = arquivo.name.lower().strip()

                if "Relatório de CO".strip().lower() in pdf_filename:
                    qtd_paginas_anteriores = 2 + get_value_by_partial_key(qtd_pages_pdf_file,
                                                                          "dcog") + get_value_by_partial_key(
                        qtd_pages_pdf_file, "bizagi")

                    ultimo_relatorio_correicao = extract_pdf(arquivo, [("pag_inicial",
                                                                        "RELATÓRIO DE CORREIÇÃO ORDINÁRIA DE MEMBRO E EM UNIDADE"),
                                                                       ("pag_final", "Assinado eletronicamente por")])

                    comparativo_produtividade = extract_pdf(arquivo, [
                        ("pag_inicial", "TABELA 1 - MOVIMENTAÇÃO PROCESSUAL (JUDICIAL)"),
                        ("pag_final", "TABELA 4 - ATIVIDADES")
                    ], opcional_string="Transação Penal")

                    campos_preencher.append((pdf_filename, "Último Relatório de Correição",
                                             f"fls. {ultimo_relatorio_correicao['pag_inicial'] + qtd_paginas_anteriores}-{ultimo_relatorio_correicao['pag_final'] + qtd_paginas_anteriores}"))
                    campos_preencher.append((pdf_filename, "Comparativo de Produtividade",
                                             f"fls. {comparativo_produtividade['pag_inicial'] + qtd_paginas_anteriores}-{comparativo_produtividade['pag_final'] + qtd_paginas_anteriores}"))

                if "EXTRATO_MERECIMENTO BIZAGI".strip().lower() in pdf_filename:
                    qtd_paginas_anteriores = 2 + get_value_by_partial_key(qtd_pages_pdf_file, "dcog")

                    bizagi_ficha_15 = extract_pdf(arquivo, [
                        ("pag_inicial", "ficha 15"),
                        ("pag_final", "ficha 16")
                    ], first_search=False)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 15",
                                             f"fls. {bizagi_ficha_15['pag_inicial'] + qtd_paginas_anteriores}"))

                    bizagi_ficha_15_16 = extract_pdf(arquivo, [
                        ("pag_inicial", "ficha 15"),
                        ("pag_final", "ficha 16")
                    ], first_search=False)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 15 e 16",
                                             f"fls. {bizagi_ficha_15_16['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_3 = extract_pdf(arquivo, [
                        ("pag_inicial", "ficha 3"),
                        ("pag_final", "ficha 5")
                    ], first_search=True)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 3",
                                             f"fls. {ficha_3['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_6_bizagi = extract_pdf(arquivo, [
                        ("pag_inicial", r"ficha 6"),
                        ("pag_final", r"ficha 7")
                    ], first_search=False)

                    # st.write("ficha_6_bizagi")
                    # st.write(ficha_6_bizagi)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 6",
                                             f"fls. {ficha_6_bizagi['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_11_bizagi = extract_pdf(arquivo, [
                        ("pag_inicial", r"ficha 11"),
                        ("pag_final", r"ficha 12")
                    ], first_search=False)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 11",
                                             f"fls. {ficha_11_bizagi['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_12_bizagi = extract_pdf(arquivo, [
                        ("pag_inicial", r"ficha 12"),
                        ("pag_final", r"ficha 13")
                    ], first_search=False)

                    # st.write("ficha_12_bizagi")
                    # st.write(ficha_12_bizagi)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 12",
                                             f"fls. {ficha_12_bizagi['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_13_bizagi = extract_pdf(arquivo, [
                        ("pag_inicial", "FICHA 13"),
                        ("pag_final", "FICHA 14")
                    ], first_search=False)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 13",
                                             f"fls. {ficha_13_bizagi['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_10_bizagi = extract_pdf(arquivo, [
                        ("pag_inicial", "FICHA 10"),
                        ("pag_final", "FICHA 11")
                    ], first_search=False)

                    # st.write("ficha_10_bizagi")
                    # st.write(ficha_10_bizagi)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 10",
                                             f"fls. {ficha_10_bizagi['pag_inicial'] + qtd_paginas_anteriores}"))

                    ficha_8_bizagi = extract_pdf(arquivo, [
                        ("pag_inicial", "FICHA 8"),
                        ("pag_final", "FICHA 9")
                    ], first_search=False)

                    # st.write("ficha_8_bizagi")
                    # st.write(ficha_8_bizagi)

                    campos_preencher.append((pdf_filename, "Bizagi - Ficha 8",
                                             f"fls. {ficha_8_bizagi['pag_inicial'] + qtd_paginas_anteriores}"))

                    # extrato merececimento bizagi

                    extrato_merecimento_bizagi = (1, get_pages(arquivo))

                    campos_preencher.append((pdf_filename, "Bizagi - Integral",
                                             f"fls. {1 + qtd_paginas_anteriores}-{extrato_merecimento_bizagi[1] + qtd_paginas_anteriores}"))

                if "certidão da dcog".strip().lower() in pdf_filename:


                    certidao_dcog = {"pag_inicial": 1, "pag_final": get_pages(arquivo)}

                    # 1 somado decorrente do indice
                    campos_preencher.append((pdf_filename, "Certidão da Diretoria da Corregedoria-Geral",
                                             f"fls. {certidao_dcog['pag_inicial'] + 2}-{certidao_dcog['pag_final'] + 2}"))

                if "comparativo promotorias".strip().lower() in pdf_filename:


                    qtd_paginas_anteriores = 2 + get_value_by_partial_key(qtd_pages_pdf_file,
                                                                          "dcog") + get_value_by_partial_key(
                        qtd_pages_pdf_file, "bizagi") + get_value_by_partial_key(qtd_pages_pdf_file, "relatório de co")




                    comparativo_promotorias = extract_pdf(arquivo, [
                        ("pag_inicial", "Período Selecionado"),
                        ("pag_final", r"TABELA 4 - ATIVIDADES")
                    ], opcional_string="Total")

                    # 1 somado decorrente do indice
                    campos_preencher.append((pdf_filename, "Comparativo atualizado",
                                             f"fls. {comparativo_promotorias['pag_inicial'] + qtd_paginas_anteriores}-{comparativo_promotorias['pag_final'] + qtd_paginas_anteriores}"))



            if st.button("visualizar"):
                dados_membros = {
                    'Cargo do Candidato': [cargo_do_candidato],
                    'Membro': [membro],
                    'Posição na Lista de Antiguidade': [posicao_lista_antiguidade],
                    'Última Correição Ordinária': [ultima_correicao_ordinaria],
                    'Órgão Ministerial da Última Correição': [orgao_ministerial_ultima_correicao],

                }

                df_membros = pd.DataFrame(dados_membros)

                st.markdown("## 📋 Tabela de Dados Gerais do Membro")
                st.table(df_membros)

                # Convertendo a lista de dados para um DataFrame do Pandas
                df_dados_gerais = pd.DataFrame(campos_preencher, columns=["Nome do Arquivo", "Dados", "Páginas"])

                st.markdown("## 📋 Tabela de Informações e Páginas")
                st.table(df_dados_gerais)  # Exibe a tabela de maneira agradável no Streamlit

                # Substituindo os placeholders
                dados_substituidos = substituir_placeholders(dados_fixos, campos_preencher)

                # Convertendo os dados substituídos em um DataFrame
                df_substituido = pd.DataFrame(dados_substituidos)

                # excluindo colunas

                st.markdown("## 📋 INFORMAÇÕES DA CORREGEDORIA GERAL")
                # Exibindo o segundo DataFrame sem índice e sem colunas já excluidas
                st.table(df_substituido)

                file_xlsx = append_to_excel_manually(df_membros, df_substituido, "tabela_informações_completa_manual")

                gerador_indice_pdf(file_xlsx, "indice.pdf")

                # ordenar arquivos e incluir indice na posicao 0
                arquivos_ordenados = sorted(arquivos, key=lambda x: x.name)

                files_mesclar = ["indice.pdf"] + arquivos_ordenados

                # mesclar arquivos pdf
                merged_pdf_file = pdf_merger_files(files_mesclar, 'merged.pdf')

                download_excel_pdf(file_xlsx, merged_pdf_file)

                st.success("Concluído")
