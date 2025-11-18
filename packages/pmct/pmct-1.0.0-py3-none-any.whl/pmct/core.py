"""
Core estimation functions for cointegration tests with structural breaks.

This module contains the fundamental estimation procedures used in the
cointegration tests with two endogenous structural breaks.
"""

import numpy as np
import math


def estimate(y, x):
    """
    Estimate regression parameters using Ordinary Least Squares (OLS).
    
    Parameters
    ----------
    y : numpy.ndarray
        Dependent variable (n x 1 array)
    x : numpy.ndarray
        Independent variables (n x k array)
    
    Returns
    -------
    b : numpy.ndarray
        Estimated coefficients (k x 1 array)
    e : numpy.ndarray
        Residuals (n x 1 array)
    sig2 : float
        Variance of residuals
    se : numpy.ndarray
        Standard errors of coefficients (k x 1 array)
    
    Notes
    -----
    This function estimates the model y = Xb + e using OLS.
    Standard errors are calculated using the formula: SE(b) = sqrt(diag((X'X)^-1) * sigma^2)
    """
    # Calculate (X'X)^-1
    m = np.linalg.inv(np.dot(np.transpose(x), x))
    
    # Calculate coefficients: b = (X'X)^-1 X'y
    b = np.dot(m, np.dot(np.transpose(x), y))
    
    # Calculate residuals: e = y - Xb
    e = y - np.dot(x, b)
    
    # Calculate variance: sigma^2 = e'e / (n - k)
    sig2 = np.dot(np.transpose(e), e) / (y.shape[0] - x.shape[1])
    
    # Ensure sig2 is scalar
    if hasattr(sig2, 'shape') and sig2.shape != ():
        sig2 = sig2[0, 0]
    
    # Calculate standard errors: SE = sqrt(diag((X'X)^-1) * sigma^2)
    se = np.sqrt(np.multiply(np.diag(m), sig2))
    se = se.reshape(-1, 1)
    
    return b, e, sig2, se


def adf_test(y, x, kmax, choice):
    """
    Modified Augmented Dickey-Fuller test for each breakpoint.
    
    Parameters
    ----------
    y : numpy.ndarray
        Dependent variable
    x : numpy.ndarray
        Independent variables
    kmax : int
        Maximum lag order
    choice : int
        Lag selection criterion:
        1 = pre-specified AR lag
        2 = AIC-chosen AR lag
        3 = BIC-chosen AR lag
        4 = downward-t-chosen AR lag
    
    Returns
    -------
    tstat : float
        ADF test statistic
    lag : int
        Selected lag length
    
    Notes
    -----
    This implements the modified ADF test as described in Hatemi-J (2008).
    The test checks for unit roots in the residuals of the cointegrating regression.
    """
    n = y.shape[0]
    b, e, sig2, se = estimate(y, x)
    
    # Calculate first differences of residuals
    de = e[1:n] - e[0:n-1]
    
    ic = 0
    k = kmax
    temp1 = np.zeros((kmax + 1, 1))
    temp2 = np.zeros((kmax + 1, 1))
    
    while k >= 0:
        yde = de[k:n]
        n1 = yde.shape[0]
        xe = e[k:n-1]
        
        j = 1
        while j <= k:
            xe = np.concatenate((xe, de[k-j:n-1-j]), axis=1)
            j = j + 1
        
        b, e1, sig2, se = estimate(yde, xe)
        
        if choice == 1:  # K is pre-specified
            temp1[k] = -1000  # Set a random negative constant
            temp2[k] = float(b[0, 0] / se[0, 0])
            break
        elif choice == 2:  # K is determined by AIC
            aic = np.log((np.dot(np.transpose(e1), e1)) / n1) + 2 * (k + 2) / n1
            if hasattr(aic, 'shape') and aic.shape != ():
                aic = aic[0, 0]
            ic = aic
        elif choice == 3:  # K is determined by BIC
            bic = np.log((np.dot(np.transpose(e1), e1)) / n1) + (k + 2) * np.log(n1) / n1
            if hasattr(bic, 'shape') and bic.shape != ():
                bic = bic[0, 0]
            ic = bic
        elif choice == 4:  # K is determined by downward t
            t_stat = float(b[k, 0] / se[k, 0])
            if abs(t_stat) >= 1.96 or k == 0:
                temp1[k] = -1000
                temp2[k] = float(b[0, 0] / se[0, 0])
                break
        
        temp1[k] = ic
        temp2[k] = float(b[0, 0] / se[0, 0])
        k = k - 1
    
    lag = np.where(temp1 == np.amin(temp1))[0]
    if len(lag) > 0:
        lag = lag[0]
    else:
        lag = 0
    
    tstat = temp2[lag]
    if hasattr(tstat, '__len__'):
        tstat = float(tstat)
    
    return float(tstat), int(lag)


