"""
multicoint: Multicointegration Analysis for I(1) and I(2) Time Series
======================================================================

A comprehensive Python package for testing and analyzing multicointegration 
in I(1) and I(2) time series based on:

- Engsted, Gonzalo, and Haldrup (1997): Testing for multicointegration
- Haldrup (1994): Single-equation cointegration regressions with I(1) and I(2) variables

Author: Dr Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/multicoint
"""

__version__ = "1.0.0"
__author__ = "Dr Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

# Import main functions
from .critical_values import (
    get_critical_values_engsted,
    get_critical_values_haldrup,
    CriticalValuesEngsted,
    CriticalValuesHaldrup
)

from .simulation import (
    generate_i1_process,
    generate_i2_process,
    generate_multicointegrated_system,
    generate_granger_lee_example,
    MulticointegrationSystem
)

from .regression import (
    cointegration_regression,
    CointegrationRegressionResult
)

from .tests import (
    adf_test_i2,
    multicointegration_test,
    granger_lee_multicointegration_test,
    ADFTestResult,
    MulticointegrationTestResult
)

from .utils import (
    integration_order,
    calculate_dw_statistic,
    calculate_r_squared,
    lag_matrix,
    cumsum_matrix,
    demean,
    detrend
)

from .tests import (
    hasza_fuller_test
)

__all__ = [
    # Critical values
    'get_critical_values_engsted',
    'get_critical_values_haldrup',
    'CriticalValuesEngsted',
    'CriticalValuesHaldrup',
    
    # Simulation
    'generate_i1_process',
    'generate_i2_process',
    'generate_multicointegrated_system',
    'generate_granger_lee_example',
    'MulticointegrationSystem',
    
    # Regression and tests
    'cointegration_regression',
    'adf_test_i2',
    'multicointegration_test',
    'granger_lee_multicointegration_test',
    'CointegrationRegressionResult',
    'ADFTestResult',
    'MulticointegrationTestResult',
    
    # Utilities
    'integration_order',
    'hasza_fuller_test',
    'calculate_dw_statistic',
    'calculate_r_squared',
    'lag_matrix',
    'cumsum_matrix',
    'demean',
    'detrend'
]
