"""
Tratamento das planilhas do EMP, compartilhado pelas abas "Tratador Específico c/ Gráficos"
e "Tratador Múltiplo e Geral".

Fluxo para cada tipo de planilha:
    1. consolidar()     -> limpa cada arquivo e junta todos numa tabela só
    2. filtrar()        -> aplica os critérios da Corregedoria, ordena pelos mais atrasados,
                           numera, formata o número do processo e ajusta os nomes das colunas
    3. dados_grafico()  -> tabela usada nos gráficos da aba 2
"""
import pandas as pd

from utils_datas import converter_datas_br
from utils_df import (apply_pipeline, convert_collum_date, exclude_specific_classes, extract_last_date,
                      filter_df_by_criteria, filter_df_by_ip, gerar_dataframe_filtrado,
                      gerar_dataframe_filtrado_extra_nf, nf_pp_fora_prazo, normalize_column_types,
                      normalize_columns, remove_empty_columns, remove_empty_rows, remove_nan_columns,
                      remove_to_classe, rename_duplicate_columns, select_nf_pp_data_in_df, title_case_column)

EXTRA = "extra sem impulsionamento"
JUDI = "judi com vista"
NF_PP = "relatório extraj"
IPS = "ips sem impulsionamento"

TIPOS = [EXTRA, JUDI, NF_PP, IPS]


def identificar_tipo(nome_arquivo):
    """Tipo da planilha pelo nome do arquivo (ou None se não for reconhecido)."""
    nome = nome_arquivo.lower()
    return next((tipo for tipo in TIPOS if tipo in nome), None)


# ---------------------------------------------------------------------------
# 1. Consolidação
# ---------------------------------------------------------------------------
_PREPARO_POR_ARQUIVO = {
    EXTRA: [remove_to_classe],
    JUDI: [remove_to_classe],
    NF_PP: [remove_nan_columns, remove_empty_columns, rename_duplicate_columns, select_nf_pp_data_in_df,
            remove_to_classe, remove_nan_columns, normalize_columns],
    IPS: [remove_to_classe, normalize_column_types, normalize_columns, remove_empty_rows,
          remove_empty_columns, extract_last_date, filter_df_by_ip],
}


def consolidar(tipo, lista_dfs):
    """Prepara cada planilha do mesmo tipo e junta todas numa única tabela."""
    tratados = [apply_pipeline(df, _PREPARO_POR_ARQUIVO[tipo]) for df in lista_dfs]
    return pd.concat(tratados, axis=0, join="outer", ignore_index=True)


# ---------------------------------------------------------------------------
# 2. Filtro, ordenação e formatação
# ---------------------------------------------------------------------------
def ordenar_mais_atrasados(df, tipo):
    """
    Coloca os mais atrasados no topo:
      - Judi com vista: maior "Dias Andamento" primeiro;
      - NF/PP: maior "Dias Fora" primeiro;
      - Extra e IPs: último impulsionamento mais antigo primeiro
        (sem impulsionamento registrado, vale a data de instauração).
    """
    if tipo == JUDI:
        chave, crescente = pd.to_numeric(df["dias andamento"], errors="coerce"), False
    elif tipo == NF_PP:
        chave, crescente = pd.to_numeric(df["dias fora"], errors="coerce"), False
    else:
        vazio = pd.Series(pd.NaT, index=df.index)
        ultimo = converter_datas_br(df["data do último impulsionamento"]) \
            if "data do último impulsionamento" in df.columns else vazio
        instauracao = converter_datas_br(df["instauração"]) if "instauração" in df.columns else vazio
        chave, crescente = ultimo.fillna(instauracao), True

    return (df.assign(_chave_ordem=chave.values)
              .sort_values("_chave_ordem", ascending=crescente, na_position="last", kind="stable")
              .drop(columns="_chave_ordem"))


def formatar_numero_cnj(valor):
    """
    Coloca a máscara nos números de processo que vêm só com dígitos:
      - judicial (CNJ, 20 dígitos): 00000534820118200103 -> 0000053-48.2011.8.20.0103
      - MP (21 dígitos):  022321480000045202532 -> 02.23.2148.0000045/2025-32
    Valores que já têm máscara ou não são números de processo ficam como estão.
    """
    texto = str(valor).strip()
    if texto.endswith(".0"):
        texto = texto[:-2]
    if not texto.isdigit():
        return valor
    if len(texto) == 21:
        d = texto
        return f"{d[:2]}.{d[2:4]}.{d[4:8]}.{d[8:15]}/{d[15:19]}-{d[19:]}"
    # 15 a 19 dígitos: número CNJ salvo como numérico no Excel, que perdeu os zeros à esquerda
    if 15 <= len(texto) <= 20:
        d = texto.zfill(20)
        return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"
    return valor


_COLUNAS_NUMERO_PROCESSO = {"procedimento", "número", "número processo", "nº processo"}


def formatar_numeros_processo(df):
    df = df.copy()
    for coluna in df.columns:
        if str(coluna).strip().lower() in _COLUNAS_NUMERO_PROCESSO:
            df[coluna] = df[coluna].map(formatar_numero_cnj)
    return df


_FILTROS = {
    EXTRA: [exclude_specific_classes, extract_last_date,
            lambda df: ordenar_mais_atrasados(df, EXTRA),
            lambda df: gerar_dataframe_filtrado(df, ["classe", "número", "prazo legal"])],
    JUDI: [normalize_columns, filter_df_by_criteria,
           lambda df: ordenar_mais_atrasados(df, JUDI),
           lambda df: gerar_dataframe_filtrado(df, ["procedimento", "classe", "assunto", "data registro",
                                                    "dias andamento"])],
    NF_PP: [nf_pp_fora_prazo,
            lambda df: ordenar_mais_atrasados(df, NF_PP),
            gerar_dataframe_filtrado_extra_nf,
            lambda df: convert_collum_date(df, ["instauração", "30 dias", "120 dias"])],
    IPS: [lambda df: ordenar_mais_atrasados(df, IPS),
          lambda df: gerar_dataframe_filtrado(df, ["classe", "número", "assunto"])],
}


def filtrar(tipo, df_consolidado):
    """Tabela final (a que vai para a tela, o Excel e o PDF)."""
    etapas = _FILTROS[tipo] + [formatar_numeros_processo, title_case_column]
    return apply_pipeline(df_consolidado.copy(), etapas)


# ---------------------------------------------------------------------------
# 3. Dados para os gráficos (aba 2)
# ---------------------------------------------------------------------------
def dados_grafico(tipo, df_consolidado):
    df = df_consolidado.copy()
    if tipo == EXTRA:
        return apply_pipeline(df, [exclude_specific_classes, extract_last_date])
    if tipo == NF_PP:
        return nf_pp_fora_prazo(df)
    return df
