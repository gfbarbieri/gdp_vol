"""
Unit tests for the data loading module.
"""

########################################################################
## IMPORTS
########################################################################

import pandas as pd
import pytest

from datetime import datetime

from src.data_loading.loaders import (
    DataRetriever, CSVLoader, ExcelLoader, JSONLoader, YAMLLoader,
    LoadAPI
)

########################################################################
## TEST FACTORY PATTERN
########################################################################

def test_data_retriever(
        sample_csv_file: str, 
        sample_excel_file: str, 
        sample_json_file: str,
        sample_yaml_file: str
    ) -> None:
    """
    Test the DataRetriever factory creates appropriate loaders.

    Parameters
    ----------
    sample_csv_file : str
        Path to the sample CSV file.
    sample_excel_file : str
        Path to the sample Excel file.
    sample_json_file : str
        Path to the sample JSON file.
    sample_yaml_file : str
        Path to the sample YAML file.

    Notes
    ----
    https://example.com and https://api.example.com are used as
    examples. This is a reserved domain for testing purposes, managed by
    IANA (Internet Assigned Numbers Authority) at
    https://iana.org/help/example-domains. It's guaranteed to never be a
    real domain, making it safe to use for testing purposes.
    """

    # Test CSV loader creation.
    csv_loader = DataRetriever.create(sample_csv_file)
    assert isinstance(csv_loader, CSVLoader)

    remote_csv_loader = DataRetriever.create("https://example.com/data.csv")
    assert isinstance(remote_csv_loader, CSVLoader)

    # Test Excel loader creation.
    excel_loader = DataRetriever.create(sample_excel_file)
    assert isinstance(excel_loader, ExcelLoader)

    remote_excel_loader = DataRetriever.create("https://example.com/data.xlsx")
    assert isinstance(remote_excel_loader, ExcelLoader)
    
    # Test JSON loader creation.
    json_loader = DataRetriever.create(sample_json_file)
    assert isinstance(json_loader, JSONLoader)

    remote_json_loader = DataRetriever.create("https://example.com/data.json")
    assert isinstance(remote_json_loader, JSONLoader)

    # Test YAML loader creation.
    yaml_loader = DataRetriever.create(sample_yaml_file)
    assert isinstance(yaml_loader, YAMLLoader)

    remote_yaml_loader = DataRetriever.create("https://example.com/data.yaml")
    assert isinstance(remote_yaml_loader, YAMLLoader)

    # Test API loader creation.
    api_loader = DataRetriever.create("https://api.example.com/data")
    assert isinstance(api_loader, LoadAPI)

########################################################################
## TEST CSV LOADER
########################################################################

def test_csv_loader(
        sample_csv_file: str, sample_data: pd.DataFrame
    ) -> None:
    """
    Test CSV file loading functionality.

    Parameters
    ----------
    sample_csv_file : str
        Path to the sample CSV file.
    sample_data : pd.DataFrame
        Expected data for comparison.
    """

    # Create a CSV loader instance.
    loader = CSVLoader(sample_csv_file)

    # Load the data. The delimiter and dtype are specified as ',' and
    # 'object' to test that the load_data method can handle delimiters
    # and data types as keyword arguments. This should convert all
    # columns to strings.
    df = loader.load_data(delimiter=',', dtype='object')

    # You could either convert the sample data to match the dtype of
    # the loaded data, or convert the loaded data to match the dtype of
    # the sample data. Here, we'll convert the loaded data to match the
    # dtype of the sample data.
    # 
    # Convert values to floats in sample data for comparison.
    # string dates to datetime objects in sample data for
    # comparison.
    df['values'] = df['values'].astype(float)
    df['dates'] = pd.to_datetime(df['dates'])

    # Compare loaded data with expected data.
    pd.testing.assert_frame_equal(df, sample_data)

