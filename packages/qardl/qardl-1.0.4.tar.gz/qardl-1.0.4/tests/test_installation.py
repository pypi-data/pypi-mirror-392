"""
QARDL Package - Verification Test
==================================

Quick test to verify the package is installed correctly and all fixes are working.
"""

import numpy as np
import sys

print("=" * 80)
print("QARDL PACKAGE - VERIFICATION TEST")
print("=" * 80)

# Test 1: Import
print("\n[TEST 1] Checking imports...")
try:
    from qardl import (
        QARDLCorrected,
        WaldTestsCorrected,
        QARDLtoECM,
        ECMWaldTests,
        select_qardl_orders,
        RollingQARDL
    )
    print("   ✓ All imports successful!")
except ImportError as e:
    print(f"   ✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Basic Estimation
print("\n[TEST 2] Testing basic estimation...")
try:
    np.random.seed(42)
    n = 300
    X = np.cumsum(np.random.normal(0, 1, n))
    Y = 0.5 * X + np.random.normal(0, 0.5, n)
    data = np.column_stack([Y, X])
    
    model = QARDLCorrected(data=data, p=2, q=1, tau=0.5, constant=True)
    results = model.fit(verbose=False)
    
    beta = results.beta[0.5][0]
    assert 0.3 < beta < 0.7, f"β̂={beta:.4f} out of expected range"
    print(f"   ✓ Estimation works! β̂ = {beta:.4f}")
except Exception as e:
    print(f"   ✗ Estimation failed: {e}")
    sys.exit(1)

# Test 3: Wald Tests
print("\n[TEST 3] Testing Wald tests...")
try:
    wald = WaldTestsCorrected(results)
    
    R = np.array([[1]])
    r = np.array([0])
    test = wald.wtestlrb(R, r, tau=0.5)
    
    assert 'statistic' in test, "Missing test statistic"
    assert 'p_value' in test, "Missing p-value"
    print(f"   ✓ Wald tests work! W = {test['statistic']:.2f}, p = {test['p_value']:.4f}")
except Exception as e:
    print(f"   ✗ Wald tests failed: {e}")
    sys.exit(1)

# Test 4: ECM
print("\n[TEST 4] Testing ECM conversion...")
try:
    ecm = QARDLtoECM(results)
    ecm_params = ecm.get_ecm_params(0.5)
    
    assert 'zeta_star' in ecm_params, "Missing error correction speed"
    assert 'half_life' in ecm_params, "Missing half-life"
    print(f"   ✓ ECM works! ζ* = {ecm_params['zeta_star']:.4f}")
except Exception as e:
    print(f"   ✗ ECM failed: {e}")
    sys.exit(1)

# Test 5: Lag Selection
print("\n[TEST 5] Testing lag selection...")
try:
    p_opt, q_opt = select_qardl_orders(
        data=data,
        p_max=3,
        q_max=3,
        criterion='bic',
        verbose=False
    )
    
    assert isinstance(p_opt, int), "p_opt not integer"
    assert isinstance(q_opt, int), "q_opt not integer"
    assert 1 <= p_opt <= 3, "p_opt out of range"
    assert 0 <= q_opt <= 3, "q_opt out of range"
    print(f"   ✓ Lag selection works! Selected: p={p_opt}, q={q_opt}")
except Exception as e:
    print(f"   ✗ Lag selection failed: {e}")
    sys.exit(1)

# Test 6: Rolling Estimation
print("\n[TEST 6] Testing rolling estimation...")
try:
    rolling = RollingQARDL(
        data=data,
        p=2,
        q=1,
        tau=0.5,
        window=100,
        constant=True
    )
    
    rolling.fit(step=50, verbose=False)  # Use large step for speed
    
    beta_series = rolling.get_parameter_series('beta', variable_idx=0)
    
    assert len(beta_series['estimate']) > 0, "No rolling estimates"
    print(f"   ✓ Rolling estimation works! {len(beta_series['estimate'])} windows")
except Exception as e:
    print(f"   ✗ Rolling estimation failed: {e}")
    sys.exit(1)

# Test 7: Multiple Quantiles
print("\n[TEST 7] Testing multiple quantiles...")
try:
    model_multi = QARDLCorrected(
        data=data,
        p=2,
        q=1,
        tau=[0.25, 0.5, 0.75],
        constant=True
    )
    
    results_multi = model_multi.fit(verbose=False)
    
    assert 0.25 in results_multi.beta, "Missing τ=0.25"
    assert 0.50 in results_multi.beta, "Missing τ=0.50"
    assert 0.75 in results_multi.beta, "Missing τ=0.75"
    print("   ✓ Multiple quantiles work!")
    
    # Test equality across quantiles
    wald_multi = WaldTestsCorrected(results_multi)
    test_eq = wald_multi.test_equality_across_quantiles('beta', [0.25, 0.5, 0.75])
    
    assert 'statistic' in test_eq, "Missing test statistic"
    print(f"   ✓ Multi-quantile tests work! W = {test_eq['statistic']:.2f}")
except Exception as e:
    print(f"   ✗ Multiple quantiles failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("ALL TESTS PASSED! ✓")
print("=" * 80)
print("\nPackage is correctly installed and all features are working!")
print("\nYou can now:")
print("  • Run the example scripts: python example_01_basic_qardl.py")
print("  • Use the package in your own code")
print("  • Read README_CORRECTED.md for full documentation")
print("\nEnjoy using the CORRECTED QARDL package!")
print("=" * 80)
