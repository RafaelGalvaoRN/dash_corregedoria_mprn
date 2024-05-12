import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


def plot_instauracao_per_month(df):
    # Converter a coluna 'Instauração' para datetime
    df['instauração'] = pd.to_datetime(df['instauração'], errors='coerce')

    # Extrair ano e mês da coluna 'Instauração'
    df['YearMonth'] = df['instauração'].dt.to_period('M')

    # Agrupar por ano e mês, contando as ocorrências
    count_per_month = df.groupby('YearMonth').size()

    # Criar o gráfico de barras
    plt.figure(figsize=(10, 6))
    count_per_month.plot(kind='bar', color='skyblue')
    plt.title('Quantidade de Processos Ativos por Mês de Instauração')
    plt.xlabel('Ano e Mês')
    plt.ylabel('Quantidade de Processos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt.gcf())


def totalize_and_plot_by_subject(df):
    # Agrupar por 'Assunto' e contar as ocorrências
    subject_counts = df['assunto'].value_counts()

    # Criar o gráfico de barras para os totais por assunto
    plt.figure(figsize=(12, 8))
    subject_counts.plot(kind='bar', color='cadetblue')
    plt.title('Total de Processos por Assunto')
    plt.xlabel('Assunto')
    plt.ylabel('Quantidade de Processos')
    plt.xticks(rotation=45, ha='right')  # Melhora a visualização dos rótulos no eixo X
    plt.tight_layout()

    # Mostrar o gráfico na interface Streamlit
    st.pyplot(plt.gcf())