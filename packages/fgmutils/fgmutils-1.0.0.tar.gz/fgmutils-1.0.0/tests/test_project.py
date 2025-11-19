from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from pandas.testing import assert_frame_equal

from fgmutils import project
from fgmutils.calculations import calcula_volume_default

DATA_DIR = Path(__file__).resolve().parent / "data" / "project_base_oriented"


def _build_base() -> pd.DataFrame:
    ages = np.repeat([60, 72, 84], 4)
    dap2 = np.array([14, 15, 16, 17, 16, 17, 18, 19, 18, 19, 20, 21], dtype=float)
    ht2 = np.array([10, 11, 12, 13, 11, 12, 13, 14, 12, 13, 14, 15], dtype=float)
    base = pd.DataFrame(
        {
            "idadearred1": ages,
            "dap1": dap2 * 0.95,
            "dap2": dap2,
            "ht1": ht2 * 0.98,
            "ht2": ht2,
        }
    )
    base["volume"] = calcula_volume_default(base["ht2"], base["dap2"])
    return base


def test_project_base_oriented_matches_r_outputs():
    base = _build_base()
    fit_dap = sm.OLS(base["dap2"], sm.add_constant(base["dap1"])).fit()
    fit_ht = sm.OLS(base["ht2"], sm.add_constant(base["ht1"])).fit()

    resultado = project.project_base_oriented(
        fit_dap=fit_dap,
        fit_ht=fit_ht,
        base=base,
        mapper=dict(age1="idadearred1", dap1="dap1", dap2="dap2", ht1="ht1", ht2="ht2"),
        calc_volume=calcula_volume_default,
    )

    for arquivo in sorted(DATA_DIR.glob("result_*.csv")):
        esperado = pd.read_csv(arquivo)
        chave = arquivo.stem
        obtido = resultado[chave].reset_index(drop=True)
        assert_frame_equal(obtido, esperado, check_dtype=False, atol=1e-10)
