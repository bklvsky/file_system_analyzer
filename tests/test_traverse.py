import os
import pytest
from unittest.mock import patch, MagicMock
from analyzer.traverse import manage_dir, manage_item, traverse_directory
from analyzer.analyze import Analyzer
from pathlib import Path
import shutil


@pytest.fixture
def empty_analyzer():
    analyzer = Analyzer()
    yield analyzer
    analyzer.close()


@pytest.fixture
def tmp_directory(tmp_path):
    # Create a temporary directory
    tmp_dir = tmp_path / "test_directory"
    tmp_dir.mkdir()
    yield tmp_dir
    # Clean up: delete the temporary directory


@pytest.fixture
def tmp_dir(tmp_path):
    # Create a temporary directory structure for testing
    dir_structure = {
        "dir1": {"file1.txt": "content", "dir2": {}},
    }
    create_dir_structure(tmp_path, dir_structure)
    Path(str(tmp_path / "symlink_dir")).symlink_to(Path(str(tmp_path / "dir1")))
    yield tmp_path

    shutil.rmtree(tmp_path)
    # return tmp_path


def create_dir_structure(base_path, structure):
    # Recursively create the directory structure
    for name, contents in structure.items():
        path = base_path / name
        if isinstance(contents, dict):
            path.mkdir()

            create_dir_structure(path, contents)
        else:
            with open(path, "w") as f:
                f.write(contents)


def test_manage_dir(tmp_directory, capsys):
    # Test managing a directory: add it to visited set and queue
    visited = set()
    queue = []
    dir_path = str(tmp_directory)
    manage_dir(tmp_directory, visited, queue)
    assert dir_path in visited
    assert dir_path in queue

    # Test symlink loop: if a directory is added the second time
    queue.pop()
    manage_dir(tmp_directory, visited, queue, "sym_link")
    captured = capsys.readouterr()
    assert (
        captured.err
        == f"Error: symlink loop detected at {dir_path}. Pointed by: sym_link.\n"
    )
    assert queue == []


def test_traverse_directory(capsys, tmp_dir, empty_analyzer):
    empty_analyzer = Analyzer()
    traverse_directory(tmp_dir, empty_analyzer, follow_links=True)

    # Check if directory traversal and analysis completed successfully
    assert (
        empty_analyzer._type_size_count != {}
    )  # Analyzer should have analyzed something
    assert "text" in empty_analyzer._type_size_count  # Ensure text files were analyzed

    # Check if the correct number of files and directories were analyzed
    expected_num_files = (
        2  # Number of text files and directories in the dir1/: 1 file and 1 directory
    )
    assert (
        len(empty_analyzer._type_size_count) == expected_num_files
    )  # Check number of file types analyzed

    # Check if the summary of file types and sizes is printed correctly
    empty_analyzer.print_summary()
    captured = capsys.readouterr()
    summary_output = captured.out
    assert (
        "text: 7.0 B" in summary_output
    )  # Ensure text files are included in the summary
    empty_analyzer.close()


def test_nonexistant_file(tmp_dir, capsys, empty_analyzer):
    empty_analyzer = Analyzer()
    nonexistant_file = str(tmp_dir / "not_exist.txt")
    Path(str(tmp_dir / "dir1" / "file_symlinks")).symlink_to(
        Path(nonexistant_file)
    )  # create symlink to nonexistent file

    traverse_directory(tmp_dir / "dir1", empty_analyzer, follow_links=True)
    captured = capsys.readouterr()
    file_path = str(tmp_dir / "dir1" / "file_symlinks")
    assert (
        f"Error: {nonexistant_file}: No such file or directory. Skipping.\n"
        in captured.err
    )
    os.chmod(tmp_dir / "dir1" / "file1.txt", 0o644)  # Restore file permissions
    empty_analyzer.close()


def test_no_permissions_directory(tmp_dir, capsys, empty_analyzer):
    empty_analyzer = Analyzer()
    #  Test unreadable directory:
    os.chmod(tmp_dir / "dir1", 0o222)  # Make directory unreadable
    traverse_directory(tmp_dir / "dir1", empty_analyzer, follow_links=True)
    captured = capsys.readouterr()
    assert (
        f"Error: {str(tmp_dir / 'dir1')}: Permission denied. Skipping directory.\n"
        in captured.err
    )
    assert (
        empty_analyzer._type_size_count == {}
    )  # No files should be visited if directory is forbidden
    empty_analyzer.close()
    # Restore directory permissions
    os.chmod(tmp_dir, 0o777)
    os.chmod(tmp_dir / "dir1", 0o777)  # Restore directory permissions
    os.chmod(tmp_dir / "dir1" / "file1.txt", 0o777)  # Restore file permissions


def test_nonexistent_directory(tmp_dir, capsys, empty_analyzer):
    empty_analyzer = Analyzer()
    # Test nonexistent directory:
    traverse_directory(tmp_dir / "nonexistent_dir", empty_analyzer)
    captured = capsys.readouterr()
    assert (
        f"Error: {str(tmp_dir / 'nonexistent_dir')}: No such file or directory. Skipping directory.\n"
        in captured
    )
