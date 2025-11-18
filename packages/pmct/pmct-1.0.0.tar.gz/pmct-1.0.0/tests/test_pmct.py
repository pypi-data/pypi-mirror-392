"""
Basic tests for the PMCT package.

These tests verify the core functionality of the cointegration testing functions.
"""

import numpy as np
import pytest
from pmct import cointegration_test_2breaks
from pmct.core import estimate, adf_test, phillips_test


class TestEstimate:
    """Tests for the estimate function."""
    
    def test_estimate_simple_regression(self):
        """Test OLS estimation with simple regression."""
        np.random.seed(42)
        n = 100
        x = np.random.randn(n, 1)
        y = 2 + 3 * x + np.random.randn(n, 1) * 0.1
        
        # Add constant
        x_with_const = np.column_stack([np.ones(n), x])
        
        b, e, sig2, se = estimate(y, x_with_const)
        
        # Check shapes
        assert b.shape == (2, 1)
        assert e.shape == (n, 1)
        assert se.shape == (2, 1)
        
        # Check that coefficients are close to true values
        assert abs(b[0, 0] - 2) < 0.5  # Intercept
        assert abs(b[1, 0] - 3) < 0.5  # Slope
    
    def test_estimate_returns_correct_types(self):
        """Test that estimate returns numpy arrays."""
        np.random.seed(123)
        n = 50
        x = np.random.randn(n, 2)
        y = np.random.randn(n, 1)
        
        b, e, sig2, se = estimate(y, x)
        
        assert isinstance(b, np.ndarray)
        assert isinstance(e, np.ndarray)
        assert isinstance(sig2, (float, np.ndarray))
        assert isinstance(se, np.ndarray)


class TestCointegrationTest:
    """Tests for the main cointegration test function."""
    
    def test_basic_functionality(self):
        """Test that the function runs without errors."""
        np.random.seed(456)
        n = 150
        x = np.cumsum(np.random.randn(n, 1))
        y = 2 + 0.5 * x + np.random.randn(n, 1) * 0.3
        
        results = cointegration_test_2breaks(y, x, model=4, max_lag=2)
        
        # Check that results object has required attributes
        assert hasattr(results, 'adf_statistic')
        assert hasattr(results, 'za_statistic')
        assert hasattr(results, 'zt_statistic')
        assert hasattr(results, 'adf_break1')
        assert hasattr(results, 'adf_break2')
        assert hasattr(results, 'coefficients')
        assert hasattr(results, 'standard_errors')
    
    def test_break_points_within_range(self):
        """Test that break points are within valid range."""
        np.random.seed(789)
        n = 200
        x = np.cumsum(np.random.randn(n, 1))
        y = 3 + 0.7 * x + np.random.randn(n, 1) * 0.4
        
        results = cointegration_test_2breaks(y, x, model=4, max_lag=2, trim=0.15)
        
        # Break points should be between trim and (1-trim)
        assert 0.15 <= results.adf_break1 <= 0.85
        assert 0.15 <= results.adf_break2 <= 0.85
        
        # First break should be before second break
        assert results.adf_break1 < results.adf_break2
    
    def test_model_specifications(self):
        """Test that all model specifications work."""
        np.random.seed(101)
        n = 150
        x = np.cumsum(np.random.randn(n, 1))
        y = 2 + 0.5 * x + np.random.randn(n, 1) * 0.3
        
        for model in [2, 3, 4]:
            results = cointegration_test_2breaks(y, x, model=model, max_lag=2)
            assert results is not None
            assert isinstance(results.adf_statistic, float)
    
    def test_invalid_model_raises_error(self):
        """Test that invalid model specification raises ValueError."""
        np.random.seed(111)
        n = 100
        x = np.random.randn(n, 1)
        y = np.random.randn(n, 1)
        
        with pytest.raises(ValueError, match="model must be 2, 3, or 4"):
            cointegration_test_2breaks(y, x, model=5)
    
    def test_mismatched_dimensions_raises_error(self):
        """Test that mismatched y and x dimensions raise ValueError."""
        y = np.random.randn(100, 1)
        x = np.random.randn(50, 1)
        
        with pytest.raises(ValueError, match="must have the same number of observations"):
            cointegration_test_2breaks(y, x)
    
    def test_summary_method(self):
        """Test that summary method returns a string."""
        np.random.seed(222)
        n = 120
        x = np.cumsum(np.random.randn(n, 1))
        y = 1 + 0.6 * x + np.random.randn(n, 1) * 0.2
        
        results = cointegration_test_2breaks(y, x, model=4, max_lag=2)
        summary = results.summary()
        
        assert isinstance(summary, str)
        assert "ADF" in summary
        assert "Phillips" in summary
        assert "Hatemi-J" in summary
    
    def test_multiple_independent_variables(self):
        """Test with multiple independent variables."""
        np.random.seed(333)
        n = 150
        x1 = np.cumsum(np.random.randn(n))
        x2 = np.cumsum(np.random.randn(n))
        x = np.column_stack([x1, x2])
        y = 2 + 0.5*x1 + 0.3*x2 + np.random.randn(n)*0.3
        y = y.reshape(-1, 1)
        
        results = cointegration_test_2breaks(y, x, model=4, max_lag=2)
        
        # Should have more coefficients with multiple variables
        # Model 4 with 2 vars: constant + 2 dummies + 2 vars + 4 interactions = 9 params
        assert len(results.coefficients) > 3


class TestInputFormats:
    """Tests for different input formats (pandas, numpy)."""
    
    def test_pandas_series_input(self):
        """Test that pandas Series input works."""
        import pandas as pd
        
        np.random.seed(444)
        n = 100
        x_array = np.cumsum(np.random.randn(n))
        y_array = 2 + 0.5 * x_array + np.random.randn(n) * 0.2
        
        y = pd.Series(y_array)
        x = pd.Series(x_array)
        
        results = cointegration_test_2breaks(y, x, model=4, max_lag=2)
        assert results is not None
    
    def test_pandas_dataframe_input(self):
        """Test that pandas DataFrame input works."""
        import pandas as pd
        
        np.random.seed(555)
        n = 100
        df = pd.DataFrame({
            'y': 2 + 0.5 * np.cumsum(np.random.randn(n)) + np.random.randn(n) * 0.2,
            'x': np.cumsum(np.random.randn(n))
        })
        
        results = cointegration_test_2breaks(
            df[['y']].values, 
            df[['x']].values, 
            model=4, 
            max_lag=2
        )
        assert results is not None


def test_reproducibility():
    """Test that results are reproducible with same seed."""
    n = 150
    
    # First run
    np.random.seed(666)
    x1 = np.cumsum(np.random.randn(n, 1))
    y1 = 2 + 0.5 * x1 + np.random.randn(n, 1) * 0.3
    results1 = cointegration_test_2breaks(y1, x1, model=4, max_lag=2)
    
    # Second run with same seed
    np.random.seed(666)
    x2 = np.cumsum(np.random.randn(n, 1))
    y2 = 2 + 0.5 * x2 + np.random.randn(n, 1) * 0.3
    results2 = cointegration_test_2breaks(y2, x2, model=4, max_lag=2)
    
    # Results should be identical
    assert results1.adf_statistic == results2.adf_statistic
    assert results1.adf_break1 == results2.adf_break1
    assert results1.adf_break2 == results2.adf_break2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
