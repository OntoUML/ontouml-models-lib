"""
The `catalog` module provides the `Catalog` class, designed to manage and query collections of ontology models within \
the OntoUML/UFO Catalog.

This module facilitates the loading, querying, and compilation of results from multiple
ontology models, leveraging RDFLib for RDF graph operations and SPARQL queries.

Overview
--------
The `Catalog` class is a specialized manager for handling a set of ontology models, each stored in its subdirectory
within a specified catalog path. Each subdirectory is expected to contain an ontology file (`ontology.ttl`) and an
optional metadata file (`metadata.yaml`). The class supports complex queries across the entire collection by compiling
results from individual models into a cohesive dataset.

Usage
-----
To use the `Catalog` class, instantiate it with the path to the catalog directory. The class will automatically load
all ontology models from their respective subdirectories. Users can then perform SPARQL queries across the catalog,
either on individual models or across the entire collection.

Examples
--------
Example 1: Loading a Catalog and Executing a Single Query on All Models

    >>> from catalog import Catalog
    >>> from query import Query

    >>> # Initialize the catalog with the path to the directory
    >>> catalog = Catalog('/path/to/catalog')

    >>> # Load a specific query from a file
    >>> query = Query('./queries/query1.sparql')

    >>> # Execute the query on all models in the catalog
    >>> catalog.execute_query_on_all_models(query)

Example 2: Filtering Models by Attributes and Executing Multiple Queries

    >>> from catalog import Catalog
    >>> from query import Query

    >>> # Initialize the catalog
    >>> catalog = Catalog('/path/to/catalog')

    >>> # Filter models that have the keyword 'ontology' or are in English language
    >>> filtered_models = catalog.get_models(language="en")

    >>> # Load multiple queries from a directory
    >>> queries = Query.load_queries('./queries')

    >>> # Execute the queries on the filtered models
    >>> catalog.execute_queries_on_models(queries, filtered_models)

Example 3: Executing Multiple Queries on a Specific Model

    >>> from catalog import Catalog
    >>> from query import Query

    >>> # Initialize the catalog
    >>> catalog = Catalog('/path/to/catalog')

    >>> # Get a specific model by ID
    >>> model = catalog.get_model('some_model_id')

    >>> # Load multiple queries from a directory
    >>> queries = Query.load_queries('./queries')

    >>> # Execute the queries on the specific model
    >>> catalog.execute_queries_on_model(queries, model)

Dependencies
------------
- **rdflib**: For RDF graph operations and SPARQL query execution.
- **loguru**: For logging operations and debugging information.
- **pandas**: For compiling and managing query results in tabular format.

References
----------
For additional details on the OntoUML/UFO catalog, refer to the official OntoUML repository:
https://github.com/OntoUML/ontouml-models
"""

from typing import Optional, Any, Union

import pandas as pd
from pathlib import Path

from loguru import logger
from rdflib import Graph
from model import Model
from query import Query
from utils.queryable_element import QueryableElement


