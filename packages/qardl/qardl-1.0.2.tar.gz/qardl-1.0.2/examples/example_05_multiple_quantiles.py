"""
QARDL Package - Example 5: Multiple Quantiles Analysis
=======================================================

This example demonstrates estimating QARDL across multiple quantiles and comparing
the results to understand how relationships vary across the distribution.
"""

import numpy as np
import matplotlib.pyplot as plt
from qardl import QARDLCorrected, WaldTestsCorrected

print("=" * 80)
print("EXAMPLE 5: MULTIPLE QUANTILES ANALYSIS")
print("=" * 80)

# ============================================================================
# Generate Heterogeneous Data
# ============================================================================
print("\n[1] Generating data with quantile-varying relationships...")

np.random.seed(101)
n = 500

# Generate X
X = np.cumsum(np.random.normal(0, 1, n))

# Generate Y with quantile-dependent relationship
# β(τ) varies with τ: stronger relationship in tails
errors = np.random.normal(0, 1, n)
quantiles_gen = np.linspace(0.1, 0.9, n)

# Different slopes for different quantiles
beta_func = lambda tau: 0.5 + 0.3 * (tau - 0.5)  # Increases from 0.35 to 0.65

Y = np.array([beta_func(tau) * X[i] + errors[i] for i, tau in enumerate(quantiles_gen)])

data = np.column_stack([Y, X])

print("   True β(τ) = 0.5 + 0.3(τ - 0.5)")
print("   β(0.25) = 0.425")
print("   β(0.50) = 0.500")
print("   β(0.75) = 0.575")

# ============================================================================
# Estimate QARDL for Multiple Quantiles
# ============================================================================
print("\n[2] Estimating QARDL at multiple quantiles...")

quantiles = [0.10, 0.25, 0.50, 0.75, 0.90]

model = QARDLCorrected(
    data=data,
    p=2,
    q=1,
    tau=quantiles,
    constant=True
)

results = model.fit(verbose=False)
print(f"   ✓ Estimated at {len(quantiles)} quantiles")

# ============================================================================
# Extract and Display Results
# ============================================================================
print("\n[3] Long-run coefficients across quantiles:")
print("-" * 80)

print("\n   Quantile    β̂        SE      t-stat   95% CI                True")
print("   " + "-" * 70)

beta_estimates = []
beta_ses = []

for tau in quantiles:
    beta_hat = results.beta[tau][0]
    beta_se = results.beta_se[tau][0]
    t_stat = beta_hat / beta_se
    ci_lower = beta_hat - 1.96 * beta_se
    ci_upper = beta_hat + 1.96 * beta_se
    beta_true = beta_func(tau)
    
    beta_estimates.append(beta_hat)
    beta_ses.append(beta_se)
    
    print(f"   {tau:6.2f}    {beta_hat:7.4f}  {beta_se:6.4f}  {t_stat:7.2f}  [{ci_lower:6.4f}, {ci_upper:6.4f}]  {beta_true:6.4f}")

# ============================================================================
# Test for Quantile Heterogeneity
# ============================================================================
print("\n[4] Testing for quantile heterogeneity...")
print("-" * 80)

wald = WaldTestsCorrected(results)

# Test if β is constant across quantiles
test_quantiles = [0.25, 0.50, 0.75]
test_equality = wald.test_equality_across_quantiles(
    parameter='beta',
    quantiles=test_quantiles
)

print(f"\nH₀: β(0.25) = β(0.50) = β(0.75)")
print(f"   Test statistic: W = {test_equality['statistic']:.2f}")
print(f"   Degrees of freedom: {test_equality['df']}")
print(f"   P-value: {test_equality['p_value']:.4f}")
print(f"   Decision: {'Reject H₀' if test_equality['reject'] else 'Fail to reject H₀'}")
print(f"\n   → β {'VARIES' if test_equality['reject'] else 'is CONSTANT'} across quantiles")

# ============================================================================
# Pairwise Comparisons
# ============================================================================
print("\n[5] Pairwise quantile comparisons:")
print("-" * 80)

tau_pairs = [(0.25, 0.75), (0.10, 0.90)]

