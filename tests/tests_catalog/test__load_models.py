import pytest
from pathlib import Path
from ontouml_models_lib import Catalog, Model


@pytest.fixture
def ontouml_models_path() -> Path:
    """Fixture to return the path to the existing ontouml-models folder."""
    return Path("../ontouml-models")


def test_load_models_existing_catalog(ontouml_models_path: Path) -> None:
    """Test that _load_models correctly loads models from the ontouml-models folder."""
    catalog = Catalog(ontouml_models_path)

    # Adjust assertions based on the actual content of your ontouml-models folder
    assert len(catalog.models) > 0, "Catalog should contain models when valid model directories are present."
    assert all(isinstance(model, Model) for model in catalog.models), "All loaded items should be instances of Model."


import shutil


def test_load_models_handles_invalid_models(ontouml_models_path: Path) -> None:
    """Test that _load_models correctly handles invalid models within the ontouml-models folder."""
    # Introduce an invalid model by creating a directory without the required files
    invalid_model_path = ontouml_models_path / "models/invalid_model"
    invalid_model_path.mkdir(parents=True, exist_ok=True)

    # Optionally, create an invalid ontology.ttl file
    (invalid_model_path / "ontology.ttl").write_text("invalid content")

    try:
        with pytest.raises(RuntimeError, match="Failed to load model from folder: .*"):
            Catalog(ontouml_models_path)
    finally:
        # Clean up the invalid model after the test
        shutil.rmtree(invalid_model_path)


def test_load_models_handles_missing_ontology_file(ontouml_models_path: Path) -> None:
    """Test that _load_models raises RuntimeError when ontology.ttl is missing from a model."""
    # Introduce an invalid model by creating a directory without the ontology.ttl file
    invalid_model_path = ontouml_models_path / "models/invalid_model_no_ontology"
    invalid_model_path.mkdir(parents=True, exist_ok=True)

    try:
        with pytest.raises(RuntimeError, match="Failed to load model from folder: .*"):
            Catalog(ontouml_models_path)
    finally:
        # Clean up the invalid model after the test
        shutil.rmtree(invalid_model_path)
