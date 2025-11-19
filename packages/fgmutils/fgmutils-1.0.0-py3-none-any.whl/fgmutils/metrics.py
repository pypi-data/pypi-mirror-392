"""Statistical metrics used across the FGM ecosystem."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

ArrayLike = np.typing.ArrayLike  # type: ignore[attr-defined]


def _as_array(values: ArrayLike) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1:
        return array.reshape(-1)
    return array


def mae(observed: ArrayLike, estimated: ArrayLike) -> float:
    """Mean absolute error."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    return float(np.mean(np.abs(obs - est)))


def rmse(observed: ArrayLike, estimated: ArrayLike) -> float:
    """Root mean square error."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    return float(np.sqrt(np.mean((obs - est) ** 2)))


def bias(observed: ArrayLike, estimated: ArrayLike) -> float:
    """Average difference between predictions and observations."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    return float(np.sum(est - obs) / obs.size)


def mse(observed: ArrayLike, estimated: ArrayLike, k: int) -> float:
    """Mean squared error with Bessel style correction from the R package."""

    if k < 0:
        raise ValueError("k must be non-negative")
    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    denom = obs.size - k
    if denom <= 0:
        raise ValueError("obs.size - k must be > 0 for mse calculation")
    return float(np.sum((est - obs) ** 2) / denom)


def mspr(observed: ArrayLike, estimated: ArrayLike, n_validation: int) -> float:
    """Mean square of prediction residuals."""

    if n_validation <= 0:
        raise ValueError("n_validation must be positive")
    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    return float(np.sum((obs - est) ** 2) / n_validation)


def rrmse(observed: ArrayLike, estimated: ArrayLike) -> float:
    """Relative RMSE using the corrected formula supplied by the user."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    mean_obs = np.mean(obs)
    if mean_obs == 0:
        raise ZeroDivisionError("Mean of observed values is zero, cannot compute RRMSE")
    return float(rmse(obs, est) / mean_obs)


def syx(observed: ArrayLike, estimated: ArrayLike, n: int | None = None, p: int = 0) -> float:
    """Standard error of estimate."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    total_n = n if n is not None else obs.size
    if total_n <= p + 1:
        raise ValueError("n must be greater than p + 1")
    return float(np.sqrt(np.sum((obs - est) ** 2) / (total_n - p - 1)))


def syx_perc(syx_value: float, observed: ArrayLike) -> float:
    """Relative version of ``syx`` in percentage."""

    obs = _as_array(observed)
    mean_obs = np.mean(obs)
    if mean_obs == 0:
        raise ZeroDivisionError("Mean of observed values is zero, cannot compute percentage")
    return float((syx_value / mean_obs) * 100)


def ce(observed: ArrayLike, estimated: ArrayLike) -> float:
    """Nash–Sutcliffe efficiency coefficient."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    numerator = np.sum(obs - est) ** 2
    denominator = np.sum(obs - (np.mean(obs) ** 2))
    if denominator == 0:
        raise ZeroDivisionError("Variance of observed values is zero, cannot compute CE")
    return float(1 - numerator / denominator)


def r21a(observed: ArrayLike, estimated: ArrayLike, k: int) -> float:
    """Adjusted determination coefficient assuming intercept."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    if k < 0:
        raise ValueError("k must be non-negative")
    a_value = _calc_a(obs.size, k)
    r2 = 1 - np.sum((obs - est) ** 2) / np.sum((obs - np.mean(obs)) ** 2)
    return float(1 - a_value * (1 - r2))


def r29a(observed: ArrayLike, estimated: ArrayLike, k: int) -> float:
    """Alternative adjusted determination coefficient without intercept."""

    obs = _as_array(observed)
    est = _as_array(estimated)
    _validate_same_length(obs, est)
    if k < 0:
        raise ValueError("k must be non-negative")
    a_value = _calc_a(obs.size, k)
    r2 = 1 - np.median(np.abs(obs - est) ** 2) / np.median(np.abs(obs - np.mean(obs)) ** 2)
    return float(1 - a_value * (1 - r2))


def _calc_a(n: int, k: int) -> float:
    if n - k - 1 == 0:
        raise ZeroDivisionError("n - k - 1 must not be zero when computing adjustment factor")
    return (n - 1) / (n - k - 1)


def _validate_same_length(observed: np.ndarray, estimated: np.ndarray) -> None:
    if observed.size != estimated.size:
        raise ValueError("observed and estimated series must contain the same number of elements")


__all__ = [
    "mae",
    "rmse",
    "bias",
    "mse",
    "mspr",
    "rrmse",
    "syx",
    "syx_perc",
    "ce",
    "r21a",
    "r29a",
]
