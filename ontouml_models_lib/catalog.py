"""
This module defines the `Catalog` class, representing a collection of ontology models in the OntoUML/UFO Catalog.
The `Catalog` class provides functionalities to load, manage, and execute queries on multiple ontology models,
compiling the results from individual models into a cohesive dataset.

The `Catalog` class inherits from `QueryableElement`, allowing it to execute SPARQL queries across its contained models.
This enables users to perform complex queries on the entire catalog, leveraging the RDFLib library for graph operations.

Classes:
    - Catalog: Manages a collection of ontology models, allowing loading, querying, and compiling results from them.

Usage Notes:
    The `Catalog` class assumes that the ontology models are organized in subfolders within the specified catalog path.
    Each subfolder should contain an ontology file (`ontology.ttl`) and a metadata file (`metadata.yaml`) for the model.

    The `execute_query_all_models` method executes a specific SPARQL query on all loaded models, compiling the results
    into a single CSV file. The `execute_all_queries_all_models` method executes all queries from a specified folder on
    all models, generating compiled results for each query.

    Both methods automatically handle the creation of result directories and logging of query execution progress.

Example:
    To use the `Catalog` class, create an instance by specifying the path to the catalog directory and call the
    `execute_query_all_models` or `execute_all_queries_all_models` methods with appropriate parameters.

    >>> from catalog import Catalog
    >>> catalog = Catalog('/path/to/catalog')
    >>> catalog.execute_query_on_all_models('/path/to/query.sparql')
    >>> catalog.execute_all_queries_on_all_models('/path/to/queries')

This module is part of a library designed to manipulate concepts from and perform queries in the OntoUML/UFO Catalog.
For more information about OntoUML and UFO, visit the OntoUML repository: https://github.com/OntoUML/ontouml-models
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
    :vartype path: pathlib.Path
    :ivar path_models: The path to the directory containing the ontology model subfolders.
    :vartype path_models: pathlib.Path
    :ivar models: A list of `Model` instances representing the loaded ontology models.
    :vartype models: list[Model]
    :ivar graph: An RDFLib `Graph` object representing the merged graph of all ontology models.
    :vartype graph: rdflib.Graph

    Example usage:

    >>> from catalog import Catalog
    >>> catalog = Catalog('/path/to/catalog')
    >>> catalog.execute_query_on_all_models('/path/to/query.sparql')
    >>> catalog.execute_all_queries_on_all_models('/path/to/queries')
    """
    def __init__(self, catalog_path: Union[Path, str])->None:
        """
        Initialize the Catalog with a given path to the ontology models.

        This method sets up the catalog by specifying the directory containing the ontology models. It initializes the
        paths, loads all models from the directory, and creates a merged graph of all models.

        :param catalog_path: The path to the catalog directory containing the ontology models.
        :type catalog_path: Union[pathlib.Path, str]
        :raises ValueError: If the provided path is not valid.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        """
        # Converting to catalog_path if it is a string
        catalog_path = Path(catalog_path) if isinstance(catalog_path, str) else catalog_path

        super().__init__(id="catalog")  # Set the id to "catalog"

        self.path: Path = Path(catalog_path)
        self.path_models: Path = self.path / "models"
        self.models: list[Model] = []
        self.load_all_models()
        self.graph: Graph = self._create_catalog_graph()

    # ---------------------------------------------
    # Public Methods
    # ---------------------------------------------

    def load_all_models(self):
        """
        Load all ontology models from the specified directory.

        This method scans the catalog directory for subfolders, each representing an ontology model.
        It loads the models from these subfolders and initializes them as instances of the `Model` class.
        The loaded models are stored in the `models` attribute.

        :raises FileNotFoundError: If the catalog path does not contain any model subfolders.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        >>> catalog.load_all_models()
        """
        list_models_folders = self._get_subfolders()
        list_models_folders = list_models_folders[0:5]
        logger.info("Loading catalog from catalog_path: {}", self.path_models)

        for model_folder in list_models_folders:
            model_path = self.path_models / model_folder
            model = Model(model_path)
            self.models.append(model)

    def execute_query_on_all_models(self, specific_query_path: Union[Path, str], results_path: Optional[Path]):
        """
        Execute a specific SPARQL query on all models and generate a compiled results CSV.

        This method reads a SPARQL query from the specified file and executes it on all loaded ontology models.
        The results from each model are compiled into a single CSV file. If a results directory is not provided,
        it creates one in the same directory as the query file.

        :param specific_query_path: The path to the SPARQL query file.
        :type specific_query_path: Union[pathlib.Path, str]
        :param results_path: The path to the directory where results should be saved. If not provided,
                             a 'results' directory is created in the same location as the query file.
        :type results_path: Optional[pathlib.Path]

        :raises FileNotFoundError: If the query file does not exist.
        :raises ValueError: If no models are loaded.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        >>> catalog.execute_query_on_all_models('/path/to/query.sparql', '/path/to/results')
        """

        # Converting to catalog_path if it is a string
        specific_query_path = Path(specific_query_path) if isinstance(specific_query_path, str) else specific_query_path

        query = Query(specific_query_path)
        results_path = specific_query_path.parent / "results" if not results_path else results_path
        results_path.mkdir(exist_ok=True)
        compiled_file_path = results_path / f"{specific_query_path.stem}_result_compiled.csv"
        results = []

        for model in self.models:
            model_results = model.execute_query(query.query_file, results_path)
            for result in model_results:
                result["model_id"] = model.id
            results.extend(model_results)

            model_result_file = results_path / f"{specific_query_path.stem}_result_{model.id}.csv"
            if model_results:
                df = pd.DataFrame(model_results)
                df.to_csv(model_result_file, index=False)
                logger.info(f"Results for model {model.id} written to {model_result_file}")

        self._generate_compiled_results(specific_query_path.stem, results, compiled_file_path)

    def execute_all_queries_on_all_models(self, queries_folder: Union[Path, str], results_path: Optional[Path] = None):
        """
        Execute all SPARQL queries in a specified folder on all models and generate compiled results CSVs.

        This method scans a directory for SPARQL query files, executes each query on all loaded ontology models, and
        compiles the results into CSV files. If a results directory is not provided, it creates one in the same
        directory as the queries folder.

        :param queries_folder: The path to the folder containing SPARQL query files.
        :type queries_folder: Union[pathlib.Path, str]
        :param results_path: The path to the directory where results should be saved. If not provided,
                             a 'results' directory is created in the same location as the queries folder.
        :type results_path: Optional[pathlib.Path]

        :raises FileNotFoundError: If the queries folder does not exist or contains no query files.
        :raises ValueError: If no models are loaded.

        Example usage:

        >>> from catalog import Catalog
        >>> catalog = Catalog('/path/to/catalog')
        >>> catalog.execute_all_queries_on_all_models('/path/to/queries', '/path/to/results')
        """
        # Converting to catalog_path if it is a string
        queries_folder = Path(queries_folder) if isinstance(queries_folder, str) else queries_folder

        queries = Query.get_all_queries(queries_folder)
        for query in queries:
            self.execute_query_on_all_models(query.query_file, results_path)

    def get_model(self, model_id: str) -> Model:
        """Retrieve a model from the catalog by its ID.

        :param model_id: The ID of the model to retrieve.
        :type model_id: str
        :return: The model with the specified ID.
        :rtype: Model
        :raises ValueError: If no model with the specified ID is found.

        Example:
            >>> catalog = Catalog(catalog_path='/catalog_path/to/catalog')
            >>> model = catalog.get_model_by_id('some_model_id')
        """
        for model in self.models:
            if model.id == model_id:
                return model
        raise ValueError(f"No model found with ID: {model_id}")

    def get_models(self, operand: str = "and", **filters: dict[str, Any]) -> list[Model]:
        """
        Return a list of models that match the given attribute restrictions.

        :param operand: Logical operand for combining filters ("and" or "or").
        :type operand: str
        :param filters: Attribute restrictions to filter models.
        :return: List of models that match the restrictions.
        :rtype: list[Model]
        """
        return [model for model in self.models if self._match_model(model, filters, operand)]

    def remove_model(self, model_id: str) -> None:
        """Remove a model from the catalog by its ID.

        :param model_id: The ID of the model to remove.
        :type model_id: str
        :raises ValueError: If no model with the specified ID is found.

        Example:
            >>> catalog = Catalog(catalog_path='/catalog_path/to/catalog')
            >>> catalog.remove_model('some_model_id')
        """
        for i, model in enumerate(self.models):
            if model.id == model_id:
                del self.models[i]
                logger.info(f"Model with ID {model_id} has been removed from the catalog.")
                return
        raise ValueError(f"No model found with ID: {model_id}")

    # ---------------------------------------------
    # Private and Setters
    # ---------------------------------------------

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
        elif operand == "or":
            return any(matches)
        else:
            raise ValueError("Invalid operand. Use 'and' or 'or'.")
