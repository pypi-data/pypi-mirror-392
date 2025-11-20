"""
Example 1: Basic Multicointegration Testing
============================================

This example demonstrates basic usage of the multicoint package to test
for multicointegration in simulated data.

Based on Engsted, Gonzalo, and Haldrup (1997)
"""

import numpy as np
import matplotlib.pyplot as plt
from multicoint import (
    generate_multicointegrated_system,
    multicointegration_test,
    cointegration_regression
)


def main():
    """Run basic multicointegration example"""
    
    print("="*70)
    print("Example 1: Basic Multicointegration Testing")
    print("="*70)
    print()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate multicointegrated system
    print("Generating multicointegrated system...")
    print("  - Sample size: n = 200")
    print("  - I(1) regressors: m1 = 2")
    print("  - I(2) regressors: m2 = 1")
    print("  - Cointegration order: d = 0 (multicointegration)")
    print()
    
    system = generate_multicointegrated_system(
        n=200,
        m1=2,                      # Two I(1) variables
        m2=1,                      # One I(2) variable
        beta1=np.array([1.5, -0.8]),  # True I(1) coefficients
        beta2=np.array([2.0]),     # True I(2) coefficient
        cointegration_order=0,     # Multicointegration
        sigma_u=0.5,
        include_intercept=True,
        include_trend=False,
        random_state=42
    )
    
    print(f"True β₁ (I(1) coefficients): {system.beta1}")
    print(f"True β₂ (I(2) coefficients): {system.beta2}")
    print()
    
    # Visualize the data
    print("Plotting time series...")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Plot y (I(2) dependent variable)
    axes[0, 0].plot(system.y)
    axes[0, 0].set_title('y_t (I(2) Dependent Variable)')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot I(1) regressors
    axes[0, 1].plot(system.x1)
    axes[0, 1].set_title('I(1) Regressors')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].legend([f'x1_{i+1}' for i in range(system.x1.shape[1])])
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot I(2) regressors
    axes[1, 0].plot(system.x2)
    axes[1, 0].set_title('I(2) Regressors')
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].legend([f'x2_{i+1}' for i in range(system.x2.shape[1])])
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot true residuals
    axes[1, 1].plot(system.u)
    axes[1, 1].set_title('True Cointegration Residuals (I(0))')
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('example_01_timeseries.png', dpi=300)
    print("  Saved: example_01_timeseries.png")
    print()
    
    # Test for multicointegration
    print("="*70)
    print("Testing for Multicointegration (One-Step Procedure)")
    print("="*70)
    print()
    
    result = multicointegration_test(
        y=system.y,
        x1=system.x1,
        x2=system.x2,
        include_intercept=True,
        include_trend=False,
        lags=None,  # Auto-select
        significance_level=0.05,
        verbose=True
    )
    
    print()
    print("="*70)
    print("Comparison of Estimates with True Values")
    print("="*70)
    print()
    print("I(1) Coefficients (β₁):")
    print(f"  True:     {system.beta1}")
    print(f"  Estimated: {result.beta1_estimate}")
    print(f"  Error:    {result.beta1_estimate - system.beta1}")
    print()
    print("I(2) Coefficients (β₂):")
    print(f"  True:     {system.beta2}")
    print(f"  Estimated: {result.beta2_estimate}")
    print(f"  Error:    {result.beta2_estimate - system.beta2}")
    print()
    
    # Detailed regression output
    print("="*70)
    print("Detailed Cointegration Regression Results")
    print("="*70)
    print()
    print(result.cointegration_regression.summary())
    print()
    
    # Plot residuals
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    
    # Plot estimated residuals
    axes[0].plot(result.cointegration_regression.residuals)
    axes[0].set_title('Estimated Cointegration Residuals')
    axes[0].set_xlabel('Time')
    axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[0].grid(True, alpha=0.3)
    
    # ACF plot
    from statsmodels.graphics.tsaplots import plot_acf
    plot_acf(result.cointegration_regression.residuals, lags=20, ax=axes[1])
    axes[1].set_title('Autocorrelation Function of Residuals')
    
    plt.tight_layout()
    plt.savefig('example_01_residuals.png', dpi=300)
    print("Saved: example_01_residuals.png")
    print()
    
    # Conclusion
    print("="*70)
    print("CONCLUSION")
    print("="*70)
    if result.is_multicointegrated:
        print("✓ MULTICOINTEGRATION DETECTED")
        print()
        print("The ADF test on cointegration residuals rejects the null")
        print("hypothesis of I(1) residuals, confirming that the system")
        print("is multicointegrated as expected.")
        print()
        print("As proven in Engsted et al. (1997):")
        print("  - β₁ is estimated at rate Op(T⁻¹) (super-consistent)")
        print("  - β₂ is estimated at rate Op(T⁻²) (super-super-consistent)")
    else:
        print("✗ MULTICOINTEGRATION NOT DETECTED")
        print()
        print("Warning: The test failed to detect multicointegration.")
        print("This could be due to small sample size or low signal-to-noise ratio.")
    print("="*70)


if __name__ == "__main__":
    main()
