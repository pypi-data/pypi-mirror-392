from pathlib import Path

import pytest

from yark.builder import create_structure
from yark.parser import load_structure
from yark.scanner import scan_existing_structure

VALID_STRUCTURES = [
    "valid_simple.yaml",
    "valid_nested.yaml",
    "valid_complex.yaml",
]

# Test 1: Scan builder-created structures (parametrized)
@pytest.mark.parametrize("yaml_file", VALID_STRUCTURES)
def test_scan_created_structure(yaml_file, tmp_path):
    """Test scanning structures created by builder."""
    fixture_path = Path("tests/fixtures") / yaml_file
    structure = load_structure(fixture_path)
    create_structure(structure, tmp_path)
    
    root_folder = list(structure.keys())[0].rstrip('/')
    result = scan_existing_structure(tmp_path / root_folder)
    
    assert isinstance(result, dict)
    assert len(result) > 0


# Test 2: Scan non-existent directory
def test_scan_nonexistent_returns_empty(tmp_path):
    """Scanning non-existent directory should return empty dict."""
    result = scan_existing_structure(tmp_path / "nonexistent")
    assert result == {}


# Test 3: Scanner ignores default patterns
def test_scan_ignores_git_and_ds_store(tmp_path):
    """Scanner should ignore .git and .DS_Store by default."""
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / "file.txt").touch()
    (tmp_path / "project" / ".git").mkdir()
    (tmp_path / "project" / ".DS_Store").touch()
    
    result = scan_existing_structure(tmp_path / "project")
    
    assert "file.txt" in result
    assert ".git" not in result
    assert ".DS_Store" not in result


# Test 4: Scan empty directory
def test_scan_empty_directory(tmp_path):
    """Scanning empty directory should return empty dict."""
    (tmp_path / "empty").mkdir()
    result = scan_existing_structure(tmp_path / "empty")
    assert result == {}