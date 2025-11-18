from pathlib import Path
from typing import Any, Union

from yaml import YAMLError, safe_load

from yark.logger import get_logger


def load_structure(yaml_path: Union[str, Path]) -> dict:
    """
    Load and validate the structure of a YAML file.
    
    Reads a YAML file, parses it, and validates that it conforms to the expected
    structure format for Yark (folders ending with '/', containing lists or dicts).
    
    Parameters
    ----------
    yaml_path : Union[str, Path]
        Path to the YAML file to load.
    
    Returns
    -------
    dict
        Parsed YAML content as a dictionary if valid.
    
    Raises
    ------
    RuntimeError
        If the file cannot be read or YAML parsing fails.
    ValueError
        If the YAML content is empty, not a dictionary, or fails validation.
    
    Examples
    --------
    >>> structure = load_structure("project.yaml")
    >>> print(structure)
    {'src/': ['main.py', 'utils.py']}
    """
    logger = get_logger()
    logger.info(f"Loading YAML structure from: {yaml_path}")
    
    try:
        with open(yaml_path, "r") as stream:
            structure: Any = safe_load(stream)
            
            if not structure:
                logger.error("YAML file is empty or invalid")
                raise ValueError("YAML file is empty or invalid.")
            
            if not isinstance(structure, dict):
                logger.error(f"Invalid YAML root type: expected dict, got {type(structure).__name__}")
                raise ValueError(
                    f"Invalid YAML root type: expected a dictionary, got {type(structure).__name__}"
                )
            
            __validate_structure(structure)
            logger.info("YAML structure validated successfully")
            return structure
            
    except (FileNotFoundError, YAMLError) as exc:
        logger.error(f"Failed to load YAML: {exc}")
        raise RuntimeError(f"Failed to load YAML: {exc}")


def __validate_structure(structure: dict, path: str = "") -> None:
    """
    Recursively validate the folder/file structure in the YAML dictionary.
    
    Ensures that:
    - All folder keys end with '/'
    - Folder values are lists or dicts
    - List items are either strings (files) or dicts (nested folders)
    
    Parameters
    ----------
    structure : dict
        The YAML dictionary to validate.
    path : str, optional
        Current nested path for error messages (used internally during recursion).
        Default is "".
    
    Returns
    -------
    None
        Returns nothing if structure is valid.
    
    Raises
    ------
    ValueError
        If the structure contains invalid keys, values, or nested items.
        - Keys must be folder names ending with '/'
        - Values must be lists or dictionaries
        - List items must be strings (files) or dicts (folders)
    
    Notes
    -----
    This is an internal validation function called by load_structure().
    It performs recursive validation of nested folder structures.
    """
    if not structure:
        raise ValueError("The YAML File is Empty.")
    
    for key, value in structure.items():
        if isinstance(key, str) and key.endswith("/"):
            new_path: str = (
                path + key if path.endswith("/") or path == "" else path + "/" + key
            )
            
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        __validate_structure(item, new_path)
                    elif isinstance(item, str):
                        continue
                    else:
                        raise ValueError(
                            f"Invalid item '{item}' in folder '{key}' at '{new_path}': "
                            f"expected a folder (dict) or filename (str), got {type(item).__name__}"
                        )
            elif isinstance(value, dict):
                __validate_structure(value, new_path)
            else:
                raise ValueError(
                    f"Invalid value for folder '{key}' at '{new_path}': "
                    f"expected list or dict, got {type(value).__name__}"
                )
        else:
            raise ValueError(
                f"Invalid key '{key}' at '{path}': folder keys must end with '/'"
            )