"""
HumeSQL package.

Natural language → SQL → JSON results.
"""

from .client import HumeSQL

# Backwards compatibility
HumanSQL = HumeSQL

__all__ = ["HumeSQL", "HumanSQL"]

__version__ = "0.3.1"
