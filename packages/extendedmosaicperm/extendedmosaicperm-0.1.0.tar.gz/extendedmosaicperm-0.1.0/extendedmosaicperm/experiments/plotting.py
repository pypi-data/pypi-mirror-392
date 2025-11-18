from __future__ import annotations

import os
import re
from typing import Callable, Dict, Iterable, Optional, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import mosaicperm as mp
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.stats import uniform

from .base import BaseExperiment  # noqa: F401  (użyte pośrednio przez API)

# Paper-friendly, serif typography
mpl.rcParams.update(
    {
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
    }
)

_LABEL_RE = re.compile(r"^(?P<gen>\w+)_(?P<size>\w+)_(?P<sym>sym|asym)_(?P<method>\w+)$")
_LABEL_MAP = {"perm": "Permutation", "sign": "Sign-flipping", "ridge": "Ridge", "ols": "OLS"}


def parse_label(label: str) -> Dict[str, str]:
    """Parse an experiment label into components.

    Args:
        label: Label string of the form
            ``"<generator>_<size>_<sym|asym>_<method>"``.

    Returns:
        Dict[str, str]: Parsed components with keys:

        * ``"gen"``,
        * ``"size"``,
        * ``"sym"``,
        * ``"method"``.
    """
    m = _LABEL_RE.match(label)
    if not m:
        parts = label.split("_")
        return {
            "gen": parts[0] if len(parts) > 0 else "unknown",
            "size": parts[1] if len(parts) > 1 else "unknown",
            "sym": parts[2] if len(parts) > 2 else "sym",
            "method": parts[-1] if parts else "unknown",
        }
    return m.groupdict()


def enrich_flatten(df_flat: pd.DataFrame) -> pd.DataFrame:
    """Add parsed label components as columns to a flattened DataFrame.

    Args:
        df_flat: Long-form DataFrame from :meth:`BaseExperiment.flatten`,
            containing at least a ``"label"`` column.

    Returns:
        pandas.DataFrame: Copy of ``df_flat`` with extra columns added:

        * ``"gen"``,
        * ``"size"``,
        * ``"sym"``,
        * ``"method"``.
    """
    parsed = df_flat["label"].apply(parse_label).apply(pd.Series)
    cols_to_add = [c for c in ["gen", "size", "sym", "method"] if c not in df_flat.columns]
    parsed = parsed[cols_to_add] if cols_to_add else parsed.iloc[:, 0:0]
    return pd.concat([df_flat.reset_index(drop=True), parsed.reset_index(drop=True)], axis=1)


