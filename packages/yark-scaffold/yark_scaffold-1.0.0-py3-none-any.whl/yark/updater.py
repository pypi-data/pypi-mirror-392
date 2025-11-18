import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Set

from yark.logger import get_logger


def update_structure(
    updated_structure: dict,
    current_structure: dict,
    root_path: Path = Path("."),
    dry_run: bool = False,
    managed_paths: Optional[Set[str]] = None,
    prefix: str = "",
) -> Optional[Dict[str, Any]]:
    """
    Update the filesystem to match updated_structure from current_structure.
    
    Only modifies resources that are in managed_paths (if provided). This ensures
    that user-created files and directories are not accidentally deleted.
    
    Parameters
    ----------
    updated_structure : dict
        The desired structure from YAML representing the target state.
    current_structure : dict
        The current filesystem structure from scanning.
    root_path : Path, optional
        The root directory path where updates are applied. Default is current directory.
    dry_run : bool, optional
        If True, returns a dict of planned changes without modifying filesystem.
        If False, applies changes and returns None. Default is False.
    managed_paths : Optional[Set[str]], optional
        Set of paths that Yark is allowed to modify/delete. Paths not in this set
        are ignored. If None, all paths can be modified. Default is None.
    prefix : str, optional
        Internal parameter for tracking full paths during recursion. Default is "".
    
    Returns
    -------
    Optional[Dict[str, Any]]
        If dry_run=True: Dictionary with structure changes marked as "CREATE" or "DELETE"
        If dry_run=False: None
    
    Raises
    ------
    RuntimeError
        If file operations fail due to permissions or OS errors.
    
    Notes
    -----
    - Only deletes files/directories that are in managed_paths
    - Creates new files/directories from updated_structure
    - Recursively processes nested structures
    """
    changes: Dict[str, Any] = {}
    logger = get_logger()
    
    def to_dict(struct: Any) -> dict:
        """Convert list-based structure to dict for uniform handling."""
        if isinstance(struct, list):
            d: dict = {}
            for item in struct:
                if isinstance(item, dict):
                    d.update(item)
                else:
                    d[item] = None
            return d
        return struct or {}

    updated_structure = to_dict(updated_structure)
    current_structure = to_dict(current_structure)
    all_keys: Set[str] = set(updated_structure) | set(current_structure)

    for key in all_keys:
        updated_val: Any = updated_structure.get(key)
        current_val: Any = current_structure.get(key)
        path: Path = root_path / key
        full_path: str = prefix + key

        # Directory case
        if isinstance(updated_val, dict) or isinstance(current_val, dict):
            if updated_val and not current_val:
                if dry_run:
                    changes[key] = "CREATE"
                else:
                    try:
                        logger.info(f"Creating directory: {path}")
                        path.mkdir(parents=True, exist_ok=True)
                        update_structure(
                            updated_val, {}, path, dry_run, managed_paths, prefix + key
                        )
                    except PermissionError as e:
                        logger.error(f"Permission denied creating directory: {path}")
                        raise RuntimeError(f"Permission denied: {path}") from e
                    except OSError as e:
                        logger.error(f"Failed to create directory {path}: {e}")
                        raise RuntimeError(f"Failed to create directory: {path}") from e
                        
            elif current_val and not updated_val:
                if managed_paths is None or full_path in managed_paths:
                    if dry_run:
                        changes[key] = "DELETE"
                    else:
                        try:
                            logger.info(f"Deleting directory: {path}")
                            shutil.rmtree(path)
                        except PermissionError as e:
                            logger.error(f"Permission denied deleting directory: {path}")
                            raise RuntimeError(f"Permission denied: {path}") from e
                        except OSError as e:
                            logger.error(f"Failed to delete directory {path}: {e}")
                            raise RuntimeError(f"Failed to delete directory: {path}") from e
            else:
                # Both exist, recurse
                nested_changes: Optional[Dict[str, Any]] = update_structure(
                    updated_val or {},
                    current_val or {},
                    path,
                    dry_run,
                    managed_paths,
                    prefix + key,
                )
                if nested_changes:
                    changes[key] = nested_changes

        # File case
        else:
            if key in updated_structure and key not in current_structure:
                if dry_run:
                    changes[key] = "CREATE"
                else:
                    try:
                        logger.info(f"Creating file: {path}")
                        path.touch(exist_ok=False)
                    except PermissionError as e:
                        logger.error(f"Permission denied creating file: {path}")
                        raise RuntimeError(f"Permission denied: {path}") from e
                    except FileExistsError as e:
                        logger.error(f"File already exists: {path}")
                        raise RuntimeError(f"File already exists: {path}") from e
                    except OSError as e:
                        logger.error(f"Failed to create file {path}: {e}")
                        raise RuntimeError(f"Failed to create file: {path}") from e
                        
            elif key in current_structure and key not in updated_structure:
                if managed_paths is None or full_path in managed_paths:
                    if dry_run:
                        changes[key] = "DELETE"
                    else:
                        try:
                            logger.info(f"Deleting file: {path}")
                            path.unlink()
                        except PermissionError as e:
                            logger.error(f"Permission denied deleting file: {path}")
                            raise RuntimeError(f"Permission denied: {path}") from e
                        except FileNotFoundError as e:
                            logger.error(f"File not found: {path}")
                            raise RuntimeError(f"File not found: {path}") from e
                        except OSError as e:
                            logger.error(f"Failed to delete file {path}: {e}")
                            raise RuntimeError(f"Failed to delete file: {path}") from e

    return changes if dry_run else None