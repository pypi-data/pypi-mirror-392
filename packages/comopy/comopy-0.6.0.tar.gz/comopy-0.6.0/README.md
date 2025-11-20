ComoPy: Co-modeling Tools for Hardware Generation with Python
================================================================

ComoPy (Co-modeling tools in Python) is a Python-based Hardware Generation, Simulation, and Debugging Framework (HGSDF) that enables hardware development with the same ease and flexibility as software development.

## Development Setup

### Prerequisites

- Python 3.13 (recommended — prebuilt CIRCT wheels on PyPI target Python 3.13)
- Python 3.10+ is supported; on 3.10/3.11/3.12 you may need to build CIRCT from source
- pip (Python package installer)

### Install Dependencies

To set up the development environment, install the required dependencies:

```bash
# Install core dependencies
pip install -e .

# Install development dependencies (for testing)
pip install -e ".[dev]"
```

### Set Up Pre-commit Hooks

If you plan to contribute to the project, install pre-commit hooks to automatically check code quality before commits:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

### Run Tests

After installing the development dependencies, you can run the test suite using pytest:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=comopy

# Run tests with HTML coverage report
pytest --cov=comopy --cov-report=html

# Run tests in verbose mode
pytest -v

# Run specific test file
pytest comopy/tests/test_specific.py
```

The tests are configured via `pytest.ini` in the project root.
