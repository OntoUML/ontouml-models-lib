import hashlib
from pathlib import Path
from typing import List, Union


class Query:
    def __init__(self, query_file: Union[str,Path]):
        query_file = Path(query_file) if isinstance(query_file, str) else query_file
        self.query_file_path: Path = query_file
        self.query_content: str = self._read_query_file(query_file)
        self.hash: int = self._compute_persistent_hash(self.query_content)

    @staticmethod
    def _read_query_file(query_file: Path) -> str:
        """Read the content of the query_content file."""
        with open(query_file, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    def _compute_persistent_hash(content: str) -> int:
        """Compute a persistent hash for the query_content content.

        :param content: The query_content content to be hashed.
        :type content: str
        :return: Consistent model_graph_hash value of the content.
        :rtype: int
        """
        # Encode the content to UTF-8
        encoded_content = content.encode("utf-8")

        # Compute the SHA-256 model_graph_hash of the encoded content
        content_hash = hashlib.sha256(encoded_content).hexdigest()

        # Convert the hexadecimal model_graph_hash to an integer
        return int(content_hash, 16)

    @staticmethod
    def load_queries(queries_path: Union[str, Path]) -> List["Query"]:
        """Load all query_content files from the specified directory catalog_path and return a list of Query instances.

        :param queries_path: Path to the directory containing query_content files.
        :type queries_path: Path
        :return: List of Query instances.
        :rtype: List[Query]
        """

        # Converting to catalog_path if it is a string
        queries_path = Path(queries_path) if isinstance(queries_path, str) else queries_path

        if not queries_path.is_dir():
            raise FileNotFoundError(f"Directory {queries_path} not found.")

        query_files = [file for file in queries_path.iterdir() if file.is_file() and file.suffix == ".txt"]
        return [Query(query_file) for query_file in query_files]
