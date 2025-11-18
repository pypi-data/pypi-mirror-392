from __future__ import annotations

from typing import Optional

import numpy as np
from sklearn.linear_model import RidgeCV
from mosaicperm import core, utilities
from mosaicperm.factor import MosaicFactorTest

from .tilings import build_adaptive_tiling


class ExtendMosaicFactorTest(MosaicFactorTest):
    """Extended mosaic factor test.

    Extends :class:`mosaicperm.factor.MosaicFactorTest` by adding:

    * sign-flip inference instead of standard permutation,
    * RidgeCV-based residual estimation,
    * adaptive tiling of data based on the correlation structure.

    Args:
        *args: Positional arguments forwarded to the base
            :class:`mosaicperm.factor.MosaicFactorTest` constructor.
        sign_flipping: Whether to use sign-flip inference instead of permutations.
        seed: Seed for the internal random number generator used for sign flips.
        ridge_alphas: Sequence of alpha values for :class:`sklearn.linear_model.RidgeCV`.
            If ``None``, ordinary least squares (OLS) is used to estimate residuals.
        adaptive_tiling: If ``True``, tiles are built automatically from
            ``outcomes`` and ``exposures`` using
            :func:`extendedmosaicperm.tilings.build_adaptive_tiling`.
        **kwargs: Keyword arguments forwarded to the base
            :class:`mosaicperm.factor.MosaicFactorTest` constructor.

    Attributes:
        sign_flipping: Boolean flag indicating whether sign-flip inference is used.
        rng: NumPy random number generator used for sign flips.
        ridge_alphas: Grid of RidgeCV penalization strengths, or ``None`` for OLS.

    Examples:
        Basic workflow with fixed exposures (2D exposures) and OLS residuals:

        >>> import numpy as np
        >>> from mosaicperm import statistics
        >>> from extendedmosaicperm.factor import ExtendMosaicFactorTest
        >>> from extendedmosaicperm.tilings import build_adaptive_tiling
        >>>
        >>> T, N, K = 60, 12, 3
        >>> rng = np.random.default_rng(0)
        >>> F = rng.standard_normal((T, K))
        >>> B = rng.standard_normal((K, N))
        >>> Y = F @ B + rng.standard_normal((T, N))
        >>>
        >>> tiles = build_adaptive_tiling(Y, B.T)  # exposures as (N x K)
        >>> mpt = ExtendMosaicFactorTest(
        ...     outcomes=Y,
        ...     exposures=B.T,
        ...     tiles=tiles,
        ...     test_stat=statistics.mean_maxcorr_stat,
        ...     sign_flipping=True,     # enable sign-flip inference
        ...     ridge_alphas=None,      # OLS for residuals
        ...     seed=0,
        ... )
        >>> _ = mpt.compute_mosaic_residuals()  # doctest: +ELLIPSIS
        >>> p = mpt._compute_p_value(nrand=20, verbose=False)
        >>> 0.0 <= p <= 1.0
        True

        Ridge-regularized residuals:

        >>> import numpy as np
        >>> from mosaicperm import statistics
        >>> from extendedmosaicperm.factor import ExtendMosaicFactorTest
        >>> from extendedmosaicperm.tilings import build_adaptive_tiling
        >>>
        >>> T, N, K = 60, 12, 3
        >>> rng = np.random.default_rng(1)
        >>> F = rng.standard_normal((T, K))
        >>> B = rng.standard_normal((K, N))
        >>> Y = F @ B + rng.standard_normal((T, N))
        >>>
        >>> tiles = build_adaptive_tiling(Y, B.T)
        >>> alphas = np.logspace(-3, 3, 5)
        >>> mpt_ridge = ExtendMosaicFactorTest(
        ...     outcomes=Y,
        ...     exposures=B.T,
        ...     tiles=tiles,
        ...     test_stat=statistics.mean_maxcorr_stat,
        ...     ridge_alphas=alphas,    # use RidgeCV
        ...     sign_flipping=False,    # standard permutation
        ...     seed=1,
        ... )
        >>> _ = mpt_ridge.compute_mosaic_residuals()  # doctest: +ELLIPSIS
        >>> p_ridge = mpt_ridge._compute_p_value(nrand=20, verbose=False)
        >>> 0.0 <= p_ridge <= 1.0
        True

        Adaptive tiling (no need to pass ``tiles`` explicitly):

        >>> import numpy as np
        >>> from mosaicperm import statistics
        >>> from extendedmosaicperm.factor import ExtendMosaicFactorTest
        >>>
        >>> T, N, K = 60, 12, 3
        >>> rng = np.random.default_rng(2)
        >>> F = rng.standard_normal((T, K))
        >>> B = rng.standard_normal((K, N))
        >>> Y = F @ B + rng.standard_normal((T, N))
        >>>
        >>> mpt_adapt = ExtendMosaicFactorTest(
        ...     outcomes=Y,
        ...     exposures=B.T,
        ...     adaptive_tiling=True,
        ...     test_stat=statistics.mean_maxcorr_stat,
        ...     sign_flipping=True,
        ...     seed=2,
        ... )
        >>> _ = mpt_adapt.compute_mosaic_residuals()  # doctest: +ELLIPSIS
        >>> p_adapt = mpt_adapt._compute_p_value(nrand=20, verbose=False)
        >>> 0.0 <= p_adapt <= 1.0
        True
    """

    def __init__(
        self,
        *args,
        sign_flipping: bool = False,
        seed: int = 123,
        ridge_alphas: Optional[np.ndarray] = None,
        adaptive_tiling: bool = False,
        **kwargs,
    ) -> None:
        if adaptive_tiling and ("tiles" not in kwargs):
            outcomes = kwargs.get("outcomes", None)
            if outcomes is None and len(args) >= 1:
                outcomes = args[0]

            exposures = kwargs.get("exposures", None)
            if exposures is None and len(args) >= 2:
                exposures = args[1]

            tiles = build_adaptive_tiling(outcomes, exposures)
            kwargs["tiles"] = tiles

        super().__init__(*args, **kwargs)
        self.sign_flipping = bool(sign_flipping)
        self.rng = np.random.default_rng(seed)
        self.ridge_alphas = ridge_alphas

    def compute_mosaic_residuals(self) -> np.ndarray:
        """Compute mosaic residuals for all tiles.

        For each (batch, group) tile, factor loadings are estimated and residuals
        are computed. If ``ridge_alphas`` is ``None``, residuals are obtained via OLS;
        otherwise, a separate :class:`RidgeCV` is fit for each observation in the tile.

        Returns:
            np.ndarray: Residual matrix with the same shape as ``self.outcomes``.
        """
        self.residuals = np.zeros_like(self.outcomes)

        for batch, group in self.tiles:
            if self.exposures.ndim == 2:
                Ltile = self.exposures[group]
            else:
                exposures_constant = all(
                    np.all(self.exposures[j, group] == self.exposures[batch[0], group])
                    for j in batch
                )
                if exposures_constant:
                    Ltile = self.exposures[batch[0], group]
                else:
                    Ltile = np.unique(
                        np.concatenate([self.exposures[j, group] for j in batch], axis=1),
                        axis=1,
                    )

            Ytile = self.outcomes[np.ix_(batch, group)]

            if self.ridge_alphas is None:
                A = np.linalg.pinv(Ltile.T @ Ltile) @ Ltile.T
                hatbeta = A @ Ytile.T
                self.residuals[np.ix_(batch, group)] = Ytile - (Ltile @ hatbeta).T
            else:
                residuals_tile = np.zeros_like(Ytile)
                for i, _t in enumerate(batch):
                    y = Ytile[i, :]
                    ridge = RidgeCV(alphas=self.ridge_alphas)
                    ridge.fit(Ltile, y)
                    residuals_tile[i, :] = y - ridge.predict(Ltile)
                self.residuals[np.ix_(batch, group)] = residuals_tile

        if not self.impute_zero:
            self.residuals[self.missing_pattern] = np.nan

        self._rtilde = self.residuals.copy()
        return self.residuals

    def flip_sign_residuals(self) -> None:
        """Apply random sign flips within each tile.

        For each tile (batch × group), an i.i.d. Rademacher vector of length
        ``len(batch)`` is drawn and applied across all assets in the tile.
        """
        self._rtilde = self.residuals.copy()
        for batch, group in self.tiles:
            flip_mask = self.rng.choice([-1, 1], size=(len(batch), 1))
            self._rtilde[np.ix_(batch, group)] *= flip_mask


    def _compute_p_value(self, nrand: int, verbose: bool) -> float:
        """Compute permutation or sign-flip p-value.

        The test statistic is recomputed under either random permutations of
        residuals (classical mosaic test) or random sign flips (Rademacher
        wild bootstrap), depending on the ``sign_flipping`` flag.

        Args:
            nrand: Number of random draws (permutations or sign-flips).
            verbose: Whether to display progress via :func:`mosaicperm.utilities.vrange`.

        Returns:
            float: p-value from the adaptive test statistic.
        """
        self.statistic = self.test_stat(self.residuals, **self.tstat_kwargs)
        d = len(self.statistic) if utilities.haslength(self.statistic) else 1

        self.null_statistics = np.zeros((nrand, d))
        for r in utilities.vrange(nrand, verbose=verbose):
            if self.sign_flipping:
                self.flip_sign_residuals()
            else:
                self.permute_residuals()
            self.null_statistics[r] = self.test_stat(self._rtilde, **self.tstat_kwargs)

        self.pval, self.adapt_stat, self.null_adapt_stats = core.compute_adaptive_pval(
            self.statistic,
            self.null_statistics,
        )

        stat = self.adapt_stat if d > 1 else self.statistic
        nstats = self.null_adapt_stats if d > 1 else self.null_statistics
        combined = np.concatenate([[stat], nstats.flatten()])
        self.apprx_zstat = (stat - combined.mean()) / combined.std() if combined.std() > 0 else 0.0

        return float(self.pval)
