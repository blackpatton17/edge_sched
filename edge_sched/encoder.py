"""
encoder.py
Builds the variable set, hard constraints, and objective
for the edge‑scheduling SMT model.  It does *not* perform
optimisation itself – that now happens in solver_interface.py.
"""
from pysmt.shortcuts import (
    Symbol, Real, Bool, And, GE, Equals,
    Plus, Times, Ite, LE
)
from pysmt.typing import REAL, BOOL

# ---------- small helper because stable PySMT has no Sum ----------
def sum_list(exprs):
    """Return Σ exprs (0 if list empty)."""
    if not exprs:
        return Real(0)
    s = exprs[0]
    for e in exprs[1:]:
        s = Plus(s, e)
    return s
# ------------------------------------------------------------------

def build_model(instance, alpha=1, beta=1, gamma=1):
    tasks   = range(instance['num_tasks'])
    devices = instance['devices']
    m       = len(devices)

    # ---------- variables ----------
    a = {}  # assignment booleans
    s = {}  # start‑time reals
    for i in tasks:
        for j in range(m):
            a[(i, j)] = Symbol(f"a_{i}_{j}", BOOL)
        s[i] = Symbol(f"s_{i}", REAL)

    # ---------- constraints ----------
    constraints = []

    # (1) each task assigned to exactly one device
    for i in tasks:
        constraints.append(
            Equals(
                sum_list([Ite(a[(i, j)], Real(1), Real(0)) for j in range(m)]),
                Real(1),
            )
        )

    # (2) trivial capacity toy example (1 task == 1 unit load)
    for j, dev in enumerate(devices):
        load = sum_list([
            Times(Ite(a[(i, j)], Real(1), Real(0)), Real(1))
            for i in tasks
        ])
        constraints.append(LE(load, Real(dev["capacity"])))

    # ---------- objective (demo: minimise # busy devices) ----------
    obj = sum_list([
        Ite(a[(i, j)], Real(1), Real(0))
        for i in tasks for j in range(m)
    ])

    return constraints, obj, a, s
