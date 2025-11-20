"""
Utility Functions
=================

Statistical utilities and helper functions for multicointegration analysis.
"""

import numpy as np
from typing import Tuple, Optional, Union
from scipy import stats


def calculate_dw_statistic(residuals: np.ndarray) -> float:
    """
    Calculate Durbin-Watson statistic
    
    DW = sum((e_t - e_{t-1})^2) / sum(e_t^2)
    
    As noted in Haldrup (1994), the DW statistic tends to zero at rate O_p(n^{-1})
    when the conditional model is I(1) or I(2).
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals
        
    Returns
    -------
    float
        Durbin-Watson statistic
        
    Examples
    --------
    >>> residuals = np.random.randn(100)
    >>> dw = calculate_dw_statistic(residuals)
    >>> 0 < dw < 4
    True
    """
    n = len(residuals)
    diff_residuals = np.diff(residuals)
    
    numerator = np.sum(diff_residuals**2)
    denominator = np.sum(residuals**2)
    
    if denominator == 0:
        return np.nan
    
    return numerator / denominator


def calculate_r_squared(y: np.ndarray, y_pred: np.ndarray) -> float:
    """
    Calculate coefficient of determination (R²)
    
    R² = 1 - SS_res / SS_tot
    
    As noted in Haldrup (1994):
    - For d=0 (stationary errors): R² → 1 at rate O_p(n^{-3})
    - For d=1: R² → 1 at rate O_p(n^{-2})
    - For d=2: R² has a non-degenerate limiting distribution
    
    Parameters
    ----------
    y : np.ndarray
        Actual values
    y_pred : np.ndarray
        Predicted values
        
    Returns
    -------
    float
        R² statistic
        
    Examples
    --------
    >>> y = np.random.randn(100)
    >>> y_pred = y + np.random.randn(100) * 0.1
    >>> r2 = calculate_r_squared(y, y_pred)
    >>> 0 <= r2 <= 1
    True
    """
    residuals = y - y_pred
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((y - np.mean(y))**2)
    
    if ss_tot == 0:
        return np.nan
    
    return 1 - (ss_res / ss_tot)


def integration_order(series: np.ndarray, 
                     max_order: int = 2,
                     significance_level: float = 0.05) -> int:
    """
    Determine integration order of a time series using ADF tests
    
    Tests the null of unit root at level, first difference, and second difference.
    Returns the minimum number of differences needed for stationarity.
    
    Parameters
    ----------
    series : np.ndarray
        Time series
    max_order : int
        Maximum integration order to test (1 or 2)
    significance_level : float
        Significance level for ADF test
        
    Returns
    -------
    int
        Integration order (0, 1, or 2)
        
    Examples
    --------
    >>> from multicoint.simulation import generate_i2_process
    >>> x = generate_i2_process(100, random_state=42)
    >>> order = integration_order(x, max_order=2)
    >>> order in [0, 1, 2]
    True
    """
    from statsmodels.tsa.stattools import adfuller
    
    current_series = series.copy()
    
    for d in range(max_order + 1):
        try:
            # Perform ADF test
            result = adfuller(current_series, maxlag=None, autolag='AIC')
            adf_stat = result[0]
            p_value = result[1]
            
            # If we reject null of unit root, series is I(d)
            if p_value < significance_level:
                return d
            
            # Difference the series for next iteration
            if d < max_order:
                current_series = np.diff(current_series)
        except:
            # If test fails, assume higher order integration
            continue
    
    # If we reach here, series is at least I(max_order+1)
    return max_order + 1


def lag_matrix(x: np.ndarray, lags: int) -> np.ndarray:
    """
    Create matrix of lagged values
    
    Parameters
    ----------
    x : np.ndarray
        Time series (n,) or (n, k)
    lags : int
        Number of lags
        
    Returns
    -------
    np.ndarray
        Matrix with lagged values (n-lags, lags*k)
        
    Examples
    --------
    >>> x = np.arange(10)
    >>> X_lagged = lag_matrix(x, lags=2)
    >>> X_lagged.shape
    (8, 2)
    """
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    
    n, k = x.shape
    
    if lags < 1:
        raise ValueError("lags must be >= 1")
    
    # Create lagged matrix
    X_lagged = np.zeros((n - lags, lags * k))
    
    for lag in range(1, lags + 1):
        start_col = (lag - 1) * k
        end_col = lag * k
        X_lagged[:, start_col:end_col] = x[lags - lag : n - lag, :]
    
    return X_lagged


def cumsum_matrix(X: np.ndarray) -> np.ndarray:
    """
    Cumulative sum of each column in a matrix
    
    This is used to transform I(1) variables to I(2) as in
    Engsted et al. (1997) equation (1).
    
    Parameters
    ----------
    X : np.ndarray
        Input matrix (n, k)
        
    Returns
    -------
    np.ndarray
        Cumulative sum matrix (n, k)
        
    Examples
    --------
    >>> X = np.array([[1, 2], [3, 4], [5, 6]])
    >>> cumsum_matrix(X)
    array([[ 1.,  2.],
           [ 4.,  6.],
           [ 9., 12.]])
    """
    return np.cumsum(X, axis=0)


def demean(x: np.ndarray) -> np.ndarray:
    """
    Remove mean from series
    
    Parameters
    ----------
    x : np.ndarray
        Time series
        
    Returns
    -------
    np.ndarray
        Demeaned series
    """
    return x - np.mean(x)


