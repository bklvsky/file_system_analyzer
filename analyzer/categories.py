import magic
import mimetypes


class Typer:
    """
    The Typer class provides functionality for categorizing files based on MIME types and file extensions.

    Public methods:
        from_extension: Determine the file type category based on the file extension.
        from_signature: Determine the file type category based on the file signature (magic number).
    """

    _instance = None
    _CATEGORIES_ARCHIVE = ["zip", "x-tar", "x-gzip", "x-bzip2", "x-rar-compressed"]

    def __new__(cls):
        """
        Get the singleton instance of the Typer class.

        Returns:
            Typer: The singleton instance of the Typer class.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the Typer instance with the magic module for MIME type detection.
        """
        self._mime = magic.Magic(mime=True)

    def _get_general_category(self, file_type: str) -> str:
        """
        Get the general category of a file type.

        Args:
            file_type (str): The MIME type of the file.

        Returns:
            str: The general category of the file type.
        """
        category = file_type.split("/")[0]

        # Determine the specific category based on MIME category
        if category == "application":
            if "pdf" in file_type:
                return "pdf"
            if any(category in file_type for category in Typer._CATEGORIES_ARCHIVE):
                return "archive"
            return "executable"
        return category

    def from_extension(self, path: str) -> str:
        """
        Determine the file type category based on the file extension.

        Args:
            path (str): The path to the file.

        Returns:
            str: The file type category.
        """
        file_type = mimetypes.guess_type(path)[0]
        if not file_type:
            return "unknown"
        return self._get_general_category(file_type)

    def from_signature(self, path: str) -> str:
        """
        Determine the file type category based on the file signature (magic number).
        If the file is determined to be empty (withh no signature) the type is obtained from file extension.

        Args:
            path (str): The path to the file.

        Returns:
            str: The file type category.
        """
        file_type = self._mime.from_file(path)
        if "empty" in file_type:
            return self.from_extension(path)
        return self._get_general_category(file_type)
