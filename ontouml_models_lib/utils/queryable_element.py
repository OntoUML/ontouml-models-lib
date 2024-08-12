"""
The `queryable_element` module provides the `QueryableElement` class, a base class designed to represent elements within
the OntoUML/UFO catalog that can be queried using SPARQL. This module facilitates the execution of SPARQL queries on RDF
graphs, manages query results, and ensures consistent hashing of both queries and graph data.

Overview
--------
The `QueryableElement` class serves as a foundational class for elements that interact with RDF graphs in the
OntoUML/UFO catalog. It provides methods for executing SPARQL queries on these graphs, computing and checking hashes
to prevent redundant query executions, and managing the storage of query results. This class is crucial for ensuring
the integrity, consistency, and reusability of queries within the catalog.

Dependencies
------------
- **rdflib**: For RDF graph operations and SPARQL query execution.
- **hashlib**: For computing hashes of RDF graphs and SPARQL queries.
- **pathlib**: For handling file paths in a platform-independent manner.
- **csv**: For managing the storage of query results in CSV format.
- **loguru**: For logging operations and debugging information.

References
----------
For additional details on the OntoUML/UFO catalog, refer to the official OntoUML repository:
https://github.com/OntoUML/ontouml-models
"""
import csv
import hashlib
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Optional, Union

from loguru import logger
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri
from query import Query


class QueryableElement(ABC):
    """
    A base class representing an element in the OntoUML/UFO catalog that can be queried using SPARQL.

    The `QueryableElement` class provides foundational functionality for executing SPARQL queries on RDF graphs,
    computing consistent hashes for both the RDF graphs and queries, and managing the storage of query results.
    It is designed to be extended by other classes, such as `Catalog` and `Model`, and should not be instantiated
    directly by users.

    This class is intended for internal use and should be accessed indirectly through the `Catalog` or `Model` classes.

    Attributes
    ----------
    :ivar id: The unique identifier for the `QueryableElement`.
    :vartype id: str
    :ivar model_graph: The RDF graph associated with the `QueryableElement`.
    :vartype model_graph: Graph
    :ivar model_graph_hash: A persistent hash value computed from the RDF graph, used to ensure consistency and
                            integrity of the graph's content.
    :vartype model_graph_hash: int
    """
    def __init__(self, id: str):
        """
        Initializes a new instance of the `QueryableElement` class.

        This constructor sets up the basic attributes for the `QueryableElement`, including a unique identifier (`id`)
        and an RDF graph (`model_graph`). It also computes and stores a persistent hash (`model_graph_hash`) for the
        RDF graph, which is used to ensure the consistency and integrity of the graph's content. This class is
        intended to be extended by other classes, such as `Catalog` and `Model`, and should not be instantiated
        directly by users.

        :param id: A unique identifier for the `QueryableElement`, typically representing the name or ID of the
                   associated RDF graph.
        :type id: str
        """
        self.id: str = id
        self.model_graph: Graph = Graph()
        self.model_graph_hash: int = self._compute_hash()

    # ---------------------------------------------
    # Public Methods
    # ---------------------------------------------

    def execute_query(self, query: Query, results_path: Optional[Union[str, Path]] = None) -> list[dict]:
        """
        Executes a SPARQL query on the element's RDF graph and returns the results as a list of dictionaries.

        This method executes a SPARQL query on the `model_graph` associated with the `QueryableElement`. It first
        checks whether the combination of the graph's hash and the query's hash has already been executed, in which
        case it skips execution to prevent redundancy. If the query is executed, the results are saved to a CSV file,
        and the hash combination is recorded for future reference.

        :param query: A `Query` instance containing the SPARQL query to be executed.
        :type query: Query
        :param results_path: The path to the directory where the query results and hash file will be saved.
                             If not provided, defaults to `./results`.
        :type results_path: Optional[Union[str, Path]]
        :return: A list of dictionaries, where each dictionary represents a result row from the SPARQL query.
        :rtype: list[dict]

        Example usage:

            >>> from model import Model
            >>> from query import Query
            >>> model = Model('/path/to/ontology_model_folder')
            >>> query = Query('/path/to/query.sparql')
            >>> results = model.execute_query(query, '/path/to/results')
            >>> print(results)
            # Output: [{'subject': 'ExampleSubject', 'predicate': 'ExamplePredicate', 'object': 'ExampleObject'}]
        """
        # Ensure results_path is not None
        results_path = Path(results_path or "./results")
        results_path.mkdir(exist_ok=True)

        # Compute the model_graph_hash for the query_content
        query_hash = self._compute_query_hash(query.query_content)

        # Check if the model_graph_hash combination already exists
        if self._hash_exists(query_hash, results_path):
            logger.info(
                f"Skipping execution of query with pair model_graph_hash/query_hash: "
                f"{query_hash}/{self.model_graph_hash}."
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

    def execute_queries(self, queries: list[Query], results_path: Optional[Union[str, Path]] = None) -> None:
        """
        Executes a list of SPARQL queries on the element's RDF graph and saves the results.

        This method iterates over a list of `Query` instances, executing each query on the `model_graph` associated
        with the `QueryableElement`. The results of each query are saved to a CSV file in the specified directory.
        This method is useful for batch processing multiple SPARQL queries on a single RDF graph.

        :param queries: A list of `Query` instances to be executed on the `model_graph`.
        :type queries: list[Query]
        :param results_path: The path to the directory where the query results will be saved. If not provided,
                             defaults to `./results`.
        :type results_path: Optional[Path]

        Example usage:

            >>> from model import Model
            >>> from query import Query
            >>> model = Model('/path/to/ontology_model_folder')
            >>> queries = [Query('/path/to/query1.sparql'), Query('/path/to/query2.sparql')]
            >>> model.execute_queries(queries, '/path/to/results')
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