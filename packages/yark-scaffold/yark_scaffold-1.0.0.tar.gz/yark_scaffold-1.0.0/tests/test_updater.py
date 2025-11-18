from pathlib import Path

import pytest

from yark.builder import create_structure
from yark.parser import load_structure
from yark.updater import update_structure


# Test 1: Update creates new files
def test_update_creates_new_files(tmp_path):
    """Test that update creates new files from desired structure."""
    # Current structure (empty)
    current = {}
    
    # Desired structure (has files)
    desired = {"project/": ["new_file.txt"]}
    
    # Update
    update_structure(desired, current, tmp_path)
    
    # Verify file was created
    assert (tmp_path / "project" / "new_file.txt").exists()


# Test 2: Update deletes managed files
def test_update_deletes_managed_files(tmp_path):
    """Test that update deletes files that are managed."""
    # Create initial file
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / "old_file.txt").touch()
    
    # Current structure (has file)
    current = {"project/": ["old_file.txt"]}
    
    # Desired structure (file removed)
    desired = {"project/": []}
    
    # Managed paths (file is managed)
    managed = {"project/", "project/old_file.txt"}
    
    # Update
    update_structure(desired, current, tmp_path, managed_paths=managed)
    
    # Verify file was deleted
    assert not (tmp_path / "project" / "old_file.txt").exists()


# Test 3: Update IGNORES unmanaged files (CRITICAL SAFETY TEST)
def test_update_ignores_unmanaged_files(tmp_path):
    """Test that update does NOT delete unmanaged files."""
    # Create user's file (not managed by Yark)
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / "user_file.txt").touch()
    
    # Current structure (has user file)
    current = {"project/": ["user_file.txt"]}
    
    # Desired structure (empty - doesn't have user file)
    desired = {"project/": []}
    
    # Managed paths (user_file.txt is NOT managed)
    managed = {"project/"}  # Only folder is managed, not the file
    
    # Update
    update_structure(desired, current, tmp_path, managed_paths=managed)
    
    # Verify user file was NOT deleted
    assert (tmp_path / "project" / "user_file.txt").exists()


# Test 4: Dry-run returns changes without modifying filesystem
def test_update_dry_run(tmp_path):
    """Test that dry-run returns changes without creating/deleting."""
    # Current structure
    current = {"project/": ["old.txt"]}
    
    # Desired structure
    desired = {"project/": ["new.txt"]}
    
    # Managed paths
    managed = {"project/", "project/old.txt"}
    
    # Dry-run
    changes = update_structure(desired, current, tmp_path, 
                              dry_run=True, managed_paths=managed)
    
    # Verify changes dict returned
    assert changes is not None
    assert "project/" in changes
    assert "new.txt" in changes["project/"]
    assert changes["project/"]["new.txt"] == "CREATE"
    assert "old.txt" in changes["project/"]
    assert changes["project/"]["old.txt"] == "DELETE"
    
    # Verify filesystem unchanged
    assert not (tmp_path / "project").exists()


# Test 5: Update creates nested structures
def test_update_creates_nested_structure(tmp_path):
    """Test that update creates nested folders and files."""
    current = {}
    desired = {
        "project/": [
            {"src/": ["main.py"]},
            "README.md"
        ]
    }
    
    update_structure(desired, current, tmp_path)
    
    # Verify nested structure created
    assert (tmp_path / "project").exists()
    assert (tmp_path / "project" / "src").exists()
    assert (tmp_path / "project" / "src" / "main.py").exists()
    assert (tmp_path / "project" / "README.md").exists()


# Test 6: Update with real structures from builder
def test_update_builder_created_structure(tmp_path):
    """Test updating a structure created by builder."""
    # Create initial structure
    initial = load_structure("tests/fixtures/valid_simple.yaml")
    create_structure(initial, tmp_path)
    
    # Get root folder
    root = list(initial.keys())[0].rstrip('/')
    
    # Add user file (unmanaged)
    (tmp_path / root / "user_file.txt").touch()
    
    # Scan current structure
    from yark.scanner import scan_existing_structure
    current = scan_existing_structure(tmp_path / root)
    
    # Update to different structure
    desired = load_structure("tests/fixtures/valid_nested.yaml")
    desired_content = list(desired.values())[0]
    
    # Managed paths (only original files, not user_file)
    from yark.state import flatten_structure
    managed = set(flatten_structure(initial, ""))
    
    # Update
    update_structure(desired_content, current, tmp_path / root, 
                    managed_paths=managed)
    
    # Verify user file still exists
    assert (tmp_path / root / "user_file.txt").exists()


# Test 7: Update handles both creates and deletes
def test_update_creates_and_deletes(tmp_path):
    """Test that update can create and delete in same operation."""
    # Create initial files
    (tmp_path / "project").mkdir()
    (tmp_path / "project" / "old.txt").touch()
    
    # Current: has old.txt
    current = {"project/": ["old.txt"]}
    
    # Desired: has new.txt (old.txt removed)
    desired = {"project/": ["new.txt"]}
    
    # Managed
    managed = {"project/", "project/old.txt"}
    
    # Update
    update_structure(desired, current, tmp_path, managed_paths=managed)
    
    # Verify
    assert not (tmp_path / "project" / "old.txt").exists()  # Deleted
    assert (tmp_path / "project" / "new.txt").exists()      # Created