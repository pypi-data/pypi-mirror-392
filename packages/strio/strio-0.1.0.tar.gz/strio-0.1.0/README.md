# Strio

A Python library that implements custom string utility functions from scratch without using Python's built-in string methods.

## Features

Strio provides a comprehensive set of string manipulation functions, all implemented manually using basic operations, loops, and character-level manipulations. This makes it an excellent learning resource and a foundation for understanding how string operations work under the hood.

## Installation

```bash
pip install strio
```

## Available Functions

- `capitalize(s)` - Capitalize the first character and lowercase the rest
- `casefold(s)` - Return a casefolded copy of the string
- `count(s, sub, start=0, end=None)` - Count occurrences of substring
- `endswith(s, suffix, start=0, end=None)` - Check if string ends with suffix
- `find(s, sub, start=0, end=None)` - Find first occurrence of substring (returns -1 if not found)
- `index(s, sub, start=0, end=None)` - Find first occurrence of substring (raises ValueError if not found)
- `isdigit(s)` - Check if all characters are digits
- `islower(s)` - Check if all cased characters are lowercase
- `isupper(s)` - Check if all cased characters are uppercase
- `strip(s, chars=None)` - Remove leading and trailing whitespace (or specified characters)
- `lstrip(s, chars=None)` - Remove leading whitespace (or specified characters)
- `rstrip(s, chars=None)` - Remove trailing whitespace (or specified characters)
- `replace(s, old, new, count=-1)` - Replace occurrences of substring
- `split(s, sep=None, maxsplit=-1)` - Split string by delimiter
- `rsplit(s, sep=None, maxsplit=-1)` - Split string from right
- `swapcase(s)` - Swap case of all characters

## Usage Examples

```python
from strio import capitalize, count, find, replace, split

# Capitalize a string
result = capitalize("hello world")
print(result)  # "Hello world"

# Count occurrences
count_val = count("hello hello", "hello")
print(count_val)  # 2

# Find substring
index = find("hello world", "world")
print(index)  # 6

# Replace substrings
new_str = replace("hello world", "world", "python")
print(new_str)  # "hello python"

# Split string
parts = split("a,b,c", ",")
print(parts)  # ["a", "b", "c"]

# Split on whitespace
words = split("hello world python")
print(words)  # ["hello", "world", "python"]
```

### More Examples

```python
from strio import (
    isdigit, islower, isupper, strip, 
    lstrip, rstrip, swapcase, endswith
)

# Check string properties
print(isdigit("123"))      # True
print(islower("hello"))    # True
print(isupper("HELLO"))    # True

# Strip whitespace
print(strip("  hello  "))   # "hello"
print(lstrip("  hello  "))  # "hello  "
print(rstrip("  hello  "))  # "  hello"

# Swap case
print(swapcase("Hello"))    # "hELLO"

# Check suffix
print(endswith("hello.py", ".py"))  # True
```

## Development

### Running Tests

```bash
pytest strio/tests/
```

### Building the Package

```bash
python setup.py sdist bdist_wheel
```

### Publishing to PyPI

```bash
twine upload dist/*
```

## Implementation Details

All functions in Strio are implemented from scratch without using Python's built-in string methods. The implementation uses:

- Character-level operations with `ord()` and `chr()`
- Manual loops and indexing
- Basic string slicing
- No reliance on built-in string methods like `.lower()`, `.upper()`, `.strip()`, etc.

This makes Strio a great educational resource for understanding string manipulation algorithms.

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

