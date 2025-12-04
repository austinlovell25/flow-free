#!/usr/bin/env python
from __future__ import annotations

import argparse
import time
from pathlib import Path

from flow_solver.model import Board
from flow_solver.model.game_board_generator import GameBoard
from flow_solver.search.basic_solver import (
    solve_puzzle as basic_solve_puzzle,
    solve_puzzle_file as basic_solve_puzzle_file,
)
from flow_solver.search.heuristic_solver import (
    solve_puzzle,
    solve_puzzle_file,
)

# python -m scripts.run_search puzzles/7x7/7x7_01.txt
# python -m scripts.run_search puzzles/7x7/7x7_01.txt --solver basic
# python -m scripts.run_search --generate --dim 7 --num-wires 6 --solver basic
# python -m scripts.run_search --generate --dim 7 --num-wires 6


def run_basic(board: Board | None = None, path: str | None = None) -> None:
    """Run the basic (DFS) solver on a board or file and print results."""
    if (board is None) == (path is None):
        raise ValueError("Exactly one of 'board' or 'path' must be provided.")

    start = time.time()
    if board is not None:
        solution = basic_solve_puzzle(board)
    else:
        solution = basic_solve_puzzle_file(path)
    elapsed = time.time() - start

    if solution is None:
        print("No solution found.")
    else:
        print("Solution found:")
        solution.pretty_print()
    print(f"Time taken: {elapsed:.4f} s")


def run_heuristic(board: Board | None = None, path: str | None = None) -> None:
    """Run the heuristic (A*) solver on a board or file and print results."""
    if (board is None) == (path is None):
        raise ValueError("Exactly one of 'board' or 'path' must be provided.")

    start = time.time()
    if board is not None:
        node, stats = solve_puzzle(board, measure_memory=False)
    else:
        node, stats = solve_puzzle_file(path, measure_memory=False)
    elapsed = time.time() - start

    if node is None:
        print("No solution found.")
    else:
        print("Solution found:")
        node.pretty_print()

    print(f"States expanded: {stats.states_expanded}")
    print(f"Time taken: {elapsed:.4f} s")
    if stats.peak_memory_bytes:
        print(f"Peak memory: {stats.peak_memory_bytes / 1024:.1f} KiB")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Flow Free search solver on a puzzle file or generate a random puzzle."
    )
    parser.add_argument(
        "puzzle_path",
        nargs="?",
        help="Path to puzzle .txt file (required if not using --generate)",
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate a random puzzle instead of loading from file.",
    )
    parser.add_argument(
        "--dim",
        type=int,
        help="Board dimension for random generation (required with --generate).",
    )
    parser.add_argument(
        "--num-wires",
        type=int,
        help="Number of wires/terminal pairs for random generation (required with --generate).",
    )
    parser.add_argument(
        "--solver",
        choices=["basic", "heuristic"],
        default="heuristic",
        help="Solver to use: 'basic' (DFS) or 'heuristic' (A*) (default: heuristic)",
    )
    args = parser.parse_args()

    # Generate a random puzzle
    if args.generate:
        if args.dim is None or args.num_wires is None:
            raise SystemExit("--dim and --num-wires are required when using --generate")

        _, clean_board = GameBoard.newGameBoard(args.dim, args.num_wires)
        board = clean_board.toBoard()

        print(f"Generated random puzzle ({args.dim}x{args.dim}, {args.num_wires} wires):")
        board.pretty_print()

        if args.solver == "basic":
            run_basic(board=board)
        else:
            run_heuristic(board=board)
        return

    # Solve from file
    if args.puzzle_path is None:
        raise SystemExit("puzzle_path is required when not using --generate")

    path = Path(args.puzzle_path)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    if args.solver == "basic":
        run_basic(path=str(path))
    else:
        run_heuristic(path=str(path))


if __name__ == "__main__":
    main()
