"""
This module contains classes for loading data from various sources,
including local files (CSV, Excel, JSON, YAML), remote files (HTTP(S)),
and API endpoints.

Classes
-------
DataRetriever
    Factory class that decides which DataRetrieval subclass to use based
    on the filepath or URL pattern.
CSVLoader
    Concrete implementation for reading CSV files from local disk or
    HTTP(S).
ExcelLoader
    Concrete implementation for reading Excel (XLSX) files from local
    disk or HTTP(S).
YAMLLoader
    Concrete implementation for reading YAML files from local disk or
    HTTP(S).
JSONLoader
    Concrete implementation for reading JSON files from local disk or
    HTTP(S).
LoadAPI
    Concrete implementation for reading data from an HTTP API endpoint.
"""

########################################################################
## IMPORTS
########################################################################

import os
import requests
import yaml

from io import StringIO, BytesIO
from pandas import DataFrame, read_csv, read_excel, read_json

from .base import BaseLoader

########################################################################
## FACTORY CLASS
########################################################################

class DataRetriever:
    """
    Factory class that decides which DataRetrieval subclass to use based
    on the filepath or URL pattern.

    Attributes
    ----------
    path_or_url : str
        The file path or URL.
    kwargs : dict
        Optional keyword arguments to pass to specific
        retrievers (like delimiter for TXT files, data_format for API,
        etc.).

    Methods
    -------
    create(path_or_url, **kwargs)
        Create a DataRetriever object based on the extension or
        protocol.

    Examples
    --------
    >>> retriever = DataRetriever.create("data.csv", delimiter=",")
    >>> data = retriever.load_data()
    """

    @staticmethod
    def create(path_or_url: str, **kwargs) -> BaseLoader:
        """
        Create a DataRetriever object based on the extension or
        protocol.

        Parameters
        ----------
        path_or_url : str
            The file path or URL.
        kwargs : dict
            Optional keyword arguments to pass to specific
            retrievers (like delimiter for TXT files, data_format for API, etc.).

        Returns
        -------
        Base
            An instance of a class that implements Base.
        """

        # CASE 1: User passes a URL, which could either be an API
        # endpoint or a remote file.
        if path_or_url.startswith("http") or path_or_url.startswith("https"):

            # Check if the URL is a file or an API endpoint. If the URL
            # has a file extension, we'll assume it's a file; otherwise,
            # we'll assume it's an API endpoint.
            extsn = os.path.splitext(path_or_url)[1]

            # CASE 1A: URL contains a file extension-like, suggesting a
            # remote file.
            if extsn != "":
                # Get the delimiter from the kwargs.
                delimiter = kwargs.get("delimiter", None)
                
                # Create appropriate loader based on extension.
                if extsn in [".csv", ".txt", ".tsv"]:
                    return CSVLoader(path_or_url, delimiter)
                elif extsn in [".xlsx", ".xls"]:
                    return ExcelLoader(path_or_url)
                elif extsn in [".yaml", ".yml"]:
                    return YAMLLoader(path_or_url)
                elif extsn in [".json"]:
                    return JSONLoader(path_or_url)
                else:
                    raise ValueError(f"Unsupported file type: {extsn}")

            # CASE 1B: URL does not contain a file extension, suggesting
            # an API endpoint.
            else:
                # Get the details form the kwargs.
                parameters = kwargs.get("parameters", {})
                headers = kwargs.get("headers", {})
                response_dtype = kwargs.get("response_dtype", None)

                return LoadAPI(
                    path_or_url, parameters, headers, response_dtype
                )

        # CASE 2: User passes a local file path, which could be a CSV,
        # Excel, YAML, or JSON file.
        extsn = os.path.splitext(path_or_url)[1]

        # CASE 2A: CSV file.
        if extsn in [".csv", ".txt", ".tsv"]:
            delimiter = kwargs.get("delimiter", None)
            return CSVLoader(path_or_url, delimiter)
        # CASE 2B: Excel file.
        elif extsn in [".xlsx", ".xls"]:
            return ExcelLoader(path_or_url)
        # CASE 2C: YAML file.
        elif extsn in [".yaml", ".yml"]:
            return YAMLLoader(path_or_url)
        # CASE 2D: JSON file.
        elif extsn in [".json"]:
            return JSONLoader(path_or_url)
        # CASE 2E: Unsupported file type.
        else:
            raise ValueError(f"Unsupported file type: {extsn}")

########################################################################
## FILE LOADER IMPLEMENTATIONS
########################################################################

