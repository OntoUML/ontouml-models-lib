import shutil
from unittest.mock import patch
import pytest
from pathlib import Path
from ontouml_models_lib import Catalog


@pytest.fixture
def ontouml_models_path() -> Path:
    """Fixture to return the path to the existing ontouml-models folder."""
    return Path("../ontouml-models")


def test_get_subfolders_populated_directory(ontouml_models_path: Path) -> None:
    """Test that _get_subfolders returns all subdirectories in a populated models directory."""
    with patch.object(Catalog, "_load_models", return_value=None):
        catalog = Catalog(ontouml_models_path)
        subfolders = catalog._get_subfolders()

        # Adjust this assertion based on actual subfolder names in your ontouml-models/models directory
        assert len(subfolders) == 5, "Expected to retrieve subdirectory names from the populated models directory."


def test_get_subfolders_ignores_files(ontouml_models_path: Path) -> None:
    """Test that _get_subfolders ignores files and only returns directory names."""
    file_path = ontouml_models_path / "models/file.txt"
    file_path.write_text("This is a test file and should be ignored.")

    with patch.object(Catalog, "_load_models", return_value=None):
        catalog = Catalog(ontouml_models_path)
        subfolders = catalog._get_subfolders()

    assert file_path.name not in subfolders, "Expected the method to ignore files and return only subdirectory names."

    # Clean up the file after the test
    file_path.unlink()


def test_get_subfolders_empty_directory(ontouml_models_path: Path) -> None:
    """Test that _get_subfolders returns an empty list when the models directory is empty."""
    models_path = ontouml_models_path / "models"
    temp_path = ontouml_models_path / "temp_models"
    models_path.rename(temp_path)
    models_path.mkdir()  # Create an empty models directory

    try:
        with patch.object(Catalog, "_load_models", return_value=None):
            catalog = Catalog(ontouml_models_path)
            subfolders = catalog._get_subfolders()
            assert subfolders == [], "Expected an empty list when the models directory is empty."
    finally:
        models_path.rmdir()
        temp_path.rename(models_path)


def test_get_subfolders_ignores_nested_directories(ontouml_models_path: Path) -> None:
    """Test that _get_subfolders ignores nested directories and only returns top-level directory names."""
    nested_dir_path = ontouml_models_path / "models/model1/nested_model"
    nested_dir_path.mkdir(parents=True, exist_ok=True)

    with patch.object(Catalog, "_load_models", return_value=None):
        catalog = Catalog(ontouml_models_path)
        subfolders = catalog._get_subfolders()

    assert "nested_model" not in subfolders, "Expected the method to return only top-level directories."

    # Clean up the nested directory after the test
    shutil.rmtree(nested_dir_path.parent)  # This will remove the 'nested_model' and its parent 'model1'


def test_get_subfolders_handles_special_characters(ontouml_models_path: Path) -> None:
    """Test that _get_subfolders correctly handles directory names with special characters."""
    special_dir_path = ontouml_models_path / "models/special_#@!_model"
    special_dir_path.mkdir(parents=True, exist_ok=True)

    with patch.object(Catalog, "_load_models", return_value=None):
        catalog = Catalog(ontouml_models_path)
        subfolders = catalog._get_subfolders()

    assert (
        "special_#@!_model" in subfolders
    ), "Expected the method to correctly handle special characters in directory names."

    # Clean up the special directory after the test
    shutil.rmtree(special_dir_path)
