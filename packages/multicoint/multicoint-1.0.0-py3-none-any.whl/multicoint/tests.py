"""
Statistical Tests Module
========================

Unit root and cointegration tests for I(1) and I(2) variables, implementing:
- Engsted, Gonzalo, and Haldrup (1997): One-step multicointegration test
- Haldrup (1994): Residual-based ADF tests for I(2) cointegration
"""

import numpy as np
from typing import Optional, Tuple, Dict, Union
from dataclasses import dataclass
from .regression import cointegration_regression
from .critical_values import (
    CriticalValuesEngsted,
    CriticalValuesHaldrup,
    get_critical_values_engsted,
    get_critical_values_haldrup
)
from .utils import lag_matrix, select_lag_length


@dataclass
class ADFTestResult:
    """
    Results from Augmented Dickey-Fuller test
    
    Attributes
    ----------
    test_statistic : float
        ADF test statistic
    p_value : float
        Approximate p-value
    critical_values : dict
        Critical values at different significance levels
    lags_used : int
        Number of lags used in regression
    n_obs : int
        Number of observations
    reject_null : bool
        Whether to reject null hypothesis at 5% level
    """
    test_statistic: float
    p_value: Optional[float]
    critical_values: Dict[float, float]
    lags_used: int
    n_obs: int
    reject_null: bool
    
    def summary(self) -> str:
        """Return test summary"""
        summary = []
        summary.append("=" * 60)
        summary.append("Augmented Dickey-Fuller Test Results")
        summary.append("=" * 60)
        summary.append(f"Test statistic: {self.test_statistic:.4f}")
        if self.p_value is not None:
            summary.append(f"P-value: {self.p_value:.4f}")
        summary.append(f"Lags used: {self.lags_used}")
        summary.append(f"Observations: {self.n_obs}")
        summary.append("-" * 60)
        summary.append("Critical values:")
        for level, cv in self.critical_values.items():
            summary.append(f"  {level*100:>5.1f}%: {cv:>8.4f}")
        summary.append("-" * 60)
        if self.reject_null:
            summary.append("Result: REJECT null hypothesis at 5% level")
        else:
            summary.append("Result: FAIL TO REJECT null hypothesis at 5% level")
        summary.append("=" * 60)
        return "\n".join(summary)


