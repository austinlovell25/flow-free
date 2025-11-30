"""
Model layer: puzzle representation and loading.

Modules:
- board: Board class that stores the grid and terminal positions.
- puzzle_loader: functions to load puzzles from text files.
"""

from .board import Board, Coord
from .puzzle_loader import load_puzzle_from_file, parse_raw_puzzle
