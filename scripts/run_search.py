#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from flow_solver.search.heuristic_solver import solve_puzzle, solve_puzzle_file
from flow_solver.model.game_board_generator import GameBoard

# python -m scripts.run_search puzzles/3x3/3x3_01.txt
# python -m scripts.run_search --generate --dim 7 --num-wires 6

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
    args = parser.parse_args()

    if args.generate:
        if args.dim is None or args.num_wires is None:
            raise SystemExit("--dim and --num-wires are required when using --generate")
        _, clean_board = GameBoard.newGameBoard(args.dim, args.num_wires)
        board = clean_board.toBoard()
        print(f"Generated random puzzle ({args.dim}x{args.dim}, {args.num_wires} wires):")
        board.pretty_print()
        node, stats = solve_puzzle(board, measure_memory=False)
    else:
        if args.puzzle_path is None:
            raise SystemExit("puzzle_path is required when not using --generate")
        path = Path(args.puzzle_path)
        if not path.exists():
            raise SystemExit(f"File not found: {path}")
        node, stats = solve_puzzle_file(str(path), measure_memory=False)

    if node is None:
        print("No solution found.")
    else:
        print("Solution Found:")
        node.pretty_print()
    print(f"States expanded: {stats.states_expanded}")
    print(f"Time taken: {stats.time_seconds:.4f} s")
    if stats.peak_memory_bytes:
        print(f"Peak memory: {stats.peak_memory_bytes / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
