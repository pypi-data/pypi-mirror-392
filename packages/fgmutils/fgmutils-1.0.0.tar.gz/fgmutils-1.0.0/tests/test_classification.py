from pathlib import Path

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from fgmutils import classification

DATA_DIR = Path(__file__).resolve().parent / "data"
INVENTORY = pd.read_csv(DATA_DIR / "forest_inventory.csv", sep=";")


def test_round_age_matches_r():
    esperado = pd.read_csv(DATA_DIR / "round_age_expected.csv")
    resultado = classification.round_age(INVENTORY["parcela"], INVENTORY["idade"])
    assert np.allclose(resultado, esperado["arredondado"].to_numpy())


def test_define_classes_matches_r():
    esperado = pd.read_csv(DATA_DIR / "define_classes_expected.csv")
    resultado = classification.define_classes(5, 25, 5, get_dataframe=True)
    assert_frame_equal(resultado.reset_index(drop=True), esperado, check_dtype=False)


def test_define_classes2_matches_r():
    esperado = pd.read_csv(DATA_DIR / "define_classes2_expected.csv")
    resultado = classification.define_classes2(INVENTORY["dap"], amplitude=2)
    obtido = pd.DataFrame(
        {
            "centro": resultado["centro"],
            "classe_min": resultado["classe"][:, 0],
            "classe_max": resultado["classe"][:, 1],
        }
    )
    assert_frame_equal(obtido.reset_index(drop=True), esperado, check_dtype=False)


def test_get_classes_matches_r():
    base = (
        INVENTORY.groupby(["idadearred", "parcela"], as_index=False)
        .agg(N=("dap", "size"), limiteMin=("dap", "min"), limiteMax=("dap", "max"), VolumeTotal=("volume", "sum"))
        .sort_values(["parcela", "idadearred"], kind="mergesort")
        .reset_index(drop=True)
    )
    esperado = pd.read_csv(DATA_DIR / "get_classes_expected.csv")
    lista = classification.get_classes(base, amplitude=2)
    combinado = []
    for idx, classe in enumerate(lista, start=1):
        if classe.empty:
            continue
        df = classe.copy()
        df["index"] = idx
        df["idadearred"] = base.loc[idx - 1, "idadearred"]
        df["parcela"] = base.loc[idx - 1, "parcela"]
        combinado.append(df)
    obtido = pd.concat(combinado, ignore_index=True)
    assert_frame_equal(obtido, esperado, check_dtype=False)


def test_classifica_classe_dap_matches_r():
    esperado = pd.read_csv(DATA_DIR / "classifica_classe_dap_expected.csv")
    base = (
        INVENTORY.groupby(["idadearred", "parcela"], as_index=False)
        .agg(limiteMin=("dap", "min"), limiteMax=("dap", "max"))
        .sort_values(["parcela", "idadearred"], kind="mergesort")
        .reset_index(drop=True)
    )
    classes = classification.get_classes(base.assign(N=0, VolumeTotal=0), amplitude=2)
    chaves = list(zip(base["idadearred"], base["parcela"]))
    mapa = {chave: idx for idx, chave in enumerate(chaves)}
    resultados = []
    for _, row in esperado.iterrows():
        idx = mapa[(row["idadearred"], row["parcela"])]
        classe = classification.classifica_classe_dap(classes[idx], row["dap"])
        resultados.append(classe)
    assert np.allclose(resultados, esperado["classe"].to_numpy())


def test_classificar_dap_matches_r():
    esperado = pd.read_csv(DATA_DIR / "classificar_dap_expected.csv")
    resultado = classification.classificar_dap(INVENTORY, amplitude=2)
    cols = esperado.columns.tolist()
    resultado = resultado[cols]
    assert_frame_equal(resultado.reset_index(drop=True), esperado, check_dtype=False)
