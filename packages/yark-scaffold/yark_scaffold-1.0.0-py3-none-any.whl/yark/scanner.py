from pathlib import Path
from typing import Any, Dict, Optional, Set, Union

from yark.logger import get_logger


def scan_existing_structure(
    root_path: Union[str, Path], 
    ignore: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """
    Recursively scan and return the directory structure at root_path.
    
    Walks through the filesystem starting at root_path and builds a nested
    dictionary representation of all folders and files, skipping ignored items.
    
    Parameters
    ----------
    root_path : Union[str, Path]
        The root directory to scan. Can be a string path or Path object.
    ignore : Optional[Set[str]], optional
        Set of file/folder names to skip during scanning.
        Default is {'.git', '.DS_Store'} if None.
    
    Returns
    -------
    Dict[str, Any]
        Nested dictionary representing the structure:
        - Keys: folder names (ending with '/') or file names
        - Values: nested dict for folders (with their contents),
                  None for files
        Empty dict if root_path doesn't exist.
    
    Examples
    --------
    >>> structure = scan_existing_structure("./project")
    >>> print(structure)
    {
        'src/': {
            'main.py': None,
            'utils.py': None
        },
        'README.md': None
    }
    
    Notes
    -----
    - Folder keys always end with '/'
    - File values are always None
    - Recursively scans subdirectories
    - Returns empty dict if path doesn't exist
    - Ignores .git and .DS_Store by default
    """
    logger = get_logger()
    root: Path = Path(root_path)
    
    if ignore is None:
        ignore = {".git", ".DS_Store", ".yark.state"}
    
    tree: Dict[str, Any] = {}
    
    if not root.exists():
        logger.warning(f"Path does not exist: {root}")
        return tree
    
    if not root.is_dir():
        logger.warning(f"Path is not a directory: {root}")
        return tree
    
    for item in root.iterdir():
        if item.name in ignore:
            logger.debug(f"Ignoring: {item.name}")
            continue
            
        if item.is_dir():
            tree[item.name + "/"] = scan_existing_structure(item, ignore)
        else:
            tree[item.name] = None
    
    return tree