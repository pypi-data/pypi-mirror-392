"""
Example usage of the PMCT package for cointegration testing with structural breaks.

This script demonstrates various use cases for the cointegration_test_2breaks function.
"""

import numpy as np
import pandas as pd
from pmct import cointegration_test_2breaks


def example_1_basic_usage():
    """
    Example 1: Basic usage with simulated data.
    """
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage with Simulated Data")
    print("=" * 80)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate sample data (200 observations)
    n = 200
    
    # Create integrated I(1) processes
    # y and x share a common stochastic trend (cointegrated)
    e1 = np.random.randn(n, 1)
    e2 = np.random.randn(n, 1)
    
    # Generate I(1) processes
    x = np.cumsum(e1)
    
    # Generate y with structural breaks
    y = np.zeros((n, 1))
    for t in range(n):
        if t < 80:  # First regime
            y[t] = 2.0 + 0.8 * x[t] + e2[t]
        elif t < 140:  # Second regime (first break)
            y[t] = 3.5 + 0.5 * x[t] + e2[t]
        else:  # Third regime (second break)
            y[t] = 4.0 + 0.6 * x[t] + e2[t]
    
    # Run cointegration test
    results = cointegration_test_2breaks(
        y=y,
        x=x,
        model=4,  # Regime shift model
        max_lag=2,
        lag_selection=2  # AIC
    )
    
    # Display results
    print(results)
    
    # True break points for comparison
    print("\nTrue break points (for simulated data):")
    print(f"  First break:  {80/n:.4f} (observation 80)")
    print(f"  Second break: {140/n:.4f} (observation 140)")
    
    print("\n")


def example_2_csv_data():
    """
    Example 2: Loading data from CSV and running test.
    """
    print("=" * 80)
    print("EXAMPLE 2: Loading Data from CSV")
    print("=" * 80)
    
    # Create sample CSV data
    np.random.seed(123)
    n = 150
    
    # Generate data
    x_data = np.cumsum(np.random.randn(n))
    y_data = 2 + 0.7 * x_data + np.random.randn(n) * 0.5
    
    # Create DataFrame
    df = pd.DataFrame({
        'Y': y_data,
        'X': x_data
    })
    
    # Save to CSV (you would normally have this file already)
    df.to_csv('sample_data.csv', index=False)
    print("Created sample_data.csv")
    
    # Load and test
    data = pd.read_csv('sample_data.csv')
    y = data['Y'].values.reshape(-1, 1)
    x = data['X'].values.reshape(-1, 1)
    
    results = cointegration_test_2breaks(y, x, model=4, max_lag=3)
    
    print("\nTest Results:")
    print(f"ADF statistic: {results.adf_statistic:.4f}")
    print(f"Za statistic:  {results.za_statistic:.4f}")
    print(f"Zt statistic:  {results.zt_statistic:.4f}")
    print(f"\nBreak points (ADF): {results.adf_break1:.4f}, {results.adf_break2:.4f}")
    
    print("\n")


def example_3_multiple_variables():
    """
    Example 3: Testing with multiple independent variables.
    """
    print("=" * 80)
    print("EXAMPLE 3: Multiple Independent Variables")
    print("=" * 80)
    
    np.random.seed(456)
    n = 180
    
    # Generate multiple I(1) processes
    x1 = np.cumsum(np.random.randn(n))
    x2 = np.cumsum(np.random.randn(n))
    x3 = np.cumsum(np.random.randn(n))
    
    # Combine into matrix
    x = np.column_stack([x1, x2, x3])
    
    # Generate cointegrated y
    y = 1.5 + 0.4*x1 + 0.3*x2 + 0.2*x3 + np.random.randn(n)*0.3
    y = y.reshape(-1, 1)
    
    # Run test
    results = cointegration_test_2breaks(
        y=y,
        x=x,
        model=4,
        max_lag=2,
        lag_selection=3  # BIC
    )
    
    print(f"Number of independent variables: {x.shape[1]}")
    print(f"\nADF statistic: {results.adf_statistic:.4f}")
    print(f"Optimal lag (ADF): {results.adf_lag}")
    
    print("\nEstimated coefficients:")
    for i, (coef, se) in enumerate(zip(results.coefficients, results.standard_errors)):
        print(f"  β{i}: {coef[0]:>8.4f} (SE: {se:>6.4f})")
    
    print("\n")


def example_4_model_comparison():
    """
    Example 4: Comparing different model specifications.
    """
    print("=" * 80)
    print("EXAMPLE 4: Comparing Model Specifications")
    print("=" * 80)
    
    np.random.seed(789)
    n = 200
    
    # Generate data
    x = np.cumsum(np.random.randn(n, 1))
    y = 3 + 0.6*x + np.random.randn(n, 1)*0.4
    
    models = {
        2: "Level Shift (C)",
        3: "Level Shift with Trend (C/T)",
        4: "Regime Shift (C/S)"
    }
    
    print("\nComparing model specifications:\n")
    
    for model_num, model_name in models.items():
        results = cointegration_test_2breaks(
            y=y,
            x=x,
            model=model_num,
            max_lag=2
        )
        
        print(f"Model {model_num} - {model_name}:")
        print(f"  ADF*: {results.adf_statistic:>8.4f}")
        print(f"  Za*:  {results.za_statistic:>8.4f}")
        print(f"  Zt*:  {results.zt_statistic:>8.4f}")
        print()
    
    print("Note: Choose the model that best fits your theoretical framework.")
    print("\n")


