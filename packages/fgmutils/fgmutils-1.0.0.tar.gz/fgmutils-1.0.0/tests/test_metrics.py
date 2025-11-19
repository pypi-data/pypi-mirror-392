import math

import numpy as np
import pytest

from fgmutils import metrics


OBS = np.array([10.0, 12.5, 15.0, 17.5, 20.0])
EST = np.array([9.0, 11.0, 15.5, 18.0, 19.0])


def test_mae():
    assert metrics.mae(OBS, EST) == pytest.approx(np.mean(np.abs(OBS - EST)))


def test_rmse():
    assert metrics.rmse(OBS, EST) == pytest.approx(math.sqrt(np.mean((OBS - EST) ** 2)))


def test_bias():
    assert metrics.bias(OBS, EST) == pytest.approx(np.sum(EST - OBS) / OBS.size)


def test_mse():
    expected = np.sum((EST - OBS) ** 2) / (OBS.size - 2)
    assert metrics.mse(OBS, EST, k=2) == pytest.approx(expected)


def test_mspr():
    expected = np.sum((OBS - EST) ** 2) / 5
    assert metrics.mspr(OBS, EST, n_validation=5) == pytest.approx(expected)


def test_rrmse_corrected_formula():
    result = metrics.rrmse(OBS, EST)
    expected = math.sqrt(np.mean((OBS - EST) ** 2)) / np.mean(OBS)
    assert result == pytest.approx(expected)


def test_syx_and_percentage():
    base_syx = metrics.syx(OBS, EST, p=2)
    assert base_syx == pytest.approx(math.sqrt(np.sum((OBS - EST) ** 2) / (OBS.size - 2 - 1)))
    assert metrics.syx_perc(base_syx, OBS) == pytest.approx((base_syx / np.mean(OBS)) * 100)


def test_ce():
    numerator = np.sum(OBS - EST) ** 2
    denominator = np.sum(OBS - (np.mean(OBS) ** 2))
    assert metrics.ce(OBS, EST) == pytest.approx(1 - numerator / denominator)


def test_r21a_and_r29a():
    r21a = metrics.r21a(OBS, EST, k=2)
    assert isinstance(r21a, float)

    r29a = metrics.r29a(OBS, EST, k=2)
    assert isinstance(r29a, float)


def test_length_validation():
    with pytest.raises(ValueError):
        metrics.mae([1, 2], [1])


def test_rrmse_zero_mean():
    with pytest.raises(ZeroDivisionError):
        metrics.rrmse([0, 0], [0, 0])


def test_ce_zero_variance():
    with pytest.raises(ZeroDivisionError):
        metrics.ce([1, 1, 1], [1, 1, 1])
