"""
The `queryable_element` module provides the `QueryableElement` class, a base class designed to represent elements \
within the OntoUML/UFO catalog that can be queried using SPARQL.

This module facilitates the execution of SPARQL queries on RDF graphs, manages query results,
and ensures consistent hashing of both queries and graph data.

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
from abc import ABC
from pathlib import Path
from typing import Optional, Union

from loguru import logger
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri
from ..query import Query


class QueryableElement(ABC):
    """
    A base class representing an element in the OntoUML/UFO catalog that can be queried using SPARQL.

    The `QueryableElement` class provides foundational functionality for executing SPARQL queries on RDF graphs,
    computing consistent hashes for both the RDF graphs and queries, and managing the storage of query results.
    It is designed to be extended by other classes, such as `Catalog` and `Model`, and should not be instantiated
    directly by users.

    This class is intended for internal use and should be accessed indirectly through the `Catalog` or `Model` classes.

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
        Initialize a new instance of the `QueryableElement` class.

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
        Execute a SPARQL query on the element's RDF graph and returns the results as a list of dictionaries.

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

            >>> from ontouml_models_lib import Model
            >>> from ontouml_models_lib import Query
            >>> model = Model('/path/to/ontology_model_folder')
            >>> query = Query('/path/to/query.sparql')
            >>> results = model.execute_query(query, '/path/to/results')
            >>> print(results)
            # Output: [{'subject': 'ExampleSubject', 'predicate': 'ExamplePredicate', 'object': 'ExampleObject'}]
        """
        # Ensure results_path is not None
        results_path = Path(results_path or "./results")
        results_path.mkdir(exist_ok=True)

        # The file is named based on the query name and the unique identifier of the QueryableElement.
        result_file = results_path / f"{query.query_file_path.stem}_result_{self.id}.csv"

        # Compute the model_graph_hash for the query_content
        query_hash = self._compute_query_hash(query.query_content)

        # Check if the model_graph_hash combination already exists
        if self._hash_exists(query_hash, results_path):
            logger.info(f"Skipping execution of query {query.query_file_path.name} on {self.id}. Results already available at {result_file}.")
            return []

        # Execute the query_content on the model_graph
        try:
            results = self.model_graph.query(query.query_content)

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
            self._save_results(result_list, result_file)
            self._save_hash_file(query_hash, results_path)
            logger.success(f"Query {query.query_file_path.name} successfully executed on {self.id}. "
                           f"Results written to {result_file}")

        except Exception:
            logger.exception(f"Query {query.query_file_path.name} execution failed on {self.id}.")
            return []

        else:
            return result_list

    def execute_queries(self, queries: list[Query], results_path: Optional[Union[str, Path]] = None) -> None:
        """
        Execute a list of SPARQL queries on the element's RDF graph and saves the results.

        This method iterates over a list of `Query` instances, executing each query on the `model_graph` associated
        with the `QueryableElement`. The results of each query are saved to a CSV file in the specified directory.
        This method is useful for batch processing multiple SPARQL queries on a single RDF graph.

        :param queries: A list of `Query` instances to be executed on the `model_graph`.
        :type queries: list[Query]
        :param results_path: The path to the directory where the query results will be saved. If not provided,
                             defaults to `./results`.
        :type results_path: Optional[Path]

        Example usage:

            >>> from ontouml_models_lib import Model
            >>> from ontouml_models_lib import Query
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
        """
        Compute a hash value for the QueryableElement.

        This method generates a hash value based on the element's unique identifier (`id`). The computed hash serves
        as a persistent identifier for the RDF graph associated with the element, ensuring consistency and integrity
        across operations involving the element.

        :return: The computed hash value for the QueryableElement.
        :rtype: int
        """
        return hash(self.id)

    def _compute_query_hash(self, query: str) -> int:
        """
        Compute a consistent hash value for a SPARQL query.

        This method generates a SHA-256 hash for the given SPARQL query string. The resulting hash is used to ensure
        that identical queries produce the same hash value, facilitating the management of query results and avoiding
        redundant executions.

        :param query: The SPARQL query string to be hashed.
        :type query: str
        :return: The computed hash value for the query.
        :rtype: int
        """
        encoded_content = query.encode("utf-8")
        content_hash = hashlib.sha256(encoded_content).hexdigest()
        return int(content_hash, 16)

    def _hash_exists(self, query_hash: int, results_path: Path) -> bool:
        """
        Check if a query's hash value already exists in the results directory.

        This method verifies whether a hash value for a given SPARQL query has been previously computed and stored in
        the `.hashes.csv` file within the specified results directory. This prevents redundant executions of the same
        query on the same RDF graph.

        :param query_hash: The hash value of the SPARQL query to be checked.
        :type query_hash: int
        :param results_path: The path to the directory where query results and hash records are stored.
        :type results_path: Path
        :return: True if the query's hash value exists in the results directory; False otherwise.
        :rtype: bool
        """
        hashes_file = results_path / ".hashes.csv"

        if not hashes_file.exists():
            return False

        with open(hashes_file, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["query_hash"]) == query_hash and int(row["model_hash"]) == self.model_graph_hash:
                    return True

        return False

    def _save_results(self, results: list[dict], result_file: Path):
        """
        Save the results of a SPARQL query to a CSV file.

        This method writes the results of a SPARQL query to a CSV file in the specified file.
        If no results are present, an empty file is created.

        :param results: A list of dictionaries containing the query results, where each dictionary represents a result row.
        :type results: list[dict]
        :param results_path: The path to the file to which the results will be saved.
        :type results_path: Path
        """
        with open(result_file, "w", newline="", encoding="utf-8") as file:
            if results:
                header = results[0].keys()
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(results)
            else:
                file.write("")  # Create an empty file if there are no results

    def _save_hash_file(self, query_hash: int, results_path: Path):
        """
        Save the hash value of a SPARQL query and the associated RDF graph to a file.

        This method records the hash values of a SPARQL query and the corresponding RDF graph in the `.hashes.csv` file
        within the specified directory. This ensures that the combination of the query and graph can be identified
        in future operations, preventing redundant executions.

        :param query_hash: The hash value of the SPARQL query being executed.
        :type query_hash: int
        :param results_path: The path to the directory where the hash record will be saved.
        :type results_path: Path
        """
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