import pandas as pd

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

                campos_preencher.append((pdf_filename, "Bizagi - Ficha 11",
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

    dados_fixos = {
        'Item': ['1.1.1 Resolutividade (Produtividade e impacto social)',
                 '1.1.2 Presteza',
                 '1.1.3 Pronto Antedimento',
                 '1.1.4 Eficiência',
                 '1.1.5 Organização e Desempenho das Funções',
                 '1.2.1 Qualidade Técnica',
                 '1.2.2 Segurança',
                 'Participação em Mutirões e/ou Sessões do Júri',
                 '3.1.1 Cursos de Formação Continuada',
                 '3.1.2 Cursos Oficiais Diversos dos de Formação Continuada e Cursos Reconhecidos de Aperfeiçoamento',
                 'a) Doutorado (pós-graduação stricto sensu) reconhecido pelo MEC (sem o afastamento previsto no art. 197, inciso III, da Lei Complementar Estadual no 141/1996 c/c Resolução no 004/2008-CSMP).',
                 'b) Mestrado (pós-graduação stricto sensu) reconhecido pelo MEC (sem o afastamento previsto no art. 197, inciso III, da Lei Complementar Estadual no 141/1996 c/c Resolução no 004/2008-CSMP).',
                 'c) Curso de especialização (pós-graduação lato sensu) reconhecido pelo MEC (sem o afastamento',
                 '3.3.1. Publicações Acadêmicas',
                 '---',
                 ],

        # 'Informações': [
        #     'Produtividade: último Relatório de Correição ({{Último Relatório de Correição}}) e Comparativo atualizado ({{Comparativo de Produtividade}}) \n Impacto Social: Bizagi – Ficha 15 ({{Bizagi - Ficha 15}}), Último Relatório de Correição ({{Último Relatório de Correição}}) e drive CGMP_RESULTADOS (G:\ Drives compartilhados\ CGMP_RESULTADOS)',
        #     'Fichas 15 e 16 do Bizagi ({{Bizagi - Ficha 15 e 16}}), Último Relatório de Correição ({{Último Relatório de Correição}}) e Certidão DCOG {{Certidão da Diretoria da Corregedoria-Geral}}',
        #     'Certidão da DCOG ({{Certidão da Diretoria da Corregedoria-Geral}})',
        #     'Ficha 3 ({{Bizagi - Ficha 3}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 3 ({{Bizagi - Ficha 3}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 3 ({{Bizagi - Ficha 3}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 3 ({{Bizagi - Ficha 3}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 6 ({{Bizagi - Ficha 6}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 11 ({{Bizagi - Ficha 11}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 12 ({{Bizagi - Ficha 12}}) e 13 ({{Bizagi - Ficha 13}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 10 ({{Bizagi - Ficha 10}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 10 ({{Bizagi - Ficha 10}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 10 ({{Bizagi - Ficha 10}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'Ficha 8 ({{Bizagi - Ficha 8}}) EXTRATO_MERECIMENTO BIZAGI',
        #     'PENDENTE DE SABER ONDE FICA',
        # ],

        'Informações': [
            'Produtividade: último Relatório de Correição e Comparativo atualizado \n Impacto Social: Bizagi – Ficha 15, Último Relatório de Correição e drive CGMP_RESULTADOS (G:\ Drives compartilhados\ CGMP_RESULTADOS)',
            'Fichas 15 e 16 do Bizagi, Último Relatório de Correição e Certidão DCOG',
            'Certidão da DCOG',
            'Ficha 3 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 3 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 3 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 3 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 6 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 11 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 12 e 13 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 10 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 10 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 10 EXTRATO_MERECIMENTO BIZAGI',
            'Ficha 8 EXTRATO_MERECIMENTO BIZAGI',
            'PENDENTE DE SABER ONDE FICA',
        ],

        'Localização das Informações': [
            '{{Último Relatório de Correição}}, {{Comparativo de Produtividade}}, {{Bizagi - Ficha 15}}, {{Último Relatório de Correição}}',
            '{{Bizagi - Ficha 15 e 16}}, {{Último Relatório de Correição}} e {{Certidão da Diretoria da Corregedoria-Geral}}',
            '{{Certidão da Diretoria da Corregedoria-Geral}}',
            '{{Bizagi - Ficha 3}}',
            '{{Bizagi - Ficha 3}}',
            '{{Bizagi - Ficha 3}}',
            '{{Bizagi - Ficha 3}}',
            '{{Bizagi - Ficha 6}}',
            '{{Bizagi - Ficha 11}}',
            '{{Bizagi - Ficha 12}} e {{Bizagi - Ficha 13}}',
            '{{Bizagi - Ficha 10}}',
            '{{Bizagi - Ficha 10}}',
            '{{Bizagi - Ficha 10}}',
            '{{Bizagi - Ficha 8}}',
            'PENDENTE DE SABER ONDE FICA',
        ],


        'Informação Conceito ou Registro Disciplinar': ['', '', '', '', '', '', '', '', '',
                                                        '', '', '', '', '', ''],

        'Observações': [
            'A produtividade é Avaliada com prevalência dos dados relativos aos doze últimos meses de efetivo exercício a contar da data final do edital do certame, por meio do comparativo da produtividade média dos membros do Ministério Público de unidades similares e com atuação em ofícios de atribuições análogas. O impacto social da atuação ministerial pode ser verificado a partir de registros constantes do último relatório de correição do membro e das informações constantes da Ficha 15 do extrato funcional.',
            'Avaliada a partir da atuação judicial e extrajudicial do membro em órgão de execução (Resolução nº 002/2018–CSMP, arts. 11, inciso I, alínea “b”; 11-A e 12), pode ser extraída do último Relatório de Correição Ordinária, bem como, de dados constantes nas fichas 15 e 16 de seus assentamentos funcionais',
            'Descumprimento de convocações, instruções, recomendações e pedidos de informação emanados dos órgãos da Administração Superior, nos doze últimos meses de efetivo exercício a contar da data final do edital de promoção/remoção pelo critério de merecimento.',
            'Medida em razão da atuação funcional constante dos assentamentos individuais resultantes do Conceito Geral de sua última Correição Ordinária.',
            'Avaliada pelo trabalho desenvolvido na unidade ministerial levando-se em conta o uso eficiente dos recursos humanos e administrativos a seu dispor, estando registrada na última Correição Ordinária.',
            'A qualidade técnica dos trabalhos, aferida pela fundamentação jurídica, redação e zelo, é verificável na última visita de Correição Ordinária.',
            'A segurança, aferida nas manifestações processuais pela adoção das providências pertinentes, precisas e sem equívocos, que revelem conhecimento jurídico e certeza no posicionamento que se está adotando é verificável na última visita de Correição Ordinária.',
            'Não remunerada, quando designada sem prejuízo de suas funções, assegurada a '
            'participação de todos quantos manifestarem interesse, pontuada a cada cinquenta processos ou procedimentos e/ou a cada sessão do Tribunal do Júri.',
            ' ',
            ' ',
            ' ',
            ' ',
            ' ',
            ' ',
            'Não foram localizados nos assentamentos funcionais do(a) interessado(a) registros que maculem sua urbanidade no tratamento dispensado aos cidadãos, magistrados, advogados, defensores públicos, partes, servidores e membros do Ministério Público, bem como sua vida pública e privada.',

        ]
    }

    if st.button("visualizar"):
        # Convertendo a lista de dados para um DataFrame do Pandas
        df = pd.DataFrame(campos_preencher, columns=["Nome do Arquivo", "Dados", "Páginas"])
        st.markdown("## 📋 Tabela de Informações e Páginas")

        st.table(df)  # Exibe a tabela de maneira agradável no Streamlit

        # Substituindo os placeholders
        dados_substituidos = substituir_placeholders(dados_fixos, campos_preencher)

        # Convertendo os dados substituídos em um DataFrame
        df_substituido = pd.DataFrame(dados_substituidos)


        st.markdown("## 📋 INFORMAÇÕES DA CORREGEDORIA GERAL")

        # Exibindo o segundo DataFrame sem índice
        st.dataframe(df_substituido)

        download_table_direto(df_substituido, "tabela_informações")