"""
Visualization functions for QARDL results
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional


def plot_quantile_coefficients(
    results,
    parameter: str = 'beta',
    variable_idx: int = 0,
    confidence_level: float = 0.95,
    figsize: tuple = (10, 6)
):
    """
    Plot parameter estimates across quantiles with confidence bands
    
    Parameters
    ----------
    results : QARDLResults
        Estimation results
    parameter : str
        Parameter to plot
    variable_idx : int
        Variable index
    confidence_level : float
        Confidence level
    figsize : tuple
        Figure size
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    quantiles = sorted(results.model.tau)
    estimates = []
    lower_ci = []
    upper_ci = []
    
    z_crit = 1.96 if confidence_level == 0.95 else 2.576
    
    for tau in quantiles:
        if parameter == 'beta':
            est = results.beta[tau][variable_idx]
            se = results.beta_se[tau][variable_idx]
        else:
            est = getattr(results, parameter)[tau][variable_idx]
            se = results.std_errors[tau][variable_idx]
            
        estimates.append(est)
        lower_ci.append(est - z_crit * se)
        upper_ci.append(est + z_crit * se)
    
    ax.plot(quantiles, estimates, 'o-', linewidth=2, label='Estimate')
    ax.fill_between(quantiles, lower_ci, upper_ci, alpha=0.2, 
                     label=f'{int(confidence_level*100)}% CI')
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax.set_xlabel('Quantile', fontsize=12)
    ax.set_ylabel(f'{parameter} coefficient', fontsize=12)
    ax.set_title(f'{parameter} Across Quantiles', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig, ax


def plot_rolling_estimates(
    rolling_results,
    parameter: str = 'beta',
    quantile: float = 0.5,
    variable_idx: int = 0,
    figsize: tuple = (12, 6)
):
    """
    Plot rolling parameter estimates over time
    
    Parameters
    ----------
    rolling_results : RollingQARDLResults
        Rolling estimation results
    parameter : str
        Parameter to plot
    quantile : float
        Quantile to plot
    variable_idx : int
        Variable index
    figsize : tuple
        Figure size
    """
    series = rolling_results.get_parameter_series(parameter, quantile)
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(series[:, variable_idx] if series.ndim > 1 else series)
    ax.set_xlabel('Time Window', fontsize=12)
    ax.set_ylabel(f'{parameter} coefficient', fontsize=12)
    ax.set_title(f'Rolling {parameter} (τ={quantile})', fontsize=14)
    ax.grid(True, alpha=0.3)
    
    return fig, ax


def plot_wald_tests(test_results, figsize: tuple = (10, 6)):
    """Plot Wald test results"""
    # Placeholder
    pass


# Alias for backward compatibility
plot_rolling_results = plot_rolling_estimates
