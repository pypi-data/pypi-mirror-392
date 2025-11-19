# TIDAS Python SDK

[中文文档](README-zh.md)

Type-safe Python tooling for working with ILCD/TIDAS life-cycle data. The SDK wraps the generated models with convenient factories, property accessors, and validation helpers so you can build rich LCA workflows in Python.

## Status

- Version: 0.1.0 (preview)
- Distribution: install from source (PyPI release coming soon)

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management and scripted commands  
  _Install via `curl -LsSf https://astral.sh/uv/install.sh | sh` if uv is not available._

## Installation

```bash
cd sdks/python
uv sync --group dev  # install core + development dependencies
```

## Quick Start

Run the end-to-end sample to see the core features in action:

```bash
uv run python examples/usage.py
```

Minimal usage example:

```python
from tidas_sdk import create_process

process = create_process({})
process.process_data_set.process_information.data_set_information.name.base_name.set_text(
    "Sample Process", lang="en"
)

print(process.to_json())
```

## Features in `examples/usage.py`

- JSON ➜ Object bootstrap: `create_process()` builds a `TidasProcess` from complete or partial JSON payloads (`creat_object_from_json()`).
- Object ➜ JSON round-trip: `to_json()` returns the ILCD-compliant dictionary for downstream tooling (`convert_object_to_json()`).
- Property access & localization: dotted attribute access plus `set_text()`/`get_text()` helpers simplify multilingual fields (`properties_access()`).
- IDE type hints: generated classes expose full type information for autocompletion (`type_hinting_and_autocompletion()`).
- On-demand validation: call `validate()` only when your dataset is ready; inspect issues with `last_validation_error()` (`validation_on_demand()`).
- XML export: `to_xml()` serializes to ILCD XML for interoperability (`convert_to_xml()`).

## Development Workflow

```bash
# Install / update dependencies
uv sync --group dev

# Linting & formatting
uv run ruff check src
uv run ruff format src

# Type checking
uv run mypy src

# Tests
uv run pytest
```

## Project Layout

- `src/tidas_sdk`: Core implementation and generated models
- `examples/usage.py`: Feature walkthrough used in this README
- `scripts/`: Utility scripts for code generation and maintenance

For questions or contributions, open an issue or pull request at https://github.com/tiangong-lca/tidas-sdk.
