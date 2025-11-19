"""Avaliação de modelos de volume."""

from __future__ import annotations

from typing import Callable, Dict, List

import numpy as np
import pandas as pd

from fgmutils import classification, evaluation, prediction, project
from fgmutils.calculations import calcula_volume_default
from fgmutils import dataops


def avalia_volume_avancado(
    base: pd.DataFrame,
    mapeamento: Dict[str, str],
    modelos: List[Callable],
    dividir_em: str = "parcela",
    percentual_de_treino: float = 0.7,
    agrupar_por: str = "parcela",
    fn_calcula_volume: Callable | None = None,
    force_predict: bool = False,
    seed: int | None = None,
    split: Dict[str, List] | None = None,
) -> dict:
    col_order = []
    for coluna in [dividir_em, agrupar_por, *mapeamento.values()]:
        if coluna not in col_order:
            col_order.append(coluna)
    missing = set(col_order).difference(base.columns)
    if missing:
        raise KeyError(f"Campos ausentes na base: {', '.join(sorted(missing))}")
    base_df = base[col_order].copy().reset_index(drop=True)
    if fn_calcula_volume is None:
        fn_calcula_volume = calcula_volume_default

    base_treino, base_validacao = _obtem_bases(
        base_df, dividir_em, percentual_de_treino, seed, split
    )

    estatisticas = {}
    ranking_rows = []
    volumes_preditos = pd.DataFrame({agrupar_por: base_validacao[agrupar_por].values})

    for modelo in modelos:
        nome, _ = modelo()
        fit_dap = modelo(y1=mapeamento["dap1"], y2=mapeamento["dap2"], base=base_treino)
        fit_ht = modelo(y1=mapeamento["ht1"], y2=mapeamento["ht2"], base=base_treino)

        pred_dap = _predict_model(fit_dap, base_validacao, force_predict)
        pred_ht = _predict_model(fit_ht, base_validacao, force_predict)

        observado_volume = fn_calcula_volume(
            ht=base_validacao[mapeamento["ht2"]],
            dap=base_validacao[mapeamento["dap2"]],
        )
        estimado_volume = fn_calcula_volume(ht=pred_ht, dap=pred_dap)

        stats = evaluation.avalia_estimativas(
            observado_volume, estimado_volume, base_validacao.reset_index(drop=True)
        )
        tabela_stats = pd.DataFrame(stats["estatisticas"]["estatisticas"])
        base_cols = list(base_validacao.columns)
        ordered_cols = base_cols + [col for col in tabela_stats.columns if col not in base_cols]
        stats["estatisticas"]["estatisticas"] = tabela_stats[ordered_cols].to_dict(orient="list")
        estatisticas[nome] = stats
        ranking_rows.append(
            {
                "name": nome,
                "b0": stats["ranking"]["b0"],
                "b1": stats["ranking"]["b1"],
                "rankingB0": stats["ranking"]["rankingB0"],
                "rankingB1": stats["ranking"]["rankingB1"],
            }
        )
        volumes_preditos[nome] = estimado_volume

    ranking_df = pd.DataFrame(ranking_rows).sort_values(["rankingB0", "rankingB1"]).reset_index(drop=True)
    ranking_df["rank"] = np.arange(1, len(ranking_df) + 1)
    ranking = {
        "rank": ranking_df["rank"].tolist(),
        "b0": ranking_df["b0"].tolist(),
        "b1": ranking_df["b1"].tolist(),
    }

    agrupado = volumes_preditos.groupby(agrupar_por).sum(numeric_only=True).reset_index()
    base_out = base_df.copy()
    for coluna in agrupado.columns:
        if coluna == agrupar_por:
            continue
        mapa = dict(zip(agrupado[agrupar_por], agrupado[coluna]))
        base_out[coluna] = base_out[agrupar_por].map(mapa).fillna(-999.0)

    return {
        "estatisticas": estatisticas,
        "base": base_out.to_dict(orient="list"),
        "ranking": ranking,
    }

