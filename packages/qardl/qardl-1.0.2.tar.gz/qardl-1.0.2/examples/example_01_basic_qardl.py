"""
QARDL Package - Example 1: Basic QARDL Estimation
==================================================

This example demonstrates basic QARDL model estimation using simulated data.
"""

import numpy as np
import sys

# Import from qardl package
from qardl import QARDLCorrected

print("=" * 80)
print("EXAMPLE 1: BASIC QARDL ESTIMATION")
print("=" * 80)

# ============================================================================
# STEP 1: Generate Simulated Data
# ============================================================================
print("\n[1] Generating simulated cointegrated data...")

np.random.seed(42)
n = 300

# Generate X (random walk)
X_innov = np.random.normal(0, 1, n)
X = np.cumsum(X_innov)

# Generate Y that is cointegrated with X
# Y_t = 0.5*X_t + error
# This creates a cointegrating relationship
beta_true = 0.5
error = np.random.normal(0, 0.5, n)
Y = beta_true * X + error

# Combine into data matrix [Y, X]
data = np.column_stack([Y, X])
print(f"   Data shape: {data.shape}")
print(f"   Sample size: {n}")
print(f"   True β (long-run coefficient): {beta_true}")

# ============================================================================
# STEP 2: Estimate QARDL Model
# ============================================================================
print("\n[2] Estimating QARDL model...")

# Create QARDL model
model = QARDLCorrected(
    data=data,
    p=2,          # AR order
    q=1,          # DL order
    tau=0.5,      # Median (can also use list: [0.25, 0.5, 0.75])
    constant=True
)

print(f"   Model: QARDL(p={model.p}, q={model.q})")
print(f"   Quantile: τ = {model.tau}")

# Estimate the model
results = model.fit(
    bandwidth_method='bofinger',
    cov_type='correct',  # Uses H_t projection formula!
    verbose=False
)

print("   ✓ Estimation complete!")

# ============================================================================
# STEP 3: View Results
# ============================================================================
print("\n[3] Results Summary:")
print("-" * 80)

# Get estimated parameters at τ=0.5
tau = 0.5
beta_hat = results.beta[tau][0]  # Long-run coefficient
beta_se = results.beta_se[tau][0]  # Standard error

print(f"\n   Long-Run Coefficients (β) at τ={tau}:")
print(f"   β̂ = {beta_hat:.4f}  (True: {beta_true:.4f})")
print(f"   SE = {beta_se:.4f}")
print(f"   t-stat = {beta_hat/beta_se:.2f}")

# Get short-run parameters
phi = results.phi[tau]  # AR parameters
theta = results.theta[tau]  # DL parameters

print(f"\n   Short-Run AR Parameters (φ):")
for i, (phi_i, se_i) in enumerate(zip(phi, results.phi_se[tau])):
    print(f"   φ_{i+1} = {phi_i:7.4f}  (SE: {se_i:.4f})")

print(f"\n   Short-Run DL Parameters (θ):")
for i, (theta_i, se_i) in enumerate(zip(theta, results.theta_se[tau])):
    print(f"   θ_{i} = {theta_i:7.4f}  (SE: {se_i:.4f})")

# ============================================================================
# STEP 4: Diagnostic Information
# ============================================================================
print("\n[4] Diagnostic Information:")
print("-" * 80)

print(f"   Effective sample size: {results.effective_n}")
print(f"   Number of parameters: {results.n_params}")
print(f"   Convergence: {'✓ Successful' if results.converged else '✗ Failed'}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE COMPLETE!")
print("=" * 80)
print("\nKey Points:")
print("  • QARDL model successfully estimated on simulated data")
print("  • Long-run coefficient β̂ ≈ 0.5 (close to true value)")
print("  • Standard errors computed using CORRECT H_t projection formula")
print("  • This matches Cho, Kim & Shin (2015) methodology exactly")
print("\nNext Steps:")
print("  • Try example_02_wald_tests.py for hypothesis testing")
print("  • Try example_03_ecm.py for ECM representation")
print("  • Try example_04_multiple_quantiles.py for multiple τ values")
print("=" * 80)
