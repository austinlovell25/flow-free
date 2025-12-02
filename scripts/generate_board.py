#!/usr/bin/env python
from __future__ import annotations

import argparse

from flow_solver.model.game_board_generator import GameBoard


# Use this to test board generation
# ex : python -m scripts.generate_board 7 6
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a random Flow Free-style board and print it."
    )
    parser.add_argument(
        "dim",
        type=int,
        help="Board dimension (must be > 3 and < 254).",
    )
    parser.add_argument(
        "num_wires",
        type=int,
        help="Number of wires/terminal pairs (must be > 1 and <= dim).",
    )
    args = parser.parse_args()

    solved_board, _ = GameBoard.newGameBoard(args.dim, args.num_wires)
    board = solved_board.toBoard()
    for y in range(len(board.grid)):
        for x in range(len(board.grid)):
            print(board.grid[x][y], end="")
        print()


if __name__ == "__main__":
    main()


