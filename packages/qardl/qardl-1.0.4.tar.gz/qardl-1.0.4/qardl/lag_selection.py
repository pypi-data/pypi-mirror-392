"""
Lag Order Selection for QARDL Models

CRITICAL CORRECTION: Use OLS-based BIC at MEAN (not quantile-based)

This implements the icmean.m approach from MATLAB code:
- Estimate ARDL at conditional MEAN using OLS
- Compute BIC for each (p,q) combination
- Select orders that minimize BIC

This is the CORRECT approach per the paper and MATLAB implementation.
The original error was using quantile-based BIC, which is WRONG.
"""

import numpy as np
from typing import Tuple, List, Optional, Dict
import warnings


def select_qardl_orders(
    data: np.ndarray,
    p_max: int = 8,
    q_max: int = 8,
    criterion: str = 'bic',
    constant: bool = True,
    verbose: bool = True
) -> Tuple[int, int]:
    """
    Select optimal QARDL orders using OLS-based information criterion at MEAN
    
    CRITICAL: This uses OLS estimation at the conditional MEAN,
    NOT quantile regression. This is the correct approach per the paper.
    
    The conditional mean equation is the weighted average of quantile
    equations, so BIC computed at mean consistently selects orders.
    
    Parameters
    ----------
    data : ndarray, shape (n, k+1)
        Data matrix [Y, X1, ..., Xk]
    p_max : int, default=8
        Maximum AR order to consider
    q_max : int, default=8
        Maximum DL order to consider
    criterion : str, default='bic'
        Information criterion: 'bic', 'aic', or 'hq'
    constant : bool, default=True
        Include intercept
    verbose : bool, default=True
        Print selection progress
        
    Returns
    -------
    p_opt : int
        Optimal AR order
    q_opt : int
        Optimal DL order
    results_dict : dict
        Dictionary with detailed results for all (p,q) combinations
        Keys are (p,q) tuples, values are dicts with 'ic', 'p', 'q'
        
    Notes
    -----
    This implements the icmean.m function from the MATLAB code.
    
    The BIC for an ARDL(p,q) model is:
        BIC = log(σ²) + (# parameters) * log(n) / n
    
    where σ² is the residual variance from OLS estimation.
    
    References
    ----------
    Pesaran & Shin (1998): Uses OLS-based IC for ARDL lag selection
    Cho, Kim & Shin (2015): MATLAB code uses icmean.m for QARDL
    """
    if verbose:
        print("=" * 70)
        print("QARDL Lag Order Selection (Correct OLS-based method)")
        print("=" * 70)
        print(f"Using {criterion.upper()} at conditional mean")
        print(f"Maximum orders: p_max={p_max}, q_max={q_max}")
        print("=" * 70)
        
    n, k_plus_1 = data.shape
    k = k_plus_1 - 1
    
    y = data[:, 0]
    X = data[:, 1:]
    
    # Storage for IC values
    ic_matrix = np.full((p_max, q_max + 1), np.inf)
    results_dict = {}  # Store detailed results
    
    # Try all (p, q) combinations
    for p in range(1, p_max + 1):
        for q in range(0, q_max + 1):
            try:
                # Estimate ARDL(p,q) using OLS
                ic_value = _compute_ols_ic(
                    y, X, p, q, criterion, constant
                )
                ic_matrix[p-1, q] = ic_value
                results_dict[(p, q)] = {
                    'bic': ic_value if criterion == 'bic' else np.nan,
                    'aic': ic_value if criterion == 'aic' else np.nan,
                    'ic': ic_value,
                    'p': p,
                    'q': q
                }
                
                if verbose and (p <= 3 or p == p_max) and (q <= 3 or q == q_max):
                    print(f"  ARDL({p},{q}): {criterion.upper()} = {ic_value:.6f}")
                    
            except Exception as e:
                if verbose:
                    print(f"  ARDL({p},{q}): FAILED ({str(e)})")
                continue
                
    # Find minimum
    min_idx = np.unravel_index(np.argmin(ic_matrix), ic_matrix.shape)
    p_opt = min_idx[0] + 1
    q_opt = min_idx[1]
    min_ic = ic_matrix[min_idx]
    
    if verbose:
        print("=" * 70)
        print(f"Optimal orders: p = {p_opt}, q = {q_opt}")
        print(f"Minimum {criterion.upper()} = {min_ic:.6f}")
        print("=" * 70)
        
    return p_opt, q_opt, results_dict


