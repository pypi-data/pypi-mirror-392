from pathlib import Path

import json

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
import statsmodels.api as sm

from fgmutils import project, evaluation, calculations

DATA_DIR = Path(__file__).resolve().parent / "data"
JSON_FILE = DATA_DIR / "eval_age_based_reference.json"


def build_base() -> pd.DataFrame:
    ages = np.repeat([60, 72, 84], 4)
    dap = np.array([14, 15, 16, 17, 16, 17, 18, 19, 18, 19, 20, 21], dtype=float)
    ht = np.array([10, 11, 12, 13, 11, 12, 13, 14, 12, 13, 14, 15], dtype=float)
    df = pd.DataFrame({
        "idade1": ages,
        "dap": dap,
        "ht": ht,
    })
    df["dap1"] = df["dap"] * 0.95
    df["dap2"] = df["dap"]
    df["ht1"] = df["ht"] * 0.98
    df["ht2"] = df["ht"]
    df["volume"] = calculations.calcula_volume_default(df["ht2"], df["dap2"])
    return df


def build_list_of_data(base: pd.DataFrame):
    fit_dap = sm.OLS(base["dap2"], sm.add_constant(base["dap1"])).fit()
    fit_ht = sm.OLS(base["ht2"], sm.add_constant(base["ht1"])).fit()
    return project.project_base_oriented(
        fit_dap=fit_dap,
        fit_ht=fit_ht,
        base=base,
        mapper=dict(age1="idade1", dap1="dap1", dap2="dap2", ht1="ht1", ht2="ht2"),
        calc_volume=calculations.calcula_volume_default,
    )


def test_eval_age_based_matches_reference():
    base = build_base()
    lista = build_list_of_data(base)
    resultado = evaluation.eval_age_based(lista, mapper=dict(
        volume2="volume",
        volume2est="volume2est",
        dap2="dap2",
        dap2est="dap2est",
        ht2="ht2",
        ht2est="ht2est",
    ))
    esperado = json.loads(JSON_FILE.read_text())
    assert resultado.keys() == esperado.keys()
    for sec in ["dap", "ht", "volume"]:
        for key, val in esperado[sec].items():
            if key == "ranking":
                assert resultado[sec][key]["rankingB0"] == pytest.approx(val["rankingB0"], abs=1e-9)
                assert resultado[sec][key]["rankingB1"] == pytest.approx(val["rankingB1"], abs=1e-9)
            else:
                res_rank = resultado[sec][key]["ranking"]
                exp_rank = val["ranking"]
                assert res_rank["rankingB0"] == pytest.approx(exp_rank["rankingB0"], abs=1e-9)
                assert res_rank["rankingB1"] == pytest.approx(exp_rank["rankingB1"], abs=1e-9)
                res_stats = pd.DataFrame(resultado[sec][key]["estatisticas"]["estatisticas"])
                exp_stats = pd.DataFrame(val["estatisticas"]["estatisticas"])
                assert_frame_equal(res_stats, exp_stats, check_dtype=False, atol=1e-9)
                res_model = resultado[sec][key]["estatisticas"]["estatisticasDoModelo"]
                exp_model = val["estatisticas"]["estatisticasDoModelo"]
                np.testing.assert_allclose(res_model["value"], exp_model["value"], atol=1e-9)
    assert resultado["ranking"]["rankingB0"] == pytest.approx(esperado["ranking"]["rankingB0"], abs=1e-9)
    assert resultado["ranking"]["rankingB1"] == pytest.approx(esperado["ranking"]["rankingB1"], abs=1e-9)
