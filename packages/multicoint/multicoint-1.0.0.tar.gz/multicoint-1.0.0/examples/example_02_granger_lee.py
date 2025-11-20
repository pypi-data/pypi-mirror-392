"""
Example 2: Granger-Lee Production-Sales-Inventory Model
=======================================================

This example demonstrates multicointegration in the classic Granger-Lee (1989, 1990)
production-sales-inventory framework.

The model:
- Y_t: Production (I(1))
- X_t: Sales (I(1))
- Z_t = Y_t - X_t: Inventory investment (I(0))
- S_t = Σ Z_j: Inventory level (I(1))

Multicointegration occurs when S_t cointegrates with X_t and/or Y_t.

References:
- Granger & Lee (1989): "Investigation of production, sales and inventory 
  relationships using multicointegration"
- Granger & Lee (1990): "Multicointegration" in Advances in Econometrics
"""

import numpy as np
import matplotlib.pyplot as plt
from multicoint import (
    generate_granger_lee_example,
    granger_lee_multicointegration_test,
    multicointegration_test
)


def main():
    """Run Granger-Lee example"""
    
    print("="*70)
    print("Example 2: Granger-Lee Production-Sales-Inventory Model")
    print("="*70)
    print()
    
    # Set random seed
    np.random.seed(123)
    
    # Generate Granger-Lee system
    print("Generating Granger-Lee production-sales-inventory system...")
    print("  - Sample size: n = 250")
    print("  - Production (Y_t): I(1)")
    print("  - Sales (X_t): I(1)")
    print("  - Inventory level (S_t): I(1)")
    print()
    
    production, sales, inventory = generate_granger_lee_example(
        n=250,
        production_shock_std=1.0,
        sales_shock_std=1.0,
        initial_inventory=10.0,
        random_state=123
    )
    
    # Calculate inventory investment
    inv_investment = production - sales
    
    # Visualize the system
    print("Plotting time series...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Production and Sales
    axes[0, 0].plot(production, label='Production (Y_t)', linewidth=2)
    axes[0, 0].plot(sales, label='Sales (X_t)', linewidth=2, alpha=0.7)
    axes[0, 0].set_title('Production and Sales (Both I(1))', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Inventory Investment (should be I(0))
    axes[0, 1].plot(inv_investment, color='green', linewidth=2)
    axes[0, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[0, 1].set_title('Inventory Investment (Z_t = Y_t - X_t, I(0))', 
                        fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Inventory Level (should be I(1))
    axes[1, 0].plot(inventory, color='purple', linewidth=2)
    axes[1, 0].set_title('Inventory Level (S_t = ΣZ_j, I(1))', 
                        fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].grid(True, alpha=0.3)
    
    # ACF of Inventory Investment
    from statsmodels.graphics.tsaplots import plot_acf
    plot_acf(inv_investment, lags=20, ax=axes[1, 1])
    axes[1, 1].set_title('ACF of Inventory Investment', 
                        fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('example_02_granger_lee_system.png', dpi=300)
    print("  Saved: example_02_granger_lee_system.png")
    print()
    
    # Test for multicointegration
    print("="*70)
    print("Testing for Multicointegration")
    print("="*70)
    print()
    
    print("Test 1: Production and Sales Cointegration")
    print("-" * 70)
    print("H₀: Y_t - X_t is I(1)")
    print("H₁: Y_t - X_t is I(0) (cointegration)")
    print()
    
    test1 = multicointegration_test(
        y=production,
        x1=sales.reshape(-1, 1),
        x2=None,
        include_intercept=True,
        verbose=False
    )
    
    print(f"ADF statistic: {test1.adf_test.test_statistic:.4f}")
    print(f"5% critical value: {test1.adf_test.critical_values[0.05]:.4f}")
    print(f"Result: {'COINTEGRATED ✓' if test1.is_multicointegrated else 'NOT COINTEGRATED ✗'}")
    print()
    
    print("Test 2: Inventory Level and Sales/Production Multicointegration")
    print("-" * 70)
    print("H₀: S_t and X_t are not cointegrated")
    print("H₁: S_t and X_t cointegrate (multicointegration)")
    print()
    
    test2 = multicointegration_test(
        y=inventory,
        x1=sales.reshape(-1, 1),
        x2=None,
        include_intercept=True,
        verbose=False
    )
    
    print(f"ADF statistic: {test2.adf_test.test_statistic:.4f}")
    print(f"5% critical value: {test2.adf_test.critical_values[0.05]:.4f}")
    print(f"Result: {'MULTICOINTEGRATED ✓' if test2.is_multicointegrated else 'NOT MULTICOINTEGRATED ✗'}")
    print()
    
    # Use specialized Granger-Lee test
    print("="*70)
    print("Specialized Granger-Lee Multicointegration Test")
    print("="*70)
    print()
    
    results = granger_lee_multicointegration_test(
        production=production,
        sales=sales,
        significance_level=0.05
    )
    
    print("Results Summary:")
    print(f"  Production-Sales Cointegration: {results['production_sales_cointegration']}")
    print(f"  Inventory Multicointegration:   {results['inventory_multicointegration']}")
    print(f"  Overall Multicointegration:     {results['multicointegration_detected']}")
    print()
    
    # Visualize residuals
    print("Plotting cointegration residuals...")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Production-Sales residuals
    resid1 = test1.cointegration_regression.residuals
    axes[0].plot(resid1, color='blue', linewidth=1.5)
    axes[0].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[0].set_title('Production-Sales Cointegration Residuals\n(Should be I(0))',
                     fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Time')
    axes[0].grid(True, alpha=0.3)
    
    # Inventory-Sales residuals
    resid2 = test2.cointegration_regression.residuals
    axes[1].plot(resid2, color='purple', linewidth=1.5)
    axes[1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
    axes[1].set_title('Inventory-Sales Multicointegration Residuals\n(Should be I(0))',
                     fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Time')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('example_02_residuals.png', dpi=300)
    print("  Saved: example_02_residuals.png")
    print()
    
    # Economic interpretation
    print("="*70)
    print("ECONOMIC INTERPRETATION")
    print("="*70)
    print()
    print("Granger and Lee (1989) show that multicointegration naturally arises")
    print("in production-sales-inventory systems when firms use integral control")
    print("to manage inventory levels.")
    print()
    print("The two levels of cointegration are:")
    print()
    print("1. FIRST LEVEL (Standard Cointegration)")
    print("   Production and sales are cointegrated:")
    print("   Y_t - β*X_t = Z_t  (inventory investment, I(0))")
    print()
    print("2. SECOND LEVEL (Multicointegration)")
    print("   Inventory level cointegrates with sales/production:")
    print("   S_t - γ*X_t ~ I(0)")
    print("   where S_t = Σ Z_j (cumulated inventory investment)")
    print()
    
    if results['multicointegration_detected']:
        print("✓ Our test CONFIRMS multicointegration in this system.")
        print()
        print("This implies firms use both:")
        print("  • Proportional control: Adjust production based on sales")
        print("  • Integral control: Adjust based on cumulated errors (inventory)")
    else:
        print("✗ Multicointegration not detected in this particular sample.")
        print("  (May be due to sampling variability)")
    
    print("="*70)


if __name__ == "__main__":
    main()
