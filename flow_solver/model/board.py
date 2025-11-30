from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple

Coord = Tuple[int, int]  # (row, col)


@dataclass
class Board:
    """
    Simple Flow Free board representation.

    - size: board dimension N
    - grid: N x N list of characters: '.', 'A', 'B', ..., 'W' etc.
    - terminals: mapping from color_char -> list of terminal coordinates
    """
    size: int
    grid: List[List[str]]
    terminals: Dict[str, List[Coord]]

    def in_bounds(self, coord: Coord) -> bool:
        r, c = coord
        return 0 <= r < self.size and 0 <= c < self.size

    def get(self, coord: Coord) -> str:
        r, c = coord
        return self.grid[r][c]

    def set(self, coord: Coord, value: str) -> None:
        r, c = coord
        self.grid[r][c] = value

    def neighbors4(self, coord: Coord) -> List[Coord]:
        """Return the 4-connected neighbors that are in bounds."""
        r, c = coord
        candidates = [
            (r - 1, c),
            (r, c + 1),
            (r + 1, c),
            (r, c - 1),
        ]
        return [p for p in candidates if self.in_bounds(p)]

    def pretty_print(self) -> None:
        """Print the board to the console."""
        for row in self.grid:
            print("".join(row))
        print()

    @property
    def colors(self) -> List[str]:
        """Return a sorted list of color characters present on the board"""
        return sorted(self.terminals.keys())
