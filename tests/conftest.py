"""
Common test fixtures and configuration for pytest.
"""

########################################################################
## IMPORTS
########################################################################

import numpy as np
import os
import pandas as pd
import pytest
import yaml

########################################################################
## FIXTURES
########################################################################

@pytest.fixture
def sample_data() -> pd.DataFrame:
    """
    Create a sample GDP time series for testing.
    """

    # Create a sample GDP time series.
    dates = pd.date_range(start='2000-01-01', periods=100, freq='QE')

    # Create a sample GDP time series.
    np.random.seed(42)
    gdp = np.random.normal(100, 10, 100).cumsum() + 1000
    gdp_ls_g = np.random.normal(100, 10, 100).cumsum() + 1000

    # Return a pandas DataFrame with the GDP time series.
    return pd.DataFrame({'gdp': gdp, 'gdp_ls_g': gdp_ls_g, 'dates': dates})

@pytest.fixture
def sample_csv_file(tmp_path: str, sample_data: pd.DataFrame) -> str:
    """
    Create a temporary CSV file with sample data.

    Parameters
    ----------
    tmp_path : str
        The path to the temporary directory.
    sample_data : pd.DataFrame
        The sample data to write to the CSV file.

    Returns
    -------
    file_path : str
        The path to the temporary CSV file.

    Notes
    ----
    `tmp_path` is a pytest fixture that provides a temporary directory.
    """

    # Create a temporary CSV file with sample data.
    file_path = os.path.join(tmp_path, "test_gdp.csv")

    # Write the sample GDP data to the CSV file.
    sample_data.to_csv(file_path, index=False)

    # Return the path to the temporary CSV file.
    return file_path

@pytest.fixture
def sample_excel_file(tmp_path: str, sample_data: pd.DataFrame) -> str:
    """
    Create a temporary Excel file with sample data.

    Parameters
    ----------
    tmp_path : str
        The path to the temporary directory.
    sample_data : pd.DataFrame
        The sample data to write to the Excel file.

    Returns
    -------
    file_path : str
        The path to the temporary Excel file.

    Notes
    ----
    `tmp_path` is a pytest fixture that provides a temporary directory.
    """

    # Create a temporary Excel file with sample data.
    file_path = os.path.join(tmp_path, "test_gdp.xlsx")

    # Convert dates to strings before writing to Excel.
    df_to_write = sample_data.copy()
    df_to_write['dates'] = df_to_write['dates'].astype(str)
    df_to_write.to_excel(file_path, index=False)

    # Return the path to the temporary Excel file.
    return file_path

@pytest.fixture
def sample_json_file(tmp_path: str, sample_data: pd.DataFrame) -> str:
    """
    Create a temporary JSON file with sample data.

    Parameters
    ----------
    tmp_path : str
        The path to the temporary directory.
    sample_data : pd.DataFrame
        The sample data to write to the JSON file.

    Returns
    -------
    file_path : str
        The path to the temporary JSON file.

    Notes
    ----
    `tmp_path` is a pytest fixture that provides a temporary directory.
    """

    # Create a temporary JSON file with sample data.
    file_path = os.path.join(tmp_path, "test_gdp.json")

    # Convert dates to strings before writing to JSON.
    df_to_write = sample_data.copy()
    df_to_write['dates'] = df_to_write['dates'].astype(str)
    df_to_write.to_json(file_path, orient='records', index=False)

    # Return the path to the temporary JSON file.
    return file_path

@pytest.fixture
def sample_yaml_file(tmp_path: str) -> str:
    """
    Create a temporary YAML configuration file.

    Parameters
    ----------
    tmp_path : str
        The path to the temporary directory.

    Returns
    -------
    file_path : str
        The path to the temporary YAML file.
    """

    # Create a temporary YAML file with configuration.
    file_path = os.path.join(tmp_path, "config.yaml")

    # Create a simple configuration structure
    config = {
        'data_source': {
            'url': 'https://example.com/data',
            'format': 'csv'
        },
        'analysis': {
            'start_date': '2000-01-01',
            'end_date': '2024-12-31',
            'frequency': 'quarterly'
        },
        'output': {
            'format': 'json',
            'path': './results'
        }
    }
    
    # Write the configuration to file
    with open(file_path, 'w') as f:
        yaml.dump(config, f)

    return file_path