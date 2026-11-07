import pandas as pd


def converter_datas_br(serie):
    """
    Converte uma coluna de datas para datetime respeitando o padrão brasileiro.

    Aceita valores no formato ISO ("2024-05-02" ou "2024-05-02 00:00:00", que é como
    o app recebe as datas do Excel depois de converter tudo para texto) e no formato
    dia/mês/ano ("02/05/2024"). Valores que não são datas viram NaT.

    Evita o comportamento padrão do pd.to_datetime, que lê "02/05/2024" como 5 de fevereiro.
    """
    if pd.api.types.is_datetime64_any_dtype(serie):
        return serie

    texto = serie.astype(str).str.strip().str[:10]
    iso = pd.to_datetime(texto, format="%Y-%m-%d", errors="coerce")
    br = pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(br)
