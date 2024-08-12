
# OntoUML/UFO Catalog Python Library

<p align="center"><img src="https://user-images.githubusercontent.com/8641647/223740939-1abcd2af-e954-4d19-b087-56f1be4417c3.png" width="500"></p>

## Overview

This Python library provides tools for manipulating and querying ontology models within the OntoUML/UFO framework. It is designed to work with concepts and models that adhere to the standards and practices outlined in the OntoUML/UFO Catalog. The library supports operations on models stored in machine-readable formats such as JSON and Turtle, and enables the execution of SPARQL queries on these models.

## About the OntoUML/UFO Catalog

The [FAIR Model Catalog for Ontology-Driven Conceptual Modeling Research](https://github.com/OntoUML/ontouml-models), also known as **OntoUML/UFO Catalog**, is a structured and open-source repository containing a collection of OntoUML and UFO ontology models. The catalog is designed to support empirical research in OntoUML and UFO, as well as the broader field of conceptual modeling. It provides a diverse range of models created by modelers with varying expertise, covering multiple domains and purposes. These models are available in machine-readable formats such as JSON and Turtle, which facilitate automated processing and querying. Each model in the catalog is accessible via a permanent identifier, ensuring long-term availability and reference.

The catalog organizes its content into a well-defined structure, storing models and their metadata in linked data formats. This structure allows for the integration of the models into a knowledge graph, enabling advanced querying and analysis using SPARQL. The OntoUML/UFO Catalog is built to be collaborative and accessible, allowing users to contribute to and leverage a comprehensive resource for conceptual modeling research. For more details, please visit the official OntoUML/UFO Catalog repository: [OntoUML/UFO Catalog](https://github.com/OntoUML/ontouml-models).


## Features

- **Catalog Management:** Load, manage, and query collections of ontology models.
- **Model Interaction:** Interact with individual ontology models, including querying and metadata management.
- **SPARQL Query Execution:** Execute SPARQL queries on RDF graphs representing ontology models.
- **Metadata Handling:** Support for metadata schemas used in the OntoUML/UFO Catalog, ensuring consistency and compliance with the catalog's structure.

## Installation

To install the library, use pip:

```bash
pip install ontouml_models_lib
```

## The Library's Classes

The `Catalog`, `Model`, and `Query` classes are core components of the OntoUML/UFO Catalog Python library, designed to enable manipulation and querying of ontology models. The `Catalog` class is used to manage collections of ontology models, allowing users to load, query, and interact with multiple models as a cohesive unit. The `Model` class represents an individual ontology model, providing methods for querying its RDF graph and accessing metadata. The `Query` class encapsulates SPARQL queries, enabling their execution on RDF graphs within the OntoUML/UFO framework.

These classes are essential when working with the OntoUML/UFO Catalog, which is a repository of high-quality, curated ontology models. Users can utilize the `Catalog` class to manage entire collections of models, the `Model` class to interact with individual models, and the `Query` class to run specific queries on the data. This design ensures that users can efficiently organize, access, and analyze ontology models in a standardized way.

### Examples

#### Example 1: Working with the Catalog Class

```python
from ontouml_model_lib import Catalog

## Load a catalog from a specified path
catalog = Catalog('/path/to/catalog')

## List all models in the catalog
models = catalog.list_models()
print(models)

## Perform a query across all models in the catalog
query = Query('/path/to/query.sparql')
results = catalog.execute_query(query)
print(results)
```

#### Example 2: Working with the Model Class

```python
from ontouml_model_lib import Model, Query

## Load an individual ontology model
model = Model('/path/to/ontology_model_folder')

## Print the title of the model
print(model.title)

## Execute a SPARQL query on the model
query = Query('/path/to/query.sparql')
results = model.execute_query(query)
print(results)
```

#### Example 3: Working with the Query Class

```python
from ontouml_model_lib import Query

## Load a SPARQL query from a file
query = Query('/path/to/query.sparql')

## Access the query content
print(query.query_content)

## Compute the hash of the query (useful for caching results)
print(query.hash)
```



## Contributing

Contributions to this library are welcome. Please refer to the [OntoUML/UFO Catalog contribution guidelines](https://github.com/OntoUML/ontouml-models#how-to-contribute) for more information on how to contribute models or report issues.

## License

This library is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Public License](https://creativecommons.org/licenses/by-sa/4.0/). Please note that the models included in the OntoUML/UFO Catalog may have their own licenses, as specified in their metadata.

## Author

The LangString library is developed and maintained by:

- Pedro Paulo Favato Barcelos [[GitHub](https://github.com/pedropaulofb)] [[LinkedIn](https://www.linkedin.com/in/pedro-paulo-favato-barcelos/)]

Feel free to reach out using the provided links. For inquiries, contributions, or to report any issues, you can [open a new issue](https://github.com/pedropaulofb/langstring/issues/new) on this repository.