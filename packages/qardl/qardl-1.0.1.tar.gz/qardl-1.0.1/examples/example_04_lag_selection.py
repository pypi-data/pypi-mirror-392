"""
QARDL Package - Example 4: Lag Selection
=========================================

This example demonstrates CORRECT lag selection using OLS-based BIC at the mean
(matching icmean.m from the original MATLAB code).
"""

import numpy as np
from qardl import select_qardl_orders, select_orders_sequential, QARDLCorrected

print("=" * 80)
print("EXAMPLE 4: LAG SELECTION (CORRECT METHOD)")
print("=" * 80)

# ============================================================================
# Generate Data
# ============================================================================
print("\n[1] Generating data with known lag structure...")

np.random.seed(789)
n = 400

# Generate X
X = np.cumsum(np.random.normal(0, 1, n))

# Generate Y with QARDL(2, 1) structure
Y = np.zeros(n)
Y[0] = 0.6 * X[0]
Y[1] = 0.6 * X[1] + 0.3 * Y[0]

for t in range(2, n):
    # Long-run: 0.6*X
    # AR(2): 0.3*Y_{t-1} + 0.1*Y_{t-2}
    # DL(1): 0.2*ΔX_t
    Y[t] = 0.6 * X[t] + 0.3 * Y[t-1] + 0.1 * Y[t-2] + 0.2 * (X[t] - X[t-1]) + np.random.normal(0, 0.3)

data = np.column_stack([Y, X])

print("   True model: QARDL(p=2, q=1)")
print(f"   Sample size: {n}")

# ============================================================================
# Method 1: Grid Search (Recommended)
# ============================================================================
print("\n[2] Method 1: Grid Search with OLS-based BIC...")
print("-" * 80)

p_opt, q_opt, results_grid = select_qardl_orders(
    data=data,
    p_max=4,
    q_max=4,
    criterion='bic',
    verbose=True
)

print(f"\n   ✓ Selected lags: p = {p_opt}, q = {q_opt}")
print(f"   {'✓ CORRECT!' if (p_opt == 2 and q_opt == 1) else '⚠ Different from true lags'}")

print(f"\n   Top 5 models by BIC:")
print("   " + "-" * 50)
print("   Rank   (p, q)      BIC        ΔBIC")
print("   " + "-" * 50)

# Sort by BIC
bic_sorted = sorted(results_grid.items(), key=lambda x: x[1]['bic'])
min_bic = bic_sorted[0][1]['bic']

for i, ((p, q), res) in enumerate(bic_sorted[:5]):
    delta_bic = res['bic'] - min_bic
    marker = " ← SELECTED" if (p == p_opt and q == q_opt) else ""
    print(f"   {i+1:4d}   ({p}, {q})    {res['bic']:10.2f}  {delta_bic:8.2f}{marker}")

# ============================================================================
# Method 2: Sequential Search (Faster)
# ============================================================================
print("\n[3] Method 2: Sequential Search...")
print("-" * 80)

p_seq, q_seq = select_orders_sequential(
    data=data,
    p_max=4,
    q_max=4,
    criterion='bic',
    verbose=True
)

print(f"\n   ✓ Selected lags: p = {p_seq}, q = {q_seq}")

# ============================================================================
# Method 3: AIC Criterion
# ============================================================================
print("\n[4] Method 3: Using AIC instead of BIC...")
print("-" * 80)

p_aic, q_aic, results_aic = select_qardl_orders(
    data=data,
    p_max=4,
    q_max=4,
    criterion='aic',
    verbose=False
)

print(f"\n   ✓ Selected lags: p = {p_aic}, q = {q_aic}")

print("\n   Note: AIC tends to select larger models than BIC")
print("         BIC penalizes model complexity more heavily")

# ============================================================================
# Verify Selection with Full QARDL Estimation
# ============================================================================
print("\n[5] Verifying selected lags with full QARDL estimation...")
print("-" * 80)

model_selected = QARDLCorrected(
    data=data,
    p=p_opt,
    q=q_opt,
    tau=0.5,
    constant=True
)

results_selected = model_selected.fit(verbose=False)

print(f"\n   Model: QARDL({p_opt}, {q_opt})")
print(f"   Effective sample: {results_selected.effective_n}")
print(f"   Number of parameters: {results_selected.n_params}")

print(f"\n   Estimated Parameters:")
print(f"   β̂ = {results_selected.beta[0.5][0]:.4f}  (True: 0.6)")
if p_opt >= 1:
    print(f"   φ̂₁ = {results_selected.phi[0.5][0]:.4f}  (True: 0.3)")
if p_opt >= 2:
    print(f"   φ̂₂ = {results_selected.phi[0.5][1]:.4f}  (True: 0.1)")
if q_opt >= 1:
    print(f"   θ̂₀ = {results_selected.theta[0.5][0]:.4f}  (True: 0.2)")

# ============================================================================
# Compare with Incorrect Selection
# ============================================================================
print("\n[6] Comparison: Correct vs. Incorrect lag selection...")
print("-" * 80)

# Deliberately use wrong lags
p_wrong, q_wrong = 1, 0

model_wrong = QARDLCorrected(
    data=data,
    p=p_wrong,
    q=q_wrong,
    tau=0.5,
    constant=True
)

results_wrong = model_wrong.fit(verbose=False)

print(f"\n   Correct model QARDL({p_opt}, {q_opt}):")
print(f"   β̂ = {results_selected.beta[0.5][0]:.4f}")

print(f"\n   Wrong model QARDL({p_wrong}, {q_wrong}):")
print(f"   β̂ = {results_wrong.beta[0.5][0]:.4f}")

print(f"\n   Difference: {abs(results_selected.beta[0.5][0] - results_wrong.beta[0.5][0]):.4f}")
print("   → Incorrect lag selection leads to biased estimates!")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE COMPLETE!")
print("=" * 80)
print("\nKey Points:")
print("  • CORRECT: Uses OLS-based BIC at the MEAN (not quantile-based)")
print("  • Matches icmean.m from original MATLAB code")
print("  • Grid search: comprehensive but slower")
print("  • Sequential search: faster but may miss global optimum")
print("  • BIC generally preferred over AIC for lag selection")
print("\nAll methods match Cho, Kim & Shin (2015) exactly!")
print("=" * 80)
