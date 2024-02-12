import argparse
import pytest
from analyzer import cli


@pytest.fixture
def tmp_directory(tmp_path):
    # Create a temporary directory
    tmp_dir = tmp_path / "test_directory"
    tmp_dir.mkdir()
    yield tmp_dir
    # Clean up: delete the temporary directory
    tmp_dir.rmdir()


@pytest.fixture
def tmp_file(tmp_path):
    # Create a temporary file
    tmp_file = tmp_path / f"{tmp_path}/test_file.txt"
    tmp_file.write_text("test")
    yield tmp_file
    # Clean up: delete the temporary file
    tmp_file.unlink()


def test_split_numerical_and_nonnumerical():
    # Test uppercase string without delimeter
    numerical, non_numerical = cli.split_numerical_and_nonnumerical("100KB")
    assert numerical == "100"
    assert non_numerical == "KB"

    # Test string without nonnumerical part
    numerical, non_numerical = cli.split_numerical_and_nonnumerical("100")
    assert numerical == "100"
    assert non_numerical == ""

    # Test invalid string without numerical part
    numerical, non_numerical = cli.split_numerical_and_nonnumerical("mb")
    assert numerical == None
    assert non_numerical == None


def test_parse_size():
    # Test with uppercase unit
    assert cli.parse_size(10, "KB") == 10240

    # Test with lowercase unit, delimited by whitespace
    assert cli.parse_size(100, "  mb") == 100 * 1024 * 1024

    # Test without unit provided
    assert cli.parse_size(100, "") == 100

    # Test with invalid unit
    with pytest.raises(argparse.ArgumentTypeError):
        cli.parse_size(100, "PB")


def test_size_type():
    assert cli.size_type("100KB") == 102400
    assert cli.size_type("1MB") == 1048576
    with pytest.raises(argparse.ArgumentTypeError):
        cli.size_type("invalid")
    with pytest.raises(argparse.ArgumentTypeError):
        cli.size_type("-10KB")


def test_get_args(monkeypatch, tmp_directory):
    # Test with valid directory
    monkeypatch.setattr(
        "sys.argv",
        [
            "script.py",
            str(tmp_directory),
            "-t",
            "10KB",
            "--report-big-files",
            "report.txt",
            "-f",
            "output.txt",
        ],
    )
    args = cli.get_args()
    assert args.path == str(tmp_directory)
    assert args.threshold == 10240
    assert args.report_big_files == "report.txt"
    assert args.report_file == "output.txt"
    assert args.follow_links == False

    # Test with follow_links flag
    monkeypatch.setattr("sys.argv", ["script.py", str(tmp_directory), "-l"])
    args = cli.get_args()
    assert args.follow_links == True


def test_valid_dir(tmp_directory, tmp_file):
    assert cli.valid_dir(str(tmp_directory))
    with pytest.raises(argparse.ArgumentTypeError) as exc:
        cli.valid_dir(str(tmp_file))
        assert str(exc.value) == f"Error: {str(tmp_directory)}: is not a directory."
    with pytest.raises(argparse.ArgumentTypeError):
        cli.valid_dir(str("nonexistent/directory"))
        assert str(exc.value) == f"Error: nonexistent/directory: doesn't exist."
