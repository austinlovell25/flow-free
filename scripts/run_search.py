#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from flow_solver.search.heuristic_solver import solve_puzzle_file

# python -m scripts.run_search puzzles/3x3/3x3_01.txt

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the basic Flow Free search solver on a puzzle file."
    )
    parser.add_argument("puzzle_path", help="Path to puzzle .txt file")
    args = parser.parse_args()

    path = Path(args.puzzle_path)
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    node, stats = solve_puzzle_file(str(path), measure_memory=False)
    #node, stats = solve_puzzle_file(str(path), measure_memory=True)


    if node is None:
        print("No solution found.")
    else:
        node.pretty_print()
    print(f"States expanded: {stats.states_expanded}")
    print(f"Time taken: {stats.time_seconds:.4f} s")
    if stats.peak_memory_bytes:
        print(f"Peak memory: {stats.peak_memory_bytes / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
