import logging
import csv
from pathlib import Path
from icecream import ic
from rdflib import Graph, URIRef
from rdflib.namespace import split_uri
from query import Query


class QueryableElement:
    def __init__(self, id: str):
        self.id = id
        self.graph = Graph()

    def execute_query(self, query_file: Path) -> list[dict]:
        """Execute a SPARQL query from a file on the element's graph and return results as a list of dictionaries.

        :param query_file: Path to the file containing the SPARQL query.
        :type query_file: Path
        :return: List of query results as dictionaries.
        :rtype: List[dict]
        """

        # Ensure query_file is a Path object
        if isinstance(query_file, str):
            query_file = Path(query_file)


        if not query_file.exists():
            raise FileNotFoundError(f"Query file {query_file} not found.")

        # Read the SPARQL query from the file
        with open(query_file, 'r', encoding='utf-8') as file:
            query = file.read()


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
                        # Remove the namespace from the URI
                        _, local_name = split_uri(result[var])
                        result_dict[str(var)] = local_name
                    else:
                        result_dict[str(var)] = value
                result_list.append(result_dict)

            return result_list

        except Exception as e:
            # Log the exception and return an empty list if the query execution fails
            logging.error(f"Query execution failed: {e}")
            return []

    def execute_all_queries(self, queries_path: Path) -> None:
        """Execute all queries from a directory and save the results.

        :param queries_path: Path to the directory containing query files.
        :type queries_path: Path
        """
        # Create the results directory inside the queries_path folder
        results_path = queries_path / 'results'
        results_path.mkdir(exist_ok=True)


        # Load all queries
        queries = Query.get_all_queries(queries_path)

        # Execute each query and save the results
        for query in queries:
            # Execute the query
            results = self.execute_query(query.query_file)

            # Ensure results is always a list
            if results is None:
                results = []


            # Save the query hash to a file
            hash_file = results_path / f".{query.query_file.stem}_hash"
            with open(hash_file, 'w', encoding='utf-8') as file:
                file.write(str(query.hash))

            # Save the results to a CSV file
            result_file = results_path / f"{query.query_file.stem}_result_{self.id}.csv"
            with open(result_file, 'w', newline='', encoding='utf-8') as file:
                if results:
                    # Get the header from the keys of the first result
                    header = results[0].keys()
                    writer = csv.DictWriter(file, fieldnames=header)
                    writer.writeheader()
                    writer.writerows(results)
                else:
                    file.write('')  # Create an empty file if there are no results

            logging.info(f"Results written to {result_file}")
