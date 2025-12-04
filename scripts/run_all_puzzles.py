#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

from flow_solver.search.heuristic_solver import (
    solve_puzzle_file as heuristic_solve_puzzle_file,
    SearchStats,
)
from flow_solver.search.basic_solver import (
    solve_puzzle_file as basic_solve_puzzle_file,
)

# Examples:
#   python -m scripts.run_all_puzzles 7
#   python -m scripts.run_all_puzzles 7 8 9
#   python -m scripts.run_all_puzzles 7 --solver basic


def run_puzzle(puzzle_path: Path, solver: str) -> Tuple[bool, SearchStats | None]:
    """Run the chosen solver on a single puzzle file and return (solved, stats)."""
    try:
        if solver == "heuristic":
            node, stats = heuristic_solve_puzzle_file(str(puzzle_path), measure_memory=False)
            solved = node is not None
            return solved, stats

        import time

        start = time.time()
        solution = basic_solve_puzzle_file(str(puzzle_path))
        elapsed = time.time() - start

        solved = solution is not None
        stats = SearchStats(
            solved=solved,
            states_expanded=0,          # basic solver doesn't track this
            time_seconds=elapsed,
            peak_memory_bytes=0,       # basic solver doesn't track this
        )
        return solved, stats

    except Exception as e:
        print(f"Error solving {puzzle_path}: {e}")
        return False, None


def process_dimension(
    dim: str,
    solver: str,
    quiet: bool,
) -> Tuple[int, int, int, int, float]:
    """
    Process all puzzles for a given dimension.

    Returns:
        total_puzzles, solved_count, failed_count, total_states, total_time
    """
    if "x" not in dim:
        dim = f"{dim}x{dim}"

    puzzle_dir = Path("puzzles") / dim
    puzzle_files = sorted(puzzle_dir.glob(f"{dim}_*.txt"))

    print(f"\n{'=' * 60}")
    print(f"Running {solver} solver on {len(puzzle_files)} puzzles in {dim}...")
    print("=" * 60)

    total_states = 0
    total_time = 0.0
    solved_count = 0

    for puzzle_file in puzzle_files:
        puzzle_name = puzzle_file.name
        if not quiet:
            print(f"\nSolving {puzzle_name}...")

        solved, stats = run_puzzle(puzzle_file, solver)

        if stats is None:
            if not quiet:
                print("  Error occurred")
            continue

        if solved:
            solved_count += 1
            total_states += stats.states_expanded
            total_time += stats.time_seconds
            if not quiet:
                if solver == "heuristic":
                    print(f"   Solved in {stats.time_seconds:.4f}s ({stats.states_expanded} states)")
                else:
                    print(f"   Solved in {stats.time_seconds:.4f}s")
        else:
            if not quiet:
                if solver == "heuristic":
                    print(f"  X No solution found ({stats.states_expanded} states)")
                else:
                    print("  X No solution found")

    total_puzzles = len(puzzle_files)
    failed_count = total_puzzles - solved_count

    # Summary for this dimension
    print(f"\n{'-' * 60}")
    print(f"SUMMARY for {dim} ({solver} solver)")
    print("-" * 60)
    print(f"Solved: {solved_count} / {total_puzzles} puzzles")

    if solved_count > 0:
        if solver == "heuristic":
            print(f"Average states expanded: {total_states / solved_count:.1f}")
        print(f"Average time: {total_time / solved_count:.4f}s")
        print(f"Total time: {total_time:.4f}s")

    return total_puzzles, solved_count, failed_count, total_states, total_time


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the Flow Free solver over all puzzles in one or more dimensions."
    )
    parser.add_argument(
        "dimensions",
        nargs="+",
        help="Dimensions like 7, 7x7, 8, 8x8, etc.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-puzzle output; only show summaries.",
    )
    parser.add_argument(
        "--solver",
        choices=["heuristic", "basic"],
        default="heuristic",
        help="Solver to use: 'heuristic' (A*) or 'basic' (DFS). Default: heuristic.",
    )
    args = parser.parse_args()

    all_total = 0
    all_solved = 0
    all_failed = 0
    all_total_states = 0
    all_total_time = 0.0

    for dim in args.dimensions:
        total, solved, failed, total_states, total_time = process_dimension(
            dim=dim,
            solver=args.solver,
            quiet=args.quiet,
        )
        all_total += total
        all_solved += solved
        all_failed += failed
        all_total_states += total_states
        all_total_time += total_time

    # Overall summary if multiple dimensions
    if len(args.dimensions) > 1:
        print(f"\n{'=' * 60}")
        print(f"OVERALL SUMMARY ({args.solver} solver)")
        print("=" * 60)
        print(f"Dimensions processed: {', '.join(args.dimensions)}")
        print(f"Total puzzles: {all_total}")
        print(f"Solved: {all_solved}")
        print(f"Failed: {all_failed}")

        if all_solved > 0:
            if args.solver == "heuristic":
                print(f"\nAverage states expanded: {all_total_states / all_solved:.1f}")
            print(f"Average time: {all_total_time / all_solved:.4f}s")
            print(f"Total time: {all_total_time:.4f}s")


if __name__ == "__main__":
    main()
