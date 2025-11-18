import numpy as np

from extendedmosaicperm.factor_data import FactorModelDataGenerator


def _check_shapes(Y, L_time, X, eps, T, p, k):
    assert Y.shape == (T, p)
    assert eps.shape == (T, p)
    assert L_time.shape == (T, p, k)
    assert X.shape == (T, k)


def test_random_correlation_shapes_and_seed():
    T, p, k = 30, 8, 3
    gen1 = FactorModelDataGenerator(T, p, k, seed=0)
    gen2 = FactorModelDataGenerator(T, p, k, seed=0)

    out1 = gen1.generate_data_random_correlation(violation_strength=0.1)
    out2 = gen2.generate_data_random_correlation(violation_strength=0.1)

    _check_shapes(*out1, T, p, k)
    for a, b in zip(out1, out2):
        assert np.allclose(a, b)


def test_block_and_common_shapes():
    T, p, k = 24, 10, 3
    gen = FactorModelDataGenerator(T, p, k, seed=1)

    Yb, Lb, Xb, epsb = gen.generate_data_block_correlation(violation_strength=0.2)
    _check_shapes(Yb, Lb, Xb, epsb, T, p, k)

    Yc, Lc, Xc, epsc = gen.generate_data_diagonal_plus_common_factor(violation_strength=0.2)
    _check_shapes(Yc, Lc, Xc, epsc, T, p, k)
