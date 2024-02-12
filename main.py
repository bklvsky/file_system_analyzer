import os
import sys
from analyzer import cli
from analyzer import traverse
from analyzer.analyze import Analyzer


def main(args):
    """
    Main function to execute the file system analysis.

    Args:
        args: Command-line arguments parsed by the cli module.

    Returns:
        None
    """
    # Getting command-line arguments
    path, threshold = args.path, args.threshold
    big_files_out, unusual_perm_out = args.report_big_files, args.report_file
    follow_links = args.follow_links

    # Normalizing arguments
    threshold = 100 if not threshold else threshold
    directory = os.path.realpath(os.path.expanduser(path))
    if not unusual_perm_out:
        unusual_perm_out = f"{directory}_report.txt"

    # Initializing analyzer
    try:
        analyzer = Analyzer(
            threshold, unusual_perm_out=unusual_perm_out, big_files_out=big_files_out
        )
        # Recursively traverse directory
        try:
            traverse.traverse_directory(directory, analyzer, follow_links=follow_links)
        except Exception as e:
            print(f"Unexpected error occurred: {e}.\nAborting.", file=sys.stderr)
        finally:
            analyzer.close()

    # Possible exceptions while opening log files for Analyzer
    except (OSError, ValueError) as e:
        print(
            f"Error: could not open logfile {e.filename}: {e.strerror}.\nAborting.",
            file=sys.stderr,
        )
    # Other exceptions while initializing analyzer
    except Exception as e:
        print(
            f"Unexpected error occurred while initializing Analyzer: {e}.\nAborting.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    args = cli.get_args()
    main(args)
