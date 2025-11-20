"""
Cointegration Regression Module
================================

Single-equation cointegration regression estimation for systems with I(1) and I(2)
variables, based on Engsted et al. (1997) and Haldrup (1994).
"""

import numpy as np
from typing import Optional, Tuple, Dict, Union
from dataclasses import dataclass
from .utils import (
    calculate_dw_statistic, 
    calculate_r_squared,
    cumsum_matrix,
    newey_west_variance
)


@dataclass
class CointegrationRegressionResult:
    """
    Results from cointegration regression
    
    Attributes
    ----------
    coefficients : np.ndarray
        Estimated coefficients [intercept, trend, trend^2, beta1, beta2]
    residuals : np.ndarray
        Regression residuals
    fitted_values : np.ndarray
        Fitted values
    std_errors : np.ndarray
        Standard errors of coefficients
    t_statistics : np.ndarray
        t-statistics for coefficients
    r_squared : float
        R² statistic
    adj_r_squared : float
        Adjusted R²
    dw_statistic : float
        Durbin-Watson statistic
    n_obs : int
        Number of observations
    n_params : int
        Number of parameters
    aic : float
        Akaike Information Criterion
    bic : float
        Bayesian Information Criterion
    coef_labels : list
        Labels for coefficients
    """
    coefficients: np.ndarray
    residuals: np.ndarray
    fitted_values: np.ndarray
    std_errors: np.ndarray
    t_statistics: np.ndarray
    r_squared: float
    adj_r_squared: float
    dw_statistic: float
    n_obs: int
    n_params: int
    aic: float
    bic: float
    coef_labels: list
    
    def summary(self) -> str:
        """
        Print regression summary
        
        Returns
        -------
        str
            Summary string
        """
        summary = []
        summary.append("=" * 70)
        summary.append("Cointegration Regression Results")
        summary.append("=" * 70)
        summary.append(f"Number of observations: {self.n_obs}")
        summary.append(f"R-squared: {self.r_squared:.4f}")
        summary.append(f"Adjusted R-squared: {self.adj_r_squared:.4f}")
        summary.append(f"Durbin-Watson: {self.dw_statistic:.4f}")
        summary.append(f"AIC: {self.aic:.4f}")
        summary.append(f"BIC: {self.bic:.4f}")
        summary.append("-" * 70)
        summary.append(f"{'Variable':<15} {'Coef':<12} {'Std Err':<12} {'t':<10}")
        summary.append("-" * 70)
        
        for i, label in enumerate(self.coef_labels):
            summary.append(
                f"{label:<15} {self.coefficients[i]:>11.4f} "
                f"{self.std_errors[i]:>11.4f} {self.t_statistics[i]:>9.3f}"
            )
        
        summary.append("=" * 70)
        
        return "\n".join(summary)


