from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import heapq
import time
import tracemalloc

from flow_solver.model import Board, load_puzzle_from_file, parse_raw_puzzle, Node

Coord = Tuple[int, int]


@dataclass
class PuzzleInstance:
    board: Board
    colors: List[str]
    starts: Dict[str, Coord]
    goals: Dict[str, Coord]

@dataclass
class SearchStats:
    solved: bool
    states_expanded: int
    time_seconds: float
    peak_memory_bytes: int


def build_puzzle_instance(board: Board) -> PuzzleInstance:
    colors = board.colors[:]
    starts: Dict[str, Coord] = {}
    goals: Dict[str, Coord] = {}

    for color in colors:
        terminals = board.terminals[color]
        if len(terminals) != 2:
            raise ValueError(
                f"Color {color} has {len(terminals)} terminals, expected exactly 2"
            )
        starts[color] = terminals[0]
        goals[color] = terminals[1]

    return PuzzleInstance(board=board, colors=colors, starts=starts, goals=goals)


def solve_puzzle(board: Board, measure_memory: bool = False) -> Tuple[Optional[Node], SearchStats]:
    instance = build_puzzle_instance(board)

    positions = {color: instance.starts[color] for color in instance.colors}
    initial_board = _clone_board(instance.board)

    empty_dirs = [[0 for _ in range(initial_board.size)] for _ in range(initial_board.size)]

    start_node = Node(
        f=0,
        g=0,
        board=initial_board,
        positions=positions,
        dirs=empty_dirs,
    )

    # Start timing
    t0 = time.perf_counter()

    if measure_memory:
        tracemalloc.start()

    solution, states_expanded = _a_star_search(instance, start_node)

    # Stop timing
    t1 = time.perf_counter()
    elapsed = t1 - t0

    peak = 0
    if measure_memory:
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    stats = SearchStats(
        solved=solution is not None,
        states_expanded=states_expanded,
        time_seconds=elapsed,
        peak_memory_bytes=peak,
    )

    return solution, stats


def solve_puzzle_file(path: str, measure_memory: bool = False) -> Optional[Node]:
    raw = load_puzzle_from_file(path)
    board = parse_raw_puzzle(raw)
    return solve_puzzle(board, measure_memory)


def _a_star_search(instance: PuzzleInstance, start_node: Node) -> Tuple[Optional[Node], int]:
    # initialize the start node
    g0 = 0
    start_node.g = g0
    h0 = _heuristic(instance, start_node)
    start_node.f = g0 + h0

    # heap of the states, pop off based on the best heuristic value
    open_heap: List[Node] = [start_node]

    state_count = 0

    while open_heap:  # Attempt to expand
        node = heapq.heappop(open_heap)
        state_count += 1
        g = node.g

        # Useful to track and see how it might get stuck!!
        # if state_count % 1000 == 0:
        #     print(f"\n--- State {state_count} ---")
        #     node.pretty_print()

        if _is_goal(instance, node):
            return node, state_count  # return the full node, not just board/dirs

        # iterate over the child states from moves of the active color
        for child, move_cost in _expand(instance, node):
            g_new = g + move_cost
            h_new = _heuristic(instance, child)
            child.g = g_new
            child.f = g_new + h_new
            heapq.heappush(open_heap, child)

    return None, state_count


"""
Expand the state to get the successors.
- Successors are the states that can be reached from the current active color.
"""
def _expand(instance: PuzzleInstance, state: Node) -> List[Tuple[Node, int]]:
    board = state.board
    successors: List[Tuple[Node, int]] = []

    # moves[color] = list of legal neighbor coords for that color
    moves: Dict[str, List[Coord]] = {}

    # 1. For each color, compute its number of legal moves
    for color in instance.colors:
        if state.positions[color] == instance.goals[color]:
            continue

        current = state.positions[color]
        goal = instance.goals[color]
        legal: List[Coord] = []

        for nb in board.neighbors4(current):
            cell = board.get(nb)

            if nb == goal:
                if cell == color:
                    legal.append(nb)
            else:
                if cell == '.':
                    legal.append(nb)

        if not legal:
            return []  # dead state

        moves[color] = legal

    # Return empty list: goal reached or no moves possible for any color
    if not moves:
        return successors

    # 2. Choose a single active color: the most constrained.
    active = min(moves.keys(), key=lambda c: (len(moves[c]), c))
    goal = instance.goals[active]

    head_r, head_c = state.positions[active]

    for nb in moves[active]:
        child = _clone_state(instance, state)
        move_cost = 1

        nr, nc = nb

        prev_index = child.dirs[head_r][head_c]
        new_index = prev_index + 1
        child.dirs[nr][nc] = new_index

        if nb != goal:
            child.board.set(nb, active)

        child.positions[active] = nb


        """
        one possible Prune
        #one could be to check a 3x3 area around where the move just took place. Ensure that any "." in that area is either touching at least
        #two other "." or is touching a head of a pipe
        """

        """
        ANother prune
        check that every connection set of "." can be reached by a head of a pipe.
        """

        """
        run bfs from every head of a color and see if it can reach the end.
        """
        #!!! Maybe do the pruning here instead
        #check the 4 corners?
        # make a separate function to go do the pruning here
        if prune(instance, child, nr, nc):
            continue


        successors.append((child, move_cost))

    # return up to 3 child states
    return successors


