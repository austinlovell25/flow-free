#!/usr/bin/env python
from __future__ import annotations

import os
import sys

# python .\generate_multiple_boards.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flow_solver.model.game_board_generator import GameBoard

def generate_puzzle_files():
    sizes = [4, 5]
    num_files = 50
    
    for size in sizes:
        folder = f"puzzles/{size}x{size}"
        os.makedirs(folder, exist_ok=True)
        
        base_wires = 2
        
        for i in range(1, num_files + 1):
            num_wires = base_wires + (i % 2)  # Cycles through base, base+1, base+2
            if num_wires < 2:
                num_wires = 2
            if num_wires > size:
                num_wires = size
            
            # Generate the board
            solved_board, puzzle_board = GameBoard.newGameBoard(size, num_wires)
            board = puzzle_board.toBoard()
            
            # Write to file
            filename = f"{folder}/{size}x{size}_{i:02d}.txt"
            with open(filename, 'w') as f:
                for row in range(len(board.grid)):
                    for col in range(len(board.grid[row])):
                        f.write(board.grid[row][col])
                    f.write('\n')
            
            print(f"Generated {filename}")

if __name__ == "__main__":
    try:
        generate_puzzle_files()
        print("All files generated successfully!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

