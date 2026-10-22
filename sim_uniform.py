from rosca import solve_rosca_milp, simulate_rosca, compute_no_rosca_wait_times, solve_rosca_heuristic

N = 10
config = {
    "num_people": N,
    "init_bank": 0,
    "init_balances_vec": [0]*N,
    "wages_vec": [1000]*N,
    "goals_vec": [10000]*N,
}

no_rosca_wait_times = compute_no_rosca_wait_times(**config)
print("Wait times (no ROSCA):")
for i in range(N):
    print(f"    Person {i}: {no_rosca_wait_times[i]}")

print(f"Total wait time (no ROSCA): {sum(no_rosca_wait_times)}")

print("ROSCA resolution (uniform)")

config["time"] = max(no_rosca_wait_times)
delta_balances, wait_times, elapsed_t = solve_rosca_milp("rosca_uniform", **config)

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