def cointegration_regression(
    y: np.ndarray,
    x1: Optional[np.ndarray] = None,
    x2: Optional[np.ndarray] = None,
    include_intercept: bool = True,
    include_trend: bool = False,
    include_quadratic_trend: bool = False,
    robust_se: bool = False,
    hac_lags: Optional[int] = None
) -> CointegrationRegressionResult:
    """
    Estimate cointegration regression with I(1) and I(2) variables
    
    The regression model is (Engsted et al. 1997, equation 2):
    
    Δ^{-1}y_t = α₀ + α₁*t + α₂*t² + β₁'*x₁ₜ + β₂'*Δ^{-1}x₂ₜ + uₜ
    
    where:
    - y is an I(2) variable
    - x1 are I(1) variables
    - x2 are I(2) variables (enter as their cumulative sums)
    - Δ^{-1} denotes cumulative sum (integration)
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (n,) - should be I(2)
    x1 : np.ndarray, optional
        I(1) regressors (n, m1)
    x2 : np.ndarray, optional
        I(2) regressors (n, m2) - will be cumulated internally
    include_intercept : bool
        Include intercept
    include_trend : bool
        Include linear trend
    include_quadratic_trend : bool
        Include quadratic trend
    robust_se : bool
        Use Newey-West HAC standard errors
    hac_lags : int, optional
        Number of lags for Newey-West (auto-selected if None)
        
    Returns
    -------
    CointegrationRegressionResult
        Regression results object
        
    Notes
    -----
    Following Haldrup (1994) Theorem 1:
    - If d=0 (multicointegration): β̂₁ = Op(n^{-1}), β̂₂ = Op(n^{-2})
    - If d=1: β̂₁ is nondegenerate, β̂₂ = Op(n^{-1})
    - If d=2: both are nondegenerate
    
    Examples
    --------
    >>> from multicoint.simulation import generate_multicointegrated_system
    >>> system = generate_multicointegrated_system(
    ...     n=100, m1=1, m2=1, cointegration_order=0, random_state=42
    ... )
    >>> result = cointegration_regression(system.y, system.x1, system.x2)
    >>> result.r_squared > 0
    True
    """
    n = len(y)
    
    # Cumulate y (make it I(2) if not already)
    y_cum = cumsum_matrix(y.reshape(-1, 1)).flatten()
    
    # Build design matrix
    X_list = []
    labels = []
    
    # Deterministic components
    if include_intercept:
        X_list.append(np.ones(n))
        labels.append('intercept')
    
    if include_trend:
        t = np.arange(1, n + 1)
        X_list.append(t)
        labels.append('trend')
    
    if include_quadratic_trend:
        t = np.arange(1, n + 1)
        X_list.append(t**2)
        labels.append('trend^2')
    
    # I(1) variables
    if x1 is not None:
        if x1.ndim == 1:
            x1 = x1.reshape(-1, 1)
        m1 = x1.shape[1]
        for i in range(m1):
            X_list.append(x1[:, i])
            labels.append(f'x1_{i+1}')
    else:
        m1 = 0
    
    # I(2) variables (cumulate them)
    if x2 is not None:
        if x2.ndim == 1:
            x2 = x2.reshape(-1, 1)
        m2 = x2.shape[1]
        x2_cum = cumsum_matrix(x2)
        for i in range(m2):
            X_list.append(x2_cum[:, i])
            labels.append(f'x2_{i+1}')
    else:
        m2 = 0
    
    if len(X_list) == 0:
        raise ValueError("Must include at least one regressor")
    
    X = np.column_stack(X_list)
    
    # OLS estimation
    beta = np.linalg.lstsq(X, y_cum, rcond=None)[0]
    fitted = X @ beta
    residuals = y_cum - fitted
    
    # Standard errors
    n_params = len(beta)
    sigma2 = np.sum(residuals**2) / (n - n_params)
    
    if robust_se:
        # Newey-West HAC standard errors
        var_cov = newey_west_variance(residuals, X, lags=hac_lags)
        std_errors = np.sqrt(np.diag(var_cov))
    else:
        # Homoskedastic standard errors
        var_cov = sigma2 * np.linalg.inv(X.T @ X)
        std_errors = np.sqrt(np.diag(var_cov))
    
    # t-statistics
    t_stats = beta / std_errors
    
    # Goodness of fit
    r2 = calculate_r_squared(y_cum, fitted)
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - n_params)
    
    # Durbin-Watson
    dw = calculate_dw_statistic(residuals)
    
    # Information criteria
    aic = n * np.log(sigma2) + 2 * n_params
    bic = n * np.log(sigma2) + n_params * np.log(n)
    
    return CointegrationRegressionResult(
        coefficients=beta,
        residuals=residuals,
        fitted_values=fitted,
        std_errors=std_errors,
        t_statistics=t_stats,
        r_squared=r2,
        adj_r_squared=adj_r2,
        dw_statistic=dw,
        n_obs=n,
        n_params=n_params,
        aic=aic,
        bic=bic,
        coef_labels=labels
    )


