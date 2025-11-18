"""
CORRECTED QARDL Package

Complete implementation of Cho, Kim & Shin (2015) with ALL corrections:

CRITICAL FIXES:
1. ✓ Proper standard errors with H_t projection (Theorem 1)
2. ✓ Correct n² scaling for long-run Wald tests (Corollary 1)
3. ✓ Correct n scaling for short-run Wald tests (Corollaries 2, 3)
4. ✓ Complete ECM representation (Equation 6)
5. ✓ OLS-based lag selection at mean (icmean.m method)
6. ✓ Correct M matrix for long-run parameters (Theorem 2)
7. ✓ Complete rolling estimation with all parameters
8. ✓ Multi-quantile covariance structures (Corollary 4)

References
----------
Cho, J.S., Kim, T., & Shin, Y. (2015). Quantile cointegration in the
autoregressive distributed-lag modeling framework. Journal of 
Econometrics, 188(1), 281-300.

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/qardl
Corrected implementation based on paper and MATLAB/GAUSS codes
"""

__version__ = "1.0.0-corrected"
__author__ = "Cho, Kim & Shin (2015) - Corrected Implementation"

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
]


def print_corrections():
    """Print all corrections made in this version"""
    print("=" * 80)
    print("QARDL PACKAGE - CRITICAL CORRECTIONS")
    print("=" * 80)
    print("\n✓ FIXED: Standard Errors")
    print("  - Now uses H_t projection formula: H_t = K_t - E[K_tW_t']E[W_tW_t']^{-1}W_t")
    print("  - Implements exact variance from Theorem 1")
    print("")
    print("✓ FIXED: Long-Run Wald Tests")
    print("  - Now uses CORRECT n² scaling (not n)")
    print("  - Test statistic: W = n²(Rβ-r)'[R(Σ⊗M⁻¹)R']⁻¹(Rβ-r)")
    print("")
    print("✓ FIXED: Short-Run Wald Tests")
    print("  - Now uses CORRECT n scaling")
    print("  - Test statistic: W = n(Rφ-r)'[RΠR']⁻¹(Rφ-r)")
    print("")
    print("✓ FIXED: ECM Representation")
    print("  - Complete implementation of Equation (6)")
    print("  - All ECM parameters: ζ, β, φ*, θ*")
    print("")
    print("✓ FIXED: Lag Selection")
    print("  - Now uses OLS-based BIC at MEAN (not quantile-based)")
    print("  - Implements icmean.m approach from MATLAB")
    print("")
    print("✓ FIXED: Rolling Estimation")
    print("  - Complete implementation with ALL parameters")
    print("  - Matches rolling_qardl from GAUSS code")
    print("")
    print("✓ FIXED: M Matrix Computation")
    print("  - Correct formula: M = n^{-2}X'[I-W(W'W)^{-1}W']X")
    print("  - Used in long-run standard errors")
    print("=" * 80)
    print("\nAll formulas now match Cho, Kim & Shin (2015) exactly!")
    print("=" * 80)


# Print corrections when package is imported
print_corrections()
