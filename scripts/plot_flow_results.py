import matplotlib.pyplot as plt

# Board sizes
sizes = [4, 5, 6, 7, 8, 9]

# Data from your summary
avg_states = [15.7, 32.2, 69.6, 190.4, 3039.9, 32160.2]
avg_time = [0.0008, 0.0026, 0.0078, 0.0291, 0.7000, 8.046]  # seconds

def main():
    # ---- Plot 1: Average states expanded vs board size ----
    plt.figure()
    plt.plot(sizes, avg_states, marker='o')
    plt.xlabel("Board size (N x N)")
    plt.ylabel("Average states expanded")
    plt.title("Average States Expanded vs Board Size")
    plt.grid(True)

    # ---- Plot 2: Average time vs board size ----
    plt.figure()
    plt.plot(sizes, avg_time, marker='o')
    plt.xlabel("Board size (N x N)")
    plt.ylabel("Average time (seconds)")
    plt.title("Average Solve Time vs Board Size")
    plt.grid(True)

    plt.show()

if __name__ == "__main__":
    main()
