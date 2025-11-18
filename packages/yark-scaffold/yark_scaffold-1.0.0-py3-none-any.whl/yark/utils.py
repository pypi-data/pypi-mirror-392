import copy
from typing import Any, Dict, List, Optional, Union


def merge_tree_with_changes(
    desired: Dict[str, Any], 
    changes: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Annotate desired structure with change markers from update diff.
    
    Overlays CREATE and DELETE markers from the changes dict onto the desired
    structure, creating a merged view that shows what will be created, deleted,
    and what remains unchanged.
    
    Parameters
    ----------
    desired : Dict[str, Any]
        The desired structure from YAML. Represents the target state with all
        folders and files that should exist.
    changes : Optional[Dict[str, Any]]
        The changes dict from update_structure's dry-run. Contains "CREATE" and
        "DELETE" markers for items that will change. Can be None or empty dict.
    
    Returns
    -------
    Dict[str, Any]
        Copy of desired structure with change markers overlaid:
        - Items marked "CREATE" will have value "CREATE"
        - Items marked "DELETE" will be added with value "DELETE"
        - Unchanged items retain their original structure
    
    Examples
    --------
    >>> desired = {"src/": ["main.py", "utils.py"]}
    >>> changes = {"src/": {"new.py": "CREATE", "old.py": "DELETE"}}
    >>> result = merge_tree_with_changes(desired, changes)
    >>> print(result)
    {
        'src/': [
            'main.py',
            'utils.py',
            {'new.py': 'CREATE'},
            {'old.py': 'DELETE'}
        ]
    }
    
    Notes
    -----
    - Does not modify input structures (creates deep copy)
    - Handles nested dicts and lists
    - Adds DELETE items even if not in desired structure
    - Used for dry-run visualization in update command
    """
    if not changes:
        return desired
    
    result: Dict[str, Any] = copy.deepcopy(desired)
    
    def annotate(node: Dict[str, Any], change_dict: Dict[str, Any]) -> None:
        """
        Recursively annotate a dict node with change markers.
        
        Parameters
        ----------
        node : Dict[str, Any]
            The dict node to annotate (modified in-place).
        change_dict : Dict[str, Any]
            Changes to apply to this node.
        """
        if not isinstance(node, dict) or not isinstance(change_dict, dict):
            return
        
        for key, value in list(node.items()):
            if key in change_dict:
                change_val: Any = change_dict[key]
                if change_val in ("CREATE", "DELETE"):
                    node[key] = change_val
                elif isinstance(change_val, dict):
                    if isinstance(value, dict):
                        annotate(value, change_val)
                    elif isinstance(value, list):
                        # Pass ONLY nested changes for this key
                        annotate_list(node, key, value, change_val)
            elif isinstance(value, dict):
                # No changes for this key, don't pass change_dict down
                pass
            elif isinstance(value, list):
                # No changes for this key, don't pass change_dict down
                pass
        
        # Add deletions at this level
        for key, value in change_dict.items():
            if key not in node and value == "DELETE":
                node[key] = value
    
    def annotate_list(
        parent_node: Dict[str, Any], 
        parent_key: str, 
        lst: List[Any], 
        change_dict: Dict[str, Any]
    ) -> None:
        """
        Annotate list items with change markers.
        
        Parameters
        ----------
        parent_node : Dict[str, Any]
            The parent dict containing this list (not used, kept for signature).
        parent_key : str
            The key in parent_node that contains this list (not used, kept for signature).
        lst : List[Any]
            The list to annotate (modified in-place).
        change_dict : Dict[str, Any]
            Changes for items in this list.
        """
        for i, item in enumerate(lst):
            if isinstance(item, str):
                # Check if this specific string has a marker
                if item in change_dict and change_dict[item] in ("CREATE", "DELETE"):
                    lst[i] = {item: change_dict[item]}
            elif isinstance(item, dict):
                # Nested dict in list - recurse with ONLY its changes
                for nested_key, nested_val in item.items():
                    if nested_key in change_dict and isinstance(
                        change_dict[nested_key], dict
                    ):
                        annotate(item, {nested_key: change_dict[nested_key]})
        
        # Add deletions ONLY for this list level
        for key, value in change_dict.items():
            if value == "DELETE":
                found: bool = any(
                    (
                        item == key
                        if isinstance(item, str)
                        else (key in item if isinstance(item, dict) else False)
                    )
                    for item in lst
                )
                if not found:
                    lst.append({key: "DELETE"})
    
    annotate(result, changes)
    return result