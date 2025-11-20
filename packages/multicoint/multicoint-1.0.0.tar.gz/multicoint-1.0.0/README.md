# multicoint: Multicointegration Analysis for I(2) Time Series

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A Python package for testing and analyzing multicointegration in I(1) and I(2) time series, implementing the methodologies from:

- **Engsted, Gonzalo, and Haldrup (1997)**: "Testing for multicointegration", *Economics Letters* 56, 259-266
- **Haldrup (1994)**: "The asymptotics of single-equation cointegration regressions with I(1) and I(2) variables", *Journal of Econometrics* 63, 153-181

## Author

**Dr Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: [@merwanroudane](https://github.com/merwanroudane)

## Features

### Core Functionality
- ✓ **One-step multicointegration testing** (Engsted et al. 1997)
- ✓ **Single-equation cointegration regression** with I(1) and I(2) variables
- ✓ **Residual-based ADF tests** with appropriate critical values
- ✓ **Critical value tables** from both papers (with interpolation)
- ✓ **Data generation** for I(1), I(2), and multicointegrated systems
- ✓ **Granger-Lee production-sales-inventory** example implementation

### Statistical Tests
- Multicointegration test (one-step procedure)
- ADF test for I(2) cointegration
- Hasza-Fuller test for double unit roots
- Unit root tests with automatic lag selection

### Estimation
- Cointegration regression estimation
- Super-consistent and super-super-consistent estimation
- Robust standard errors (Newey-West HAC)
- Diagnostic statistics (R², DW, AIC, BIC)

## Installation

### From PyPI (once published)
```bash
pip install multicoint
```

### From GitHub
```bash
git clone https://github.com/merwanroudane/multicoint.git
cd multicoint
pip install -e .
```

### Requirements
- Python ≥ 3.7
- NumPy ≥ 1.20.0
- SciPy ≥ 1.7.0
- pandas ≥ 1.3.0
- statsmodels ≥ 0.13.0
- matplotlib ≥ 3.4.0

## Quick Start

### Example 1: Testing for Multicointegration

```python
import numpy as np
from multicoint import (
    generate_multicointegrated_system,
    multicointegration_test
)

# Generate a multicointegrated system
# y_t (I(2)), x1_t (I(1)), x2_t (I(2)) with multicointegration
system = generate_multicointegrated_system(
    n=100,                    # Sample size
    m1=1,                     # Number of I(1) variables
    m2=1,                     # Number of I(2) variables
    cointegration_order=0,    # 0 = multicointegration
    random_state=42
)

# Test for multicointegration
result = multicointegration_test(
    y=system.y,
    x1=system.x1,
    x2=system.x2,
    include_intercept=True,
    include_trend=True
)

print(f"Multicointegration detected: {result.is_multicointegrated}")
print(f"ADF statistic: {result.adf_test.test_statistic:.4f}")
print(f"5% critical value: {result.adf_test.critical_values[0.05]:.4f}")
```

### Example 2: Granger-Lee Production-Sales-Inventory

```python
from multicoint import (
    generate_granger_lee_example,
    granger_lee_multicointegration_test
)

# Generate Granger-Lee system
production, sales, inventory = generate_granger_lee_example(
    n=200,
    random_state=42
)

# Test for multicointegration
results = granger_lee_multicointegration_test(
    production=production,
    sales=sales
)

print(f"Multicointegration in production-sales-inventory: "
      f"{results['multicointegration_detected']}")
```

### Example 3: Manual Cointegration Regression

```python
from multicoint import cointegration_regression

# Estimate cointegration regression
# Δ⁻¹y_t = α + β₁'x₁ₜ + β₂'Δ⁻¹x₂ₜ + u_t
reg_result = cointegration_regression(
    y=system.y,
    x1=system.x1,
    x2=system.x2,
    include_intercept=True,
    include_trend=True,
    robust_se=True  # Use Newey-West HAC standard errors
)

# Print regression summary
print(reg_result.summary())

# Access results
print(f"R²: {reg_result.r_squared:.4f}")
print(f"DW statistic: {reg_result.dw_statistic:.4f}")
print(f"Coefficients: {reg_result.coefficients}")
```

## Theoretical Background

### Multicointegration

**Definition** (Engsted et al. 1997): Let Y_t and X_t be I(1) time series that cointegrate such that Z_t = Y_t - βX_t is I(0). If the cumulated error series S_t = Σⱼ₌₁ᵗ Zⱼ (which is I(1)) cointegrates with X_t, then Y_t and X_t are said to be **multicointegrated**.

This implies two levels of cointegration:
1. **First level**: Y_t ~ X_t, CI(1,1) → Z_t is I(0)
2. **Second level**: S_t ~ X_t, CI(1,1) → multicointegration

### One-Step Procedure

Engsted et al. (1997) propose a one-step procedure that simultaneously tests both levels:

1. Estimate the regression:
   ```
   Δ⁻¹y_t = α₀ + α₁t + α₂t² + β₁'x₁ₜ + β₂'Δ⁻¹x₂ₜ + u_t
   ```

2. Test whether u_t is I(1) vs I(0) using ADF test with special critical values

**Advantages**:
- Estimates β₂ at super-super-consistent rate Op(T⁻²)
- Estimates β₁ at super-consistent rate Op(T⁻¹)
- Avoids two-step estimation problems

### Critical Values

The package includes complete critical value tables for:

#### Engsted et al. (1997)
- **Table 1**: Linear trend case (intercept + trend in cointegration regression)
- **Table 2**: Quadratic trend case (intercept + trend + trend²)
- Dimensions: m₁ ∈ {0,1,2,3,4}, m₂ ∈ {1,2}, n ∈ {25,50,100,250,500}
- Quantiles: 1%, 2.5%, 5%, 10%

#### Haldrup (1994)
- **Table 1**: Intercept case
- Same dimensions and quantiles as Engsted et al.

**Interpolation**: The package automatically interpolates critical values for sample sizes not in the tables.

## API Reference

### Main Functions

#### `multicointegration_test()`
Test for multicointegration using one-step procedure.

```python
from multicoint import multicointegration_test

result = multicointegration_test(
    y,                          # I(2) dependent variable
    x1=None,                    # I(1) regressors
    x2=None,                    # I(2) regressors
    include_intercept=True,
    include_trend=False,
    include_quadratic_trend=False,
    lags=None,                  # Auto-selected if None
    significance_level=0.05,
    verbose=True
)
```

**Returns**: `MulticointegrationTestResult` with attributes:
- `is_multicointegrated`: bool
- `adf_test`: ADF test results
- `cointegration_regression`: Regression results
- `beta1_estimate`: I(1) coefficients
- `beta2_estimate`: I(2) coefficients

#### `cointegration_regression()`
Estimate cointegration regression.

```python
from multicoint import cointegration_regression

result = cointegration_regression(
    y,
    x1=None,
    x2=None,
    include_intercept=True,
    include_trend=False,
    include_quadratic_trend=False,
    robust_se=False,           # Use Newey-West if True
    hac_lags=None
)
```

**Returns**: `CointegrationRegressionResult` with comprehensive statistics.

#### `adf_test_i2()`
ADF test for I(2) cointegration residuals.

```python
from multicoint import adf_test_i2

result = adf_test_i2(
    residuals,
    m1,                        # Number of I(1) regressors
    m2,                        # Number of I(2) regressors
    lags=None,
    trend_type='linear',       # 'linear' or 'quadratic'
    significance_level=0.05,
    method='engsted'           # 'engsted' or 'haldrup'
)
```

### Simulation Functions

#### `generate_multicointegrated_system()`
Generate multicointegrated data.

```python
from multicoint import generate_multicointegrated_system

system = generate_multicointegrated_system(
    n=100,
    m1=1,
    m2=1,
    beta1=None,                # Default: ones
    beta2=None,                # Default: ones
    sigma_u=1.0,
    sigma_x1=1.0,
    sigma_x2=1.0,
    cointegration_order=0,     # 0, 1, or 2
    include_intercept=True,
    include_trend=False,
    random_state=None
)
```

**Returns**: `MulticointegrationSystem` with:
- `y`: I(2) dependent variable
- `x1`: I(1) regressors
- `x2`: I(2) regressors
- `beta1`, `beta2`: True coefficients
- `u`: True residuals

#### `generate_i1_process()` and `generate_i2_process()`
Generate I(1) and I(2) processes.

```python
from multicoint import generate_i1_process, generate_i2_process

# I(1) process (random walk)
x_i1 = generate_i1_process(n=100, sigma=1.0, drift=0.0)

# I(2) process (double integration)
x_i2 = generate_i2_process(n=100, sigma=1.0)
```

### Critical Values Functions

#### `get_critical_values_engsted()` and `get_critical_values_haldrup()`
Get critical values from tables.

```python
from multicoint import get_critical_values_engsted

cv = get_critical_values_engsted(
    m1=1,
    m2=1,
    n=100,
    quantile=0.05,            # Or None for all quantiles
    trend_type='linear'
)
```

### Utility Functions

```python
from multicoint import (
    integration_order,         # Determine I(d) order
    calculate_dw_statistic,    # Durbin-Watson
    calculate_r_squared,       # R²
    lag_matrix,                # Create lagged variables
    cumsum_matrix,             # Cumulative sum
    demean,                    # Remove mean
    detrend                    # Remove trend
)
```

## Examples Directory

See the `examples/` directory for comprehensive examples:

- `example_01_basic_multicointegration.py`: Basic usage
- `example_02_granger_lee.py`: Production-sales-inventory
- `example_03_monte_carlo.py`: Monte Carlo simulations
- `example_04_critical_values.py`: Working with critical values
- `example_05_uk_money_demand.py`: Real data application

## Methodological Notes

### Convergence Rates

As proven in Haldrup (1994) and Engsted et al. (1997):

| Case | β̂₁ (I(1) coefs) | β̂₂ (I(2) coefs) |
|------|-----------------|-----------------|
| d=0 (multicointegration) | Op(T⁻¹) | Op(T⁻²) |
| d=1 (first-level coint.) | Op(1) | Op(T⁻¹) |
| d=2 (no cointegration) | Op(1) | Op(1) |

### Spurious Regression

When d=1 or d=2 (no multicointegration):
- F-statistics diverge at rate Op(n)
- Durbin-Watson → 0 at rate Op(n⁻¹)
- R² → 1 (d=0,1) or has non-degenerate limit (d=2)

### Deterministic Components

The package handles:
- **Intercept**: Accounts for non-zero means
- **Linear trend**: Generated when I(1) variables have drift
- **Quadratic trend**: Generated when I(2) variables have drift

Critical values differ depending on which deterministics are included.

## Testing

Run tests:
```bash
pytest tests/
```

Run specific test:
```bash
pytest tests/test_multicointegration.py -v
```

## Citation

If you use this package in your research, please cite:

```bibtex
@software{roudane2024multicoint,
  author = {Roudane, Merwan},
  title = {multicoint: Multicointegration Analysis for I(2) Time Series},
  year = {2024},
  url = {https://github.com/merwanroudane/multicoint},
  version = {1.0.0}
}
```

And cite the original papers:

```bibtex
@article{engsted1997testing,
  title={Testing for multicointegration},
  author={Engsted, Tom and Gonzalo, Jesus and Haldrup, Niels},
  journal={Economics Letters},
  volume={56},
  number={3},
  pages={259--266},
  year={1997},
  publisher={Elsevier}
}

@article{haldrup1994asymptotics,
  title={The asymptotics of single-equation cointegration regressions with I(1) and I(2) variables},
  author={Haldrup, Niels},
  journal={Journal of Econometrics},
  volume={63},
  number={1},
  pages={153--181},
  year={1994},
  publisher={Elsevier}
}
```

## References

### Primary Sources

1. **Engsted, T., Gonzalo, J., and Haldrup, N. (1997)**. "Testing for multicointegration". *Economics Letters*, 56(3), 259-266.

2. **Haldrup, N. (1994)**. "The asymptotics of single-equation cointegration regressions with I(1) and I(2) variables". *Journal of Econometrics*, 63(1), 153-181.

### Related Literature

3. **Granger, C.W.J. and Lee, T. (1989)**. "Investigation of production, sales and inventory relationships using multicointegration and non-symmetric error correction models". *Journal of Applied Econometrics*, 4, S145-S159.

4. **Johansen, S. (1995)**. "A statistical analysis of cointegration for I(2) variables". *Econometric Theory*, 11, 25-59.

5. **Engle, R.F. and Granger, C.W.J. (1987)**. "Co-integration and error correction: Representation, estimation and testing". *Econometrica*, 55(2), 251-276.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

For major changes, please open an issue first to discuss.

## Support

- **Issues**: [GitHub Issues](https://github.com/merwanroudane/multicoint/issues)
- **Email**: merwanroudane920@gmail.com
- **Documentation**: See examples and docstrings

## Acknowledgments

This package implements the methodologies developed by:
- Tom Engsted (Aarhus School of Business)
- Jesus Gonzalo (University of Carlos III, Madrid)  
- Niels Haldrup (University of Aarhus)

Special thanks to the econometrics community for advancing the theory of I(2) cointegration.

---

**Keywords**: econometrics, time series, cointegration, multicointegration, I(2), unit root, ADF test, spurious regression, Engsted-Gonzalo-Haldrup, Haldrup, Granger-Lee
