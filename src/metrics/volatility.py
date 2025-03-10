"""
This module contains classes for calculating a variety of volatility
metrics: standard deviation, coefficient of variation, cyclical
volatility, etc.

Classes
-------
Volatility
    A class for calculating volatility metrics.
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd

from typing import Union

########################################################################
## VOLATILITY CLASS
########################################################################

class Volatility:
    """
    A class for calculating volatility metrics.

    Attributes
    ----------
    dataframe : pd.DataFrame
        The DataFrame on which to calculate volatility metrics.

    Methods
    -------
    standard_deviation(
            self, column: str, window: int=None
        ) -> Union[float, pd.Series]:
        Calculate the standard deviation of a column.
    coefficient_of_variation(
            self, column: str, reference_col: str=None, window: int=None
        ) -> Union[float, pd.Series]:
        Calculate the coefficient of variation of a column.
    cyclical_volatility(
            self, cycle_col: str, reference_col: str=None
        ) -> float:
        Calculate the cyclical volatility of a column.
    rolling_volatility(
            self, column: str, window: int=4,
            method: Literal[
                'standard_deviation', 'coefficient_of_variation'
            ]='standard_deviation',
            reference_col: str=None
        ) -> pd.Series:
        Calculate the rolling volatility of a column.
    """

    def __init__(
            self, dataframe: pd.DataFrame, date_column: str=None
        ) -> None:
        """
        Initialize the Volatility class.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The DataFrame to calculate volatility metrics on.
        date_column : str, optional
            The name of the column containing dates. If provided, this
            column will be set as the index with appropriate frequency
            detection.
        """

        self.dataframe = dataframe

        # If date_column is provided, set it as the index.
        if date_column:

            # Ensure the date column is a datetime type.
            self.dataframe[date_column] = pd.to_datetime(
                self.dataframe[date_column]
            )

            # Set the date column as the index.
            self.dataframe = self.dataframe.set_index(date_column)

    def standard_deviation(
            self, column: str, window: int = None
        ) -> Union[float, pd.Series]:
        """
        Calculate the standard deviation of a column.

        Parameters
        ----------
        column : str
            The column for which to calculate the standard deviation.
        window : int, optional
            If provided, calculates the rolling standard deviation with
            the specified window size. If None, calculates the standard
            deviation for the entire column.

        Returns
        -------
        Union[float, pd.Series]
            If window is None, returns the standard deviation as a
            float. If window is provided, returns the rolling standard
            deviation as a pd.Series.

        Raises
        ------
        KeyError
            If column does not exist in the dataframe.
        ValueError
            If window is less than 1.
        """
        
        # If window is provided, calculate rolling standard deviation.
        if window is not None:

            # Raise an error if window is less than 1.
            if window < 1:
                raise ValueError("Window size must be at least 1.")
            
            # Calculate rolling standard deviation. You have to sort the
            # index first to ensure the rolling is done in the correct
            # order.
            std = (
                self.dataframe[column]
                .sort_index()
                .rolling(window=window)
                .std()
            )

        # Otherwise, calculate standard deviation for the entire column.
        else:
            std = self.dataframe[column].std()

        return std

    def coefficient_of_variation(
            self, column: str, reference_col: str=None, window: int=None
        ) -> Union[float, pd.Series]:
        """
        Calculate the coefficient of variation of a column.

        Parameters
        ----------
        column : str
            The column for which to calculate the coefficient of
            variation.
        reference_col : str, optional
            The column to use as a reference for calculating the
            coefficient of variation. If None, the coefficient of
            variation is calculated with respect to the column itself.
        window : int, optional
            If provided, calculates the rolling coefficient of
            variation with the specified window size. If None,
            calculates the coefficient of variation for the entire
            column.

        Returns
        -------
        Union[float, pd.Series]
            If window is None, returns the coefficient of variation as a
            float. If window is provided, returns the rolling
            coefficient of variation as a pd.Series.

        Raises
        ------
        ValueError
            If window is less than 1.
        """
        
        if window is not None:

            # Raise an error if window is less than 1.
            if window < 1:
                raise ValueError("Window size must be at least 1.")

            # Calculate rolling standard deviation for the numerator.
            std = (
                self.dataframe[column]
                .sort_index()
                .rolling(window=window)
                .std()
            )
            
            # If reference column is provided, use its mean as the
            # denominator. Otherwise, use the rolling mean of the column
            # itself as the denominator.
            if reference_col is not None:
                mean = (
                    self.dataframe[reference_col]
                    .sort_index()
                    .rolling(window=window)
                    .mean()
                )
            else:
                mean = (
                    self.dataframe[column]
                    .sort_index()
                    .rolling(window=window)
                    .mean()
                )

        else:

            # Calculate standard deviation.
            std = self.dataframe[column].std()

            # If reference column is provided, use its mean as the
            # denominator. Otherwise, use the mean of the column itself
            # as the denominator.
            if reference_col is not None:
                mean = self.dataframe[reference_col].mean()
            else:
                mean = self.dataframe[column].mean()

        # Calculate coefficient of variation.
        co_var = std / mean

        return co_var