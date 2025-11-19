"""Predição resiliente reproduzindo o comportamento de `predizer` em R."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def get_columns_of_adjust(model: Any) -> list[str]:
    names = None
    if hasattr(model, "exog_names"):
        names = list(getattr(model, "exog_names"))
    elif hasattr(model, "model") and hasattr(model.model, "exog_names"):
        names = list(model.model.exog_names)
    if names is not None:
        return names[1:] if names and names[0].lower() in {"const", "intercept"} else names
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)
    raise ValueError("Model does not expose column metadata")


def predizer(model: Any, newdata: pd.DataFrame, force: bool = False) -> np.ndarray:
    try:
        predito = model.predict(newdata)
    except Exception:  # pragma: no cover - fallback to manual pipeline
        predito = np.zeros(len(newdata))

    if not np.allclose(predito, 0) and not force:
        return np.asarray(predito)

    columns = get_columns_of_adjust(model)
    base_validacao = _extract_columns(newdata, columns)
    predito = _fallback_predict(model, base_validacao)
    return np.asarray(predito)


def _fallback_predict(model: Any, base_validacao: pd.DataFrame) -> np.ndarray:
    import statsmodels.api as sm

    params = getattr(model, "params", None)
    exog_names = getattr(model, "exog_names", None)
    if exog_names is None and hasattr(model, "model"):
        exog_names = getattr(model.model, "exog_names", None)
    if params is not None and exog_names is not None:
        k_const = getattr(model, "k_constant", getattr(getattr(model, "model", None), "k_constant", 0))
        has_const_flag = "raise" if k_const else "add"
        design = sm.add_constant(base_validacao, has_constant=has_const_flag)
        return design.to_numpy() @ params
    if hasattr(model, "coef_"):
        coefs = np.atleast_1d(model.coef_)
        intercept = np.atleast_1d(getattr(model, "intercept_", 0.0))
        design = sm.add_constant(base_validacao, has_constant="add")
        params = np.concatenate([intercept, coefs])
        return design.to_numpy() @ params
    raise ValueError("Unable to reconstruct prediction from provided model")


def _extract_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    data = {}
    for coluna in columns:
        if coluna in df.columns:
            data[coluna] = df[coluna]
            continue
        if coluna.startswith("I(") and coluna.endswith(")"):
            expr = coluna[2:-1]
            data[coluna] = df.eval(expr)
            continue
        raise KeyError(f"Coluna '{coluna}' não encontrada na base de predição")
    return pd.DataFrame(data)


__all__ = ["predizer", "get_columns_of_adjust"]
