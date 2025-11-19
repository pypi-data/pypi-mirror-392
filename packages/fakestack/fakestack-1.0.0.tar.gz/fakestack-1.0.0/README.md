<p align="center">
  <img src="../assets/fake-stack.svg" alt="Fakestack Logo" width="200"/>
</p>

<h1 align="center">Fakestack</h1>

<p align="center">
Python wrapper for the high-performance Fakestack database generator.
</p>

## Installation

```bash
pip install fakestack
```

## Features

- **Zero Dependencies**: No runtime dependencies, all functionality provided by bundled Go binary
- **50+ Fake Data Generators**: Built on gofakeit
- **Multi-Database Support**: SQLite, MySQL, PostgreSQL
- **Fast**: 10-100x faster than pure Python implementations
- **Cross-Platform**: Works on Linux, macOS, Windows (x64 & ARM64)
- **Python 3.8+**: Compatible with Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13

## Quick Start

### Command Line

```bash
# Download example schema
python -m fakestack.runner -d .

# Create database and populate with fake data
python -m fakestack.runner -c -p -f schema.json
```

Or use the installed command:

```bash
fakestack -d .
fakestack -c -p -f schema.json
```

### Python API

```python
from fakestack import fakestack

# Download schema
fakestack(['-d', '.'])

# Create and populate database
fakestack(['-c', '-p', '-f', 'schema.json'])
```

## Schema Example

```json
{
  "database": {
    "db_type": "sqlite",
    "db_name": "test.db"
  },
  "tables": [
    {
      "name": "users",
      "count": 50,
      "columns": [
        {"name": "id", "type": "INTEGER PRIMARY KEY AUTOINCREMENT"},
        {"name": "name", "type": "TEXT", "fake": "name"},
        {"name": "email", "type": "TEXT", "fake": "email"},
        {"name": "phone", "type": "TEXT", "fake": "phoneformatted"},
        {"name": "address", "type": "TEXT", "fake": "address"},
        {"name": "created_at", "type": "TEXT", "fake": "date"}
      ]
    }
  ]
}
```

## Available Options

- `-d <path>` - Download example schema
- `-c` - Create database tables
- `-p` - Populate tables with fake data  
- `-f <file>` - Schema file path

## Available Fake Data Types

See [golang/README.md](../golang/README.md) for complete list of 50+ fake data generators.

## Development

### Setup
```bash
cd python
pip install -e ".[dev]"
```

### Run Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
black fakestack/
isort fakestack/
flake8 fakestack/
```

## How It Works

This package bundles pre-compiled Go binaries for all major platforms. When you run fakestack, the Python wrapper:
1. Detects your OS and architecture
2. Selects the appropriate binary from `fakestack/bin/`
3. Executes it with your arguments
4. Returns the exit code

This approach provides:
- ✅ Zero runtime dependencies
- ✅ Native performance
- ✅ Easy installation
- ✅ Cross-platform compatibility

## License

MIT - See LICENSE file in root directory

## Links

- PyPI: https://pypi.org/project/fakestack/
- GitHub: https://github.com/0xdps/fake-stack
- Issues: https://github.com/0xdps/fake-stack/issues
