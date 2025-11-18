# Terminator Test Cleaner

A simple test package for testing terminator functionality.

## Installation

```bash
pip install terminator-test-cleaner
```

## Usage

```python
from terminator_test_cleaner import clean_terminator_data, get_version

# Clean string data
cleaned = clean_terminator_data("  hello world  ")
print(cleaned)  # Output: "hello world"

# Clean list data
cleaned_list = clean_terminator_data(["  item1  ", "  item2  "])
print(cleaned_list)  # Output: ["item1", "item2"]

# Get version
print(get_version())  # Output: "0.1.5"
```

## License

MIT License