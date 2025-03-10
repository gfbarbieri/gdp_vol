"""
This module contains classes for modeling Vector Autoregression (VAR)
models. It provides functionality for fitting VAR models, forecasting,
and analyzing impulse response functions for time series data.

Classes
-------
VARRegression
    A class for performing Vector Autoregression (VAR) on time series
    data.
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.figure import Figure
from statsmodels.tsa.api import VAR
from typing import Optional, Any, List, Tuple

########################################################################
## VAR REGRESSION CLASS
########################################################################

class VARRegressor:
    """
    A class for performing Vector Autoregression (VAR) on time series
    data.
    
    Attributes
    ----------
    data : pd.DataFrame
        The input time series data.
    lags : int
        The number of lags to include in the VAR model.
    date_column : Optional[str]
        The name of the column containing dates, if the DataFrame
        doesn't already use a DatetimeIndex.
    model : Optional[VAR]
        The VAR model instance created from the input data. Set after
        calling fit().
    results : Optional[VARResults]
        The fitted VAR model results. Set after calling fit().
    
    Methods
    -------
    fit(
            columns: Optional[List[str]] = None, trend: str = 'c',
            **kwargs
        ) -> None:
        Fit the VAR model to the provided data.
    forecast(steps: int) -> np.ndarray:
        Forecast future values using the fitted VAR model.
    get_summary() -> str:
        Retrieve a summary of the fitted VAR model results.
    plot_irf(steps: int = 10) -> Figure:
        Generate an Impulse Response Function (IRF) plot.
    
    Examples
    --------

    .. code-block:: python
    
        # Create a VARRegressor instance with a DataFrame and 2 lags
        var_model = VARRegressor(data=time_series_df, lags=2, date_column='date')
        
        # Fit the model to the data.
        var_model.fit(columns=['gdp', 'inflation'])
        
        # Forecast the next 5 time steps.
        forecasts = var_model.forecast(steps=5)

    """
    
    def __init__(
            self, data: pd.DataFrame, lags: int=1,
            date_column: Optional[str]=None,
            freq: Optional[str]='QS'
        ) -> None:
        """
        Initialize the VARRegressor instance with time series data and
        number of lags.
        
        Parameters
        ----------
        data : pd.DataFrame
            A pandas DataFrame containing the time series data where
            each column represents a different variable.
        lags : int, optional
            The number of lags to include in the VAR model (default is
            1).
        date_column : Optional[str], optional
            The name of the column containing dates, if the DataFrame doesn't 
            already use a DatetimeIndex. If provided, this column will be set 
            as index during fitting.
        freq : Optional[str], optional
            The frequency of the time series data. Default is 'QS' for
            quarterly data starting at the beginning of periods.
        """

        self.data = data
        self.lags = lags
        self.freq = freq
        self.model = None
        self.results = None

        # If date_column is provided, set it as the index.
        if date_column:

            # Ensure the date column is a datetime type.
            self.data[date_column] = pd.to_datetime(
                self.data[date_column]
            )

            # Set the date column as the index.
            self.data = self.data.set_index(date_column)

    def fit(self, columns: Optional[List[str]] = None, **kwargs) -> None:
        """
        Fit the VAR model to the provided data using the specified
        number of lags.
        
        This method creates the VAR model instance from the data and
        fits the model. The results are stored in the 'results'
        attribute.
        
        Parameters
        ----------
        columns : Optional[List[str]], optional
            List of column names to include in the VAR model. If None, 
            all columns in the data will be used.
        **kwargs : dict
            Additional arguments to pass to the VAR.fit() method from
            statsmodels, such as 'ic' (information criterion) or
            'maxlags'.

        Notes
        -----
        This method must be called before using forecasting or analysis
        methods.
        
        Raises
        ------
        ValueError
            If the data doesn't have a DatetimeIndex and no date_column was provided.
        """

        # Sort the index to ensure chronological order.
        self.data.sort_index(inplace=True)

        # Create a VAR model instance using the selected data.
        if columns is not None:
            self.model = VAR(self.data[columns], freq=self.freq)
        else:
            self.model = VAR(self.data, freq=self.freq)

        # Fit the VAR model.
        self.results = self.model.fit(self.lags, **kwargs)
    
    def forecast(self, steps: int) -> np.ndarray:
        """
        Forecast future values using the fitted VAR model.
        
        Parameters
        ----------
        steps : int
            The number of future time steps to forecast.
        
        Returns
        -------
        forecast : np.ndarray
            A numpy array containing the forecasted values for each
            variable. Shape will be (steps, n_variables).
        
        Raises
        ------
        ValueError
            If the model has not been fitted yet.
        
        Notes
        -----
        The forecast is based on the last observations in the original 
        data.
        """

        # Ensure the model has been fitted.
        if self.results is None:
            raise ValueError(
                "Model has not been fitted yet. Please call the fit() "
                "method first."
            )
        
        # Determine the number of lags used in the fitted model.
        lag_order: int = self.results.k_ar
        
        # Extract the last 'lag_order' observations from the data to use
        # as the forecast starting point.
        last_obs: np.ndarray = self.data.values[-lag_order:]
        
        # Generate and return the forecast for the specified number of
        # steps.
        forecast: np.ndarray = self.results.forecast(y=last_obs, steps=steps)

        return forecast

    def get_summary(self) -> str:
        """
        Retrieve a summary of the fitted VAR model results.
        
        Returns
        -------
        summary_str : str
            A string representation of the fitted model's summary
            including coefficients, statistics, and diagnostic
            information.
        
        Raises
        ------
        ValueError
            If the model has not been fitted yet.
        """

        # Ensure the model has been fitted.
        if self.results is None:
            raise ValueError(
                "Model has not been fitted yet. Please call the fit() "
                "method first."
            )
        
        return self.results.summary()

    def plot_irf(self, steps: int = 10) -> Figure:
        """
        Generate and return an Impulse Response Function (IRF) plot for
        the fitted VAR model.
        
        The IRF shows how variables respond over time to a shock in one
        of the variables.
        
        Parameters
        ----------
        steps : int, optional
            The number of steps for which to compute the IRF (default is
            10).
        
        Returns
        -------
        fig : Figure
            A matplotlib Figure object containing the IRF plot.
        
        Raises
        ------
        ValueError
            If the model has not been fitted yet.
        
        Notes
        -----
        The plot shows the response of each variable to shocks in all
        variables. For a model with n variables, the plot will have n
        rows and n columns.
        """

        # Ensure the model has been fitted.
        if self.results is None:
            raise ValueError(
                "Model has not been fitted yet. Please call the fit() "
                "method first."
            )
        
        # Create the IRF object using the fitted model results.
        irf_obj = self.results.irf(steps)
        
        # Generate the IRF plot, which returns a matplotlib Figure.
        fig = irf_obj.plot(orth=False)

        return fig
