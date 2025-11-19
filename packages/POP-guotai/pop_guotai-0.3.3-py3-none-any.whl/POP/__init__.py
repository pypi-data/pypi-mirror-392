"""
POP - Prompt Oriented Programming
Reusable, mutable, prompt functions for LLMs.


# =============================
# DEPRECATION NOTICE
# =============================
# This package is deprecated and will no longer be maintained.
# Please use the new package name: pypop
# =============================
Author: Guotai Shen
"""

from .POP import PromptFunction
from .Embedder import Embedder

import warnings

warnings.warn(
    "The 'POP-guotai' package is deprecated and will no longer be maintained. "
    "Please install and import 'pypop' instead (pip install pypop).",
    DeprecationWarning,
    stacklevel=2,
)

# Versioning
__version__ = "0.3.2"
__author__ = "Guotai Shen"
__license__ = "MIT"

# Expose key functionalities
__all__ = ["PromptFunction", "Embedder"]
