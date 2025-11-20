"""
Simulation Module
=================

Functions for generating I(1), I(2), and multicointegrated time series
as described in Engsted et al. (1997) and Haldrup (1994).
"""

import numpy as np
from typing import Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class MulticointegrationSystem:
    """
    Container for a multicointegrated system
    
    Attributes
    ----------
    y : np.ndarray
        The I(2) dependent variable
    x1 : np.ndarray
        I(1) regressors (n x m1)
    x2 : np.ndarray
        I(2) regressors (n x m2)
    beta1 : np.ndarray
        True coefficients for I(1) variables
    beta2 : np.ndarray
        True coefficients for I(2) variables
    u : np.ndarray
        True cointegration residuals
    """
    y: np.ndarray
    x1: np.ndarray
    x2: np.ndarray
    beta1: np.ndarray
    beta2: np.ndarray
    u: np.ndarray


def generate_i1_process(n: int, sigma: float = 1.0, 
                       drift: float = 0.0,
                       initial_value: float = 0.0,
                       random_state: Optional[int] = None) -> np.ndarray:
    """
    Generate an I(1) process (random walk with drift)
    
    The process is: x_t = x_{t-1} + drift + epsilon_t
    where epsilon_t ~ N(0, sigma^2)
    
    Parameters
    ----------
    n : int
        Length of series
    sigma : float
        Standard deviation of innovations
    drift : float
        Drift parameter (default 0 for pure random walk)
    initial_value : float
        Starting value
    random_state : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        I(1) time series of length n
        
    Examples
    --------
    >>> x = generate_i1_process(100, sigma=1.0, drift=0.0)
    >>> len(x)
    100
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    innovations = np.random.normal(0, sigma, n)
    x = np.zeros(n)
    x[0] = initial_value + innovations[0]
    
    for t in range(1, n):
        x[t] = x[t-1] + drift + innovations[t]
    
    return x


def generate_i2_process(n: int, sigma: float = 1.0,
                       drift1: float = 0.0, drift2: float = 0.0,
                       initial_values: Tuple[float, float] = (0.0, 0.0),
                       random_state: Optional[int] = None) -> np.ndarray:
    """
    Generate an I(2) process (double integration)
    
    The process is: Δ²x_t = epsilon_t
    or equivalently: x_t = x_{t-1} + (x_{t-1} - x_{t-2}) + drift1 + epsilon_t
    
    This can be thought of as cumulating an I(1) process:
    - Let z_t be I(1): z_t = z_{t-1} + drift1 + epsilon_t
    - Then x_t = sum_{j=1}^t z_j is I(2)
    
    Parameters
    ----------
    n : int
        Length of series
    sigma : float
        Standard deviation of innovations
    drift1 : float
        Drift in first difference (default 0)
    drift2 : float
        Quadratic drift (default 0)
    initial_values : tuple
        (x_0, x_1) starting values
    random_state : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        I(2) time series of length n
        
    Examples
    --------
    >>> x = generate_i2_process(100, sigma=1.0)
    >>> len(x)
    100
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # First, generate the I(1) first differences
    delta_x = generate_i1_process(n, sigma=sigma, drift=drift1, 
                                  initial_value=0.0, random_state=None)
    
    # Then cumulate to get I(2) process
    x = np.zeros(n)
    x[0] = initial_values[0]
    x[1] = initial_values[1] + delta_x[0]
    
    for t in range(2, n):
        x[t] = x[t-1] + delta_x[t-1] + drift2 * t
    
    return x


