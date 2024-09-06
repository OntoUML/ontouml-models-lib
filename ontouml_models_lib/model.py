"""
The `model` module provides the `Model` class, a specialized extension of the `QueryableElement` class, designed \
for managing and interacting with individual ontology models within the OntoUML/UFO catalog.

This module facilitates the loading, querying, and management of RDF graphs and associated metadata for ontology
models, ensuring compliance with the metadata schema specified in Appendix A.

Overview
--------
The `Model` class represents a single ontology model, encapsulating its RDF graph and metadata, and provides methods for
querying and interacting with this data. The metadata attributes, such as `title`, `keyword`, `acronym`, `language`,
and others, are populated based on a YAML file and follow the standards defined in the OntoUML/UFO catalog's metadata
schema. The class is built to support operations on ontology models stored in RDF formats, such as Turtle, and
accompanied by metadata in YAML format.

Usage
-----
Example 1: Loading a Model and Accessing Metadata

    >>> from ontouml_models_lib import Model
    >>> model = Model('/path/to/ontology_model_folder')
    >>> print(model.title)
    # Output: "Example Ontology Title"
    >>> print(model.keyword)
    # Output: ["ontology", "example"]

Example 2: Executing a Query on the Model

    >>> from ontouml_models_lib import Model
    >>> from ontouml_models_lib import Query
    >>> model = Model('/path/to/ontology_model_folder')
    >>> query = Query('/path/to/query.sparql')
    >>> results = model.execute_query(query, '/path/to/results')
    >>> print(results)
    # Output: [{'subject': 'ExampleSubject', 'predicate': 'ExamplePredicate', 'object': 'ExampleObject'}]

Dependencies
------------
- **rdflib**: For RDF graph operations and SPARQL query execution.
- **yaml**: For parsing YAML files containing metadata.
- **loguru**: For logging operations and debugging information.

References
----------
For additional details on the OntoUML/UFO catalog, refer to the official OntoUML repository:
https://github.com/OntoUML/ontouml-models
"""

import hashlib
from pathlib import Path
from typing import Optional, Union

import yaml
from loguru import logger
from rdflib import Graph
from rdflib.compare import to_isomorphic
from rdflib.util import guess_format

from .enumerations import OntologyPurpose, OntologyDevelopmentContext, OntologyRepresentationStyle, OntologyType
from .utils.queryable_element import QueryableElement


