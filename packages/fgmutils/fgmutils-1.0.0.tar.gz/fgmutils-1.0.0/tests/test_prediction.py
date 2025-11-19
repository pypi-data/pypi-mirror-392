from pathlib import Path

import numpy as np
import pandas as pd
from pandas.testing import assert_series_equal

from fgmutils import prediction

DATA_FILE = Path(__file__).resolve().parent / "data" / "predizer_r_output.csv"
PARAMS_FILE = Path(__file__).resolve().parent / "data" / "predizer_model_params.csv"


def test_predizer_matches_r_output():
    df = pd.read_csv(DATA_FILE)
    params = pd.read_csv(PARAMS_FILE)

    class StubModel:
        def __init__(self, coef):
            self.params = coef
            self.exog_names = ["const", "dap", "I(dap^2)"]
            self.k_constant = 1

        def predict(self, X):
            raise RuntimeError("force fallback")

    base = df[["dap", "dap_sq"]].rename(columns={"dap_sq": "I(dap^2)"})
    coef = params["estimate"].to_numpy()
    modelo = StubModel(coef)

    predito = prediction.predizer(modelo, base)
    assert_series_equal(pd.Series(predito), df["pred"], check_names=False, atol=1e-8)
