from __future__ import annotations

import time
from typing import Dict

import mosaicperm as mp
import numpy as np
import pandas as pd
from tqdm.auto import tqdm

from extendedmosaicperm.factor import ExtendMosaicFactorTest
from extendedmosaicperm.factor_data import FactorModelDataGenerator
from .base import BaseExperiment


class SignFlipExperiment(BaseExperiment):
    """Compare permutation-based vs sign-flip inference across generators and sizes.

    The experiment runs a grid over:

    * data generators: ``"random"``, ``"block"``, ``"common"``,
    * size settings: e.g. ``"small"``, ``"medium"``, ``"large"``,
    * residual symmetry: symmetric vs asymmetric,
    * methods: permutation (``"perm"``) vs sign-flip (``"sign"``).

    Args:
        n_sims: Number of Monte Carlo replications per configuration.
        nrand: Number of random draws (permutations or sign-flips) per fit.
        seed: Base seed; ``seed + sim`` is used for the ``sim``-th replication.
        violation_strengths: List of residual correlation strengths to iterate over.
        sizes: Mapping from size key to a dict with keys ``"T"``, ``"p"``, ``"k"``.
            For example: ``{"small": {"T": 250, "p": 50, "k": 5}, ...}``.
        exposures_update_interval: If greater than zero, exposures are redrawn
            every given number of periods.

    Examples:
        >>> from extendedmosaicperm.experiments.sign_flip import SignFlipExperiment
        >>> exp = SignFlipExperiment(n_sims=1, nrand=3, seed=0, violation_strengths=[0.0])
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
        # method name → sign_flipping flag
        self.methods = {"perm": False, "sign": True}

    def extract_method(self, label: str) -> str:
        """Return the method identifier parsed from an experiment label.

        Args:
            label: Label string of the form
                ``"<gen>_<size>_<sym|asym>_<perm|sign>"``.

        Returns:
            str: ``"sign"`` if the label ends with ``"_sign"``, otherwise ``"perm"``.
        """
        return "sign" if "sign" in label else "perm"

    def run(self) -> None:
        """Execute the full simulation grid and store p-values.

        Populates ``self.results`` as a nested dictionary of the form::

            {
                label: {
                    violation_strength: np.ndarray of p-values
                }
            }

        where ``label`` encodes generator, size, symmetry, and method.
        """
        results: Dict[str, Dict[float, np.ndarray]] = {}

        label_list = [
            (g, s, sym, m)
            for g in self.generators
            for s in self.sizes
            for sym in [True, False]  # symmetric vs asymmetric
            for m in self.methods
        ]

        for gname, sname, sym, mname in tqdm(label_list, desc="Running SignFlipExperiment"):
            label = f"{gname}_{sname}_{'sym' if sym else 'asym'}_{mname}"
            results[label] = {}

            gen_func = self.generators[gname]
            params = self.sizes[sname]
            use_sign = self.methods[mname]

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
                        sign_flipping=use_sign,
                    )
                    mpt.fit(nrand=self.nrand, verbose=False)
                    pvals.append(float(mpt.pval))

                results[label][v] = np.array(pvals)

        self.results = results

    def compare_method_timings_all_sizes(
        self,
        n_repeats: int = 10,
        violation_strength: float = 0.1,
        symmetric: bool = True,
        return_full: bool = False,
    ):
        """Benchmark permutation vs sign-flipping for the ``"block"`` generator.

        For each size setting and method (``"perm"``, ``"sign"``), this routine
        runs ``n_repeats`` short fits using the same dataset across methods
        within a repeat. It records p-values and wall-clock runtimes.

        Args:
            n_repeats: Number of runs per method per size.
            violation_strength: Strength of the residual correlation / symmetry
                violation for the ``"block"`` generator.
            symmetric: Whether residuals are symmetric (``True`` → ``"sym"``,
                ``False`` → ``"asym"``).
            return_full: If ``True``, also return the full run-level DataFrame in
                addition to the summary.

        Returns:
            pandas.DataFrame or tuple[pandas.DataFrame, pandas.DataFrame]:
                If ``return_full`` is ``False``, returns a summary DataFrame with
                columns:

                * ``"size"``,
                * ``"method"``,
                * ``"pval_mean"``,
                * ``"pval_std"``,
                * ``"runtime_mean"``,
                * ``"runtime_std"``.

                If ``return_full`` is ``True``, returns a pair
                ``(summary, df_full)``, where ``df_full`` contains run-level
                results with columns:

                * ``"size"``,
                * ``"method"``,
                * ``"p_value"``,
                * ``"runtime_sec"``.

        Raises:
            ValueError: If the ``"block"`` generator is not available.
        """
        if "block" not in self.generators:
            raise ValueError("This benchmark expects a 'block' generator in self.generators.")

        all_results = []

        for size_name, params in self.sizes.items():
            for i in tqdm(range(n_repeats), desc=f"{size_name} runs", leave=False):
                # One dataset per repeat, reused across methods
                generator = FactorModelDataGenerator(
                    n_timepoints=params["T"],
                    n_assets=params["p"],
                    n_factors=params["k"],
                    seed=self.seed + i,
                )
                Y, L, X, eps = self.generators["block"](generator, violation_strength, symmetric)

                for method_name, sign_flip_flag in self.methods.items():
                    mpt = ExtendMosaicFactorTest(
                        outcomes=Y,
                        exposures=L,
                        test_stat=mp.statistics.mean_maxcorr_stat,
                        sign_flipping=sign_flip_flag,
                    )

                    t0 = time.time()
                    mpt.fit(nrand=self.nrand, verbose=False)
                    t1 = time.time()

                    all_results.append(
                        {
                            "size": size_name,
                            "method": method_name,
                            "p_value": float(mpt.pval),
                            "runtime_sec": t1 - t0,
                        }
                    )

        df_full = pd.DataFrame(all_results)
        summary = (
            df_full.groupby(["size", "method"])
            .agg(
                pval_mean=("p_value", "mean"),
                pval_std=("p_value", "std"),
                runtime_mean=("runtime_sec", "mean"),
                runtime_std=("runtime_sec", "std"),
            )
            .reset_index()
        )

        if return_full:
            return summary, df_full
        return summary
