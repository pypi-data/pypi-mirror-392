from pathlib import Path

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from fgmutils import statistics

DATA_DIR = (Path(__file__).resolve().parent / "data")
VALUES_CSV = DATA_DIR / "estatisticas_values.csv"
METRICS_CSV = DATA_DIR / "estatisticas_metrics.csv"


def test_run_statistics_matches_r():
    esperado_values = pd.read_csv(VALUES_CSV)
    esperado_metrics = pd.read_csv(METRICS_CSV)

    resultado = statistics.run_statistics(
        observado=esperado_values["observado"],
        estimado=esperado_values["estimado"],
        intercepto=True,
        ajuste=0,
    )

    obtido_values = pd.DataFrame(resultado.values, columns=["observado", "estimado"])
    obtido_metrics = pd.DataFrame(resultado.metrics)

    assert_frame_equal(obtido_values, esperado_values, check_dtype=False)
    assert_frame_equal(obtido_metrics, esperado_metrics, check_dtype=False)