class CSVLoader(BaseLoader):
    """
    Concrete implementation for reading CSV files from local disk or
    HTTP(S).
    """

    def __init__(self, path_or_url: str):
        """
        Parameters
        ----------
        path_or_url : str
            The path or URL to the CSV file.
        """

        self.path_or_url = path_or_url
        self.is_remote = path_or_url.startswith(("http://", "https://"))

    def load_data(self, **kwargs) -> DataFrame:
        """
        Load the data from the CSV file and return as a DataFrame.
        
        Returns
        -------
        DataFrame
            The data from the CSV file.

        Notes
        -----
        The `kwargs` parameter is passed to the `read_csv` function.
        """

        # CASE 1: The file is remote.
        if self.is_remote:
            # Download the file content.
            response = requests.get(self.path_or_url)
            response.raise_for_status()
            
            # Create a StringIO object with the content.
            content = StringIO(response.text)
            df = read_csv(content, **kwargs)

        # CASE 2: The file is local.
        else:
            df = read_csv(self.path_or_url, **kwargs)

        # Return the DataFrame.
        return df

class ExcelLoader(BaseLoader):
    """
    Concrete implementation for reading Excel (XLSX) files from local
    disk or HTTP(S).
    """

    def __init__(self, path_or_url: str) -> None:
        """
        Parameters
        ----------
        path_or_url : str
            The path or URL to the Excel file.
        """

        self.path_or_url = path_or_url
        self.is_remote = path_or_url.startswith(("http://", "https://"))

    def load_data(self, **kwargs) -> DataFrame:
        """
        Load the data from the Excel file and return as a DataFrame.
        
        Returns
        -------
        DataFrame
            The data from the Excel file.
        """

        # CASE 1: The file is remote.
        if self.is_remote:
            # Download the file content.
            response = requests.get(self.path_or_url)
            response.raise_for_status()
            
            # Create a BytesIO object with the content.
            content = BytesIO(response.content)
            df = read_excel(content, **kwargs)

        # CASE 2: The file is local.
        else:
            df = read_excel(self.path_or_url, **kwargs)

        return df

class YAMLLoader(BaseLoader):
    """
    Concrete implementation for reading YAML files from local disk or
    HTTP(S).
    """

    def __init__(self, path_or_url: str) -> None:
        """
        Parameters
        ----------
        path_or_url : str
            The path or URL to the YAML file.
        """

        self.path_or_url = path_or_url
        self.is_remote = path_or_url.startswith(("http://", "https://"))

    def load_data(self) -> DataFrame:
        """
        Load the data from the YAML file and return as a DataFrame.
        
        Returns
        -------
        DataFrame
            The data from the YAML file.
        """

        # CASE 1: The file is remote.
        if self.is_remote:
            # Download the file content.
            response = requests.get(self.path_or_url)
            response.raise_for_status()

            # Parse YAML from the response text.
            data = yaml.safe_load(response.text)

        # CASE 2: The file is local.
        else:
            # Load YAML data from local file.
            with open(self.path_or_url, 'r') as f:
                data = yaml.safe_load(f)

        return data

class JSONLoader(BaseLoader):
    """
    Concrete implementation for reading JSON files from local disk or
    HTTP(S).
    """

    def __init__(self, path_or_url: str) -> None:
        """
        Parameters
        ----------
        path_or_url : str
            The path or URL to the JSON file.
        """

        self.path_or_url = path_or_url
        self.is_remote = path_or_url.startswith(("http://", "https://"))

    def load_data(self, **kwargs) -> DataFrame:
        """
        Load the data from the JSON file and return as a DataFrame.
        
        Returns
        -------
        DataFrame
            The data from the JSON file.

        Notes
        -----
        The `kwargs` parameter is passed to the `read_json` function.
        """

        # CASE 1: The file is remote.
        if self.is_remote:
            # Download the file content.
            response = requests.get(self.path_or_url)
            response.raise_for_status()

            # Parse JSON from the response text.
            df = read_json(StringIO(response.text), orient='records', **kwargs)

        # CASE 2: The file is local.
        else:
            df = read_json(self.path_or_url, orient='records', **kwargs)

        return df

########################################################################
## API LOADER IMPLEMENTATION
########################################################################

class LoadAPI(BaseLoader):
    """
    Concrete implementation for reading data from an HTTP API endpoint.
    """

    def __init__(
        self, base_url: str, parameters: dict, headers: dict, 
        response_dtype: str=None
    ) -> None:
        """
        Parameters
        ----------
        base_url : str
            The base URL for the API endpoint.
        parameters : dict
            Query parameters to include in the request.
        headers : dict
            HTTP headers to include in the request.
        response_dtype : str, optional
            The expected data type of the response.
        """

        self.base_url = base_url
        self.parameters = parameters
        self.headers = headers
        self.response_dtype = response_dtype

    def load_data(self) -> DataFrame:
        """
        Load the data from the API endpoint and return as a DataFrame.
        
        Returns
        -------
        DataFrame
            The data from the API endpoint.
        """

        # Make the API request.
        response = requests.get(
            self.base_url, params=self.parameters, headers=self.headers
        )
        response.raise_for_status()

        # Parse the response as JSON.
        data = response.json()

        # Convert to DataFrame if the response contains a 'data' key.
        if isinstance(data, dict) and 'data' in data:
            df = DataFrame(data['data'])
        else:
            df = DataFrame(data)

        return df