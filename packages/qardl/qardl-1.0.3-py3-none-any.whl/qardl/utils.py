"""
Utility functions for QARDL package
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from typing import Tuple, Optional, Union


def quantile_regression(
    y: Union[np.ndarray, pd.Series],
    X: Union[np.ndarray, pd.DataFrame],
    tau: float = 0.5
) -> np.ndarray:
    """
    Basic quantile regression estimation

    Parameters
    ----------
    y : array-like
        Dependent variable
    X : array-like
        Independent variables
    tau : float
        Quantile (0 < tau < 1)

    Returns
    -------
    beta : ndarray
        Coefficient estimates
    """
    # Convert to arrays
    if isinstance(y, pd.Series):
        y = y.values
    else:
        y = np.asarray(y).flatten()

    if isinstance(X, pd.DataFrame):
        X = X.values
    else:
        X = np.atleast_2d(X)

    n, p = X.shape

    def rho(u, tau):
        """Check function for quantile regression"""
        return np.where(u >= 0, tau * u, (tau - 1) * u)

    def objective(beta):
        residuals = y - X @ beta
        return np.sum(rho(residuals, tau))

    # Initial guess from OLS
    try:
        beta_init = np.linalg.lstsq(X, y, rcond=None)[0]
    except:
        beta_init = np.zeros(p)

    # Minimize
    result = minimize(objective, beta_init, method='SLSQP')

    return result.x


def bandwidth_hall_sheather(
    y: Union[np.ndarray, pd.Series],
    tau: float = 0.5,
    method: str = 'normal'
) -> float:
    """
    Hall-Sheather bandwidth selection for quantile regression

    Parameters
    ----------
    y : array-like
        Data for bandwidth selection
    tau : float
        Quantile
    method : str
        Bandwidth method ('normal' or 'empirical')

    Returns
    -------
    h : float
        Bandwidth
    """
    if isinstance(y, pd.Series):
        y = y.values
    else:
        y = np.asarray(y).flatten()

    n = len(y)

    if method == 'normal':
        # Assumes normal distribution
        z_tau = stats.norm.ppf(tau)
        phi_z = stats.norm.pdf(z_tau)
        h = n**(-1/3) * stats.norm.ppf(0.975)**(2/3) * \
            ((1.5 * phi_z**2) / (2 * z_tau**2 + 1))**(1/3)
    else:
        # Empirical method
        iqr = np.percentile(y, 75) - np.percentile(y, 25)
        h = 1.06 * min(np.std(y), iqr/1.34) * n**(-1/5)

    return h


def select_lag_order(
    y: Union[np.ndarray, pd.Series],
    X: Union[np.ndarray, pd.DataFrame],
    max_p: int = 5,
    max_q: int = 5,
    criterion: str = 'bic',
    tau: float = 0.5
) -> Tuple[int, int]:
    """
    Select optimal lag order (p, q) using information criterion

    Parameters
    ----------
    y : array-like
        Dependent variable
    X : array-like
        Independent variables
    max_p : int
        Maximum p to consider
    max_q : int
        Maximum q to consider
    criterion : str
        'bic' or 'aic'
    tau : float
        Quantile for selection

    Returns
    -------
    p_opt, q_opt : tuple of int
        Optimal lag orders
    """
    from .core_corrected import QARDLCorrected

    # Convert to arrays
    if isinstance(y, pd.Series):
        y = y.values
    else:
        y = np.asarray(y).flatten()

    if isinstance(X, pd.DataFrame):
        X = X.values
    else:
        X = np.asarray(X)
        if X.ndim == 1:
            X = X.reshape(-1, 1)

    best_ic = np.inf
    best_p, best_q = 1, 1

    for p in range(1, max_p + 1):
        for q in range(0, max_q + 1):
            try:
                model = QARDLCorrected(y=y, X=X, p=p, q=q, tau=tau)
                results = model.fit(verbose=False)

                # Compute IC
                n = model.effective_n
                coef = results.coefficients[tau]
                k = len(coef)
                resid = model.y_effective - model.Z_matrix @ coef
                rho = np.sum(resid * (tau - (resid < 0)))

                if criterion == 'bic':
                    ic = np.log(rho / n) + k * np.log(n) / n
                else:  # aic
                    ic = np.log(rho / n) + 2 * k / n

                if ic < best_ic:
                    best_ic = ic
                    best_p, best_q = p, q

            except:
                continue

    return best_p, best_q