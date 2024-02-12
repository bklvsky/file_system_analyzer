# File System Analyzer

This repository contains my solution to the testing assignment for CloudLinux.

## Overview

The project on traversing and analyzing file structure. The project recursively iterates file structure (optionally iterates over symbolic links as well), logs files of size bigger than a threshold to stdout or to a file, forms a report on files with unusual permissions. In the end of iteration it outputs total size of different type categories.  

Goals:  
- To form a report file, logging all files with unusual permissions.  
- To determine and output the list of files that are bigger than a certain threshold.  
- To classify files in the directory to categories and calculate total size for each category.  

### Implementation details
Traversal algorithm is implemented with a loop to avoid stack overflow in recursion in case of a big directory.  
The script can handle symbolic links in two ways: the paths can be followed if an according flag is provided, in other case they are treated as regular files of a separate category. In case of following symbolic links, possible link loops are handled and outputed to stderr.  
Directories are treated as separate file categories in the output statistic to take into account their memory usage as well.


## Installation

Provide clear instructions for running your code and any necessary setup steps. Include any command-line commands or scripts that should be run, as well as any required dependencies.  
```
# Clone the repository
git clone https://github.com/bklvsky/file_system_analyzer.git

# Navigate to the project directory
cd file_system_analyzer

# Install dependencies
pip install -r requirements.txt
```

## Usage

To run the main script, run:

```
python main.py ./path/to/directory/to/traverse
```

Script also takes optional arguments which are:  

- `-t`, `--threshold`  
  A threshold to determine a big file in bytes, KB, MB or GB. The value for the threshold is case insensitive and can whitespace delimited.  
  Examples:  
  ```
  python main ./ -t 2048 # will set a threshold to 2048 bytes
  python main ./ -t '1024B' # will set a threshold to 1024 bytes
  python main ./ -t '10 mb' # will set a threshold to 10 megabytes
  ```
-  `--report-big-files`  
  Defines a file to output the list of big files. If not defined, the list is logged to standart output.  
  Takes a path to the output file. Warning: contents of existing file will be overwritten.  
  Example:  
  ```
  # creates big_files.txt with a list of files with size bigger than threshold
  python main.py ./ --report-big-files big_files.txt
  ```
-  `-f`, `--report-file`  
  Defines a file to output a report on files with unusual permission bits. If not defined, output is directed to `[directory_to_traverse]_report.txt.` file.  
  Takes a path to the output file. Warning: contents of existing file will be overwritten.  
  Example:
  ```
  # creates custom_report.txt with a list of files with unusual permissions
  python main.py ./ -f custom_report.txt
  ```
- `-l`, `--follow-links`  
  Flag to follow symlinks during directory traversal. Defaults to False.  
  By default symlinks are treated as files and are counted in the file statistics as a separate file category. If the flag is set to True links are resolved and directories and file pointed by them are traversed.  
  Example:
  ```
  python main.py ./ -l # follows symbolic links
  ```
- `-h`, `--help`  
  Output help message for the script.

### Usage example

In the repository a dircetory `./files` is provided for demonstrating basic functionality of the tool.  
To analyze the directory run:
```
cd files
sh ./init_files.sh  # will set unusual permissions to files and create symbolic links

cd ../
python main.py files -t '1 mb' --report-big-files big-files.txt -l
```
This example demonstrates symlink loops management, statistics for 3 categories (text, image and audio), management of empty files, determing category based on extension in case of no permissions and forming a report.  
It will create `big-files.txt` with a list of files with size bigger than 1 MB, `files_report.txt` with a list of files with unusual permissions (in this example file with 000 permission), output symlinks loop information and file errors to standart error and log directory statistic to standart output.


## Project structure

```
fs_analyzer/
├── main.py           # The main entry point of the application.
└── analyzer/
│   ├── __init__.py
│    analyze.py       # `Analyzer` class for file analysis and to output statistics.
│   ├── categories.py # `Typer` class for categorizing files based on type.
│   ├── cli.py        # Command-line interface
│   ├── traverse.py   # Traversal of directory
│   └── utils.py
├── files/            # set of files to use as an example for testing
└── tests/            # pytest testing module
```

### Modules description

- `analyze.py`  
  Provides the `Analyzer` class for file analysis. Gets information on file permissions, its size and category and logs the calculated statistics.
- `categories.py`  
  Contains the `Typer` class for categorizing files based on type. File type is determined based on file signature (with `magic` module). In case of an empty file (no file signature) the file type is determined based on the file extension (with mimetypes built-in package).  
  The class implements singleton pattern so that it is not necessary to reinstantiate libmagic wrapper for each file analyzed.  
- `cli.py`
  Implements command-line argument parsing logic with argparse module.  
- `traverse.py`  
  Traverses given directory breadth-first. Handles symbolic links and outputs link loops to stdout.  
- `utils.py`  
  Contains utility functions used throughout the project.  

### Testing
Testing is done with pytest framework with 97% of coverage. Test files can be found in the `test/` directory.