def compute_power_table(df_flat: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Aggregate empirical power across methods and configurations.

    Args:
        df_flat: Long-form DataFrame from :meth:`BaseExperiment.flatten`.
        alpha: Significance level used to compute power (default 0.05).

    Returns:
        pandas.DataFrame: DataFrame with columns:

        * ``"gen"``,
        * ``"size"``,
        * ``"sym"``,
        * ``"method"``,
        * ``"violation_strength"``,
        * ``"power"``.
    """
    df = enrich_flatten(df_flat).copy()
    df["reject"] = df["p_value"] < alpha
    grp = df.groupby(["gen", "size", "sym", "method", "violation_strength"], dropna=False)["reject"]
    return grp.mean().reset_index().rename(columns={"reject": "power"})


def plot_qq_grid_all_sizes(
    df_flat: pd.DataFrame,
    generators: Optional[Iterable[str]] = None,
    sizes: Optional[Iterable[str]] = None,
    v: float = 0.0,
    symmetry_options: Iterable[str] = ("sym", "asym"),
    method_linestyles: Optional[Dict[str, str]] = None,
    figscale: Tuple[int, int] = (12, 16),
    output_path: Optional[str] = None,
    title_fontsize: int = 17,
    label_fontsize: int = 16,
    tick_fontsize: int = 15,
    legend_fontsize: int = 14,
    legend_ncol: Optional[int] = None,
    legend_offset: float = -0.012,
    tight_rect: Tuple[float, float, float, float] = (0.02, 0.05, 0.98, 0.96),
):
    """Create a QQ-grid by generator (rows) and symmetry (columns).

    Each panel shows QQ-plots of p-values at a fixed violation level ``v``,
    colored by size and styled by method.

    Args:
        df_flat: Long-form DataFrame from :meth:`BaseExperiment.flatten`.
        generators: Generators to display. If ``None``, all available
            generators are used.
        sizes: Size categories to display. If ``None``, all available sizes
            are used.
        v: Violation strength to slice on.
        symmetry_options: Iterable of symmetry flags (e.g. ``("sym", "asym")``).
        method_linestyles: Mapping from method to line style, e.g.
            ``{"perm": "-", "sign": "--"}``. If ``None``, a default mapping
            is used.
        figscale: Figure size as ``(width, height)`` in inches.
        output_path: Optional path to save the figure as an image.
        title_fontsize: Font size for panel titles.
        label_fontsize: Font size for axis labels.
        tick_fontsize: Font size for tick labels.
        legend_fontsize: Font size for legend labels.
        legend_ncol: Number of columns in the combined legend. If ``None``,
            a heuristic is used.
        legend_offset: Vertical offset for the combined legend in figure
            coordinates.
        tight_rect: Bounding rectangle for :func:`matplotlib.pyplot.tight_layout`.

    Returns:
        matplotlib.figure.Figure: The created figure.

    Raises:
        ValueError: If the required label structure or requested generators /
            sizes are not present in the data.
    """
    df = enrich_flatten(df_flat).copy()

    if method_linestyles is None:
        method_linestyles = {"perm": "-", "sign": "--", "ridge": ":", "ols": "-."}

    gens_avail = sorted(df["gen"].unique()) if "gen" in df.columns else []
    if not gens_avail:
        raise ValueError(
            "No 'gen' column detected. Ensure labels follow "
            "'<gen>_<size>_<sym|asym>_<method>'."
        )

    if generators is None:
        generators = gens_avail
    else:
        generators = [g for g in generators if g in gens_avail]
        if not generators:
            raise ValueError("Requested generators not found in data.")

    symmetry_options = list(symmetry_options)
    n_rows = len(generators)
    n_cols = len(symmetry_options)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figscale, sharex=True, sharey=True)
    axes = np.atleast_2d(axes)

    sizes_avail = sorted(df["size"].unique()) if "size" in df.columns else []
    if sizes is None:
        sizes_used = sizes_avail
    else:
        sizes_used = [s for s in sizes if s in sizes_avail]
        if not sizes_used:
            raise ValueError("Requested sizes not found in data.")

    cmap = plt.get_cmap("tab10", max(1, len(sizes_used)))
    size_color_map = {size: cmap(i) for i, size in enumerate(sizes_used)}

    for r, gen in enumerate(generators):
        for c, sym in enumerate(symmetry_options):
            ax = axes[r, c]
            pane = df[
                (df["gen"] == gen)
                & (df["sym"] == sym)
                & (df["violation_strength"] == v)
            ]
            if pane.empty:
                ax.set_visible(False)
                continue

            pane_sizes = [s for s in sorted(pane["size"].unique()) if s in sizes_used]
            methods_present = sorted(pane["method"].unique())
            for size in pane_sizes:
                for method in methods_present:
                    sub = pane[(pane["size"] == size) & (pane["method"] == method)]
                    pvals = np.sort(sub["p_value"].to_numpy())
                    n = len(pvals)
                    if n == 0:
                        continue

                    uq = uniform.ppf((np.arange(1, n + 1) - 0.5) / n)
                    ax.plot(
                        uq,
                        pvals,
                        linestyle=method_linestyles.get(method, "-"),
                        color=size_color_map.get(size, "C0"),
                        linewidth=2,
                    )

            ax.plot([0, 1], [0, 1], "k--", linewidth=1)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal", "box")
            ax.grid(True, linestyle=":", linewidth=0.6)
            if r == n_rows - 1:
                ax.set_xlabel("Theoretical quantiles", fontsize=label_fontsize)
            if c == 0:
                ax.set_ylabel("Empirical quantiles", fontsize=label_fontsize)
            ax.set_title(
                f"{gen.capitalize()} — {'Sym' if sym == 'sym' else 'Asym'}",
                fontsize=title_fontsize,
            )
            ax.tick_params(axis="both", labelsize=tick_fontsize)

    methods_global = sorted(df["method"].unique())
    handles, labels = [], []
    for size in sizes_used:
        for method in methods_global:
            handles.append(
                Line2D(
                    [0],
                    [0],
                    color=size_color_map[size],
                    lw=3,
                    linestyle=method_linestyles.get(method, "-"),
                )
            )
            labels.append(f"{size.capitalize()} ({_LABEL_MAP.get(method, method)})")

    if handles:
        if legend_ncol is None:
            legend_ncol = min(4, max(2, len(methods_global)))
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, legend_offset),
            ncol=legend_ncol,
            fontsize=legend_fontsize,
            title_fontsize=legend_fontsize,
            frameon=False,
            title="Size (Method)",
        )

    plt.tight_layout(rect=tight_rect)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def plot_qq_grid_generators_by_alpha(
    df_flat: pd.DataFrame,
    generators: Iterable[str],
    alphas: Iterable[float],
    sizes: Optional[Iterable[str]] = None,
    symmetry: str = "asym",
    method_linestyles: Optional[Dict[str, str]] = None,
    figscale_base: Tuple[float, float] = (5.8, 4.8),
    output_path: Optional[str] = None,
    title_fontsize: int = 17,
    label_fontsize: int = 16,
    tick_fontsize: int = 15,
    legend_fontsize: int = 14,
    legend_ncol: int = 3,
    legend_offset: float = -0.012,
    tight_rect: Tuple[float, float, float, float] = (0.02, 0.05, 0.98, 0.94),
):
    """Create a QQ-grid with rows = generators and columns = violation strengths.

    Args:
        df_flat: Long-form DataFrame from :meth:`BaseExperiment.flatten`.
        generators: Generators to include as rows.
        alphas: Violation strength values (x-axis conditions) to include as
            columns.
        sizes: Size categories to display. If ``None``, all available sizes
            are used.
        symmetry: Symmetry flag to filter on (e.g. ``"asym"``).
        method_linestyles: Mapping from method to line style. If ``None``,
            a default mapping is used.
        figscale_base: Base figure size for a single panel. Total figure size
            scales with the grid dimensions.
        output_path: Optional path to save the figure as an image.
        title_fontsize: Font size for panel titles.
        label_fontsize: Font size for axis labels.
        tick_fontsize: Font size for tick labels.
        legend_fontsize: Font size for legend labels.
        legend_ncol: Number of columns in the combined legend.
        legend_offset: Vertical offset for the combined legend.
        tight_rect: Bounding rectangle for :func:`matplotlib.pyplot.tight_layout`.

    Returns:
        matplotlib.figure.Figure: The created figure.

    Raises:
        ValueError: If there is no data after filtering or requested sizes are
            not present.
    """
    df = enrich_flatten(df_flat).copy()

    if method_linestyles is None:
        method_linestyles = {"perm": "-", "sign": "--", "ridge": ":", "ols": "-."}

    generators = list(generators)
    alphas = list(alphas)

    df = df[df["sym"] == symmetry]
    if df.empty:
        raise ValueError(f"No data after filtering for symmetry='{symmetry}'.")

    sizes_avail = sorted(df["size"].unique()) if "size" in df.columns else []
    if sizes is None:
        sizes_used = sizes_avail
    else:
        sizes_used = [s for s in sizes if s in sizes_avail]
        if not sizes_used:
            raise ValueError("Requested sizes not found in data.")

    n_rows, n_cols = len(generators), len(alphas)
    fig_w = figscale_base[0] * n_cols
    fig_h = figscale_base[1] * n_rows
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_w, fig_h), sharex=True, sharey=True)
    axes = np.atleast_2d(axes)

    cmap = plt.get_cmap("tab10", max(1, len(sizes_used)))
    size_color_map = {size: cmap(i) for i, size in enumerate(sizes_used)}

    for r, gen in enumerate(generators):
        for c, v in enumerate(alphas):
            ax = axes[r, c]
            pane = df[(df["gen"] == gen) & (df["violation_strength"] == v)]
            if pane.empty:
                ax.set_visible(False)
                continue

            for size in sizes_used:
                for method in sorted(pane["method"].unique()):
                    sub = pane[(pane["size"] == size) & (pane["method"] == method)]
                    pvals = np.sort(sub["p_value"].to_numpy())
                    n = len(pvals)
                    if n == 0:
                        continue

                    uq = uniform.ppf((np.arange(1, n + 1) - 0.5) / n)
                    ax.plot(
                        uq,
                        pvals,
                        linestyle=method_linestyles.get(method, "-"),
                        color=size_color_map.get(size, "C0"),
                        linewidth=2,
                    )

            ax.plot([0, 1], [0, 1], "k--", linewidth=1)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal", "box")
            ax.grid(True, linestyle=":", linewidth=0.6)
            if c == 0:
                ax.set_ylabel("Empirical quantiles", fontsize=label_fontsize)
            if r == n_rows - 1:
                ax.set_xlabel("Theoretical quantiles", fontsize=label_fontsize)
            ax.set_title(f"{gen.capitalize()}, α = {v:g}", fontsize=title_fontsize)
            ax.tick_params(axis="both", labelsize=tick_fontsize)

    methods_global = sorted(df["method"].unique())
    handles, labels = [], []
    for size in sizes_used:
        for method in methods_global:
            handles.append(
                Line2D(
                    [0],
                    [0],
                    color=size_color_map[size],
                    lw=3,
                    linestyle=method_linestyles.get(method, "-"),
                )
            )
            labels.append(f"{size.capitalize()} ({_LABEL_MAP.get(method, method)})")

    if handles:
        fig.legend(
            handles,
            labels,
            loc="lower center",
            bbox_to_anchor=(0.5, legend_offset),
            ncol=legend_ncol,
            fontsize=legend_fontsize,
            title_fontsize=legend_fontsize,
            frameon=False,
            title="Size (Method)",
        )

    plt.tight_layout(rect=tight_rect)
    plt.subplots_adjust(wspace=0, hspace=0.15)

    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def plot_figure3_panels(
    L_time: np.ndarray,
    simulate_fn: Callable[[np.random.Generator], np.ndarray],
    *,
    test_stat: Callable = mp.statistics.mean_maxcorr_stat,
    n_rep_a: int = 100,
    n_rep_b: int = 100,
    b_boot: int = 300,
    n_runs_c: int = 100,
    n_perm_c: int = 300,
    bins_a: int = 25,
    bins_b: int = 25,
    bins_c: int = 25,
    seed: int = 42,
    colors: Optional[Dict[str, str]] = None,
    outdir: Optional[str] = None,
    save_basename: str = "figure3_panels",
    title_fontsize: int = 14,
    label_fontsize: int = 12,
    tick_fontsize: int = 11,
    legend_fontsize: int = 11,
) -> Tuple[plt.Figure, Dict[str, np.ndarray]]:
    """Reproduce a three-panel comparison: naive permutation, bootstrap, and Mosaic test.

    Panel (a) compares the naive permutation distribution of the maximum
    off-diagonal correlation with the observed OLS-based statistic.
    Panel (b) compares bootstrap Z-statistics with a standard normal.
    Panel (c) compares Mosaic test statistics with their permutation null.

    Args:
        L_time: Time-varying exposures of shape ``(T, p, k)``.
        simulate_fn: Callable that takes a NumPy :class:`~numpy.random.Generator`
            and returns a simulated outcome matrix ``Y`` of shape ``(T, p)``.
        test_stat: Test statistic to be used by the Mosaic test.
        n_rep_a: Number of datasets for panel (a).
        n_rep_b: Number of datasets for panel (b).
        b_boot: Number of bootstrap draws per dataset in panel (b).
        n_runs_c: Number of datasets for panel (c).
        n_perm_c: Number of permutations per dataset in panel (c).
        bins_a: Number of bins for the histogram in panel (a).
        bins_b: Number of bins for the histogram in panel (b).
        bins_c: Number of bins for the histogram in panel (c).
        seed: Seed used to initialize the random generator.
        colors: Optional mapping for color names
            ``{"null": ..., "alt": ..., "boot": ...}``.
        outdir: Optional output directory to save the figure as PNG.
        save_basename: Base file name for saving (without extension).
        title_fontsize: Font size for panel titles.
        label_fontsize: Font size for axis labels.
        tick_fontsize: Font size for tick labels.
        legend_fontsize: Font size for legend entries.

    Returns:
        tuple[matplotlib.figure.Figure, Dict[str, np.ndarray]]:
            The figure and a dictionary with the simulated statistics.
    """
    assert L_time.ndim == 3, "L_time must have shape (T, p, k)"
    T, p, k = L_time.shape
    L_const = L_time[0, :, :]
    rng = np.random.default_rng(seed)

    if colors is None:
        colors = {"null": "gray", "alt": "royalblue", "boot": "royalblue"}

    LtL_inv = np.linalg.pinv(L_const.T @ L_const)
    P_L = L_const @ LtL_inv @ L_const.T
    Mperp = np.eye(p) - P_L

    def ols_residuals(Y: np.ndarray) -> np.ndarray:
        return (Mperp @ Y.T).T

    def S_max_offdiag_corr(M: np.ndarray) -> float:
        C = np.corrcoef((M + 1e-12 * rng.normal(size=M.shape)).T)
        iu = np.triu_indices_from(C, k=1)
        return float(np.nanmax(np.abs(C[iu])))

    def permute_cols_independent(M: np.ndarray) -> np.ndarray:
        out = np.empty_like(M)
        for j in range(M.shape[1]):
            out[:, j] = rng.permutation(M[:, j])
        return out

    def bootstrap_Z_for_dataset(eps_hat: np.ndarray, n_boot: int) -> float:
        S_obs = S_max_offdiag_corr(eps_hat)
        S_b = np.empty(n_boot)
        T_ = eps_hat.shape[0]
        for b in range(n_boot):
            idx = rng.integers(0, T_, size=T_)
            S_b[b] = S_max_offdiag_corr(eps_hat[idx, :])
        bias = S_b.mean() - S_obs
        sd = S_b.std(ddof=1) + 1e-12
        return (S_obs - bias) / sd

    S_true, S_perm = np.empty(n_rep_a), np.empty(n_rep_a)
    for r in range(n_rep_a):
        Y = simulate_fn(rng)
        eps_hat = ols_residuals(Y)
        S_true[r] = S_max_offdiag_corr(eps_hat)
        S_perm[r] = S_max_offdiag_corr(permute_cols_independent(eps_hat))

    edges_a = np.linspace(
        min(S_true.min(), S_perm.min()),
        max(S_true.max(), S_perm.max()),
        bins_a + 1,
    )

    Z_boot = np.empty(n_rep_b)
    for r in range(n_rep_b):
        Y = simulate_fn(rng)
        eps_hat = ols_residuals(Y)
        Z_boot[r] = bootstrap_Z_for_dataset(eps_hat, b_boot)
    Z_ref = rng.normal(size=n_rep_b)
    edges_b = np.linspace(
        min(Z_boot.min(), Z_ref.min()),
        max(Z_boot.max(), Z_ref.max()),
        bins_b + 1,
    )

    S_mosaic, S_null_mean = [], []
    for _ in range(n_runs_c):
        Y = simulate_fn(rng)
        mpt = mp.factor.MosaicFactorTest(
            outcomes=Y,
            exposures=L_time,
            test_stat=test_stat,
        )
        res = mpt.fit(nrand=n_perm_c, verbose=False)
        S_mosaic.append(float(res.statistic))
        S_null_mean.append(float(np.mean(res.null_statistics)))
    S_mosaic = np.asarray(S_mosaic)
    S_null_mean = np.asarray(S_null_mean)

    edges_c = np.linspace(
        min(S_mosaic.min(), S_null_mean.min()),
        max(S_mosaic.max(), S_null_mean.max()),
        bins_c + 1,
    )
    centers_c = (edges_c[:-1] + edges_c[1:]) / 2
    widths_c = np.diff(edges_c)

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15, 5.8),
        constrained_layout=True,
    )

    ax = axes[0]
    ax.hist(
        S_perm,
        bins=edges_a,
        color=colors["null"],
        alpha=0.7,
        label="Naive perm. test",
    )
    ax.hist(
        S_true,
        bins=edges_a,
        color=colors["alt"],
        alpha=0.85,
        label=r"OLS statistic $S(\hat{\epsilon}^{\mathrm{OLS}})$",
    )
    ax.set_xlabel("(a) Naive permutation", fontsize=title_fontsize, labelpad=8)
    ax.set_ylabel("Count", fontsize=label_fontsize)
    ax.tick_params(axis="both", labelsize=tick_fontsize)
    ax.grid(True, ls=":", lw=0.6)
    ax.legend(
        frameon=False,
        fontsize=legend_fontsize,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.22),
        ncol=1,
    )

    ax = axes[1]
    ax.hist(
        Z_ref,
        bins=edges_b,
        color=colors["null"],
        alpha=0.8,
        label=r"$N(0,1)$",
    )
    ax.hist(
        Z_boot,
        bins=edges_b,
        color=colors["boot"],
        alpha=0.8,
        label="Bootstrap Z-statistic",
    )
    ax.set_xlabel("(b) Bootstrap calibration", fontsize=title_fontsize, labelpad=8)
    ax.tick_params(axis="both", labelsize=tick_fontsize)
    ax.grid(True, ls=":", lw=0.6)
    ax.legend(
        frameon=False,
        fontsize=legend_fontsize,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.22),
        ncol=1,
    )

    ax = axes[2]
    ax.bar(
        centers_c,
        np.histogram(S_null_mean, bins=edges_c)[0],
        width=widths_c,
        color=colors["null"],
        alpha=0.65,
        label="Mosaic permutations",
    )
    ax.bar(
        centers_c,
        np.histogram(S_mosaic, bins=edges_c)[0],
        width=widths_c,
        color=colors["alt"],
        alpha=0.85,
        label=r"Mosaic statistic $S(\hat{\epsilon})$",
    )
    ax.set_xlabel("(c) Mosaic test", fontsize=title_fontsize, labelpad=8)
    ax.tick_params(axis="both", labelsize=tick_fontsize)
    ax.grid(True, ls=":", lw=0.6)
    ax.legend(
        frameon=False,
        fontsize=legend_fontsize,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.22),
        ncol=1,
    )

    if outdir:
        os.makedirs(outdir, exist_ok=True)
        figpath = os.path.join(outdir, f"{save_basename}.png")
        fig.savefig(figpath, dpi=300, bbox_inches="tight")
        print(f"[INFO] Figure saved to: {figpath}")

    data = {
        "S_true": S_true,
        "S_perm": S_perm,
        "Z_boot": Z_boot,
        "Z_ref": Z_ref,
        "S_mosaic": S_mosaic,
        "S_null_mean": S_null_mean,
        "edges_a": edges_a,
        "edges_b": edges_b,
        "edges_c": edges_c,
    }
    return fig, data
