"""
This module contains functions for analyzing time series data.
"""

########################################################################
## IMPORTS
########################################################################

import numpy as np

########################################################################
## FUNCTIONS
########################################################################

def find_crossovers(
        left: 'pandas.Series', right: 'pandas.Series'
    ) -> list:
    """
    Finds indices where two series cross over each other.
    
    Parameters
    ----------
    left
        First time series
    right
        Second time series
    
    Returns
    -------
    list
        Indices where the two series cross each other
    """


    # Reindex the series to ensure they have the same index.
    # common_index = left.index.intersection(right.index)
    # left = left.reindex(common_index).dropna()
    # right = right.reindex(common_index).dropna()

    # Calculate the difference between the two series.
    diff = left - right

    # Find sign changes.
    crossovers = np.where(np.sign(diff.values[:-1]) != np.sign(diff.values[1:]))[0]
    
    return left.index[crossovers]