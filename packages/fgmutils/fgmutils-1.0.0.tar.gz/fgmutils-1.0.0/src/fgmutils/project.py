"""Porta da função `projectBaseOriented` do pacote R."""

from __future__ import annotations

from typing import Callable, Dict

import numpy as np
import pandas as pd

from fgmutils.calculations import calcula_volume_default
from fgmutils.prediction import predizer


def project_base_oriented(
    fit_dap,
    fit_ht,
    base: pd.DataFrame,
    first_age: float | None = None,
    last_age: float | None = None,
    mapper: Dict[str, str] | None = None,
    calc_volume: Callable[..., np.ndarray] | None = None,
    force_predict: bool = False,
) -> dict[str, pd.DataFrame]:
    if mapper is None:
        mapper = dict(age1="idadearred1", dap1="dap1", dap2="dap2", ht1="ht1", ht2="ht2")
    if calc_volume is None:
        calc_volume = calcula_volume_default

    age_col = mapper["age1"]
    dap1_col = mapper["dap1"]
    dap2_col = mapper["dap2"]
    ht1_col = mapper["ht1"]
    ht2_col = mapper["ht2"]

    ages = base[age_col]
    if first_age is None:
        first_age = np.min(ages)
    if last_age is None:
        last_age = np.max(ages)

    retorno: dict[str, pd.DataFrame] = {}

    for idade in range(int(np.floor(first_age)), int(np.ceil(last_age)) + 1):
        mask = np.isclose(base[age_col], idade)
        if not mask.any():
            continue
        b2 = base.loc[mask].copy()
        b2["volume1"] = calc_volume(dap=b2[dap1_col], ht=b2[ht1_col], base=base)
        b2["volume2"] = calc_volume(dap=b2[dap2_col], ht=b2[ht2_col], base=base)
        b2["dap2est"] = predizer(fit_dap, b2, force=force_predict)
        b2["ht2est"] = predizer(fit_ht, b2, force=force_predict)
        b2["volume2est"] = calc_volume(dap=b2["dap2est"], ht=b2["ht2est"], base=base)
        retorno[f"result_{idade}"] = b2

    if not retorno:
        raise ValueError("No data for the requested age interval")
    return retorno


__all__ = ["project_base_oriented"]
