from pathlib import Path

import pandas as pd
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

    def _get_subfolders(self) -> list:
        """
        Get the names of all subfolders in the catalog path.

        :return: A list of subfolder names.
        """
        return [subfolder.name for subfolder in self.path_models.iterdir() if subfolder.is_dir()]


    def _create_catalog_graph(self) -> Graph:
        """Create a single RDFLib graph by merging all graphs from the models."""
        catalog_graph = Graph()

        for model in self.models:
            if model.graph:
                catalog_graph += model.graph

        return catalog_graph

    def _generate_compiled_results(self, query_name: str, results: list[dict], compiled_file_path: Path):
        """Generate a compiled CSV file from results of all models."""
        if results:
            # Convert to DataFrame
            df = pd.DataFrame(results)
            # Ensure 'model_id' is the first column
            cols = ['model_id'] + [col for col in df.columns if col != 'model_id']
            df = df[cols]
            # Save as CSV
            df.to_csv(compiled_file_path, index=False)
            logger.info(f"Compiled results written to {compiled_file_path}")

    def _save_hash_file(self, results_path: Path, query: Query, model: Model):
        """Save the hash of the query and the model to a file."""
        hash_file = results_path / f".{query.query_file.stem}_{model.id}"
        with open(hash_file, 'w', encoding='utf-8') as file:
            file.write(f"{query.hash}\n{model.hash}")
        logger.info(f"Hash written to {hash_file}")

    def execute_query_all_models(self, specific_query_path: Path):
        """Execute a specific query on all models and generate a compiled results CSV."""
        query = Query(specific_query_path)
        results_path = specific_query_path.parent / 'results'
        results_path.mkdir(exist_ok=True)
        compiled_file_path = results_path / f"{specific_query_path.stem}_result_compiled.csv"
        results = []

        for model in self.models:
            model_results = model.execute_query(query.query_file)
            for result in model_results:
                result['model_id'] = model.id
            results.extend(model_results)

            # Save individual model results
            model_result_file = results_path / f"{specific_query_path.stem}_result_{model.id}.csv"
            if model_results:
                df = pd.DataFrame(model_results)
                df.to_csv(model_result_file, index=False)
                logger.info(f"Results for model {model.id} written to {model_result_file}")

            # Save the query and model hash
            self._save_hash_file(results_path, query, model)

        # Generate compiled results
        self._generate_compiled_results(specific_query_path.stem, results, compiled_file_path)

    def execute_all_queries_all_models(self, queries_folder: Path):
        """Execute all queries in a folder on all models and generate compiled results CSVs."""
        queries = Query.get_all_queries(queries_folder)

        for query in queries:
            self.execute_query_all_models(query.query_file)