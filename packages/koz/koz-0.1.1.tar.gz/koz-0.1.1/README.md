# koz

Python monkeypatch detection and analysis tool.

## Overview

`koz` is a static analysis tool that detects and catalogs monkeypatch modifications in Python codebases. It uses AST parsing to identify patches and generates structured output for patch management.

## Features

- Detects three types of monkeypatching:
  - `@patch_to` decorator from `fastcore.basic`
  - Direct attribute assignment monkeypatching
  - `functools.wraps` decorator in `__init__` methods
- Generates JSON/TOML output with comprehensive metadata
- Integrates with git history for author and timestamp information
- Fast AST-based analysis without code execution

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Analyze current directory
koz analyze

# Analyze specific directory
koz analyze /path/to/project

# Use a configuration file to filter files
koz analyze --config koz_config.yaml

# Output to TOML
koz analyze --format toml --output patches.toml

# Output to JSON
koz analyze --format json --output patches.json

# Combine options
koz analyze /path/to/project --config koz_config.yaml --format json
```

### Configuration File

You can use a YAML configuration file to filter which files/folders to analyze. Create a `koz_config.yaml` file:

```yaml
# Include patterns: list of regex patterns for files/folders to include
include:
  - "src/.*"           # Include all files in src/ directory
  - "lib/.*"           # Include all files in lib/ directory

# Exclude patterns: list of regex patterns for files/folders to exclude
exclude:
  - ".*test_.*"        # Exclude test files
  - ".*/tests/.*"      # Exclude tests/ directory
  - ".*/__pycache__/.*"  # Exclude __pycache__ directories
```

**Notes:**
- Patterns are evaluated as regular expressions
- Exclude patterns are evaluated first
- If include patterns are specified, files must match at least one include pattern
- If no config file is provided, all files (except default exclusions) are analyzed
- See `examples/koz_config.yaml` for a complete example

### Detected Patterns

#### 1. fastcore.basic.patch_to Decorator
The most common pattern in fastai/fastcore projects:

```python
from fastcore.basic import patch_to

class MyClass:
    def __init__(self):
        self.value = 0

@patch_to(MyClass)
def new_method(self):
    """This method is added to MyClass via patch_to."""
    return self.value * 2
```

#### 2. Direct Attribute Assignment
```python
def custom_method(self):
    return "custom"

MyClass.method = custom_method
```

#### 3. functools.wraps Pattern
```python
from functools import wraps

class Wrapper:
    def __init__(self):
        @wraps(TargetClass.method)
        def wrapped(self):
            return "wrapped"
        TargetClass.method = wrapped
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linter
ruff check src/ tests/

# Format code
black src/ tests/

# Type check
mypy src/

# Install pre-commit hooks
pre-commit install
```

## License

Unlicense
