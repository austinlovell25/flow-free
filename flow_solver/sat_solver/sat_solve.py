from pysat.formula import CNF, IDPool
from pysat.solvers import Solver 
from pysat.card import CardEnc
from flow_solver.sat_solver.generate_graph import generateBoard

'''grid = [
    [".","B", "."],
    ["B",".", '.'],
    ["A",".",'A']
]'''


# GENERATE GRID
grid = generateBoard(9, 4)

R, C = len(grid), len(grid[0])
letters = sorted({c for row in grid for c in row if c != "."})
var_index = {}
var_index_rev = {}
counter = 1

def get_var(cell1, cell2, L):
    global counter
    key = tuple(sorted([cell1, cell2])) + (L,)
    if key not in var_index:
        var_index[key] = counter
        var_index_rev[counter] = key
        counter += 1
    return var_index[key]

def neighbors(r, c):
    for dr, dc in [(0,1),(1,0),(0,-1),(-1,0)]:
        rr, cc = r+dr, c+dc
        if 0 <= rr < R and 0 <= cc < C:
            yield (rr,cc)


def edge_var(r1,c1,r2,c2,L):
    # undirected: sort endpoints
    if (r1,c1) < (r2,c2):
        return get_var((r1,c1),(r2,c2),L)
    else:
        return get_var((r2,c2),(r1,c1),L)


def incident_edges(r,c,L):
    out = []
    for (rr,cc) in neighbors(r,c):
        out.append(edge_var(r,c,rr,cc,L))
    return out

def print_last_added_clause():
    clause = cnf.clauses[-1]
    readable = []
    for lit in clause:
        var = abs(lit)
        sign = '' if lit > 0 else '¬'
        # suppose var_index_inv maps variable number to meaning
        key = var_index_rev.get(var, "temp")
        readable.append(f"{sign}{key}")
    print(' OR '.join(readable))


# ------------------------------------------------------------
# 2. BUILD CNF
# ------------------------------------------------------------

cnf = CNF()


# ------------------------------------------------------------
# A. At most one letter per undirected edge
# ------------------------------------------------------------
edges = set()
for r in range(R):
    for c in range(C):
        for rr,cc in neighbors(r,c):
            if (r,c) < (rr,cc):
                edges.add(((r,c),(rr,cc)))

for (u,v) in edges:
    for i in range(len(letters)):
        e1 = get_var(u, v, letters[i])
        for j in range(i+1, len(letters)):
            L2 = letters[j]
            e2 = get_var(u, v, L2)
            cnf.append([-e1, -e2])
# ------------------------------------------------------------
# B. Cell constraints
# ------------------------------------------------------------
for r in range(R):
    for c in range(C):
        cell = grid[r][c]
        '''print("------------------------------------------------------------")
        print((r,c))
        print("------------------------------------------------------------")'''
        if cell == ".":
            T = incident_edges(r,c,letters[0])
            if len(T) == 4:
                total = []
                for L in letters:
                    total.extend(incident_edges(r,c,L))
                vpool = IDPool(start_from=counter+1)
                clauses = CardEnc.atmost(total, bound=2, encoding=1, vpool=vpool).clauses
                counter=vpool.top+1
                # print("At most 2 clause, L=., 4 edges")
                for clause in clauses:
                        cnf.append(clause)
                        # print_last_added_clause()
        for L in letters:
            T = incident_edges(r,c,L)
            readable = []
            for i in T:
                readable.append(var_index_rev[i])
            '''print("------------------------------------------------------------")
            print(readable)
            print("------------------------------------------------------------")'''
            if cell == L:
                # Endpoint of letter L: sum(T) == 1
                # at least 1
                #print("Incident", T)
                cnf.append(T[:])
                '''print("At least 1, L=L")
                print_last_added_clause()'''
                # at most 1
                # print("At most 1, L=L")
                for i in range(len(T)):
                    for j in range(i+1, len(T)):
                        cnf.append([-T[i], -T[j]])
                        # print_last_added_clause()
            elif cell == ".":
                if len(T) == 0:
                    continue
                vpool = IDPool(start_from=counter+1)
                clauses = CardEnc.atmost(T, bound=2, encoding=1, vpool=vpool).clauses
                counter=vpool.top+1
                # print("At most 2 clause, L=.")
                for clause in clauses:
                    cnf.append(clause)
                    # print_last_added_clause()
                # print("/= 1 clause, L=.")
                for i, ti in enumerate(T):
                    others = [t for j,t in enumerate(T) if j != i]
                    cnf.append([-ti] + others)
                    # print_last_added_clause()
            else:
                # Endpoint of some OTHER letter: sum(T)=0 for letter L
                T = incident_edges(r,c,L)
                # print("Exclude clauses, L/=L")
                for e in T:
                    key = 0
                    for k, v in var_index.items():
                        if v == e:
                            key = k
                            break
                    cnf.append([-e])
                    # print_last_added_clause()


# ------------------------------------------------------------
# Solve
# ------------------------------------------------------------
solver = Solver()
solver.append_formula(cnf)
sat = solver.solve()

print("SAT:", sat)

if sat:
    model = set(x for x in solver.get_model() if x > 0)
    # print(model)
    # Reconstruct solution grid with path markings
    sol = [["." for _ in range(C)] for __ in range(R)]

    # Mark endpoints
    for r in range(R):
        for c in range(C):
            if grid[r][c] != ".":
                sol[r][c] = grid[r][c]

    # Mark path cells
    for L in letters:
        for r in range(R):
            for c in range(C):
                T = incident_edges(r,c,L)
                used = sum(1 for e in T if e in model)
                if used > 0 and sol[r][c] == ".":
                    sol[r][c] = L  # mark interior of path

    print("\nSolution:")
    for row in sol:
        print(" ".join(row))