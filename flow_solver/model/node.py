from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from .board import Board

Coord = Tuple[int, int]  # (row, col)

@dataclass(order=True)
class Node:
    f: int
    g: int = field(compare=False)
    board: Board = field(compare=False)
    positions: Dict[str, Coord] = field(compare=False)  # color -> current head position
    dirs: List[List[int]] = field(compare=False)

    def pretty_print(self) -> None:
        grid = self.board.grid
        size = self.board.size
        dirs = self.dirs

        terminal_sets: Dict[str, set[Coord]] = {
            color: set(coords) for color, coords in self.board.terminals.items()
        }

        # Assign ANSI colors per pipe color
        palette = [
            "\033[31m",  # red
            "\033[32m",  # green
            "\033[34m",  # blue
            "\033[33m",  # yellow
            "\033[35m",  # magenta
            "\033[36m",  # cyan
            "\033[91m",  # bright red
            "\033[92m",  # bright green
            "\033[94m",  # bright blue
        ]
        color_keys = sorted(self.board.terminals.keys())
        color_map: Dict[str, str] = {
            color: palette[i % len(palette)] for i, color in enumerate(color_keys)
        }
        reset = "\033[0m"

        def is_connected(r: int, c: int, nr: int, nc: int, color: str, idx: int) -> bool:
            if nr < 0 or nr >= size or nc < 0 or nc >= size: #check bounds
                return False
            if grid[nr][nc] != color:
                return False

            neighbor_idx = dirs[nr][nc]
            if abs(neighbor_idx - idx) == 1:
                return True

            return False

        def pipe_char(up: bool, down: bool, left: bool, right: bool, fallback: str) -> str:
            if up and down:
                return "│"
            if left and right:
                return "─"
            if up and right:
                return "└"
            if up and left:
                return "┘"
            if down and right:
                return "┌"
            if down and left:
                return "┐"

            if up or down:
                return "│"
            if left or right:
                return "─"

        for r in range(size):
            parts: List[str] = []
            for c in range(size):
                ch = grid[r][c]
                idx = dirs[r][c]

                if ch == ".":
                    parts.append(".")
                    continue

                color = ch
                color_code = color_map.get(color, "")

                # Check if this is a terminal (start or end) - show letter character
                is_terminal = (r, c) in terminal_sets.get(color, set())
                if is_terminal:
                    parts.append(f"{color_code}{ch}{reset}")
                    continue

                # Interior pipe segment
                up = is_connected(r, c, r - 1, c, color, idx)
                down = is_connected(r, c, r + 1, c, color, idx)
                left = is_connected(r, c, r, c - 1, color, idx)
                right = is_connected(r, c, r, c + 1, color, idx)

                ch_pipe = pipe_char(up, down, left, right, color)
                parts.append(f"{color_code}{ch_pipe}{reset}")

            # Fill gaps between horizontally connected cells
            line_segments: List[str] = []
            for c in range(size):
                line_segments.append(parts[c])

                if c < size - 1:
                    gap = " "

                    # Check if cells (r, c) and (r, c+1) are part of the same horizontal pipe
                    ch_left = grid[r][c]
                    ch_right = grid[r][c + 1]
                    idx_left = dirs[r][c]
                    idx_right = dirs[r][c + 1]

                    if ch_left != "." and ch_left == ch_right:
                        color = ch_left
                        color_code = color_map.get(color, "")

                        connected = False
                        if idx_left > 0 and is_connected(r, c, r, c + 1, color, idx_left):
                            connected = True
                        elif idx_right > 0 and is_connected(r, c + 1, r, c, color, idx_right):
                            connected = True

                        if connected:
                            gap = f"{color_code}─{reset}"

                    line_segments.append(gap)

            print("".join(line_segments))
