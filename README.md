# Source Code Export Tool v2.0

A modern Python utility that exports the directory structure and content of your source code project to various text formats. This tool is especially useful when you need to:

- Share source code via text
- Document project structure
- Back up code content in a readable format
- Analyze project structure
- Submit code for academic exercises

## Features in Version 2.0

- Modern graphical user interface (GUI)
- Dark/light theme support
- Multilingual (English and Vietnamese)
- Multiple export formats (TXT, Markdown, HTML, JSON)
- Source code statistics and analysis
- Export history management
- Search and filter capabilities
- Progress bar and status updates
- Advanced filtering options

## Installation

```bash
# Clone repository
git clone https://github.com/ThuanD/source_code_export.git

# Navigate to project directory
cd source_code_export

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Application

The simplest way to run the application is:

```bash
python run.py
```

### GUI Features

1. **History View**
   - View previous exports
   - Search and filter history
   - Create new export configurations
   - Toggle between light/dark themes
   - Switch language (English/Vietnamese)

2. **Export Configuration**
   - Basic settings (input folder, output file, format)
   - Advanced settings (exclude paths, file extensions, size limits)
   - Progress tracking during export
   - Open exported files directly

### Export Formats

The tool supports four output formats:
- **Text (TXT)**: Simple, plain text format
- **Markdown (MD)**: Formatted with syntax highlighting
- **HTML**: Rich web-based representation with syntax highlighting
- **JSON**: Structured data format for programmatic use

## Project Structure

```
.
├── src/                    # Source code
│   ├── models/             # Data models
│   │   ├── exporter.py     # Core export functionality
│   │   └── history.py      # Export history management
│   ├── views/              # UI components
│   ├── controllers/        # Application logic
│   ├── themes/             # Theme management
│   ├── i18n/               # Internationalization
│   ├── utils/              # Utility functions
│   └── main.py             # Main entry point
├── data/                   # Data directory (history, settings)
├── run.py                  # Quick start script
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

## Supported File Types

The tool supports common file formats:

- Python (.py)
- JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
- HTML/CSS (.html, .css)
- Configuration files (.json, .yml, .yaml)
- Documentation (.md, .rst)
- Shell scripts (.sh, .bash)
- And many more...

## Default Configuration

The tool automatically excludes the following system directories:

- .git
- __pycache__
- node_modules
- .env
- .venv
- venv
- .DS_Store

## Features Coming Soon

- Remote repository export (GitHub, GitLab, etc.)
- PDF export format
- Code metrics and complexity analysis
- Direct integration with code editors

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a new branch
3. Submit a Pull Request

## License

No License

---

For questions or support, please open an issue on GitHub.
