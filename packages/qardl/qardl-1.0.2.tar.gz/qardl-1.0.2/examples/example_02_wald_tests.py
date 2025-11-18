"""
QARDL Package - Example 2: Wald Tests
======================================

This example demonstrates hypothesis testing using CORRECTED Wald tests:
- Long-run tests (n² scaling)
- Short-run tests (n scaling)
- Multi-quantile tests
"""

import numpy as np
from qardl import QARDLCorrected, WaldTestsCorrected

print("=" * 80)
print("EXAMPLE 2: WALD TESTS WITH CORRECT SCALING")
print("=" * 80)

# ============================================================================
# Generate Data
# ============================================================================
print("\n[1] Generating simulated data...")

np.random.seed(123)
n = 400

# Generate X (random walk)
X = np.cumsum(np.random.normal(0, 1, n))

# Generate Y cointegrated with X
# Y_t = α + 0.6*X_t + dynamics + error
beta_true = 0.6
Y = 1.0 + beta_true * X + 0.3 * np.roll(X, 1) + np.random.normal(0, 0.5, n)

data = np.column_stack([Y, X])
print(f"   True β: {beta_true}")

# ============================================================================
# Estimate Model
# ============================================================================
print("\n[2] Estimating QARDL model...")

model = QARDLCorrected(
    data=data,
    p=2,
    q=1,
    tau=[0.25, 0.5, 0.75],  # Multiple quantiles
    constant=True
)

results = model.fit(verbose=False)
print("   ✓ Estimation complete!")

# ============================================================================
# Initialize Wald Tests
# ============================================================================
print("\n[3] Setting up Wald tests...")

wald = WaldTestsCorrected(results)
print("   ✓ Test framework ready")

# ============================================================================
# TEST 1: Long-Run Coefficient = 0 (uses n² scaling)
# ============================================================================
print("\n" + "-" * 80)
print("TEST 1: H₀: β = 0 (Long-run relationship test)")
print("-" * 80)

tau = 0.5  # Test at median

# Restriction matrix R and vector r
# For testing β₁ = 0: R = [1, 0, ...], r = [0]
k = 1  # Number of X variables
R = np.zeros((1, k))
R[0, 0] = 1
r = np.array([0])

test_beta = wald.wtestlrb(R, r, tau=tau)

print(f"\nAt τ = {tau}:")
print(f"   Test statistic: W = {test_beta['statistic']:.2f}")
print(f"   Critical value (5%): {test_beta['critical_value']:.2f}")
print(f"   P-value: {test_beta['p_value']:.4f}")
print(f"   Decision: {'Reject H₀' if test_beta['reject'] else 'Fail to reject H₀'}")
print(f"\n   → {'Strong' if test_beta['reject'] else 'No'} evidence of cointegration")
print(f"   ✓ Using n² scaling (correct for long-run parameters)")

# ============================================================================
# TEST 2: Short-Run AR Parameter = 0 (uses n scaling)
# ============================================================================
print("\n" + "-" * 80)
print("TEST 2: H₀: φ₁ = 0 (First AR parameter test)")
print("-" * 80)

# Restriction for φ₁ = 0
Q = np.zeros((1, model.p))
Q[0, 0] = 1
q = np.array([0])

test_phi = wald.wtestsrp(Q, q, tau=tau)

print(f"\nAt τ = {tau}:")
print(f"   Test statistic: W = {test_phi['statistic']:.2f}")
print(f"   Critical value (5%): {test_phi['critical_value']:.2f}")
print(f"   P-value: {test_phi['p_value']:.4f}")
print(f"   Decision: {'Reject H₀' if test_phi['reject'] else 'Fail to reject H₀'}")
print(f"\n   ✓ Using n scaling (correct for short-run parameters)")

# ============================================================================
# TEST 3: Equality Across Quantiles
# ============================================================================
print("\n" + "-" * 80)
print("TEST 3: H₀: β(0.25) = β(0.5) = β(0.75) (Quantile equality)")
print("-" * 80)

quantiles = [0.25, 0.5, 0.75]
test_equality = wald.test_equality_across_quantiles(
    parameter='beta',
    quantiles=quantiles
)

print(f"\n   Test statistic: W = {test_equality['statistic']:.2f}")
print(f"   Degrees of freedom: {test_equality['df']}")
print(f"   P-value: {test_equality['p_value']:.4f}")
print(f"   Decision: {'Reject H₀' if test_equality['reject'] else 'Fail to reject H₀'}")
print(f"\n   → Long-run relationship is {'NOT constant' if test_equality['reject'] else 'constant'} across quantiles")

# ============================================================================
# TEST 4: Joint Test - Multiple Restrictions
# ============================================================================
print("\n" + "-" * 80)
print("TEST 4: H₀: φ₁ = φ₂ = 0 (Joint AR test)")
print("-" * 80)

# Test both AR parameters = 0
Q_joint = np.eye(model.p)  # Identity matrix for all AR parameters
q_joint = np.zeros(model.p)

test_joint = wald.wtestsrp(Q_joint, q_joint, tau=0.5)

print(f"\n   Test statistic: W = {test_joint['statistic']:.2f}")
print(f"   Critical value (5%): {test_joint['critical_value']:.2f}")
print(f"   P-value: {test_joint['p_value']:.4f}")
print(f"   Decision: {'Reject H₀' if test_joint['reject'] else 'Fail to reject H₀'}")
print(f"\n   → Past values {'ARE' if test_joint['reject'] else 'are NOT'} jointly significant")

# ============================================================================
# Compare Results Across Quantiles
# ============================================================================
print("\n" + "-" * 80)
print("COMPARISON: β estimates across quantiles")
print("-" * 80)

print("\n   Quantile    β̂      SE    t-stat   95% CI")
print("   " + "-" * 50)

for tau_val in quantiles:
    beta_hat = results.beta[tau_val][0]
    beta_se = results.beta_se[tau_val][0]
    t_stat = beta_hat / beta_se
    ci_lower = beta_hat - 1.96 * beta_se
    ci_upper = beta_hat + 1.96 * beta_se
    
    print(f"   {tau_val:6.2f}    {beta_hat:6.3f}  {beta_se:5.3f}  {t_stat:6.2f}  [{ci_lower:5.3f}, {ci_upper:5.3f}]")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE COMPLETE!")
print("=" * 80)
print("\nKey Corrections Applied:")
print("  • Long-run tests use n² scaling (Corollary 1)")
print("  • Short-run tests use n scaling (Corollaries 2, 3)")
print("  • Multi-quantile tests use proper Θ(τ) covariance (Corollary 4)")
print("\nAll formulas match Cho, Kim & Shin (2015) exactly!")
print("=" * 80)