def generate_multicointegrated_system(
    n: int,
    m1: int = 1,
    m2: int = 1,
    beta1: Optional[np.ndarray] = None,
    beta2: Optional[np.ndarray] = None,
    gamma: Optional[np.ndarray] = None,
    sigma_u: float = 1.0,
    sigma_x1: float = 1.0,
    sigma_x2: float = 1.0,
    cointegration_order: int = 0,
    include_intercept: bool = True,
    include_trend: bool = False,
    random_state: Optional[int] = None
) -> MulticointegrationSystem:
    """
    Generate a multicointegrated system as in Engsted et al. (1997)
    
    The system is:
    - x1_t: I(1) variables (m1-dimensional)
    - x2_t: I(2) variables (m2-dimensional)
    - y_t = beta0 + beta1'*x1_t + beta2'*x2_t + u_t
    
    Depending on cointegration_order:
    - 0: Full multicointegration (u_t is I(0))
    - 1: First-level cointegration (u_t is I(1))
    - 2: No cointegration (u_t is I(2))
    
    For multicointegration (d=0), we have:
    - y_t, x2_t ~ CI(2,1) with cointegrating vector (1, -beta2)
    - The resulting z_t = y_t - beta2'*x2_t ~ I(1)
    - z_t and x1_t cointegrate with vector (1, -beta1)
    
    Parameters
    ----------
    n : int
        Sample size
    m1 : int
        Number of I(1) regressors
    m2 : int
        Number of I(2) regressors
    beta1 : np.ndarray, optional
        True coefficients for I(1) variables (default: ones)
    beta2 : np.ndarray, optional
        True coefficients for I(2) variables (default: ones)
    gamma : np.ndarray, optional
        Coefficient for deterministic trend (default: None)
    sigma_u : float
        Standard deviation of u_t innovations
    sigma_x1 : float
        Standard deviation for I(1) processes
    sigma_x2 : float
        Standard deviation for I(2) processes
    cointegration_order : int
        Integration order of residuals: 0 (multicointegration), 1, or 2
    include_intercept : bool
        Include intercept in DGP
    include_trend : bool
        Include linear trend in DGP
    random_state : int, optional
        Random seed
        
    Returns
    -------
    MulticointegrationSystem
        Object containing generated series and parameters
        
    Examples
    --------
    >>> # Generate multicointegrated system with 1 I(1) and 1 I(2) variable
    >>> system = generate_multicointegrated_system(
    ...     n=100, m1=1, m2=1, cointegration_order=0, random_state=42
    ... )
    >>> system.y.shape
    (100,)
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Set default coefficients
    if beta1 is None:
        beta1 = np.ones(m1)
    if beta2 is None:
        beta2 = np.ones(m2)
    
    beta1 = np.atleast_1d(beta1)
    beta2 = np.atleast_1d(beta2)
    
    if len(beta1) != m1:
        raise ValueError(f"beta1 must have length {m1}")
    if len(beta2) != m2:
        raise ValueError(f"beta2 must have length {m2}")
    
    # Generate I(1) regressors
    x1 = np.zeros((n, m1))
    for i in range(m1):
        x1[:, i] = generate_i1_process(n, sigma=sigma_x1)
    
    # Generate I(2) regressors
    x2 = np.zeros((n, m2))
    for i in range(m2):
        x2[:, i] = generate_i2_process(n, sigma=sigma_x2)
    
    # Generate error term with appropriate integration order
    if cointegration_order == 0:
        # I(0) errors - multicointegration
        u = np.random.normal(0, sigma_u, n)
    elif cointegration_order == 1:
        # I(1) errors - first level cointegration only
        u = generate_i1_process(n, sigma=sigma_u)
    elif cointegration_order == 2:
        # I(2) errors - no cointegration
        u = generate_i2_process(n, sigma=sigma_u)
    else:
        raise ValueError("cointegration_order must be 0, 1, or 2")
    
    # Generate y
    y = beta1 @ x1.T + beta2 @ x2.T + u
    
    # Add deterministic components
    if include_intercept:
        y += 5.0  # Add intercept
    
    if include_trend:
        t = np.arange(1, n + 1)
        if gamma is None:
            gamma = 0.1
        y += gamma * t
    
    return MulticointegrationSystem(
        y=y,
        x1=x1,
        x2=x2,
        beta1=beta1,
        beta2=beta2,
        u=u
    )


def generate_granger_lee_example(
    n: int,
    production_shock_std: float = 1.0,
    sales_shock_std: float = 1.0,
    initial_inventory: float = 0.0,
    random_state: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate data from the Granger-Lee (1989, 1990) production-sales-inventory example
    
    This is the canonical multicointegration example where:
    - Y_t (production) and X_t (sales) are I(1)
    - Z_t = Y_t - X_t (inventory investment) is I(0)
    - S_t = sum Z_j (inventory level) is I(1)
    - S_t cointegrates with X_t and/or Y_t (multicointegration)
    
    Parameters
    ----------
    n : int
        Sample size
    production_shock_std : float
        Standard deviation of production shocks
    sales_shock_std : float
        Standard deviation of sales shocks
    initial_inventory : float
        Initial inventory level
    random_state : int, optional
        Random seed
        
    Returns
    -------
    production : np.ndarray
        Production series (I(1))
    sales : np.ndarray
        Sales series (I(1))
    inventory : np.ndarray
        Inventory level (I(1), cointegrates with production/sales)
        
    Examples
    --------
    >>> prod, sales, inv = generate_granger_lee_example(100, random_state=42)
    >>> len(prod)
    100
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate I(1) sales and production
    sales = generate_i1_process(n, sigma=sales_shock_std)
    production = generate_i1_process(n, sigma=production_shock_std)
    
    # Inventory investment is I(0) by construction (assuming cointegration)
    # In reality, firms adjust to maintain inventory levels
    # For simplicity, we make inventory investment = production - sales + noise
    inventory_investment = production - sales + np.random.normal(0, 0.1, n)
    
    # Cumulate to get inventory level (I(1))
    inventory = np.zeros(n)
    inventory[0] = initial_inventory + inventory_investment[0]
    for t in range(1, n):
        inventory[t] = inventory[t-1] + inventory_investment[t]
    
    return production, sales, inventory


def add_structural_break(series: np.ndarray, 
                        break_point: int,
                        break_type: str = 'level',
                        break_size: float = 5.0) -> np.ndarray:
    """
    Add a structural break to a time series
    
    Parameters
    ----------
    series : np.ndarray
        Original time series
    break_point : int
        Index where break occurs
    break_type : str
        Type of break: 'level' or 'trend'
    break_size : float
        Size of the break
        
    Returns
    -------
    np.ndarray
        Series with structural break
    """
    n = len(series)
    series_break = series.copy()
    
    if break_type == 'level':
        # Level shift
        series_break[break_point:] += break_size
    elif break_type == 'trend':
        # Trend break
        t = np.arange(n)
        trend_change = np.zeros(n)
        trend_change[break_point:] = break_size * (t[break_point:] - break_point)
        series_break += trend_change
    else:
        raise ValueError("break_type must be 'level' or 'trend'")
    
    return series_break


def generate_covariance_matrix(m: int, correlation: float = 0.5) -> np.ndarray:
    """
    Generate a covariance matrix with specified correlation structure
    
    Parameters
    ----------
    m : int
        Dimension
    correlation : float
        Off-diagonal correlation (between 0 and 1)
        
    Returns
    -------
    np.ndarray
        m x m covariance matrix
    """
    if not 0 <= correlation < 1:
        raise ValueError("correlation must be in [0, 1)")
    
    cov = np.ones((m, m)) * correlation
    np.fill_diagonal(cov, 1.0)
    
    return cov