def _heuristic(instance: PuzzleInstance, state: Node) -> int:
    # Keep the heuristic cheap: remaining blanks plus the worst-case Manhattan
    # distance from any head to its goal.
    board = state.board
    blanks = sum(row.count('.') for row in board.grid)

    max_manhattan = 0
    for color in instance.colors:
        pos = state.positions[color]
        goal = instance.goals[color]
        if pos != goal:
            d = _manhattan(pos, goal)
            if d > max_manhattan:
                max_manhattan = d
    return (blanks * 10) + max_manhattan


def _is_goal(instance: PuzzleInstance, state: Node) -> bool:
    for color in instance.colors:
        if state.positions[color] != instance.goals[color]:
            return False
    return _board_is_full(state.board)


def _board_is_full(board: Board) -> bool:
    for r in range(board.size):
        for c in range(board.size):
            if board.grid[r][c] == '.':
                return False
    return True


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _clone_board(board: Board) -> Board:
    new_grid = [row[:] for row in board.grid]
    new_terminals = {k: v[:] for k, v in board.terminals.items()}
    return Board(size=board.size, grid=new_grid, terminals=new_terminals)


def _clone_state(instance: PuzzleInstance, state: Node) -> Node:
    new_board = _clone_board(state.board)
    new_positions = dict(state.positions)
    new_dirs = [row[:] for row in state.dirs]
    return Node(
        f=state.f,
        g=state.g,
        board=new_board,
        positions=new_positions,
        dirs=new_dirs,
    )


""" PRUNING """
def prune(instance: PuzzleInstance, state: Node, nr: int, nc: int) -> bool:
    if corner_prune(instance, state, nr, nc):
        return True
    if unreachable_goal_prune(instance, state):
        return True
    if isolated_region_prune(instance, state):
        return True
    return False

def corner_prune(instance: PuzzleInstance, state: Node, nr: int, nc: int) -> bool:
    """
    From the new head position (nr, nc), look at the four diagonal cells.
    For each diagonal cell that is in-bounds and '.', check its 4 neighbors
    (up, down, left, right). If it does NOT:

      - share a border with at least two other '.' cells, OR
      - share a border with ANY head of a pipe

    then this state is pruned, return True.
    """
    board = state.board
    grid = board.grid
    size = board.size

    # set of all head positions (one per color)
    heads = set(state.positions.values())

    # set of all goal/terminal positions
    goals = set(instance.goals.values())

    diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in diagonals:
        cr = nr + dr
        cc = nc + dc

        # must be in bounds
        if not (0 <= cr < size and 0 <= cc < size):
            continue

        # only care about empty diagonal cells
        if grid[cr][cc] != '.':
            continue

        # check its 4 direct neighbors
        neighbors = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
        empty_neighbors = 0
        touches_head = False

        for rr, cc2 in neighbors:
            if 0 <= rr < size and 0 <= cc2 < size:  # check in bounds
                if grid[rr][cc2] == '.' or (rr, cc2) in goals:
                    empty_neighbors += 1
                if (rr, cc2) in heads:
                    touches_head = True

        if not (empty_neighbors >= 2 or touches_head):
            return True  # need to prune

    #do not prune
    return False


def unreachable_goal_prune(instance: PuzzleInstance, state: Node) -> bool:
    """
    If any active color has no path to its goal given current walls, prune.
    Only '.' cells are traversable; the color's goal cell is allowed as the
    final step.
    """
    board = state.board
    for color in instance.colors:
        head = state.positions[color]
        goal = instance.goals[color]
        if head == goal:
            continue
        if _shortest_path_length(board, head, goal) is None:
            return True
    return False


def isolated_region_prune(instance: PuzzleInstance, state: Node) -> bool:
    """
    '.' cells must be reachable from at least one active head. If an empty
    region is completely fenced off by existing pipes/terminals, the board
    can never be filled.
    """
    board = state.board
    size = board.size

    active_heads = [
        state.positions[color]
        for color in instance.colors
        if state.positions[color] != instance.goals[color]
    ]

    # If everything is already connected, nothing to prune here.
    if not active_heads:
        return False

    reachable = [[False for _ in range(size)] for _ in range(size)]
    q: deque[Coord] = deque()

    # Multi-source BFS starting from each active head into '.' cells only.
    for head in active_heads:
        hr, hc = head
        reachable[hr][hc] = True
        for nb in board.neighbors4(head):
            if board.get(nb) == '.' and not reachable[nb[0]][nb[1]]:
                reachable[nb[0]][nb[1]] = True
                q.append(nb)

    while q:
        r, c = q.popleft()
        for nb in board.neighbors4((r, c)):
            nr, nc = nb
            if board.get(nb) != '.' or reachable[nr][nc]:
                continue
            reachable[nr][nc] = True
            q.append(nb)

    for r in range(size):
        for c in range(size):
            if board.grid[r][c] == '.' and not reachable[r][c]:
                return True

    return False


def _shortest_path_length(board: Board, start: Coord, goal: Coord) -> Optional[int]:
    """
    Shortest path length from start to goal using only '.' cells (goal is
    allowed as the final cell). Returns None if unreachable.
    """
    if start == goal:
        return 0

    q: deque[Tuple[Coord, int]] = deque([(start, 0)])
    visited = {start}

    while q:
        (r, c), dist = q.popleft()
        for nb in board.neighbors4((r, c)):
            if nb in visited:
                continue
            cell = board.get(nb)
            if cell == '.':
                visited.add(nb)
                q.append((nb, dist + 1))
            elif nb == goal:
                return dist + 1
    return None

