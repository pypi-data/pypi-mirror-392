# tree2cmd/cli.py

import os
import sys
import argparse
from typing import List, Optional
from tree2cmd.parser import parse_tree
from tree2cmd.utils import tree_from_shell_commands


def read_input(path: Optional[str] = None, use_stdin: bool = False) -> str:
    if use_stdin:
        return sys.stdin.read()
    if not path:
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def convert_tree_to_commands(text: str, *, dry_run: bool = True) -> List[str]:
    parsed = parse_tree(text)
    commands: List[str] = []
    created_dirs = set()
    created_files = set()

    for path, is_dir in parsed:
        path = path.strip("/")
        if not path:
            continue

        if is_dir:
            if path not in created_dirs:
                commands.append(f'mkdir -p "{path}/"')
                created_dirs.add(path)
        else:
            parent = os.path.dirname(path)
            if parent and parent not in created_dirs:
                commands.append(f'mkdir -p "{parent}/"')
                created_dirs.add(parent)

            if path not in created_files:
                commands.append(f'touch "{path}"')
                created_files.add(path)

    return commands


def main():
    ap = argparse.ArgumentParser(description="Convert a tree (struct.txt or ASCII) into mkdir/touch commands")
    ap.add_argument("input", nargs="?", help="Input file path")
    ap.add_argument("--stdin", action="store_true", help="Read from stdin")
    ap.add_argument("--run", action="store_true", help="Execute generated commands")
    ap.add_argument("--save", help="Save commands to a shell script")
    ap.add_argument("--tree", action="store_true", help="Print reconstructed tree from generated commands")
    args = ap.parse_args()

    text = read_input(args.input, args.stdin)
    cmds = convert_tree_to_commands(text, dry_run=not args.run)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            f.write("#!/bin/sh\n\n")
            for c in cmds:
                f.write(c + "\n")

    if args.tree:
        print(tree_from_shell_commands(cmds))
        return

    if args.run:
        for c in cmds:
            os.system(c)
    else:
        for c in cmds:
            print(c)


if __name__ == "__main__":
    main()
