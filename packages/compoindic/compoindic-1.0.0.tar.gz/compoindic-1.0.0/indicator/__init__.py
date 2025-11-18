"""
Composite Indicator Builder Package
Author: Dr. Merwan Roudane
Email: merwanroudane920@gmail.com
GitHub: https://github.com/merwanroudane/indicators

A professional Python package for constructing composite indicators
using various methodologies based on OECD guidelines.
"""

__version__ = "1.0.0"
__author__ = "Dr. Merwan Roudane"
__email__ = "merwanroudane920@gmail.com"
__github__ = "https://github.com/merwanroudane/indicators"

from .methods import (
    EqualWeights,
    BOD_Calculation,
    Entropy_Calculation,
    PCA_Calculation,
    Minimal_Uncertainty,
    GeometricMean,
    HarmonicMean,
    FactorAnalysis_Calculation,
    CorrelationWeights,
    normalizar_dados,
    Result
)

from .gui import CompositeIndicatorApp, main

__all__ = [
    'EqualWeights',
    'BOD_Calculation',
    'Entropy_Calculation',
    'PCA_Calculation',
    'Minimal_Uncertainty',
    'GeometricMean',
    'HarmonicMean',
    'FactorAnalysis_Calculation',
    'CorrelationWeights',
    'normalizar_dados',
    'Result',
    'CompositeIndicatorApp',
    'main'
]
