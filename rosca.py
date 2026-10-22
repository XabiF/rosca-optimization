import pulp
import math
import numpy as np
from time import perf_counter

def solve_rosca_milp(name, num_people, init_bank, init_balances_vec, wages_vec, goals_vec, time):
    start_t = perf_counter()
    prob = pulp.LpProblem("ROSCA", sense=pulp.LpMaximize)

    dp_i_t = [[pulp.LpVariable(f"dp_{i}_{t}") for i in range(num_people)] for t in range(time)]
    a_i_t = [[pulp.LpVariable(f"a_{i}_{t}", cat=pulp.LpBinary) for i in range(num_people)] for t in range(time)]

    p_i_last = init_balances_vec[:]
    q_i_last = p_i_last[:]
    B_last = init_bank
    weights_vec = []
    for t in range(time):
        dp_i_cur = [dp_i_t[t][i] for i in range(num_people)]
        a_i_cur = [a_i_t[t][i] for i in range(num_people)]

        p_i_cur = [p_i_last[i] + dp_i_cur[i] + wages_vec[i] for i in range(num_people)]
        q_i_cur = [p_i_last[i] + dp_i_cur[i] + wages_vec[i] - a_i_cur[i] * goals_vec[i] for i in range(num_people)]
        B_cur = B_last - pulp.lpSum(dp_i_cur)

        prob += B_cur >= 0
        for i in range(num_people):
            prob += q_i_last[i] + dp_i_cur[i] + wages_vec[i] >= 0
            prob += a_i_cur[i] <= p_i_cur[i] / goals_vec[i]
            if t > 1:
                prob += a_i_cur[i] >= a_i_t[t-1][i]
        
        p_i_last = p_i_cur
        q_i_last = q_i_cur
        B_last = B_cur
 
    prob += pulp.lpSum(a_i_t[t][i] for i in range(num_people) for t in range(time))

    # prob.writeLP(f"{name}_pulp_tmp.lp")
    prob.solve(pulp.COIN_CMD(msg=False))

    delta_balances_values = [[pulp.value(dp_i_t[t][i]) for i in range(num_people)] for t in range(time)]
    a_values = [[int(pulp.value(a_i_t[t][i])) for i in range(num_people)] for t in range(time)]

    # Using time+1 since we want wait times to begin by 1 (goal at t=0 means it took 1 time-step to achieve it)
    wait_times = [(time + 1) - sum(a_values[t][i] for t in range(time)) for i in range(num_people)]
    end_t = perf_counter()

    return delta_balances_values, wait_times, end_t-start_t

def simulate_rosca(num_people, init_bank, init_balances_vec, wages_vec, goals_vec, time, delta_balances):
    last_balances_vec = init_balances_vec[:]
    last_bank = init_bank
    times_of_goal_reached = [None]*num_people

    print("ROSCA SIMULATION")

    for t in range(time):
        print(f" TIME-STEP t={t}:")
        delta_balances_vec = [delta_balances[t][i] for i in range(num_people)]
        new_balances_vec = [last_balances_vec[i] + delta_balances_vec[i] + wages_vec[i] for i in range(num_people)]
        new_bank = last_bank - sum(delta_balances_vec)

        print(f"  Bank currently has {last_bank}€")

        for i in range(num_people):
            reached_now = (new_balances_vec[i] >= goals_vec[i]) and (times_of_goal_reached[i] is None)

            c = "*" if ((times_of_goal_reached[i] is not None) or reached_now) else "-"
            if delta_balances[t][i] >= 0:
                print(f"   {c} Person {i} (currently has {last_balances_vec[i]}€) earns {wages_vec[i]}€ and takes {delta_balances[t][i]}€ from the bank (now has {new_balances_vec[i]}€)")
            else:
                print(f"   {c} Person {i} (currently has {last_balances_vec[i]}€) earns {wages_vec[i]}€ and deposits {-delta_balances[t][i]}€ in the bank (now has {new_balances_vec[i]}€)")

            if reached_now:
                new_balances_vec[i] -= goals_vec[i]
                print(f"      Goal of {goals_vec[i]}€ reached! Purchased, now has {new_balances_vec[i]}€")
                times_of_goal_reached[i] = t+1

        print(f"  Bank is left with {new_bank}€")

        last_balances_vec = new_balances_vec
        last_bank = new_bank

        for i in range(num_people):
            assert new_balances_vec[i] >= 0, f"Balance of person {i} cannot be in debt! (value at t={t}: {new_balances_vec[i]}€)"
        assert new_bank >= 0, f"Bank cannot be in debt! (value at t={t}: {new_bank}€)"

    print(f"Goal reach wait times: {times_of_goal_reached}, total wait time = {sum(times_of_goal_reached)}")

def compute_no_rosca_wait_times(num_people, init_balances_vec, wages_vec, goals_vec, **kwargs):
    return [math.ceil((goals_vec[i] - init_balances_vec[i]) / wages_vec[i]) for i in range(num_people)]

def solve_rosca_heuristic(num_people, init_bank, init_balances_vec, wages_vec, goals_vec, time):
    start_t = perf_counter()

    no_rosca_wait_times = compute_no_rosca_wait_times(num_people, init_balances_vec, wages_vec, goals_vec)
    x = np.argsort(no_rosca_wait_times)
    ordered_people = np.array(list(range(num_people)))[x]

    wait_times = [None]*num_people
    all_money_per_step = sum(wages_vec)

    last_person = None
    person_had_fract_step = [False]*num_people
    last_person_fract_money = 0
    delta_balances = []
    for k in ordered_people:
        rem_money = goals_vec[k] - init_balances_vec[k]

        if not np.allclose(last_person_fract_money, 0):
            # Spend shared step with previous person
            delta_balances_vec = [- wages_vec[i] for i in range(num_people)]
            for i in range(num_people):
                if i == last_person:
                    delta_balances_vec[i] += last_person_fract_money
                elif i == k:
                    delta_balances_vec[i] += all_money_per_step - last_person_fract_money
                    rem_money -= (all_money_per_step - last_person_fract_money)
            last_person_fract_money = 0
            delta_balances.append(delta_balances_vec)
            wait_times[last_person] += 1

        # Compute number of cycles needed
        wait_time_raw = rem_money / all_money_per_step

        wait_time_fract, wait_time_int = math.modf(wait_time_raw)
        wait_time_int = int(wait_time_int)

        # Full steps of money to person k
        for t in range(wait_time_int):
            delta_balances_vec = [- wages_vec[i] for i in range(num_people)]
            for i in range(num_people):
                if i == k:
                    delta_balances_vec[i] += all_money_per_step
            delta_balances.append(delta_balances_vec)

        wait_times[k] = len(delta_balances)

        # Fractional step
        last_person = k
        last_person_fract_money = wait_time_fract * all_money_per_step

    if last_person_fract_money > 0:
        # Spend last "fractional" step
        delta_balances_vec = [0]*num_people
        for i in range(num_people):
            if i == last_person:
                delta_balances_vec[i] = all_money_per_step - wages_vec[last_person]
            else:
                delta_balances_vec[i] = - wages_vec[i]
        delta_balances.append(delta_balances_vec)
        wait_times[last_person] += 1

    # The heuristic can sometimes end its logic faster than the considered time-step cound
    # (this does not mean the aggregate wait time is optimal or better than other solvers!)
    while len(delta_balances) < time:
        delta_balances.append([0]*num_people)

    end_t = perf_counter()

    return delta_balances, wait_times, end_t-start_t
