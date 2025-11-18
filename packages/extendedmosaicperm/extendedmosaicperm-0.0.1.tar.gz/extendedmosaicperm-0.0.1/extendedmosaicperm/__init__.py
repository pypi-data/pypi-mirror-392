"""
extendedmosaicperm: extensions and experiments for mosaic permutation tests.
"""

__version__ = "0.0.1"

from .factor import ExtendMosaicFactorTest
from .tilings import build_adaptive_tiling
from .factor_data import FactorModelDataGenerator

__all__ = ["ExtendMosaicFactorTest", "build_adaptive_tiling", "FactorModelDataGenerator", "experiments"]
