import streamlit as st


def textos_documentacao():
    st.markdown("---")

    st.write("🚀 - 14/05/2024 - Versão 1.01. Possibilidade de múltiplos arquivos com concatenação e geração de tabela na forma pretendida pela Corregedoria.")


    st.markdown("---")

    st.write(":sunglasses: Toda tabela é passível de ser baixada. Coloque o mouse em cima dela e espere o botão de download ser exibido no canto superior direito da mesma.")


    st.write(":sunglasses: Na análise de IP's é possível passar mais de um arquivo. O sistema agrupará todas as tabelas em um único arquivo, para fazer o filtro.")

    st.write(":sunglasses: Os nomes das colunas das planilhas não devem ser alterados.")

    st.write(":sunglasses: Observe o nome dos arquivos a serem enviados ao aplicativo; eles devem ser:")

    lst = ['Extra sem impulsionamento.xlsx', 'IPs sem impulsionamento.xlsx',
           'Judi com vista.xlsx', "Relatório Extraj - NF - PP.xlsx"]

    for i in lst:
        st.markdown("- " + i)

    st.write(":sunglasses: Criado em 10/05/2024.")
