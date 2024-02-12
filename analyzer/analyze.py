import os
import sys
import stat

from collections import defaultdict

from analyzer.categories import Typer
from analyzer import utils


class Analyzer:
    """
    The Analyzer class provides functionality to analyze files in a directory,
    categorize them by type, calculate the total size for each category,
    log files with unusual permissions, and identify large files.

    Public Attributes:
        None

    Public Methods:
        add(path: str): Add a file or a directory to the analyzer and log its information.
        add_link(path:str): Add a symbolic link to the analyzer without following it.
        print_summary(): Print the summary of file types and their sizes to stdout.
        close(): Close the output files.
    """

    def __init__(
        self,
        threshold: int = 2048,
        unusual_perm_out: str = "report.txt",
        big_files_out: str = "",
    ):
        """
        Initialize the Analyzer.

        Args:
            threshold (int): The size threshold for identifying large files (default: 2048 bytes).
            unusual_perm_out (str): Path to the file for logging files with unusual permissions (default: "report.txt").
            big_files_out (str): Path to the file for logging large files (default: ""). If no file is provided, sys.stdout is used.

        Raises:
            Exception: If unable to open the specified output files.
        """
        self._typer = Typer()  # Instantiate the Typer class from the categories module
        self._type_size_count = defaultdict(int)  # Initialize a counter for file types
        self._threshold = (
            threshold  # Set the size threshold for identifying large files
        )

        # Open the file for logging files with unusual permissions
        self._up_out = open(unusual_perm_out, "w")
        try:
            # Open the file for logging large files (or default to sys.stdout)
            self._bf_out = sys.stdout if not big_files_out else open(big_files_out, "w")
        except Exception as e:
            # Close previously opened file in case of an error
            self._up_out.close()
            raise e

    def _log_permissions(self, mode: int, path: str):
        """
        Analyze file permissions and log files with unusual permissions.

        Args:
            mode (int): The mode (permissions) of the file.
            path (str): The path to the file.
        """

        unusual_perm = utils.unusual_permissions(mode)
        if unusual_perm:
            self._up_out.write(f"{path}: {stat.filemode(mode)} ({unusual_perm})\n")

    def _add_dir(self, path: str):
        """
        Add a directory to the analyzer and log its information.
        Directories are treated as a separate file category and counted in total size statistic.

        Args:
            path (str): The path to the directory to analyze.
        """
        dir_size = os.path.getsize(path)
        mode = os.stat(path).st_mode
        self._log_permissions(mode, path)
        self._type_size_count["directories"] += dir_size

    def add(self, path: str):
        """
        Add a file or a directory to the analyzer and log its information.

        Args:
            path (str): The path to the file/directory to analyze.
        """
        if os.path.isdir(path):
            self._add_dir(path)
        else:
            self._add_file(path)

    def _add_file(self, path: str):
        """
        Add a file to the analyzer and log its information.

        Args:
            path (str): The path to the file to analyze.
        """
        file_stat = os.stat(path)  # Get file statistics
        self._log_permissions(
            file_stat.st_mode, path
        )  # Analyze file permissions and log if unusual

        category = ""

        # Determine the file type category based on its file signature
        try:
            category = self._typer.from_signature(path)
        # If the file can't be read, its type is obtained from its extension
        except PermissionError:
            category = self._typer.from_extension(path)
        if file_stat.st_size > self._threshold:
            self._bf_out.write(
                f"{path}: {utils.file_size(file_stat.st_size)}\n"
            )  # Log large files
        self._type_size_count[
            category
        ] += file_stat.st_size  # Update the file type counter

    def add_link(self, path: str):
        """
        Add a symbolic link to the analyzer and log its information.
        The link is treated as a regular file of a separate category and it is not resolved.

        Args:
            path (str): The path to the file to analyze.
        """
        link_stat = os.lstat(path)
        mode = link_stat.st_mode
        self._log_permissions(mode, path)
        self._type_size_count["symlink"] += link_stat.st_size

    def print_summary(self):
        """
        Print the summary of file types and their sizes to stdout.
        """
        for key, value in self._type_size_count.items():
            print(f"{key}: {utils.file_size(value)}.")

    def close(self):
        """
        Close the output files.
        """
        if not self._up_out.closed:
            self._up_out.close()
        if self._bf_out is not sys.stdout and not self._bf_out.closed:
            self._bf_out.close()
