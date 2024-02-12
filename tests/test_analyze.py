import pytest
import stat
import os

from analyzer.analyze import Analyzer


@pytest.fixture
def empty_analyzer():
    analyzer = Analyzer()
    yield analyzer
    analyzer.close()


@pytest.fixture
def flags_analyzer(tmp_path):
    analyzer = Analyzer(
        threshold=10,
        unusual_perm_out=str(tmp_path / "report.txt"),
        big_files_out=str(tmp_path / "big_files_report.txt"),
    )
    yield analyzer
    analyzer.close()


@pytest.fixture
def tmp_symlink(tmp_path):
    # Create a target file
    target_file = tmp_path / "target_file.txt"
    target_file.write_text("This is the target file")

    # Create a symbolic link
    symlink = tmp_path / "symbolic_link"
    os.symlink(target_file, symlink)

    yield symlink

    # Cleanup: Remove the symbolic link and target file
    os.remove(symlink)
    os.remove(target_file)


@pytest.fixture
def tmp_directory(tmp_path):
    # Create a temporary directory
    tmp_dir = tmp_path / "test_directory"
    tmp_dir.mkdir()
    yield tmp_dir
    # Clean up: delete the temporary directory
    tmp_dir.rmdir()


def testadd(tmp_path, tmp_directory, capsys):
    analyzer = Analyzer(threshold=10)

    # Test with a directory

    analyzer.add(str(tmp_directory))
    assert analyzer._type_size_count == {"directories": 4096}

    # Test with a regular file

    file = tmp_path / "test.txt"
    with open(file, "w") as f:
        f.write("test")  # Write 4 bytes into a file
    analyzer.add(file)
    assert analyzer._type_size_count["text"] == 4  # Size of the file is 4 bytes

    # Test with a big file

    big_file = tmp_path / "big.txt"
    with open(big_file, "w") as f:
        f.write("A" * 20)  # write 20 bytes, more than threshold
    analyzer.add(str(big_file))
    captured = capsys.readouterr()
    assert f"{big_file}: 20.0 B\n" in captured.out

    # Test with an file with no reading permissions

    forbidden_path = tmp_path / "forbidden.unknown"
    with open(forbidden_path, "w") as f:
        f.write("test")

    os.chmod(forbidden_path, 0o000)  # Set file permissions to 000
    analyzer.add(str(forbidden_path))
    # won't be able to read the file so it will add 'uknown' to list of types based on extension
    assert "unknown" in analyzer._type_size_count

    analyzer.close()


def test_add_link(tmp_symlink):
    # Test adding a symbolic links
    analyzer = Analyzer()
    analyzer.add_link(str(tmp_symlink))

    assert analyzer._type_size_count == {"symlink": os.lstat(str(tmp_symlink)).st_size}
    analyzer.close()


def test_print_summary(capsys, empty_analyzer):
    # Create an analyzer with some data
    empty_analyzer._type_size_count["text"] = 1024  # 1 KB
    empty_analyzer._type_size_count["application"] = 2048  # 2 KB

    # Print the summary
    empty_analyzer.print_summary()

    # Check if the summary was printed correctly
    captured = capsys.readouterr()
    assert "text: 1.0 KB.\n" in captured.out
    assert "application: 2.0 KB.\n" in captured.out


def test_close(flags_analyzer, tmp_path):
    # Close the analyzer
    flags_analyzer.close()

    # Check if the output files are closed
    assert flags_analyzer._up_out.closed
    assert flags_analyzer._bf_out.closed
