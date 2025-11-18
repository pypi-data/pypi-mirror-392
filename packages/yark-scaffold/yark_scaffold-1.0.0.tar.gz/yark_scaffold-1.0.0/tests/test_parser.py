from pathlib import Path

import pytest

from yark.parser import load_structure

VALID_YAMLS = [
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

@pytest.mark.parametrize("yaml_file", VALID_YAMLS)
def test_valid_yaml_loads_successfully(yaml_file):
    """Test that all valid YAML files load without errors."""
    fixture_path = Path("tests/fixtures") / yaml_file
    result = load_structure(fixture_path)
    
    assert isinstance(result, dict)
    
    assert len(result) > 0


INVALID_YAMLS = [
    ("invalid_no_slash.yaml", "folder keys must end with '/'"),
    ("invalid_empty.yaml", "YAML file is empty or invalid"),
    ("invalid_root_list.yaml", "expected a dictionary"),
    ("invalid_folder_value.yaml", "expected list or dict"),
    ("invalid_list_item.yaml", "expected a folder .* or filename"),
    ("invalid_nested_no_slash.yaml", "folder keys must end with '/'"),
]

@pytest.mark.parametrize("yaml_file,expected_error", INVALID_YAMLS)
def test_invalid_yaml_raises_error(yaml_file, expected_error):
    """Test that all invalid YAML files raise appropriate errors."""
    fixture_path = Path("tests/fixtures") / yaml_file
    
    with pytest.raises(ValueError, match=expected_error):
        load_structure(fixture_path)