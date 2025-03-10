"""
Unit tests for the data transformation module.
"""

########################################################################
## IMPORTS
########################################################################

import pytest
import pandas as pd
import numpy as np

from src.data_transformation.transformer import DataTransformer

########################################################################
## TESTS
########################################################################

def test_log_transform(sample_data: pd.DataFrame) -> None:
    """
    Test log transformation functionality.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Create a transformer instance.
    transformer = DataTransformer(sample_data)

    # Apply log transformation to gdp column.
    transformer.log_transform('values', 'values_log')

    # Verify the new column exists in the dataframe.
    assert 'values_log' in transformer.dataframe.columns

    # Verify the log transformation calculation is correct.
    np.testing.assert_array_almost_equal(
        transformer.dataframe['values_log'],
        np.log(sample_data['values'])
    )

def test_difference(sample_data: pd.DataFrame) -> None:
    """
    Test difference calculation functionality.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Create a transformer instance.
    transformer = DataTransformer(sample_data)

    # Calculate first difference of gdp, sorting by dates.
    transformer.difference(
        'values', date_column='dates', periods=1, new_col_name='values_diff'
    )

    # Verify the new column exists in the dataframe.
    assert 'values_diff' in transformer.dataframe.columns
    
    # Sort the sample data for comparison.
    expected = sample_data.sort_values(by='dates').copy()
    expected['values_diff'] = expected['values'].diff(1)
    
    # Verify the difference calculation is correct.
    pd.testing.assert_series_equal(
        transformer.dataframe['values_diff'], 
        expected['values_diff'],
        check_names=False
    )

def test_hp_filter(sample_data: pd.DataFrame) -> None:
    """
    Test Hodrick-Prescott filter functionality.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Create a transformer instance.
    transformer = DataTransformer(sample_data)

    # Apply Hodrick-Prescott filter to gdp with lambda=1600 (quarterly
    # data).
    transformer.hp_filter('values', lamb=1600)

    # Verify the trend and cycle columns exist.
    assert 'values_trend' in transformer.dataframe.columns
    assert 'values_cycle' in transformer.dataframe.columns

    # Verify the decomposition is correct (trend + cycle = original).
    np.testing.assert_array_almost_equal(
        transformer.dataframe['values'],
        (
            transformer.dataframe['values_trend'] +
            transformer.dataframe['values_cycle']
        )
    )

def test_bk_filter(sample_data: pd.DataFrame) -> None:
    """
    Test Baxter-King filter functionality.
    
    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """
    
    # Create a transformer instance.
    transformer = DataTransformer(sample_data)
    
    # Apply Baxter-King filter to gdp with default parameters.
    transformer.bk_filter('values')
    
    # Verify the cycle and trend columns exist.
    assert 'values_cycle' in transformer.dataframe.columns
    assert 'values_trend' in transformer.dataframe.columns
    
    # Verify the decomposition results in NaN for first and last K
    # entries.
    K = 12  # Default K parameter.
    assert transformer.dataframe['values_cycle'].iloc[:K].isna().all()
    assert transformer.dataframe['values_cycle'].iloc[-K:].isna().all()
    
    # For non-NaN values, verify that trend + cycle = original.
    mask = ~transformer.dataframe['values_cycle'].isna()
    np.testing.assert_array_almost_equal(
        transformer.dataframe.loc[mask, 'values'],
        (
            transformer.dataframe.loc[mask, 'values_trend'] +
            transformer.dataframe.loc[mask, 'values_cycle']
        )
    )

def test_linear_detrend(sample_data: pd.DataFrame) -> None:
    """
    Test linear detrending functionality.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Create a transformer instance.
    transformer = DataTransformer(sample_data)

    # Apply linear detrending to gdp.
    transformer.linear_detrend('values')

    # Verify the detrended and trend columns exist.
    assert 'values_detrended' in transformer.dataframe.columns
    assert 'values_trend' in transformer.dataframe.columns

    # Verify the decomposition is correct (trend + detrended =
    # original).
    np.testing.assert_array_almost_equal(
        transformer.dataframe['values'],
        (
            transformer.dataframe['values_trend'] +
            transformer.dataframe['values_detrended']
        )
    )
    
    # Calculate and verify the trend is effectively zero in the
    # detrended series.
    x = np.arange(len(transformer.dataframe))
    slope = np.polyfit(x, transformer.dataframe['values_detrended'], 1)[0]
    assert abs(slope) < 1e-10  # Should be close to zero.

def test_method_chaining(sample_data: pd.DataFrame) -> None:
    """
    Test sequential transformation functionality (no method chaining in
    implementation).

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Create a transformer instance.
    transformer = DataTransformer(sample_data)

    # Apply multiple transformations sequentially.
    transformer.log_transform('values', 'values_log')
    transformer.difference(
        'values_log', date_column='dates', periods=1,
        new_col_name='values_growth'
    )
    transformer.hp_filter('values_growth', lamb=1600)

    # Verify all transformed columns exist.
    assert 'values_log' in transformer.dataframe.columns
    assert 'values_growth' in transformer.dataframe.columns
    assert 'values_growth_trend' in transformer.dataframe.columns
    assert 'values_growth_cycle' in transformer.dataframe.columns

def test_invalid_column(sample_data: pd.DataFrame) -> None:
    """
    Test handling of invalid column names.

    Parameters
    ----------
    sample_data : pd.DataFrame
        Sample GDP data for testing.
    """

    # Create a transformer instance.
    transformer = DataTransformer(sample_data)

    # Verify that invalid column raises KeyError.
    with pytest.raises(KeyError):
        transformer.log_transform('invalid_column')