from pathlib import Path

from loguru import logger
from rdflib import Graph

from model import Model
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
