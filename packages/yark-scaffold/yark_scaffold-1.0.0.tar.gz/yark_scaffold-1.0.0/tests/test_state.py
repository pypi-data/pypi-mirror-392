from pathlib import Path

import pytest

from yark.parser import load_structure
from yark.state import flatten_structure


# Test 1: Flatten simple structure
def test_flatten_simple_structure():
    """Test flattening a simple structure."""
    structure = {
        "project/": ["file1.txt", "file2.py"]
    }
    
    result = flatten_structure(structure)
    
    assert "project/" in result
    assert "project/file1.txt" in result
    assert "project/file2.py" in result
    assert len(result) == 3


# Test 2: Flatten nested structure
def test_flatten_nested_structure():
    """Test flattening nested folders."""
    structure = {
        "root/": [
            {"src/": ["main.py"]},
            "README.md"
        ]
    }
    
    result = flatten_structure(structure)
    
    assert "root/" in result
    assert "root/src/" in result
    assert "root/src/main.py" in result
    assert "root/README.md" in result
    assert len(result) == 4


# Test 3: Flatten deeply nested structure
def test_flatten_deep_nesting():
    """Test flattening deeply nested folders."""
    structure = {
        "a/": [
            {"b/": [
                {"c/": [
                    {"d/": ["deep.txt"]}
                ]}
            ]}
        ]
    }
    
    result = flatten_structure(structure)
    
    assert "a/" in result
    assert "a/b/" in result
    assert "a/b/c/" in result
    assert "a/b/c/d/" in result
    assert "a/b/c/d/deep.txt" in result


# Test 4: Flatten empty structure
def test_flatten_empty_structure():
    """Test flattening empty structure."""
    structure = {}
    
    result = flatten_structure(structure)
    
    assert result == []


# Test 5: Flatten structure with None
def test_flatten_none():
    """Test flattening None returns empty list."""
    result = flatten_structure(None)
    
    assert result == []


# Test 6: Flatten mixed dict and list structure
def test_flatten_mixed_structure():
    """Test flattening structure with both dict and list values."""
    structure = {
        "project/": {
            "src/": ["main.py", "utils.py"],
            "tests/": ["test.py"]
        }
    }
    
    result = flatten_structure(structure)
    
    assert "project/" in result
    assert "project/src/" in result
    assert "project/src/main.py" in result
    assert "project/src/utils.py" in result
    assert "project/tests/" in result
    assert "project/tests/test.py" in result


# Test 7: Flatten from YAML fixtures (parametrized)
VALID_STRUCTURES = [
    "valid_simple.yaml",
    "valid_nested.yaml",
    "valid_complex.yaml",
]

@pytest.mark.parametrize("yaml_file", VALID_STRUCTURES)
def test_flatten_from_yaml(yaml_file):
    """Test flattening structures from YAML fixtures."""
    fixture_path = Path("tests/fixtures") / yaml_file
    structure = load_structure(fixture_path)
    
    result = flatten_structure(structure)
    
    assert isinstance(result, list)
    
    assert len(result) > 0
    
    assert all(isinstance(item, str) for item in result)
    
    assert any(item.endswith('/') for item in result)


# Test 8: Flatten preserves correct paths
def test_flatten_preserves_paths():
    """Test that flattened paths are correct."""
    structure = {
        "root/": [
            {"sub1/": ["file1.txt"]},
            {"sub2/": ["file2.txt"]}
        ]
    }
    
    result = flatten_structure(structure)
    
    assert "root/sub1/file1.txt" in result
    assert "root/sub2/file2.txt" in result
    
    assert "root/sub1/" in result
    assert "root/sub2/" in result


# Test 9: Flatten with prefix parameter
def test_flatten_with_prefix():
    """Test flattening with custom prefix."""
    structure = {
        "project/": ["file.txt"]
    }
    
    result = flatten_structure(structure, prefix="base/")
    
    assert "base/project/" in result
    assert "base/project/file.txt" in result