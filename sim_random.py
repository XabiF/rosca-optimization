from rosca import solve_rosca_milp, simulate_rosca, compute_no_rosca_wait_times, solve_rosca_heuristic
import numpy as np

N = 10
config = {
    "num_people": N,
    "init_bank": np.random.randint(low=0, high=1000+1),
    "init_balances_vec": np.random.randint(low=0, high=3000+1, size=N),
    "wages_vec": np.random.randint(low=800, high=1600, size=N),
    "goals_vec": np.random.randint(low=8000, high=16000, size=N),
}

no_rosca_wait_times = compute_no_rosca_wait_times(**config)
print("Wait times (no ROSCA):")
for i in range(N):
    print(f"    Person {i}: {no_rosca_wait_times[i]}")

print(f"Total wait time (no ROSCA): {sum(no_rosca_wait_times)}")

print("ROSCA resolution (random)")

config["time"] = max(no_rosca_wait_times)
delta_balances, wait_times, elapsed_t = solve_rosca_milp("rosca_onediff", **config)

print(f"Wait times (ROSCA-MILP, elapsed time = {elapsed_t:.3f}s):")
for i in range(N):
    print(f"    Person {i}: {wait_times[i]}")

print(f"Total wait time (ROSCA-MILP): {sum(wait_times)}")

print("#############################################################################################")
simulate_rosca(**config, delta_balances=delta_balances)
print("#############################################################################################")

delta_balances, wait_times, elapsed_t = solve_rosca_heuristic(**config)

print(f"Wait times (ROSCA-heuristic, elapsed time = {elapsed_t:.3f}s):")
for i in range(N):
    print(f"    Person {i}: {wait_times[i]}")

print(f"Total wait time (ROSCA-heuristic): {sum(wait_times)}")

print("#############################################################################################")
simulate_rosca(**config, delta_balances=delta_balances)
print("#############################################################################################")
