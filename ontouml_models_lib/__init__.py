"""
The `__init__.py` file for the OntoUML/UFO catalog package.

This package provides a set of tools for manipulating and querying ontology models within the OntoUML/UFO framework.
The library is designed to help users work with concepts and models that conform to the standards and practices outlined
in the OntoUML/UFO Catalog, a structured and open-source repository containing high-quality, curated OntoUML and UFO
ontology models.

About the OntoUML/UFO Catalog
-----------------------------
The OntoUML/UFO Catalog, also known as the FAIR Model Catalog for Ontology-Driven Conceptual Modeling Research, is a
comprehensive and collaborative repository that supports empirical research in OntoUML and UFO, as well as in general
conceptual modeling. It offers a diverse collection of models in machine-readable formats (JSON and Turtle) that are
accessible via permanent identifiers. These models cover various domains and are created by modelers with differing
levels of expertise.

Public API
----------
This file defines the public API of the package, exposing the following classes and enumerations:

Public Classes
--------------
    - **Catalog**: Manages a collection of ontology models, enabling queries across multiple models within the catalog.
    - **Query**: Encapsulates SPARQL queries, providing methods for loading, hashing, and executing queries.
    - **Model**: Represents an individual ontology model, allowing for querying and metadata management.

Public Enumerations
-------------------
- class `OntologyPurpose`: Enumerates the standardized purposes for which an ontology model may be designed.
- class `OntologyDevelopmentContext`: Enumerates the possible development contexts for an ontology model.
- class `OntologyRepresentationStyle`: Enumerates the representation styles adopted in an ontology model.
- class `OntologyType`: Enumerates the categories of ontologies according to their scope.

Intended Use
------------
This library is specifically designed to assist users in manipulating and querying ontology models that conform to the
OntoUML/UFO standards. It provides a robust framework for interacting with the formal representations of concepts,
relations, and constraints that are central to the OntoUML/UFO modeling approach.

Example usage:

    >>> from ontouml_models_lib import Catalog, Query, Model
    >>> catalog = Catalog('/path/to/catalog')
    >>> query = Query('/path/to/query.sparql')
    >>> model = Model('/path/to/ontology_model_folder')

For more information on the OntoUML/UFO project and to access the latest models, please visit the official repository:
https://github.com/OntoUML/ontouml-models
"""

# Importing the publicly available classes
from .catalog import Catalog
from .query import Query
from .model import Model

# Importing the enumerations
from .enumerations import OntologyPurpose, OntologyDevelopmentContext, OntologyRepresentationStyle, OntologyType

# Defining the public API
__all__ = [
    "Catalog",
    "Query",
    "Model",
    "OntologyPurpose",
    "OntologyDevelopmentContext",
    "OntologyRepresentationStyle",
    "OntologyType",
]
