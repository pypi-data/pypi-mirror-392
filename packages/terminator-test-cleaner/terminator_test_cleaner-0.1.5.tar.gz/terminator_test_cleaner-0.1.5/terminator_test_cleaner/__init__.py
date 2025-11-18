"""
Terminator Test Cleaner Package

A simple test package for testing terminator functionality.
"""

__version__ = "0.1.5"
__author__ = "Test Author"
__email__ = "test@example.com"

def clean_terminator_data(data):
    """
    A simple function to clean terminator test data.

    Args:
        data: Input data to clean

    Returns:
        Cleaned data
    """
    if isinstance(data, str):
        return data.strip()
    elif isinstance(data, list):
        return [item.strip() if isinstance(item, str) else item for item in data]
    else:
        return data

def get_version():
    """Return the package version."""
    return __version__