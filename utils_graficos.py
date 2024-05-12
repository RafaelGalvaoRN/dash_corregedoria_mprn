import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns




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

    # Definindo os intervalos de dias fora do prazo
    bins = [0, 30, 60, 90, 120, float('inf')]
    labels = ['0-30', '31-60', '61-90', '91-120', '121+']

    # Criando uma nova coluna com os intervalos
    df['Intervalo Dias Fora'] = pd.cut(df['Dias Fora'], bins=bins, labels=labels, right=False)

    # Criando o gráfico
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Intervalo Dias Fora', hue='classe')
    plt.title('Distribuição de Processos por Dias Fora e Classe')
    plt.xlabel('Dias Fora do Prazo')
    plt.ylabel('Número de Processos')
    plt.legend(title='Classe')

    # Mostrando o gráfico no Streamlit
    st.pyplot(plt)


def grafico_procedimento_prazos(df):
    # Definindo os intervalos de dias fora do prazo
    bins = [0, 30, 60, 90, 120, float('inf')]
    labels = ['0-30', '31-60', '61-90', '91-120', '121+']

    # Certifique-se de que a coluna 'Dias Fora' é numérica
    df['Dias Fora'] = pd.to_numeric(df['Dias Fora'], errors='coerce')

    # Criando uma nova coluna com os intervalos
    df['Intervalo Dias Fora'] = pd.cut(df['Dias Fora'], bins=bins, labels=labels, right=False)

    # Criando o gráfico
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Intervalo Dias Fora', hue='Classe')
    plt.title('Distribuição de Processos por Dias Fora do Prazo e Classe')
    plt.xlabel('Dias Fora do Prazo')
    plt.ylabel('Número de Processos')
    plt.legend(title='Classe')

    # Mostrando o gráfico no Streamlit
    st.pyplot(plt)