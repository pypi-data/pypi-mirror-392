"""
Critical Values Module
======================

This module contains critical values for cointegration tests with I(2) variables from:
- Engsted, Gonzalo, and Haldrup (1997), Tables 1 and 2  
- Haldrup (1994), Table 1

The critical values depend on:
- m1: number of I(1) regressors
- m2: number of I(2) regressors
- Sample size (n)
- Deterministic components (intercept, trend, quadratic trend)

References
----------
Engsted, T., Gonzalo, J., and Haldrup, N. (1997). "Testing for multicointegration". 
Economics Letters, 56(3), 259-266.

Haldrup, N. (1994). "The asymptotics of single-equation cointegration regressions 
with I(1) and I(2) variables". Journal of Econometrics, 63(1), 153-181.
"""

import numpy as np
from typing import Dict, Optional, Union
from scipy.interpolate import interp1d


class CriticalValuesEngsted:
    """
    Critical values from Engsted, Gonzalo, and Haldrup (1997)
    
    These are for the cointegration ADF test allowing for I(2) variables.
    The null hypothesis is that residuals are I(1) under the assumption that
    all I(2) variables cointegrate into an I(1) relation.
    
    Under the alternative, residuals are I(0), indicating multicointegration.
    """
    
    # Table 1: Linear trend case (intercept + trend in cointegration regression)
    LINEAR_TREND = {
        0: {
            1: {
                25:  {0.01: -5.21, 0.025: -4.72, 0.05: -4.29, 0.10: -3.88},
                50:  {0.01: -4.66, 0.025: -4.33, 0.05: -4.01, 0.10: -3.67},
                100: {0.01: -4.55, 0.025: -4.18, 0.05: -3.90, 0.10: -3.59},
                250: {0.01: -4.41, 0.025: -4.08, 0.05: -3.83, 0.10: -3.51},
                500: {0.01: -4.33, 0.025: -4.04, 0.05: -3.78, 0.10: -3.49}
            },
            2: {
                25:  {0.01: -5.81, 0.025: -5.25, 0.05: -4.83, 0.10: -4.41},
                50:  {0.01: -5.14, 0.025: -4.77, 0.05: -4.45, 0.10: -4.10},
                100: {0.01: -4.93, 0.025: -4.56, 0.05: -4.31, 0.10: -3.98},
                250: {0.01: -4.81, 0.025: -4.49, 0.05: -4.20, 0.10: -3.91},
                500: {0.01: -4.75, 0.025: -4.42, 0.05: -4.14, 0.10: -3.84}
            }
        },
        1: {
            1: {
                25:  {0.01: -5.60, 0.025: -5.10, 0.05: -4.71, 0.10: -4.30},
                50:  {0.01: -5.11, 0.025: -4.70, 0.05: -4.42, 0.10: -4.08},
                100: {0.01: -4.85, 0.025: -4.54, 0.05: -4.26, 0.10: -3.94},
                250: {0.01: -4.73, 0.025: -4.43, 0.05: -4.19, 0.10: -3.89},
                500: {0.01: -4.73, 0.025: -4.42, 0.05: -4.15, 0.10: -3.87}
            },
            2: {
                25:  {0.01: -6.24, 0.025: -5.68, 0.05: -5.21, 0.10: -4.80},
                50:  {0.01: -5.62, 0.025: -5.22, 0.05: -4.89, 0.10: -4.51},
                100: {0.01: -5.23, 0.025: -4.90, 0.05: -4.62, 0.10: -4.29},
                250: {0.01: -5.11, 0.025: -4.77, 0.05: -4.50, 0.10: -4.20},
                500: {0.01: -5.05, 0.025: -4.74, 0.05: -4.48, 0.10: -4.18}
            }
        },
        2: {
            1: {
                25:  {0.01: -6.09, 0.025: -5.57, 0.05: -5.14, 0.10: -4.69},
                50:  {0.01: -5.47, 0.025: -5.07, 0.05: -4.74, 0.10: -4.38},
                100: {0.01: -5.21, 0.025: -4.86, 0.05: -4.58, 0.10: -4.26},
                250: {0.01: -5.07, 0.025: -4.79, 0.05: -4.51, 0.10: -4.20},
                500: {0.01: -5.00, 0.025: -4.73, 0.05: -4.48, 0.10: -4.18}
            },
            2: {
                25:  {0.01: -6.70, 0.025: -6.17, 0.05: -5.70, 0.10: -5.22},
                50:  {0.01: -5.98, 0.025: -5.53, 0.05: -5.17, 0.10: -4.79},
                100: {0.01: -5.59, 0.025: -5.19, 0.05: -4.93, 0.10: -4.62},
                250: {0.01: -5.35, 0.025: -5.07, 0.05: -4.80, 0.10: -4.51},
                500: {0.01: -5.34, 0.025: -5.02, 0.05: -4.75, 0.10: -4.46}
            }
        },
        3: {
            1: {
                25:  {0.01: -6.47, 0.025: -5.95, 0.05: -5.53, 0.10: -5.08},
                50:  {0.01: -5.89, 0.025: -5.43, 0.05: -5.13, 0.10: -4.76},
                100: {0.01: -5.52, 0.025: -5.18, 0.05: -4.91, 0.10: -4.59},
                250: {0.01: -5.38, 0.025: -5.05, 0.05: -4.78, 0.10: -4.74},
                500: {0.01: -5.34, 0.025: -5.04, 0.05: -4.78, 0.10: -4.50}
            },
            2: {
                25:  {0.01: -7.19, 0.025: -6.63, 0.05: -6.08, 0.10: -5.89},
                50:  {0.01: -6.23, 0.025: -5.81, 0.05: -5.48, 0.10: -5.12},
                100: {0.01: -5.97, 0.025: -5.58, 0.05: -5.25, 0.10: -4.92},
                250: {0.01: -5.69, 0.025: -5.37, 0.05: -5.07, 0.10: -4.80},
                500: {0.01: -5.67, 0.025: -5.33, 0.05: -5.06, 0.10: -4.76}
            }
        },
        4: {
            1: {
                25:  {0.01: -6.95, 0.025: -6.37, 0.05: -5.90, 0.10: -5.44},
                50:  {0.01: -6.35, 0.025: -5.85, 0.05: -5.47, 0.10: -5.10},
                100: {0.01: -5.86, 0.025: -5.49, 0.05: -5.20, 0.10: -4.89},
                250: {0.01: -5.66, 0.025: -5.35, 0.05: -5.08, 0.10: -4.77},
                500: {0.01: -5.63, 0.025: -5.31, 0.05: -5.06, 0.10: -4.76}
            },
            2: {
                25:  {0.01: -7.61, 0.025: -6.93, 0.05: -6.43, 0.10: -5.91},
                50:  {0.01: -6.64, 0.025: -6.18, 0.05: -5.82, 0.10: -5.41},
                100: {0.01: -6.09, 0.025: -5.76, 0.05: -5.50, 0.10: -5.16},
                250: {0.01: -5.95, 0.025: -5.61, 0.05: -5.34, 0.10: -5.04},
                500: {0.01: -5.92, 0.025: -5.56, 0.05: -5.29, 0.10: -5.02}
            }
        }
    }
    
    # Table 2: Quadratic trend case (intercept + trend + quadratic trend)
    QUADRATIC_TREND = {
        0: {
            1: {
                25:  {0.01: -5.77, 0.025: -5.28, 0.05: -4.86, 0.10: -4.43},
                50:  {0.01: -5.20, 0.025: -4.81, 0.05: -4.47, 0.10: -4.12},
                100: {0.01: -4.94, 0.025: -4.60, 0.05: -4.32, 0.10: -4.00},
                250: {0.01: -4.77, 0.025: -4.47, 0.05: -4.21, 0.10: -3.92},
                500: {0.01: -4.73, 0.025: -4.43, 0.05: -4.17, 0.10: -3.88}
            },
            2: {
                25:  {0.01: -6.44, 0.025: -5.85, 0.05: -5.42, 0.10: -4.96},
                50:  {0.01: -5.61, 0.025: -5.21, 0.05: -4.88, 0.10: -4.52},
                100: {0.01: -5.33, 0.025: -4.97, 0.05: -4.67, 0.10: -4.34},
                250: {0.01: -5.13, 0.025: -4.79, 0.05: -4.52, 0.10: -4.23},
                500: {0.01: -5.07, 0.025: -4.76, 0.05: -4.50, 0.10: -4.21}
            }
        },
        1: {
            1: {
                25:  {0.01: -6.21, 0.025: -5.69, 0.05: -5.27, 0.10: -4.83},
                50:  {0.01: -5.56, 0.025: -5.16, 0.05: -4.83, 0.10: -4.47},
                100: {0.01: -5.29, 0.025: -4.93, 0.05: -4.64, 0.10: -4.32},
                250: {0.01: -5.11, 0.025: -4.79, 0.05: -4.52, 0.10: -4.23},
                500: {0.01: -5.05, 0.025: -4.75, 0.05: -4.49, 0.10: -4.20}
            },
            2: {
                25:  {0.01: -6.85, 0.025: -6.30, 0.05: -5.82, 0.10: -5.33},
                50:  {0.01: -5.99, 0.025: -5.58, 0.05: -5.22, 0.10: -4.86},
                100: {0.01: -5.63, 0.025: -5.27, 0.05: -4.98, 0.10: -4.65},
                250: {0.01: -5.43, 0.025: -5.09, 0.05: -4.84, 0.10: -4.54},
                500: {0.01: -5.35, 0.025: -5.05, 0.05: -4.78, 0.10: -4.49}
            }
        },
        2: {
            1: {
                25:  {0.01: -6.66, 0.025: -6.10, 0.05: -5.65, 0.10: -5.20},
                50:  {0.01: -5.92, 0.025: -5.50, 0.05: -5.17, 0.10: -4.82},
                100: {0.01: -5.57, 0.025: -5.23, 0.05: -4.95, 0.10: -4.63},
                250: {0.01: -5.42, 0.025: -5.08, 0.05: -4.82, 0.10: -4.52},
                500: {0.01: -5.36, 0.025: -5.04, 0.05: -4.77, 0.10: -4.48}
            },
            2: {
                25:  {0.01: -7.32, 0.025: -6.68, 0.05: -6.21, 0.10: -5.69},
                50:  {0.01: -6.35, 0.025: -5.90, 0.05: -5.54, 0.10: -5.16},
                100: {0.01: -5.90, 0.025: -5.54, 0.05: -5.25, 0.10: -4.92},
                250: {0.01: -5.69, 0.025: -5.37, 0.05: -5.10, 0.10: -4.80},
                500: {0.01: -5.61, 0.025: -5.29, 0.05: -5.04, 0.10: -4.76}
            }
        },
        3: {
            1: {
                25:  {0.01: -7.12, 0.025: -6.51, 0.05: -6.05, 0.10: -5.55},
                50:  {0.01: -6.27, 0.025: -5.85, 0.05: -5.50, 0.10: -5.12},
                100: {0.01: -5.90, 0.025: -5.54, 0.05: -5.25, 0.10: -4.91},
                250: {0.01: -5.71, 0.025: -5.38, 0.05: -5.11, 0.10: -4.81},
                500: {0.01: -5.60, 0.025: -5.30, 0.05: -5.04, 0.10: -4.76}
            },
            2: {
                25:  {0.01: -7.68, 0.025: -7.06, 0.05: -6.55, 0.10: -6.03},
                50:  {0.01: -6.63, 0.025: -6.23, 0.05: -5.86, 0.10: -5.46},
                100: {0.01: -6.19, 0.025: -5.85, 0.05: -5.55, 0.10: -5.22},
                250: {0.01: -5.96, 0.025: -5.64, 0.05: -5.37, 0.10: -5.07},
                500: {0.01: -5.85, 0.025: -5.55, 0.05: -5.30, 0.10: -5.02}
            }
        },
        4: {
            1: {
                25:  {0.01: -7.61, 0.025: -6.93, 0.05: -6.43, 0.10: -5.91},
                50:  {0.01: -6.56, 0.025: -6.15, 0.05: -5.79, 0.10: -5.41},
                100: {0.01: -6.18, 0.025: -5.81, 0.05: -5.52, 0.10: -5.19},
                250: {0.01: -5.96, 0.025: -5.64, 0.05: -5.36, 0.10: -5.05},
                500: {0.01: -5.87, 0.025: -5.57, 0.05: -5.30, 0.10: -5.01}
            },
            2: {
                25:  {0.01: -8.18, 0.025: -7.47, 0.05: -6.93, 0.10: -6.38},
                50:  {0.01: -7.00, 0.025: -6.55, 0.05: -6.16, 0.10: -5.76},
                100: {0.01: -6.47, 0.025: -6.10, 0.05: -5.80, 0.10: -5.47},
                250: {0.01: -6.21, 0.025: -5.87, 0.05: -5.60, 0.10: -5.31},
                500: {0.01: -6.12, 0.025: -5.80, 0.05: -5.54, 0.10: -5.26}
            }
        }
    }
    
    @classmethod
    def get_critical_value(cls, m1: int, m2: int, n: int, 
                          quantile: float = 0.05,
                          trend_type: str = 'linear') -> float:
        """
        Get critical value for given parameters with interpolation
        
        Parameters
        ----------
        m1 : int
            Number of I(1) regressors
        m2 : int
            Number of I(2) regressors
        n : int
            Sample size
        quantile : float
            Significance level (0.01, 0.025, 0.05, or 0.10)
        trend_type : str
            'linear' for intercept + trend, 'quadratic' for intercept + trend + trend²
            
        Returns
        -------
        float
            Critical value (interpolated if needed)
        """
        if trend_type.lower() == 'linear':
            table = cls.LINEAR_TREND
        elif trend_type.lower() == 'quadratic':
            table = cls.QUADRATIC_TREND
        else:
            raise ValueError("trend_type must be 'linear' or 'quadratic'")
        
        if m1 not in table or m2 not in table[m1]:
            raise ValueError(f"No critical values for m1={m1}, m2={m2}")
        
        available_quantiles = [0.01, 0.025, 0.05, 0.10]
        if quantile not in available_quantiles:
            raise ValueError(f"quantile must be one of {available_quantiles}")
        
        data = table[m1][m2]
        sample_sizes = sorted(data.keys())
        
        if n in sample_sizes:
            return data[n][quantile]
        
        # Interpolate for sample sizes not in table
        if n < min(sample_sizes):
            return data[min(sample_sizes)][quantile]
        if n > max(sample_sizes):
            return data[max(sample_sizes)][quantile]
        
        # Linear interpolation
        values = [data[size][quantile] for size in sample_sizes]
        interpolator = interp1d(sample_sizes, values, kind='linear')
        return float(interpolator(n))