def estimate_cointegration_parameters(
    y: np.ndarray,
    x1: Optional[np.ndarray] = None,
    x2: Optional[np.ndarray] = None,
    include_intercept: bool = True,
    include_trend: bool = False,
    method: str = 'ols'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Estimate cointegration parameters
    
    Returns separately the coefficients for I(1) and I(2) variables.
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable
    x1 : np.ndarray, optional
        I(1) regressors
    x2 : np.ndarray, optional
        I(2) regressors
    include_intercept : bool
        Include intercept
    include_trend : bool
        Include trend
    method : str
        Estimation method ('ols', 'dols', 'fmols')
        
    Returns
    -------
    beta1 : np.ndarray
        Coefficients for I(1) variables
    beta2 : np.ndarray
        Coefficients for I(2) variables
        
    Notes
    -----
    As stated in Engsted et al. (1997):
    - The one-step procedure estimates both levels of cointegration simultaneously
    - β₂ (I(2) coefficients) are estimated at rate Op(T^{-2}) under multicointegration
    - β₁ (I(1) coefficients) are estimated at rate Op(T^{-1})
    
    Examples
    --------
    >>> from multicoint.simulation import generate_multicointegrated_system
    >>> system = generate_multicointegrated_system(
    ...     n=100, m1=1, m2=1, cointegration_order=0, random_state=42
    ... )
    >>> beta1, beta2 = estimate_cointegration_parameters(
    ...     system.y, system.x1, system.x2
    ... )
    >>> beta1.shape[0] == 1
    True
    """
    if method == 'ols':
        result = cointegration_regression(
            y, x1, x2, 
            include_intercept=include_intercept,
            include_trend=include_trend
        )
        
        # Extract I(1) and I(2) coefficients
        n_deterministic = int(include_intercept) + int(include_trend)
        
        m1 = 0 if x1 is None else (1 if x1.ndim == 1 else x1.shape[1])
        m2 = 0 if x2 is None else (1 if x2.ndim == 1 else x2.shape[1])
        
        start_idx = n_deterministic
        beta1 = result.coefficients[start_idx : start_idx + m1]
        beta2 = result.coefficients[start_idx + m1 : start_idx + m1 + m2]
        
        return beta1, beta2
    
    elif method == 'dols':
        # Dynamic OLS - add leads and lags of differenced regressors
        # TODO: Implement DOLS
        raise NotImplementedError("DOLS not yet implemented")
    
    elif method == 'fmols':
        # Fully Modified OLS
        # TODO: Implement FMOLS
        raise NotImplementedError("FMOLS not yet implemented")
    
    else:
        raise ValueError(f"Unknown method: {method}")


def residual_diagnostics(residuals: np.ndarray,
                        lags: int = 10) -> Dict[str, float]:
    """
    Perform diagnostic tests on regression residuals
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals
    lags : int
        Number of lags for autocorrelation tests
        
    Returns
    -------
    dict
        Dictionary of diagnostic test statistics
        
    Examples
    --------
    >>> residuals = np.random.randn(100)
    >>> diag = residual_diagnostics(residuals)
    >>> 'dw_statistic' in diag
    True
    """
    from scipy import stats
    
    diagnostics = {}
    
    # Durbin-Watson
    diagnostics['dw_statistic'] = calculate_dw_statistic(residuals)
    
    # Jarque-Bera normality test
    jb_stat, jb_pval = stats.jarque_bera(residuals)
    diagnostics['jarque_bera_stat'] = jb_stat
    diagnostics['jarque_bera_pvalue'] = jb_pval
    
    # Ljung-Box test for autocorrelation
    from statsmodels.stats.diagnostic import acorr_ljungbox
    lb_result = acorr_ljungbox(residuals, lags=lags, return_df=False)
    diagnostics['ljung_box_stat'] = lb_result[0][-1]
    diagnostics['ljung_box_pvalue'] = lb_result[1][-1]
    
    # ARCH test
    from statsmodels.stats.diagnostic import het_arch
    arch_result = het_arch(residuals, nlags=lags)
    diagnostics['arch_lm_stat'] = arch_result[0]
    diagnostics['arch_lm_pvalue'] = arch_result[1]
    
    return diagnostics


def predict(result: CointegrationRegressionResult,
           x1_new: Optional[np.ndarray] = None,
           x2_new: Optional[np.ndarray] = None,
           n_ahead: int = 1) -> np.ndarray:
    """
    Generate predictions from cointegration regression
    
    Parameters
    ----------
    result : CointegrationRegressionResult
        Fitted regression result
    x1_new : np.ndarray, optional
        Future values of I(1) variables
    x2_new : np.ndarray, optional
        Future values of I(2) variables
    n_ahead : int
        Number of periods ahead to forecast
        
    Returns
    -------
    np.ndarray
        Predicted values
        
    Notes
    -----
    For multicointegrated systems, forecasting requires careful handling
    of the different integration orders.
    """
    # TODO: Implement proper forecasting for multicointegrated systems
    raise NotImplementedError("Forecasting not yet implemented")
