"""Fakestack - High-Performance Database Generator

Generate databases from JSON schemas with realistic fake data.
Powered by a Go core for blazing-fast performance!
"""

__version__ = "1.1.0"
__author__ = "Devendra Pratap"
__email__ = "dps.manit@gmail.com"
__license__ = "MIT"

# Import main API
from .runner import fakestack, main, run_fakestack

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "main",
    "run_fakestack",
    "fakestack",
]
