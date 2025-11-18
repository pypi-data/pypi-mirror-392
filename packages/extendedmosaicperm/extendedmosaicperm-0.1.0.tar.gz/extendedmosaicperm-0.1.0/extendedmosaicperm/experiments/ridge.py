from __future__ import annotations

from typing import Dict

import mosaicperm as mp
import numpy as np
from tqdm.auto import tqdm

from extendedmosaicperm.factor import ExtendMosaicFactorTest
from extendedmosaicperm.factor_data import FactorModelDataGenerator
from .base import BaseExperiment


class RidgeExperiment(BaseExperiment):
    """Compare OLS vs RidgeCV residual estimation across generators and sizes.

    The experiment runs a grid over:

    * generators: ``"random"``, ``"block"``, ``"common"``,
    * sizes: e.g. ``"small"``, ``"medium"``, ``"large"``,
    * residual symmetry: symmetric vs asymmetric,
    * residual estimators: OLS vs RidgeCV (with a grid of alphas).

    Args:
        n_sims: Number of Monte Carlo replications per configuration.
        nrand: Number of random draws for the test statistic per fit.
        seed: Base seed; ``seed + sim`` is used for the ``sim``-th replication.
        violation_strengths: List of correlation strength values to iterate over.
        sizes: Mapping from size key to a dict with keys ``"T"``, ``"p"``, ``"k"``.
        exposures_update_interval: If greater than zero, exposures are redrawn
            every given number of periods.

    Examples:
        >>> from extendedmosaicperm.experiments.ridge import RidgeExperiment
        >>> exp = RidgeExperiment(n_sims=1, nrand=3, seed=0, violation_strengths=[0.0])
        >>> exp.run()  # doctest: +ELLIPSIS
        >>> df = exp.summarize()
        >>> {"label", "method", "violation_strength"}.issubset(df.columns)
        True
    """

    def __init__(
        self,
        n_sims: int = 100,
        nrand: int = 100,
        seed: int = 42,
        violation_strengths: list[float] | None = None,
        sizes: Dict[str, Dict[str, int]] | None = None,
        exposures_update_interval: int = 10,
    ) -> None:
        super().__init__()
        self.n_sims = n_sims
        self.nrand = nrand
        self.seed = seed
        self.violation_strengths = violation_strengths or [0.0, 0.025, 0.05, 0.1, 0.15, 0.2]
        self.sizes = sizes or {
            "small": {"T": 250, "p": 50, "k": 5},
            "medium": {"T": 750, "p": 250, "k": 20},
            "large": {"T": 1500, "p": 500, "k": 40},
        }
        self.generators = {
            "random": lambda gen, v, sym: gen.generate_data_random_correlation(
                violation_strength=v,
                symmetric_residuals=sym,
                exposures_update_interval=exposures_update_interval,
            ),
            "block": lambda gen, v, sym: gen.generate_data_block_correlation(
                violation_strength=v,
                symmetric_residuals=sym,
                exposures_update_interval=exposures_update_interval,
            ),
            "common": lambda gen, v, sym: gen.generate_data_diagonal_plus_common_factor(
                violation_strength=v,
                symmetric_residuals=sym,
                exposures_update_interval=exposures_update_interval,
            ),
        }
        # key → grid of alphas; "ols" == no penalization
        self.ridge_settings: Dict[str, np.ndarray | None] = {
            "ols": None,
            "ridge": np.logspace(-3, 3, 10),
        }

    def extract_method(self, label: str) -> str:
        """Return the residual estimator identifier parsed from a label.

        Args:
            label: Label string of the form
                ``"<gen>_<size>_<sym|asym>_<ols|ridge>"``.

        Returns:
            str: ``"ridge"`` if the label ends with ``"_ridge"``, otherwise
            ``"ols"``.
        """
        return "ridge" if "ridge" in label else "ols"

    def run(self) -> None:
        """Execute the full simulation grid and store p-values.

        Populates ``self.results`` as a nested dictionary of the form::

            {
                label: {
                    violation_strength: np.ndarray of p-values
                }
            }

        where ``label`` encodes generator, size, symmetry, and residual method.
        """
        results: Dict[str, Dict[float, np.ndarray]] = {}

        label_list = [
            (g, s, sym, r)
            for g in self.generators
            for s in self.sizes
            for sym in [True, False]  # symmetric vs asymmetric
            for r in self.ridge_settings
        ]

        for gname, sname, sym, ridge_mode in tqdm(label_list, desc="Running RidgeExperiment"):
            label = f"{gname}_{sname}_{'sym' if sym else 'asym'}_{ridge_mode}"
            results[label] = {}

            gen_func = self.generators[gname]
            params = self.sizes[sname]
            ridge_alphas = self.ridge_settings[ridge_mode]

            for v in self.violation_strengths:
                pvals = []
                for sim in range(self.n_sims):
                    generator = FactorModelDataGenerator(
                        n_timepoints=params["T"],
                        n_assets=params["p"],
                        n_factors=params["k"],
                        seed=self.seed + sim,
                    )
                    Y, L, X, eps = gen_func(generator, v, sym)

                    mpt = ExtendMosaicFactorTest(
                        outcomes=Y,
                        exposures=L,
                        test_stat=mp.statistics.mean_maxcorr_stat,
                        ridge_alphas=ridge_alphas,
                    )
                    mpt.fit(nrand=self.nrand, verbose=False)
                    pvals.append(float(mpt.pval))

                results[label][v] = np.array(pvals)

        self.results = results
