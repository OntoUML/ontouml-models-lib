"""
This module defines the `Catalog` class, which represents a collection of ontology models in the OntoUML/UFO Catalog.
The `Catalog` class provides functionalities to load, manage, and execute queries on multiple ontology models,
compiling the results from individual models into a cohesive dataset.

The `Catalog` class inherits from `QueryableElement`, allowing it to execute SPARQL queries across its contained models.
This enables users to perform complex queries on the entire catalog, leveraging the RDFLib library for model_graph operations.

Example usage of the `Catalog` class:

    >>> from catalog import Catalog
    >>> catalog = Catalog(path='/path/to/catalog')
    >>> catalog.execute_query_all_models(specific_query_path=Path('/path/to/query.rq'))
    >>> catalog.execute_all_queries_all_models(queries_folder=Path('/path/to/queries'))

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
    >>> catalog = Catalog(path='/path/to/catalog')
    >>> catalog.execute_query_all_models(specific_query_path=Path('/path/to/query.rq'))
    >>> catalog.execute_all_queries_all_models(queries_folder=Path('/path/to/queries'))

This module is part of a library designed to manipulate concepts from and perform queries in the OntoUML/UFO Catalog.
For more information about OntoUML and UFO, visit the OntoUML repository: https://github.com/OntoUML/ontouml-models
"""


import pandas as pd
from pathlib import Path
from loguru import logger
from rdflib import Graph
from model import Model
from query import Query
from utils.queryable_element import QueryableElement

class Catalog(QueryableElement):
    def __init__(self, path: str):
        super().__init__(id="catalog")  # Set the id to "catalog"
        self.path: Path = Path(path)
        self.path_models: Path = self.path / 'models'
        self.models: list[Model] = []
        self.load_models()
        self.graph: Graph = self._create_catalog_graph()

    # ---------------------------------------------
    # Public Methods
    # ---------------------------------------------

    def load_models(self):
        """Load data from the specified directory path."""
        list_models_folders = self._get_subfolders()
        list_models_folders = list_models_folders[0:5]
        logger.info("Loading catalog from path: {}", self.path_models)

        for model_folder in list_models_folders:
            model_path = self.path_models / model_folder
            try:
                model = Model(model_path)
                self.models.append(model)
                logger.info("Successfully loaded model from folder: {}", model_folder)
            except Exception as e:
                logger.error("Failed to load model from folder: {}. Error: {}", model_folder, e)

    def execute_query_all_models(self, specific_query_path: Path):
        """Execute a specific query on all models and generate a compiled results CSV."""
        query = Query(specific_query_path)
        results_path = specific_query_path.parent / 'results'
        results_path.mkdir(exist_ok=True)
        compiled_file_path = results_path / f"{specific_query_path.stem}_result_compiled.csv"
        results = []

        for model in self.models:
            model_results = model.execute_query(query.query_file, results_path)
            for result in model_results:
                result['model_id'] = model.id
            results.extend(model_results)

            model_result_file = results_path / f"{specific_query_path.stem}_result_{model.id}.csv"
            if model_results:
                df = pd.DataFrame(model_results)
                df.to_csv(model_result_file, index=False)
                logger.info(f"Results for model {model.id} written to {model_result_file}")

        self._generate_compiled_results(specific_query_path.stem, results, compiled_file_path)

    def execute_all_queries_all_models(self, queries_folder: Path):
        """Execute all queries in a folder on all models and generate compiled results CSVs."""
        queries = Query.get_all_queries(queries_folder)
        for query in queries:
            self.execute_query_all_models(query.query_file)

    def get_model(self, model_id: str) -> Model:
        """Retrieve a model from the catalog by its ID.

        :param model_id: The ID of the model to retrieve.
        :type model_id: str
        :return: The model with the specified ID.
        :rtype: Model
        :raises ValueError: If no model with the specified ID is found.

        Example:
            >>> catalog = Catalog(path='/path/to/catalog')
            >>> model = catalog.get_model_by_id('some_model_id')
        """
        for model in self.models:
            if model.id == model_id:
                return model
        raise ValueError(f"No model found with ID: {model_id}")

    def remove_model(self, model_id: str) -> None:
        """Remove a model from the catalog by its ID.

        :param model_id: The ID of the model to remove.
        :type model_id: str
        :raises ValueError: If no model with the specified ID is found.

        Example:
            >>> catalog = Catalog(path='/path/to/catalog')
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
        """Get the names of all subfolders in the catalog path."""
        return [subfolder.name for subfolder in self.path_models.iterdir() if subfolder.is_dir()]

    def _create_catalog_graph(self) -> Graph:
        """Create a single RDFLib model_graph by merging all graphs from the models."""
        catalog_graph = Graph()
        for model in self.models:
            if model.model_graph:
                catalog_graph += model.model_graph
        return catalog_graph

    def _generate_compiled_results(self, query_name: str, results: list[dict], compiled_file_path: Path):
        """Generate a compiled CSV file from results of all models."""
        if results:
            df = pd.DataFrame(results)
            cols = ['model_id'] + [col for col in df.columns if col != 'model_id']
            df = df[cols]
            df.to_csv(compiled_file_path, index=False)
            logger.info(f"Compiled results written to {compiled_file_path}")