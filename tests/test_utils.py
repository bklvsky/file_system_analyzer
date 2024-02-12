import os
import pytest
from analyzer.utils import file_size, unusual_permissions, normalize_path


def test_file_size():
    assert file_size(0) == "0 B"
    assert file_size(1) == "1.0 B"
    assert file_size(1024) == "1.0 KB"
    assert file_size(1024 * 1024) == "1.0 MB"
    assert file_size(1024 * 1024 * 1024) == "1.0 GB"
    assert file_size(1024 * 1024 * 1024 * 1024) == "1024.0 GB"


def test_unusual_permissions():
    assert unusual_permissions(0o777) == "world writable"
    assert unusual_permissions(0o4644) == "setuid"
    assert unusual_permissions(0o2644) == "setgid"
    assert unusual_permissions(0o000) == "no permissions"
    assert unusual_permissions(0o644) == None


def test_normalize_path():
    # Test absolute path
    assert normalize_path("/home/user/Documents") == "/home/user/Documents"

    # Test relative path
    assert (normalize_path("./data.txt")) == os.path.abspath("./data.txt")

    # Test relative path with parent directory
    assert (
        normalize_path("../data.txt", "/home/user/Documents") == "/home/user/data.txt"
    )

    # Test path with tilde expansion
    assert normalize_path("~/Documents") == f"{os.path.expanduser('~')}/Documents"

    # Test path with parent directory and tilde expansion
    assert (
        normalize_path("~/Downloads", "/home/user/Documents")
        == f"{os.path.expanduser('~')}/Downloads"
    )
