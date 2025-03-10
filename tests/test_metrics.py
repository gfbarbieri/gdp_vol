"""
Unit tests for the metrics module.
"""

########################################################################
## IMPORTS
########################################################################

import pytest
import pandas as pd
import numpy as np
from src.metrics.volatility import Volatility

########################################################################
## TESTS
########################################################################

def test_standard_deviation(sample_data: pd.DataFrame) -> None:
    """
    Test standard deviation calculation.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data, date_column='dates')

    # Calculate standard deviation.
    std_dev = vol_calculator.standard_deviation('values')

    # Verify the result is a float.
    assert isinstance(std_dev, float)

    # Verify standard deviation is non-negative.
    assert std_dev >= 0

    # Verify the calculation matches pandas std.
    expected_std_dev = sample_data['values'].std()
    np.testing.assert_almost_equal(std_dev, expected_std_dev)

def test_coefficient_of_variation(sample_data: pd.DataFrame) -> None:
    """
    Test coefficient of variation calculation.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data, date_column='dates')

    # Calculate coefficient of variation.
    cv = vol_calculator.coefficient_of_variation('values')

    # Verify the result is a float.
    assert isinstance(cv, float)

    # Verify coefficient of variation is non-negative.
    assert cv >= 0

    # Verify the calculation matches expected formula.
    expected_cv = sample_data['values'].std() / sample_data['values'].mean()
    np.testing.assert_almost_equal(cv, expected_cv)

def test_coefficient_of_variation_with_reference(
        sample_data: pd.DataFrame
    ) -> None:
    """
    Test coefficient of variation calculation with reference column.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a reference column.
    sample_data_with_ref = sample_data.copy()
    sample_data_with_ref['reference'] = sample_data['values'] * 2

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data_with_ref, date_column='dates')

    # Calculate coefficient of variation with reference.
    cv = vol_calculator.coefficient_of_variation(
        'values', reference_col='reference'
    )

    # Verify the result is a float.
    assert isinstance(cv, float)

    # Verify coefficient of variation is non-negative.
    assert cv >= 0

    # Verify the calculation matches expected formula.
    expected_cv = (
        sample_data_with_ref['values'].std() /
        sample_data_with_ref['reference'].mean()
    )

    np.testing.assert_almost_equal(cv, expected_cv)

def test_rolling_standard_deviation(sample_data: pd.DataFrame) -> None:
    """
    Test rolling standard deviation calculation.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data, date_column='dates')

    # Calculate rolling standard deviation with window size 4.
    rolling_std = vol_calculator.standard_deviation('values', window=4)

    # Verify the result is a pandas Series.
    assert isinstance(rolling_std, pd.Series)

    # Verify the length matches input data.
    assert len(rolling_std) == len(sample_data)

    # Verify first window-1 values are NaN.
    assert rolling_std.iloc[:3].isna().all()

    # Verify remaining values are non-negative.
    assert (rolling_std.dropna() >= 0).all()

    # Create a reference with dates as index for comparison
    sample_with_dates = sample_data.copy().set_index('dates')
    sample_with_dates.index = pd.to_datetime(sample_with_dates.index)
    expected_rolling_std = sample_with_dates['values'].rolling(window=4).std()

    # Compare values rather than series directly since index might
    # differ.
    np.testing.assert_array_almost_equal(
        rolling_std.dropna().values, 
        expected_rolling_std.dropna().values
    )

