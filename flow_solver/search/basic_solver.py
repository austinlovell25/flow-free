from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from flow_solver.model import Board, load_puzzle_from_file, parse_raw_puzzle

"""
Basic solver:
- Solves the puzzle by extending colors one-by-one in sequence.
"""

Coord = Tuple[int, int]


@dataclass
class PuzzleInstance:
    board: Board
    colors: List[str]
    starts: Dict[str, Coord]          # color -> start coord
    goals: Dict[str, Coord]           # color -> goal coord


def build_puzzle_instance(board: Board) -> PuzzleInstance:
    """
    Prepare a simple sequential-flow instance:
    - For each color, pick one terminal as start, the other as goal.
    """
    colors = board.colors[:]
    starts: Dict[str, Coord] = {}
    goals: Dict[str, Coord] = {}

    for color in colors:
        terminals = board.terminals[color]
        if len(terminals) != 2:
            raise ValueError(
                f"Color {color} has {len(terminals)} terminals, expected exactly 2"
            )
        # Simple choice: first is start, second is goal
        starts[color] = terminals[0]
        goals[color] = terminals[1]

    return PuzzleInstance(board=board, colors=colors, starts=starts, goals=goals)


def solve_puzzle(board: Board) -> Optional[Board]:
    """
    Solve the given puzzle using a simple depth-first search.
    """
    instance = build_puzzle_instance(board)

    if _solve_color(instance, color_index=0):
        return instance.board
    else:
        return None


def solve_puzzle_file(path: str) -> Optional[Board]:
    raw = load_puzzle_from_file(path)
    board = parse_raw_puzzle(raw)
    return solve_puzzle(board)


def _solve_color(instance: PuzzleInstance, color_index: int) -> bool:
    """
    Recursively solve colors in sequence: colors[0], then colors[1], ...
    """
    colors = instance.colors
    board = instance.board

    if color_index >= len(colors):
        # All colors are connected; check if the board is fully filled
        return _board_is_full(board)

    color = colors[color_index]
    start = instance.starts[color]
    goal = instance.goals[color]

    visited = set()
    visited.add(start)

    return _dfs_extend_color(instance, color_index, current=start, goal=goal, visited=visited)


def _dfs_extend_color(
    instance: PuzzleInstance,
    color_index: int,
    current: Coord,
    goal: Coord,
    visited: set[Coord],
) -> bool:
    """
    Depth-first search for a single color path from `current` to `goal`.

    When we reach `goal`, we move on to the next color in sequence.
    """
    board = instance.board
    color = instance.colors[color_index]

    if current == goal:
        return _solve_color(instance, color_index + 1)

    for nb in board.neighbors4(current):
        if nb in visited:
            continue

        ch = board.get(nb)

        # We can step into:
        # - an empty cell '.'
        # - the goal cell (which already has `color` on it)
        if nb == goal:
            visited.add(nb)
            if _dfs_extend_color(instance, color_index, nb, goal, visited):
                return True
            visited.remove(nb)
            continue

        # For non-goal cells, only allow empty. Dont replace already filled cells.
        if ch != '.':
            continue

        board.set(nb, color)
        visited.add(nb)

        if _dfs_extend_color(instance, color_index, nb, goal, visited):
            return True

        # Backtrack
        visited.remove(nb)
        board.set(nb, '.')

    return False


def _board_is_full(board: Board) -> bool:
    """
    Check that the board has no empty '.' cells left.
    """
    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] == '.':
                return False
    return True
