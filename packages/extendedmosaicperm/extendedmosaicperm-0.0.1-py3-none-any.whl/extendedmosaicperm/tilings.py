from __future__ import annotations

from typing import List, Sequence, Optional

import numpy as np
from mosaicperm.tilings import Tiling, even_random_partition


def estimate_covariance(
    residuals: np.ndarray,
    prev_batches: Sequence[Sequence[int]],
    prev_groups: Sequence[Sequence[int]],
) -> np.ndarray:
    """Estimate residual covariance from previous tiles.

    For each previously observed (batch, group) pair, the function computes
    a local covariance matrix and aggregates these estimates into a global
    covariance estimate.

    Args:
        residuals: Residual matrix of shape ``(T, p)``.
        prev_batches: Sequence of time-index arrays used so far.
        prev_groups: Sequence of asset-index arrays corresponding to the
            groups used so far.

    Returns:
        np.ndarray: Estimated covariance matrix of shape ``(p, p)``.

    Notes:
        Entries not covered by any previous (batch, group) pair remain zero.
        Division by zero is avoided by replacing empty counts with one.
    """
    p = residuals.shape[1]
    cov = np.zeros((p, p))
    count = np.zeros((p, p))

    for B, G in zip(prev_batches, prev_groups):
        block = residuals[np.ix_(B, G)]
        if block.shape[0] < 2:
            continue
        block = block - block.mean(axis=0, keepdims=True)
        local_cov = block.T @ block / block.shape[0]
        for i in range(len(G)):
            for j in range(len(G)):
                cov[G[i], G[j]] += local_cov[i, j]
                count[G[i], G[j]] += 1.0

    count[count == 0] = 1.0
    return cov / count


def greedy_grouping(cov: np.ndarray, D: int, seed: int = 0) -> List[np.ndarray]:
    """Greedily group variables to weaken within-group correlations.

    The algorithm starts from ``D`` randomly selected variables and then
    iteratively assigns remaining variables to the group with which they have
    the weakest (maximum absolute) correlation.

    Args:
        cov: Covariance (or correlation) matrix of shape ``(p, p)``.
        D: Number of groups.
        seed: Random seed used to initialize the starting variables.

    Returns:
        list[np.ndarray]: List of ``D`` index arrays forming a partition of
        ``{0, ..., p-1}``.

    Examples:
        >>> import numpy as np
        >>> from extendedmosaicperm.tilings import greedy_grouping
        >>> cov = np.eye(6)
        >>> groups = greedy_grouping(cov, D=3, seed=42)
        >>> len(groups), sum(len(g) for g in groups)
        (3, 6)
        >>> all(len(set(g1).intersection(set(g2))) == 0
        ...     for i, g1 in enumerate(groups) for j, g2 in enumerate(groups) if i < j)
        True
        >>> set(np.concatenate(groups)) == set(range(6))
        True
    """
    rng = np.random.default_rng(seed)
    p = cov.shape[0]
    perm = rng.permutation(p)
    groups: List[list[int]] = [[] for _ in range(D)]

    # Initialize groups with distinct starting indices
    for d in range(D):
        groups[d].append(int(perm[d]))
    assigned = set(perm[:D])

    # Greedy assignment of remaining indices
    for j in perm[D:]:
        max_corrs = [max(abs(cov[j, g]) for g in group) if group else 0.0 for group in groups]
        d_star = int(np.argmin(max_corrs))
        groups[d_star].append(int(j))

    return [np.array(g, dtype=int) for g in groups]


def build_adaptive_tiling(
    outcomes: np.ndarray,
    exposures: np.ndarray,
    batch_size: int = 10,
    D: Optional[int] = None,
    seed: int = 0,
) -> Tiling:
    """Build an adaptive tiling of the sample based on residual covariance.

    The time dimension is split into batches of size ``batch_size``. For the
    first batch, groups are assigned using a random even partition. For
    subsequent batches, residuals from previous tiles are used to estimate
    a covariance matrix, and the grouping is updated via :func:`greedy_grouping`.

    Args:
        outcomes: Outcome matrix of shape ``(T, p)``.
        exposures: Factor loadings, either constant of shape ``(p, K)`` or
            time-varying of shape ``(T, p, K)``.
        batch_size: Number of observations per batch.
        D: Number of groups. If ``None``, defaults to
            ``max(2, p // (2 * K))``, where ``K`` is the number of factors.
        seed: Random seed used for initial grouping and subsequent updates.

    Returns:
        Tiling: A tiling object containing all (batch, group) pairs.

    Raises:
        ValueError: If ``outcomes`` or ``exposures`` is ``None``, or if the
            exposure slices cannot be reshaped to ``(p, K)``.

    Examples:
        >>> import numpy as np
        >>> from mosaicperm.tilings import Tiling
        >>> from extendedmosaicperm.tilings import build_adaptive_tiling
        >>> rng = np.random.default_rng(0)
        >>> T, p, K = 12, 6, 2
        >>> Y = rng.normal(size=(T, p))
        >>> L = rng.normal(size=(p, K))
        >>> til = build_adaptive_tiling(Y, L, batch_size=4, D=3, seed=7)
        >>> isinstance(til, Tiling)
        True
        >>> len(til)  # doctest: +ELLIPSIS
        9
    """
    if outcomes is None or exposures is None:
        raise ValueError("`outcomes` and `exposures` cannot be None.")

    T, p = outcomes.shape
    k = exposures.shape[-1]
    if D is None:
        D = max(2, p // (2 * k))

    # Time batches
    batches = [np.arange(i, min(i + batch_size, T)) for i in range(0, T, batch_size)]
    tiles: list[tuple[np.ndarray, np.ndarray]] = []
    prev_batches: list[np.ndarray] = []
    prev_groups: list[np.ndarray] = []

    residuals = np.zeros((T, p))

    for i, B in enumerate(batches):
        # Choose grouping for this batch
        if i == 0:
            groups = even_random_partition(p, D)
        else:
            cov = estimate_covariance(residuals, prev_batches, prev_groups)
            groups = greedy_grouping(cov, D, seed=seed + i)

        # Add tiles for all groups in this batch
        for G in groups:
            tiles.append((B, G))

        # Slice outcomes and exposures for this batch
        Y = outcomes[np.ix_(B, np.arange(p))]
        if exposures.ndim == 3:
            L = exposures[B]
        else:
            L = exposures

        # Compute residuals for each time index in the batch
        for t_idx, t in enumerate(B):
            L_t = L if exposures.ndim == 2 else L[t_idx]
            if L_t.shape == (k, p):
                L_t = L_t.T
            elif L_t.shape != (p, k):
                raise ValueError(f"Invalid exposure shape {L_t.shape}; expected (p, K) or (K, p).")

            A = np.linalg.pinv(L_t.T @ L_t) @ L_t.T
            beta = A @ Y[t_idx]
            residuals[t] = Y[t_idx] - L_t @ beta

        prev_batches.append(B)
        prev_groups.append(np.concatenate(groups))

    return Tiling(tiles, check_valid=True)