def detrend(x: np.ndarray, order: int = 1) -> np.ndarray:
    """
    Remove polynomial trend from series
    
    Parameters
    ----------
    x : np.ndarray
        Time series (length n)
    order : int
        Order of polynomial (1 for linear, 2 for quadratic)
        
    Returns
    -------
    np.ndarray
        Detrended series
        
    Examples
    --------
    >>> t = np.arange(100)
    >>> x = 2 * t + np.random.randn(100)
    >>> x_detrended = detrend(x, order=1)
    >>> abs(np.mean(x_detrended)) < 1
    True
    """
    n = len(x)
    t = np.arange(1, n + 1)
    
    # Create design matrix
    if order == 1:
        X = np.column_stack([np.ones(n), t])
    elif order == 2:
        X = np.column_stack([np.ones(n), t, t**2])
    else:
        raise ValueError("order must be 1 or 2")
    
    # OLS regression
    beta = np.linalg.lstsq(X, x, rcond=None)[0]
    trend = X @ beta
    
    return x - trend


def information_criteria(residuals: np.ndarray, 
                        n_params: int,
                        criterion: str = 'aic') -> float:
    """
    Calculate information criteria (AIC, BIC, HQC)
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals
    n_params : int
        Number of parameters in model
    criterion : str
        'aic', 'bic', or 'hqc'
        
    Returns
    -------
    float
        Information criterion value
        
    Examples
    --------
    >>> residuals = np.random.randn(100)
    >>> aic = information_criteria(residuals, n_params=5, criterion='aic')
    >>> isinstance(aic, float)
    True
    """
    n = len(residuals)
    sse = np.sum(residuals**2)
    
    if criterion.lower() == 'aic':
        return n * np.log(sse / n) + 2 * n_params
    elif criterion.lower() == 'bic':
        return n * np.log(sse / n) + n_params * np.log(n)
    elif criterion.lower() == 'hqc':
        return n * np.log(sse / n) + 2 * n_params * np.log(np.log(n))
    else:
        raise ValueError("criterion must be 'aic', 'bic', or 'hqc'")


def select_lag_length(residuals: np.ndarray,
                     max_lags: int = 10,
                     criterion: str = 'aic') -> int:
    """
    Select optimal lag length using information criteria
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals
    max_lags : int
        Maximum number of lags to consider
    criterion : str
        Information criterion to use
        
    Returns
    -------
    int
        Optimal lag length
        
    Examples
    --------
    >>> residuals = np.random.randn(100)
    >>> lag = select_lag_length(residuals, max_lags=10)
    >>> 0 <= lag <= 10
    True
    """
    n = len(residuals)
    ic_values = []
    
    for p in range(1, min(max_lags + 1, n // 4)):
        # Create lagged matrix
        X_lagged = lag_matrix(residuals, p)
        y = residuals[p:]
        
        # OLS regression
        beta = np.linalg.lstsq(X_lagged, y, rcond=None)[0]
        fitted = X_lagged @ beta
        resid = y - fitted
        
        # Calculate IC
        n_params = p + 1
        ic = information_criteria(resid, n_params, criterion)
        ic_values.append(ic)
    
    # Return lag with minimum IC
    return np.argmin(ic_values) + 1


def bootstrap_critical_values(test_statistic_func,
                              n: int,
                              n_bootstrap: int = 1000,
                              quantiles: Optional[list] = None,
                              random_state: Optional[int] = None,
                              **kwargs) -> dict:
    """
    Bootstrap critical values for a test statistic
    
    Parameters
    ----------
    test_statistic_func : callable
        Function that generates data and computes test statistic
    n : int
        Sample size
    n_bootstrap : int
        Number of bootstrap replications
    quantiles : list, optional
        Quantiles to compute (default: [0.01, 0.025, 0.05, 0.10])
    random_state : int, optional
        Random seed
    **kwargs
        Additional arguments to test_statistic_func
        
    Returns
    -------
    dict
        Dictionary mapping quantiles to critical values
        
    Examples
    --------
    >>> def my_test_func(n, **kwargs):
    ...     from multicoint.simulation import generate_i1_process
    ...     x = generate_i1_process(n)
    ...     return np.mean(x)
    >>> cv = bootstrap_critical_values(my_test_func, n=100, n_bootstrap=100)
    >>> 0.01 in cv
    True
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    if quantiles is None:
        quantiles = [0.01, 0.025, 0.05, 0.10]
    
    # Collect test statistics
    test_stats = []
    for i in range(n_bootstrap):
        stat = test_statistic_func(n, **kwargs)
        test_stats.append(stat)
    
    test_stats = np.array(test_stats)
    
    # Compute quantiles
    critical_values = {}
    for q in quantiles:
        critical_values[q] = np.quantile(test_stats, q)
    
    return critical_values


def newey_west_variance(residuals: np.ndarray,
                       X: np.ndarray,
                       lags: Optional[int] = None) -> np.ndarray:
    """
    Calculate Newey-West HAC covariance matrix
    
    This is used for robust standard errors in the presence of
    autocorrelation and heteroskedasticity.
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals (n,)
    X : np.ndarray
        Design matrix (n, k)
    lags : int, optional
        Number of lags for Newey-West (default: floor(4*(n/100)^(2/9)))
        
    Returns
    -------
    np.ndarray
        HAC covariance matrix (k, k)
    """
    n, k = X.shape
    
    if lags is None:
        lags = int(np.floor(4 * (n / 100)**(2/9)))
    
    # Meat of sandwich
    XXe = X * residuals[:, np.newaxis]
    S0 = XXe.T @ XXe / n
    
    # Add autocovariance terms with Bartlett kernel
    for lag in range(1, lags + 1):
        weight = 1 - lag / (lags + 1)
        gamma = (XXe[lag:].T @ XXe[:-lag]) / n
        S0 += weight * (gamma + gamma.T)
    
    # Bread of sandwich
    Q = X.T @ X / n
    Q_inv = np.linalg.inv(Q)
    
    # Sandwich
    V = Q_inv @ S0 @ Q_inv / n
    
    return V