def adf_test_i2(
    residuals: np.ndarray,
    m1: int,
    m2: int,
    lags: Optional[int] = None,
    trend_type: str = 'linear',
    significance_level: float = 0.05,
    method: str = 'engsted'
) -> ADFTestResult:
    """
    ADF test for I(2) cointegration residuals
    
    Implements the test described in:
    - Engsted et al. (1997): Tables 1 and 2
    - Haldrup (1994): Table 1
    
    The null hypothesis is that residuals are I(1), assuming that
    all I(2) variables cointegrate into an I(1) relation.
    
    The alternative is that residuals are I(0), indicating 
    multicointegration (Engsted et al.) or full cointegration (Haldrup).
    
    Parameters
    ----------
    residuals : np.ndarray
        Regression residuals from cointegration regression
    m1 : int
        Number of I(1) regressors
    m2 : int
        Number of I(2) regressors
    lags : int, optional
        Number of lags in ADF regression (auto-selected if None)
    trend_type : str
        For Engsted: 'linear' or 'quadratic' (which deterministics in cointegration regression)
        Ignored for Haldrup
    significance_level : float
        Significance level for test
    method : str
        'engsted' (Engsted et al. 1997) or 'haldrup' (Haldrup 1994)
        
    Returns
    -------
    ADFTestResult
        Test result object
        
    Notes
    -----
    As described in Engsted et al. (1997) Section 4:
    "To test whether û_t is integrated of order one, the standard augmented 
    Dickey-Fuller test is conducted. That is, the t-statistic of ρ₀ from the 
    regression Δû_t = ρ₀û_{t-1} + Σ ρⱼΔû_{t-j} + η_pt"
    
    The distribution depends on both m1 (number of I(1) regressors) and 
    m2 (number of I(2) regressors).
    
    Examples
    --------
    >>> from multicoint.simulation import generate_multicointegrated_system
    >>> from multicoint.regression import cointegration_regression
    >>> system = generate_multicointegrated_system(
    ...     n=100, m1=1, m2=1, cointegration_order=0, random_state=42
    ... )
    >>> result = cointegration_regression(system.y, system.x1, system.x2)
    >>> test = adf_test_i2(result.residuals, m1=1, m2=1, method='engsted')
    >>> isinstance(test.test_statistic, float)
    True
    """
    n = len(residuals)
    
    # Select lag length if not provided
    if lags is None:
        lags = select_lag_length(residuals, max_lags=min(10, n // 10))
    
    # Ensure we have enough observations
    if n - lags - 1 < 10:
        raise ValueError("Insufficient observations for ADF test")
    
    # Construct ADF regression: Δû_t = ρ₀û_{t-1} + Σ ρⱼΔû_{t-j} + η_t
    delta_u = np.diff(residuals)
    u_lagged = residuals[:-1]
    
    # Design matrix
    X_list = [u_lagged[lags:]]  # û_{t-1}
    
    # Add lagged differences if lags > 0
    if lags > 0:
        delta_u_lagged = lag_matrix(delta_u, lags)
        X_list.append(delta_u_lagged)
    
    X = np.column_stack(X_list) if lags > 0 else u_lagged[lags:].reshape(-1, 1)
    y = delta_u[lags:]
    
    # OLS estimation
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    fitted = X @ beta
    resid = y - fitted
    
    # Calculate standard error of ρ₀
    sigma2 = np.sum(resid**2) / (len(y) - len(beta))
    var_cov = sigma2 * np.linalg.inv(X.T @ X)
    se_rho0 = np.sqrt(var_cov[0, 0])
    
    # ADF test statistic
    rho0 = beta[0]
    adf_stat = rho0 / se_rho0
    
    # Get critical values
    if method.lower() == 'engsted':
        cv_dict = get_critical_values_engsted(
            m1=m1, m2=m2, n=n, trend_type=trend_type, quantile=None
        )
    elif method.lower() == 'haldrup':
        cv_dict = get_critical_values_haldrup(
            m1=m1, m2=m2, n=n, quantile=None
        )
    else:
        raise ValueError("method must be 'engsted' or 'haldrup'")
    
    # Determine rejection
    cv_5pct = cv_dict[significance_level]
    reject = adf_stat < cv_5pct  # One-sided test
    
    return ADFTestResult(
        test_statistic=adf_stat,
        p_value=None,  # No exact p-values available
        critical_values=cv_dict,
        lags_used=lags,
        n_obs=n,
        reject_null=reject
    )


@dataclass
class MulticointegrationTestResult:
    """
    Results from multicointegration test
    
    Attributes
    ----------
    is_multicointegrated : bool
        Whether multicointegration is detected
    adf_test : ADFTestResult
        ADF test results on cointegration residuals
    cointegration_regression : object
        Regression results
    beta1_estimate : np.ndarray
        Estimated coefficients for I(1) variables
    beta2_estimate : np.ndarray
        Estimated coefficients for I(2) variables
    """
    is_multicointegrated: bool
    adf_test: ADFTestResult
    cointegration_regression: object
    beta1_estimate: Optional[np.ndarray]
    beta2_estimate: Optional[np.ndarray]
    
    def summary(self) -> str:
        """Return test summary"""
        summary = []
        summary.append("\n")
        summary.append("=" * 70)
        summary.append("Multicointegration Test Results")
        summary.append("Based on Engsted, Gonzalo, and Haldrup (1997)")
        summary.append("=" * 70)
        
        if self.beta1_estimate is not None:
            summary.append("\nEstimated I(1) coefficients (β₁):")
            summary.append(str(self.beta1_estimate))
        
        if self.beta2_estimate is not None:
            summary.append("\nEstimated I(2) coefficients (β₂):")
            summary.append(str(self.beta2_estimate))
        
        summary.append("\n" + "=" * 70)
        summary.append("ADF Test on Cointegration Residuals")
        summary.append("=" * 70)
        summary.append(f"H₀: Residuals are I(1) (no multicointegration)")
        summary.append(f"H₁: Residuals are I(0) (multicointegration)")
        summary.append("")
        summary.append(f"Test statistic: {self.adf_test.test_statistic:.4f}")
        summary.append(f"5% critical value: {self.adf_test.critical_values[0.05]:.4f}")
        summary.append("")
        
        if self.is_multicointegrated:
            summary.append("✓ MULTICOINTEGRATION DETECTED")
            summary.append("  (Reject null at 5% level)")
        else:
            summary.append("✗ NO MULTICOINTEGRATION DETECTED")
            summary.append("  (Fail to reject null at 5% level)")
        
        summary.append("=" * 70)
        
        return "\n".join(summary)


def multicointegration_test(
    y: np.ndarray,
    x1: Optional[np.ndarray] = None,
    x2: Optional[np.ndarray] = None,
    include_intercept: bool = True,
    include_trend: bool = False,
    include_quadratic_trend: bool = False,
    lags: Optional[int] = None,
    significance_level: float = 0.05,
    verbose: bool = True
) -> MulticointegrationTestResult:
    """
    Test for multicointegration using one-step procedure
    
    Implements the one-step procedure described in Engsted, Gonzalo, and 
    Haldrup (1997), Section 4.
    
    The procedure:
    1. Estimate cointegration regression: Δ⁻¹y_t = α + β₁'x₁ₜ + β₂'Δ⁻¹x₂ₜ + u_t
    2. Test whether residuals u_t are I(1) vs I(0) using ADF test
    3. Use special critical values that account for I(2) variables
    
    Parameters
    ----------
    y : np.ndarray
        Dependent variable (should be I(2))
    x1 : np.ndarray, optional
        I(1) regressors (n, m1)
    x2 : np.ndarray, optional
        I(2) regressors (n, m2)
    include_intercept : bool
        Include intercept in cointegration regression
    include_trend : bool
        Include linear trend
    include_quadratic_trend : bool
        Include quadratic trend
    lags : int, optional
        Number of lags in ADF test
    significance_level : float
        Significance level for test
    verbose : bool
        Print results
        
    Returns
    -------
    MulticointegrationTestResult
        Test result object
        
    Notes
    -----
    As stated in Engsted et al. (1997):
    "The procedure that we propose simultaneously tests both levels of 
    cointegration by exploiting the fact that multicointegration implies 
    I(2) cointegration in a particular way."
    
    "provided there is multicointegration, the cointegration parameter at 
    the first level will be estimated at the super-super-consistent rate, 
    Op(T²), in the single-step procedure."
    
    Examples
    --------
    >>> from multicoint.simulation import generate_multicointegrated_system
    >>> system = generate_multicointegrated_system(
    ...     n=100, m1=1, m2=1, cointegration_order=0, random_state=42
    ... )
    >>> result = multicointegration_test(
    ...     system.y, system.x1, system.x2, verbose=False
    ... )
    >>> isinstance(result.is_multicointegrated, bool)
    True
    """
    # Step 1: Estimate cointegration regression
    reg_result = cointegration_regression(
        y=y,
        x1=x1,
        x2=x2,
        include_intercept=include_intercept,
        include_trend=include_trend,
        include_quadratic_trend=include_quadratic_trend
    )
    
    # Determine m1 and m2
    m1 = 0 if x1 is None else (1 if x1.ndim == 1 else x1.shape[1])
    m2 = 0 if x2 is None else (1 if x2.ndim == 1 else x2.shape[1])
    
    # Extract coefficient estimates
    n_deterministic = int(include_intercept) + int(include_trend) + int(include_quadratic_trend)
    beta1_est = reg_result.coefficients[n_deterministic : n_deterministic + m1] if m1 > 0 else None
    beta2_est = reg_result.coefficients[n_deterministic + m1:] if m2 > 0 else None
    
    # Determine trend type for critical values
    if include_quadratic_trend:
        trend_type = 'quadratic'
    elif include_trend:
        trend_type = 'linear'
    else:
        trend_type = 'linear'  # Default
    
    # Step 2: ADF test on residuals
    adf_result = adf_test_i2(
        residuals=reg_result.residuals,
        m1=m1,
        m2=m2,
        lags=lags,
        trend_type=trend_type,
        significance_level=significance_level,
        method='engsted'
    )
    
    # Create result object
    result = MulticointegrationTestResult(
        is_multicointegrated=adf_result.reject_null,
        adf_test=adf_result,
        cointegration_regression=reg_result,
        beta1_estimate=beta1_est,
        beta2_estimate=beta2_est
    )
    
    if verbose:
        print(result.summary())
    
    return result


def hasza_fuller_test(
    x: np.ndarray,
    lags: Optional[int] = None,
    include_intercept: bool = True,
    include_trend: bool = False
) -> ADFTestResult:
    """
    Hasza-Fuller test for I(2) unit root
    
    Tests the null hypothesis that a series has two unit roots (I(2))
    against the alternative of one unit root (I(1)).
    
    Parameters
    ----------
    x : np.ndarray
        Time series
    lags : int, optional
        Number of lags (auto-selected if None)
    include_intercept : bool
        Include intercept
    include_trend : bool
        Include trend
        
    Returns
    -------
    ADFTestResult
        Test result
        
    References
    ----------
    Hasza, D.P. and Fuller, W.A. (1979), "Estimation of autoregressive 
    processes with unit roots", Annals of Statistics 7, 1106-1120.
    
    Notes
    -----
    This tests: H₀: Δ²x_t is stationary vs H₁: Δx_t has a unit root
    
    Examples
    --------
    >>> from multicoint.simulation import generate_i2_process
    >>> x = generate_i2_process(100, random_state=42)
    >>> result = hasza_fuller_test(x)
    >>> isinstance(result.test_statistic, float)
    True
    """
    # This is a simplified implementation
    # Full implementation would follow Hasza and Fuller (1979)
    
    from statsmodels.tsa.stattools import adfuller
    
    # Test second difference
    d2x = np.diff(x, n=2)
    
    result = adfuller(d2x, maxlag=lags, autolag='AIC' if lags is None else None)
    
    adf_stat = result[0]
    p_value = result[1]
    cv_dict = {0.01: result[4]['1%'], 
               0.05: result[4]['5%'], 
               0.10: result[4]['10%']}
    
    return ADFTestResult(
        test_statistic=adf_stat,
        p_value=p_value,
        critical_values=cv_dict,
        lags_used=result[2],
        n_obs=len(d2x),
        reject_null=p_value < 0.05
    )


def granger_lee_multicointegration_test(
    production: np.ndarray,
    sales: np.ndarray,
    significance_level: float = 0.05
) -> Dict:
    """
    Test for multicointegration in Granger-Lee production-sales-inventory framework
    
    This implements the specific test for the example in Granger and Lee (1989, 1990).
    
    Tests:
    1. Whether production and sales are CI(1,1)
    2. Whether inventory level cointegrates with production/sales (multicointegration)
    
    Parameters
    ----------
    production : np.ndarray
        Production series (Y_t)
    sales : np.ndarray
        Sales series (X_t)
    significance_level : float
        Significance level
        
    Returns
    -------
    dict
        Dictionary of test results
        
    References
    ----------
    Granger, C.W.J. and Lee, T. (1989), "Investigation of production, sales 
    and inventory relationships using multicointegration and non-symmetric 
    error correction models"
    
    Examples
    --------
    >>> from multicoint.simulation import generate_granger_lee_example
    >>> prod, sales, inv = generate_granger_lee_example(100, random_state=42)
    >>> results = granger_lee_multicointegration_test(prod, sales)
    >>> 'multicointegration_detected' in results
    True
    """
    n = len(production)
    
    # Calculate inventory investment and level
    inv_investment = production - sales
    inventory_level = np.cumsum(inv_investment)
    
    # Test 1: Are production and sales cointegrated? (should be I(0))
    # We expect Z_t = Y_t - X_t to be I(0)
    test1 = multicointegration_test(
        y=production,
        x1=sales.reshape(-1, 1),
        x2=None,
        verbose=False
    )
    
    # Test 2: Does inventory level cointegrate with production/sales?
    # We expect S_t - γX_t to be I(0) (or S_t - γY_t)
    test2 = multicointegration_test(
        y=inventory_level,
        x1=sales.reshape(-1, 1),
        x2=None,
        verbose=False
    )
    
    results = {
        'production_sales_cointegration': test1.is_multicointegrated,
        'inventory_multicointegration': test2.is_multicointegrated,
        'multicointegration_detected': test1.is_multicointegrated and test2.is_multicointegrated,
        'test1_results': test1,
        'test2_results': test2
    }
    
    return results
