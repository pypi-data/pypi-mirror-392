"""
Utility functions for tree2cmd.

This module contains helpers for:
- Rendering a directory tree from shell commands (mkdir/touch)
"""

from __future__ import annotations
from typing import Dict, List


def tree_from_shell_commands(commands: List[str]) -> str:
    """
    Build a visual directory tree from a list of mkdir/touch commands.

    Example output:

        Project
        ├── src
        │   └── main.py
        └── README.md

        2 directories, 1 files
    """

    # ------------------------------------------------------------------
    # 1. Build a nested dictionary tree structure
    # ------------------------------------------------------------------
    tree: Dict[str, dict] = {}

    for cmd in commands:
        if not (cmd.startswith("mkdir -p") or cmd.startswith("touch")):
            continue

        # Extract the final quoted path
        path = cmd.split()[-1].strip("\"'")
        parts = [p for p in path.split("/") if p]

        # Insert into tree structure
        current = tree
        for part in parts:
            current = current.setdefault(part, {})

    # If no tree could be constructed:
    if not tree:
        return "No directories or files\n\n0 directories, 0 files"

    # ------------------------------------------------------------------
    # 2. Recursive tree printer
    # ------------------------------------------------------------------
    def _build(d: Dict[str, dict], prefix: str = "") -> List[str]:
        lines = []
        # Sort alphabetically for deterministic builds/tests
        items = sorted(d.keys())

        for i, name in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")

            subtree = d[name]
            if subtree:
                extension = "    " if is_last else "│   "
                lines.extend(_build(subtree, prefix + extension))

        return lines

    # ------------------------------------------------------------------
    # 3. Determine root (top-level folder)
    # ------------------------------------------------------------------
    roots = sorted(tree.keys())
    if not roots:
        return "Empty tree\n\n0 directories, 0 files"

    root = roots[0]  # deterministic choice

    full_lines = [root] + _build(tree[root], "")

    # ------------------------------------------------------------------
    # 4. Count items
    # ------------------------------------------------------------------
    count_dirs = sum(1 for c in commands if c.startswith("mkdir -p"))
    count_files = sum(1 for c in commands if c.startswith("touch"))

    return "\n".join(full_lines) + f"\n\n{count_dirs} directories, {count_files} files"
