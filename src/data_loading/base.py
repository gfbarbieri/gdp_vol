"""
This module defines the abstract base class for data loaders.
"""

########################################################################
## IMPORTS
########################################################################

from abc import ABC, abstractmethod
from pandas import DataFrame

########################################################################
## BASE LOADER CLASS
########################################################################

class BaseLoader(ABC):
    """
    Abstract base class that defines the interface for data retrieval.
    Each concrete implementation must implement the load_data() method.
    """

    @abstractmethod
    def load_data(self) -> DataFrame:
        """
        Loads data and returns it as a pandas DataFrame.
        """
        pass