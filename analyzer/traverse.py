import os
import sys

from analyzer.analyze import Analyzer
from analyzer import utils


def manage_dir(path: str, visited: set, queue: list, sym_link: str = ""):
    """
    Manage a directory path.

    If the directory path has not been visited before, add it to the queue of directories to traverse.
    If the directory path has been visited before, print an error message indicating a symlink loop.

    Args:
        path (str): The directory path to manage.
        visited (set): A set containing visited directory paths.
        queue (list): A list representing the queue of directories to traverse.
        sym_link (str): A path to symbolic link that points to the directory.
                        If not the directory was not pointed by symlink, defaults to "".
    """
    path = os.path.abspath(path)
    if path not in visited:
        visited.add(path)
        queue.append(path)
    else:
        sym_link_str = f" Pointed by: {sym_link}." if sym_link else ""
        print(f"Error: symlink loop detected at {path}.{sym_link_str}", file=sys.stderr)


def manage_item(
    item: os.DirEntry, visited: set, queue: list, analyzer: Analyzer, follow_links=False
):
    """
    Manage an item (file or directory) encountered during directory traversal.

    This function is responsible for managing each item (file or directory) encountered
    during directory traversal. It determines the type of the item and takes appropriate
    actions based on its type:
        - If the item is a symbolic link, it resolves the symlink path,
          expands any '~' characters, and adds the resulting directory to queue or analyzes the file.
        - If the item is a directory, it adds the directory to the queue for further traversal.
        - If the item is a regular file, it analyzes the file using the provided 'analyzer' object.

    Args:
        item (os.DirEntry): The item encountered during traversal.
        visited (set): A set containing visited directory paths.
        queue (list): A list representing the queue of directories to traverse.
        analyzer (Analyzer): An instance of the Analyzer class for analyzing files.

    Returns:
        None
    """
    try:
        item_path = item.path
        if item.is_symlink():
            if follow_links:
                item_path = os.readlink(item)  # get a symbolic link
                item_path = utils.normalize_path(item_path, os.path.dirname(item.path))
                if os.path.isdir(item_path):
                    manage_dir(item_path, visited, queue, sym_link=item.path)
            else:
                analyzer.add_link(item_path)
                return
        elif item.is_dir():
            manage_dir(item_path, visited, queue)

        analyzer.add(item_path)
    except OSError or ValueError as e:
        print(f"Error: {e.filename}: {e.strerror}. Skipping.", file=sys.stderr)


def traverse_directory(directory: str, analyzer: Analyzer, follow_links=False):
    """
    Traverse a directory recursively and analyze its contents.

    Args:
        directory (str): an absolute path to the directory to traverse.
        analyzer (Analyzer): An instance of the Analyzer class for analyzing files.
    """
    visited = set()

    directory = utils.normalize_path(directory)
    queue = [directory]
    visited.add(directory)

    while queue:
        cur_dir = queue.pop(0)
        try:
            for item in os.scandir(cur_dir):
                manage_item(item, visited, queue, analyzer, follow_links=follow_links)

        except OSError as e:
            print(
                f"Error: {e.filename}: {e.strerror}. Skipping directory.",
                file=sys.stderr,
            )

    analyzer.print_summary()
