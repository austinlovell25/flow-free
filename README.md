# Flow Free Solver

A Flow Free puzzle solver using A* (heuristic) and basic DFS, with pruning and simple heuristics.

All module-style scripts are run from the project root with `python -m`.

---

## Scripts

### `scripts.generate_board`

Generate and print a single random board.

**Usage:**
```bash
python -m scripts.generate_board <dim> <num_wires>
```

**Example:**
```bash
python -m scripts.generate_board 7 6
```

---

### `generate_multiple_boards.py`

Generate many puzzles and save them under `puzzles/`.

**Usage (run directly):**
```bash
python generate_multiple_boards.py
```

Creates multiple puzzles for several dimensions (e.g., 6x6–10x10).

---

### `scripts.show_puzzle`

Display a puzzle file: size, grid, and terminal positions.

**Usage:**
```bash
python -m scripts.show_puzzle <puzzle_path>
```

**Example:**
```bash
python -m scripts.show_puzzle puzzles/7x7/7x7_01.txt
```

---

### `scripts.run_search`

Solve a single puzzle or generate and solve a random one.

**Usage:**
```bash
# Solve a puzzle (default = heuristic solver)
python -m scripts.run_search <puzzle_path>

# Use the basic solver (DFS)
python -m scripts.run_search <puzzle_path> --solver basic

# Generate + solve
python -m scripts.run_search --generate --dim <dim> --num-wires <num_wires>

# Generate + basic solver
python -m scripts.run_search --generate --dim <dim> --num-wires <num_wires> --solver basic
```

**Examples:**
```bash
python -m scripts.run_search puzzles/7x7/7x7_01.txt
python -m scripts.run_search puzzles/7x7/7x7_01.txt --solver basic

python -m scripts.run_search --generate --dim 7 --num-wires 6
python -m scripts.run_search --generate --dim 7 --num-wires 6 --solver basic
```

Outputs the puzzle (if generated), the solution if found, and statistics such as states expanded, time, and memory.

---

### `scripts.run_all_puzzles`

Run the solver over all puzzles for one or more dimensions and show summaries.

**Usage:**
```bash
# Single dimension
python -m scripts.run_all_puzzles <dim>

# Multiple dimensions
python -m scripts.run_all_puzzles <dim1> <dim2> <dim3> ...

# Basic solver
python -m scripts.run_all_puzzles <dim> --solver basic

# Quiet mode (summary only)
python -m scripts.run_all_puzzles <dim> --quiet
```

**Examples:**
```bash
python -m scripts.run_all_puzzles 7
python -m scripts.run_all_puzzles 7 8 9
python -m scripts.run_all_puzzles 7x7 8x8

python -m scripts.run_all_puzzles 7 --solver basic
python -m scripts.run_all_puzzles 7 8 9 --solver basic --quiet
```

Outputs per-puzzle results (unless `--quiet`) and summary stats across all puzzles run.

---

## Puzzle Format

Puzzle files use:

- `.` → empty cell  
- `A, B, C, ...` → terminals (each letter appears exactly twice)  
- Filenames: `{dim}x{dim}_{index}.txt` (e.g., `7x7_01.txt`)

Generated puzzles are guaranteed to contain at least one valid solution (the generation path).
