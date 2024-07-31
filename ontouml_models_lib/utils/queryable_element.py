import logging
import csv
import hashlib
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri
from query import Query

class QueryableElement:
    def __init__(self, id: str):
        self.id = id
        self.graph = Graph()
        self.hash = self._compute_hash()

    def _compute_hash(self) -> int:
        """Compute a hash for the QueryableElement."""
        return hash(self.id)

    def execute_query(self, query_file: Path, results_path: Path) -> list[dict]:
        """Execute a SPARQL query from a file on the element's graph and return results as a list of dictionaries.

        :param query_file: Path to the file containing the SPARQL query.
        :param results_path: Path to the directory to save the results and hash file.
        :return: List of query results as dictionaries.
        """
        # Ensure query_file is a Path object
        if isinstance(query_file, str):
            query_file = Path(query_file)

        if not query_file.exists():
            raise FileNotFoundError(f"Query file {query_file} not found.")

        # Read the SPARQL query from the file
        with open(query_file, 'r', encoding='utf-8') as file:
            query = file.read()

        # Compute the hash for the query
        query_hash = self._compute_query_hash(query)

        # Check if the hash combination already exists
        if self._hash_exists(query_hash, results_path):
            logging.info(f"Query with hash {query_hash} and model hash {self.hash} already executed. Skipping execution.")
            return []

        # Log the query
        logging.info(f"Executing query from file {query_file}: {query}")

        # Execute the query on the graph
        try:
            results = self.graph.query(query)
            logging.info(f"Query results: {results}")

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

            # Save the results and the hash
            self._save_results(query_file.stem, result_list, results_path)
            self._save_hash_file(query_hash, results_path)

            return result_list

        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            return []

    def _compute_query_hash(self, query: str) -> int:
        """Compute a consistent hash for the query content."""
        encoded_content = query.encode('utf-8')
        content_hash = hashlib.sha256(encoded_content).hexdigest()
        return int(content_hash, 16)

    def _hash_exists(self, query_hash: int, results_path: Path) -> bool:
        """Check if the hash combination already exists in the .hashes.csv file."""
        hashes_file = results_path / ".hashes.csv"

        if not hashes_file.exists():
            return False

        with open(hashes_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if int(row["query_hash"]) == query_hash and int(row["model_hash"]) == self.hash:
                    return True

        return False

    def _save_results(self, query_name: str, results: list[dict], results_path: Path):
        """Save the query results to a CSV file."""
        result_file = results_path / f"{query_name}_result_{self.id}.csv"
        with open(result_file, 'w', newline='', encoding='utf-8') as file:
            if results:
                header = results[0].keys()
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writeheader()
                writer.writerows(results)
            else:
                file.write('')  # Create an empty file if there are no results

        logging.info(f"Results written to {result_file}")

    def _save_hash_file(self, query_hash: int, results_path: Path):
        """Save the hash of the query and the model to a single .hashes.csv file."""
        hashes_file = results_path / ".hashes.csv"
        row = {"query_hash": query_hash, "model_hash": self.hash}

        if not hashes_file.exists():
            with open(hashes_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=row.keys())
                writer.writeheader()
                writer.writerow(row)
        else:
            with open(hashes_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=row.keys())
                writer.writerow(row)

        logging.info(f"Hash written to {hashes_file}")

    def execute_all_queries(self, queries_path: Path) -> None:
        """Execute all queries from a directory and save the results.

        :param queries_path: Path to the directory containing query files.
        """
        queries = Query.get_all_queries(queries_path)
        for query in queries:
            results_path = queries_path / 'results'
            self.execute_query(query.query_file, results_path)
