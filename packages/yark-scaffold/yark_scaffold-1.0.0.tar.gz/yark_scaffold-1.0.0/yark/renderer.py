from typing import Any, Dict, List, Optional, Tuple, Union

from rich.console import Console
from rich.tree import Tree

console = Console(force_terminal=True, color_system="auto")


def render_tree(
    structure: Union[Dict[str, Any], List[Any]], 
    tree: Optional[Tree] = None
) -> Optional[Tree]:
    """
    Render a nested project structure as a Rich tree.
    
    Handles CREATE/DELETE markers with colored backgrounds for visual distinction
    of changes. Supports nested dictionaries and lists representing folders and files.
    
    Parameters
    ----------
    structure : Union[Dict[str, Any], List[Any]]
        The structure to render. Can be a dict (folder contents) or list (items).
        Supports markers "CREATE" and "DELETE" for changed items.
    tree : Optional[Tree], optional
        Parent tree node for recursive rendering. If None, creates root tree.
        Default is None.
    
    Returns
    -------
    Optional[Tree]
        Rich Tree object ready for printing, or None if structure is invalid.
    
    Notes
    -----
    Color scheme:
    - CREATE items: Green background
    - DELETE items: Red background with strikethrough
    - Folders: Blue bold text
    - Unchanged items: Default styling
    
    Examples
    --------
    >>> structure = {"project/": ["file.py", {"src/": ["main.py"]}]}
    >>> tree = render_tree(structure)
    >>> console.print(tree)
    """
    if tree is None:
        if not isinstance(structure, dict) or len(structure) != 1:
            return None
        root_name: str
        contents: Any
        root_name, contents = next(iter(structure.items()))
        tree = Tree(f"📁 [bold blue]{root_name}[/bold blue]")
    else:
        contents = structure

    if isinstance(contents, dict):
        iterable: List[Tuple[str, Any]] = list(contents.items())
    elif isinstance(contents, list):
        iterable = []
        for item in contents:
            if isinstance(item, dict):
                name, value = next(iter(item.items()))
                iterable.append((name, value))
            else:
                iterable.append((item, None))
    else:
        return tree

    for name, value in iterable:
        is_folder: bool = name.endswith("/") or isinstance(value, (dict, list))
        icon: str = "📁" if is_folder else "📄"
        
        # Check for status markers
        if isinstance(value, str) and value == "CREATE":
            # Green background for new items
            tree.add(f"{icon} [black on green]{name}[/black on green]")
        elif isinstance(value, str) and value == "DELETE":
            # Red background + strikethrough for deleted items
            tree.add(f"{icon} [white on red strike]{name}[/white on red strike]")
        elif isinstance(value, (dict, list)):
            # Nested structure
            if is_folder:
                subtree: Tree = tree.add(f"{icon} [bold blue]{name}[/bold blue]")
            else:
                subtree = tree.add(f"{icon} {name}")
            render_tree(value, subtree)
        else:
            # Unchanged item
            if is_folder:
                tree.add(f"{icon} [bold blue]{name}[/bold blue]")
            else:
                tree.add(f"{icon} {name}")

    return tree


def print_tree(structure: Union[Dict[str, Any], List[Any]]) -> None:
    """
    Print the Rich tree to console.
    
    Renders and prints a visual tree representation of the project structure
    to the console with colors and formatting.
    
    Parameters
    ----------
    structure : Union[Dict[str, Any], List[Any]]
        The structure to print. Must be compatible with render_tree().
    
    Returns
    -------
    None
        Prints directly to console, returns nothing.
    
    Notes
    -----
    Works for three main use cases:
    - create: Shows structure to be created
    - update: Shows changes with colors (CREATE/DELETE markers)
    - list: Shows current structure
    
    Examples
    --------
    >>> structure = {"project/": ["README.md", "src/"]}
    >>> print_tree(structure)
    📁 project/
    ├── 📄 README.md
    └── 📁 src/
    """
    tree: Optional[Tree] = render_tree(structure)
    if tree is None:
        console.print("[yellow]Empty or invalid structure[/yellow]")
    else:
        console.print(tree)