"""
Copyright (c) 2025 Adam Ulichny

This source code is licensed under the MIT OR Apache-2.0 license
that can be found in the LICENSE-MIT or LICENSE-APACHE files
at the root of this source tree.

powerlawrs: A Python package for analyzing power-law distributions.
"""

# Import the native Rust module
from . import _powerlawrs

# Expose the submodules from the native module at the package level
stats = _powerlawrs.stats
util = _powerlawrs.util
dist = _powerlawrs.dist

# For convenience, you can also expose nested modules
exponential = dist.exponential
powerlaw = dist.powerlaw
pareto = dist.pareto

# The user's example `Powerlaw` class needs these
estimation = pareto.estimation
gof = pareto.gof
hypothesis = pareto.hypothesis

class Powerlaw:
    """
    A class to fit and analyze power-law distributions in a given dataset.
    """
    def __init__(self, data):
        """
        Initializes the Powerlaw object with data.

        Args:
            data (list[float]): The dataset to analyze.
        """
        self.data = data
        self.alphas = None
        self.x_mins = None
        self.Fitment = None

    def fit(self):
        """
        Fits the data to a power-law distribution.

        This method finds the optimal x_min and alpha parameters for the power-law
        fit and assesses the goodness of fit. The results are stored in the
        object's attributes.
        """
        # Ensure data is sorted for some of the underlying functions
        sorted_data = sorted(self.data)

        # find_alphas_fast returns a list of tuples, but we want two separate lists
        (self.x_mins, self.alphas) = estimation.find_alphas_fast(sorted_data)

        # gof expects the full dataset, not just the tail
        self.Fitment = gof.gof(sorted_data, self.x_mins, self.alphas)
        return

def fit(data):
    """
    Fits the data to a power-law distribution.

    This function is a convenience wrapper that instantiates the Powerlaw class,
    fits the data, and returns the fitment results.

    Args:
        data (list[float]): The dataset to analyze.

    Returns:
        The fitment result object.
    """
    p = Powerlaw(data)
    p.fit()
    return p.Fitment

# Define what gets imported with 'from powerlawrs import *'
__all__ = [
    "fit",
    "Powerlaw",
    "stats",
    "util",
    "dist",
    "exponential",
    "powerlaw",
    "pareto",
    "estimation",
    "gof",
    "hypothesis",
]

# Package-level metadata
__version__ = "0.1.0"