class CriticalValuesHaldrup:
    """
    Critical values from Haldrup (1994), Table 1
    
    These are for the cointegration ADF test with intercept only.
    Same null and alternative as Engsted et al.
    """
    
    # Table 1: Intercept case
    INTERCEPT = {
        0: {
            1: {
                25:  {0.01: -4.45, 0.025: -4.02, 0.05: -3.68, 0.10: -3.30},
                50:  {0.01: -4.18, 0.025: -3.82, 0.05: -3.51, 0.10: -3.16},
                100: {0.01: -4.09, 0.025: -3.70, 0.05: -3.42, 0.10: -3.12},
                250: {0.01: -4.02, 0.025: -3.65, 0.05: -3.38, 0.10: -3.08},
                500: {0.01: -3.99, 0.025: -3.67, 0.05: -3.38, 0.10: -3.08}
            },
            2: {
                25:  {0.01: -5.21, 0.025: -4.71, 0.05: -4.32, 0.10: -3.90},
                50:  {0.01: -4.70, 0.025: -4.34, 0.05: -4.02, 0.10: -3.70},
                100: {0.01: -4.51, 0.025: -4.15, 0.05: -3.86, 0.10: -3.54},
                250: {0.01: -4.35, 0.025: -4.06, 0.05: -3.80, 0.10: -3.49},
                500: {0.01: -4.42, 0.025: -4.07, 0.05: -3.79, 0.10: -3.49}
            }
        },
        1: {
            1: {
                25:  {0.01: -5.10, 0.025: -4.60, 0.05: -4.21, 0.10: -3.79},
                50:  {0.01: -4.65, 0.025: -4.25, 0.05: -3.93, 0.10: -3.60},
                100: {0.01: -4.51, 0.025: -4.17, 0.05: -3.89, 0.10: -3.55},
                250: {0.01: -4.39, 0.025: -4.06, 0.05: -3.80, 0.10: -3.49},
                500: {0.01: -4.40, 0.025: -4.08, 0.05: -3.80, 0.10: -3.48}
            },
            2: {
                25:  {0.01: -5.73, 0.025: -5.20, 0.05: -4.79, 0.10: -4.35},
                50:  {0.01: -5.15, 0.025: -4.72, 0.05: -4.40, 0.10: -4.06},
                100: {0.01: -4.85, 0.025: -4.56, 0.05: -4.26, 0.10: -3.94},
                250: {0.01: -4.71, 0.025: -4.45, 0.05: -4.18, 0.10: -3.88},
                500: {0.01: -4.70, 0.025: -4.38, 0.05: -4.09, 0.10: -3.83}
            }
        },
        2: {
            1: {
                25:  {0.01: -5.50, 0.025: -5.02, 0.05: -4.64, 0.10: -4.23},
                50:  {0.01: -4.93, 0.025: -4.64, 0.05: -4.30, 0.10: -3.99},
                100: {0.01: -4.81, 0.025: -4.49, 0.05: -4.25, 0.10: -3.93},
                250: {0.01: -4.77, 0.025: -4.41, 0.05: -4.16, 0.10: -3.88},
                500: {0.01: -4.73, 0.025: -4.41, 0.05: -4.15, 0.10: -3.83}
            },
            2: {
                25:  {0.01: -6.15, 0.025: -5.66, 0.05: -5.22, 0.10: -4.75},
                50:  {0.01: -5.54, 0.025: -5.14, 0.05: -4.77, 0.10: -4.42},
                100: {0.01: -5.29, 0.025: -4.90, 0.05: -4.59, 0.10: -4.26},
                250: {0.01: -5.06, 0.025: -4.76, 0.05: -4.49, 0.10: -4.19},
                500: {0.01: -4.99, 0.025: -4.68, 0.05: -4.44, 0.10: -4.16}
            }
        },
        3: {
            1: {
                25:  {0.01: -6.02, 0.025: -5.49, 0.05: -5.09, 0.10: -4.64},
                50:  {0.01: -5.38, 0.025: -5.04, 0.05: -4.71, 0.10: -4.36},
                100: {0.01: -5.20, 0.025: -4.89, 0.05: -4.56, 0.10: -4.25},
                250: {0.01: -5.05, 0.025: -4.75, 0.05: -4.48, 0.10: -4.16},
                500: {0.01: -5.05, 0.025: -4.71, 0.05: -4.48, 0.10: -4.17}
            },
            2: {
                25:  {0.01: -6.68, 0.025: -6.09, 0.05: -5.60, 0.10: -5.12},
                50:  {0.01: -5.76, 0.025: -5.38, 0.05: -5.08, 0.10: -4.75},
                100: {0.01: -5.58, 0.025: -5.23, 0.05: -4.92, 0.10: -4.60},
                250: {0.01: -5.44, 0.025: -5.12, 0.05: -4.83, 0.10: -4.52},
                500: {0.01: -5.37, 0.025: -5.06, 0.05: -4.80, 0.10: -4.48}
            }
        },
        4: {
            1: {
                25:  {0.01: -6.50, 0.025: -5.98, 0.05: -5.49, 0.10: -5.03},
                50:  {0.01: -5.81, 0.025: -5.41, 0.05: -5.09, 0.10: -4.72},
                100: {0.01: -5.58, 0.025: -5.23, 0.05: -4.93, 0.10: -4.59},
                250: {0.01: -5.39, 0.025: -5.05, 0.05: -4.28, 0.10: -4.48},
                500: {0.01: -5.36, 0.025: -5.03, 0.05: -4.75, 0.10: -4.45}
            },
            2: {
                25:  {0.01: -6.99, 0.025: -6.41, 0.05: -6.01, 0.10: -5.53},
                50:  {0.01: -6.24, 0.025: -5.82, 0.05: -5.48, 0.10: -5.10},
                100: {0.01: -5.88, 0.025: -5.50, 0.05: -5.20, 0.10: -4.89},
                250: {0.01: -5.64, 0.025: -5.33, 0.05: -5.07, 0.10: -4.77},
                500: {0.01: -5.60, 0.025: -5.31, 0.05: -5.03, 0.10: -4.74}
            }
        }
    }
    
    @classmethod
    def get_critical_value(cls, m1: int, m2: int, n: int, 
                          quantile: float = 0.05) -> float:
        """
        Get critical value for given parameters with interpolation
        
        Parameters
        ----------
        m1 : int
            Number of I(1) regressors
        m2 : int
            Number of I(2) regressors
        n : int
            Sample size
        quantile : float
            Significance level (0.01, 0.025, 0.05, or 0.10)
            
        Returns
        -------
        float
            Critical value (interpolated if needed)
        """
        table = cls.INTERCEPT
        
        if m1 not in table or m2 not in table[m1]:
            raise ValueError(f"No critical values for m1={m1}, m2={m2}")
        
        available_quantiles = [0.01, 0.025, 0.05, 0.10]
        if quantile not in available_quantiles:
            raise ValueError(f"quantile must be one of {available_quantiles}")
        
        data = table[m1][m2]
        sample_sizes = sorted(data.keys())
        
        if n in sample_sizes:
            return data[n][quantile]
        
        # Interpolate for sample sizes not in table
        if n < min(sample_sizes):
            return data[min(sample_sizes)][quantile]
        if n > max(sample_sizes):
            return data[max(sample_sizes)][quantile]
        
        # Linear interpolation
        values = [data[size][quantile] for size in sample_sizes]
        interpolator = interp1d(sample_sizes, values, kind='linear')
        return float(interpolator(n))


