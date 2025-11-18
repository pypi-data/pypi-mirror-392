# Dummy Test Package

This is a dummy Python package created for testing private PyPI index uploads.

## Installation

```bash
pip install dummy-test-package
```

## Usage

```python
from dummy_package import greet

greet("World")
```

## Building the Package

```bash
python -m build
```

## Uploading to Private PyPI

```bash
twine upload --repository-url https://your-private-pypi-url/simple/ dist/*
```
