from pathlib import Path
from typing import Any, Dict, List, Set, Union


def flatten_structure(structure: Dict[str, Any], prefix: str = "") -> List[str]:
    """
    Flatten a nested YAML structure into a list of all paths.
    
    Recursively walks through the structure dict and extracts all file and folder
    paths as strings with their full relative paths.
    
    Parameters
    ----------
    structure : Dict[str, Any]
        The nested structure to flatten. Keys are folder/file names, values are
        contents (lists, dicts, or None).
    prefix : str, optional
        Current path prefix for recursion. Used internally to build full paths.
        Default is "".
    
    Returns
    -------
    List[str]
        Flat list of all paths in the structure with full relative paths.
        Empty list if structure is None or empty.
    
    Examples
    --------
    >>> structure = {"src/": ["main.py", {"tests/": ["test.py"]}]}
    >>> paths = flatten_structure(structure)
    >>> print(paths)
    ['src/', 'src/main.py', 'src/tests/', 'src/tests/test.py']
    
    Notes
    -----
    - Folder paths end with '/'
    - File paths have no trailing '/'
    - Handles nested dicts (folders inside folders)
    - Handles lists (files and folders at same level)
    """
    if not structure:
        return []
    
    flattened_struct: List[str] = []
    
    for dir_name, files in structure.items():
        current_prefix: str = prefix + dir_name
        flattened_struct.append(current_prefix)
        
        if isinstance(files, list):
            for file in files:
                if isinstance(file, str):
                    flattened_struct.append(f"{current_prefix}{file}")
                elif isinstance(file, dict):
                    nested: List[str] = flatten_structure(file, prefix + dir_name)
                    flattened_struct.extend(nested)
                    
        elif isinstance(files, dict):
            nested = flatten_structure(files, prefix + dir_name)
            flattened_struct.extend(nested)
    
    return flattened_struct