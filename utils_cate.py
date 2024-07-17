import pandas as pd
import streamlit as st
from io import BytesIO
import matplotlib.pyplot as plt

def plotar_solicitacoes_por_unidade(df, qtd):
    """
    Gera um gráfico de barras mostrando a quantidade de solicitações por unidade solicitante.

    Args:
    df (pandas.DataFrame): DataFrame contendo os dados das solicitações.

    Returns:
    None: A função apenas exibe o gráfico.
    """
    # Agrupando os dados por 'Unidade Solicitante' e contando as ocorrências
    contagem_unidades = df['Unidade Solicitante'].value_counts().head(qtd)

    # Criando o gráfico de barras
    plt.figure(figsize=(10, 6))  # Ajusta o tamanho do gráfico
    contagem_unidades.plot(kind='bar', color='skyblue')  # Plota um gráfico de barras
    plt.title(f'Top {qtd} Unidades Solicitantes por Quantidade de Solicitações')  # Título do gráfico
    plt.xlabel('Unidade Solicitante')  # Rótulo do eixo X
    plt.ylabel('Quantidade de Solicitações')  # Rótulo do eixo Y
    plt.xticks(rotation=45, ha='right')  # Rotaciona os rótulos do eixo X para melhor visualização
    plt.tight_layout()  # Ajusta layout para não cortar informações
    st.pyplot(plt)




def cate_extract():
    arquivos = st.file_uploader("Junte seu arquivo XLS aqui", type="xlsx", accept_multiple_files=True)
    return arquivos


def cate_concatena_xlsx(arquivos):
    lista_dfs = [pd.read_excel(arquivo) for arquivo in arquivos]

    df_unificado = pd.concat(lista_dfs)

    return df_unificado


def cate_get_promotoria(df):
    promotorias = df['Unidade Solicitante'].unique()
    return list(promotorias)


def cate_filtra_por_promotoria(df, promotoria_selecionada):
    df_filtrado = df[df['Unidade Solicitante'] == promotoria_selecionada]
    return df_filtrado



def cate_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def converter_colunas_para_datetime(df, lista_colunas):
    """
    Converte múltiplas colunas de string para datetime em um DataFrame.

    Args:
    df (pandas.DataFrame): DataFrame que contém as colunas a serem convertidas.
    lista_colunas (list): Lista contendo os nomes das colunas que contêm datas em formato string.

    Returns:
    pandas.DataFrame: DataFrame com as colunas convertidas para datetime.
    """
    # Itera sobre a lista de nomes de colunas fornecida
    for coluna in lista_colunas:
        # Verifica se a coluna existe no DataFrame
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna], errors='coerce').dt.strftime('%d/%m/%Y')
        else:
            raise ValueError(f"A coluna '{coluna}' não existe no DataFrame.")

    return df