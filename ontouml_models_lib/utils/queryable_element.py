import csv
import hashlib
from pathlib import Path
from typing import Optional, Union

from loguru import logger
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri
from query import Query


class QueryableElement:
    def __init__(self, id: str):
        self.id = id
        self.model_graph = Graph()
        self.model_graph_hash = self._compute_hash()

    # ---------------------------------------------
    # Public Methods
    # ---------------------------------------------

    def execute_query(self, query: Query, results_path: Optional[Union[str, Path]] = None) -> list[dict]:
        """Execute a SPARQL query_content on the element's model_graph and return results as a list of dictionaries.

        :param query: A Query instance containing the SPARQL query_content to be executed.
        :param results_path: Path to the directory to save the results and model_graph_hash file.
        :return: List of query_content results as dictionaries.
        """

        # Ensure results_path is not None
        results_path = Path(results_path or "./results")
        results_path.mkdir(exist_ok=True)

        # Compute the model_graph_hash for the query_content
        query_hash = self._compute_query_hash(query.query_content)

        # Check if the model_graph_hash combination already exists
        if self._hash_exists(query_hash, results_path):
            logger.info(
                f"Skipping execution of query with pair model_graph_hash/query_hash: {query_hash}/{self.model_graph_hash}."
            )
            return []

        # Log the query_content
        logger.info(f"Executing query_content: {query.query_file_path}")

        # Execute the query_content on the model_graph
        try:
            results = self.model_graph.query(query.query_content)
            logger.info(f"Query results: {results}")

            # Prepare results as a list of dictionaries
            result_list = []
            for result in results:
                result_dict = {}
                for var in result.labels:
                    value = str(result[var])
                    if isinstance(result[var], URIRef):
                        _, local_name = split_uri(result[var])
                        result_dict[str(var)] = local_name
                    else:
                        result_dict[str(var)] = value
                result_list.append(result_dict)

            # Save the results and the model_graph_hash
            self._save_results(query.query_file_path.stem, result_list, results_path)
            self._save_hash_file(query_hash, results_path)

            return result_list

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []

    def execute_queries(self, queries: list[Query], results_path: Optional[Path]) -> None:
        """Execute a list of Query instances and save the results.

        :param queries: List of Query instances to be executed.
        :param results_path: Optional; Path to the directory to save the results.
        """
        # Ensure the results_path is set, or use a default location
        results_path = results_path or Path("./results")
        results_path.mkdir(exist_ok=True)

        for query in queries:
            self.execute_query(query, results_path)

    # ---------------------------------------------
    # Private Methods
    # ---------------------------------------------

    def _compute_hash(self) -> int:
        """Compute a model_graph_hash for the QueryableElement."""
        return hash(self.id)

    def _compute_query_hash(self, query: str) -> int:
        """Compute a consistent model_graph_hash for the query_content content."""
        encoded_content = query.encode("utf-8")
        content_hash = hashlib.sha256(encoded_content).hexdigest()
        return int(content_hash, 16)

    def _hash_exists(self, query_hash: int, results_path: Path) -> bool:
        """Check if the model_graph_hash combination already exists in the .hashes.csv file."""
        hashes_file = results_path / ".hashes.csv"

        if not hashes_file.exists():
            return False

        with open(hashes_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["query_hash"]) == query_hash and int(row["model_hash"]) == self.model_graph_hash:
                    return True

        return False

    def _save_results(self, query_name: str, results: list[dict], results_path: Path):
        """Save the query_content results to a CSV file."""
        result_file = results_path / f"{query_name}_result_{self.id}.csv"
        with open(result_file, "w", newline="", encoding="utf-8") as file:
            if results:
                header = results[0].keys()
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(results)
            else:
                file.write("")  # Create an empty file if there are no results

        logger.info(f"Results written to {result_file}")

    def _save_hash_file(self, query_hash: int, results_path: Path):
        """Save the model_graph_hash of the query_content and the model to a single .hashes.csv file."""
        hashes_file = results_path / ".hashes.csv"
        row = {"query_hash": query_hash, "model_hash": self.model_graph_hash}

        if not hashes_file.exists():
            with open(hashes_file, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=row.keys())
                writer.writeheader()
                writer.writerow(row)
        else:
            with open(hashes_file, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=row.keys())
                writer.writerow(row)

        logger.info(f"Hash written to {hashes_file}")
