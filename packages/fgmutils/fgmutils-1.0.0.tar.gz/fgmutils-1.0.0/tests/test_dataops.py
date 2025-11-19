from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from fgmutils import dataops


DATA_DIR = Path(__file__).resolve().parent / "data"
INPUT_CSV = DATA_DIR / "non_longitudinal.csv"
EXPECTED_FULL = DATA_DIR / "pairs_full_expected.csv"
EXPECTED_SINGLE = DATA_DIR / "pairs_single_expected.csv"
SPLIT_BASE = DATA_DIR / "separa_dados_base.csv"
SPLIT_TREINO = DATA_DIR / "separa_dados_treino.csv"
SPLIT_VALIDACAO = DATA_DIR / "separa_dados_validacao.csv"
SPLIT_IND_TREINO = DATA_DIR / "separa_dados_individuos_treino.csv"
SPLIT_IND_VALIDACAO = DATA_DIR / "separa_dados_individuos_validacao.csv"
SPLIT_RESUMO = DATA_DIR / "separa_dados_resumo.csv"


def test_add_column_extends_dataframe():
    df = pd.DataFrame({"a": [1, 2]})
    result = dataops.add_column(df, [10, 20, 30], "b")
    assert list(result["b"]) == [10, 20, 30]
    assert len(result) == 3
    assert np.isnan(result.loc[2, "a"])  # nova linha preenchida com NA


def test_add_column_pads_values():
    df = pd.DataFrame({"a": [1, 2, 3, 4]})
    result = dataops.add_column(df, [9], "b")
    assert result.loc[0, "b"] == 9
    assert result["b"].isna().sum() == 3


def test_convert_column_to_str():
    df = pd.DataFrame({"data": [201401, 201402]})
    result = dataops.convert_column_to_str(df, "data")
    assert result["data"].tolist() == ["201401", "201402"]


def test_convert_column_missing():
    df = pd.DataFrame({"x": [1]})
    try:
        dataops.convert_column_to_str(df, "y")
    except KeyError as err:
        assert "y" in str(err)
    else:  # pragma: no cover
        raise AssertionError("Expected KeyError")


def test_separa_dados_split_reproducible():
    df = pd.DataFrame(
        {
            "parcela": list("AABBCC"),
            "valor": [1, 2, 3, 4, 5, 6],
        }
    )
    resultado = dataops.separa_dados(df, "parcela", perc_training=2 / 3, seed=10)
    repeticao = dataops.separa_dados(df, "parcela", perc_training=2 / 3, seed=10)
    assert resultado["individuos"]["treino"].equals(repeticao["individuos"]["treino"])
    assert resultado["treino"].equals(repeticao["treino"])
    assert resultado["nro_individuos"] == 3
    treino_ids = set(resultado["individuos"]["treino"]["parcela"])
    valid_ids = set(resultado["individuos"]["validacao"]["parcela"])
    assert treino_ids.isdisjoint(valid_ids)


def test_separa_dados_invalid_percentual():
    df = pd.DataFrame({"campo": [1, 2, 3]})
    with pytest.raises(ValueError):
        dataops.separa_dados(df, "campo", perc_training=0.0)


def test_atualiza_campo_base_aplica_sentinelas_e_atualiza():
    base_atualizar = pd.DataFrame(
        {
            "parcela": ["A", "A", "B"],
            "idade": ["1", "2", "1"],
            "volume": [0, 0, 0],
        }
    )
    base_agrupada = pd.DataFrame(
        {
            "parcela": ["A", "B"],
            "idade": [1, 1],
            "volume": [50, 30],
            "novo": ["x", "y"],
        }
    )
    resultado = dataops.atualiza_campo_base(
        ["volume", "novo"], base_agrupada, base_atualizar, ["parcela", "idade"]
    )
    linha_a1 = resultado[(resultado["parcela"] == "A") & (resultado["idade"] == "1")].iloc[0]
    assert linha_a1["volume"] == 50
    assert linha_a1["novo"] == "x"
    linha_sem_match = resultado[(resultado["parcela"] == "A") & (resultado["idade"] == "2")].iloc[0]
    assert linha_sem_match["volume"] == -999
    assert linha_sem_match["novo"] == "-999"