class Catalog(QueryableElement):
    """
    Manages a collection of ontology models in the OntoUML/UFO Catalog.

    The `Catalog` class allows loading, managing, and executing queries on multiple ontology models. It compiles the
    results from individual models into a cohesive dataset, enabling complex queries across the entire catalog. This
    class inherits from `QueryableElement`, which provides functionality to execute SPARQL queries using RDFLib.

    :ivar path: The path to the catalog directory.
    :vartype path: str
    :ivar path_models: The path to the directory containing the ontology model subfolders.
    :vartype path_models: str
    :ivar models: A list of `Model` instances representing the loaded ontology models.
    :vartype models: list[Model]
    :ivar graph: An RDFLib `Graph` object representing the merged graph of all ontology models.
    :vartype graph: rdflib.Graph

    Examples
    --------
    Basic usage example of the `Catalog` class:

        >>> from catalog import Catalog
        >>> from query import Query

        >>> # Initialize the catalog with the path to the directory
        >>> catalog = Catalog('/path/to/catalog')

        >>> # Load a specific query from a file
        >>> query = Query('./queries/query.sparql')

        >>> # Execute the query on all models in the catalog
        >>> catalog.execute_query_on_all_models(query)

        >>> # Execute multiple queries on all models in the catalog
        >>> queries = Query.load_queries('./queries')
        >>> catalog.execute_queries_on_all_models(queries)

        >>> # Execute multiple queries on a specific model
        >>> model = catalog.get_model('some_model_id')
        >>> catalog.execute_queries_on_model(queries, model)
    """

    def __init__(self, catalog_path: Union[Path, str]) -> None:  # noqa: DOC101,DOC103
        """
        Initialize the Catalog with a given path to the ontology models.

        This method sets up the catalog by specifying the directory containing the ontology models. It initializes the
        paths, loads all models from the directory, and creates a merged RDF graph of all models.

        :param catalog_path: The path to the catalog directory containing the ontology models.
                             The path can be provided as a string or a Path object.
        :type catalog_path: Union[Path, str]

        :raises ValueError: If the provided path is not valid or if the directory does not contain any models.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        """
        # Converting to catalog_path if it is a string
        catalog_path = Path(catalog_path) if isinstance(catalog_path, str) else catalog_path

        super().__init__(id="catalog")  # Set the id to "catalog"

        self.path: Path = catalog_path
        self.path_models: Path = self.path / "models"
        self.models: list[Model] = []
        self._load_models()
        self.graph: Graph = self._create_catalog_graph()

    # ---------------------------------------------
    # Public Methods
    # ---------------------------------------------

    # ----- EXECUTE METHODS -----

    def execute_query_on_model(
        self, query: Query, model: Model, results_path: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Execute a specific Query on a specific Model and save the results.

        This method runs a single SPARQL query on a specific ontology model and saves the results to the specified
        directory. If no directory is provided, the results are saved in the default "./results" directory.

        :param query: A Query instance representing the SPARQL query to be executed.
        :type query: Query
        :param model: A Model instance on which the query will be executed.
        :type model: Model
        :param results_path: Optional; Path to the directory where the query results should be saved. If not provided,
                             defaults to "./results".
        :type results_path: Optional[Union[str, Path]]

        :raises FileNotFoundError: If the provided results path does not exist and cannot be created.
        :raises Exception: For any other errors that occur during query execution.

        Example usage:

        >>> from catalog import Catalog
        >>> from query import Query
        >>> catalog = Catalog('/path/to/catalog')
        >>> query = Query('./queries/query.sparql')  # Load a SPARQL query from a file
        >>> model = catalog.get_model('some_model_id')  # Retrieve a model by its ID
        >>> catalog.execute_query_on_model(query, model)
        """
        results_path = results_path or Path("./results")
        results_path.mkdir(exist_ok=True)
        model.execute_query(query, results_path)

    def execute_query_on_all_models(self, query: Query, results_path: Optional[Union[str, Path]] = None) -> None:
        """
        Execute a single Query instance on all loaded Model instances in the catalog and save the results.

        This method runs a single SPARQL query across all ontology models loaded in the catalog. The results are saved
        in the specified directory, or in the default "./results" directory if no directory is provided.

        :param query: A Query instance representing the SPARQL query to be executed on all models.
        :type query: Query
        :param results_path: Optional; Path to the directory where the query results should be saved. If not provided,
                             defaults to "./results".
        :type results_path: Optional[Union[str, Path]]

        :raises FileNotFoundError: If the provided results path does not exist and cannot be created.
        :raises Exception: For any other errors that occur during query execution.

        Example usage:

        >>> from catalog import Catalog
        >>> from query import Query
        >>> catalog = Catalog('/path/to/catalog')
        >>> query = Query('./queries/query.sparql')  # Load a SPARQL query from a file
        >>> catalog.execute_query_on_all_models(query)  # Execute the query on all models
        """
        # Ensure results_path is not None
        results_path = Path(results_path or "./results")
        results_path.mkdir(exist_ok=True)

        # Execute the query on each model in the catalog
        for model in self.models:
            model.execute_query(query, results_path)

    def execute_queries_on_model(
        self, queries: list[Query], model: Model, results_path: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Execute a list of Query instances on a specific Model instance and save the results.

        This method runs multiple SPARQL queries on a specific ontology model. The results of each query are saved in
        the specified directory, or in the default "./results" directory if no directory is provided.

        :param queries: A list of Query instances to be executed on the model.
        :type queries: list[Query]
        :param model: A Model instance on which the queries will be executed.
        :type model: Model
        :param results_path: Optional; Path to the directory where the query results should be saved. If not provided,
                             defaults to "./results".
        :type results_path: Optional[Union[str, Path]]

        :raises FileNotFoundError: If the provided results path does not exist and cannot be created.
        :raises Exception: For any other errors that occur during query execution.

        Example usage:

        >>> from catalog import Catalog
        >>> from query import Query
        >>> catalog = Catalog('/path/to/catalog')
        >>> model = catalog.get_model('some_model_id')  # Retrieve a model by its ID
        >>> queries = Query.load_queries('./queries')  # Load multiple SPARQL queries from a directory
        >>> catalog.execute_queries_on_model(queries, model)
        """
        # Ensure results_path is not None
        results_path = Path(results_path or "./results")
        results_path.mkdir(exist_ok=True)

        # Execute each query on the specified model
        for query in queries:
            model.execute_query(query, results_path)

    def execute_queries_on_models(
        self, queries: list[Query], models: list[Model], results_path: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Execute a list of Query instances on a list of Model instances and save the results.

        This method runs multiple SPARQL queries across a specified set of ontology models in the catalog. The results
        of each query on each model are saved in the specified directory, or in the default "./results" directory if no
        directory is provided.

        :param queries: A list of Query instances to be executed on the models.
        :type queries: list[Query]
        :param models: A list of Model instances on which the queries will be executed.
        :type models: list[Model]
        :param results_path: Optional; Path to the directory where the query results should be saved. If not provided,
                             defaults to "./results".
        :type results_path: Optional[Union[str, Path]]

        :raises FileNotFoundError: If the provided results path does not exist and cannot be created.
        :raises Exception: For any other errors that occur during query execution.

        Example usage:

        >>> from catalog import Catalog
        >>> from query import Query
        >>> catalog = Catalog('/path/to/catalog')
        >>> models = catalog.get_models(language="en")  # Filter models by language
        >>> queries = Query.load_queries('./queries')  # Load multiple SPARQL queries from a directory
        >>> catalog.execute_queries_on_models(queries, models)
        """
        results_path = results_path or Path("./results")
        results_path.mkdir(exist_ok=True)
        for model in models:
            for query in queries:
                model.execute_query(query, results_path)

    def execute_queries_on_all_models(
        self, queries: list[Query], results_path: Optional[Union[str, Path]] = None
    ) -> None:
        """
        Execute a list of Query instances on all loaded Model instances in the catalog and save the results.

        This method runs multiple SPARQL queries across all ontology models loaded in the catalog. The results of each
        query on each model are saved in the specified directory, or in the default "./results" directory if no
        directory is provided.

        :param queries: A list of Query instances to be executed on all models.
        :type queries: list[Query]
        :param results_path: Optional; Path to the directory where the query results should be saved. If not provided,
                             defaults to "./results".
        :type results_path: Optional[Union[str, Path]]

        :raises FileNotFoundError: If the provided results path does not exist and cannot be created.
        :raises Exception: For any other errors that occur during query execution.

        Example usage:

        >>> from catalog import Catalog
        >>> from query import Query
        >>> catalog = Catalog('/path/to/catalog')
        >>> queries = Query.load_queries('./queries')  # Load multiple SPARQL queries from a directory
        >>> catalog.execute_queries_on_all_models(queries)  # Execute the queries on all models
        """
        self.execute_queries_on_models(queries, self.models, results_path)

    # ----- GET METHODS -----

    def get_model(self, model_id: str) -> Model:
        """
        Retrieve a model from the catalog by its ID.

        This method searches for a model within the catalog's loaded models by its unique ID. If a model with the
        specified ID is found, it is returned. Otherwise, a `ValueError` is raised.

        :param model_id: The ID of the model to retrieve.
        :type model_id: str
        :return: The model with the specified ID.
        :rtype: Model
        :raises ValueError: If no model with the specified ID is found.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        >>> model = catalog.get_model('some_model_id')  # Retrieve a model by its unique ID
        """
        for model in self.models:
            if model.id == model_id:
                return model
        raise ValueError(f"No model found with ID: {model_id}")

    def get_models(self, operand: str = "and", **filters: dict[str, Any]) -> list[Model]:
        """
        Return a list of models that match the given attribute restrictions.

        This method filters the loaded models based on specified attribute restrictions. It supports logical operations
        ("and" or "or") to combine multiple filters. If only a single filter is provided, the operand is ignored.

        :param operand: Logical operand for combining filters ("and" or "or"). Defaults to "and".
        :type operand: str
        :param filters: Attribute restrictions to filter models. Attribute names and values should be passed as keyword
                        arguments. Multiple values for the same attribute can be provided as a list.
        :type filters: dict[str, Any]
        :return: List of models that match the restrictions.
        :rtype: list[Model]
        :raises ValueError: If an invalid operand is provided.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        >>> # Filter models by a single attribute (language)
        >>> filtered_models = catalog.get_models(language="en")
        >>> # Filter models by multiple keywords
        >>> filtered_models = catalog.get_models(operand="or", keyword=["safety", "geology"])
        >>> # Filter models by multiple attributes (keyword and language)
        >>> filtered_models = catalog.get_models(operand="and", keyword="safety", language="en")
        """
        if len(filters) == 1:
            attr, value = next(iter(filters.items()))
            return [model for model in self.models if self._match_single_filter(model, attr, value)]

        return [model for model in self.models if self._match_model(model, filters, operand)]

    # ----- REMOVE METHODS -----

    def remove_model_by_id(self, model_id: str) -> None:
        """
        Remove a model from the catalog by its ID.

        This method searches for a model within the catalog's loaded models by its unique ID. If a model with the
        specified ID is found, it is removed from the catalog. Otherwise, a `ValueError` is raised.

        :param model_id: The ID of the model to remove.
        :type model_id: str
        :raises ValueError: If no model with the specified ID is found.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        >>> catalog.remove_model_by_id('some_model_id')  # Remove a model by its unique ID
        """
        for i, model in enumerate(self.models):
            if model.id == model_id:
                del self.models[i]
                logger.info(f"Model with ID {model_id} has been removed from the catalog.")
                return
        raise ValueError(f"No model found with ID: {model_id}")

    # ---------------------------------------------
    # Private Methods
    # ---------------------------------------------

    def _load_models(self) -> None:
        """
        Load all ontology models from the specified directory.

        This method is called internally by the initializer to scan the catalog directory for subfolders, each
        representing an ontology model. It loads the models from these subfolders and initializes them as instances of
        the `Model` class. The loaded models are stored in the `models` attribute.

        :raises FileNotFoundError: If the catalog path does not contain any model subfolders.
        """
        list_models_folders = self._get_subfolders()
        list_models_folders = list_models_folders[0:5]
        logger.info("Loading catalog from catalog_path: {}", self.path_models)

        for model_folder in list_models_folders:
            model_path = self.path_models / model_folder
            model = Model(model_path)
            self.models.append(model)

    def _get_subfolders(self) -> list:
        """Get the names of all subfolders in the catalog catalog_path."""
        return [subfolder.name for subfolder in self.path_models.iterdir() if subfolder.is_dir()]

    def _create_catalog_graph(self) -> Graph:
        """Create a single RDFLib model_graph by merging all graphs from the models."""
        catalog_graph = Graph()
        for model in self.models:
            if model.model_graph:
                catalog_graph += model.model_graph
        return catalog_graph

    def _generate_compiled_results(self, results: list[dict], compiled_file_path: Path):
        """Generate a compiled CSV file from results of all models."""
        if results:
            df = pd.DataFrame(results)
            cols = ["model_id"] + [col for col in df.columns if col != "model_id"]
            df = df[cols]
            df.to_csv(compiled_file_path, index=False)
            logger.info(f"Compiled results written to {compiled_file_path}")

    def _match_model(self, model: Model, filters: dict[str, Any], operand: str) -> bool:
        """
        Check if a model matches the given attribute restrictions.

        :param model: The model to check.
        :type model: Model
        :param filters: Attribute restrictions to filter models.
        :type filters: dict
        :param operand: Logical operand for combining filters ("and" or "or").
        :type operand: str
        :return: True if the model matches the restrictions, False otherwise.
        :rtype: bool
        """
        matches: list[bool] = []
        for attr, value in filters.items():
            model_value = getattr(model, attr, None)
            if isinstance(model_value, list):
                match = value in model_value
            else:
                match = model_value == value
            matches.append(match)

        if operand == "and":
            return all(matches)

        if operand == "or":
            return any(matches)

        raise ValueError("Invalid operand. Use 'and' or 'or'.")

    def _match_single_filter(self, model: Model, attr: str, value: Any) -> bool:
        """
        Check if a model matches a single attribute restriction.

        :param model: The model to check.
        :type model: Model
        :param attr: The attribute name to filter by.
        :type attr: str
        :param value: The attribute value or list of values to filter by.
        :type value: Any
        :return: True if the model matches the restriction, False otherwise.
        :rtype: bool
        """
        model_value = getattr(model, attr, None)
        if isinstance(model_value, list):
            if isinstance(value, list):
                return any(val in model_value for val in value)
            return value in model_value

        if isinstance(value, list):
            return model_value in value

        return model_value == value
