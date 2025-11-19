"""Funções de cálculo utilitárias (porta direta do R)."""

from __future__ import annotations

import numpy as np


def calcula_volume_default(ht, dap, *_args, **_kwargs):
    """Reimplementa `calculaVolumeDefault` do R."""

    b0 = -10.1399754928663
    b1 = 1.86835930704287
    b2 = 1.07778665273381
    ht = np.asarray(ht, dtype=float)
    dap = np.asarray(dap, dtype=float)
    return np.exp(b0 + b1 * np.log(dap) + b2 * np.log(ht))


__all__ = ["calcula_volume_default"]
