[![Project DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10211480.svg)](https://doi.org/10.5281/zenodo.10211480)
[![Project Status - Active](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)
![GitHub - Release Date - PublishedAt](https://img.shields.io/github/release-date/OntoUML/ontouml-models-lib)
![GitHub - Last Commit - Branch](https://img.shields.io/github/last-commit/OntoUML/ontouml-models-lib/main)
![PyPI - Project](https://img.shields.io/pypi/v/ontouml-models-lib)
![PyPI - Downloads](https://img.shields.io/pypi/dm/ontouml-models-lib)
![Language - Top](https://img.shields.io/github/languages/top/OntoUML/ontouml-models-lib)
![Language - Version](https://img.shields.io/pypi/pyversions/ontouml-models-lib)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/OntoUML/ontouml-models-lib)
![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/OntoUML/ontouml-models-lib/badge)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)
![License - GitHub](https://img.shields.io/github/license/OntoUML/ontouml-models-lib)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
![Website](https://img.shields.io/website/http/ontouml.github.io/ontouml-models-lib.svg)

[//]: # ([![pre-commit.ci status]&#40;https://results.pre-commit.ci/badge/github/OntoUML/ontouml-models-lib/main.svg&#41;]&#40;https://results.pre-commit.ci/latest/github/OntoUML/ontouml-models-lib/main&#41;)
[//]: # (![GitHub Workflow Status &#40;with event&#41;]&#40;https://img.shields.io/github/actions/workflow/status/OntoUML/ontouml-models-lib/code_testing.yml&#41;)
[//]: # ([![OpenSSF Best Practices]&#40;https://www.bestpractices.dev/projects/8328/badge&#41;]&#40;https://www.bestpractices.dev/projects/8328&#41;)
[//]: # (![Static Badge]&#40;https://img.shields.io/badge/Test_Coverage-100%25-green&#41;)

# OntoUML/UFO Catalog Python Library

<p align="center"><img src="https://raw.githubusercontent.com/OntoUML/ontouml-models-lib/main/resources/ontouml-models-lib-logo.png" width="500"></p>

<!-- TOC -->
* [OntoUML/UFO Catalog Python Library](#ontoumlufo-catalog-python-library)
  * [Overview](#overview)
  * [About the OntoUML/UFO Catalog](#about-the-ontoumlufo-catalog)
  * [Features](#features)
  * [Installation](#installation)
  * [The Library's Classes](#the-librarys-classes)
    * [Examples](#examples)
      * [Example 1: Working with the Catalog Class](#example-1-working-with-the-catalog-class)
      * [Example 2: Working with the Model Class](#example-2-working-with-the-model-class)
      * [Example 3: Working with the Query Class](#example-3-working-with-the-query-class)
  * [How to Contribute](#how-to-contribute)
    * [Reporting Issues](#reporting-issues)
    * [Code Contributions](#code-contributions)
    * [Test Contributions](#test-contributions)
    * [General Guidelines](#general-guidelines)
  * [License](#license)
  * [Author](#author)
<!-- TOC -->

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
pip install ontouml-models-lib
```

## The Library's Classes

The `Catalog`, `Model`, and `Query` classes are core components of the OntoUML/UFO Catalog Python library, designed to enable manipulation and querying of ontology models. The `Catalog` class is used to manage collections of ontology models, allowing users to load, query, and interact with multiple models as a cohesive unit. The `Model` class represents an individual ontology model, providing methods for querying its RDF graph and accessing metadata. The `Query` class encapsulates SPARQL queries, enabling their execution on RDF graphs within the OntoUML/UFO framework.

These classes are essential when working with the OntoUML/UFO Catalog, which is a repository of high-quality, curated ontology models. Users can utilize the `Catalog` class to manage entire collections of models, the `Model` class to interact with individual models, and the `Query` class to run specific queries on the data. This design ensures that users can efficiently organize, access, and analyze ontology models in a standardized way.

### Examples

#### Example 1: Working with the Catalog Class

```python
from ontouml_models_lib import Catalog

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
from ontouml_models_lib import Model, Query

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
from ontouml_models_lib import Query

## Load a SPARQL query from a file
query = Query('/path/to/query.sparql')

## Access the query content
print(query.query_content)

## Compute the hash of the query (useful for caching results)
print(query.hash)
```



## How to Contribute

We welcome and appreciate contributions from the community! Whether you want to report a bug, suggest a new feature, or improve our codebase, your input is valuable.

### Reporting Issues

- If you find a bug or wish to suggest a feature, please [open a new issue](https://github.com/OntoUML/ontouml-models-lib/issues/new).
- If you notice any discrepancies in the documentation created with the aid of AI, feel free to [report them by opening an issue](https://github.com/OntoUML/ontouml-models-lib/issues/new).

### Code Contributions

1. Fork the project repository and create a new feature branch for your work: `git checkout -b feature/YourFeatureName`.
2. Make and commit your changes with descriptive commit messages.
3. Push your work back up to your fork: `git push origin feature/YourFeatureName`.
4. Submit a pull request to propose merging your feature branch into the main project repository.

### Test Contributions

- Enhance the project's reliability by adding new tests or improving existing ones.

### General Guidelines

- Ensure your code follows our coding standards.
- Update the documentation as necessary.
- Make sure your contributions do not introduce new issues.

We appreciate your time and expertise in contributing to this project!

## License

This library is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International Public License](https://creativecommons.org/licenses/by-sa/4.0/). Please note that the models included in the OntoUML/UFO Catalog may have their own licenses, as specified in their metadata.

## Author

The ontouml-models-lib library is developed and maintained by:

- Pedro Paulo Favato Barcelos [[GitHub](https://github.com/pedropaulofb)] [[LinkedIn](https://www.linkedin.com/in/pedro-paulo-favato-barcelos/)]

Feel free to reach out using the provided links. For inquiries, contributions, or to report any issues, you can [open a new issue](https://github.com/OntoUML/ontouml-models-lib/issues/new) on this repository.
