"""
tree2cmd — Convert text-based folder trees into real directories and files.

This package provides:
- parse_tree()                    → Parse struct.txt into a list of paths
- convert_tree_to_commands()      → Turn parsed tree into mkdir/touch commands
- tree_from_shell_commands()      → Render a directory tree from commands

The goal is to make LLM-generated folder trees executable and reproducible.
"""

from __future__ import annotations

from importlib.metadata import version, PackageNotFoundError

# Public API
from .parser import parse_tree
from .cli import convert_tree_to_commands
from .utils import tree_from_shell_commands


# ---------------------------------------------------------
# Version Metadata (auto-updates from pyproject.toml)
# ---------------------------------------------------------
try:
    __version__ = version("tree2cmd")
except PackageNotFoundError:
    # Local development fallback
    __version__ = "0.2.1"

__all__ = [
    "parse_tree",
    "convert_tree_to_commands",
    "tree_from_shell_commands",
    "__version__",
]

__author__ = "Antony Joseph Mathew"
__email__ = "antonyjosephmathew1@gmail.com"
