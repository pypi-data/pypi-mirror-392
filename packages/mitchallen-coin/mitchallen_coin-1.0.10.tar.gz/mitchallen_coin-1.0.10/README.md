# mitchallen.coin

[![PyPI version](https://img.shields.io/pypi/v/mitchallen-coin.svg)](https://pypi.org/project/mitchallen-coin/)
[![Python versions](https://img.shields.io/pypi/pyversions/mitchallen-coin.svg)](https://pypi.org/project/mitchallen-coin/)
[![License](https://img.shields.io/pypi/l/mitchallen-coin.svg)](https://github.com/mitchallen/python-coin-flip/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/mitchallen-coin.svg)](https://pypi.org/project/mitchallen-coin/)
[![CI](https://github.com/mitchallen/python-coin-flip/actions/workflows/test-coin.yml/badge.svg)](https://github.com/mitchallen/python-coin-flip/actions/workflows/test-coin.yml)
[![codecov](https://codecov.io/gh/mitchallen/python-coin-flip/branch/main/graph/badge.svg?flag=mitchallen-coin)](https://codecov.io/gh/mitchallen/python-coin-flip)

A simple, lightweight Python package that provides a random number generator perfect for simulations, games, and probabilistic applications.

## Installation

```bash
pip install mitchallen-coin
```

Or using [uv](https://docs.astral.sh/uv/):

```bash
uv add mitchallen-coin
```

## Quick Start

```python
from mitchallen.coin import flip, heads, tails

# Get a boolean coin flip result
result = flip()
print(result)  # True or False

# Alternative: using heads()
is_heads = heads()
print(is_heads)  # True or False

# Alternative: using tails()
is_tails = tails()
print(is_tails)  # True or False
```

## Usage Examples

### Simulate a Coin Flip

```python
from mitchallen.coin import heads, tails

# Using heads()
if heads():
    print("Heads")
else:
    print("Tails")

# Or using tails()
if tails():
    print("Tails")
else:
    print("Heads")
```

### Random 50/50 Decisions

```python
from mitchallen.coin import flip

# Use flip() for 50/50 decisions
if flip():
    print("Event A happens")
else:
    print("Event B happens")
```

## API Reference

### `flip()`

Returns a random boolean value with 50% probability for True or False.

**Returns:**
- `bool`: True or False with equal probability

**Example:**

```python
from mitchallen.coin import flip

value = flip()
assert isinstance(value, bool)

# Use in conditional logic
if flip():
    print("Heads!")
else:
    print("Tails!")
```

### `heads()`

Returns a random boolean value (same as flip()). Useful for simple boolean coin flip simulations.

**Returns:**
- `bool`: True or False with equal probability

**Example:**

```python
from mitchallen.coin import heads

result = heads()
if result:
    print("Heads!")
else:
    print("Tails!")
```

### `tails()`

Returns the opposite boolean value of heads(). Returns True if heads() would return False, and False if heads() would return True.

**Returns:**
- `bool`: The opposite of what heads() would return

**Example:**

```python
from mitchallen.coin import tails

result = tails()
if result:
    print("Tails!")
else:
    print("Heads!")
```

## Why mitchallen.coin?

- **Simple**: Clean API with intuitive functions
- **Lightweight**: No dependencies
- **Type-safe**: Full type annotations with mypy type checking
- **Quality**: Enforced code quality with Ruff linting and formatting
- **Tested**: Comprehensive test suite ensuring quality and reliability
- **Namespace package**: Works alongside other mitchallen packages

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](https://github.com/mitchallen/python-coin-flip/blob/main/CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](https://github.com/mitchallen/python-coin-flip/blob/main/LICENSE) for details.