def get_critical_values_engsted(m1: int, m2: int, n: int,
                               quantile: Optional[float] = None,
                               trend_type: str = 'linear') -> Union[float, Dict[float, float]]:
    """
    Convenience function to get Engsted et al. (1997) critical values
    
    Parameters
    ----------
    m1 : int
        Number of I(1) regressors
    m2 : int
        Number of I(2) regressors
    n : int
        Sample size
    quantile : float or None
        If provided, return single value for this quantile
        If None, return dict with all quantiles
    trend_type : str
        'linear' or 'quadratic'
    
    Returns
    -------
    float or dict
        Critical value(s)
        
    Examples
    --------
    >>> # Get 5% critical value
    >>> cv = get_critical_values_engsted(m1=1, m2=1, n=100, quantile=0.05)
    >>> # Get all quantiles
    >>> cvs = get_critical_values_engsted(m1=1, m2=1, n=100)
    """
    quantiles = [0.01, 0.025, 0.05, 0.10]
    result = {}
    for q in quantiles:
        result[q] = CriticalValuesEngsted.get_critical_value(
            m1, m2, n, q, trend_type
        )
    
    if quantile is not None:
        return result[quantile]
    return result


def get_critical_values_haldrup(m1: int, m2: int, n: int,
                               quantile: Optional[float] = None) -> Union[float, Dict[float, float]]:
    """
    Convenience function to get Haldrup (1994) critical values
    
    Parameters
    ----------
    m1 : int
        Number of I(1) regressors
    m2 : int
        Number of I(2) regressors
    n : int
        Sample size
    quantile : float or None
        If provided, return single value for this quantile
        If None, return dict with all quantiles
    
    Returns
    -------
    float or dict
        Critical value(s)
        
    Examples
    --------
    >>> # Get 5% critical value
    >>> cv = get_critical_values_haldrup(m1=1, m2=1, n=100, quantile=0.05)
    >>> # Get all quantiles
    >>> cvs = get_critical_values_haldrup(m1=1, m2=1, n=100)
    """
    quantiles = [0.01, 0.025, 0.05, 0.10]
    result = {}
    for q in quantiles:
        result[q] = CriticalValuesHaldrup.get_critical_value(m1, m2, n, q)
    
    if quantile is not None:
        return result[quantile]
    return result
