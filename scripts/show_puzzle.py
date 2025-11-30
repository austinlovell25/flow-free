#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from flow_solver.model import load_puzzle_from_file, parse_raw_puzzle


# python -m scripts.show_puzzle puzzles/examples/demo_5x5_01.txt

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load a Flow Free puzzle and print basic info."
    )
    parser.add_argument("puzzle_path", help="Path to puzzle .txt file")
    args = parser.parse_args()

    path = Path(args.puzzle_path)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    raw = load_puzzle_from_file(str(path))
    board = parse_raw_puzzle(raw)

    print(f"Puzzle name: {raw.name}")
    print(f"Board size: {board.size}x{board.size}")
    print("Grid:")
    board.pretty_print()

    print("Terminals:")
    for color in board.colors:
        coords = board.terminals[color]
        print(f"  {color}: {coords}")


if __name__ == "__main__":
    main()
