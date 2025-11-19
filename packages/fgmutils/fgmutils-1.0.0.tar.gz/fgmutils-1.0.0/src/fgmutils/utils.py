"""Utility functions ported from the R helpers."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np


def return_value(value):
    """Mimic ``retornaValor``: strings stay strings, everything else becomes numeric."""

    if isinstance(value, str):
        return value
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - defensive branch
        raise ValueError("Value cannot be coerced to float") from exc


def check_integer(value) -> bool:
    """Replicate the check.integer logic from the R package."""

    if isinstance(value, (int, np.integer)):
        return True
    if isinstance(value, (float, np.floating)):
        return value.is_integer()
    return False


def verifica_tipo_coluna(column: Sequence) -> str:
    """Return the conversion hint used by the R helper."""

    array = np.asarray(column)
    if array.dtype.kind in {"U", "S", "O"}:
        return "as.character()"
    return "as.numeric()"


__all__ = ["return_value", "check_integer", "verifica_tipo_coluna"]
