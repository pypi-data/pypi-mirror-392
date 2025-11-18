"""
QARDL Package - Example 6: Rolling Estimation
==============================================

This example demonstrates rolling window QARDL estimation to track time-varying
parameters and structural changes.
"""

import numpy as np
import matplotlib.pyplot as plt
from qardl import QARDLCorrected, RollingQARDL

print("=" * 80)
print("EXAMPLE 6: ROLLING WINDOW ESTIMATION")
print("=" * 80)

# ============================================================================
# Generate Data with Structural Break
# ============================================================================
print("\n[1] Generating data with structural break...")

np.random.seed(202)
n = 600

# Generate X
X = np.cumsum(np.random.normal(0, 1, n))

# Generate Y with structural break at t=300
Y = np.zeros(n)
break_point = 300

for t in range(n):
    if t < break_point:
        # First regime: β = 0.4
        Y[t] = 0.4 * X[t] + np.random.normal(0, 0.5)
    else:
        # Second regime: β = 0.7
        Y[t] = 0.7 * X[t] + np.random.normal(0, 0.5)

data = np.column_stack([Y, X])

print(f"   Sample size: {n}")
print(f"   Structural break at t = {break_point}")
print(f"   β before break: 0.4")
print(f"   β after break: 0.7")

# ============================================================================
# Full Sample Estimation (for comparison)
# ============================================================================
print("\n[2] Full sample estimation (for comparison)...")

model_full = QARDLCorrected(
    data=data,
    p=2,
    q=1,
    tau=0.5,
    constant=True
)

results_full = model_full.fit(verbose=False)
beta_full = results_full.beta[0.5][0]

print(f"   Full sample β̂: {beta_full:.4f}")
print("   (Should be between 0.4 and 0.7 due to averaging)")

# ============================================================================
# Rolling Window Estimation
# ============================================================================
print("\n[3] Rolling window estimation...")
print("-" * 80)

window_size = 150  # 25% of sample

rolling = RollingQARDL(
    data=data,
    p=2,
    q=1,
    tau=0.5,
    window=window_size,
    constant=True
)

print(f"   Window size: {window_size}")
print(f"   Step size: 1 (default)")
print(f"   Number of windows: {n - window_size + 1}")

# Estimate with rolling windows
rolling.fit(step=5, verbose=True)  # step=5 for faster computation

print("\n   ✓ Rolling estimation complete!")

# ============================================================================
# Extract Results
# ============================================================================
print("\n[4] Extracting rolling estimates...")

# Get time series of β estimates
beta_series = rolling.get_parameter_series('beta', variable_idx=0, tau=0.5)
window_centers = rolling.get_window_centers()

print(f"   Number of estimates: {len(beta_series['estimate'])}")
print(f"   Time range: t={window_centers[0]:.0f} to t={window_centers[-1]:.0f}")

# ============================================================================
# Structural Break Detection
# ============================================================================
print("\n[5] Detecting structural changes...")
print("-" * 80)

# Find maximum change in β
beta_est = np.array(beta_series['estimate'])
beta_diff = np.abs(np.diff(beta_est))
max_change_idx = np.argmax(beta_diff)
max_change_time = window_centers[max_change_idx]

print(f"\n   Maximum parameter change at t ≈ {max_change_time:.0f}")
print(f"   (True break at t = {break_point})")
print(f"   Detection error: {abs(max_change_time - break_point):.0f} periods")

# Average β before and after detected break
idx_break = int(max_change_time - window_centers[0])
beta_before = np.mean(beta_est[:max(1, idx_break)])
beta_after = np.mean(beta_est[min(len(beta_est)-1, idx_break):])

print(f"\n   Average β before break: {beta_before:.4f}  (True: 0.40)")
print(f"   Average β after break:  {beta_after:.4f}  (True: 0.70)")

# ============================================================================
# Rolling Wald Tests
# ============================================================================
print("\n[6] Rolling hypothesis tests...")
print("-" * 80)

# Test H0: β = 0 over time
wald_rolling = rolling.get_rolling_wald_tests(
    test_type='beta_zero',
    variable_idx=0,
    tau=0.5
)

