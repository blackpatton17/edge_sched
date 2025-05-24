import z3
from z3 import Real, Bool, And, Or, If, Sum, Optimize
import json

def solve_instance(input_file, alpha=1.0, beta=1.0, gamma=1.0, timeout=60, filename='output.json'):
    z3.set_param('verbose', 10)
    with open(input_file, 'r') as f:
        data = json.load(f)

    tasks = data["tasks"]
    edges = data["edges"]
    devices = data["devices"]
    payloads = {int(k): float(v) for k, v in data["payloads"].items()}
    n, m = len(tasks), len(devices)

    if sum(payloads.values()) > sum(dev["capacity"] for dev in devices):
        return {"status": "UNSAT", "reason": "overload"}

    a = {}
    s = {}
    for i in tasks:
        s[i] = Real(f"s_{i}")
        for j in range(m):
            a[i, j] = Bool(f"a_{i}_{j}")

    # Total payload assigned to each device (utilization)
    u = {}
    for j in range(m):
        u[j] = Sum([If(a[i, j], payloads[i], 0.0) for i in tasks])

    opt = Optimize()

    # Assignment constraints
    for i in tasks:
        opt.add(Sum([If(a[i, j], 1, 0) for j in range(m)]) == 1)

    # Precedence constraints
    for i, k in edges:
        for j in range(m):
            latency = devices[j]["zeta"] + devices[j]["eta"] * payloads[i]
            opt.add(If(a[i, j], s[k] >= s[i] + latency, True))


    # Capacity constraint based on total payload per device
    for j in range(m):
        total_payload = Sum([
            If(a[i, j], payloads[i], 0.0) for i in tasks
        ])
        opt.add(total_payload <= devices[j]["capacity"])

    
    energy_terms = []
    for i in tasks:
        for j in range(m):
            epsilon = devices[j]["epsilon"]
            delta = devices[j]["delta"]
            mu = devices[j]["mu"]
            nu = devices[j]["nu"]
            U1 = devices[j]["U1"]
            U2 = devices[j]["U2"]

            payload = payloads[i]
            base = epsilon * payload + delta
            mid = base + mu * (u[j] - U1)
            high = base + mu * (U2 - U1) + nu * (u[j] - U2)

            # Piecewise function for energy cost
            piecewise_energy = If(u[j] < U1, base,
                                  If(u[j] < U2, mid, high))

            energy_terms.append(If(a[i, j], piecewise_energy, 0.0))
            # energy = epsilon * payloads[i] + delta
            # energy_terms.append(If(a[i, j], energy, 0.0))

    total_energy = Sum(energy_terms)

    latency_terms = [
        If(a[i, j], devices[j]["zeta"] + devices[j]["eta"] * payloads[i], 0.0)
        for i in tasks for j in range(m)
    ]

    total_latency = Sum(latency_terms)

    total_compute = Sum([
        If(a[i, j], payloads[i] / devices[j]["processing_rate"], 0.0)
        for i in tasks for j in range(m)
    ])

    # Objective: placeholder costs
    # total_energy = Sum([If(a[i, j], 1.0, 0.0) for i in tasks for j in range(m)])
    # total_latency = Sum([If(a[i, j], 1.0, 0.0) for i in tasks for j in range(m)])
    # total_compute = Sum([If(a[i, j], 1.0, 0.0) for i in tasks for j in range(m)])

    obj = alpha * total_energy + beta * total_latency + gamma * total_compute
    for i in tasks:
        opt.add(s[i] >= 0)
    opt.minimize(obj)

    with open(filename, 'w') as f:
        if opt.check() == z3.sat:
            model = opt.model()
            assignments = {}
            start_times = {}

            for i in tasks:
                for j in range(m):
                    val = model.evaluate(a[i, j], model_completion=True)
                    if z3.is_true(val):
                        assignments[str(i)] = j

                s_val = model.evaluate(s[i], model_completion=True)
                start_times[str(i)] = float(s_val.as_decimal(5).replace("?", ""))

            # Evaluate total cost from objective expression
            total_cost_val = model.evaluate(obj, model_completion=True)
            total_cost = float(total_cost_val.as_decimal(5).replace("?", ""))

            json.dump({
                "status": "SAT",
                "assignments": assignments,
                "start_times": start_times,
                "total_cost": total_cost
            }, f, indent=2)
            return

        else:
            json.dump({
                "status": "UNSAT"
            }, f, indent=2)
            return

