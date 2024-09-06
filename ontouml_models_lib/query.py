"""
The `query` module provides the `Query` class, designed to handle the loading, representation, and hashing of SPARQL \
queries for execution within the OntoUML/UFO catalog.

This module ensures that SPARQL queries are consistently managed,
enabling reliable query execution across RDF graphs representing ontology models.

Overview
--------
The `Query` class encapsulates SPARQL queries, providing methods to load queries from files, compute persistent hashes
to ensure the uniqueness and reusability of query results, and facilitate query execution across RDF graphs. This class
is crucial for managing the integrity and consistency of queries used within the catalog.

Usage
-----
Example 1: Loading a Query from a File

    >>> from ontouml_models_lib import Query
    >>> query = Query('/path/to/query.sparql')
    >>> print(query.query_content)
    # Output: "SELECT ?s WHERE { ?s ?p ?o }"

Example 2: Computing the Hash of a Query

    >>> from ontouml_models_lib import Query
    >>> query = Query('/path/to/query.sparql')
    >>> print(query.hash)
    # Output: 12345678901234567890 (example hash value)

Dependencies
------------
- **hashlib**: For computing hashes of the SPARQL queries.
- **pathlib**: For handling file paths in a platform-independent manner.

References
----------
For additional details on the OntoUML/UFO catalog, refer to the official OntoUML repository:
https://github.com/OntoUML/ontouml-models
"""
import csv
import hashlib
from pathlib import Path
from typing import Union, Optional

from loguru import logger


class Query:
    """
    Represents a SPARQL query for execution within the OntoUML/UFO catalog.

    The `Query` class encapsulates a SPARQL query, providing methods for loading the query from a file, computing a
    persistent hash for the query content, and managing multiple queries through batch loading. This class ensures that
    queries are handled consistently, facilitating their reuse and reliable execution across RDF graphs representing
    ontology models.

    :ivar query_file_path: The path to the file from which the SPARQL query was loaded.
    :vartype query_file_path: Path
    :ivar query_content: The content of the SPARQL query as a string.
    :vartype query_content: str
    :ivar hash: A persistent hash value computed from the query content, used to ensure consistent result management.
    :vartype hash: int

    **Example**::

        >>> from ontouml_models_lib import Query
        >>> query = Query('/path/to/query.sparql')
        >>> print(query.query_content)
        # Output: "SELECT ?s WHERE { ?s ?p ?o }"
    """

    def __init__(self, query_file: Union[str, Path]):
        """
        Initialize a new instance of the `Query` class by loading a SPARQL query from the specified file.

        This constructor reads the content of a SPARQL query from a file, computes a persistent hash of the query
        content, and stores both the query content and the hash as attributes of the `Query` instance.
        The hash is used to manage query results consistently, preventing redundant executions of the same query.

        :param query_file: The path to the file containing the SPARQL query.
                           This can be provided as a string or a Path object.
        :type query_file: Union[str, Path]
        :raises FileNotFoundError: If the specified query file does not exist.
        :raises OSError: If an error occurs while reading the query file.

        **Example**::

            >>> from ontouml_models_lib import Query
            >>> query = Query('/path/to/query.sparql')
            >>> print(query.query_content)
            # Output: "SELECT ?s WHERE { ?s ?p ?o }"
        """
        query_file = Path(query_file) if isinstance(query_file, str) else query_file
        self.query_file_path: Path = query_file
        self.name: str = self.query_file_path.stem  # Extract the name from the file path without the extension
        self.query_content: str = self._read_query_file(query_file)
        self.hash: int = self._compute_persistent_hash(self.query_content)

    # ---------------------------------------------
    # Public Static Methods
    # ---------------------------------------------

    @staticmethod
    def load_queries(queries_path: Union[str, Path]) -> list["Query"]:
        """
        Load all query_content files from the specified directory catalog_path and return a list of Query instances.

        :param queries_path: Path to the directory containing query_content files.
        :type queries_path: Path
        :return: List of Query instances.
        :rtype: list[Query]
        """
        # Converting to catalog_path if it is a string
        queries_path = Path(queries_path) if isinstance(queries_path, str) else queries_path

        if not queries_path.is_dir():
            raise FileNotFoundError(f"Directory {queries_path} not found.")

        query_files = [file for file in queries_path.iterdir() if file.is_file()]
        return [Query(query_file) for query_file in query_files]


    def execute_on_models(
        self,
        models: list["Model"],
        results_path: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Execute the query on a list of models and consolidate the results into a single file.

        This method executes the query across multiple ontology models and saves all results
        into a single consolidated file.

        :param models: A list of Model instances on which the query will be executed.
        :type models: list[Model]
        :param results_path: Optional; Path to the directory where the query results should be saved.
                             If not provided, defaults to "./results".
        :type results_path: Optional[Union[str, Path]]

        :raises Exception: For any errors that occur during query execution.
        """
        # Import Model here to avoid circular dependency
        from .model import Model

        results_path = Path(results_path or "./results")
        results_path.mkdir(exist_ok=True)

        # Consolidate results from all models
        consolidated_results = []
        for model in models:
            # Execute query on the model without saving individual results
            result = model.execute_query(self, save_results=False)

            # Add model's ID to each result
            for res in result:
                res_with_model_id = {'model_id': model.id}  # Add model's ID as the first column
                res_with_model_id.update(res)  # Combine with the rest of the result
                consolidated_results.append(res_with_model_id)

        # Use the _save_results method to save consolidated results
        self._save_results(consolidated_results, results_path, suffix='consolidated')

    def _save_results(self, results: list[dict], results_path: Path, suffix: str = "") -> None:
        """
        Save the results to a file.

        This method is responsible for saving the results of the query execution to a file.

        :param results: The results to save.
        :type results: list[dict]
        :param results_path: The path to save the results file.
        :type results_path: Path
        :param suffix: An optional suffix for the filename to distinguish different types of results.
        :type suffix: str
        """
        if not results:
            return  # No results to save

        # Construct the filename based on the query's file name and the optional suffix
        file_name = f"{self.query_file_path.stem}_{suffix}.csv"
        file_path = results_path / file_name

        # Write results to CSV using the csv.DictWriter
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        logger.success(f"Results of {self.name} saved to {file_path}")

    # ---------------------------------------------
    # Private Methods
    # ---------------------------------------------

    @staticmethod
    def _read_query_file(query_file: Path) -> str:
        """
        Read the content of a SPARQL query file.

        This method opens a SPARQL query file, reads its content, and returns it as a string. The file is read using
        UTF-8 encoding to ensure compatibility with a wide range of characters.

        :param query_file: The path to the SPARQL query file.
        :type query_file: Path
        :return: The content of the SPARQL query file as a string.
        :rtype: str
        :raises FileNotFoundError: If the specified query file does not exist.
        :raises OSError: If an error occurs while reading the query file.
        """
        with open(query_file, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def _compute_persistent_hash(content: str) -> int:
        """
        Compute a persistent hash value for the content of a SPARQL query.

        This method generates a SHA-256 hash from the content of a SPARQL query string. The hash is computed in a way
        that ensures consistency across executions, facilitating the identification and management of query results.

        :param content: The content of the SPARQL query to be hashed.
        :type content: str
        :return: The computed hash value for the query content.
        :rtype: int
        """
        # Encode the content to UTF-8
        encoded_content = content.encode("utf-8")

        # Compute the SHA-256 model_graph_hash of the encoded content
        content_hash = hashlib.sha256(encoded_content).hexdigest()

        # Convert the hexadecimal model_graph_hash to an integer
        return int(content_hash, 16)
