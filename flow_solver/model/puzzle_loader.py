from __future__ import annotations
from dataclasses import dataclass
from typing import List

from .board import Board, Coord


@dataclass
class RawPuzzle:
    """Container for the lines of a puzzle file."""
    name: str
    grid_lines: List[str]


def load_puzzle_from_file(path: str) -> RawPuzzle:
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if line.strip()]

    if not lines:
        raise ValueError(f"Puzzle file {path} is empty")

    row_len = len(lines[0])
    if any(len(row) != row_len for row in lines):
        raise ValueError(f"Puzzle file {path} has non-rectangular grid")

    name = path.split("/")[-1]
    return RawPuzzle(name=name, grid_lines=lines)


def parse_raw_puzzle(raw: RawPuzzle) -> Board:
    """
    Convert a RawPuzzle into a Board.

    Conventions:
    - '.' means empty.
    - Any uppercase letter [A-Z] is treated as a color terminal.
      Pairs of the same letter are the two endpoints of that color.
    - Later we can reserve a special character (e.g., 'W') for wildcard nodes.
    """
    grid_lines = raw.grid_lines
    size = len(grid_lines)

    grid: List[List[str]] = []
    terminals: dict[str, List[Coord]] = {}

    for r, line in enumerate(grid_lines):
        row_chars = list(line)
        if len(row_chars) != size:
            raise ValueError(
                f"row {r} has length {len(row_chars)} != {size}"
            )
        grid.append(row_chars)

        for c, ch in enumerate(row_chars):
            if ch == '.':
                continue
            if ch.isalpha():
                color = ch.upper()
                if color not in terminals:
                    terminals[color] = []
                terminals[color].append((r, c))

    board = Board(size=size, grid=grid, terminals=terminals)
    return board
