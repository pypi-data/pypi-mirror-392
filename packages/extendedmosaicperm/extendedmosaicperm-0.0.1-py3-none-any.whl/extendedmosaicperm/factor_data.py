import numpy as np


class FactorModelDataGenerator:
    """Generator of synthetic data for factor-model simulations.

    Supports multiple residual correlation structures, time-varying exposures,
    and configurable distributional asymmetry.

    Args:
        n_timepoints: Number of time periods ``T``.
        n_assets: Number of assets ``N``.
        n_factors: Number of factors ``K``.
        seed: Random seed for reproducibility.

    Examples:
        Basic usage with constant exposures and symmetric residuals:

        >>> from extendedmosaicperm.factor_data import FactorModelDataGenerator
        >>> gen = FactorModelDataGenerator(n_timepoints=20, n_assets=6, n_factors=2, seed=0)
        >>> Y, L_time, X, eps = gen.generate_data_random_correlation(
        ...     violation_strength=0.1,
        ...     exposures_update_interval=None,
        ...     symmetric_residuals=True,
        ... )
        >>> Y.shape, L_time.shape, X.shape, eps.shape
        ((20, 6), (20, 6, 2), (20, 2), (20, 6))

        Time-varying exposures, redrawn every 5 periods:

        >>> gen = FactorModelDataGenerator(n_timepoints=15, n_assets=5, n_factors=3, seed=1)
        >>> Y, L_time, X, eps = gen.generate_data_block_correlation(
        ...     violation_strength=0.2,
        ...     block_ratio=0.4,
        ...     exposures_update_interval=5,
        ...     symmetric_residuals=True,
        ... )
        >>> L_time[0].shape
        (5, 3)

        Asymmetric residuals (gamma-based, standardized):

        >>> gen = FactorModelDataGenerator(n_timepoints=12, n_assets=7, n_factors=2, seed=2)
        >>> Y, L_time, X, eps = gen.generate_data_diagonal_plus_common_factor(
        ...     violation_strength=0.3,
        ...     exposures_update_interval=None,
        ...     symmetric_residuals=False,
        ...     gamma_shape=2.0,
        ...     gamma_scale=1.0,
        ... )
        >>> eps.shape == Y.shape == (12, 7)
        True
    """

    def __init__(
        self,
        n_timepoints: int = 60,
        n_assets: int = 10,
        n_factors: int = 3,
        seed: int = 123,
    ) -> None:
        self.n_timepoints = n_timepoints
        self.n_assets = n_assets
        self.n_factors = n_factors
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def _build_time_varying_exposures(
        self,
        exposures_update_interval: int | None = None,
    ) -> np.ndarray:
        """Construct time-varying or constant factor exposures.

        Args:
            exposures_update_interval: Number of timepoints after which exposures
                are redrawn. If ``None``, exposures are constant over time.

        Returns:
            np.ndarray: Array of shape ``(T, N, K)`` with factor exposures.

        Examples:
            Constant exposures:

            >>> from extendedmosaicperm.factor_data import FactorModelDataGenerator
            >>> gen = FactorModelDataGenerator(n_timepoints=5, n_assets=4, n_factors=2, seed=0)
            >>> L = gen._build_time_varying_exposures(None)
            >>> L.shape
            (5, 4, 2)

            Time-varying exposures updated every 2 periods:

            >>> L = gen._build_time_varying_exposures(2)
            >>> L.shape
            (5, 4, 2)
        """
        if exposures_update_interval is None:
            L_const = self.rng.normal(0, 1, size=(self.n_assets, self.n_factors))
            return np.repeat(L_const[np.newaxis, :, :], self.n_timepoints, axis=0)

        L_time = np.zeros((self.n_timepoints, self.n_assets, self.n_factors))
        start = 0
        while start < self.n_timepoints:
            end = min(start + exposures_update_interval, self.n_timepoints)
            block_L = self.rng.normal(0, 1, size=(self.n_assets, self.n_factors))
            L_time[start:end] = block_L
            start = end
        return L_time

    def _sample_base_noise(
        self,
        symmetric: bool,
        gamma_shape: float,
        gamma_scale: float,
    ) -> np.ndarray:
        """Sample base noise vector with optional asymmetry.

        Args:
            symmetric: If ``True``, draw standard Gaussian noise.
                If ``False``, draw Gamma noise and standardize it to zero mean
                and unit variance.
            gamma_shape: Shape parameter for Gamma noise (used when
                ``symmetric=False``).
            gamma_scale: Scale parameter for Gamma noise (used when
                ``symmetric=False``).

        Returns:
            np.ndarray: Residual vector for one timepoint, shape ``(N,)``.

        Examples:
            Symmetric Gaussian:

            >>> from extendedmosaicperm.factor_data import FactorModelDataGenerator
            >>> gen = FactorModelDataGenerator(n_assets=5, seed=0)
            >>> z = gen._sample_base_noise(True, 2.0, 1.0)
            >>> z.shape
            (5,)

            Asymmetric gamma-based (standardized):

            >>> z = gen._sample_base_noise(False, 2.0, 1.0)
            >>> z.shape
            (5,)
            >>> abs(float(np.mean(z))) < 1e-6
            True
        """
        if symmetric:
            return self.rng.normal(size=self.n_assets)
        z = self.rng.gamma(gamma_shape, gamma_scale, size=self.n_assets)
        return (z - np.mean(z)) / np.std(z)

    def generate_data_random_correlation(
        self,
        violation_strength: float = 0.0,
        exposures_update_interval: int | None = None,
        symmetric_residuals: bool = True,
        gamma_shape: float = 2.0,
        gamma_scale: float = 1.0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Generate data with a random residual correlation structure.

        Residuals are generated from a random positive-definite correlation
        matrix, with the degree of cross-sectional dependence controlled by
        ``violation_strength``.

        Args:
            violation_strength: Strength of cross-sectional residual
                correlation in ``[0, 1]``. ``0`` corresponds to independence,
                ``1`` to the raw random correlation structure.
            exposures_update_interval: Interval (in timepoints) for refreshing
                exposures; ``None`` means constant exposures.
            symmetric_residuals: Whether residuals are symmetric (Gaussian) or
                asymmetric (gamma-based).
            gamma_shape: Shape parameter for asymmetric (Gamma) noise.
            gamma_scale: Scale parameter for asymmetric (Gamma) noise.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
                A tuple ``(Y, L_time, X, eps)`` where:

                * ``Y`` – simulated outcomes, shape ``(T, N)``,
                * ``L_time`` – exposures, shape ``(T, N, K)``,
                * ``X`` – latent factors, shape ``(T, K)``,
                * ``eps`` – residuals, shape ``(T, N)``.

        Examples:
            >>> from extendedmosaicperm.factor_data import FactorModelDataGenerator
            >>> gen = FactorModelDataGenerator(n_timepoints=30, n_assets=8, n_factors=3, seed=0)
            >>> Y, L_time, X, eps = gen.generate_data_random_correlation(violation_strength=0.2)
            >>> Y.shape, L_time.shape, X.shape, eps.shape
            ((30, 8), (30, 8, 3), (30, 3), (30, 8))
        """
        L_time = self._build_time_varying_exposures(exposures_update_interval)
        X = self.rng.normal(0, 1, size=(self.n_timepoints, self.n_factors))

        # Random covariance → correlation matrix
        A = self.rng.normal(0, 1, size=(self.n_assets, self.n_assets))
        Sigma_raw = A @ A.T
        d = np.sqrt(np.diag(Sigma_raw))
        Corr_raw = (Sigma_raw / d).T / d
        np.fill_diagonal(Corr_raw, 1.0)

        Corr_m = violation_strength * Corr_raw + (1 - violation_strength) * np.eye(self.n_assets)
        Corr_m += 1e-8 * np.eye(self.n_assets)

        chol = np.linalg.cholesky(Corr_m)
        eps = np.zeros((self.n_timepoints, self.n_assets))
        for t in range(self.n_timepoints):
            z = self._sample_base_noise(symmetric_residuals, gamma_shape, gamma_scale)
            eps[t, :] = chol @ z

        Y = np.zeros((self.n_timepoints, self.n_assets))
        for t in range(self.n_timepoints):
            Y[t, :] = L_time[t, :, :] @ X[t, :] + eps[t, :]

        return Y, L_time, X, eps

    def generate_data_block_correlation(
        self,
        violation_strength: float = 0.0,
        block_ratio: float = 0.5,
        exposures_update_interval: int | None = None,
        symmetric_residuals: bool = True,
        gamma_shape: float = 2.0,
        gamma_scale: float = 1.0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Generate data with block-correlated residuals.

        A subset of assets (a "block") exhibits stronger cross-sectional
        correlation than the rest. The size of the block and correlation
        strength are controlled by ``block_ratio`` and ``violation_strength``.

        Args:
            violation_strength: Within-block correlation strength in ``[0, 1]``.
            block_ratio: Fraction of assets forming the strongly correlated block
                in ``(0, 1]``.
            exposures_update_interval: Interval (in timepoints) for refreshing
                exposures; ``None`` means constant exposures.
            symmetric_residuals: Whether residuals are symmetric (Gaussian) or
                asymmetric (gamma-based).
            gamma_shape: Shape parameter for asymmetric (Gamma) noise.
            gamma_scale: Scale parameter for asymmetric (Gamma) noise.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
                A tuple ``(Y, L_time, X, eps)`` where:

                * ``Y`` – simulated outcomes, shape ``(T, N)``,
                * ``L_time`` – exposures, shape ``(T, N, K)``,
                * ``X`` – latent factors, shape ``(T, K)``,
                * ``eps`` – residuals, shape ``(T, N)``.

        Examples:
            >>> from extendedmosaicperm.factor_data import FactorModelDataGenerator
            >>> gen = FactorModelDataGenerator(n_timepoints=24, n_assets=10, n_factors=3, seed=0)
            >>> Y, L_time, X, eps = gen.generate_data_block_correlation(
            ...     violation_strength=0.3, block_ratio=0.5, exposures_update_interval=6
            ... )
            >>> Y.shape[1], L_time.shape[2], X.shape[1]
            (10, 3, 3)
        """
        L_time = self._build_time_varying_exposures(exposures_update_interval)
        X = self.rng.normal(0, 1, size=(self.n_timepoints, self.n_factors))

        p = self.n_assets
        block_size = int(np.ceil(p * block_ratio))
        Sigma = np.eye(p)
        block_val = 0.95 * violation_strength
        other_val = 0.05 * violation_strength

        for i in range(p):
            for j in range(p):
                if i != j:
                    if i < block_size and j < block_size:
                        Sigma[i, j] = block_val
                    else:
                        Sigma[i, j] = other_val

        Sigma += 1e-8 * np.eye(p)
        chol = np.linalg.cholesky(Sigma)

        eps = np.zeros((self.n_timepoints, p))
        for t in range(self.n_timepoints):
            z = self._sample_base_noise(symmetric_residuals, gamma_shape, gamma_scale)
            eps[t, :] = chol @ z

        Y = np.zeros((self.n_timepoints, p))
        for t in range(self.n_timepoints):
            Y[t, :] = L_time[t, :, :] @ X[t, :] + eps[t, :]

        return Y, L_time, X, eps

    def generate_data_diagonal_plus_common_factor(
        self,
        violation_strength: float = 0.0,
        exposures_update_interval: int | None = None,
        symmetric_residuals: bool = True,
        gamma_shape: float = 2.0,
        gamma_scale: float = 1.0,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Generate data with diagonal residual covariance plus a common factor.

        Residuals are decomposed into a diagonal idiosyncratic component and
        a single common factor component with strength controlled by
        ``violation_strength``.

        Args:
            violation_strength: Strength of the common residual factor in
                ``[0, 1]``.
            exposures_update_interval: Interval (in timepoints) for refreshing
                exposures; ``None`` means constant exposures.
            symmetric_residuals: Whether residuals are symmetric (Gaussian) or
                asymmetric (gamma-based).
            gamma_shape: Shape parameter for asymmetric (Gamma) noise.
            gamma_scale: Scale parameter for asymmetric (Gamma) noise.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
                A tuple ``(Y, L_time, X, eps)`` where:

                * ``Y`` – simulated outcomes, shape ``(T, N)``,
                * ``L_time`` – exposures, shape ``(T, N, K)``,
                * ``X`` – latent factors, shape ``(T, K)``,
                * ``eps`` – residuals, shape ``(T, N)``.

        Examples:
            >>> from extendedmosaicperm.factor_data import FactorModelDataGenerator
            >>> gen = FactorModelDataGenerator(n_timepoints=25, n_assets=9, n_factors=2, seed=0)
            >>> Y, L_time, X, eps = gen.generate_data_diagonal_plus_common_factor(
            ...     violation_strength=0.2
            ... )
            >>> X.shape
            (25, 2)
        """
        L_time = self._build_time_varying_exposures(exposures_update_interval)
        X = self.rng.normal(0, 1, size=(self.n_timepoints, self.n_factors))

        # Heterogeneous diagonal variances
        variances = 0.1 + 0.3 * self.rng.random(self.n_assets)
        chol_diag = np.linalg.cholesky(np.diag(variances))

        alpha = violation_strength
        loadings = self.rng.normal(0, 1, size=self.n_assets)

        eps = np.zeros((self.n_timepoints, self.n_assets))
        for t in range(self.n_timepoints):
            z = self._sample_base_noise(symmetric_residuals, gamma_shape, gamma_scale)
            diag_part = chol_diag @ z
            common_part = alpha * self.rng.normal() * loadings
            eps[t, :] = diag_part + common_part

        Y = np.zeros((self.n_timepoints, self.n_assets))
        for t in range(self.n_timepoints):
            Y[t, :] = L_time[t, :, :] @ X[t, :] + eps[t, :]

        return Y, L_time, X, eps