def example_5_interpretation():
    """
    Example 5: Full interpretation with critical values.
    """
    print("=" * 80)
    print("EXAMPLE 5: Full Interpretation with Critical Values")
    print("=" * 80)
    
    np.random.seed(101)
    n = 250
    
    # Generate strongly cointegrated data with breaks
    e1 = np.random.randn(n, 1) * 0.5
    e2 = np.random.randn(n, 1) * 0.3
    
    x = np.cumsum(e1)
    y = np.zeros((n, 1))
    
    # Create clear structural breaks
    for t in range(n):
        if t < 100:
            y[t] = 1.0 + 0.9 * x[t] + e2[t]
        elif t < 180:
            y[t] = 4.0 + 0.4 * x[t] + e2[t]  # Clear break
        else:
            y[t] = 2.0 + 0.7 * x[t] + e2[t]  # Second break
    
    results = cointegration_test_2breaks(y, x, model=4, max_lag=3, lag_selection=2)
    
    print(results)
    
    # Critical values for k=1 (one independent variable) from Hatemi-J (2008)
    critical_values = {
        'ADF': {'1%': -6.503, '5%': -6.015, '10%': -5.653},
        'Za': {'1%': -6.503, '5%': -6.015, '10%': -5.653},
        'Zt': {'1%': -90.794, '5%': -76.003, '10%': -52.232}
    }
    
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    
    print("\nCritical Values (k=1, from Hatemi-J 2008, Table 1):")
    print(f"{'Test':<6} {'1%':<10} {'5%':<10} {'10%':<10}")
    print("-" * 40)
    for test in ['ADF', 'Za', 'Zt']:
        cvs = critical_values[test]
        print(f"{test:<6} {cvs['1%']:<10.3f} {cvs['5%']:<10.3f} {cvs['10%']:<10.3f}")
    
    print("\nTest Decision:")
    
    # ADF Test
    if results.adf_statistic < critical_values['ADF']['1%']:
        print(f"  ADF: {results.adf_statistic:.3f} < {critical_values['ADF']['1%']:.3f} → Reject H0 at 1%")
    elif results.adf_statistic < critical_values['ADF']['5%']:
        print(f"  ADF: {results.adf_statistic:.3f} < {critical_values['ADF']['5%']:.3f} → Reject H0 at 5%")
    elif results.adf_statistic < critical_values['ADF']['10%']:
        print(f"  ADF: {results.adf_statistic:.3f} < {critical_values['ADF']['10%']:.3f} → Reject H0 at 10%")
    else:
        print(f"  ADF: {results.adf_statistic:.3f} → Fail to reject H0")
    
    # Zt Test
    if results.zt_statistic < critical_values['Zt']['1%']:
        print(f"  Zt:  {results.zt_statistic:.3f} < {critical_values['Zt']['1%']:.3f} → Reject H0 at 1%")
    elif results.zt_statistic < critical_values['Zt']['5%']:
        print(f"  Zt:  {results.zt_statistic:.3f} < {critical_values['Zt']['5%']:.3f} → Reject H0 at 5%")
    elif results.zt_statistic < critical_values['Zt']['10%']:
        print(f"  Zt:  {results.zt_statistic:.3f} < {critical_values['Zt']['10%']:.3f} → Reject H0 at 10%")
    else:
        print(f"  Zt:  {results.zt_statistic:.3f} → Fail to reject H0")
    
    print("\nConclusion:")
    print("  H0: No cointegration")
    print("  H1: Cointegration with two structural breaks")
    
    # Determine overall conclusion
    adf_reject = results.adf_statistic < critical_values['ADF']['10%']
    zt_reject = results.zt_statistic < critical_values['Zt']['10%']
    
    if adf_reject or zt_reject:
        print("\n  → Evidence of cointegration with structural breaks at 10% level or better")
    else:
        print("\n  → Insufficient evidence to reject no cointegration")
    
    print("\n")


def main():
    """
    Run all examples.
    """
    print("\n")
    print("*" * 80)
    print("PMCT PACKAGE - USAGE EXAMPLES")
    print("*" * 80)
    print("\n")
    
    # Run all examples
    example_1_basic_usage()
    example_2_csv_data()
    example_3_multiple_variables()
    example_4_model_comparison()
    example_5_interpretation()
    
    print("*" * 80)
    print("All examples completed successfully!")
    print("*" * 80)
    print("\n")


if __name__ == "__main__":
    main()
