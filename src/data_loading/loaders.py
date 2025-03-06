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
import json

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
        Optional keyword arguments to pass to specific retrievers

    Methods
    -------
    create(path_or_url, **kwargs)
        Create a DataRetriever object based on the extension or
        protocol.

    Examples
    --------

    .. code-block:: python

        # Create a DataRetriever object for a CSV file.
        retriever = DataRetriever.create("data.csv")

        # Load the data.
        data = retriever.load_data()

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
            Optional keyword arguments to pass to specific retrievers.

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
                
                # Create appropriate loader based on extension.
                if extsn in [".csv", ".txt", ".tsv"]:
                    return CSVLoader(path_or_url)
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
                    base_url=path_or_url, parameters=parameters,
                    headers=headers, response_dtype=response_dtype
                )

        # CASE 2: User passes a local file path, which could be a CSV,
        # Excel, YAML, or JSON file.
        extsn = os.path.splitext(path_or_url)[1]

        # CASE 2A: CSV file.
        if extsn in [".csv", ".txt", ".tsv"]:
            return CSVLoader(path_or_url)
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
        
        Parameters
        ----------
        **kwargs
            Additional keyword arguments passed to pandas.read_csv or
            pandas.DataFrame.

        Returns
        -------
        DataFrame
            The data from the CSV file.
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
        
        Parameters
        ----------
        **kwargs
            Additional keyword arguments passed to pandas.read_excel.

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

    Attributes
    ----------
    path_or_url : str
        The path or URL to the JSON file.
    is_remote : bool
        Whether the JSON file is remote.
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

    def load_data(self, data_key: str=None, **kwargs) -> DataFrame:
        """
        Load the data from the JSON file and return as a DataFrame.

        Parameters
        ----------
        data_key : str, optional
            The key in the JSON object that contains the data to load
            into the DataFrame. If None, the entire JSON object is
            loaded.
        **kwargs
            Additional keyword arguments passed to pandas.read_json or
            pandas.DataFrame.

        Returns
        -------
        DataFrame
            The data from the JSON file.
        """

        # CASE 1: The file is remote.
        if self.is_remote:

            # Download the file content.
            response = requests.get(self.path_or_url)
            response.raise_for_status()

            # CASE 1A: The user wants to load a specific key from the
            # JSON object.
            if data_key:

                # Parse the JSON object.
                data = json.loads(response.text)

                # Check if the key exists in the JSON object.
                if data_key not in data:
                    raise KeyError(
                        f"Data key '{data_key}' not found in JSON "
                        "response"
                    )

                # Load the data into a DataFrame.
                df = DataFrame(data[self.data_key], **kwargs)
            else:
                df = read_json(StringIO(response.text), **kwargs)

        # CASE 2: The file is local.
        else:

            # See if the user wants to load a specific key from the JSON
            if data_key:

                # Load the JSON object.
                with open(self.path_or_url, 'r') as f:
                    data = json.load(f)

                # Check if the key exists in the JSON object.
                if data_key not in data:
                    raise KeyError(
                        f"Data key '{data_key}' not found in JSON "
                        "response"
                    )

                # Load the data into a DataFrame.
                df = DataFrame(data[data_key], **kwargs)

            # The user wants to load the entire JSON object.
            else:
                df = read_json(self.path_or_url, **kwargs)

        return df

########################################################################
## API LOADER IMPLEMENTATION
########################################################################

class LoadAPI(BaseLoader):
    """
    Concrete implementation for reading data from an HTTP API endpoint.
    """

    def __init__(
            self, base_url: str, parameters: dict, headers: dict
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
        """

        self.base_url = base_url
        self.parameters = parameters
        self.headers = headers

    def load_data(self, data_key: str=None, **kwargs) -> DataFrame:
        """
        Load the data from the API endpoint and return as a DataFrame.

        Parameters
        ----------
        data_key : str, optional
            The key in the JSON object that contains the data to load
            into the DataFrame. If None, the entire JSON object is
            loaded.
        **kwargs
            Additional keyword arguments passed to pandas.DataFrame or
            pandas.read_json.

        Returns
        -------
        DataFrame
            The data from the API endpoint.
        """

        # Make the API request.
        response = requests.get(
            url=self.base_url, params=self.parameters, headers=self.headers
        )

        # Raise an error if the request was unsuccessful.
        response.raise_for_status()

        # Parse the response as JSON.
        data = response.json()

        # See if the user wants to load a specific key from the JSON.
        if data_key:

            # Load the JSON object.
            with open(self.path_or_url, 'r') as f:
                data = json.load(f)

            # Check if the key exists in the JSON object.
            if data_key not in data:
                raise KeyError(
                    f"Data key '{data_key}' not found in JSON "
                    "response"
                )

            # Load the data into a DataFrame.
            df = DataFrame(data[data_key], **kwargs)

        # The user wants to load the entire JSON object.
        else:
            df = read_json(self.path_or_url, **kwargs)

        return df