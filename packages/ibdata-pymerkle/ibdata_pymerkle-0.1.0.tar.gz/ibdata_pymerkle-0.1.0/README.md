# ibdata-pymerkle

A module for producing and/or reading IBData-compatible Merkle trees for directory structures.

## Features


## Installation

### Using uv (recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

uv tool install ibdata-pymerkle # This is usually what you want to do

# or install the package
uv pip install ibdata-pymerkle

# Or install in development mode with all dependencies
uv sync --group dev

```

### Traditional pip

```bash
pip install ibdata-pymerkle
```

## Usage

### Command Line

#### Basic Usage

```bash
ibdata-pymerkle --help # Show help

ibdata-pymerkle 

```

#### Using installed command

```bash
# Generate terraform configuration from terraform.tfvars
ibdata-pymerkle

# Or run directly with uv
uv run ibdata-pymerkle
```

### Python API

```python
from ibdata_pymerkle.merkle_tree import MerkleTree

result = "TODO"
print(result)
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and building.

### Setup Development Environment

It is highly recommended that you use the devcontainer defined in `.devcontainer` for a consistent development environment.

Otherwise, you will need `uv` and `make` installed.

```bash
# Install development dependencies
uv sync --group dev
```

### Running Tests

```bash
# Run simple tests (no dependencies required)
uv run python -m tests.simple_test_merkle

# Run full test suite
uv run --group test pytest tests/ -v

# Run tests with coverage
uv run --group test pytest tests/ --cov=src --cov-report=term-missing

# Or use make commands
make test
make test-cov
```

### Code Quality

```bash
# Format code
uv run --group lint black src tests
uv run --group lint ruff format src tests

# Lint code
uv run --group lint ruff check src tests

# Type check
uv run --group lint mypy src

# use make commands
make format
make lint
make type-check
```

### Building and Publishing

```bash
# Build the package
uv build

# Install locally
uv pip install .
```

### Makefile Commands

For convenience, use the included Makefile:

```bash
make help            # Show all available commands
make dev-install     # Install with development dependencies  
make test            # Run all tests
make test-simple     # Run simple tests only
make test-script     # Test the direct ibdatapy script
make install-script  # Install ibdatapy script globally
make uninstall-script # Remove installed script
make lint            # Run code linting
make format          # Format code
make type-check      # Run type checking
make build           # Build the package
make clean           # Clean build artifacts
```

## Configuration

The tool expects a configuration file

TODO

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

See the [LICENSE](LICENSE) file for full license text.
