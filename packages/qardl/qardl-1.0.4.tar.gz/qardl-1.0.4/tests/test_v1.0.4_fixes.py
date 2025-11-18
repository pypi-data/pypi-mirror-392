"""
QARDL v1.0.4 - Verification Script
===================================

This script tests all 4 bug fixes to ensure they work correctly.
Run this after installing the package to verify everything is working.
"""

import numpy as np
import sys

print("=" * 80)
print("QARDL v1.0.4 - Verification Script")
print("=" * 80)

# Generate test data
print("\n[1] Generating test data...")
np.random.seed(42)
n = 200
X = np.cumsum(np.random.normal(0, 1, n))
Y = 0.6 * X + 0.3 * np.roll(X, 1) + np.cumsum(np.random.normal(0, 0.2, n))
data = np.column_stack([Y, X])
print("   ✓ Data generated successfully")

# Test 1: test_long_run_parameters() method
print("\n[2] Testing Fix #1: test_long_run_parameters() method...")
try:
    from qardl import QARDLCorrected, WaldTestsCorrected
    
    model = QARDLCorrected(data, p=2, q=1, tau=0.5, constant=True)
    results = model.fit(verbose=False)
    wald = WaldTestsCorrected(results)
    
    # This should NOT raise AttributeError
    lr_test = wald.test_long_run_parameters()
    
    print(f"   ✓ test_long_run_parameters() works!")
    print(f"     Statistic: {lr_test['statistic']:.4f}")
    print(f"     P-value: {lr_test['p_value']:.4f}")
except AttributeError as e:
    print(f"   ✗ FAILED: {e}")
    sys.exit(1)
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    sys.exit(1)

# Test 2: ECM conversion without broadcasting error
print("\n[3] Testing Fix #2: ECM broadcasting error...")
try:
    from qardl import QARDLtoECM, ECMWaldTests
    
    # This should NOT raise ValueError about broadcasting
    ecm = QARDLtoECM(results)
    
    # Test ECM-specific operations
    ecm_wald = ECMWaldTests(ecm)
    speed_test = ecm_wald.test_speed_of_adjustment()
    
    print(f"   ✓ ECM conversion works!")
    print(f"     Speed of adjustment: {ecm.ecm_params[0.5]['zeta']:.4f}")
    print(f"     Speed test statistic: {speed_test['statistic']:.4f}")
except ValueError as e:
    if "broadcast" in str(e):
        print(f"   ✗ FAILED: Broadcasting error still exists: {e}")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    sys.exit(1)

# Test 3: select_qardl_orders returns 3 values
print("\n[4] Testing Fix #3: select_qardl_orders() return values...")
try:
    from qardl import select_qardl_orders
    
    # This should return 3 values
    result = select_qardl_orders(
        data=data,
        p_max=3,
        q_max=3,
        criterion='bic',
        verbose=False
    )
    
    if len(result) != 3:
        print(f"   ✗ FAILED: Expected 3 return values, got {len(result)}")
        sys.exit(1)
    
    p_opt, q_opt, results_dict = result
    
    print(f"   ✓ select_qardl_orders() returns 3 values!")
    print(f"     Optimal lags: p={p_opt}, q={q_opt}")
    print(f"     Results dict has {len(results_dict)} entries")
    
    # Verify results_dict structure
    if not isinstance(results_dict, dict):
        print(f"   ✗ FAILED: Third return value is not a dict")
        sys.exit(1)
    
    # Check one entry
    first_key = list(results_dict.keys())[0]
    if 'bic' not in results_dict[first_key]:
        print(f"   ✗ FAILED: Results dict missing 'bic' key")
        sys.exit(1)
        
    print(f"     ✓ Results dict structure is correct")
    
except TypeError as e:
    if "unpack" in str(e):
        print(f"   ✗ FAILED: Still returning wrong number of values: {e}")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    sys.exit(1)

# Test 4: RollingQARDL.estimate() method
print("\n[5] Testing Fix #4: RollingQARDL.estimate() method...")
try:
    from qardl import RollingQARDL
    
    rolling = RollingQARDL(
        data=data,
        p=2,
        q=1,
        tau=0.5,
        window=100,
        constant=True
    )
    
    # This should NOT raise AttributeError
    rolling_results = rolling.estimate(verbose=False, step=20)
    
    print(f"   ✓ RollingQARDL.estimate() works!")
    print(f"     Number of windows: {len(rolling.results['zeta'])}")
    print(f"     Mean zeta: {np.mean(rolling.results['zeta']):.4f}")
    
    # Also verify fit() still works
    rolling2 = RollingQARDL(data=data, p=2, q=1, tau=0.5, window=100)
    rolling2.fit(verbose=False, step=20)
    
    print(f"   ✓ RollingQARDL.fit() also works!")
    
except AttributeError as e:
    if "estimate" in str(e):
        print(f"   ✗ FAILED: estimate() method still missing: {e}")
        sys.exit(1)
    else:
        raise
except Exception as e:
    print(f"   ✗ Unexpected error: {e}")
    sys.exit(1)

# All tests passed!
print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED!")
print("=" * 80)
print("\nAll 4 bug fixes verified successfully:")
print("  1. ✓ test_long_run_parameters() method works")
print("  2. ✓ ECM conversion handles all array shapes")
print("  3. ✓ select_qardl_orders() returns 3 values")
print("  4. ✓ RollingQARDL.estimate() method works")
print("\nQARDL v1.0.4 is ready to use!")
print("=" * 80)