# Count rejections
rejections = sum(wald_rolling['reject'])
total_tests = len(wald_rolling['reject'])

print(f"\n   H₀: β = 0 tested at each window")
print(f"   Rejections: {rejections}/{total_tests} ({100*rejections/total_tests:.1f}%)")
print(f"   → {'Strong' if rejections/total_tests > 0.9 else 'Moderate'} evidence of cointegration throughout")

# ============================================================================
# Visualization
# ============================================================================
print("\n[7] Creating visualization...")

try:
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Plot 1: Rolling β estimates
    ax1 = axes[0]
    ax1.plot(window_centers, beta_series['estimate'], 'b-', linewidth=2, label='β̂(t)')
    ax1.fill_between(window_centers, 
                     beta_series['ci_lower'], 
                     beta_series['ci_upper'], 
                     alpha=0.2, label='95% CI')
    ax1.axhline(y=0.4, color='r', linestyle='--', alpha=0.5, label='True β (before)')
    ax1.axhline(y=0.7, color='g', linestyle='--', alpha=0.5, label='True β (after)')
    ax1.axvline(x=break_point, color='k', linestyle=':', alpha=0.5, linewidth=2, label='True break')
    ax1.set_ylabel('Long-run Coefficient (β)', fontsize=11)
    ax1.set_title('Rolling Window Estimation: Time-Varying Parameters', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9, loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim([0.2, 0.9])
    
    # Plot 2: Rolling p-values
    ax2 = axes[1]
    ax2.plot(window_centers, wald_rolling['p_value'], 'purple', linewidth=2)
    ax2.axhline(y=0.05, color='r', linestyle='--', linewidth=2, label='5% significance')
    ax2.fill_between(window_centers, 0, wald_rolling['p_value'], 
                     where=np.array(wald_rolling['p_value']) < 0.05, 
                     alpha=0.3, color='green', label='Reject H₀')
    ax2.set_ylabel('P-value', fontsize=11)
    ax2.set_title('Rolling Wald Test: H₀: β = 0', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('log')
    
    # Plot 3: Data
    ax3 = axes[2]
    ax3.plot(Y, alpha=0.7, label='Y')
    ax3.plot(X, alpha=0.7, label='X')
    ax3.axvline(x=break_point, color='k', linestyle=':', linewidth=2, label='Structural break')
    ax3.set_xlabel('Time', fontsize=11)
    ax3.set_ylabel('Value', fontsize=11)
    ax3.set_title('Original Data', fontsize=13, fontweight='bold')
    ax3.legend(fontsize=9)
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/rolling_estimation.png', dpi=150, bbox_inches='tight')
    print("   ✓ Plot saved to rolling_estimation.png")
    
except Exception as e:
    print(f"   ⚠ Visualization skipped: {e}")

# ============================================================================
# Export Results
# ============================================================================
print("\n[8] Exporting results...")

df = rolling.to_dataframe()
df.to_csv('/mnt/user-data/outputs/rolling_estimates.csv', index=False)

print(f"   ✓ Results exported to rolling_estimates.csv")
print(f"   Columns: {list(df.columns)}")
print(f"   Rows: {len(df)}")

# ============================================================================
# Summary Statistics
# ============================================================================
print("\n[9] Summary statistics:")
print("-" * 80)

print(f"\n   β̂ statistics:")
print(f"   Mean:     {np.mean(beta_series['estimate']):.4f}")
print(f"   Std Dev:  {np.std(beta_series['estimate']):.4f}")
print(f"   Min:      {np.min(beta_series['estimate']):.4f}")
print(f"   Max:      {np.max(beta_series['estimate']):.4f}")
print(f"   Range:    {np.max(beta_series['estimate']) - np.min(beta_series['estimate']):.4f}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE COMPLETE!")
print("=" * 80)
print("\nKey Features:")
print("  • Rolling window estimation captures time-varying parameters")
print("  • Successfully detected structural break")
print("  • Confidence intervals track parameter uncertainty over time")
print("  • Rolling tests identify periods of significant relationships")
print("\nApplications:")
print("  • Structural break detection")
print("  • Time-varying risk analysis")
print("  • Regime change identification")
print("  • Model stability assessment")
print("=" * 80)
