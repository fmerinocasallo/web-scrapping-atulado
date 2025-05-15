"""
Parser for current electricity rates from A tu Lado Energía.

Provides tools to extract consumption and power prices from the company's website.
"""

__all__ = ["parser", "paths"]
__version__ = "0.0.1"

# Import the private implementation details
from . import parser, paths
