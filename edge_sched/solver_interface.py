"""
solver_interface.py
High‑level wrapper: read YAML → build model → branch‑and‑bound
to minimise the objective using a plain SMT solver.
"""
import yaml, json
from pysmt.shortcuts import Solver, Real, LE
from edge_sched.encoder import build_model

def solve_instance(path, alpha=1, beta=1, gamma=1, timeout=60):
    data = yaml.safe_load(open(path))

    # Build constraints & objective
    constraints, obj, a_vars, _ = build_model(data, alpha, beta, gamma)

    solver = Solver(name="z3")

    for c in constraints:
        solver.add_assertion(c)

    best_cost   = None
    best_assign = None

    # --- simple integer branch‑and‑bound loop ---
    while True:
        if not solver.solve():
            break   # UNSAT with current bound → last model was optimal

        model     = solver.get_model()
        cost_val = model.get_value(obj).constant_value()

        # record best
        best_cost   = cost_val
        best_assign = {
            (i, j): model.get_value(var).is_true()
            for (i, j), var in a_vars.items()
        }

        # tighten bound: obj ≤ best‑1   (cost is integer here)
        solver.add_assertion(LE(obj, Real(cost_val - 1)))

    if best_assign is None:
        return {"status": "unsat"}

    # extract task→device mapping
    assignment = {}
    for (i, j), truth in best_assign.items():
        if truth:
            assignment[i] = data["devices"][j]["id"]

    return {
        "status":     "opt",
        "best_cost":  float(best_cost),
        "assignment": assignment,
    }
