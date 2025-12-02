import random
from flow_solver.model.board import Board


# Warning: I use "Node" and "Terminal" kinda interchangably in the code here, because I can't keep a consistent vocabulary to save my life
# All function names and arguments will use "Terminal" though, to be consistent with our lab-writeup
class GameBoard:
    """
    Initializes the GameBoard class
    Don't use this unless you want a blank gameboard for some reason
    Use GameBoard.newGameBoard instead

    Arguments:
        dim: The dimensions of the board to be created
    """
    def __init__(self, dim):
        self._board = []
        self._starts = []
        self._ends = []
        self._dim = dim
        self._wires = []
        self._numWires = 0
        
        for x in range(dim):
            self._board.append([])
            for y in range(dim):
                self._board[x].append(0)
    
    """
    Creates two new GameBoard classes, representing a
    unique puzzle, and returns them as a tuple.

    Arguments:
        dim: the dimensions of the board to be created
        numWires: the number of wires to populate the board
            NOTE: Due to limitations on the algorithm I'm porting over here,
            this won't work where numWires > dim. I'm working on a solution


    Returns a tuple:
        0: The "intended" solution to the generated board
            NOTE: There may be more than one solution for a board, this
            is just the solution created by the generator
        1: A "blank" board, with only the terminals filled

    This contains a LOT of inefficiences that I will fix later
    Most of these are some bad decisions I made in the original code that I didn't bother
    to check when I ported it over to Python.
    Oops.
    """
    
    def newGameBoard(dim, numWires):
        assert(dim > 3 and dim < 254 and numWires > 1 and numWires < 254)
        # Making these lambdas to save time, prevent clutter, and reduce chances of accidental function overload
        _toSBI = lambda x: x >> 16 if x > 65535 else x >> 8 # "To Single-Bit-Identifier"
        _toSI = lambda x : x << 8 # "To Start-Identifier"
        _toEI = lambda x : x << 16 # "To End-Identifier"

        solvedBoard = GameBoard(dim)
        solvedBoard._numWires = numWires
        wires = []
        # Populate the the first n - 1 wires
        for x in range(numWires - 1):
            wires.append([])
            for y in range(dim):
                wires[x].append((x, y))
            # Populate our board
            solvedBoard._board[x][0]= _toSI(x + 1)
            for y in range(1, dim - 1):
                solvedBoard._board[x][y] = x + 1
            solvedBoard._board[x][-1]= _toEI(x + 1)
        
        # We use a "snake" methodology to populate the final wire (to ensure the board is full)
        wires.append([])
        for x in range(numWires - 1, dim):
            if (x % 2):
                # "Uprun"
                for y in range(dim - 1, -1, -1):
                    solvedBoard._board[x][y] = numWires
                    wires[numWires - 1].append((x, y))
            else:
                # "Downrun"
                for y in range(0, dim):
                    solvedBoard._board[x][y] = numWires
                    wires[numWires - 1].append((x, y))

        if ((numWires - 1) % 2):
            # We start on an "uprun", so set the starting terminal at the bottom
            solvedBoard._board[numWires - 1][dim - 1] = _toSI(numWires)
        else:
            # Inverse of above
            solvedBoard._board[numWires - 1][0] = _toSI(numWires)

        if ((dim - 1) % 2):
            # We end on an "uprun", so set the ending terminal at the top
            solvedBoard._board[dim - 1][0] = _toEI(numWires)
        else:
            # Inverse of above
            solvedBoard._board[dim - 1][dim - 1] = _toEI(numWires)
   
        
        GEN_ITERATIONS = 300 # Total number of iterations to be run during this phase
        SHRINK_THRESHOLD = 4

        # Some more lambdas
        _isEI = lambda c : solvedBoard._board[c[0]][c[1]] > 65535 # "Is End-Identifier"
        _isSI = lambda c : solvedBoard._board[c[0]][c[1]] > 255 # "Is Start-Identifier
        _isTerm = lambda c : _isSI(c)
        _isShrinkable = lambda c : _isTerm(c) and len(wires[_toSBI(solvedBoard._board[c[0]][c[1]]) - 1]) >= SHRINK_THRESHOLD
        _isMovable = lambda c : solvedBoard._board[c[0]][c[1]] == 0 or _isShrinkable(c)
        _isFree = lambda c: c[0] >= 0 and c[0] < dim and c[1] >= 0 and c[1] < dim and _isMovable(c)
        
       
        for iteration in range(GEN_ITERATIONS):
            chosenWire = random.randint(0, numWires - 1) # The wire we are altering this run
            wireCode = chosenWire + 1 # Account for our 1-indexed encoding scheme
            # Grow our selected wire
            if (random.randint(0, 1)):
                # From the head
                nodeX = wires[chosenWire][0][0]
                nodeY = wires[chosenWire][0][1]
                options = [(nodeX + 1, nodeY), (nodeX, nodeY + 1), (nodeX - 1, nodeY), (nodeX, nodeY - 1)]
                # Limit our options to "grow" to what is open
                realizedOptions = list(filter(_isFree, options))
                if len(realizedOptions) == 0:
                    # We cannot grow this wire
                    continue
                # Extend our wire to one of these options
                frontier = tuple(random.choice(realizedOptions))
                if (_isTerm(frontier)):

                    # Shrink this terminal either way
                    shrinkTermCode = solvedBoard._board[frontier[0]][frontier[1]]
                    shrinkWireIndex = _toSBI(shrinkTermCode) - 1 #Index of the terminal we've encountered
                    if (_isEI(frontier)):
                        #Shrink the tail of this opposing wire
                        wires[shrinkWireIndex] = wires[shrinkWireIndex][:-1]
                        nswx, nswy = wires[shrinkWireIndex][-1] # New Shrink Wire X, Y
                        solvedBoard._board[nswx][nswy] = shrinkTermCode
                    else:
                        #Shrink the head of this opposing wire
                        wires[shrinkWireIndex] = wires[shrinkWireIndex][1:]
                        nswx, nswy = wires[shrinkWireIndex][0] # New Shrink Wire X, Y
                        solvedBoard._board[nswx][nswy] = shrinkTermCode
                    
                solvedBoard._board[nodeX][nodeY] = wireCode
                wires[chosenWire].insert(0, frontier)
                solvedBoard._board[frontier[0]][frontier[1]] = _toSI(wireCode)
                
            else:
                # From the tail
                nodeX = wires[chosenWire][-1][0]
                nodeY = wires[chosenWire][-1][1]
                options = [(nodeX + 1, nodeY), (nodeX, nodeY + 1), (nodeX - 1, nodeY), (nodeX, nodeY - 1)]
                # Limit our options to "grow" to what is open
                realizedOptions = list(filter(_isFree, options))
                if len(realizedOptions) == 0:
                    # We cannot grow this wire
                    continue
                # Extend our wire to one of these options
                frontier = tuple(random.choice(realizedOptions))
                if (_isTerm(frontier)):
                    # Shrink this terminal either way
                    shrinkTermCode = solvedBoard._board[frontier[0]][frontier[1]]
                    shrinkWireIndex = _toSBI(shrinkTermCode) - 1 #Index of the terminal we've encountered
                    if (_isEI(frontier)):
                        #Shrink the tail of this opposing wire
                        wires[shrinkWireIndex] = wires[shrinkWireIndex][:-1]
                        nswx, nswy = wires[shrinkWireIndex][-1] # New Shrink Wire X, Y
                        solvedBoard._board[nswx][nswy] = shrinkTermCode
                    else:
                        #Shrink the head of this opposing wire
                        wires[shrinkWireIndex] = wires[shrinkWireIndex][1:]
                        nswx, nswy = wires[shrinkWireIndex][0] # New Shrink Wire X, Y
                        solvedBoard._board[nswx][nswy] = shrinkTermCode
                wires[chosenWire].append(frontier)
                solvedBoard._board[nodeX][nodeY] = wireCode
                solvedBoard._board[frontier[0]][frontier[1]] = _toEI(wireCode)
  
        
        solvedBoard._wires = [w[::] for w in wires]
        solvedBoard._starts = [w[0] for w in wires]
        solvedBoard._ends = [w[-1] for w in wires]
        return (solvedBoard, solvedBoard.cleanCopy())

    """
    Creates a "clean" copy, one with no wires; only start/endpoints

    Returns: The "clean" copy

    """
    def cleanCopy(self):
        cleanBoard = GameBoard(self._dim)
        cleanBoard._board = [b[::] for b in self._board]
        cleanBoard._starts = self._starts[::]
        cleanBoard._ends = self._ends[::]
        cleanBoard._numWires = self._numWires
        cleanBoard._wires = [[self._starts[i]] for i in range(self._numWires)]
        # Scrub the board
        for x in range(self._dim):
            for y in range(self._dim):
                if (cleanBoard._board[x][y] < 256):
                    
                    cleanBoard._board[x][y] = 0
        return cleanBoard

    """
    Creates a copy of this GameBoard's current state

    Returns: The "clean" copy

    """
    def copy(self):
        newBoard = GameBoard(self._dim)
        cleanBoard._board = [b[::] for b in self._board[::]]
        newBoard._starts = self._starts[::]
        newBoard._ends = self._ends[::]
        newBoard._numWires = self._numWires
        newBoard._wires = [w[::] for w in self._wires]

        return newBoard


    """
    Determines if a spot is "open" or not

    Arguments:
        x: The 0-indexed "x" position on the board
        y: The 0-indexed "y" position on the board
        wireIndex: The index of the wire we're currently checking as

    Returns: a boolean value, which is true if the given coord is
        a valid expansion target for this wire
    """
    def _isFree(self, x, y, wireIndex):
        if (x < 0 or x >= self._dim or y < 0 or y>= self._dim):
            return False
        boardValue = self._board[x][y]
        if (boardValue == 0):
            return True
        if (boardValue > 65535) and ((boardValue >> 16) == wireIndex + 1):
            return True
        return False

    """
    Determines if the given wire is "completed" i.e. the last node in its
    chain is the end terminal

    Arguments:
        wireIndex: The index of the wire we're checking

    Returns: A boolean value
    """
    def isWireComplete(self, wireIndex):
        return (self._wires[wireIndex][-1][0] == self._ends[wireIndex][0]
            and self._wires[wireIndex][-1][1] == self._ends[wireIndex][1])
        

    """
    Gets the available actions in the format used by the proposal document

    Returns: The two-dimensional list of actions
    """

    def getActions(self):
        actions = []
        for wireIndex in range(len(self._wires)):
            if (self.isWireComplete(wireIndex)):
                actions.append([])
                continue
            else:
                nodeX = self._wires[wireIndex][-1][0]
                nodeY = self._wires[wireIndex][-1][1]
                options = [(nodeX + 1, nodeY), (nodeX, nodeY + 1), (nodeX - 1, nodeY), (nodeX, nodeY - 1)]
                freeChecker = lambda c: self._isFree(c[0], c[1], wireIndex)
                availableActions = [tuple(i) for i in filter(freeChecker, options)]
                actions.append(availableActions)
        return actions


    """
    Takes an action, extending a wire

    Arguments:
        wireIndex: The index of the wire we're extending
        action: A 2-index tuple, representing the zero-index
            coordinates we're extending to

    """

    def takeAction(self, wireIndex, action):
        assert self._isFree(action[0], action[1], wireIndex) #Just to be safe
        assert self._manhattanDistance(self._wires[wireIndex][-1], action) == 1
        assert type(action) is tuple 
        self._wires[wireIndex].append(action)
        self._board[action[0]][action[1]] = wireIndex + 1

    


    """
    Takes an action, extending a wire, but return the updated state as a new gameboard
    For chaining purposes (if you prefer chaining in your search solutions)

    Arguments:
        wireIndex: The index of the wire we're extending
        action: A 2-index tuple, representing the zero-index
            coordinates we're extending to

    Returns:
        The updated GameBoard


    """
    def takeActionChainable(self, wireIndex, action):
        rBoard = self.copy()
        rBoard.takeAction(wireIndex, action)
        return rBoard

    """
    Caclulates the manhattan distance between two tuples
    Really only intended this for internal use
    """
    def _manhattanDistance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    """
    Getter for the board
    """
    def getBoard(self):
        return self._board

    """
    Getter for start terminals
    """
    def getStartTerminals(self):
        return self._starts

    """
    Getter for end terminals
    """
    def getEndTerminals(self):
        return self._ends

    """
    Getter for wires lists
    """
    def getWires(self):
        return self._wires

    """
    Getter for dimension
    """
    def getDim(self):
        return self._dim

    """
    Getter for number of wires
    """
    def getNumWires(self):
        return self._numWires


    """
    Getter for the wire "head"s (i.e. coordinates to the end of each wire)
    """
    def getWireHeads(self):
        return [w[-1] for w in self._wires]
        
        

    """
    Checks if the board is complete
    i.e. no holes and all wires are completed
    Does as close to a full audit as I feel like is necessary
        Does not check for double-backs in wires
    """
    def isComplete(self):
        for x in range(self._dim):
            for y in range(self._dim):
                if self._board[x][y] == 0:
                    return False
        for w in range(self._numWires):
            if (not self.isWireComplete(w)):
                print(w)
                return False
            for i in range(1, len(self._wires[w])):
                if (self._manhattanDistance(self._wires[w][i], self._wires[w][i-1]) != 1):
                    return False
        return True

    
        

    """
    Prints the board in the default format
    """
    def printBoard(self):
        for y in range(self._dim):
            for x in range(self._dim):
                n = self._board[x][y]
                if (n == 0):
                    print("   ", end = " ")
                elif (n > 65535):
                    print("(%2i)" % (n >> 16), end = "")
                elif (n > 255):
                   print("[%2i]" % (n >> 8), end = "")
                else:
                    print(" %2i " % n, end = "")
            print("")

    """
    Prints the board in a human-readable format
    """

    def prettyPrint(self):
        if (len(self._wires) >= 10):
            print("Cannot pretty print 10 or more wires!")
        _toSBI = lambda x: x >> 16 if x > 65535 else x >> 8 # "To Single-Bit-Identifier"
        printBoard = [[" ‧ " for i in range(self._dim)] for i in range(self._dim)]
        for i in range(len(self._starts)):
            printBoard[self._starts[i][0]][self._starts[i][1]] = "(" + str(i + 1) + ")"
        for i in range(len(self._wires)):
            wire = self._wires[i]
            printBoard[wire[0][0]][wire[0][1]] = "(" + str(i + 1) + ")"
            for wIndex in range(1, len(wire) - 1):
                pX = wire[wIndex - 1][0]
                pY = wire[wIndex - 1][1]
                nX = wire[wIndex + 1][0]
                nY = wire[wIndex + 1][1]
                cX = wire[wIndex][0]
                cY = wire[wIndex][1]
                repChar = " "
                if (pX == nX):
                    repChar = " │ "
                elif (pY == nY):
                    repChar = "───"
                elif ((pX > cX or nX > cX) and (pY < cY or nY < cY)):
                    #One left and one below
                    repChar = " └─"
                elif ((pX < cX or nX < cX) and (pY < cY or nY < cY)):
                    #One left and one above
                    repChar = "─┘ "

                elif ((pX > cX or nX > cX) and (pY > cY or nY > cY)):
                    #One right and one below
                    repChar = " ┌─"
                elif ((pX < cX or nX < cX) and (pY > cY or nY > cY)):
                    #One right and one above
                    repChar = "─┐ "
                else:
                    repChar = "-?-"
                printBoard[cX][cY] = repChar
            if (len(wire) > 1):
                fWX = wire[-1][0]
                fWY = wire[-1][1]
                sWX = wire[-2][0]
                sWY = wire[-2][1]
                repChar = " . "
                if (sWX < fWX):
                    repChar = "─‧ "
                elif (sWX > fWX):
                    repChar = " ‧─"
                elif (sWY < fWY):
                    repChar = " ╵ "
                else:
                    repChar = " ╷ "
                printBoard[fWX][fWY] = repChar
            

        for i in range(len(self._ends)):
            printBoard[self._ends[i][0]][self._ends[i][1]] = "[" + str(i + 1) + "]"
 
        print("┌─" + ("─+─" * self._dim) + "─┐")
        for y in range(self._dim):
            
            print("┆ ", end = "")
            for x in range(self._dim):
                print(printBoard[x][y], end = "")
            print(" ┆")
        print("└─" + ("─+─" * self._dim) + "─┘") 

    """
    Converts this GameBoard to a Board object for use with the solver.
    """
    def toBoard(self) -> Board:
        grid = [["." for _ in range(self._dim)] for _ in range(self._dim)]
        terminals = {}
        
        # Mark terminals with their corresponding letters
        for wireIndex in range(self._numWires):
            letter = chr(ord('A') + wireIndex)  # A for wire 0, B for wire 1, etc.
            terminals[letter] = []
            
            # Mark start terminal
            if wireIndex < len(self._starts):
                startX, startY = self._starts[wireIndex]
                grid[startY][startX] = letter
                terminals[letter].append((startY, startX))
            
            # Mark end terminal
            if wireIndex < len(self._ends):
                endX, endY = self._ends[wireIndex]
                grid[endY][endX] = letter
                terminals[letter].append((endY, endX))
        
        return Board(size=self._dim, grid=grid, terminals=terminals)
