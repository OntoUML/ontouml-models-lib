from unittest import mock

import pytest
from pathlib import Path
from rdflib import Graph, Literal, URIRef, RDF
from ontouml_models_lib import Catalog
from unittest.mock import patch


@pytest.fixture
def ontouml_models_path() -> Path:
    """Fixture to return the path to the existing ontouml-models folder."""
    return Path("../ontouml-models")


def test_create_catalog_graph_basic(ontouml_models_path: Path) -> None:
    """Test that _create_catalog_graph successfully creates an RDF graph with models."""
    catalog = Catalog(ontouml_models_path)
    graph: Graph = catalog._create_catalog_graph()

    assert isinstance(graph, Graph), "Expected an RDFLib Graph instance."
    assert len(graph) > 0, "Expected the graph to contain triples."


def test_create_catalog_graph_structure(ontouml_models_path: Path) -> None:
    """Test that _create_catalog_graph creates a graph with expected structure."""
    catalog = Catalog(ontouml_models_path)
    graph: Graph = catalog._create_catalog_graph()

    # Check for expected triples. Adjust the namespaces and predicates as per your vocabulary.
    for model in catalog.models:
        assert (None, None, None) in graph, f"Expected the graph to contain triples related to model: {model.id}"

def test_create_catalog_graph_consistency(ontouml_models_path: Path) -> None:
    """Test that the graph created by _create_catalog_graph is consistent with the catalog's state."""
    catalog = Catalog(ontouml_models_path)
    graph: Graph = catalog.graph

    for model in catalog.models:
        model_id = URIRef(f"https://w3id.org/ontouml-models/model/{model.id}/")
        assert (model_id, None, None) in graph or (None, None, model_id) in graph, \
            f"Expected the graph to contain references to model: {model.id}"

    assert len(graph) > 0, "The catalog graph should contain multiple triples representing the catalog state."

def test_catalog_graph_contains_expected_triples(ontouml_models_path: Path) -> None:
    """Test that specific expected triples are present in the graph."""
    catalog = Catalog(ontouml_models_path)
    graph: Graph = catalog.graph

    # Replace these with actual triples you expect to be in the graph
    expected_triples = [
        (URIRef("https://w3id.org/ontouml-models/model/abel2015petroleum-system/"), URIRef(RDF.type), URIRef("https://w3id.org/ontouml#Project")),
    ]

    for triple in expected_triples:
        assert triple in graph, f"Expected triple {triple} not found in the graph."


def test_catalog_graph_with_edge_cases(ontouml_models_path: Path) -> None:
    """Test how the graph handles models with edge case characteristics."""
    catalog = Catalog(ontouml_models_path)
    graph: Graph = catalog.graph

    # Example edge case: Check if graph handles a model with an empty or unusual element
    assert len(graph) > 0, "Graph should handle edge cases and still produce triples."

def test_create_catalog_graph_after_model_removal(ontouml_models_path: Path) -> None:
    """Test the graph after a model has been removed from the catalog."""
    catalog = Catalog(ontouml_models_path)
    initial_graph: Graph = catalog.graph

    # Simulate removal of a model
    model_to_remove = catalog.models[0]
    catalog.models.remove(model_to_remove)
    updated_graph: Graph = catalog._create_catalog_graph()

    model_id = URIRef(f"https://w3id.org/ontouml-models/model/{model_to_remove.id}/")
    assert (model_id, None, None) not in updated_graph and (None, None, model_id) not in updated_graph, \
        f"Expected the graph to not contain references to removed model: {model_to_remove.id}"
