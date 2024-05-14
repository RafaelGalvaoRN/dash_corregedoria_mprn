import pandas as pd
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
    plt.title('Quantidade de Processos Ativos por Ano / Mês de Instauração')
    plt.xlabel('Ano e Mês')
    plt.ylabel('Quantidade de Processos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt.gcf())


def plot_ultimo_impulsionamento_per_month(df):
    # Converter a coluna 'Instauração' para datetime
    df['data do último impulsionamento'] = pd.to_datetime(df['data do último impulsionamento'], errors='coerce')

    # Extrair ano e mês da coluna 'Instauração'
    df['YearMonth'] = df['data do último impulsionamento'].dt.to_period('M')

    # Agrupar por ano e mês, contando as ocorrências
    count_per_month = df.groupby('YearMonth').size()

    # Criar o gráfico de barras
    plt.figure(figsize=(10, 6))
    count_per_month.plot(kind='bar', color='skyblue')
    plt.title('Quantidade de Processos Ativos por Ano / Mês do Último Impulsionamento')
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


def grafico_procedimento_prazos(df):
    # Definindo os intervalos de dias fora do prazo
    bins = [0, 30, 60, 90, 120, float('inf')]
    labels = ['0-30', '31-60', '61-90', '91-120', '121+']

    # Certifique-se de que a coluna 'Dias Fora' é numérica
    df['dias fora'] = pd.to_numeric(df['dias fora'], errors='coerce')

    # Criando uma nova coluna com os intervalos
    df['Intervalo Dias Fora'] = pd.cut(df['dias fora'], bins=bins, labels=labels, right=False)

    # Criando o gráfico
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='Intervalo Dias Fora', hue='classe')
    plt.title('Distribuição de Processos por Dias Fora do Prazo e Classe')
    plt.xlabel('Dias Fora do Prazo')
    plt.ylabel('Número de Processos')
    plt.legend(title='Classe')

    # Mostrando o gráfico no Streamlit
    st.pyplot(plt)


def grafico_procedimento_prazos_ultimo_impulsionamento(df):
    # Converter 'Last Date' para datetime
    df['data do último impulsionamento'] = pd.to_datetime(df['data do último impulsionamento'], errors='coerce')

    # Criar coluna de mês/ano
    df['Month-Year'] = df['data do último impulsionamento'].dt.to_period('M')

    # Agrupar por mês/ano e classe, e contar ocorrências
    grouped = df.groupby(['Month-Year', 'classe']).size().reset_index(name='Count')

    # Preparar os dados para o gráfico
    plt.figure(figsize=(12, 8))
    sns.barplot(data=grouped, x='Month-Year', y='Count', hue='classe')
    plt.title('Distribuição de Processos por Mês/Ano do Último Impulsionamento e Classe do Procedimento')
    plt.xlabel('Ano/Mês')
    plt.ylabel('Número de Processos')
    plt.xticks(rotation=45)  # Rotação dos labels no eixo X para melhor visualização
    plt.legend(title='Classe')
    plt.tight_layout()

    # Mostrando o gráfico no Streamlit
    st.pyplot(plt)


def grafico_pizza_judiciais(df):
    counts = df["classe"].value_counts()

    # Função para formatar o texto de autopct com porcentagem e valor absoluto
    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct * total / 100.0))
            return f'{pct:.1f}%\n({val:d})'

        return my_format

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=counts.index, autopct=autopct_format(counts), startangle=90)
    plt.title("Distribuição de Procedimentos Judiciais com mais de 60 dias por Classe")
    plt.axis('equal')  # Ensure that pie is drawn as a circle.

    st.pyplot(plt)
