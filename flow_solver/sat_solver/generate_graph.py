from flow_solver.model.game_board_generator import GameBoard
from flow_solver.model.board import Board


class Node:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value
        self.neighbors = []
        self.domain = []



def generateBoard():
    solved, board = GameBoard.newGameBoard(4, 2)
    board = GameBoard.toBoard(board)
    return board
    

def board_to_graph(board, colors):
    size = len(board.grid)
    nodes = [[None for _ in range(size)] for _ in range(size)]

    for i in range(size):
        for j in range(size):
            # Create Node
            nodes[i][j] = Node(i, j, board.grid[i][j])

    for i in range(size):
        for j in range(size):

            node = nodes[i][j]

            # Assign domain to the node
            if node.value == '.':
                node.domain = list(colors)
            else:
                node.domain = [node.value]
            
            # Assign neighbors to the node
            if i > 0:
                node.neighbors.append(nodes[i-1][j])
            if i < size-1:
                node.neighbors.append(nodes[i+1][j])
            if j > 0:
                node.neighbors.append(nodes[i][j-1])
            if j < size-1:
                node.neighbors.append(nodes[i][j+1])


    return nodes

def print_graph_adj_list(graph):
    size = len(graph)

    for r in range(size):
        for c in range(size):
            node = graph[r][c]
            neigh = [(n.row, n.col) for n in node.neighbors]
            print(f"Node({r},{c}) val={node.value} domain={node.domain} → neighbors={neigh}")
        print()


if __name__ == "__main__":
   board = generateBoard()
   print(board)
   print(board.pretty_print())
   colors = board.terminals.keys()
   graph = board_to_graph(board, colors)
   print_graph_adj_list(graph)