def phillips_test(y, x):
    """
    Modified Phillips-Perron tests (Za and Zt) for each breakpoint.
    
    Parameters
    ----------
    y : numpy.ndarray
        Dependent variable
    x : numpy.ndarray
        Independent variables
    
    Returns
    -------
    za : float
        Phillips Za test statistic
    zt : float
        Phillips Zt test statistic
    
    Notes
    -----
    This implements the modified Phillips-Perron tests as described in 
    Phillips and Ouliaris (1990) and adapted by Hatemi-J (2008) for 
    structural breaks.
    """
    n = y.shape[0]
    
    # OLS regression: b = (X'X)^-1 X'y
    xtx = np.dot(np.transpose(x), x)
    xty = np.dot(np.transpose(x), y)
    b = np.dot(np.linalg.inv(xtx), xty)
    e = y - np.dot(x, b)
    
    # OLS regression on lagged residuals
    e_lag = e[0:n-1]
    e_current = e[1:n]
    
    # For scalar regression: be = (e_lag' * e_current) / (e_lag' * e_lag)
    be = np.dot(np.transpose(e_lag), e_current) / np.dot(np.transpose(e_lag), e_lag)
    
    # Extract scalar value
    if hasattr(be, 'shape'):
        be = float(be.item()) if be.size == 1 else float(be[0, 0])
    
    ue = e_current - e_lag * be
    
    # Calculate bandwidth number
    nu = ue.shape[0]
    ue_lag = ue[0:nu-1]
    ue_current = ue[1:nu]
    
    # bu = (ue_lag' * ue_current) / (ue_lag' * ue_lag)
    bu = np.dot(np.transpose(ue_lag), ue_current) / np.dot(np.transpose(ue_lag), ue_lag)
    
    # Extract scalar value
    if hasattr(bu, 'shape'):
        bu_val = float(bu.item()) if bu.size == 1 else float(bu[0, 0])
    else:
        bu_val = float(bu)
    
    uu = ue_current - ue_lag * bu_val
    
    su = float((np.power(uu, 2)).mean())
    
    a2 = (4 * np.power(bu_val, 2) * su / (np.power((1 - bu_val), 8))) / (su / (np.power(1 - bu_val, 4)))
    
    bandwidth = 1.3221 * (np.power(a2 * nu, 0.2))
    
    m = bandwidth
    j = 1
    lemda = 0
    
    while j <= m:
        ueTue = np.dot(np.transpose(ue[0:nu-j]), ue[j:nu])
        gama = ueTue / nu
        c = j / m
        Pi = math.pi
        w = (75 / ((6 * Pi * c) ** 2)) * (math.sin(1.2 * Pi * c) / (1.2 * Pi * c) - math.cos(1.2 * Pi * c))
        lemda = lemda + w * gama
        j = j + 1
    
    # Calculate Za and Zt for each t
    p = np.sum(np.multiply(e[0:n-1], e[1:n]) - lemda) / np.sum(np.power(e[0:n-1], 2))
    za = n * (p - 1)
    
    sigma2 = 2 * lemda + (np.dot(np.transpose(ue), ue) / nu)
    s = sigma2 / (np.dot(np.transpose(e[0:n-1]), e[0:n-1]))
    zt = (p - 1) / np.sqrt(s)
    
    # Ensure scalars
    if hasattr(za, 'shape') and za.shape != ():
        za = float(za[0, 0])
    if hasattr(zt, 'shape') and zt.shape != ():
        zt = float(zt[0, 0])
    
    return float(za), float(zt)


def create_dummies(n, t1, t2):
    """
    Create dummy variables for structural breaks.
    
    Parameters
    ----------
    n : int
        Number of observations
    t1 : int
        First breakpoint
    t2 : int
        Second breakpoint
    
    Returns
    -------
    dummy1 : numpy.ndarray
        First dummy variable (n x 1)
    dummy2 : numpy.ndarray
        Second dummy variable (n x 1)
    """
    dummy1 = np.concatenate((np.zeros((t1, 1)), np.ones((n - t1, 1))), axis=0)
    dummy2 = np.concatenate((np.zeros((t2, 1)), np.ones((n - t2, 1))), axis=0)
    return dummy1, dummy2


def construct_regressors(n, x, dummy1, dummy2, model):
    """
    Construct the regression matrix based on the specified model.
    
    Parameters
    ----------
    n : int
        Number of observations
    x : numpy.ndarray
        Original independent variables
    dummy1 : numpy.ndarray
        First dummy variable
    dummy2 : numpy.ndarray
        Second dummy variable
    model : int
        Model specification:
        2 = C (constant only)
        3 = C/T (constant and trend)
        4 = C/S (constant with regime shifts in slope)
    
    Returns
    -------
    x1 : numpy.ndarray
        Constructed regression matrix
    """
    if model == 3:
        # Model with constant, dummies, and trend
        trend = np.arange(1, n + 1).reshape(-1, 1)
        x1 = np.concatenate((np.ones((n, 1)), dummy1, dummy2, trend, x), axis=1)
    elif model == 4:
        # Model with constant, dummies, and interacted slopes
        x1 = np.concatenate((
            np.ones((n, 1)), 
            dummy1, 
            dummy2, 
            x,
            np.multiply(dummy1, x), 
            np.multiply(dummy2, x)
        ), axis=1)
    elif model == 2:
        # Model with constant and dummies only
        x1 = np.concatenate((np.ones((n, 1)), dummy1, dummy2, x), axis=1)
    else:
        raise ValueError(f"Invalid model specification: {model}. Must be 2, 3, or 4.")
    
    return x1
