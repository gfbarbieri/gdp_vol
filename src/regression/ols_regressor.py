"""
This module contains classes for performing ordinary least squares
regression. Provides a simple wrapper around statsmodels for linear or
OLS regressions on time-series columns.

Classes
-------
OLSRegressor
    A class for performing ordinary least squares regression.
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd
import statsmodels.api as sm

########################################################################
## OLS REGRESSOR CLASS
########################################################################

class OLSRegressor:
    """
    A class for performing ordinary least squares regression.

    Attributes
    ----------
    dataframe : pd.DataFrame
        The DataFrame on which to perform the regression.
    model : statsmodels.regression.linear_model.RegressionResultsWrapper
        The fitted model.
    results : statsmodels.regression.linear_model.RegressionResultsWrapper
        The results of the fitted model.

    Methods
    -------
    fit(self, y_col: str, x_cols: list[str]) -> RegressionResultsWrapper:
        Fit the OLSRegressor model.
    predict(self, dataframe: pd.DataFrame) -> pd.Series:
        Predict the dependent variable using the OLSRegressor model.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        """
        Initialize the OLSRegressor class.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The DataFrame on which to perform the regression.
        """

        self.dataframe = dataframe
        self.model = None
        self.results = None

    def fit(
            self, y_col: str, x_cols: list[str], constant: bool=True
        ) -> None:
        """
        Fit the OLSRegressor model. Missing values are dropped before
        fitting.

        Parameters
        ----------
        y_col : str
            The dependent variable.
        x_cols : list[str]
            The independent variables.
        constant : bool, optional
            Whether to add a constant term to the model. Default is
            True.

        Returns
        -------
        statsmodels.regression.linear_model.RegressionResultsWrapper
            The fitted model.
        """

        # Drop missing values and reset the index.
        data = (
            self.dataframe
            .dropna(subset=[y_col] + x_cols)
            .reset_index(drop=True)
        )

        # Add constant term for intercept if constant is True.
        if constant:
            X = sm.add_constant(data[x_cols])
        else:
            X = data[x_cols]

        # Fit the model
        self.model = sm.OLS(data[y_col], X)

        # Get the results
        self.results = self.model.fit()

    def predict(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        Make predictions using the fitted model.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame containing the predictor variables.

        Returns
        -------
        pd.Series
            Predicted values.
        """

        # Check if the model has been fitted.
        if self.results is None:
            raise ValueError("Model must be fitted before making predictions.")

        # Add constant term to the input dataframe.
        X = sm.add_constant(dataframe)

        # Make predictions.
        preds = self.results.predict(X)

        return preds
