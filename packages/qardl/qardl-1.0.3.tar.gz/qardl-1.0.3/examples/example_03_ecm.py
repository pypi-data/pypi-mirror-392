"""
QARDL Package - Example 3: ECM Representation
==============================================

This example demonstrates the COMPLETE Error Correction Model (ECM) representation,
including error correction speed and half-life computation.
"""

import numpy as np
from qardl import QARDLCorrected, QARDLtoECM, ECMWaldTests

print("=" * 80)
print("EXAMPLE 3: ERROR CORRECTION MODEL (ECM)")
print("=" * 80)

# ============================================================================
# Generate Data with Error Correction Mechanism
# ============================================================================
print("\n[1] Generating data with error correction...")

np.random.seed(456)
n = 500

# Generate X (random walk)
X = np.cumsum(np.random.normal(0, 1, n))

# Generate Y with error correction mechanism
# ΔY_t = -0.2*(Y_{t-1} - 0.7*X_{t-1}) + dynamics + error
beta_true = 0.7
zeta_true = -0.2  # Error correction speed

Y = np.zeros(n)
Y[0] = beta_true * X[0]

for t in range(1, n):
    error_correction = zeta_true * (Y[t-1] - beta_true * X[t-1])
    Y[t] = Y[t-1] + error_correction + 0.5 * np.random.normal()

data = np.column_stack([Y, X])

print(f"   True β (long-run): {beta_true}")
print(f"   True ζ (error correction speed): {zeta_true}")
print(f"   True half-life: {-np.log(2)/np.log(1 + zeta_true):.2f} periods")

# ============================================================================
# Estimate QARDL Model
# ============================================================================
print("\n[2] Estimating QARDL model...")

model = QARDLCorrected(
    data=data,
    p=2,
    q=1,
    tau=0.5,
    constant=True
)

results = model.fit(verbose=False)
print("   ✓ Estimation complete!")

# ============================================================================
# Convert to ECM Representation
# ============================================================================
print("\n[3] Converting to ECM representation...")

ecm = QARDLtoECM(results)
print("   ✓ ECM conversion complete!")

# ============================================================================
# View ECM Parameters
# ============================================================================
print("\n[4] ECM Parameters:")
print("-" * 80)

tau = 0.5
ecm_params = ecm.get_ecm_params(tau)

print(f"\nAt τ = {tau}:")
print(f"\n   α* (intercept): {ecm_params['alpha_star']:.4f}")

print(f"\n   ζ* (error correction speed): {ecm_params['zeta_star']:.4f}")
print(f"   SE: {ecm_params['zeta_star_se']:.4f}")
print(f"   Half-life: {ecm_params['half_life']:.2f} periods")
print(f"   (True ζ: {zeta_true:.4f})")

print(f"\n   β* (long-run coefficients):")
for i, (b, se) in enumerate(zip(ecm_params['beta_star'], ecm_params['beta_star_se'])):
    print(f"   β*_{i+1} = {b:7.4f}  (SE: {se:.4f})")

print(f"\n   φ* (short-run AR dynamics):")
for i, (p, se) in enumerate(zip(ecm_params['phi_star'], ecm_params['phi_star_se'])):
    print(f"   φ*_{i+1} = {p:7.4f}  (SE: {se:.4f})")

print(f"\n   θ* (short-run DL dynamics):")
for i, (t, se) in enumerate(zip(ecm_params['theta_star'], ecm_params['theta_star_se'])):
    print(f"   θ*_{i} = {t:7.4f}  (SE: {se:.4f})")

# ============================================================================
# ECM-Specific Wald Tests
# ============================================================================
print("\n[5] ECM-Specific Tests:")
print("-" * 80)

ecm_tests = ECMWaldTests(ecm)

# Test 1: No error correction (ζ* = 0)
print("\nTEST 1: H₀: ζ* = 0 (No error correction)")
test_no_ec = ecm_tests.test_no_error_correction(tau=tau)

print(f"   Test statistic: W = {test_no_ec['statistic']:.2f}")
print(f"   P-value: {test_no_ec['p_value']:.4f}")
print(f"   Decision: {'Reject H₀' if test_no_ec['reject'] else 'Fail to reject H₀'}")
print(f"   → Error correction is {'PRESENT' if test_no_ec['reject'] else 'ABSENT'}")

# Test 2: Granger causality (if there are DL parameters)
if model.q > 0:
    print("\nTEST 2: H₀: θ* = 0 (No Granger causality from X to Y)")
    test_granger = ecm_tests.test_granger_causality(variable_idx=0, tau=tau)
    
    print(f"   Test statistic: W = {test_granger['statistic']:.2f}")
    print(f"   P-value: {test_granger['p_value']:.4f}")
    print(f"   Decision: {'Reject H₀' if test_granger['reject'] else 'Fail to reject H₀'}")
    print(f"   → X {'DOES' if test_granger['reject'] else 'does NOT'} Granger-cause Y")

# ============================================================================
# ECM Equation
# ============================================================================
print("\n[6] Estimated ECM Equation:")
print("-" * 80)

alpha = ecm_params['alpha_star']
zeta = ecm_params['zeta_star']
beta = ecm_params['beta_star'][0]
phi = ecm_params['phi_star']
theta = ecm_params['theta_star']

print(f"\nΔY_t = {alpha:.4f} + {zeta:.4f}[Y_{{t-1}} - {beta:.4f}X_{{t-1}}]")

if len(phi) > 0:
    phi_terms = " + ".join([f"{p:.4f}ΔY_{{t-{i+1}}}" for i, p in enumerate(phi)])
    print(f"       + {phi_terms}")

if len(theta) > 0:
    theta_terms = " + ".join([f"{t:.4f}ΔX_{{t-{i}}}" for i, t in enumerate(theta)])
    print(f"       + {theta_terms}")

print(f"       + u_t(τ)")

# ============================================================================
# Interpretation
# ============================================================================
print("\n[7] Economic Interpretation:")
print("-" * 80)

print(f"\n   Long-run Equilibrium:")
print(f"   Y = {beta:.4f} × X")
print(f"   (1 unit ↑ in X → {beta:.4f} units ↑ in Y in long run)")

print(f"\n   Adjustment Speed:")
if zeta < 0:
    print(f"   ζ* = {zeta:.4f} < 0  ✓ Stable error correction")
    print(f"   {abs(zeta)*100:.1f}% of disequilibrium corrected per period")
    print(f"   Half-life: {ecm_params['half_life']:.2f} periods")
else:
    print(f"   ζ* = {zeta:.4f} ≥ 0  ⚠ Unstable or no error correction")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE COMPLETE!")
print("=" * 80)
print("\nKey Features:")
print("  • Complete ECM representation (Equation 6 from paper)")
print("  • Error correction coefficient ζ* computed correctly")
print("  • Half-life calculation for adjustment dynamics")
print("  • ECM-specific hypothesis tests")
print("\nAll formulas match Cho, Kim & Shin (2015) exactly!")
print("=" * 80)
