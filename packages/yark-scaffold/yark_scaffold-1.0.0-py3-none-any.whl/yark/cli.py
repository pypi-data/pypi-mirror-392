import argparse
import json
import sys
from pathlib import Path

from yark.builder import create_structure
from yark.logger import setup_logger
from yark.parser import load_structure
from yark.renderer import print_tree
from yark.scanner import scan_existing_structure
from yark.state import flatten_structure
from yark.updater import update_structure
from yark.utils import merge_tree_with_changes
from yark import __version__


def main():
    parser = argparse.ArgumentParser(
        prog="yark", description="Yark: YAML-based directory scaffolding tool"
    )
    parser.add_argument("--version", action="version", version=f"yark {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create
    create_parser = subparsers.add_parser(
        "create", help="Create a new directory structure from YAML"
    )
    create_parser.add_argument(
        "-f", "--file",
        dest="yaml_file",
        required=True,
        help="Path to YAML structure file")
    create_parser.add_argument(
        "-p", "--path",
        dest="path",
        default=".",
        help="Target directory (default: current directory)",
    )
    create_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without creating anything",
    )

    # update
    update_parser = subparsers.add_parser(
        "update", help="Update existing structure to match YAML"
    )
    update_parser.add_argument(
        "-f", "--file",
        dest="yaml_file",
        required=True,
        help="Path to YAML structure file")
    update_parser.add_argument(
        "-p", "--path",
        dest="path",
        default=".",
        help="Target directory (default: current directory)",
    )
    update_parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without applying them"
    )

    # list
    list_parser = subparsers.add_parser(
        "list", help="Display current directory structure (tree view)"
    )
    list_parser.add_argument(
        "-p", "--path",
        nargs="?",
        default=".",
        help="Directory to list (default: current directory)",
    )

    args = parser.parse_args()
    
    logger = setup_logger()
    logger.info("yark started")
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "create":
            print(f"Creating structure from {args.yaml_file}")
            logger.info(f"Creating structure from {args.yaml_file}")
            desired = load_structure(args.yaml_file)
            target_path = Path(args.path)

            if args.dry_run:
                print(f"[DRY RUN] Structure to be created in '{target_path}':\n")
                wrapped_tree = {target_path.name + "/": desired}
                print_tree(wrapped_tree)
                print(f"\n✓ All items will be created")
            else:
                create_structure(desired, args.path)
                print(f"✓ Structure created successfully in {target_path}")
                logger.info(f"✓ Structure created successfully in {target_path}")
                all_paths = flatten_structure(desired, "")
                state = {"managed_resources": {}}
                for path in all_paths:
                    state["managed_resources"][path] = {}
                state_file_path = Path(args.path) / ".yark.state"
                with open(state_file_path, "w") as f:
                    json.dump(state, f, indent=2)

        elif args.command == "update":
            print(f"Updating structure from {args.yaml_file}")
            logger.info(f"Updating structure from {args.yaml_file}")
            desired = load_structure(args.yaml_file)
            current = scan_existing_structure(args.path)
            target_path = Path(args.path)

            # Load state
            state_file = target_path / ".yark.state"
            if not state_file.exists():
                print("Error: No state file found. Use 'yark create' first.", file=sys.stderr)
                logger.error("State file not found")
                sys.exit(1)

            with open(state_file, "r") as f:
                state_data = json.load(f)

            managed_paths = set(state_data["managed_resources"].keys())

            if args.dry_run:
                print(f"[DRY RUN] Preview of changes in '{target_path}':\n")

                diff_tree = update_structure(
                    desired,
                    current,
                    root_path=target_path,
                    dry_run=True,
                    managed_paths=managed_paths,
                )

                display_tree = merge_tree_with_changes(desired, diff_tree or {})
                wrapped_tree = {target_path.name + "/": display_tree}
                print_tree(wrapped_tree)

                if not diff_tree:
                    print("\n✓ No changes required. Structure already matches YAML.")
                    logger.info("✓ No changes required. Structure already matches YAML.")
                else:
                    # Count changes
                    def count_changes(tree):
                        creates = deletes = 0
                        if isinstance(tree, dict):
                            for k, v in tree.items():
                                if v == "CREATE":
                                    creates += 1
                                elif v == "DELETE":
                                    deletes += 1
                                elif isinstance(v, dict):
                                    c, d = count_changes(v)
                                    creates += c
                                    deletes += d
                        return creates, deletes

                    creates, deletes = count_changes(diff_tree)
                    print(f"\nChanges: {creates} to create, {deletes} to delete")
                    logger.info(f"Changes: {creates} to create, {deletes} to delete")
            else:
                # Apply changes
                update_structure(
                    desired,
                    current,
                    root_path=target_path,
                    dry_run=False,
                    managed_paths=managed_paths,
                )

                # Update state file
                new_managed = set(flatten_structure(desired, ""))
                state_data["managed_resources"] = {path: {} for path in new_managed}

                with open(state_file, "w") as f:
                    json.dump(state_data, f, indent=2)
                print(f"✓ Structure updated successfully in '{target_path}'")
                logger.info(f"✓ Structure updated successfully in '{target_path}'")

        elif args.command == "list":
            target_path = Path(args.path)

            if not target_path.exists():
                print(f"Error: Directory '{target_path}' does not exist")
                logger.error(f"Error: Directory '{target_path}' does not exist")
                sys.exit(1)

            structure = scan_existing_structure(args.path)
            if not structure:
                print(f"Directory '{target_path}' is empty")
                logger.info(f"Directory '{target_path}' is empty")
            else:
                wrapped_tree = {target_path.name + "/": structure}
                print_tree(wrapped_tree)

    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        logger.error(f"Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        logger.error("\nOperation cancelled by user")
        sys.exit(130)


if __name__ == "__main__":
    main()
