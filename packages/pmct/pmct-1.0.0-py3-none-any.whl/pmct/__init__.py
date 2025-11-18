"""
PMCT: Python Module for Cointegration Tests with Two Endogenous Structural Breaks

This package implements three residual-based cointegration tests with two unknown
regime shifts based on Hatemi-J (2008).

Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/pmct

Original methodology: Hatemi-J, A. (2008). Tests for cointegration with two unknown 
regime shifts with an application to financial market integration. 
Empirical Economics, 35(3), 497-505.

Python implementation based on code by Dr. Alan Mustafa and Prof. Abdulnasser Hatemi-J.
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"

from .tests import cointegration_test_2breaks
from .core import estimate

__all__ = ['cointegration_test_2breaks', 'estimate']
