"""
QARDL: Quantile Autoregressive Distributed Lag Models

Complete implementation of Cho, Kim & Shin (2015) with ALL corrections applied.

Key Features
------------
✓ Proper standard errors with H_t projection (Theorem 1)
✓ Correct n² scaling for long-run Wald tests (Corollary 1)
✓ Correct n scaling for short-run Wald tests (Corollaries 2, 3)
✓ Complete ECM representation (Equation 6)
✓ OLS-based lag selection at mean (icmean.m method)
✓ Correct M matrix for long-run parameters (Theorem 2)
✓ Complete rolling estimation with all parameters
✓ Multi-quantile covariance structures (Corollary 4)

Example
-------
>>> import numpy as np
>>> from qardl import QARDLCorrected
>>>
>>> # Generate data
>>> y = np.random.randn(100)
>>> X = np.random.randn(100, 2)
>>>
>>> # Estimate QARDL(2,1) at median
>>> model = QARDLCorrected(y, X, p=2, q=1, tau=0.5)
>>> results = model.fit()
>>> print(results.summary())
>>>
>>> # Multiple quantiles
>>> model_multi = QARDLCorrected(y, X, p=2, q=1, tau=[0.25, 0.5, 0.75])
>>> results_multi = model_multi.fit()

References
----------
Cho, J.S., Kim, T.-H., & Shin, Y. (2015). Quantile cointegration in the
autoregressive distributed-lag modeling framework. Journal of Econometrics,
188(1), 281-300.

Author
------
Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/qardl

Version History
---------------
1.0.3 - API change: Accept (y, X) instead of (data) for better usability
1.0.2 - Previous version
1.0.1 - Bug fix: X_effective ordering in _prepare_data() method
1.0.0 - Initial release with all corrections
"""

__version__ = "1.0.3"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

# Core estimation
from .core_corrected import QARDLCorrected, QARDLResultsCorrected

# Wald tests with CORRECT scaling
from .tests_corrected import WaldTestsCorrected

# Complete ECM representation
from .ecm_corrected import QARDLtoECM, ECMWaldTests

# Lag selection using OLS at mean
from .lag_selection import (
    select_qardl_orders,
    select_orders_sequential,
    evaluate_order_stability,
    compare_orders
)

# Complete rolling estimation
from .rolling_corrected import RollingQARDL, compare_quantiles_rolling

# Utilities
from .utils import quantile_regression, bandwidth_hall_sheather
from .visualization import plot_quantile_coefficients, plot_rolling_results

__all__ = [
    # Core
    'QARDLCorrected',
    'QARDLResultsCorrected',

    # Tests
    'WaldTestsCorrected',

    # ECM
    'QARDLtoECM',
    'ECMWaldTests',

    # Lag selection
    'select_qardl_orders',
    'select_orders_sequential',
    'evaluate_order_stability',
    'compare_orders',

    # Rolling
    'RollingQARDL',
    'compare_quantiles_rolling',

    # Utilities
    'quantile_regression',
    'bandwidth_hall_sheather',
    'plot_quantile_coefficients',
    'plot_rolling_results',
]


def get_corrections():
    """Return information about corrections in version 1.0.3"""
    return {
        'version': '1.0.3',
        'api_change': 'Accept (y, X) parameters instead of (data) for better usability',
        'corrections': [
            'API: Accept separate y and X parameters (more intuitive)',
            'Bug fix: X_effective and y_effective now set BEFORE building matrices',
            'Proper H_t projection for standard errors (Theorem 1)',
            'Correct n² scaling for long-run Wald tests (Corollary 1)',
            'Correct n scaling for short-run Wald tests (Corollaries 2-3)',
            'Complete ECM representation (Equation 6)',
            'OLS-based lag selection at mean',
            'Correct M matrix computation (Theorem 2)',
            'Complete rolling estimation',
        ],
        'reference': 'Cho, Kim & Shin (2015) Journal of Econometrics'
    }


def print_corrections():
    """Print all corrections made in this package"""
    print("=" * 80)
    print("QARDL PACKAGE v1.0.3 - CORRECTIONS SUMMARY")
    print("=" * 80)
    print("\n✓ NEW in v1.0.3:")
    print("  - API CHANGE: Now accepts (y, X, p, q, tau) instead of (data, p, q, tau)")
    print("  - More intuitive: Separate y and X parameters like standard packages")
    print("")
    print("✓ CRITICAL BUG FIX (v1.0.1):")
    print("  - Fixed X_effective ordering in _prepare_data()")
    print("  - Problem: X_effective was set AFTER _build_Z_matrix() called")
    print("  - Solution: X_effective now set BEFORE building matrices")
    print("")
    print("✓ Standard Errors:")
    print("  - Uses H_t projection: H_t = K_t - E[K_tW_t']E[W_tW_t']^{-1}W_t")
    print("  - Implements exact variance from Theorem 1")
    print("")
    print("✓ Long-Run Wald Tests:")
    print("  - Uses n² scaling (Corollary 1)")
    print("  - Statistic: W = n²(Rβ-r)'[R(Σ⊗M⁻¹)R']⁻¹(Rβ-r)")
    print("")
    print("✓ Short-Run Wald Tests:")
    print("  - Uses n scaling (Corollaries 2-3)")
    print("  - Statistic: W = n(Rφ-r)'[RΞR']⁻¹(Rφ-r)")
    print("")
    print("✓ ECM Representation:")
    print("  - Complete Equation (6) implementation")
    print("  - All parameters: ζ, β, φ*, θ*")
    print("")
    print("✓ Lag Selection:")
    print("  - OLS-based BIC at mean (icmean.m)")
    print("")
    print("✓ Rolling Estimation:")
    print("  - Complete with all parameters")
    print("")
    print("=" * 80)
    print("Reference: Cho, Kim & Shin (2015) Journal of Econometrics")
    print("=" * 80)