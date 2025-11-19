# tree2cmd/parser.py

import re
import unicodedata
from typing import List, Tuple


# ------------------------------------------------------------
# Detect whether ASCII connectors exist (├ └ │)
# ------------------------------------------------------------
def is_ascii_tree(text: str) -> bool:
    return any(ch in text for ch in ("├", "└", "│"))


# ------------------------------------------------------------
# Count visual indent levels in ASCII tree prefixes
# Each "│   " or "    " = 1 logical indent level
# ------------------------------------------------------------
def _count_prefix_groups(prefix: str) -> int:
    if not prefix:
        return 0
    count = 0
    i = 0
    L = len(prefix)
    while i + 4 <= L:
        chunk = prefix[i : i + 4]
        if chunk == "│   " or chunk == "    ":
            count += 1
            i += 4
        else:
            i += 1
    return count


# ------------------------------------------------------------
# Convert ASCII tree → struct indent tree
# ------------------------------------------------------------
def ascii_to_struct(text: str, indent_width: int = 2) -> str:
    out_lines: List[str] = []

    for raw in text.splitlines():
        if not raw.strip():
            continue

        # Locate first connector
        m = re.search(r"[├└]", raw)
        if m:
            pos = m.start()
            prefix = raw[:pos]

            groups = _count_prefix_groups(prefix)
            depth = groups + 1

            tail = raw[pos:]

            # Remove common connector formats
            tail = re.sub(r"^[├└]\s*──\s*", "", tail)
            tail = re.sub(r"^[\s│]+", "", tail)

            name = tail.strip()

        else:
            # Fallback: treat leading whitespace as levels
            m2 = re.match(r"^([ \t]*)", raw)
            leading_ws = m2.group(1) if m2 else ""
            groups = _count_prefix_groups(leading_ws)
            depth = groups
            name = raw.strip()

        struct_line = (" " * (depth * indent_width)) + name
        out_lines.append(struct_line)

    return "\n".join(out_lines)


# ------------------------------------------------------------
# Remove tree-drawing symbols → get real node name
# ------------------------------------------------------------
def clean_name(raw: str) -> str:
    s = raw.rstrip()

    # Remove unicode tree glyphs at start
    s = re.sub(r"^[\s│├└┌─┐┬┴┼━┃╭╰╯╮\u2500-\u257F]*", "", s)

    # Remove ASCII connectors
    s = re.sub(r"^(?:[|\+\-`*>•●○\s]*)?(?:├──|└──|[|\+\-]{1,3})\s*", "", s)

    s = unicodedata.normalize("NFKC", s).strip()

    return s.rstrip("/")


# ------------------------------------------------------------
# Count indent levels (struct-style)
# ------------------------------------------------------------
def detect_indent(raw: str, indent_width: int = 2) -> int:
    m = re.match(r"^([ \t]*)", raw)
    leading_ws = m.group(1) if m else ""
    expanded = leading_ws.replace("\t", " " * indent_width)
    return len(expanded) // indent_width


# ------------------------------------------------------------
# Main parser
# ------------------------------------------------------------
def parse_tree(text: str, indent_width: int = 2) -> List[Tuple[str, bool]]:
    """
    Parse input text (ASCII or struct) → list[(path, is_dir)]
    """

    if not text.strip():
        return []

    # Convert ASCII tree → struct tree if needed
    if is_ascii_tree(text):
        text = ascii_to_struct(text, indent_width=indent_width)

    lines = [ln for ln in text.splitlines() if ln.strip()]
    results: List[Tuple[str, bool]] = []
    stack: List[str] = []

    for idx, raw in enumerate(lines):

        indent = detect_indent(raw, indent_width)
        name = clean_name(raw)

        if not name:
            continue

        next_line = lines[idx + 1] if idx + 1 < len(lines) else ""

        # Maintain stack depth
        while len(stack) > indent:
            stack.pop()

        # Determine directory status
        if raw.strip().endswith("/"):
            is_dir = True
        elif "." in name:
            is_dir = False
        else:
            is_dir = detect_indent(next_line, indent_width) > indent

        full_path = "/".join(stack + [name])

        results.append((full_path, is_dir))

        if is_dir:
            stack.append(name)

    return results
