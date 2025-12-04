from pysat.formula import CNF, IDPool
from pysat.solvers import Solver 
from pysat.card import CardEnc

grid = [
    ["A","B", "C"],
    [".",".", "."],
    ["A","B", "C"],
]
R, C = len(grid), len(grid[0])
letters = sorted({c for row in grid for c in row if c != "."})
var_index = {}
counter = 1

def get_var(cell1, cell2, L):
    global counter
    key = tuple(sorted([cell1, cell2])) + (L,)
    if key not in var_index:
        var_index[key] = counter
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
print(edges)

for (u,v) in edges:
    for i in range(len(letters)):
        print(i)
        e1 = get_var(u, v, letters[i])
        for j in range(i+1, len(letters)):
            print(j)
            L2 = letters[j]
            e2 = get_var(u, v, L2)
            cnf.append([-e1, -e2])
print(var_index)
# ------------------------------------------------------------
# B. Cell constraints
# ------------------------------------------------------------
for r in range(R):
    for c in range(C):
        cell = grid[r][c]

        for L in letters:
            T = incident_edges(r,c,L)
            print(r,",",c)
            print(T)
            for i in T:
                print(i)
                for k, v in var_index.items():
                    if v == i:
                        print("is",k)
                    break
            print("end")
            if cell == L:
                # Endpoint of letter L: sum(T) == 1
                # at least 1
                #print("Incident", T)
                cnf.append(T[:])
                # at most 1
                for i in range(len(T)):
                    for j in range(i+1, len(T)):
                        cnf.append([-T[i], -T[j]])
            elif cell == ".":
                if len(T) == 0:
                    continue
                vpool = IDPool(start_from=counter)
                clauses = CardEnc.atmost(T, bound=2, encoding=1, vpool=vpool).clauses
                #print("clauses",clauses)
                counter=vpool.top
                for clause in clauses:
                    cnf.append(clause)
                for i, ti in enumerate(T):
                    others = [t for j,t in enumerate(T) if j != i]
                    cnf.append([-ti] + others)
            else:
                # Endpoint of some OTHER letter: sum(T)=0 for letter L
                T = incident_edges(r,c,L)
                for e in T:
                    key = 0
                    for k, v in var_index.items():
                        if v == e:
                            key = k
                            break
                    #print("Not ", key, " on", r, ",",c)
                    cnf.append([-e])


# ------------------------------------------------------------
# Solve
# ------------------------------------------------------------
for clause in cnf.clauses:
    readable = []
    for lit in clause:
        var = abs(lit)
        sign = '' if lit > 0 else '¬'
        # suppose var_index_inv maps variable number to meaning
        key = 0
        for k, v in var_index.items():
            if v == var:
                key = k
                break
        readable.append(f"{sign}{key}")
    print(' OR '.join(readable))
solver = Solver()
solver.append_formula(cnf)
sat = solver.solve()

print("SAT:", sat)

if sat:
    model = set(x for x in solver.get_model() if x > 0)
    print(model)
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