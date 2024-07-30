import hashlib
from pathlib import Path
from typing import List

class Query:
    def __init__(self, query_file: Path):
        self.query_file = query_file
        self.query = self._read_query_file(query_file)
        self.hash = self._compute_consistent_hash(self.query)

    @staticmethod
    def _read_query_file(query_file: Path) -> str:
        """Read the content of the query file."""
        with open(query_file, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def _compute_consistent_hash(content: str) -> int:
        """ Compute a consistent hash for the query content.

        :param content: The query content to be hashed.
        :type content: str
        :return: Consistent hash value of the content.
        :rtype: int
        """
        # Encode the content to UTF-8
        encoded_content = content.encode('utf-8')

        # Compute the SHA-256 hash of the encoded content
        content_hash = hashlib.sha256(encoded_content).hexdigest()

        # Convert the hexadecimal hash to an integer
        return int(content_hash, 16)

    @staticmethod
    def get_all_queries(path: Path) -> List['Query']:
        """Load all query files from the specified directory path and return a list of Query instances.

        :param path: Path to the directory containing query files.
        :type path: Path
        :return: List of Query instances.
        :rtype: List[Query]
        """
        if not path.is_dir():
            raise FileNotFoundError(f"Directory {path} not found.")

        query_files = [file for file in path.iterdir() if file.is_file() and file.suffix == '.txt']
        return [Query(query_file) for query_file in query_files]