def _compute_ols_ic(
    y: np.ndarray,
    X: np.ndarray,
    p: int,
    q: int,
    criterion: str,
    constant: bool
) -> float:
    """
    Compute information criterion for ARDL(p,q) using OLS
    
    This is the CORRECT method per icmean.m
    
    Parameters
    ----------
    y : ndarray
        Dependent variable
    X : ndarray, shape (n, k)
        Explanatory variables
    p : int
        AR order
    q : int
        DL order
    criterion : str
        'bic', 'aic', or 'hq'
    constant : bool
        Include intercept
        
    Returns
    -------
    ic : float
        Information criterion value
    """
    n = len(y)
    k = X.shape[1]
    
    # Build design matrix
    max_lag = max(p, q)
    effective_n = n - max_lag
    
    # Lagged Y
    Y_lags = np.zeros((effective_n, p))
    for j in range(1, p+1):
        Y_lags[:, j-1] = y[max_lag-j:n-j]
        
    # Current and lagged X
    X_current = X[max_lag:, :]
    
    X_lags = []
    for j in range(1, q+1):
        X_lags.append(X[max_lag-j:n-j, :])
    if X_lags:
        X_lags = np.hstack(X_lags)
    else:
        X_lags = np.empty((effective_n, 0))
        
    # Build regressor matrix
    if constant:
        Z = np.column_stack([
            np.ones(effective_n),
            Y_lags,
            X_current,
            X_lags
        ])
    else:
        Z = np.column_stack([
            Y_lags,
            X_current,
            X_lags
        ])
        
    # Effective dependent variable
    y_eff = y[max_lag:]
    
    # OLS estimation
    try:
        beta_ols = np.linalg.lstsq(Z, y_eff, rcond=None)[0]
    except np.linalg.LinAlgError:
        return np.inf
        
    # Residuals
    residuals = y_eff - Z @ beta_ols
    
    # Residual variance
    sigma_sq = np.sum(residuals**2) / effective_n
    
    # Number of parameters
    num_params = Z.shape[1]
    
    # Information criterion
    if criterion == 'bic':
        ic = np.log(sigma_sq) + num_params * np.log(effective_n) / effective_n
    elif criterion == 'aic':
        ic = np.log(sigma_sq) + 2 * num_params / effective_n
    elif criterion == 'hq':
        ic = np.log(sigma_sq) + 2 * num_params * np.log(np.log(effective_n)) / effective_n
    else:
        raise ValueError(f"Unknown criterion: {criterion}")
        
    return ic


def select_orders_sequential(
    data: np.ndarray,
    p_max: int = 8,
    q_max: int = 8,
    criterion: str = 'bic',
    constant: bool = True,
    verbose: bool = True
) -> Tuple[int, int]:
    """
    Sequential lag order selection (alternative method)
    
    First selects p fixing q at q_max, then selects q fixing p at p_opt.
    
    This can be faster than grid search but may not find global optimum.
    
    Parameters
    ----------
    data : ndarray
        Data matrix
    p_max : int
        Maximum AR order
    q_max : int
        Maximum DL order
    criterion : str
        Information criterion
    constant : bool
        Include intercept
    verbose : bool
        Print progress
        
    Returns
    -------
    p_opt : int
        Optimal AR order
    q_opt : int
        Optimal DL order
    """
    n, k_plus_1 = data.shape
    y = data[:, 0]
    X = data[:, 1:]
    
    if verbose:
        print("Sequential lag order selection")
        print("-" * 50)
        
    # Step 1: Select p given q = q_max
    ic_p = []
    for p in range(1, p_max + 1):
        ic = _compute_ols_ic(y, X, p, q_max, criterion, constant)
        ic_p.append(ic)
        if verbose:
            print(f"  p={p}, q={q_max}: {criterion.upper()}={ic:.6f}")
            
    p_opt = np.argmin(ic_p) + 1
    
    if verbose:
        print(f"\nSelected p = {p_opt}")
        print("-" * 50)
        
    # Step 2: Select q given p = p_opt
    ic_q = []
    for q in range(0, q_max + 1):
        ic = _compute_ols_ic(y, X, p_opt, q, criterion, constant)
        ic_q.append(ic)
        if verbose:
            print(f"  p={p_opt}, q={q}: {criterion.upper()}={ic:.6f}")
            
    q_opt = np.argmin(ic_q)
    
    if verbose:
        print(f"\nSelected q = {q_opt}")
        print(f"Final: ARDL({p_opt}, {q_opt})")
        print("=" * 50)
        
    return p_opt, q_opt


