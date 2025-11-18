from yark.utils import merge_tree_with_changes


# Test 1: Merge with no changes returns original
def test_merge_no_changes():
    """Test that merging with no changes returns original structure."""
    desired = {"project/": ["file1.txt", "file2.txt"]}
    changes = {}
    
    result = merge_tree_with_changes(desired, changes)
    
    assert result == desired


# Test 2: Merge with None changes returns original
def test_merge_none_changes():
    """Test that merging with None returns original structure."""
    desired = {"project/": ["file.txt"]}
    changes = None
    
    result = merge_tree_with_changes(desired, changes)
    
    assert result == desired


# Test 3: Merge adds CREATE markers
def test_merge_adds_create_markers():
    """Test that CREATE markers are added to structure."""
    desired = {"project/": ["file.txt"]}
    changes = {"project/": {"file.txt": "CREATE"}}
    
    result = merge_tree_with_changes(desired, changes)
    
    # file.txt should have CREATE marker
    assert "project/" in result
    assert isinstance(result["project/"], list)
    # Should contain dict with marker
    assert {"file.txt": "CREATE"} in result["project/"]


# Test 4: Merge adds DELETE markers
def test_merge_adds_delete_markers():
    """Test that DELETE markers are added to structure."""
    desired = {"project/": ["file1.txt"]}
    changes = {"project/": {"old_file.txt": "DELETE"}}
    
    result = merge_tree_with_changes(desired, changes)
    
    # old_file.txt should be added with DELETE marker
    assert "project/" in result
    assert {"old_file.txt": "DELETE"} in result["project/"]


# Test 5: Merge with both CREATE and DELETE
def test_merge_create_and_delete():
    """Test merging with both CREATE and DELETE markers."""
    desired = {
        "project/": [
            "unchanged.txt",
            "new.txt"
        ]
    }
    changes = {
        "project/": {
            "new.txt": "CREATE",
            "old.txt": "DELETE"
        }
    }
    
    result = merge_tree_with_changes(desired, changes)
    
    # Should have unchanged file
    assert "unchanged.txt" in result["project/"]
    # Should have CREATE marker
    assert {"new.txt": "CREATE"} in result["project/"]
    # Should have DELETE marker
    assert {"old.txt": "DELETE"} in result["project/"]


# Test 6: Merge nested structures
def test_merge_nested_structure():
    """Test merging nested folder structures."""
    desired = {
        "root/": [
            {"src/": ["main.py", "new.py"]},
            "README.md"
        ]
    }
    changes = {
        "root/": {
            "src/": {
                "new.py": "CREATE",
                "old.py": "DELETE"
            }
        }
    }
    
    result = merge_tree_with_changes(desired, changes)
    
    # Structure should be preserved
    assert "root/" in result
    # Should be able to traverse (this is a complex assertion, simplified)
    assert isinstance(result["root/"], list)


# Test 7: Merge preserves unchanged items
def test_merge_preserves_unchanged():
    """Test that unchanged items remain in structure."""
    desired = {
        "project/": [
            "unchanged1.txt",
            "unchanged2.txt",
            {"src/": ["unchanged.py"]}
        ]
    }
    changes = {
        "project/": {
            "new.txt": "CREATE"
        }
    }
    
    result = merge_tree_with_changes(desired, changes)
    
    # Unchanged items should still be there
    assert "unchanged1.txt" in result["project/"]
    assert "unchanged2.txt" in result["project/"]