class Model(QueryableElement):
    """
    Represents an individual ontology model within the OntoUML/UFO catalog.

    The `Model` class extends the `QueryableElement` class to manage and interact with RDF graphs representing ontology
    models. It provides methods for loading RDF graphs, extracting metadata from associated YAML files, and executing
    SPARQL queries. This class ensures that ontology data is consistently managed and that metadata attributes are
    easily accessible.

    :ivar title: The title of the ontology model, as determined by the `dct:title` property. There must be at most one
                 title per language.
    :vartype title: str
    :ivar keyword: A list of keywords associated with the ontology model, aiding in the categorization and
                   searchability of the model.
    :vartype keyword: list[str]
    :ivar acronym: An optional acronym for the ontology model, providing a shorthand identifier.
    :vartype acronym: Optional[str]
    :ivar source: The source or origin of the ontology model, typically a publication, organization, or project.
                  It is recommended to use persistent and resolvable identifiers, such as DOIs or DBLP URIs,
                  to refer to these resources.
    :vartype source: Optional[str]
    :ivar language: The language in which the lexical labels of the ontology model are written.
                    The use of values from the IANA Language Sub Tag Registry (e.g., "en", "pt") is required.
    :vartype language: Optional[str]
    :ivar designedForTask: A list of standardized purposes for which the ontology model was designed, categorized using
                           the OntologyPurpose enumeration. Examples include Conceptual Clarification, Data Publication,
                           and Decision Support Systems.
    :vartype designedForTask: list[OntologyPurpose]
    :ivar context: The development context of the ontology model, classified under the OntologyDevelopmentContext
                   enumeration. Examples include Research, Industry, and Classroom.
    :vartype context: list[OntologyDevelopmentContext]
    :ivar representationStyle: The representation style of the ontology model, categorized under the
                               OntologyRepresentationStyle enumeration. Examples include OntoumlStyle and UfoStyle.
    :vartype representationStyle: Optional[OntologyRepresentationStyle]
    :ivar ontologyType: The type of ontology, categorized under the OntologyType enumeration.
                        Examples include Core, Domain, and Application.
    :vartype ontologyType: Optional[OntologyType]
    :ivar theme: The central theme of the ontology model, identified according to a theme taxonomy such as the
                 Library of Congress Classification (LCC).
    :vartype theme: Optional[str]

    **Example**::

        >>> from ontouml_models_lib import Model
        >>> model = Model('/path/to/ontology_model_folder')
        >>> print(model.title)
        # Output: "Example Ontology Title"
        >>> print(model.keyword)
        # Output: ["ontology", "example"]
    """

    def __init__(self, model_path: Union[Path, str]) -> None:
        """
        Initialize a new instance of the `Model` class.

        This constructor loads an ontology model from the specified path, including its RDF graph and associated
        metadata. It verifies the validity of the provided path, loads the RDF graphs from Turtle files (`ontology.ttl`
        and `metadata.ttl`), and extracts metadata from a YAML file (`metadata.yaml`). The metadata attributes are
        populated based on the definitions provided in the OntoUML/UFO catalog's metadata schema.

        :param model_path: The path to the directory containing the ontology model files. This path must exist and
                           typically contains `ontology.ttl`, `metadata.ttl`, and `metadata.yaml` files.
        :type model_path: Union[Path, str]

        :raises ValueError: If the provided path is invalid or does not exist.
        :raises RuntimeError: If loading the RDF graph or metadata fails.

        **Example**::

            >>> from ontouml_models_lib import Model
            >>> model = Model('/path/to/ontology_model_folder')
            >>> print(model.title)
            # Output: "Example Ontology Title"
        """
        if isinstance(model_path, str):
            model_path = Path(model_path)

        # Check if the model_path is a valid Path and exists
        if not isinstance(model_path, Path) or not model_path.exists():
            raise ValueError(f"Invalid catalog_path provided: '{model_path}'. Path must exist.")

        super().__init__(id=model_path.name)  # Set the id to the last folder in the catalog_path

        # Metadata attributes
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

        # Paths
        self.model_path: Path = model_path
        path_model_graph = model_path / "ontology.ttl"
        path_metadata_graph = model_path / "metadata.ttl"
        path_metadata_yaml = model_path / "metadata.yaml"

        try:

            # Load model_graph and metadata_graph
            self.model_graph: Graph = self._load_graph_safely(path_model_graph)
            self.metadata_graph: Graph = self._load_graph_safely(path_metadata_graph)

            # Compute the persistent hashes of the model's graphs
            self.model_graph_hash = self._compute_consistent_hash(self.model_graph)
            self.metadata_graph_hash = self._compute_consistent_hash(self.metadata_graph)

            # Populate attributes from the YAML file
            self._populate_attributes(path_metadata_yaml)

            logger.success(f"Successfully loaded model from folder: {model_path.name}")

        except Exception as e:
            raise RuntimeError(f"Failed to load model from folder: {model_path.name}") from e

    # ---------------------------------------------
    # Private Methods
    # ---------------------------------------------

    def _compute_consistent_hash(self, graph: Graph) -> int:
        """
        Compute a consistent hash value for an RDFLib graph.

        This method generates a SHA-256 hash for an RDFLib graph by first serializing it to a canonical format
        (N-Triples), sorting the serialized triples, and then encoding the sorted serialization to UTF-8. The
        resulting hash value is used to ensure consistency and integrity of the graph's content.

        :param graph: The RDFLib graph to be hashed.
        :type graph: Graph
        :return: The computed hash value for the RDFLib graph.
        :rtype: int
        """
        # Serialize the model_graph to a canonical format (N-Triples)
        iso_graph = to_isomorphic(graph)
        serialized_graph = iso_graph.serialize(format="nt")

        # Sort the serialized triples
        sorted_triples = sorted(serialized_graph.splitlines())
        sorted_graph_str = "\n".join(sorted_triples)

        # Encode the sorted serialization to UTF-8
        encoded_graph = sorted_graph_str.encode("utf-8")

        # Compute the SHA-256 model_graph_hash of the encoded model_graph
        graph_hash = hashlib.sha256(encoded_graph).hexdigest()

        # Convert the hexadecimal model_graph_hash to an integer
        return int(graph_hash, 16)

    def _load_graph_safely(self, ontology_file: Path) -> Graph:
        """
        Safely load an RDFLib graph from a file.

        This method loads an RDFLib graph from a specified ontology file, ensuring that the file exists and is correctly
        parsed. It determines the file format based on its extension and returns the loaded graph.

        :param ontology_file: The path to the ontology file to be loaded.
        :type ontology_file: Path
        :return: The loaded RDFLib graph.
        :rtype: Graph
        :raises FileNotFoundError: If the ontology file does not exist.
        :raises OSError: If an error occurs during the parsing of the ontology file.
        """
        ontology_graph = Graph()
        if not ontology_file.exists():
            raise FileNotFoundError(f"Ontology file {ontology_file} not found.")
        try:
            file_format = guess_format(ontology_file)
            ontology_graph.parse(ontology_file, format=file_format, encoding="utf-8")
        except Exception as error:
            raise OSError(f"Error parsing ontology file {ontology_file}: {error}") from error

        return ontology_graph

    def _populate_attributes(self, yaml_file: Path) -> None:
        """
        Populate the model's attributes from a YAML metadata file.

        This method reads a YAML file containing metadata and assigns the corresponding values to the model's attrs.
        It handles enumerations by matching the string values in the YAML file to the appropriate enumeration members.
        The method supports both single-value and list-value attributes.

        :param yaml_file: The path to the YAML file containing the metadata.
        :type yaml_file: Path
        :raises FileNotFoundError: If the YAML metadata file does not exist.
        :raises ValueError: If an invalid value is encountered for an enumeration attribute.
        """
        if not yaml_file.exists():
            raise FileNotFoundError(f"Metadata file {yaml_file} not found.")

        with open(yaml_file, "r", encoding="utf-8") as file:
            metadata = yaml.safe_load(file)

        self.title = metadata.get("title", "")
        self.keyword = metadata.get("keyword", [])
        self.acronym = metadata.get("acronym")
        self.source = metadata.get("source")
        self.language = metadata.get("language")

        def match_enum_value(enum_class, value: str):
            value_normalized = value.lower().replace(" ", "").replace("_", "")
            for member in enum_class:
                member_value_normalized = member.value.lower().replace("_", "")
                if member_value_normalized == value_normalized:
                    return member
            # Explicit mapping for known cases
            if enum_class == OntologyRepresentationStyle:
                if value_normalized == "ontouml":
                    return OntologyRepresentationStyle.ONTOUML_STYLE
                if value_normalized == "ufo":
                    return OntologyRepresentationStyle.UFO_STYLE
            raise ValueError(f"{value} is not a valid {enum_class.__name__}")

        self.designedForTask = [match_enum_value(OntologyPurpose, task) for task in metadata.get("designedForTask", [])]
        self.context = [match_enum_value(OntologyDevelopmentContext, ctx) for ctx in metadata.get("context", [])]

        # Handle single value or list for representationStyle
        representation_style = metadata.get("representationStyle")
        if isinstance(representation_style, list):
            self.representationStyle = [
                match_enum_value(OntologyRepresentationStyle, style) for style in representation_style
            ]
        elif isinstance(representation_style, str):
            self.representationStyle = match_enum_value(OntologyRepresentationStyle, representation_style)
        else:
            self.representationStyle = None

        # Handle single value or list for ontologyType
        ontology_type = metadata.get("ontologyType")
        if isinstance(ontology_type, list):
            self.ontologyType = [match_enum_value(OntologyType, otype) for otype in ontology_type]
        elif isinstance(ontology_type, str):
            self.ontologyType = match_enum_value(OntologyType, ontology_type)
        else:
            self.ontologyType = None

        self.theme = metadata.get("theme")
