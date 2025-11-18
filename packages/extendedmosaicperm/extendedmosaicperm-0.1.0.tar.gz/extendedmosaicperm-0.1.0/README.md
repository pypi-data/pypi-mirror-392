# extendedmosaicperm

Extended tools for Mosaic Permutation Tests — including:

- ✓ sign-flip inference  
- ✓ ridge-regularized residuals  
- ✓ adaptive tiling  
- ✓ experiment utilities  

All built as a thin, clean extension on top of the original `mosaicperm` package.

The goal is to explore faster, more robust, and more flexible randomization inference procedures for high-dimensional factor models.

---

## Installation

### Stable version (PyPI)
```
pip install extendedmosaicperm
```

### Development version (GitHub)
```
pip install git+https://github.com/skonieczkak/extendedmosaicperm.git
```

---

## Usage Examples

### Basic — Sign-flip test
```python
import numpy as np
from extendedmosaicperm.factor import ExtendMosaicFactorTest
import mosaicperm as mp

rng = np.random.default_rng(0)
T, p, k = 200, 50, 3

Y = rng.normal(size=(T, p))
L = rng.normal(size=(p, k))

test = ExtendMosaicFactorTest(
    outcomes=Y,
    exposures=L,
    test_stat=mp.statistics.mean_maxcorr_stat,
    sign_flipping=True,
)

test.fit(nrand=500)
print("p-value:", test.pval)
```

### Adaptive tiling
```python
from extendedmosaicperm.tilings import build_adaptive_tiling

tiling = build_adaptive_tiling(
    outcomes=Y,
    exposures=L,
    batch_size=20,
    seed=0
)

print(len(tiling.tiles))
```

### Monte Carlo experiment
```python
from extendedmosaicperm.experiments.sign_flip import SignFlipExperiment

exp = SignFlipExperiment(
    n_sims=100,
    nrand=200,
    seed=123
)

exp.run()
df = exp.summarize()
print(df.head())
```

---

## Documentation

Full documentation, including the API reference, usage examples, and theoretical background, is available at:

https://extendedmosaicperm.readthedocs.io

---

## Testing

Run the unit tests:
```
pytest extendedmosaicperm/tests
```


## License

MIT License — same as the parent `mosaicperm` project.

---
