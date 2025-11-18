# QARDL: Quantile Autoregressive Distributed Lag Models

[![PyPI version](https://badge.fury.io/py/qardl.svg)](https://pypi.org/project/qardl/)
[![Python](https://img.shields.io/pypi/pyversions/qardl.svg)](https://pypi.org/project/qardl/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Complete Python implementation of **Quantile Autoregressive Distributed Lag (QARDL)** models from:

> Cho, J.S., Kim, T.-H., & Shin, Y. (2015). **Quantile cointegration in the autoregressive distributed-lag modeling framework**. *Journal of Econometrics*, 188(1), 281-300.

## What's New in v1.0.1

**CRITICAL BUG FIX:**
- Fixed ordering issue in `_prepare_data()` method
- `X_effective` and `y_effective` now correctly set **BEFORE** building matrices
- This bug caused "AttributeError: X_effective doesn't exist" errors

All theoretical corrections from the original paper are maintained and working properly.

## Features

✅ **Correct Implementation** - All formulas match Cho, Kim & Shin (2015) exactly
✅ **Proper Standard Errors** - H_t projection with correct asymptotic variance
✅ **Correct Wald Tests** - n² scaling for long-run, n scaling for short-run
✅ **Complete ECM** - Full Error Correction Model representation
✅ **Lag Selection** - OLS-based BIC/AIC at mean (icmean.m method)
✅ **Rolling Estimation** - Time-varying parameter analysis
✅ **Multi-Quantile** - Cross-quantile inference
✅ **Publication Ready** - Output formatted for academic journals

## Installation

```bash
pip install qardl
```

For development:
```bash
git clone https://github.com/merwanroudane/qardl
cd qardl
pip install -e .
```

## Quick Start

```python
import numpy as np
from qardl import QARDLCorrected

# Generate data
np.random.seed(42)
n = 200
y = np.cumsum(np.random.normal(0, 1, n))
X = np.cumsum(np.random.normal(0, 1, (n, 2)), axis=0)

# Estimate QARDL(2,1) at median
model = QARDLCorrected(y, X, p=2, q=1, tau=0.5)
results = model.fit()
results.summary()
```

## Core Functionality

### 1. QARDL Estimation

```python
from qardl import QARDLCorrected

# Single quantile
model = QARDLCorrected(y, X, p=2, q=1, tau=0.5)
results = model.fit()

# Multiple quantiles
model_multi = QARDLCorrected(y, X, p=2, q=1, tau=[0.25, 0.50, 0.75])
results_dict = model_multi.fit()
```

### 2. Hypothesis Testing

```python
from qardl import WaldTestsCorrected

# Initialize tests
wald = WaldTestsCorrected(results)

# Long-run parameters (uses n² scaling)
lr_test = wald.test_long_run_parameters()
print(f"LR Wald: {lr_test['statistic']:.4f}, p-value: {lr_test['pvalue']:.4f}")

# Short-run parameters (uses n scaling)
sr_test = wald.test_short_run_parameters()
print(f"SR Wald: {sr_test['statistic']:.4f}, p-value: {sr_test['pvalue']:.4f}")

# Symmetry test
sym_test = wald.test_symmetry()
```

### 3. ECM Representation

```python
from qardl import QARDLtoECM, ECMWaldTests

# Convert to ECM
ecm = QARDLtoECM(results)
ecm.print_summary()

# ECM-specific tests
ecm_wald = ECMWaldTests(ecm)
speed_test = ecm_wald.test_speed_of_adjustment()
```

### 4. Lag Selection

```python
from qardl import select_qardl_orders

# Automatic lag selection
best_orders = select_qardl_orders(
    y, X,
    max_p=4,
    max_q=4,
    tau=0.5,
    criterion='bic'
)
print(f"Optimal lags: p={best_orders['p']}, q={best_orders['q']}")
```

### 5. Rolling Estimation

```python
from qardl import RollingQARDL

# Rolling window estimation
rolling = RollingQARDL(y, X, p=2, q=1, tau=0.5, window=100)
rolling_results = rolling.estimate()

# Plot results
rolling.plot_coefficients(['beta_y_lag1', 'delta_x1'])
```

## Complete Example

See `examples/` folder for detailed examples:
- `example_01_basic_qardl.py` - Basic estimation
- `example_02_wald_tests.py` - Hypothesis testing
- `example_03_ecm.py` - ECM representation
- `example_04_lag_selection.py` - Lag selection
- `example_05_multiple_quantiles.py` - Multi-quantile analysis
- `example_06_rolling.py` - Rolling estimation

## Mathematical Background

### QARDL(p,q) Model

The model estimates conditional quantiles:

```
Q_τ(y_t | X_t) = β_0(τ) + β_1(τ)y_{t-1} + Σ γ_i(τ)Δy_{t-i} + 
                  Σ_j [δ_j(τ)x_{jt} + Σ_i φ_{ji}(τ)Δx_{jt-i}]
```

### Key Corrections

1. **Standard Errors** (Theorem 1):
   - Uses H_t projection: `H_t = K_t - E[K_tW_t']E[W_tW_t']^{-1}W_t`
   - Asymptotic variance: `Var(β̂) = τ(1-τ) * (M^{-1} Σ M^{-1}) / n²`

2. **Long-Run Wald Tests** (Corollary 1):
   - Statistic: `W = n²(Rβ-r)'[R(Σ⊗M^{-1})R']^{-1}(Rβ-r)`
   - Uses **n²** scaling (not n)

3. **Short-Run Wald Tests** (Corollaries 2-3):
   - Statistic: `W = n(Rφ-r)'[RΠR']^{-1}(Rφ-r)`
   - Uses **n** scaling

4. **M Matrix** (Theorem 2):
   - Formula: `M = n^{-2}X'[I - W(W'W)^{-1}W']X`
   - Critical for long-run inference

## API Reference

### Classes

- **`QARDLCorrected`** - Main estimation class
- **`QARDLResultsCorrected`** - Results container
- **`WaldTestsCorrected`** - Hypothesis testing
- **`QARDLtoECM`** - ECM representation
- **`RollingQARDL`** - Rolling window estimation

### Functions

- **`select_qardl_orders()`** - Automatic lag selection
- **`select_orders_sequential()`** - Sequential testing
- **`compare_orders()`** - Compare multiple specifications
- **`quantile_regression()`** - Basic quantile regression
- **`bandwidth_hall_sheather()`** - Bandwidth selection

## Requirements

- Python >= 3.7
- NumPy >= 1.20.0
- SciPy >= 1.7.0
- pandas >= 1.3.0
- statsmodels >= 0.13.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0

## Citation

If you use this package in your research, please cite:

```bibtex
@article{cho2015quantile,
  title={Quantile cointegration in the autoregressive distributed-lag modeling framework},
  author={Cho, Jin Seo and Kim, Tae-Hwan and Shin, Yongcheol},
  journal={Journal of Econometrics},
  volume={188},
  number={1},
  pages={281--300},
  year={2015},
  publisher={Elsevier}
}
```

And for the software:

```bibtex
@software{qardl2024,
  title={QARDL: Quantile Autoregressive Distributed Lag Models},
  author={Roudane, Merwan},
  year={2024},
  url={https://github.com/merwanroudane/qardl}
}
```

## License

MIT License - see LICENSE file

## Author

**Dr. Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: https://github.com/merwanroudane

## Acknowledgments

This implementation is based on the original MATLAB and GAUSS codes accompanying Cho, Kim & Shin (2015). All theoretical results follow their paper exactly.

## Support

- **Issues**: https://github.com/merwanroudane/qardl/issues
- **Documentation**: https://github.com/merwanroudane/qardl
- **Email**: merwanroudane920@gmail.com

---

**Important**: This package implements ALL corrections from the original paper. Previous versions may have had bugs - always use v1.0.1 or later.
