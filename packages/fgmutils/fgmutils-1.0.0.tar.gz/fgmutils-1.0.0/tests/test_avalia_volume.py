from pathlib import Path
import json

import numpy as np
import pandas as pd
import pytest
import statsmodels.formula.api as smf

from fgmutils.volume import avalia_volume_avancado, avalia_volume_age_based
from fgmutils.calculations import calcula_volume_default

BASE_FILE = Path(__file__).resolve().parent / "data" / "avalia_volume_base.csv"
REFERENCE_FILE = Path(__file__).resolve().parent / "data" / "avalia_volume_reference.json"
AGE_BASE_FILE = Path(__file__).resolve().parent / "data" / "avalia_volume_age_base.csv"
AGE_REFERENCE_FILE = Path(__file__).resolve().parent / "data" / "avalia_volume_age_reference.json"


class FormulaModel:
    def __init__(self, name: str, template: str):
        self.name = name
        self.template = template

    def __call__(self, y1: str = None, y2: str = None, base: pd.DataFrame = None):
        if y1 is None or y2 is None or base is None:
            return (self.name, self.template)
        formula = self.template.format(y1=y1, y2=y2)
        return smf.ols(formula, data=base).fit()


def test_avalia_volume_avancado_matches_reference():
    base = pd.read_csv(BASE_FILE)
    modelos = [
        FormulaModel("ModeloLinear", "{y2} ~ {y1}"),
        FormulaModel("ModeloQuadratico", "{y2} ~ {y1} + I({y1}**2)"),
    ]
    esperado = json.loads(REFERENCE_FILE.read_text())
    resultado = avalia_volume_avancado(
        base=base,
        mapeamento={"dap1": "dap1", "dap2": "dap2", "ht1": "ht1", "ht2": "ht2"},
        modelos=modelos,
        dividir_em="parcela",
        percentual_de_treino=0.7,
        agrupar_por="parcela",
        fn_calcula_volume=calcula_volume_default,
        force_predict=False,
        split=esperado.get("split"),
    )

    for key in ["rank", "b0", "b1"]:
        assert resultado["ranking"][key] == pytest.approx(esperado["ranking"][key])
    pd.testing.assert_frame_equal(
        pd.DataFrame(resultado["base"]),
        pd.DataFrame(esperado["base"]),
        check_dtype=False,
        atol=1e-9,
    )
    for nome, stats in esperado["estatisticas"].items():
        res_stats = resultado["estatisticas"][nome]
        assert res_stats["ranking"]["b0"] == pytest.approx(stats["ranking"]["b0"])
        assert res_stats["ranking"]["b1"] == pytest.approx(stats["ranking"]["b1"])
        pd.testing.assert_frame_equal(
            pd.DataFrame(res_stats["estatisticas"]["estatisticas"]),
            pd.DataFrame(stats["estatisticas"]["estatisticas"]),
            check_dtype=False,
            atol=1e-9,
        )


def test_avalia_volume_age_based_matches_reference():
    base = pd.read_csv(AGE_BASE_FILE)
    esperado = json.loads(AGE_REFERENCE_FILE.read_text())
    split = esperado.get("split")
    modelos = [
        FormulaModel("ModeloLinear", "{y2} ~ {y1}"),
        FormulaModel("ModeloQuadratico", "{y2} ~ {y1} + I({y1}**2)"),
    ]
    mapper = {
        "age1": "idade1",
        "age2": "idade2",
        "dap1": "dap1",
        "dap2": "dap2",
        "dap2est": "dap2est",
        "ht1": "ht1",
        "ht2": "ht2",
        "ht2est": "ht2est",
        "volume1": "volume1",
        "volume2": "volume2",
        "volume2est": "volume2est",
    }
    resultado = avalia_volume_age_based(
        base=base,
        first_age=int(np.floor(base["idade1"].min())),
        last_age=int(np.ceil(base["idade2"].max())),
        modelos=modelos,
        mapper=mapper,
        split=split,
        fn_calcula_volume=calcula_volume_default,
        age_round=int(np.floor(base["idade1"].min())),
    )

    for campo in ["base", "baseTreino", "baseValidacao"]:
        pd.testing.assert_frame_equal(
            pd.DataFrame(resultado[campo]),
            pd.DataFrame(esperado[campo]),
            check_dtype=False,
            atol=1e-9,
        )

    for key in ["model", "rankingB0", "rankingB1"]:
        assert resultado["ranking"][key] == pytest.approx(esperado["ranking"][key])

    for nome_modelo in ["ModeloLinear", "ModeloQuadratico"]:
        res_modelo = resultado[nome_modelo]
        exp_modelo = esperado[nome_modelo]
        assert res_modelo["ranking"]["rankingB0"] == pytest.approx(exp_modelo["ranking"]["rankingB0"])
        assert res_modelo["ranking"]["rankingB1"] == pytest.approx(exp_modelo["ranking"]["rankingB1"])
        for tipo in ["dap", "ht", "volume"]:
            res_tipo = res_modelo[tipo]
            exp_tipo = exp_modelo[tipo]
            assert res_tipo["ranking"]["rankingB0"] == pytest.approx(exp_tipo["ranking"]["rankingB0"])
            assert res_tipo["ranking"]["rankingB1"] == pytest.approx(exp_tipo["ranking"]["rankingB1"])
            for chave, exp_val in exp_tipo.items():
                if chave == "ranking":
                    continue
                res_val = res_tipo[chave]
                assert res_val["ranking"]["b0"] == pytest.approx(exp_val["ranking"]["b0"])
                assert res_val["ranking"]["b1"] == pytest.approx(exp_val["ranking"]["b1"])
                pd.testing.assert_frame_equal(
                    pd.DataFrame(res_val["estatisticas"]["estatisticas"]),
                    pd.DataFrame(exp_val["estatisticas"]["estatisticas"]),
                    check_dtype=False,
                    atol=1e-9,
                )
