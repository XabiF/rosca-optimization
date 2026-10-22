# ROtating Savings and Credit Association ('ROSCA') optimization PoC

This project is a simple Proof-of-Concept for finding optimal [ROtating Savings and Credit Association ('ROSCA')](https://en.wikipedia.org/wiki/Rotating_savings_and_credit_association) strategies.

> Check [here](https://xabif.github.io/pub/2026-10-21-rosca-optimization) for a post explaining this project in more detail.

## Usage

- [rosca.py](rosca.py) provides the general framework for three different 'ROSCA' solvers that find the optimal configuration that minimizes the total wait time: no 'ROSCA' (trivial case of only individual savings), a MILP-formulated resolution, and a greedy heuristic algorithm.

- [sim_uniform.py](sim_uniform.py), [sim_onediff.py](sim_onediff.py) and [sim_random.py](sim_random.py) serve for simple, manual testing of the solvers under different considered 'ROSCA' scenarios.

- [study_plots.ipynb](study_plots.ipynb) makes a more systematic study of how the solutions and the run-time scales with the problem size.

These are the required Python libraries:

```
pulp
numpy
```

Optionally, for [study_plots.ipynb](study_plots.ipynb), `matplotlib` is needed.
