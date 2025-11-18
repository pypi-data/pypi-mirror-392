"""
Complete test script for the updated QARDL package API

Run this after updating all files to ensure everything works correctly.
"""

import numpy as np
import pandas as pd
from qardl import (
    QARDLCorrected,
    select_qardl_orders,
    RollingQARDL,
    compare_quantiles_rolling,
    WaldTestsCorrected,
    QARDLtoECM,
    evaluate_order_stability
)

print("=" * 80)
print("QARDL PACKAGE API TEST SUITE")
print("=" * 80)

# Generate sample data
np.random.seed(42)
n = 200
y = np.cumsum(np.random.normal(0, 1, n))
X = np.cumsum(np.random.normal(0, 1, (n, 2)), axis=0)

print("\n" + "=" * 80)
print("TEST 1: Basic QARDL Estimation with NumPy Arrays")
print("=" * 80)
try:
    model = QARDLCorrected(y, X, p=2, q=1, tau=0.5)
    results = model.fit()
    print(results.summary())
    print("✓ TEST 1 PASSED")
except Exception as e:
    print(f"✗ TEST 1 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 2: Multi-Quantile Estimation")
print("=" * 80)
try:
    model_multi = QARDLCorrected(y, X, p=2, q=1, tau=[0.25, 0.50, 0.75])
    results_multi = model_multi.fit()
    print(results_multi.summary())
    print("✓ TEST 2 PASSED")
except Exception as e:
    print(f"✗ TEST 2 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 3: Pandas DataFrame/Series Input")
print("=" * 80)
try:
    df = pd.DataFrame({
        'Y': y,
        'X1': X[:, 0],
        'X2': X[:, 1]
    })
    model_pd = QARDLCorrected(
        y=df['Y'], 
        X=df[['X1', 'X2']], 
        p=2, 
        q=1, 
        tau=0.5
    )
    results_pd = model_pd.fit()
    print(results_pd.summary())
    print("✓ TEST 3 PASSED")
except Exception as e:
    print(f"✗ TEST 3 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 4: Lag Selection")
print("=" * 80)
try:
    p_opt, q_opt = select_qardl_orders(
        y, X, 
        p_max=4, 
        q_max=4, 
        verbose=True
    )
    print(f"\nOptimal orders: p={p_opt}, q={q_opt}")
    print("✓ TEST 4 PASSED")
except Exception as e:
    print(f"✗ TEST 4 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 5: Stability Evaluation")
print("=" * 80)
try:
    stability = evaluate_order_stability(y, X, p=2, q=1)
    print(f"Stability check: {stability['message']}")
    print("✓ TEST 5 PASSED")
except Exception as e:
    print(f"✗ TEST 5 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 6: Wald Tests")
print("=" * 80)
try:
    model = QARDLCorrected(y, X, p=2, q=1, tau=0.5)
    results = model.fit(verbose=False)
    
    wald = WaldTestsCorrected(results)
    
    # Test long-run parameter = 0
    R = np.array([[1, 0]])  # Test first variable
    r = np.array([0])
    test_result = wald.wtestlrb(R, r, tau=0.5)
    print(f"Long-run Wald test: statistic={test_result['statistic']:.4f}, "
          f"p-value={test_result['p_value']:.4f}")
    print("✓ TEST 6 PASSED")
except Exception as e:
    print(f"✗ TEST 6 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 7: ECM Representation")
print("=" * 80)
try:
    model = QARDLCorrected(y, X, p=2, q=1, tau=0.5)
    results = model.fit(verbose=False)
    
    ecm = QARDLtoECM(results)
    print(ecm.summary_ecm(tau=0.5))
    print("✓ TEST 7 PASSED")
except Exception as e:
    print(f"✗ TEST 7 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 8: Rolling QARDL")
print("=" * 80)
try:
    rolling = RollingQARDL(
        y=y, 
        X=X, 
        p=2, 
        q=1, 
        tau=0.5, 
        window=50,
        min_periods=50
    )
    rolling.fit(verbose=True)
    print(rolling.summary())
    print("✓ TEST 8 PASSED")
except Exception as e:
    print(f"✗ TEST 8 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 9: Compare Quantiles Rolling")
print("=" * 80)
try:
    results_dict = compare_quantiles_rolling(
        y=y,
        X=X,
        p=2,
        q=1,
        quantiles=[0.25, 0.5, 0.75],
        window=50
    )
    print(f"Completed rolling estimation for {len(results_dict)} quantiles")
    for tau, rolling_res in results_dict.items():
        print(f"  τ={tau}: {len(rolling_res.results['dates'])} windows")
    print("✓ TEST 9 PASSED")
except Exception as e:
    print(f"✗ TEST 9 FAILED: {e}")

print("\n" + "=" * 80)
print("TEST 10: Single Variable X")
print("=" * 80)
try:
    X_single = X[:, 0]  # Single variable
    model_single = QARDLCorrected(y, X_single, p=2, q=1, tau=0.5)
    results_single = model_single.fit(verbose=False)
    print(results_single.summary())
    print("✓ TEST 10 PASSED")
except Exception as e:
    print(f"✗ TEST 10 FAILED: {e}")

print("\n" + "=" * 80)
print("FINAL TEST SUMMARY")
print("=" * 80)
print("All basic API tests completed!")
print("If all tests passed (✓), your package is ready for PyPI publication.")
print("\nNext steps:")
print("1. Update setup.py with version 1.0.3")
print("2. Update README.md with new API examples")
print("3. Run full test suite: pytest tests/")
print("4. Build package: python setup.py sdist bdist_wheel")
print("5. Upload to PyPI: twine upload dist/*")
print("=" * 80)
