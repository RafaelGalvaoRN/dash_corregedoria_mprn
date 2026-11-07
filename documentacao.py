import streamlit as st

ARQUIVOS_ACEITOS = [
    ("Extra sem impulsionamento.xlsx", "procedimentos extrajudiciais sem impulsionamento há mais de 180 dias (NFs e PPs são excluídos)"),
    ("IPs sem impulsionamento.xlsx", "inquéritos policiais sem impulsionamento além do prazo"),
    ("Judi com vista.xlsx", "processos judiciais com vista (IPs são excluídos; ficam só os com mais de 60 dias)"),
    ("Relatório ExtraJ - NF -PP.xlsx", "Notícias de Fato e Procedimentos Preparatórios (ficam só os fora do prazo)"),
]


def textos_documentacao():
    st.subheader("Como usar")

    st.markdown("**1. Exporte as planilhas do EMP** e salve com um destes nomes. O app identifica o tipo "
                "pelo nome do arquivo, então pode haver texto antes ou depois "
                "(ex.: \"5ª PmJ - Extra sem impulsionamento.xlsx\"):")
    for nome, descricao in ARQUIVOS_ACEITOS:
        st.markdown(f"- **{nome}** — {descricao}")
    st.caption("Não altere os nomes das colunas das planilhas.")

    st.markdown("**2. Escolha a aba conforme o objetivo:**")
    st.markdown("""
- **Tratador Específico c/ Gráficos** — envie planilhas de **um único tipo** (vários arquivos do mesmo tipo são agrupados).
  O app mostra a tabela consolidada, a tabela filtrada, gráficos e o botão para baixar o Excel tratado.
- **Tratador Múltiplo e Geral** — gera o **relatório em PDF** da Sala de Acompanhamento Virtual:
    1. escolha a promotoria;
    2. informe o acervo extrajudicial e o acervo judicial (o judicial **inclui os IPs**);
    3. envie as planilhas (tipos diferentes podem ir juntos);
    4. baixe o ZIP com o PDF e as planilhas tratadas.

  Se o acervo estiver zerado ou menor que o passivo, o app avisa antes do download.
- **Relatório Cate** — envie as planilhas do CATE, escolha quantas promotorias aparecem no gráfico e
  selecione uma promotoria para filtrar e baixar.
- **Info Membros** — preencha os dados do membro e envie os 4 PDFs (Certidão da DCOG,
  EXTRATO_MERECIMENTO BIZAGI, Relatório de CO e Comparativo Promotorias). O checklist mostra o que
  foi reconhecido; com os 4 presentes, clique em **visualizar** para gerar o índice e o PDF consolidado.
""")

    st.markdown("**3. Como o índice de atraso é calculado**")
    st.markdown("""
- **Índice de atraso = passivo ÷ acervo × 100**, separado em extrajudicial e judicial.
- Passivo extrajudicial = itens de *Extra sem impulsionamento* + NFs/PPs fora do prazo do *Relatório ExtraJ*.
- Passivo judicial = itens de *Judi com vista* (mais de 60 dias) + *IPs sem impulsionamento*.
""")

    st.info("Toda tabela exibida na tela pode ser baixada: passe o mouse sobre ela e use o ícone de "
            "download no canto superior direito.")

    with st.expander("Histórico de versões"):
        st.write("😎 - 06/11/2026 - Relatório PDF em A4, com resumo no início, fonte maior, quebra de linha nas "
                 "células e numeração de páginas; datas no padrão brasileiro; índices de atraso formatados "
                 "e avisos de acervo; checklist de documentos em 'Info Membros'.")
        st.write("😎 - 23/09/2024 - Inclusão da ABA 'Info Membros' que visa facilitar a feitura de relatório de "
                 "correição dos membros, por meio de identificação das folhas onde os itens se encontram e "
                 "elaboração de sumário síntese")
        st.write("😎 - 16/07/2024 - Inclusão da ABA 'Relatório CATE' que visa tratar concatenar tabelas do CATE "
                 "e filtrar por promotoria")
        st.write("😎 - 16/05/2024 - Inclusão da confecção de relatório em PDF na aba 'Tratador Múltiplo e Geral'")
        st.write("😎 - 15/05/2024 - Inclusão da aba 'Tratador Múltiplo e Geral'")
        st.write("😎 - 15/05/2024 - Melhoria do filtro na tabela 'Extra sem impulsionamento' que passa a excluir "
                 "PPs e NFs")
        st.write("😎 - 15/05/2024 - Implementação da pesquisa de NF e PP na mesma tabela, apesar de estarem em "
                 "seções diferentes")
        st.write("🚀 - 14/05/2024 - Versão 1.01. Possibilidade de múltiplos arquivos com concatenação e geração "
                 "de tabela na forma pretendida pela Corregedoria.")
        st.write("Criado em 10/05/2024.")
