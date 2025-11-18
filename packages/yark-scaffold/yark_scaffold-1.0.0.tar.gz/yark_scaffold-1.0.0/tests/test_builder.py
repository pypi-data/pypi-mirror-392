from pathlib import Path

import pytest

from yark.builder import create_structure
from yark.parser import load_structure

VALID_STRUCTURES = [
    "valid_simple.yaml",
    "valid_nested.yaml",
    "valid_complex.yaml",
    "valid_mixed.yaml",
    "valid_empty_folders.yaml",
    "edge_single_file.yaml",
    "edge_deep_nesting.yaml",
    "edge_many_files.yaml",
    "edge_special_chars.yaml",
]

# Test 1: Creates all valid structures (MOST IMPORTANT)
@pytest.mark.parametrize("yaml_file", VALID_STRUCTURES)
def test_create_structure_from_yaml(yaml_file, tmp_path):
    """Test creating structures from all valid YAML fixtures."""
    fixture_path = Path("tests/fixtures") / yaml_file
    structure = load_structure(fixture_path)
    create_structure(structure, tmp_path)
    
    # Verify something was created
    created_items = list(tmp_path.iterdir())
    assert len(created_items) > 0


# Test 2: Invalid input raises error
def test_invalid_type_raises_error(tmp_path):
    """Non-dict should raise TypeError."""
    with pytest.raises(TypeError, match="structure must be a dict"):
        create_structure("not a dict", tmp_path)


# Test 3: Idempotency
def test_create_twice_no_error(tmp_path):
    """Creating same structure twice should not error."""
    structure = load_structure("tests/fixtures/valid_simple.yaml")
    create_structure(structure, tmp_path)
    create_structure(structure, tmp_path)
    assert len(list(tmp_path.iterdir())) > 0