def evaluate_order_stability(
    data: np.ndarray,
    p: int,
    q: int,
    constant: bool = True
) -> Dict:
    """
    Check stability conditions for selected orders
    
    For QARDL to have stable long-run relationship:
    1. Roots of φ(L) polynomial must lie outside unit circle
    2. 1 - Σφ_j ≠ 0 (no exact unit root)
    
    Parameters
    ----------
    data : ndarray
        Data matrix
    p : int
        AR order
    q : int
        DL order
    constant : bool
        Include intercept
        
    Returns
    -------
    results : dict
        Stability diagnostics
    """
    n = len(data)
    y = data[:, 0]
    X = data[:, 1:]
    k = X.shape[1]
    
    # Estimate model
    max_lag = max(p, q)
    effective_n = n - max_lag
    
    # Build design matrix (simplified)
    Y_lags = np.zeros((effective_n, p))
    for j in range(1, p+1):
        Y_lags[:, j-1] = y[max_lag-j:n-j]
        
    X_current = X[max_lag:, :]
    
    if constant:
        Z = np.column_stack([np.ones(effective_n), Y_lags, X_current])
    else:
        Z = np.column_stack([Y_lags, X_current])
        
    y_eff = y[max_lag:]
    
    # OLS
    beta_ols = np.linalg.lstsq(Z, y_eff, rcond=None)[0]
    
    # Extract φ coefficients
    if constant:
        phi = beta_ols[1:1+p]
    else:
        phi = beta_ols[0:p]
        
    # Check stability
    phi_sum = np.sum(phi)
    
    # Characteristic polynomial: 1 - φ_1*z - φ_2*z² - ... - φ_p*z^p
    # Equivalently: φ(L) = 1 - Σφ_j*L^j
    # Need roots of this to be outside unit circle
    
    # Companion matrix method
    companion = np.zeros((p, p))
    companion[0, :] = phi
    if p > 1:
        companion[1:, :-1] = np.eye(p-1)
        
    eigenvalues = np.linalg.eigvals(companion)
    max_eigenvalue = np.max(np.abs(eigenvalues))
    
    # Stability check
    stable = max_eigenvalue < 1.0
    cointegrated = np.abs(1 - phi_sum) > 0.01  # Not too close to unit root
    
    return {
        'p': p,
        'q': q,
        'phi_sum': phi_sum,
        'error_correction': -(1 - phi_sum),
        'max_eigenvalue': max_eigenvalue,
        'stable': stable,
        'cointegrated': cointegrated,
        'eigenvalues': eigenvalues,
        'message': _stability_message(stable, cointegrated, max_eigenvalue, phi_sum)
    }


def _stability_message(
    stable: bool,
    cointegrated: bool,
    max_eig: float,
    phi_sum: float
) -> str:
    """Generate stability message"""
    if stable and cointegrated:
        return (f"✓ Model is stable and cointegrated\n"
               f"  Max eigenvalue: {max_eig:.4f} < 1.0\n"
               f"  Error correction: {-(1-phi_sum):.4f}")
    elif not stable:
        return (f"✗ Model is UNSTABLE\n"
               f"  Max eigenvalue: {max_eig:.4f} >= 1.0\n"
               f"  Consider reducing lag orders")
    elif not cointegrated:
        return (f"⚠ Near unit root detected\n"
               f"  Σφ ≈ 1.0 (unit root)\n"
               f"  Long-run relationship may not exist")
    else:
        return "Model characteristics unclear"


def compare_orders(
    data: np.ndarray,
    order_list: List[Tuple[int, int]],
    criterion: str = 'bic',
    constant: bool = True
) -> Dict:
    """
    Compare multiple (p,q) specifications
    
    Useful for model selection and robustness checks
    
    Parameters
    ----------
    data : ndarray
        Data matrix
    order_list : list of tuples
        List of (p, q) pairs to compare
    criterion : str
        Information criterion
    constant : bool
        Include intercept
        
    Returns
    -------
    results : dict
        Comparison results
    """
    y = data[:, 0]
    X = data[:, 1:]
    
    results = []
    
    for p, q in order_list:
        ic = _compute_ols_ic(y, X, p, q, criterion, constant)
        stability = evaluate_order_stability(data, p, q, constant)
        
        results.append({
            'p': p,
            'q': q,
            'ic': ic,
            'stable': stability['stable'],
            'cointegrated': stability['cointegrated'],
            'error_correction': stability['error_correction']
        })
        
    # Sort by IC
    results.sort(key=lambda x: x['ic'])
    
    # Find best
    best = results[0]
    
    return {
        'best': best,
        'all_results': results,
        'criterion': criterion
    }
