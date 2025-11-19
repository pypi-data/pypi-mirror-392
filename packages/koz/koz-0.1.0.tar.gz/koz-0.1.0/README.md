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

# Output to TOML
koz analyze --format toml --output patches.toml

# Output to JSON
koz analyze --format json --output patches.json
```

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