def avalia_volume_age_based(
    base: pd.DataFrame,
    first_age: float | None,
    last_age: float | None,
    modelos: List[Callable],
    mapper: Dict[str, str],
    group_by: str = "parcela",
    plot: str = "parcela",
    perc_training: float = 0.7,
    fn_calcula_volume: Callable | None = None,
    force_predict: bool = False,
    seed: int | None = None,
    age_round: float | None = None,
    age_in_years: bool = False,
    split: Dict[str, List] | None = None,
) -> dict:
    if fn_calcula_volume is None:
        fn_calcula_volume = calcula_volume_default

    required_cols = {group_by, plot, *mapper.values()}
    missing = required_cols.difference(base.columns)
    if missing:
        raise KeyError(f"Campos ausentes na base: {', '.join(sorted(missing))}")

    subset_cols = [col for col in base.columns if col in required_cols]
    base_df = base[subset_cols].copy().reset_index(drop=True)
    base_original = base.reset_index(drop=True)

    base_treino, base_validacao = _obtem_bases(
        base_df, mapper["age1"], perc_training, seed, split
    )

    base_validacao = base_validacao.copy()
    base_validacao["idadearred"] = classification.round_age(
        base_validacao[plot],
        base_validacao[mapper["age1"]],
        in_years=age_in_years,
        first_age=age_round,
    )
    mapper_proj = mapper.copy()
    mapper_proj["age1"] = "idadearred"

    ordered_cols = _ordered_mapper_columns(mapper, group_by)
    base_treino_export = base_treino[[col for col in ordered_cols if col in base_treino.columns]]
    base_validacao_export = base_validacao.copy()
    if "idadearred" in base_validacao_export.columns:
        base_validacao_export = base_validacao_export.drop(columns=["idadearred"])
    base_validacao_export = base_validacao_export[
        [col for col in ordered_cols if col in base_validacao_export.columns]
    ]

    resultado = {
        "base": base_original.to_dict(orient="list"),
        "baseTreino": base_treino_export.to_dict(orient="list"),
        "baseValidacao": base_validacao_export.to_dict(orient="list"),
    }
    ranking_rows = []

    for modelo in modelos:
        nome, _ = modelo()
        fit_dap = modelo(y1=mapper["dap1"], y2=mapper["dap2"], base=base_treino)
        fit_ht = modelo(y1=mapper["ht1"], y2=mapper["ht2"], base=base_treino)
        first = (
            float(first_age)
            if first_age is not None
            else float(np.nanmin(base_validacao[mapper_proj["age1"]]))
        )
        last = (
            float(last_age)
            if last_age is not None
            else float(np.nanmax(base_validacao[mapper_proj["age1"]]))
        )
        list_of_data = project.project_base_oriented(
            fit_dap=fit_dap,
            fit_ht=fit_ht,
            base=base_validacao,
            first_age=first,
            last_age=last,
            mapper=mapper_proj,
            calc_volume=fn_calcula_volume,
            force_predict=force_predict,
        )
        avaliacao = evaluation.eval_age_based(list_of_data, mapper=mapper)
        stats_cols = _ordered_mapper_columns(mapper, group_by) + ["idadearred"]
        _ordenar_estatisticas(avaliacao["dap"], stats_cols)
        _ordenar_estatisticas(avaliacao["ht"], stats_cols)
        _ordenar_estatisticas(avaliacao["volume"], stats_cols)
        resultado[nome] = avaliacao
        ranking_rows.append(
            {
                "model": nome,
                "rankingB0": avaliacao["ranking"]["rankingB0"],
                "rankingB1": avaliacao["ranking"]["rankingB1"],
            }
        )

    ranking_df = (
        pd.DataFrame(ranking_rows)
        .sort_values(["rankingB0", "rankingB1"])
        .reset_index(drop=True)
    )
    resultado["ranking"] = {
        "model": ranking_df["model"].tolist(),
        "rankingB0": ranking_df["rankingB0"].tolist(),
        "rankingB1": ranking_df["rankingB1"].tolist(),
    }
    return resultado


__all__ = ["avalia_volume_avancado", "avalia_volume_age_based"]


def _predict_model(model, data, force):
    if hasattr(model, "predict") and not force:
        try:
            return np.asarray(model.predict(data))
        except Exception:
            pass
    return prediction.predizer(model, data, force=force)


def _obtem_bases(
    base_df: pd.DataFrame,
    dividir_em: str,
    percentual_de_treino: float,
    seed: int | None,
    split: Dict[str, List] | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if split is not None:
        treino_ids = split.get("treino", [])
        validacao_ids = split.get("validacao", [])
        treino_mask = _match_values(base_df[dividir_em], treino_ids)
        validacao_mask = _match_values(base_df[dividir_em], validacao_ids)
        base_treino = base_df[treino_mask].reset_index(drop=True)
        base_validacao = base_df[validacao_mask].reset_index(drop=True)
        return base_treino, base_validacao

    separacao = dataops.separa_dados(
        base_df,
        dividir_em,
        perc_training=percentual_de_treino,
        seed=seed,
    )
    return separacao["treino"].reset_index(drop=True), separacao["validacao"].reset_index(
        drop=True
    )


def _match_values(series: pd.Series, valores: List) -> np.ndarray:
    if not valores:
        return np.zeros(len(series), dtype=bool)
    try:
        arr = series.astype(float).to_numpy()
        vals = np.asarray(valores, dtype=float)
        return np.any(np.isclose(arr[:, None], vals[None, :], atol=1e-8), axis=1)
    except (ValueError, TypeError):
        return series.isin(valores).to_numpy()


def _ordered_mapper_columns(mapper: Dict[str, str], group_by: str) -> list[str]:
    ordem_preferida = [
        group_by,
        mapper.get("dap1"),
        mapper.get("dap2"),
        mapper.get("age1"),
        mapper.get("age2"),
        mapper.get("dap2est"),
        mapper.get("ht1"),
        mapper.get("ht2"),
        mapper.get("ht2est"),
        mapper.get("volume1"),
        mapper.get("volume2"),
        mapper.get("volume2est"),
    ]
    vistos: list[str] = []
    for coluna in ordem_preferida:
        if coluna and coluna not in vistos:
            vistos.append(coluna)
    return vistos


def _ordenar_estatisticas(entrada: dict, colunas_ordem: list[str]) -> None:
    for chave, valor in entrada.items():
        if chave == "ranking":
            continue
        tabela = pd.DataFrame(valor["estatisticas"]["estatisticas"])
        ordem = ["observado", "estimado"] + [col for col in colunas_ordem if col in tabela.columns]
        valor["estatisticas"]["estatisticas"] = tabela[ordem].to_dict(orient="list")
