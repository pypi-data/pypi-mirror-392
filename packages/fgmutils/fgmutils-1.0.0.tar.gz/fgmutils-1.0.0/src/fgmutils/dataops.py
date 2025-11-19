"""Data wrangling helpers inspired by the R utilities."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from pandas.api import types as ptypes

from fgmutils import utils


def add_column(df: pd.DataFrame, values: Iterable, column_name: str) -> pd.DataFrame:
    """Replicate ``add.col`` padding shorter vectors with ``NaN``."""

    frame = df.copy()
    values_series = pd.Series(list(values))
    target_len = max(len(frame), len(values_series))
    frame = frame.reindex(range(target_len)).reset_index(drop=True)
    values_series = values_series.reindex(range(target_len))
    frame[column_name] = values_series.values
    return frame


def convert_column_to_str(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Convert a column to ``str`` (``converteCampoParaCharacter``)."""

    if column_name not in df.columns:
        raise KeyError(f"Column '{column_name}' not found")
    frame = df.copy()
    frame[column_name] = frame[column_name].astype(str)
    return frame


def separa_dados(
    df: pd.DataFrame,
    field_name: str,
    perc_training: float = 0.70,
    seed: int | None = None,
):
    """Split a dataframe into treino/validacao groups, mirroring ``separaDados``."""

    if field_name not in df.columns:
        raise KeyError(f"Campo '{field_name}' inexistente na base")
    if perc_training <= 0.01 or perc_training > 1:
        raise ValueError("perc_training deve estar entre 0.01 e 1")

    unique_ids = df[[field_name]].drop_duplicates().reset_index(drop=True)
    total = len(unique_ids)
    tamanho = int(np.floor(total * perc_training))
    rng = np.random.RandomState(seed)
    if tamanho > 0:
        idx_treino = np.sort(rng.choice(total, size=tamanho, replace=False))
    else:
        idx_treino = np.array([], dtype=int)
    treino_ids = unique_ids.iloc[idx_treino].reset_index(drop=True)
    mascara_validacao = np.ones(total, dtype=bool)
    mascara_validacao[idx_treino] = False
    validacao_ids = unique_ids.loc[mascara_validacao].reset_index(drop=True)

    treino_df = df[df[field_name].isin(treino_ids[field_name])].reset_index(drop=True)
    validacao_df = df[df[field_name].isin(validacao_ids[field_name])].reset_index(drop=True)

    perc_validacao = (len(validacao_ids) / total) if total else 0.0
    percentual = {"treino": 1 - perc_validacao, "validacao": perc_validacao}

    return {
        "individuos": {"treino": treino_ids, "validacao": validacao_ids},
        "nro_individuos": total,
        "percentual": percentual,
        "treino": treino_df,
        "validacao": validacao_df,
    }


def atualiza_campo_base(
    campos_atualizar: Sequence[str],
    base_agrupada: pd.DataFrame,
    base_atualizar: pd.DataFrame,
    keys: Sequence[str],
) -> pd.DataFrame:
    """Atualiza colunas de ``base_atualizar`` com os valores agregados via ``keys``."""

    if not campos_atualizar:
        raise ValueError("Informe ao menos um campo para atualizar")
    for key in keys:
        if key not in base_agrupada.columns or key not in base_atualizar.columns:
            raise KeyError(f"Chave '{key}' inexistente em uma das bases")
    for col in campos_atualizar:
        if col not in base_agrupada.columns:
            raise KeyError(f"Campo '{col}' nao existe na base agregada")

    agr = base_agrupada.copy()
    att = base_atualizar.copy()

    for key in keys:
        if agr[key].dtype != att[key].dtype:
            agr[key] = agr[key].astype(str)
            att[key] = att[key].astype(str)

    for col in campos_atualizar:
        att[col] = _default_series(agr[col], len(att))

    updates = agr[list(keys) + list(campos_atualizar)]
    updates = updates.drop_duplicates(subset=keys, keep="last").set_index(keys)
    att_indexed = att.set_index(keys)
    att_indexed.update(updates)
    return att_indexed.reset_index()


def cria_dados_pareados(
    data_frame: pd.DataFrame,
    campo_chave: str,
    campo_comparacao: str,
    campos_pareados: Sequence[str],
    campos_nao_pareados: Sequence[str],
):
    """Replica ``criaDadosPareados`` usando pandas."""

    required = {campo_chave, campo_comparacao, *campos_pareados, *campos_nao_pareados}
    missing = required.difference(data_frame.columns)
    if missing:
        raise KeyError(f"Campos inexistentes: {', '.join(sorted(missing))}")

    base = data_frame.copy().sort_values([campo_chave, campo_comparacao]).reset_index(drop=True)
    base.columns = [col.lower() for col in base.columns]
    campo_chave = campo_chave.lower()
    campo_comparacao = campo_comparacao.lower()
    campos_pareados = [c.lower() for c in campos_pareados]
    campos_nao_pareados = [c.lower() for c in campos_nao_pareados]

    column_order = [
        campo_chave,
        f"{campo_comparacao}1",
        f"{campo_comparacao}2",
    ]
    for campo in campos_pareados:
        column_order.extend([f"{campo}1", f"{campo}2"])
    column_order.extend(campos_nao_pareados)

    result = pd.DataFrame({col: pd.Series(dtype=_result_dtype(base, col, campo_comparacao)) for col in column_order})

    registros: list[dict[str, object]] = []
    for idx in range(1, len(base)):
        anterior = base.iloc[idx - 1]
        atual = base.iloc[idx]
        if atual[campo_chave] == anterior[campo_chave] and atual[campo_comparacao] > anterior[campo_comparacao]:
            registro: dict[str, object] = {
                campo_chave: utils.return_value(anterior[campo_chave]),
                f"{campo_comparacao}1": utils.return_value(anterior[campo_comparacao]),
                f"{campo_comparacao}2": utils.return_value(atual[campo_comparacao]),
            }
            for campo in campos_pareados:
                registro[f"{campo}1"] = utils.return_value(anterior[campo])
                registro[f"{campo}2"] = utils.return_value(atual[campo])
            for campo in campos_nao_pareados:
                registro[campo] = utils.return_value(atual[campo])
            registros.append(registro)

    if registros:
        result = pd.DataFrame(registros)[column_order]
    return result


def _default_series(template: pd.Series, length: int) -> pd.Series:
    if length == 0:
        return pd.Series(dtype=template.dtype)
    if ptypes.is_bool_dtype(template):
        fill_value = True
    elif ptypes.is_numeric_dtype(template):
        fill_value = -999
    else:
        fill_value = "-999"
    return pd.Series([fill_value] * length, dtype=template.dtype)


def _result_dtype(base: pd.DataFrame, column: str, campo_comparacao: str):
    mapping = {c: c for c in base.columns}
    reference = column
    if column.endswith("1") or column.endswith("2"):
        prefix = column[:-1]
        reference = prefix if prefix in mapping else campo_comparacao
    if reference not in base.columns:
        return float
    serie = base[reference]
    if ptypes.is_numeric_dtype(serie):
        return float
    return object

__all__ = [
    "add_column",
    "convert_column_to_str",
    "separa_dados",
    "atualiza_campo_base",
    "cria_dados_pareados",
]
