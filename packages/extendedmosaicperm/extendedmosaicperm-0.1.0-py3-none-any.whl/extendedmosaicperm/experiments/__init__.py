"""
Monte Carlo experiments and plotting utilities for extendedmosaicperm.
"""

from .base import BaseExperiment
from .adaptive_tiling import AdaptiveTilingExperiment
from .ridge import RidgeExperiment
from .sign_flip import SignFlipExperiment
from .plotting import (
    enrich_flatten,
    compute_power_table,
    plot_qq_grid_all_sizes,
    plot_qq_grid_generators_by_alpha,
    plot_figure3_panels,
)

__all__ = [
    "BaseExperiment",
    "AdaptiveTilingExperiment",
    "RidgeExperiment",
    "SignFlipExperiment",
    "enrich_flatten",
    "compute_power_table",
    "plot_qq_grid_all_sizes",
    "plot_qq_grid_generators_by_alpha",
    "plot_figure3_panels",
]