# mitchallen-roll

[![PyPI version](https://img.shields.io/pypi/v/mitchallen-roll.svg)](https://pypi.org/project/mitchallen-roll/)
[![Python versions](https://img.shields.io/pypi/pyversions/mitchallen-roll.svg)](https://pypi.org/project/mitchallen-roll/)
[![License](https://img.shields.io/pypi/l/mitchallen-roll.svg)](https://github.com/mitchallen/python-coin-flip/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/mitchallen-roll.svg)](https://pypi.org/project/mitchallen-roll/)
[![CI](https://github.com/mitchallen/python-coin-flip/actions/workflows/test-roll.yml/badge.svg)](https://github.com/mitchallen/python-coin-flip/actions/workflows/test-roll.yml)
[![codecov](https://codecov.io/gh/mitchallen/python-coin-flip/branch/main/graph/badge.svg?flag=mitchallen-roll)](https://codecov.io/gh/mitchallen/python-coin-flip)

A simple dice rolling random number generator for Python.

## Installation

```bash
pip install mitchallen-roll
```

Or with uv:

```bash
uv add mitchallen-roll
```

## Usage

```python
from mitchallen.roll import roll, d6, d20

# Roll a standard 6-sided die
result = roll()  # Returns 1-6

# Roll a custom die
result = roll(20)  # Returns 1-20

# Convenience functions
result = d6()   # Roll a 6-sided die
result = d20()  # Roll a 20-sided die
```

## API Reference

### `roll(sides=6) -> int`

Roll a die with the specified number of sides.

**Parameters:**
- `sides` (int): Number of sides on the die (default: 6, minimum: 1)

**Returns:**
- `int`: A random integer from 1 to sides (inclusive)

**Raises:**
- `ValueError`: If sides is less than 1

### `d6() -> int`

Convenience function to roll a 6-sided die.

**Returns:**
- `int`: A random integer from 1 to 6

### `d20() -> int`

Convenience function to roll a 20-sided die.

**Returns:**
- `int`: A random integer from 1 to 20

## Development

See the main repository README for development setup instructions.

## License

MIT License - see LICENSE file for details
