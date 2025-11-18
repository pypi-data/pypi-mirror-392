"""
Main testing functions for cointegration with two endogenous structural breaks.

This module provides the high-level API for conducting cointegration tests
following the methodology of Hatemi-J (2008).
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Union
from .core import estimate, adf_test, phillips_test, create_dummies, construct_regressors


class CointegrationResults:
    """
    Container for cointegration test results.
    
    Attributes
    ----------
    adf_statistic : float
        Modified ADF test statistic
    adf_lag : int
        Optimal lag length for ADF test
    adf_break1 : float
        First breakpoint (ADF test) as fraction of sample
    adf_break2 : float
        Second breakpoint (ADF test) as fraction of sample
    za_statistic : float
        Phillips Za test statistic
    za_break1 : float
        First breakpoint (Za test) as fraction of sample
    za_break2 : float
        Second breakpoint (Za test) as fraction of sample
    zt_statistic : float
        Phillips Zt test statistic
    zt_break1 : float
        First breakpoint (Zt test) as fraction of sample
    zt_break2 : float
        Second breakpoint (Zt test) as fraction of sample
    coefficients : numpy.ndarray
        Estimated coefficients
    standard_errors : numpy.ndarray
        Standard errors of coefficients
    t_statistics : numpy.ndarray
        t-statistics for coefficients
    n_obs : int
        Number of observations
    model : int
        Model specification used
    """
    
    def __init__(self):
        self.adf_statistic = None
        self.adf_lag = None
        self.adf_break1 = None
        self.adf_break2 = None
        self.za_statistic = None
        self.za_break1 = None
        self.za_break2 = None
        self.zt_statistic = None
        self.zt_break1 = None
        self.zt_break2 = None
        self.coefficients = None
        self.standard_errors = None
        self.t_statistics = None
        self.n_obs = None
        self.model = None
    
    def summary(self) -> str:
        """
        Generate a formatted summary of the test results.
        
        Returns
        -------
        str
            Formatted summary string
        """
        summary_lines = []
        summary_lines.append("=" * 80)
        summary_lines.append("COINTEGRATION TEST RESULTS WITH TWO ENDOGENOUS STRUCTURAL BREAKS")
        summary_lines.append("=" * 80)
        summary_lines.append("")
        
        # ADF Test Results
        summary_lines.append("Modified ADF Test")
        summary_lines.append("-" * 40)
        summary_lines.append(f"  t-statistic:          {self.adf_statistic:.4f}")
        summary_lines.append(f"  AR lag:               {self.adf_lag}")
        summary_lines.append(f"  First break point:    {self.adf_break1:.4f}")
        summary_lines.append(f"  Second break point:   {self.adf_break2:.4f}")
        summary_lines.append("")
        
        # Phillips Tests Results
        summary_lines.append("Modified Phillips Tests (Zt and Za)")
        summary_lines.append("-" * 40)
        summary_lines.append(f"  Zt statistic:         {self.zt_statistic:.4f}")
        summary_lines.append(f"  First break (Zt):     {self.zt_break1:.4f}")
        summary_lines.append(f"  Second break (Zt):    {self.zt_break2:.4f}")
        summary_lines.append("")
        summary_lines.append(f"  Za statistic:         {self.za_statistic:.4f}")
        summary_lines.append(f"  First break (Za):     {self.za_break1:.4f}")
        summary_lines.append(f"  Second break (Za):    {self.za_break2:.4f}")
        summary_lines.append("")
        
        # Parameter Estimates
        summary_lines.append("Parameter Estimates")
        summary_lines.append("-" * 40)
        summary_lines.append(f"{'Parameter':<15} {'Estimate':>12} {'Std. Error':>12} {'t-statistic':>12}")
        summary_lines.append("-" * 55)
        for i in range(len(self.coefficients)):
            summary_lines.append(
                f"  β{i:<13} {self.coefficients[i][0]:>12.6f} "
                f"{self.standard_errors[i]:>12.6f} {self.t_statistics[i][0]:>12.4f}"
            )
        summary_lines.append("")
        summary_lines.append("=" * 80)
        summary_lines.append("Reference:")
        summary_lines.append("  Hatemi-J, A. (2008). Tests for cointegration with two unknown regime")
        summary_lines.append("  shifts with an application to financial market integration.")
        summary_lines.append("  Empirical Economics, 35(3), 497-505.")
        summary_lines.append("")
        summary_lines.append("Note: For critical values, please refer to Table 1 in Hatemi-J (2008).")
        summary_lines.append("=" * 80)
        
        return "\n".join(summary_lines)
    
    def __str__(self):
        return self.summary()
    
    def __repr__(self):
        return f"CointegrationResults(ADF={self.adf_statistic:.4f}, Za={self.za_statistic:.4f}, Zt={self.zt_statistic:.4f})"


def cointegration_test_2breaks(
    y: Union[np.ndarray, pd.Series, pd.DataFrame],
    x: Union[np.ndarray, pd.DataFrame],
    model: int = 4,
    max_lag: int = 2,
    lag_selection: int = 2,
    trim: float = 0.15
) -> CointegrationResults:
    """
    Conduct cointegration tests with two endogenous structural breaks.
    
    This function implements three residual-based cointegration tests that account
    for two unknown regime shifts as developed by Hatemi-J (2008). The timing of
    each structural break is determined endogenously.
    
    Parameters
    ----------
    y : array-like
        Dependent variable (n x 1). Can be numpy array, pandas Series, or DataFrame.
    x : array-like
        Independent variable(s) (n x k). Can be numpy array or pandas DataFrame.
    model : int, default=4
        Model specification:
        - 2: C (level shift model - constant with breaks)
        - 3: C/T (level shift with trend)
        - 4: C/S (regime shift model - constant with slope changes)
    max_lag : int, default=2
        Maximum lag order for ADF test.
    lag_selection : int, default=2
        Lag selection criterion for ADF test:
        - 1: Pre-specified AR lag (uses max_lag)
        - 2: AIC (Akaike Information Criterion)
        - 3: BIC (Bayesian Information Criterion)
        - 4: Downward-t selection
    trim : float, default=0.15
        Trimming percentage for break point search (0.15 = 15% from each end).
    
    Returns
    -------
    CointegrationResults
        Object containing all test statistics, break points, and parameter estimates.
    
    Examples
    --------
    >>> import numpy as np
    >>> from pmct import cointegration_test_2breaks
    >>> 
    >>> # Generate sample data
    >>> n = 200
    >>> x = np.random.randn(n, 1)
    >>> y = 2 + 0.5 * x + np.random.randn(n, 1) * 0.1
    >>> 
    >>> # Run the test
    >>> results = cointegration_test_2breaks(y, x, model=4, max_lag=2)
    >>> print(results)
    >>> 
    >>> # Access specific results
    >>> print(f"ADF statistic: {results.adf_statistic:.4f}")
    >>> print(f"First break: {results.adf_break1:.4f}")
    
    Notes
    -----
    The null hypothesis is no cointegration against the alternative of cointegration
    with two structural breaks. Critical values for these tests can be found in
    Table 1 of Hatemi-J (2008), page 501.
    
    The model specifications are:
    - Model 2 (C): y_t = α_0 + α_1*D1_t + α_2*D2_t + β*x_t + u_t
    - Model 3 (C/T): y_t = α_0 + α_1*D1_t + α_2*D2_t + γ*t + β*x_t + u_t
    - Model 4 (C/S): y_t = α_0 + α_1*D1_t + α_2*D2_t + β_0*x_t + β_1*D1_t*x_t + β_2*D2_t*x_t + u_t
    
    where D1_t and D2_t are dummy variables for the structural breaks.
    
    References
    ----------
    Hatemi-J, A. (2008). Tests for cointegration with two unknown regime shifts
    with an application to financial market integration. Empirical Economics,
    35(3), 497-505. https://doi.org/10.1007/s00181-007-0175-9
    """
    # Convert inputs to numpy arrays
    if isinstance(y, (pd.Series, pd.DataFrame)):
        y = y.values
    if isinstance(x, pd.DataFrame):
        x = x.values
    
    # Ensure proper shape
    if y.ndim == 1:
        y = y.reshape(-1, 1)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    
    # Validate inputs
    if y.shape[0] != x.shape[0]:
        raise ValueError(f"y and x must have the same number of observations. Got {y.shape[0]} and {x.shape[0]}")
    
    if model not in [2, 3, 4]:
        raise ValueError(f"model must be 2, 3, or 4. Got {model}")
    
    if not 0 < trim < 0.5:
        raise ValueError(f"trim must be between 0 and 0.5. Got {trim}")
    
    n = y.shape[0]
    
    # Define search range for break points
    begin = int(np.rint(trim * n))
    final1 = int(np.rint((1 - trim - trim) * n))
    final2 = int(np.rint((1 - trim) * n))
    
    # Initialize result matrices
    temp1 = 999 * np.ones((final1 - begin + 1, final2 - begin * 2 + 1))  # ADF stats
    temp2 = temp1.copy()  # Lags
    temp3 = temp1.copy()  # Za stats
    temp4 = temp1.copy()  # Zt stats
    
    # Grid search over all possible break point combinations
    t1 = begin
    while t1 <= final1:
        t2 = t1 + begin
        while t2 <= final2:
            # Create dummy variables for this break combination
            dummy1, dummy2 = create_dummies(n, t1, t2)
            
            # Construct regressors based on model specification
            x1 = construct_regressors(n, x, dummy1, dummy2, model)
            
            # Compute ADF test
            temp1[t1 - begin, t2 - begin * 2], temp2[t1 - begin, t2 - begin * 2] = adf_test(
                y, x1, max_lag, lag_selection
            )
            
            # Compute Phillips tests (Za and Zt)
            temp3[t1 - begin, t2 - begin * 2], temp4[t1 - begin, t2 - begin * 2] = phillips_test(
                y, x1
            )
            
            t2 = t2 + 1
        t1 = t1 + 1
    
    # Find optimal break points for ADF test (minimum statistic)
    tstatminc = np.amin(temp1, axis=0)
    minlag1ind = np.argmin(temp1, axis=0)
    adf_stat = np.amin(tstatminc, axis=0)
    bpt2_adf = np.where(tstatminc == np.amin(tstatminc))[0][0]
    bpt1_adf = minlag1ind[bpt2_adf]
    breakpt_adf1 = (bpt1_adf + begin) / n
    breakpt_adf2 = (bpt2_adf + begin * 2) / n
    lag = int(temp2[bpt1_adf, bpt2_adf])
    
    # Find optimal break points for Za test (minimum statistic)
    zaminc = np.amin(temp3, axis=0)
    minlag1ind = np.argmin(temp3, axis=0)
    za_stat = np.amin(zaminc, axis=0)
    bpt2_za = np.argmin(zaminc, axis=0)
    bpt1_za = minlag1ind[bpt2_za]
    breakpt_za1 = (bpt1_za + begin) / n
    breakpt_za2 = (bpt2_za + begin * 2) / n
    
    # Find optimal break points for Zt test (minimum statistic)
    ztminc = np.amin(temp4, axis=0)
    minlag1ind = np.argmin(temp4, axis=0)
    zt_stat = np.amin(ztminc, axis=0)
    bpt2_zt = np.argmin(ztminc, axis=0)
    bpt1_zt = minlag1ind[bpt2_zt]
    breakpt_zt1 = (bpt1_zt + begin) / n
    breakpt_zt2 = (bpt2_zt + begin * 2) / n
    
    # Estimate final model with optimal break points from ADF test
    dummy1, dummy2 = create_dummies(n, bpt1_adf + begin, bpt2_adf + begin * 2)
    x1 = construct_regressors(n, x, dummy1, dummy2, model)
    b, e1, sig2, se = estimate(y, x1)
    
    # Calculate t-statistics
    t_stats = np.divide(b, se)
    
    # Create results object
    results = CointegrationResults()
    results.adf_statistic = float(adf_stat)
    results.adf_lag = lag
    results.adf_break1 = float(breakpt_adf1)
    results.adf_break2 = float(breakpt_adf2)
    results.za_statistic = float(za_stat)
    results.za_break1 = float(breakpt_za1)
    results.za_break2 = float(breakpt_za2)
    results.zt_statistic = float(zt_stat)
    results.zt_break1 = float(breakpt_zt1)
    results.zt_break2 = float(breakpt_zt2)
    results.coefficients = b
    results.standard_errors = se.flatten()
    results.t_statistics = t_stats
    results.n_obs = n
    results.model = model
    
    return results


def load_data_from_csv(filepath: str, y_col: int = 0, x_cols: Optional[list] = None) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load data from a CSV file for cointegration testing.
    
    Parameters
    ----------
    filepath : str
        Path to the CSV file
    y_col : int, default=0
        Column index for the dependent variable
    x_cols : list of int, optional
        Column indices for independent variables. If None, uses all columns except y_col.
    
    Returns
    -------
    y : numpy.ndarray
        Dependent variable
    x : numpy.ndarray
        Independent variables
    
    Examples
    --------
    >>> from pmct import load_data_from_csv
    >>> y, x = load_data_from_csv('data.csv', y_col=0, x_cols=[1, 2])
    """
    data = pd.read_csv(filepath, header=None)
    
    y = data.iloc[:, y_col].values.reshape(-1, 1)
    
    if x_cols is None:
        # Use all columns except y_col
        all_cols = list(range(data.shape[1]))
        all_cols.remove(y_col)
        x_cols = all_cols
    
    x = data.iloc[:, x_cols].values
    
    return y, x