def test_cria_dados_pareados_valores():
    base = pd.DataFrame(
        {
            "COD_ID": ["x", "x", "x", "y", "y"],
            "ANO_MEDICAO": [2010, 2012, 2014, 2011, 2013],
            "DAP": [10, 12, 15, 11, 13],
            "HT": [5.0, 6.0, 7.0, 5.5, 6.5],
            "ID_PROJETO": ["p1", "p1", "p1", "p2", "p2"],
        }
    )
    resultado = dataops.cria_dados_pareados(
        base,
        campo_chave="COD_ID",
        campo_comparacao="ANO_MEDICAO",
        campos_pareados=["DAP", "HT"],
        campos_nao_pareados=["ID_PROJETO"],
    )
    assert list(resultado.columns) == [
        "cod_id",
        "ano_medicao1",
        "ano_medicao2",
        "dap1",
        "dap2",
        "ht1",
        "ht2",
        "id_projeto",
    ]
    assert len(resultado) == 3
    primeira = resultado.iloc[0]
    assert primeira["cod_id"] == "x"
    assert primeira["ano_medicao1"] == 2010
    assert primeira["ano_medicao2"] == 2012
    assert primeira["dap1"] == 10
    assert primeira["dap2"] == 12
    assert primeira["id_projeto"] == "p1"


def test_cria_dados_pareados_sem_pares():
    base = pd.DataFrame(
        {
            "COD_ID": ["z"],
            "ANO_MEDICAO": [2010],
            "DAP": [10],
        }
    )
    resultado = dataops.cria_dados_pareados(
        base,
        campo_chave="COD_ID",
        campo_comparacao="ANO_MEDICAO",
        campos_pareados=["DAP"],
        campos_nao_pareados=[],
    )
    assert resultado.empty


@pytest.mark.skipif(
    not SPLIT_BASE.exists(),
    reason="Referências do separaDados não foram geradas via R",
)
def test_separa_dados_reproduz_metricas_R():
    base = pd.read_csv(SPLIT_BASE)
    esperado_resumo = pd.read_csv(SPLIT_RESUMO)

    resultado = dataops.separa_dados(base, "parcela", perc_training=0.65, seed=42)

    assert resultado["nro_individuos"] == esperado_resumo["nro_individuos"].iloc[0]
    assert resultado["percentual"]["treino"] == pytest.approx(esperado_resumo["percentual_treino"].iloc[0], abs=0.01)
    assert resultado["percentual"]["validacao"] == pytest.approx(esperado_resumo["percentual_validacao"].iloc[0], abs=0.01)




@pytest.mark.skipif(
    not EXPECTED_FULL.exists(),
    reason="Resultados de referência em R não foram gerados (execute o script R)",
)
def test_cria_dados_pareados_bate_com_referencia_r():
    df = pd.read_csv(INPUT_CSV, sep=";")
    esperado = pd.read_csv(EXPECTED_FULL)
    resultado = dataops.cria_dados_pareados(
        df,
        campo_chave="Arv",
        campo_comparacao="Idade",
        campos_pareados=["Volume"],
        campos_nao_pareados=["Parcela", "cod_id"],
    )
    assert_frame_equal(
        resultado.reset_index(drop=True),
        esperado,
        check_dtype=False,
    )


@pytest.mark.skipif(
    not EXPECTED_SINGLE.exists(),
    reason="Resultados de referência em R não foram gerados (execute o script R)",
)
def test_cria_dados_pareados_sem_pares_referencia_r():
    df = pd.read_csv(INPUT_CSV, sep=";")
    apenas_primeira = df[df["Idade"] == 1]
    esperado = pd.read_csv(EXPECTED_SINGLE)
    resultado = dataops.cria_dados_pareados(
        apenas_primeira,
        campo_chave="Arv",
        campo_comparacao="Idade",
        campos_pareados=["Volume"],
        campos_nao_pareados=["Parcela", "cod_id"],
    )
    assert_frame_equal(
        resultado.reset_index(drop=True),
        esperado,
        check_dtype=False,
    )
