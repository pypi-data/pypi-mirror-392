# PyDevMate

A Python utilities library providing decorator-based tools for common development tasks.

## Features

PyDevMate offers a collection of reusable decorator classes that simplify common development tasks:

### Caching & Storage
- **CacheIt**: Function result caching with support for diskcache, Redis, and SQLite backends
- **SaveIt**: Core storage abstraction for persistent data storage

### Monitoring & Debugging
- **TimeIt**: Execution time measurement
- **MemIt**: Memory usage tracking
- **DebugIt**: Function call debugging with colored output

### Logging
- **LogIt**: Enhanced logger with color support and additional methods (success, show, separator)

### Utilities
- **LazyIt**: Lazy evaluation decorator for deferred computation
- **ConvertIt**: Static methods for size and time unit conversions
- **Colors**: Enum for terminal color constants
- **Infos**: Runtime information utilities (script name, path, Python version, PID)

## Installation

### Install directly from GitHub

```bash
# Install latest version from main branch
pip install git+https://github.com/lounisbou/PyDevMate.git

# Install specific branch
pip install git+https://github.com/lounisbou/PyDevMate.git@branch-name

# Install specific tag/release
pip install git+https://github.com/lounisbou/PyDevMate.git@v0.0.1
```

### Install from source (development)

```bash
# Clone the repository
git clone https://github.com/lounisbou/PyDevMate.git
cd PyDevMate

# Install in editable mode
pip install -e .

# Or install dependencies separately
pip install -r requirements.txt
```

## Quick Start

```python
from pydevmate import CacheIt, TimeIt, LogIt, MemIt

# Cache function results
@CacheIt()
def expensive_computation(n):
    return sum(i ** 2 for i in range(n))

# Measure execution time
@TimeIt
def timed_function():
    return [i for i in range(1000000)]

# Track memory usage
@MemIt
def memory_intensive():
    return [i for i in range(1000000)]

# Enhanced logging
logger = LogIt(__name__)
logger.success("Operation completed successfully!")
```

## Testing

```bash
# Run all utility tests
python main.py

# Test a specific utility
python main.py <utility_name>

# Test individual module directly
python pydevmate/<module_name>.py
```

## Building the Package

```bash
# Install build tools
pip install build

# Build wheel
python -m build --wheel

# Built wheel will be in dist/ directory
```

## Requirements

- Python >= 3.6
- diskcache >= 5.6.3
- psutil >= 6.1.0
- redis >= 5.2.0
- termcolor >= 2.5.0

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

LounisBou (lounis.bou@gmail.com)

## Repository

https://github.com/lounisbou/PyDevMate
