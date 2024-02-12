import argparse
import re
import os


def valid_dir(value):
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError(f"Error: {value}: doesn't exist.")
    if not os.path.isdir(value):
        raise argparse.ArgumentTypeError(f"Error: {value}: is not a directory.")
    return value


def split_numerical_and_nonnumerical(string: str):
    """
    Extract the numerical part from the beginning of the string and the non-numerical part from the rest.

    Args:
        string (str): The input string.

    Returns:
        tuple: A tuple containing the numerical part (as a string) and the non-numerical part (as a string)
               of the input string. If no numerical part is found, both parts will be None.
    """
    match = re.match(r"(-?\d+)(.*)", string)
    if match:
        numerical_part = match.group(1)
        non_numerical_part = match.group(2)
        return numerical_part, non_numerical_part
    else:
        return None, None


def parse_size(value: int, size_str: str):
    """
    Parse a size string with units (e.g., "100KB", "1GB") into bytes.

    Args:
        value (int): The numerical value of the size.
        size_str (str): The size string with units. Units accepted: B, KB, MB, GB, accepted in lower and uppercase.

    Returns:
        int: The size in bytes.

    Raises:
        argparse.ArgumentTypeError: If the size string is invalid.
    """
    sizes = {"B": 0, "KB": 1, "MB": 2, "GB": 3}

    # If no units are provided, we assume that the threshold is given in bytes
    if not size_str:
        return value

    # Units are accepted in both lower- and uppercases, with or without whitespace as a delimeter
    size_str = size_str.strip().upper()
    if size_str not in sizes:
        raise argparse.ArgumentTypeError(
            f"Invalid unit size {size_str} is provided for the threshold. Valid inputs are: B, KB, MB, GB"
        )
    return value * (1024 ** sizes[size_str])


def size_type(value):
    """
    Validate and parse the threshold value.

    Args:
        value (str): The threshold value provided as a string.

    Returns:
        int: The parsed threshold value in bytes.

    Raises:
        argparse.ArgumentTypeError: If the threshold value is invalid.
    """
    num_value, size_str = split_numerical_and_nonnumerical(value)
    if not num_value:
        raise argparse.ArgumentTypeError(f"Threshold can't be set to [{value}] value.")
    ivalue = int(num_value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            f"Invalid threshold value {value}: should be a positive number."
        )
    ivalue = parse_size(ivalue, size_str)
    return ivalue


def get_args():
    """
    Parse command-line arguments and return the parsed arguments.

    Returns:
        argparse.Namespace: The parsed command-line arguments.

    Expected command-line arguments:
        path: The path to the directory to be analyzed.

    Optional command-line flags:
        -t, --threshold: flag specifying the size threshold for identifying large files.
                         The threshold value can be provided with optional units (e.g., 100KB, 1MB).
        --report-big-files: Optional flag to enable reporting of large files found during analysis.
        -f, --report-file: Optional path to specify the file to write the analysis report to.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--threshold",
        type=size_type,
        help="A threshold to determine a big file in bytes, KB, MB or GB. E.g.: '10 mb', '5KB', '100'.",
    )
    parser.add_argument(
        "path", type=valid_dir, help="A path to a directory to analyze."
    )
    parser.add_argument(
        "--report-big-files",
        help="An path to file to log big files. If not provided defaults to stdout.",
    )
    parser.add_argument(
        "-f",
        "--report-file",
        help="A path to output unusual permissions report. Defaults to [dir_path]_report.txt.",
    )
    parser.add_argument(
        "-l",
        "--follow-links",
        action="store_true",
        help="Follow symlink during directory traversal.",
    )
    args = parser.parse_args()
    return args
