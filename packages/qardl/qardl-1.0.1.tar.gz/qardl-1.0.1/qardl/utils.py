"""
Utility functions for QARDL package
"""

import numpy as np
from scipy import stats
from typing import Tuple, Optional


def select_lag_order(
    data: np.ndarray,
    max_p: int = 5,
    max_q: int = 5,
    criterion: str = 'bic',
    tau: float = 0.5
) -> Tuple[int, int]:
    """
    Select optimal lag order (p, q) using information criterion
    
    Parameters
    ----------
    data : ndarray
        Data matrix
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
    from .core import QARDL
    
    best_ic = np.inf
    best_p, best_q = 1, 1
    
    for p in range(1, max_p + 1):
        for q in range(0, max_q + 1):
            try:
                model = QARDL(data, p=p, q=q, tau=tau)
                results = model.fit(verbose=False)
                
                # Compute IC
                n = model.effective_n
                k = len(results.coefficients[tau])
                resid = model.y_effective - model.Z_matrix @ results.coefficients[tau]
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