def test_remote_csv_loader(mocker: pytest.MonkeyPatch) -> None:
    """
    Test remote CSV file loading functionality.

    Parameters
    ----------
    mocker : pytest.MonkeyPatch
        Pytest mocker fixture for mocking HTTP requests.
    """

    # Create a mock response with sample CSV data. The mock response is
    # a CSV object with a 'dates' and 'values' column. Hardcoded for
    # testing purposes. The mock response is encoded to ensure that the
    # CSVLoader can read the mock response as a CSV file.
    mock_response = mocker.Mock()
    mock_response.text = "dates,values\n2000-01-01,1000\n2000-04-01,1010"
    mock_response.content = mock_response.text.encode()

    # Patch the requests.get function to return our mock. The
    # 'request.get()' function is used by the CSVLoader to load the
    # data from the remote file. So we need to patch it to return our
    # mock response.
    mocker.patch('requests.get', return_value=mock_response)

    # Create a CSV loader instance for remote file.
    loader = CSVLoader(path_or_url="https://example.com/data.csv")

    # Load the data. The delimiter and dtype are specified as ',' and
    # 'object' to test that the load_data method can handle delimiters
    # and data types as keyword arguments. This should convert all
    # columns to strings.
    df = loader.load_data(delimiter=',', dtype='object')

    # Verify the loaded data. Check that the loaded data is a Pandas
    # DataFrame and that the 'dates' and 'values' columns are present.
    assert isinstance(df, pd.DataFrame)
    assert 'dates' in df.columns
    assert 'values' in df.columns

########################################################################
## TEST EXCEL LOADER
########################################################################

def test_excel_loader(
        sample_excel_file: str, sample_data: pd.DataFrame
    ) -> None:
    """
    Test Excel file loading functionality.

    Parameters
    ----------
    sample_excel_file : str
        Path to the sample Excel file.
    sample_data : pd.DataFrame
        Expected data for comparison.
    """

    # Create an Excel loader instance.
    loader = ExcelLoader(sample_excel_file)

    # Load the data.
    df = loader.load_data()

    # You could either convert the sample data to match the dtype of
    # the loaded data, or convert the loaded data to match the dtype of
    # the sample data. Here, we'll convert the sample data to match the
    # dtype of the loaded data.
    #
    # Convert dates to strings in sample data for comparison.
    sample_data['dates'] = sample_data['dates'].astype(str)

    # Compare loaded data with expected data.
    pd.testing.assert_frame_equal(df, sample_data)

def test_remote_excel_loader(mocker: pytest.MonkeyPatch, sample_excel_file: str) -> None:
    """
    Test remote Excel file loading functionality.

    Parameters
    ----------
    mocker : pytest.MonkeyPatch
        Pytest mocker fixture for mocking HTTP requests.
    sample_excel_file : str
        Path to a sample Excel file to use as mock data.
    """

    # Read the sample Excel file to use as mock data.
    with open(sample_excel_file, 'rb') as f:
        excel_content = f.read()

    # Create a mock response with the Excel file content.
    mock_response = mocker.Mock()
    mock_response.content = excel_content

    # Patch the requests.get function to return our mock.
    mocker.patch('requests.get', return_value=mock_response)

    # Create an Excel loader instance for remote file.
    loader = ExcelLoader("https://example.com/data.xlsx")

    # Load the data.
    df = loader.load_data()

    # Verify the loaded data.
    assert isinstance(df, pd.DataFrame)
    assert 'dates' in df.columns
    assert 'values' in df.columns

########################################################################
## TEST JSON LOADER
########################################################################

def test_json_loader(
        sample_json_file: str, sample_data: pd.DataFrame
    ) -> None:
    """
    Test JSON file loading functionality.

    Parameters
    ----------
    sample_json_file : str
        Path to the sample JSON file.
    sample_data : pd.DataFrame
        Expected data for comparison.
    """

    # Create a JSON loader instance.
    loader = JSONLoader(sample_json_file)

    # Load the data.
    df = loader.load_data()

    # Convert dates to strings in sample data for comparison.
    sample_data['dates'] = sample_data['dates'].astype(str)

    # Compare loaded data with expected data.
    pd.testing.assert_frame_equal(df, sample_data)

def test_remote_json_loader(mocker: pytest.MonkeyPatch) -> None:
    """
    Test remote JSON file loading functionality.

    Parameters
    ----------
    mocker : pytest.MonkeyPatch
        Pytest mocker fixture for mocking HTTP requests.
    """

    # Create a mock response with sample JSON data.
    mock_response = mocker.Mock()

    # The mock response is a JSON object with an 'observations' key. The
    # 'observations' key is a list of dictionaries, each containing
    # 'dates' and 'value' keys.
    mock_response.text = """
    {
        "observation_start": "2000-01-01",
        "observation_end": "9999-12-31",
        "observations": [
            {"dates": "2000-01-01", "value": 1000},
            {"dates": "2000-04-01", "value": 1010}
        ]
    }
    """

    # Patch the requests.get function to return our mock.
    mocker.patch('requests.get', return_value=mock_response)

    # Create a JSON loader instance for remote file with data_key.
    loader = DataRetriever.create(
        path_or_url="https://example.com/data.json", data_key="observations"
    )

    # Load the data.
    df = loader.load_data(data_key="observations")

    # Verify the loaded data.
    assert isinstance(df, pd.DataFrame)
    assert 'dates' in df.columns
    assert 'value' in df.columns

