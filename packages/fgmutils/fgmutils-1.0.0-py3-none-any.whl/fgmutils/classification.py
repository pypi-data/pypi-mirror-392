"""Classificação de DAP e utilidades relacionadas."""

from __future__ import annotations

import math
import warnings
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


def round_age(plots: Iterable, ages: Iterable, in_years: bool = False, first_age: float | None = None) -> np.ndarray:
    df = pd.DataFrame({"parcela": list(plots), "idade": list(ages)})
    incr = 1 if in_years else 12
    rounded = np.full(len(df), np.nan)
    for parcela, grupo in df.groupby("parcela"):
        idades_unicas = np.sort(grupo["idade"].unique())
        if len(idades_unicas) > 1:
            diffs = np.diff(idades_unicas)
            if np.any(diffs > incr + (incr / 2)):
                warnings.warn(
                    f"pronounced difference between age intervals in parcela {parcela}",
                    RuntimeWarning,
                )
        inicio = round(float(idades_unicas[0]))
        if first_age is not None:
            inicio = first_age
        valores = inicio + np.arange(len(idades_unicas)) * incr
        mapping = dict(zip(idades_unicas, valores))
        mask = df["parcela"] == parcela
        rounded[mask.values] = df.loc[mask, "idade"].map(mapping).to_numpy()
    return rounded


def define_classes(
    limite_min: float,
    limite_max: float,
    amplitude: float,
    decrescente: bool = True,
    get_dataframe: bool = False,
    verbose: bool = False,
):
    if limite_min > limite_max or limite_min < 0:
        if verbose:
            warnings.warn("erro ao criar classe", RuntimeWarning)
        return pd.DataFrame() if get_dataframe else []
    if math.isclose(limite_min, limite_max):
        registro = [1, limite_min, limite_min, limite_max, 0, 0]
        if get_dataframe:
            return pd.DataFrame([registro], columns=["indice", "linf", "centro", "lsup", "NCLASSES", "NhaClasse"])
        return [registro[:4]]

    nro_classes = math.ceil((limite_max - limite_min) / amplitude)
    inicial = math.floor(limite_min)
    registros = []
    indice = 1
    while inicial < math.ceil(limite_max):
        if decrescente:
            idx_val = nro_classes
        else:
            idx_val = indice
        linf = inicial
        lsup = inicial + amplitude
        centro = (linf + lsup) / 2
        registros.append([idx_val, linf, centro, lsup, 0, 0])
        inicial += amplitude
        indice += 1
        nro_classes -= 1
    if get_dataframe:
        return pd.DataFrame(registros, columns=["indice", "linf", "centro", "lsup", "NCLASSES", "NhaClasse"])
    return [r[:4] for r in registros]


def define_classes2(dados: Sequence[float], amplitude: float) -> dict:
    start = math.floor(min(dados))
    end = math.ceil(max(dados))
    p_centro = np.arange(start, end + 1e-9, amplitude)
    p_classe = np.column_stack((p_centro - (amplitude / 2), p_centro + amplitude - (amplitude / 2)))
    if p_classe[-1, 1] == max(dados):
        p_classe[-1, 1] = max(dados) + 1e-8
    return {"centro": p_centro, "classe": p_classe}


def get_classes(base: pd.DataFrame, amplitude: float, verbose: bool = False) -> list[pd.DataFrame]:
    classes = []
    for _, row in base.iterrows():
        df = define_classes(row["limiteMin"], row["limiteMax"], amplitude, get_dataframe=True, verbose=verbose)
        classes.append(df)
    return classes


def classifica_classe_dap(
    df_classes_dap: pd.DataFrame,
    dap: float,
    get_nha_classe: bool = False,
    get_n_classes: bool = False,
) -> float:
    linhas = df_classes_dap.shape[0]
    if linhas == 0:
        return -1
    for i in range(linhas):
        linf = df_classes_dap.iloc[i]["linf"]
        lsup = df_classes_dap.iloc[i]["lsup"]
        centro = df_classes_dap.iloc[i]["centro"]
        if (dap >= linf) and (dap < lsup or (i == linhas - 1 and dap <= lsup)):
            if get_n_classes:
                return df_classes_dap.iloc[i]["NCLASSES"]
            if get_nha_classe:
                return df_classes_dap.iloc[i]["NhaClasse"]
            return centro
    return -1


def classificar_dap(inventario: pd.DataFrame, amplitude: float = 1, verbose: bool = False) -> pd.DataFrame:
    campos = ["projeto", "talhao", "parcela", "fila", "cova", "fuste", "idade", "idadearred", "dap", "volume", "NHa"]
    df = inventario[campos].copy()
    df["cod_id"] = (
        df["projeto"].astype(str)
        + "_"
        + df["talhao"].astype(str)
        + "_"
        + df["parcela"].astype(str)
        + "_"
        + df["fila"].astype(str)
        + "_"
        + df["cova"].astype(str)
        + "_"
        + df["fuste"].astype(str)
    )
    df["classeDAP"] = -999.0
    df["N"] = -999
    df["NCLASSES"] = -999.0
    df["VolumeTotal"] = -999.0
    df["classeDAPpriMed"] = -999.0
    df["NhaClasse"] = -999.0
    df["PROBABILIDADE"] = -999.0
    df["VolumeClasse"] = -999.0

    base = (
        df.groupby(["idadearred", "parcela"], as_index=False)
        .agg(N=("dap", "size"), limiteMin=("dap", "min"), limiteMax=("dap", "max"), VolumeTotal=("volume", "sum"))
        .sort_values(["parcela", "idadearred"], kind="mergesort")
        .reset_index(drop=True)
    )
    classes = get_classes(base, amplitude=amplitude, verbose=verbose)
    chave_para_indice = {
        (row["idadearred"], row["parcela"]): idx for idx, row in base.iterrows()
    }

    for idx, row in df.iterrows():
        chave = (row["idadearred"], row["parcela"])
        base_idx = chave_para_indice.get(chave)
        if base_idx is None:
            continue
        df.at[idx, "N"] = base.loc[base_idx, "N"]
        df.at[idx, "VolumeTotal"] = base.loc[base_idx, "VolumeTotal"]
        classe_df = classes[base_idx]
        classe = classifica_classe_dap(classe_df, row["dap"])
        df.at[idx, "classeDAP"] = classe
        mask = classe_df["centro"] == classe
        if mask.any():
            classes[base_idx].loc[mask, "NCLASSES"] += 1
            classes[base_idx].loc[mask, "NhaClasse"] += row["NHa"]

    first_class = (
        df.sort_values("idade")
        .groupby("cod_id", as_index=False)
        .first()[["cod_id", "classeDAP"]]
        .set_index("cod_id")
    )
    df["classeDAPpriMed"] = df["cod_id"].map(first_class["classeDAP"])

    for idx, row in df.iterrows():
        chave = (row["idadearred"], row["parcela"])
        base_idx = chave_para_indice.get(chave)
        if base_idx is None:
            continue
        classe_df = classes[base_idx]
        df.at[idx, "NCLASSES"] = classifica_classe_dap(classe_df, row["dap"], get_n_classes=True)
        df.at[idx, "NhaClasse"] = classifica_classe_dap(classe_df, row["dap"], get_nha_classe=True)

    df["PROBABILIDADE"] = df["NCLASSES"] / df["N"].replace(0, np.nan)
    df["VolumeClasse"] = df["PROBABILIDADE"] * df["VolumeTotal"]
    return df


__all__ = [
    "round_age",
    "define_classes",
    "define_classes2",
    "get_classes",
    "classifica_classe_dap",
    "classificar_dap",
]
