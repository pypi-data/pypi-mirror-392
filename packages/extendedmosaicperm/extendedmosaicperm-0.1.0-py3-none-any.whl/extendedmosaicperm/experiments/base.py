from __future__ import annotations

import os
import pickle
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import uniform


class BaseExperiment:
    """Base utilities and containers for Monte Carlo experiments.

    Subclasses should implement :meth:`run` to populate ``self.results`` and
    :meth:`extract_method` to map a label string to a method identifier.

    Attributes:
        results: Nested mapping of the form
            ``{label: {violation_strength: np.ndarray of p-values}}``,
            populated by :meth:`run`.
    """

    def __init__(self) -> None:
        """Initialize an empty experiment container."""
        self.results: Dict[str, Dict[float, np.ndarray]] | None = None

    def save(self, path: str) -> None:
        """Serialize results to a pickle file.

        Args:
            path: Output file path for the serialized results.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.results, f)

    def load(self, path: str) -> None:
        """Load results from a pickle file.

        Args:
            path: Input file path containing serialized results created by
                :meth:`save`.
        """
        with open(path, "rb") as f:
            self.results = pickle.load(f)

    def flatten(self) -> pd.DataFrame:
        """Flatten nested results into a long-form DataFrame.

        Returns:
            pandas.DataFrame: A DataFrame with columns:

            * ``"label"``,
            * ``"violation_strength"``,
            * ``"method"``,
            * ``"p_value"``.

        Raises:
            AssertionError: If ``self.results`` is ``None`` (i.e. :meth:`run`
                has not been executed).
        """
        assert self.results is not None, "No results. Run the experiment first."
        rows = []
        for label, v_dict in self.results.items():
            method = self.extract_method(label)
            for v, pvals in v_dict.items():
                for p in pvals:
                    rows.append(
                        {
                            "label": label,
                            "violation_strength": v,
                            "method": method,
                            "p_value": float(p),
                        }
                    )
        return pd.DataFrame(rows)

    def summarize(self) -> pd.DataFrame:
        """Summarize empirical power and p-value moments.

        For each label and violation strength, compute empirical rejection
        probability and basic p-value summaries.

        Returns:
            pandas.DataFrame: A summary DataFrame with columns:

            * ``"label"``,
            * ``"method"``,
            * ``"violation_strength"``,
            * ``"power"``,
            * ``"mean_pval"``,
            * ``"median_pval"``,
            * ``"std_pval"``,
            * ``"n"``.

        Raises:
            AssertionError: If ``self.results`` is ``None``.
        """
        assert self.results is not None, "No results. Run the experiment first."
        summary = []
        for label, v_dict in self.results.items():
            method = self.extract_method(label)
            for v, pvals in v_dict.items():
                pvals = np.asarray(pvals, dtype=float)
                summary.append(
                    {
                        "label": label,
                        "method": method,
                        "violation_strength": v,
                        "power": float(np.mean(pvals < 0.05)),
                        "mean_pval": float(np.mean(pvals)),
                        "median_pval": float(np.median(pvals)),
                        "std_pval": float(np.std(pvals)),
                        "n": int(len(pvals)),
                    }
                )
        return pd.DataFrame(summary)

    def extract_method(self, label: str) -> str:
        """Extract the method name from a label string.

        Args:
            label: Label produced by a concrete experiment, e.g.
                ``"random_small_sym_sign"``.

        Returns:
            str: Method identifier used by the experiment, e.g.
            ``"sign"``, ``"perm"``, ``"ridge"``, ``"ols"``.

        Raises:
            NotImplementedError: If a subclass does not override this method.
        """
        raise NotImplementedError

    def plot_power(
        self,
        df_flat: pd.DataFrame,
        generator: str = "random",
        symmetry: str = "sym",
    ):
        """Plot empirical power curves vs violation strength.

        Creates three panels for size settings ``"small"``, ``"medium"``,
        and ``"large"``.

        Args:
            df_flat: Long-form DataFrame returned by :meth:`flatten`.
            generator: Generator key used in labels, e.g. ``"random"``,
                ``"block"``, ``"common"``.
            symmetry: Symmetry flag used in labels, either ``"sym"`` or
                ``"asym"``.

        Returns:
            matplotlib.figure.Figure: Figure with three subplots showing power
            by method.
        """
        sizes = ["small", "medium", "large"]
        fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharex=True, sharey=True)

        for j, size in enumerate(sizes):
            base_label = f"{generator}_{size}_{symmetry}"
            ax = axes[j]
            df_sub = df_flat[df_flat["label"].str.startswith(base_label)].copy()
            df_sub["reject"] = df_sub["p_value"] < 0.05
            grouped = df_sub.groupby(["violation_strength", "method"])["reject"].mean().unstack()

            if grouped is not None and not grouped.empty:
                x = grouped.index.to_numpy()
                for method in grouped.columns:
                    ax.plot(x, grouped[method].to_numpy(), marker="o", label=method.capitalize())

            ax.set_title(f"{size.capitalize()} / {'Symmetric' if symmetry == 'sym' else 'Asymmetric'}")
            ax.grid(True)
            ax.set_xlabel("Violation Strength")
            if j == 0:
                ax.set_ylabel("Empirical Power")

        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper right",
            bbox_to_anchor=(0.98, 0.98),
            fontsize=12,
            title="Method",
        )
        plt.suptitle(
            f"Power Comparison ({symmetry.title()}) – {generator.capitalize()} Generator",
            fontsize=16,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.92])
        return fig

    def plot_qq(
        self,
        df_flat: pd.DataFrame,
        label_bases: list[str],
        v: float,
    ):
        """Draw QQ-plots of p-values for selected label bases at a fixed violation level.

        Args:
            df_flat: Long-form DataFrame returned by :meth:`flatten`.
            label_bases: Base labels (without method suffix) to compare, e.g.
                ``["random_small_sym", "random_medium_sym"]``.
            v: Violation strength value to slice on.

        Returns:
            matplotlib.figure.Figure: Figure with two QQ plots
            (empirical vs uniform).
        """
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True, sharey=True)

        for ax, label_base in zip(axes, label_bases):
            for method in df_flat["method"].unique():
                full_label = f"{label_base}_{method}"
                subset = df_flat[
                    (df_flat["label"] == full_label)
                    & (df_flat["violation_strength"] == v)
                ]
                pvals = subset["p_value"].sort_values().to_numpy()
                n = len(pvals)
                if n == 0:
                    continue
                uniform_q = uniform.ppf((np.arange(1, n + 1) - 0.5) / n)
                ax.plot(uniform_q, pvals, label=method.capitalize(), linewidth=2)

            ax.plot([0, 1], [0, 1], "k--", linewidth=1)
            ax.set_title(f"{label_base} (v = {v})")
            ax.set_xlabel("Theoretical Quantiles")
            ax.grid(True)

        axes[0].set_ylabel("Empirical Quantiles")
        axes[1].legend()
        plt.suptitle("QQ-Plots Under $H_0$", fontsize=14)
        plt.tight_layout(rect=[0, 0, 1, 0.93])
        return fig

    def plot_pval_histogram(
        self,
        df_flat: pd.DataFrame,
        label: str,
        v: float = 0.0,
        bins: int = 20,
    ):
        """Plot histograms of p-values at a given violation strength.

        Args:
            df_flat: Long-form DataFrame returned by :meth:`flatten`.
            label: Label prefix to filter rows, e.g. ``"random_small_sym"``.
            v: Violation strength value to slice on.
            bins: Number of histogram bins.

        Returns:
            matplotlib.figure.Figure: Figure with two panels, one histogram
            per method.
        """
        subset = df_flat[
            (df_flat["label"].str.startswith(label))
            & (df_flat["violation_strength"] == v)
        ]
        methods = subset["method"].unique()

        fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
        bin_edges = np.linspace(0, 1, bins + 1)

        for ax, method in zip(axes, methods):
            data = subset[subset["method"] == method]["p_value"]
            ax.hist(data, bins=bin_edges)
            ax.axhline(y=len(data) / bins, color="black", linestyle="--", linewidth=1)
            ax.axvline(x=0.05, color="red", linestyle="--", linewidth=1.5)
            ax.set_title(method.capitalize())
            ax.set_xlabel("p-value")
            ax.grid(True, linestyle=":", linewidth=0.5)

        axes[0].set_ylabel("Frequency")
        fig.suptitle(f"p-value Distributions for {label} (v = {v})", fontsize=14)
        return fig
