import numpy as np
from mosaicperm.tilings import Tiling

from extendedmosaicperm.tilings import (
    estimate_covariance,
    greedy_grouping,
    build_adaptive_tiling,
)


def test_estimate_covariance_basic():
    R = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [-1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
        ]
    )
    prev_batches = [np.array([0, 1, 2, 3])]
    prev_groups = [np.array([0, 1])]
    C = estimate_covariance(R, prev_batches, prev_groups)

    assert C.shape == (3, 3)
    assert np.allclose(C[:2, :2], np.array([[0.5, 0.0], [0.0, 0.5]]))
    assert float(C[2, 2]) == 0.0
    assert np.allclose(C, C.T)


def test_greedy_grouping_partition():
    p = 10
    cov = np.eye(p)
    D = 3
    groups = greedy_grouping(cov, D=D, seed=0)

    assert len(groups) == D
    all_idx = np.concatenate(groups)
    assert set(all_idx) == set(range(p))
    for i, g1 in enumerate(groups):
        for j, g2 in enumerate(groups):
            if i < j:
                assert len(set(g1).intersection(set(g2))) == 0


def test_build_adaptive_tiling_shapes_and_type():
    rng = np.random.default_rng(0)
    T, p, k = 12, 6, 2
    Y = rng.normal(size=(T, p))
    L = rng.normal(size=(p, k))

    til = build_adaptive_tiling(Y, L, batch_size=4, D=3, seed=7)
    assert isinstance(til, Tiling)
    n_batches = int(np.ceil(T / 4))
    assert len(til) == n_batches * 3
