"""
Unit tests for the regression module.
"""

########################################################################
## IMPORTS
########################################################################

import pytest
import pandas as pd
import numpy as np
from src.regression.ols_regressor import OLSRegressor
from src.regression.var_regressor import VARRegressor

########################################################################
## TESTS
########################################################################

def test_ols_regressor_basic(sample_data: pd.DataFrame) -> None:
    """
    Test basic OLS regression functionality.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for regression.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))
    sample_data['interest_rate'] = np.random.normal(3, 0.5, len(sample_data))

    # Create OLSRegressor instance.
    regressor = OLSRegressor(sample_data)

    # Fit the model.
    regressor.fit('values', ['inflation', 'interest_rate'])

    # Verify model and results are set.
    assert regressor.model is not None
    assert regressor.results is not None

    # Verify results contain expected attributes.
    assert hasattr(regressor.results, 'params')
    assert hasattr(regressor.results, 'pvalues')
    assert hasattr(regressor.results, 'rsquared')

    # Verify number of coefficients (intercept + 2 variables).
    assert len(regressor.results.params) == 3

    # Verify R-squared is between 0 and 1.
    assert 0 <= regressor.results.rsquared <= 1

def test_ols_regressor_predict(sample_data: pd.DataFrame) -> None:
    """
    Test prediction functionality of OLSRegressor.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for regression.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))
    sample_data['interest_rate'] = np.random.normal(3, 0.5, len(sample_data))

    # Create OLSRegressor instance.
    regressor = OLSRegressor(sample_data)

    # Fit the model.
    regressor.fit('values', ['inflation', 'interest_rate'])

    # Create test data for prediction.
    test_data = pd.DataFrame({
        'inflation': np.random.normal(2, 0.5, 5),
        'interest_rate': np.random.normal(3, 0.5, 5)
    })

    # Make predictions.
    predictions = regressor.predict(test_data)

    # Verify predictions are a Series with correct length.
    assert isinstance(predictions, pd.Series)
    assert len(predictions) == len(test_data)

def test_ols_regressor_missing_data(sample_data: pd.DataFrame) -> None:
    """
    Test handling of missing data in OLSRegressor.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for regression.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))
    sample_data['interest_rate'] = np.random.normal(3, 0.5, len(sample_data))

    # Add some missing values.
    sample_data.loc[0:2, 'inflation'] = np.nan

    # Create OLSRegressor instance.
    regressor = OLSRegressor(sample_data)

    # Fit the model - should handle missing data gracefully.
    regressor.fit('values', ['inflation', 'interest_rate'])

    # Verify model was fitted successfully.
    assert regressor.model is not None
    assert regressor.results is not None

def test_var_regressor_basic(sample_data: pd.DataFrame) -> None:
    """
    Test basic VAR regression functionality.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for VAR.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))

    # Create VARRegressor instance.
    var_model = VARRegressor(
        data=sample_data,
        lags=1,
        date_column='dates',
        freq='QE'
    )

    # Fit the model.
    var_model.fit(columns=['values', 'inflation'])

    # Verify model and results are set.
    assert var_model.model is not None
    assert var_model.results is not None

    # Verify results contain expected attributes.
    assert hasattr(var_model.results, 'params')
    assert hasattr(var_model.results, 'pvalues')
    assert hasattr(var_model.results, 'aic')

def test_var_regressor_forecast(sample_data: pd.DataFrame) -> None:
    """
    Test forecasting functionality of VARRegressor.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for VAR.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))

    # Create VARRegressor instance.
    var_model = VARRegressor(
        data=sample_data,
        lags=1,
        date_column='dates',
        freq='QE'
    )

    # Fit the model.
    var_model.fit(columns=['values', 'inflation'])

    # Generate forecast.
    forecast = var_model.forecast(steps=5)

    # Verify forecast shape.
    assert isinstance(forecast, np.ndarray)
    assert forecast.shape[0] == 5  # Number of steps.
    assert forecast.shape[1] == 2  # Number of variables.

def test_var_regressor_irf(sample_data: pd.DataFrame) -> None:
    """
    Test impulse response function calculation of VARRegressor.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for VAR.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))
    # Create VARRegressor instance.
    var_model = VARRegressor(
        data=sample_data,
        lags=1,
        date_column='dates',
        freq='QE'
    )

    # Fit the model.
    var_model.fit(columns=['values', 'inflation'])

    # Generate IRF plot.
    fig = var_model.plot_irf(steps=4)

    # Verify plot was created.
    assert fig is not None
    assert hasattr(fig, 'axes')

def test_var_regressor_summary(sample_data: pd.DataFrame) -> None:
    """
    Test summary generation of VARRegressor.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for VAR.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))
    # Create VARRegressor instance.
    var_model = VARRegressor(
        data=sample_data,
        lags=1,
        date_column='dates',
        freq='QE'
    )

    # Fit the model.
    var_model.fit(columns=['values', 'inflation'])

    # Get summary.
    summary = var_model.get_summary()

    # Verify summary is a string.
    assert isinstance(summary.summary, str)
    assert len(summary.summary) > 0

def test_var_regressor_unfitted_errors(sample_data: pd.DataFrame) -> None:
    """
    Test error handling for unfitted VARRegressor.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Add required columns for VAR.
    sample_data['inflation'] = np.random.normal(2, 0.5, len(sample_data))

    # Create VARRegressor instance without fitting.
    var_model = VARRegressor(
        data=sample_data,
        lags=1,
        date_column='dates',
        freq='QE'
    )

    # Verify appropriate errors are raised.
    with pytest.raises(ValueError, match="Model has not been fitted yet"):
        var_model.forecast(steps=5)

    with pytest.raises(ValueError, match="Model has not been fitted yet"):
        var_model.plot_irf(steps=10)

    with pytest.raises(ValueError, match="Model has not been fitted yet"):
        var_model.get_summary() 