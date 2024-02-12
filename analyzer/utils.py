import os


def file_size(size: int) -> str:
    """
    Convert a file size in bytes to a human-readable format.

    Args:
        size (int): Size of the file in bytes.

    Returns:
        str: Human-readable representation of the file size.
    """
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}

    if size == 0:
        return "0 B"
    for unit, threshold in units.items():
        if size // threshold < 1024 and size // threshold > 0:
            return f"{size / threshold :.1f} {unit}"
    size /= units["GB"]
    return f"{size} GB"


def unusual_permissions(mode: int) -> str:
    """
    Check for unusual file permissions based on the mode bits.

    Args:
        mode (int): File mode bits representing permissions.

    Returns:
        str: Description of unusual permissions, if any.
    """
    if mode & 0o777 == 0:
        return "no permissions"
    if mode & 0o4000 != 0:
        return "setuid"
    if mode & 0o2000 != 0:
        return "setgid"
    if mode & 0o2 != 0:
        return "world writable"


def normalize_path(path: str, parent_dir: str = "") -> str:
    """
    Normalize a given file or directory path.

    This method normalizes the given 'path' by expanding any tilde characters ('~'),
    resolving relative paths, and ensuring the path is absolute. If the 'parent_dir'
    parameter is provided, it is used to resolve paths relative to the parent directory.

    Args:
        path (str): The file or directory path to normalize.
        parent_dir (str, optional): The path of the parent directory. Required when
            the 'path' is not in the same directory as the parent. Defaults to "".

    Returns:
        str: The normalized absolute path.

    Examples:
        >>> normalize_path("~/Documents")
        '/home/user/Documents'
        >>> normalize_path("../data.txt", "/home/user/Documents")
        '/home/user/data.txt'
    """
    # Expand any tilde characters and resolve relative paths
    path = os.path.expanduser(path)

    # Join the parent directory and path if parent_dir is provided, else return the absolute path
    path = os.path.join(parent_dir, path)
    return os.path.abspath(path)
