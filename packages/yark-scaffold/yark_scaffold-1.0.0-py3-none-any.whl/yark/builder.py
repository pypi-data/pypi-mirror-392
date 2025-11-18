from pathlib import Path
from typing import Iterable, Optional, Union

from yark.logger import get_logger


def create_structure(
    structure: dict, root_path: Optional[Union[str, Path]] = None
) -> None:
    """
    Create files and directories described by `structure` under `root_path`.
    Expected `structure` shape (flexible):
      - { "folder/": [ "file.txt", {"sub/": [...]} , ... ], ... }
      - { "folder/": { "sub/": [...] }, ... }
      - Keys may end with "/" (recommended) or not — they are treated as directories.
      - List items can be strings (filenames) or dicts (nested folders).
      - If a key does not represent a directory (no trailing slash and value is not list/dict),
        it will be created as a file.
    Parameters
    ----------
    structure:
        Mapping describing the tree to create.
    root_path:
        Where to create the tree. If None uses current working directory.
    Notes
    -----
    - This function is idempotent: it will not error if directories or files already exist.
    - Raises RuntimeError on permissions/OS errors.
    """
    if not isinstance(structure, dict):
        raise TypeError("structure must be a dict")

    logger = get_logger()
    base: Path = Path(root_path) if root_path is not None else Path.cwd()
    base = base.resolve()

    try:
        for key, value in structure.items():
            # normalize key: treat keys as directory names by default
            is_dir: bool = isinstance(value, (dict, list)) or str(key).endswith("/")
            name: str = str(key).rstrip("/")
            target: Path = base / name

            if is_dir:
                # create directory
                logger.info(f"Creating directory: {target}")
                target.mkdir(parents=True, exist_ok=True)

                # handle different value shapes
                if value is None:
                    continue
                if isinstance(value, dict):
                    # nested mapping: recurse with the nested dict
                    create_structure(value, target)
                elif isinstance(value, list) or isinstance(value, Iterable):
                    for item in value:
                        if isinstance(item, str):
                            file_path: Path = target / item
                            file_path.parent.mkdir(parents=True, exist_ok=True)
                            logger.info(f"Creating file: {file_path}")
                            file_path.touch(exist_ok=True)
                        elif isinstance(item, dict):
                            # nested folder described as dict inside the list
                            create_structure(item, target)
                        else:
                            # ignore unsupported types; could also raise ValueError
                            raise ValueError(
                                f"Unsupported item type in list for '{key}': {type(item).__name__}"
                            )
                else:
                    # unexpected type for a directory value
                    raise ValueError(
                        f"Unsupported value type for directory '{key}': {type(value).__name__}"
                    )
            else:
                # treat as file
                target.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"Creating file: {target}")
                target.touch(exist_ok=True)

    except PermissionError as e:
        logger.error(f"Permission denied while creating structure under '{base}': {e}")
        raise RuntimeError(
            f"Permission denied while creating structure under '{base}': {e}"
        ) from e
    except OSError as e:
        logger.error(f"OS error while creating structure under '{base}': {e}")
        raise RuntimeError(
            f"OS error while creating structure under '{base}': {e}"
        ) from e