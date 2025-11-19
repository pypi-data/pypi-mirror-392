"""Implementações Python das rotinas de estatísticas do FGMUtils."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

import numpy as np

from fgmutils import metrics


@dataclass
class StatisticsResult:
    values: np.ndarray
    metrics: List[Dict[str, float]]


def run_statistics(
    observado,
    estimado,
    intercepto: bool = True,
    ajuste: Callable | None = None,
) -> StatisticsResult:
    obs = np.asarray(observado, dtype=float)
    est = np.asarray(estimado, dtype=float)
    metrics_list = []
    metrics_list.append({"name": "bias", "value": metrics.bias(obs, est)})
    metrics_list.append({"name": "mae", "value": metrics.mae(obs, est)})
    metrics_list.append({"name": "rmse", "value": metrics.rmse(obs, est)})
    metrics_list.append({"name": "ce", "value": _nash_sutcliffe(obs, est)})
    k = ajuste if isinstance(ajuste, int) else len(obs)
    if intercepto:
        metrics_list.append({"name": "r2", "value": metrics.r21a(obs, est, k=k)})
    else:
        metrics_list.append({"name": "r2", "value": metrics.r29a(obs, est, k=k)})
    values = np.column_stack((obs, est))
    return StatisticsResult(values=values, metrics=metrics_list)


__all__ = ["run_statistics", "StatisticsResult"]


def _nash_sutcliffe(obs: np.ndarray, est: np.ndarray) -> float:
    numerator = np.sum(obs - est) ** 2
    denominator = np.sum(obs - (np.mean(obs) ** 2))
    if denominator == 0:
        return float("nan")
    return float(1 - numerator / denominator)
