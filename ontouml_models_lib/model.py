import hashlib
from pathlib import Path
from typing import Optional

import yaml
from rdflib import Graph
from rdflib.compare import to_isomorphic
from rdflib.util import guess_format

from enumerations import OntologyPurpose, OntologyDevelopmentContext, OntologyRepresentationStyle, OntologyType
from utils.queryable_element import QueryableElement

class Model(QueryableElement):
    def __init__(self, model_path: Path) -> None:
        super().__init__(id=model_path.name)  # Set the id to the last folder in the path
        self.model_path: Path = model_path
        self.title: str = ""
        self.keyword: list[str] = []
        self.acronym: Optional[str] = None
        self.source: Optional[str] = None
        self.language: Optional[str] = None
        self.designedForTask: list[OntologyPurpose] = []
        self.context: list[OntologyDevelopmentContext] = []
        self.representationStyle: Optional[OntologyRepresentationStyle] = None
        self.ontologyType: Optional[OntologyType] = None
        self.theme: Optional[str] = None

        path_model_graph = model_path / "ontology.ttl"
        path_metamodel_yaml = model_path / "metadata.yaml"

        self._load_graph_safely(path_model_graph)
        self.hash = self._compute_consistent_hash(self.graph)

        self._populate_attributes(path_metamodel_yaml)

    def _load_graph_safely(self, ontology_file: Path) -> Optional[Graph]:
        """ Safely load graph from file to working memory.

        :param ontology_file: Path to the ontology file to be loaded into the working memory.
        :type ontology_file: str
        :return: RDFLib graph loaded as object.
        :rtype: Graph
        """
        ontology_graph = Graph()
        if not ontology_file.exists():
            raise FileNotFoundError(f"Ontology file {ontology_file} not found.")
        try:
            file_format = guess_format(ontology_file)
            ontology_graph.parse(ontology_file, format=file_format, encoding='utf-8')
        except Exception as error:
            raise OSError(f"Error parsing ontology file {ontology_file}: {error}")

        self.graph = ontology_graph

    def _populate_attributes(self, yaml_file: Path) -> None:
        """Populate the attributes of the model from a YAML file.

        :param yaml_file: Path to the YAML file containing the metadata.
        :type yaml_file: Path
        """
        if not yaml_file.exists():
            raise FileNotFoundError(f"Metadata file {yaml_file} not found.")

        with open(yaml_file, 'r', encoding='utf-8') as file:
            metadata = yaml.safe_load(file)

        self.title = metadata.get('title', "")
        self.keyword = metadata.get('keyword', [])
        self.acronym = metadata.get('acronym')
        self.source = metadata.get('source')
        self.language = metadata.get('language')

        def match_enum_value(enum_class, value: str):
            value_normalized = value.lower().replace(" ", "").replace("_", "")
            for member in enum_class:
                member_value_normalized = member.value.lower().replace("_", "")
                if member_value_normalized == value_normalized:
                    return member
            # Explicit mapping for known cases
            if enum_class == OntologyRepresentationStyle:
                if value_normalized == 'ontouml':
                    return OntologyRepresentationStyle.ONTOUMLSTYLE
                elif value_normalized == 'ufo':
                    return OntologyRepresentationStyle.UFOSTYLE
            raise ValueError(f"{value} is not a valid {enum_class.__name__}")

        self.designedForTask = [
            match_enum_value(OntologyPurpose, task)
            for task in metadata.get('designedForTask', [])
        ]
        self.context = [
            match_enum_value(OntologyDevelopmentContext, ctx)
            for ctx in metadata.get('context', [])
        ]

        # Handle single value or list for representationStyle
        representation_style = metadata.get('representationStyle')
        if isinstance(representation_style, list):
            self.representationStyle = [
                match_enum_value(OntologyRepresentationStyle, style) for style in representation_style
            ]
        elif isinstance(representation_style, str):
            self.representationStyle = match_enum_value(OntologyRepresentationStyle, representation_style)
        else:
            self.representationStyle = None

        # Handle single value or list for ontologyType
        ontology_type = metadata.get('ontologyType')
        if isinstance(ontology_type, list):
            self.ontologyType = [
                match_enum_value(OntologyType, otype) for otype in ontology_type
            ]
        elif isinstance(ontology_type, str):
            self.ontologyType = match_enum_value(OntologyType, ontology_type)
        else:
            self.ontologyType = None

        self.theme = metadata.get('theme')

    def _compute_consistent_hash(self, graph: Graph) -> int:
        """ Compute a consistent hash for an RDFLib graph.

        :param graph: RDFLib graph to be hashed.
        :type graph: Graph
        :return: Consistent hash value of the graph.
        :rtype: int
        """
        # Serialize the graph to a canonical format (N-Triples)
        iso_graph = to_isomorphic(graph)
        serialized_graph = iso_graph.serialize(format='nt')

        # Sort the serialized triples
        sorted_triples = sorted(serialized_graph.splitlines())
        sorted_graph_str = "\n".join(sorted_triples)

        # Encode the sorted serialization to UTF-8
        encoded_graph = sorted_graph_str.encode('utf-8')

        # Compute the SHA-256 hash of the encoded graph
        graph_hash = hashlib.sha256(encoded_graph).hexdigest()

        # Convert the hexadecimal hash to an integer
        return int(graph_hash, 16)
