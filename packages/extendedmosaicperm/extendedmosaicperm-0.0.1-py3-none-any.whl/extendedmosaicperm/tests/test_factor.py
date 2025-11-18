import numpy as np
import mosaicperm as mp

from extendedmosaicperm.factor import ExtendMosaicFactorTest
from extendedmosaicperm.tilings import build_adaptive_tiling


def _toy_data(seed=0):
    rng = np.random.default_rng(seed)
    T, N, K = 20, 6, 2
    F = rng.standard_normal((T, K))
    B = rng.standard_normal((K, N))
    Y = F @ B + rng.standard_normal((T, N))
    exposures = B.T  # (N, K)
    tiles = build_adaptive_tiling(Y, exposures, batch_size=5, D=2, seed=seed)
    return Y, exposures, tiles


def test_signflip_vs_perm_different_null(seed=0):
    Y, exposures, tiles = _toy_data(seed)

    m_perm = ExtendMosaicFactorTest(
        outcomes=Y,
        exposures=exposures,
        tiles=tiles,
        test_stat=mp.statistics.mean_maxcorr_stat,
        sign_flipping=False,
        seed=seed,
    )
    m_perm.fit(nrand=20, verbose=False)

    m_sign = ExtendMosaicFactorTest(
        outcomes=Y,
        exposures=exposures,
        tiles=tiles,
        test_stat=mp.statistics.mean_maxcorr_stat,
        sign_flipping=True,
        seed=seed,
    )
    m_sign.fit(nrand=20, verbose=False)

    assert m_perm.null_statistics.shape == m_sign.null_statistics.shape
    assert not np.allclose(m_perm.null_statistics, m_sign.null_statistics)


def test_ridge_and_ols_residuals_shapes():
    Y, exposures, tiles = _toy_data(1)

    m_ols = ExtendMosaicFactorTest(
        outcomes=Y,
        exposures=exposures,
        tiles=tiles,
        test_stat=mp.statistics.mean_maxcorr_stat,
        ridge_alphas=None,
    )
    res_ols = m_ols.compute_mosaic_residuals()
    assert res_ols.shape == Y.shape

    alphas = np.logspace(-2, 2, 5)
    m_ridge = ExtendMosaicFactorTest(
        outcomes=Y,
        exposures=exposures,
        tiles=tiles,
        test_stat=mp.statistics.mean_maxcorr_stat,
        ridge_alphas=alphas,
    )
    res_ridge = m_ridge.compute_mosaic_residuals()
    assert res_ridge.shape == Y.shape
