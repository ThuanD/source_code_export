# Source Code Export Tool

This Python tool helps you export the directory structure and content of your source code project to a text file. This tool is useful when you need to:

- Share code via text
- Create documentation about project structure
- Backup code content as text
- Analyze project structure

## Features

- Exports directory structure as a tree view
- Exports content of text/source code files
- Option to exclude unwanted directories/files
- Automatically ignores system folders (.git, __pycache__, etc.)
- Supports various source code file formats
- Cross-platform (Windows, Linux, MacOS)

## Installation

```bash
# Clone repository
git clone https://github.com/ThuanD/source_code_export.git
```

## Usage

### Basic Syntax

```bash
python source_code_export.py [path] [options]
```

### Parameters

- `path`: Path to the project directory (required)
- `-o`, `--output`: Output file (default: source_code_export.txt)
- `-e`, `--exclude`: List of patterns to exclude (glob patterns)
- `--exclude-ext`: List of extensions to exclude

### Examples

```bash
# Basic export
python source_code_export.py /path/to/project

# Specify output file
python source_code_export.py /path/to/project -o my_export.txt

# Exclude some directories/files
python source_code_export.py /path/to/project --exclude "test/*" "*.log"
python source_code_export.py . -e postgresql logs migrations translations

# Exclude some extensions
python source_code_export.py /path/to/project --exclude-ext .pyc .jar
```

## Output Format

The output file will have the following structure:

```
Project Structure: project_name
==================================================

Directory Structure:
--------------------
├── src
  ├── components
  ├── services
  └── utils
...

File Contents:
--------------------
File: src/components/example.js
--------------------------------------------------
// File content
```

## Supported File Types

The tool supports common file formats:

- Python (.py)
- JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
- HTML/CSS (.html, .css)
- Config files (.json, .yml, .yaml)
- Documentation (.md, .rst)
- Shell scripts (.sh, .bash)
- And many more...

## Default Configuration

The tool automatically excludes certain system folders:

- .git
- __pycache__
- node_modules
- .env

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a new branch
3. Submit a Pull Request

## License

No License
