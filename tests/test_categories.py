import pytest
from analyzer.categories import Typer


@pytest.fixture
def typer_instance():
    return Typer()


@pytest.fixture
def tmp_file(tmp_path):
    # Create a temporary file
    tmp_file = tmp_path / f"{tmp_path}/test_file.txt"
    tmp_file.write_text("test")
    yield tmp_file
    # Clean up: delete the temporary file
    tmp_file.unlink()


@pytest.fixture
def tmp_empty_file(tmp_path):
    # Create a temporary file
    tmp_file = tmp_path / f"{tmp_path}/test_file.empty"
    tmp_file.touch()

    yield tmp_file
    # Clean up: delete the temporary file
    tmp_file.unlink()


def test_from_extension(typer_instance):
    # Test with text
    assert typer_instance.from_extension("file.txt") == "text"

    # Test with audio
    assert typer_instance.from_extension("file.mp3") == "audio"

    # Test with pdf
    assert typer_instance.from_extension("file.pdf") == "pdf"

    # Test eith archive
    assert typer_instance.from_extension("file.tar") == "archive"

    # Test with an executable
    assert typer_instance.from_extension("file.exe") == "executable"

    # Test with unknown file extension
    assert typer_instance.from_extension("file.file") == "unknown"


def test_from_signature_empty(typer_instance, tmp_empty_file):
    assert typer_instance.from_signature(str(tmp_empty_file)) == "unknown"


def test_from_signature(typer_instance, tmp_file):
    assert typer_instance.from_signature(str(tmp_file)) == "text"