def test_rolling_coefficient_of_variation(sample_data: pd.DataFrame) -> None:
    """
    Test rolling coefficient of variation calculation.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data, date_column='dates')

    # Calculate rolling coefficient of variation.
    rolling_cv = vol_calculator.coefficient_of_variation('values', window=4)

    # Verify the result is a pandas Series.
    assert isinstance(rolling_cv, pd.Series)

    # Verify the length matches input data.
    assert len(rolling_cv) == len(sample_data)

    # Verify first window-1 values are NaN.
    assert rolling_cv.iloc[:3].isna().all()

    # Verify remaining values are non-negative where not NaN.
    assert (rolling_cv.dropna() >= 0).all()

    # Create a reference with dates as index for comparison.
    sample_with_dates = sample_data.copy().set_index('dates')
    sample_with_dates.index = pd.to_datetime(sample_with_dates.index)
    rolling_std = sample_with_dates['values'].rolling(window=4).std()
    rolling_mean = sample_with_dates['values'].rolling(window=4).mean()
    expected_rolling_cv = rolling_std / rolling_mean

    # Compare values rather than series directly since index might
    # differ.
    np.testing.assert_array_almost_equal(
        rolling_cv.dropna().values, 
        expected_rolling_cv.dropna().values
    )

def test_rolling_coefficient_of_variation_with_reference(
        sample_data: pd.DataFrame
    ) -> None:
    """
    Test rolling coefficient of variation with reference column.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a reference column.
    sample_data_with_ref = sample_data.copy()
    sample_data_with_ref['reference'] = sample_data['values'] * 2

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data_with_ref, date_column='dates')

    # Calculate rolling coefficient of variation with reference.
    rolling_cv = vol_calculator.coefficient_of_variation(
        'values', reference_col='reference', window=4
    )

    # Verify the result is a pandas Series.
    assert isinstance(rolling_cv, pd.Series)

    # Verify the length matches input data.
    assert len(rolling_cv) == len(sample_data_with_ref)

    # Verify first window-1 values are NaN.
    assert rolling_cv.iloc[:3].isna().all()

    # Create a reference with dates as index for comparison.
    sample_with_dates = sample_data_with_ref.copy().set_index('dates')
    sample_with_dates.index = pd.to_datetime(sample_with_dates.index)
    
    # Calculate expected values using rolling mean for reference
    rolling_std = sample_with_dates['values'].rolling(window=4).std()
    rolling_ref_mean = sample_with_dates['reference'].rolling(window=4).mean()
    expected_rolling_cv = rolling_std / rolling_ref_mean

    # Compare values rather than series directly since index might
    # differ.
    np.testing.assert_array_almost_equal(
        rolling_cv.dropna().values,
        expected_rolling_cv.dropna().values
    )

def test_invalid_column() -> None:
    """
    Test handling of invalid column name.
    """

    # Create a dataframe.
    df = pd.DataFrame({
        'values': [1, 2, 3],
        'dates': ['2022-01-01', '2022-01-02', '2022-01-03']
    })

    # Create a Volatility instance.
    vol_calculator = Volatility(df, date_column='dates')

    # Verify invalid column raises KeyError.
    with pytest.raises(KeyError):
        vol_calculator.standard_deviation('non_existent_column')

def test_invalid_date_column() -> None:
    """
    Test handling of invalid date column.
    """

    # Create a dataframe.
    df = pd.DataFrame({
        'values': [1, 2, 3],
        'dates': ['2022-01-01', '2022-01-02', '2022-01-03']
    })

    # Verify invalid date column raises KeyError.
    with pytest.raises(KeyError):
        Volatility(df, date_column='non_existent_column')

def test_invalid_window_in_standard_deviation(
        sample_data: pd.DataFrame
    ) -> None:
    """
    Test handling of invalid window size for standard deviation.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data, date_column='dates')

    # Verify invalid window size raises ValueError.
    with pytest.raises(ValueError, match="Window size must be at least 1"):
        vol_calculator.standard_deviation('values', window=0)

def test_invalid_window_in_coefficient_of_variation(
        sample_data: pd.DataFrame
    ) -> None:
    """
    Test handling of invalid window size for coefficient of variation.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample data for testing.
    """

    # Create a Volatility instance.
    vol_calculator = Volatility(sample_data, date_column='dates')

    # Verify invalid window size raises ValueError.
    with pytest.raises(ValueError, match="Window size must be at least 1"):
        vol_calculator.coefficient_of_variation('values', window=0)

def test_empty_dataframe() -> None:
    """
    Test handling of empty dataframe.
    """

    # Create an empty dataframe.
    empty_df = pd.DataFrame({'values': [], 'dates': []})

    # Create a Volatility instance. Not using date_column since it's
    # empty.
    vol_calculator = Volatility(empty_df)

    # Verify standard deviation for empty series is NaN.
    assert np.isnan(vol_calculator.standard_deviation('values'))

def test_constant_series() -> None:
    """
    Test handling of constant series.
    """

    # Create a dataframe with constant values.
    dates = pd.date_range(start='2022-01-01', periods=10, freq='D')
    constant_df = pd.DataFrame({'values': [1.0] * 10, 'dates': dates})

    # Create a Volatility instance.
    vol_calculator = Volatility(constant_df, date_column='dates')

    # Verify standard deviation is zero for constant series.
    assert vol_calculator.standard_deviation('values') == 0.0