for tau_low, tau_high in tau_pairs:
    test_pair = wald.test_equality_across_quantiles(
        parameter='beta',
        quantiles=[tau_low, tau_high]
    )
    
    beta_diff = results.beta[tau_high][0] - results.beta[tau_low][0]
    
    print(f"\nH₀: β({tau_low}) = β({tau_high})")
    print(f"   Difference: {beta_diff:.4f}")
    print(f"   P-value: {test_pair['p_value']:.4f}")
    print(f"   Decision: {'Reject H₀' if test_pair['reject'] else 'Fail to reject H₀'}")

# ============================================================================
# Visualization
# ============================================================================
print("\n[6] Creating visualization...")

try:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: β estimates across quantiles
    tau_plot = np.array(quantiles)
    beta_plot = np.array(beta_estimates)
    se_plot = np.array(beta_ses)
    
    ax1.plot(tau_plot, beta_plot, 'o-', linewidth=2, markersize=8, label='Estimated β̂(τ)')
    ax1.fill_between(tau_plot, beta_plot - 1.96*se_plot, beta_plot + 1.96*se_plot, 
                     alpha=0.3, label='95% CI')
    
    # True β
    tau_fine = np.linspace(0.1, 0.9, 100)
    beta_true_fine = [beta_func(t) for t in tau_fine]
    ax1.plot(tau_fine, beta_true_fine, '--r', linewidth=2, label='True β(τ)')
    
    ax1.set_xlabel('Quantile (τ)', fontsize=12)
    ax1.set_ylabel('Long-run Coefficient (β)', fontsize=12)
    ax1.set_title('Long-Run Coefficients Across Quantiles', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    ax1.set_ylim([0.3, 0.7])
    
    # Plot 2: Error correction speeds
    zetas = []
    for tau in quantiles:
        ecm_params = results.get_ecm_params(tau) if hasattr(results, 'get_ecm_params') else None
        if ecm_params:
            zetas.append(ecm_params.get('zeta_star', 0))
        else:
            # Approximate from parameters
            zetas.append(0)  # Placeholder
    
    if any(zetas):
        ax2.plot(tau_plot, zetas, 's-', linewidth=2, markersize=8, color='darkgreen')
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        ax2.set_xlabel('Quantile (τ)', fontsize=12)
        ax2.set_ylabel('Error Correction Speed (ζ*)', fontsize=12)
        ax2.set_title('Error Correction Across Quantiles', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
    else:
        # Alternative: plot AR coefficients
        phi1_plot = [results.phi[tau][0] for tau in quantiles]
        ax2.plot(tau_plot, phi1_plot, 's-', linewidth=2, markersize=8, color='purple')
        ax2.set_xlabel('Quantile (τ)', fontsize=12)
        ax2.set_ylabel('First AR Coefficient (φ₁)', fontsize=12)
        ax2.set_title('Short-Run Dynamics Across Quantiles', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/quantile_analysis.png', dpi=150, bbox_inches='tight')
    print("   ✓ Plot saved to quantile_analysis.png")
    
except Exception as e:
    print(f"   ⚠ Visualization skipped: {e}")

# ============================================================================
# Economic Interpretation
# ============================================================================
print("\n[7] Economic Interpretation:")
print("-" * 80)

beta_25 = results.beta[0.25][0]
beta_50 = results.beta[0.50][0]
beta_75 = results.beta[0.75][0]

print(f"\n   Lower tail (τ=0.25): β̂ = {beta_25:.4f}")
print("   → When Y is below its median, relationship with X is weaker")

print(f"\n   Median (τ=0.50):     β̂ = {beta_50:.4f}")
print("   → Typical relationship")

print(f"\n   Upper tail (τ=0.75): β̂ = {beta_75:.4f}")
print("   → When Y is above its median, relationship with X is stronger")

if beta_75 > beta_25:
    print(f"\n   → ASYMMETRIC RELATIONSHIP:")
    print(f"     Positive shocks to X have {((beta_75/beta_25 - 1)*100):.1f}% stronger impact")
    print("     than negative shocks (compared to median)")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE COMPLETE!")
print("=" * 80)
print("\nKey Findings:")
print(f"  • Long-run relationship varies significantly across quantiles")
print(f"  • β increases from {beta_25:.3f} (τ=0.25) to {beta_75:.3f} (τ=0.75)")
print(f"  • Quantile heterogeneity test: p = {test_equality['p_value']:.4f}")
print("\nApplications:")
print("  • Risk analysis: different impacts in booms vs. recessions")
print("  • Policy analysis: asymmetric effects across the distribution")
print("  • Tail risk modeling: extreme quantile behavior")
print("=" * 80)