########################################################################
## TEST YAML LOADER
########################################################################

def test_yaml_loader(sample_yaml_file: str) -> None:
    """
    Test YAML file loading functionality.

    Parameters
    ----------
    sample_yaml_file : str
        Path to the sample YAML configuration file.
    """

    # Create a YAML loader instance.
    loader = YAMLLoader(sample_yaml_file)

    # Load the configuration.
    config = loader.load_data()

    # Verify the configuration structure.
    assert isinstance(config, dict)
    assert 'data_source' in config
    assert 'analysis' in config
    assert 'output' in config
    
    # Verify specific configuration values.
    assert config['data_source']['file_type'] == 'json'
    assert config['analysis']['frequency'] == 'quarterly'
    assert config['output']['file_type'] == 'json'

def test_remote_yaml_loader(mocker: pytest.MonkeyPatch) -> None:
    """
    Test remote YAML file loading functionality.

    Parameters
    ----------
    mocker : pytest.MonkeyPatch
        Pytest mocker fixture for mocking HTTP requests.
    """

    # Create a mock response with sample YAML configuration.
    mock_response = mocker.Mock()

    # The mock response is a YAML object with a 'data_source' key and
    # an 'analysis' key. The 'data_source' key contains a 'url' key and
    # a 'file_type' key. The 'analysis' key contains an 'observation_start'
    # key and a 'frequency' key.
    mock_response.text = """
    data_source:
      url: https://example.com/data
      file_type: json
    analysis:
      observation_start: 2000-01-01
      frequency: quarterly
    """

    # Patch the requests.get function to return our mock.
    mocker.patch('requests.get', return_value=mock_response)

    # Create a YAML loader instance for remote file.
    loader = YAMLLoader("https://example.com/config.yaml")

    # Load the configuration.
    config = loader.load_data()

    # Verify the configuration structure. Note that the observation_start
    # is a string in the mock response, but PyYAML library converts it
    # to a datetime object. So we need to convert the datetime object to
    # a string for comparison.
    assert isinstance(config, dict)
    assert 'data_source' in config
    assert 'analysis' in config
    assert config['data_source']['file_type'] == 'json'
    assert config['analysis']['observation_start'] == datetime(2000, 1, 1).date()
    assert config['analysis']['frequency'] == 'quarterly'

########################################################################
## TEST API LOADER
########################################################################

def test_load_api(mocker: pytest.MonkeyPatch) -> None:
    """
    Test API data loading functionality.

    Parameters
    ----------
    mocker : pytest.MonkeyPatch
        Pytest mocker fixture for mocking HTTP requests.
    """

    # Create a mock response with sample JSON data.
    mock_response = mocker.Mock()

    # The mock response is a JSON object with a 'data' key. The
    # 'observations' key is a list of dictionaries, each containing
    # 'dates' and 'value' keys.
    mock_response.json.return_value = {
        'observation_start': '2000-01-01',
        'observation_end': '9999-12-31',
        'observations': [
            {'dates': '2000-01-01', 'value': 1000},
            {'dates': '2000-04-01', 'value': 1010}
        ]
    }

    # Patch the requests.get function to return our mock.
    mocker.patch('requests.get', return_value=mock_response)

    # Create an API loader instance with test parameters.
    loader = LoadAPI(
        "https://api.example.com/data",
        params={'observation_start': '2000-01-01'},
        headers={'Authorization': 'Bearer token'}
    )

    # Load the data.
    df = loader.load_data(data_key="observations")

    # Verify the loaded data.
    assert (isinstance(df, pd.DataFrame))
    assert ('value' in df.columns)
    assert ('dates' in df.columns)

########################################################################
## TEST INVALID FILE TYPE
########################################################################

def test_invalid_file_type() -> None:
    """
    Test handling of invalid file types.
    """

    # Attempt to create a loader for an unsupported file type.
    with pytest.raises(ValueError, match="Unsupported file type: .xml"):
        DataRetriever.create("data.xml")

    # Test with a file without extension
    with pytest.raises(ValueError, match="Unsupported file type: "):
        DataRetriever.create("data")

    # Test with an unsupported remote file type
    with pytest.raises(ValueError, match="Unsupported file type: .xml"):
        DataRetriever.create("https://example.com/data.xml") 