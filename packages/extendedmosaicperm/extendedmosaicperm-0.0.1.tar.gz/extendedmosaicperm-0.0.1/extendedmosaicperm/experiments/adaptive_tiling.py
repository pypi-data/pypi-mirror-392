from __future__ import annotations

from typing import Dict

import mosaicperm as mp
import numpy as np
from tqdm.auto import tqdm

from extendedmosaicperm.factor import ExtendMosaicFactorTest
from extendedmosaicperm.factor_data import FactorModelDataGenerator
from .base import BaseExperiment


class AdaptiveTilingExperiment(BaseExperiment):
    """Compare default vs adaptive tiling across generators and sizes.

    For each generator/size combination, the experiment runs the test with:

    * default tiling (baseline from :mod:`mosaicperm`),
    * adaptive tiling (data-driven grouping, using the same test statistic).

    Args:
        n_sims: Number of Monte Carlo replications per configuration.
        nrand: Number of random draws for the test statistic per fit.
        seed: Base seed; ``seed + sim`` is used for the ``sim``-th replication.
        violation_strengths: List of correlation strength values to iterate over.
        sizes: Mapping from size key to a dict with keys ``"T"``, ``"p"``, ``"k"``.
        exposures_update_interval: If greater than zero, exposures are redrawn
            every given number of periods.

    Examples:
        >>> from extendedmosaicperm.experiments.adaptive_tiling import AdaptiveTilingExperiment
        >>> exp = AdaptiveTilingExperiment(n_sims=1, nrand=3, seed=0, violation_strengths=[0.0])
        >>> exp.run()  # doctest: +ELLIPSIS
        >>> df = exp.summarize()
        >>> {"label", "method", "violation_strength"}.issubset(df.columns)
        True
    """

    def __init__(
        self,
        n_sims: int = 50,
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
        self.violation_strengths = violation_strengths or [0.0, 0.025, 0.05]
        self.sizes = sizes or {
            "small": {"T": 250, "p": 50, "k": 5},
            "medium": {"T": 750, "p": 250, "k": 20},
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
        # method name → adaptive_tiling flag
        self.methods = {"default": False, "adaptive": True}

    def extract_method(self, label: str) -> str:
        """Return the tiling mode parsed from an experiment label.

        Args:
            label: Label string of the form
                ``"<gen>_<size>_<sym|asym>_<default|adaptive>"``.

        Returns:
            str: ``"adaptive"`` if the label ends with ``"_adaptive"``,
            otherwise ``"default"``.
        """
        return "adaptive" if "adaptive" in label else "default"

    def run(self) -> None:
        """Execute the full simulation grid and store p-values.

        Populates ``self.results`` as a nested dictionary of the form::

            {
                label: {
                    violation_strength: np.ndarray of p-values
                }
            }

        where ``label`` encodes generator, size, symmetry, and tiling mode.
        """
        results: Dict[str, Dict[float, np.ndarray]] = {}

        label_list = [
            (g, s, sym, m)
            for g in self.generators
            for s in self.sizes
            for sym in [True]  # only symmetric residuals here
            for m in self.methods
        ]

        for gname, sname, sym, method in tqdm(label_list, desc="Running AdaptiveTilingExperiment"):
            label = f"{gname}_{sname}_{'sym' if sym else 'asym'}_{method}"
            results[label] = {}

            gen_func = self.generators[gname]
            params = self.sizes[sname]
            use_adaptive = self.methods[method]

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
                        adaptive_tiling=use_adaptive,
                        sign_flipping=False,
                    )
                    mpt.fit(nrand=self.nrand, verbose=False)
                    pvals.append(float(mpt.pval))

                results[label][v] = np.array(pvals)

        self.results = results
