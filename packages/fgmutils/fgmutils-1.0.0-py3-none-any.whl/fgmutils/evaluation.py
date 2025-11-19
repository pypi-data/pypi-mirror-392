"""Avaliação de estimativas e projeções por idade."""

from __future__ import annotations

from typing import Dict, Iterable

import numpy as np
import pandas as pd

from fgmutils import metrics


DEFAULT_STATS = (
    ("bias", metrics.bias),
    ("mae", metrics.mae),
    ("rmse", metrics.rmse),
    ("ce", metrics.ce),
)


def avalia_estimativas(
    observado: Iterable[float],
    estimado: Iterable[float],
    tabela: pd.DataFrame | None = None,
    estatisticas_funcs = None,
) -> dict:
    obs = np.asarray(observado, dtype=float)
    est = np.asarray(estimado, dtype=float)
    valores = pd.DataFrame({"observado": obs, "estimado": est})
    if tabela is not None:
        combinado = pd.concat([valores.reset_index(drop=True), tabela.reset_index(drop=True)], axis=1)
    else:
        combinado = valores
    slope, intercept = _fit_linear(obs, est)
    ranking = {
        "b0": float(intercept),
        "b1": float(slope),
        "rankingB0": float(abs(intercept)),
        "rankingB1": float(abs(slope - 1)),
    }
    funcs = estatisticas_funcs or DEFAULT_STATS
    metrics_model = {
        "name": [name for name, _ in funcs],
        "value": [float(func(obs, est)) for _, func in funcs],
    }
    return {
        "ranking": ranking,
        "observado": obs.tolist(),
        "estimado": est.tolist(),
        "estatisticas": {
            "estatisticas": combinado.to_dict(orient="list"),
            "estatisticasDoModelo": metrics_model,
        },
    }


def evaluate_estimates(observado: Iterable[float], estimado: Iterable[float], tabela: pd.DataFrame) -> dict:
    return avalia_estimativas(observado, estimado, tabela)


def eval_age_based(list_of_data: Dict[str, pd.DataFrame], mapper: dict | None = None) -> dict:
    if mapper is None:
        mapper = dict(
            volume2="volume",
            volume2est="volume2est",
            dap2="dap2",
            dap2est="dap2est",
            ht2="ht2",
            ht2est="ht2est",
        )
    tipos = (
        ("dap", mapper["dap2"], mapper["dap2est"]),
        ("ht", mapper["ht2"], mapper["ht2est"]),
        ("volume", mapper["volume2"], mapper["volume2est"]),
    )
    retorno = {}
    rank_total = {"rankingB0": 0.0, "rankingB1": 0.0}
    base_concat = None
    for idx, (tipo, obs_col, est_col) in enumerate(tipos):
        tipo_dict = {}
        b0_sum = 0.0
        b1_sum = 0.0
        for nome, tabela in list_of_data.items():
            res = avalia_estimativas(tabela[obs_col], tabela[est_col], tabela)
            tipo_dict[f"Estatistics_Age_{nome.split('result_')[-1]}"] = res
            b0_sum += res["ranking"]["rankingB0"]
            b1_sum += res["ranking"]["rankingB1"]
            if idx == 0:
                base_concat = tabela if base_concat is None else pd.concat([base_concat, tabela], ignore_index=True)
        tipo_dict["ranking"] = {"rankingB0": b0_sum, "rankingB1": b1_sum}
        retorno[tipo] = tipo_dict
        rank_total["rankingB0"] += b0_sum
        rank_total["rankingB1"] += b1_sum
    retorno["base"] = base_concat.to_dict(orient="list") if base_concat is not None else {}
    retorno["ranking"] = rank_total
    return retorno


def _fit_linear(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    return float(slope), float(intercept)


__all__ = ["evaluate_estimates", "eval_age_based"]
