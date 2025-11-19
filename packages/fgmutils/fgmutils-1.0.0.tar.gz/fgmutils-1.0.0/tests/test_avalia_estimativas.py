from pathlib import Path
import json
import numpy as np
import pytest
import pandas as pd

from fgmutils import evaluation

DATA_FILE = Path(__file__).resolve().parent / "data" / "avalia_estimativas_reference.json"


def test_avalia_estimativas_matches_reference():
    esperado = json.loads(DATA_FILE.read_text())
    resultado = evaluation.avalia_estimativas(esperado["observado"], esperado["estimado"])
    for campo in ["b0", "b1", "rankingB0", "rankingB1"]:
        assert resultado["ranking"][campo] == pytest.approx(esperado["ranking"][campo], abs=1e-9)
    pd.testing.assert_frame_equal(
        pd.DataFrame(resultado["estatisticas"]["estatisticas"]),
        pd.DataFrame(esperado["estatisticas"]["estatisticas"]),
        check_dtype=False,
        atol=1e-9,
    )
    res_model = resultado["estatisticas"]["estatisticasDoModelo"]
    exp_model = esperado["estatisticas"]["estatisticasDoModelo"]
    np.testing.assert_allclose(res_model["value"], exp_model["value"], atol=1e-9)
