"""
This module contains classes for transforming data, including
differencing, log transforms, filtering, and detrending.

Classes
-------
DataTransformer
    A class for transforming data.
"""

########################################################################
## IMPORTS
########################################################################

import numpy as np
import pandas as pd
import statsmodels.tsa.api as tsa

########################################################################
## DATA TRANSFORMER CLASS
########################################################################

class DataTransformer:
    """
    A class for transforming data.

    Attributes
    ----------
    dataframe : pd.DataFrame
        The DataFrame to transform.

    Methods
    -------
    log_transform(self) -> pd.DataFrame:
        Create a new column with the log of the specified column.
    difference(self) -> pd.DataFrame:
        Compute discrete or log differences (depending on your approach)
        to get growth rates or changes.
    hp_filter(self) -> pd.DataFrame:
        Apply the Hodrick-Prescott filter on the specified column, store
        the cycle/trend in new columns.
    bk_filter(self) -> pd.DataFrame:
        Apply the Baxter-King filter on the specified column, store the
        cycle/trend in new columns.
    linear_detrend(self) -> pd.DataFrame:
        Fit a linear trend and store the detrended series.

    Examples
    --------
    Log transform the data:

    .. code-block:: python

        # Create a DataTransformer object.
        transformer = DataTransformer(dataframe=dataframe)

        # Log transform the data.
        transformer.log_transform(column, new_col_name)

    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Initialize the DataTransformer class.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The DataFrame to transform.
        """

        self.dataframe = dataframe

    def log_transform(self, column: str, new_col_name: str=None) -> None:
        """
        Create a new column with the log of the specified column.

        Parameters
        ----------
        column : str
            The column to log transform.
        new_col_name : str, optional
            The name of the new column. If None, then the name will be
            the original column name with "_log" appended.
        """

        if new_col_name is None:
            new_col_name = f"{column}_log"

        self.dataframe[new_col_name] = np.log(self.dataframe[column])

    def difference(
            self, column: str, date_column: str, periods: int=1,
            new_col_name: str=None
        ) -> None:
        """
        Compute discrete or log differences (depending on your approach)
        to get growth rates or changes.

        Parameters
        ----------
        column : str
            The column to difference.
        date_column : str
            The date column on which to sort the dataframe. This is
            necessary because the difference method does not take into
            account the date column.
        periods : int, optional
            The number of periods to difference.
        new_col_name : str, optional
            The name of the new column. If None, then the name will be
            the original column name with "_diff" appended.
        """

        # If user does not specify a new column name.
        if new_col_name is None:
            new_col_name = f"{column}_diff"

        # Sort the dataframe by the date column.
        self.dataframe.sort_values(by=date_column, inplace=True)

        # Compute the differences.
        self.dataframe[new_col_name] = self.dataframe[column].diff(periods)

    def hp_filter(
            self, column: str, lamb: float, cycle_col_name: str=None,
            trend_col_name: str=None
        ) -> None:
        """
        Apply the Hodrick-Prescott filter on the specified column, store
        the cycle/trend in new columns.

        Parameters
        ----------
        column : str
            The column to filter.
        lamb : float
            The lambda (smoothing) parameter for the HP filter. From the
            statsmodels documentation: "The Hodrick-Prescott smoothing
            parameter. A value of 1600 is suggested for quarterly data.
            Ravn and Uhlig suggest using a value of 6.25 (1600/4**4) for
            annual data and 129600 (1600*3**4) for monthly data."
        cycle_col_name : str, optional
            The name of the new column for the cycle. If None, then the
            name will be the original column name with "_cycle"
            appended.
        trend_col_name : str, optional
            The name of the new column for the trend. If None, then the
            name will be the original column name with "_trend"
            appended.
        """

        # If user does not specify a new column name.
        if cycle_col_name is None:
            cycle_col_name = f"{column}_cycle"

        if trend_col_name is None:
            trend_col_name = f"{column}_trend"

        # Apply the HP filter.
        cycle, trend = tsa.filters.hpfilter(
            self.dataframe[column], lamb=lamb
        )

        # Store the cycle and trend in the new columns.
        self.dataframe[cycle_col_name] = cycle
        self.dataframe[trend_col_name] = trend

    def bk_filter(
            self, column: str, low: int=6, high: int=32, K: int=12,
            cycle_col_name: str=None, trend_col_name: str=None
        ) -> None:
        """
        Apply the Baxter-King filter on the specified column, store the
        cycle in a new column.

        Parameters
        ----------
        column : str
            The column to filter.
        low : int, optional
            The low frequency cutoff. Default is 6 for quarterly data.
        high : int, optional
            The high frequency cutoff. Default is 32 for quarterly data.
        K : int, optional
            Lead-lag length. A la BK, default is 12 for quarterly data.
            The effect is that the filter column is missing the first
            and last K entries.
        cycle_col_name : str, optional
            The name of the new column for the cycle. If None, then the
            name will be the original column name with "_cycle"
            appended.
        trend_col_name : str, optional
            The name of the new column for the trend. If None, then the
            name will be the original column name with "_trend"
            appended.
        """

        # If user does not specify a new column name.
        if cycle_col_name is None:
            cycle_col_name = f"{column}_cycle"

        if trend_col_name is None:
            trend_col_name = f"{column}_trend"

        # Apply the Baxter-King filter.
        cycle = tsa.filters.bkfilter(
            self.dataframe[column], low=low, high=high, K=K
        )

        trend = self.dataframe[column] - cycle

        # Store the cycle and trend in the new columns.
        self.dataframe[cycle_col_name] = cycle
        self.dataframe[trend_col_name] = trend

    def linear_detrend(
            self, column: str, order: int=1, new_col_name: str=None,
            trend_col_name: str=None
        ) -> None:
        """
        Fit a linear trend and store the detrended series.

        Parameters
        ----------
        column : str
            The column to detrend.
        order : int, optional
            The order of the trend. Default is 1 for a linear trend.
        new_col_name : str, optional
            The name of the new column. If None, then the name will be
            the original column name with "_detrended" appended.
        trend_col_name : str, optional
            The name of the new column for the trend. If None, then the
            name will be the original column name with "_trend"
            appended.
        """

        # If user does not specify a new column name.
        if new_col_name is None:
            new_col_name = f"{column}_detrended"

        if trend_col_name is None:
            trend_col_name = f"{column}_trend"

        # Fit a linear trend.
        detrended = tsa.tsatools.detrend(self.dataframe[column], order=order)

        # Store the detrended and trend series in the new columns.
        self.dataframe[new_col_name] = detrended
        self.dataframe[trend_col_name] = self.dataframe[column] - detrended