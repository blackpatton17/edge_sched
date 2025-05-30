import z3
from z3 import Real, Bool, And, Or, If, Sum, Optimize
import json


def solve_instance(input_file, alpha=1.0, beta=1.0, gamma=1.0, timeout=360, filename='output.json'):
    z3.set_param('verbose', 10)
    z3.set_param("parallel.enable", True)
    with open(input_file, 'r') as f:
        data = json.load(f)

    tasks = data["tasks"]
    edges = data["edges"]
    devices = data["devices"]
    payloads = {int(k): float(v) for k, v in data["payloads"].items()}
    deadlines = {int(k): float(v) for k, v in data.get("deadlines", {}).items()}
    n, m = len(tasks), len(devices)

    if sum(payloads.values()) > sum(dev["capacity"] for dev in devices):
        return {"status": "UNSAT", "reason": "overload"}

    

    a = {}  # assignment variables
    s = {}  # start times
    for i in tasks:
        s[i] = Real(f"s_{i}")
        for j in range(m):
            a[i, j] = Bool(f"a_{i}_{j}")

    u = {}  # utilization per device
    for j in range(m):
        u[j] = Sum([If(a[i, j], payloads[i], 0.0) for i in tasks])

    opt = Optimize()
    opt.set("timeout", timeout * 1000)  # Set timeout in ms

    top_k = 5
    for i in tasks:
        scores = [(j, devices[j]["zeta"] + devices[j]["eta"] * payloads[i]) for j in range(m)]
        best_j = [j for j, _ in sorted(scores, key=lambda x: x[1])[:top_k]]
        for j in range(m):
            if j not in best_j:
                opt.add(a[i, j] == False)

    # Task-to-one-device constraint
    for i in tasks:
        opt.add(Sum([If(a[i, j], 1, 0) for j in range(m)]) == 1)

    # Precedence constraint
    for i, k in edges:
        for j in range(m):
            latency = devices[j]["zeta"] + devices[j]["eta"] * payloads[i]
            opt.add(If(a[i, j], s[k] >= s[i] + latency, True))

    # Capacity constraint
    for j in range(m):
        total_payload = Sum([If(a[i, j], payloads[i], 0.0) for i in tasks])
        opt.add(total_payload <= devices[j]["capacity"])

    # Energy budget constraint
    for j in range(m):
        epsilon = devices[j]["epsilon"]
        delta = devices[j]["delta"]
        mu = devices[j]["mu"]
        nu = devices[j]["nu"]
        U1 = devices[j]["U1"]
        U2 = devices[j]["U2"]

        energy_j = Sum([
            If(a[i, j],
               If(u[j] < U1, epsilon * payloads[i] + delta,
               If(u[j] < U2,
                  epsilon * payloads[i] + delta + mu * (u[j] - U1),
                  epsilon * payloads[i] + delta + mu * (U2 - U1) + nu * (u[j] - U2))),
               0.0)
            for i in tasks
        ])
        opt.add(energy_j <= devices[j]["energy_budget"])

    # Deadline constraint (optional)
    for i in tasks:
        if i in deadlines:
            for j in range(m):
                latency = devices[j]["zeta"] + devices[j]["eta"] * payloads[i]
                opt.add(If(a[i, j], latency <= deadlines[i], True))

    # Total energy, latency, compute cost
    energy_terms = []
    latency_terms = []
    compute_terms = []
    for i in tasks:
        for j in range(m):
            payload = payloads[i]
            epsilon = devices[j]["epsilon"]
            delta = devices[j]["delta"]
            mu = devices[j]["mu"]
            nu = devices[j]["nu"]
            U1 = devices[j]["U1"]
            U2 = devices[j]["U2"]

            base = epsilon * payload + delta
            mid = base + mu * (u[j] - U1)
            high = base + mu * (U2 - U1) + nu * (u[j] - U2)

            energy = If(u[j] < U1, base, If(u[j] < U2, mid, high))
            latency = devices[j]["zeta"] + devices[j]["eta"] * payload
            compute = payload / devices[j]["processing_rate"]

            energy_terms.append(If(a[i, j], energy, 0.0))
            latency_terms.append(If(a[i, j], latency, 0.0))
            compute_terms.append(If(a[i, j], compute, 0.0))

    total_energy = Sum(energy_terms)
    total_latency = Sum(latency_terms)
    total_compute = Sum(compute_terms)

    opt.minimize(alpha * total_energy + beta * total_latency + gamma * total_compute)

    for i in tasks:
        opt.add(s[i] >= 0)

    with open(filename, 'w') as f:
        if opt.check() == z3.sat:
            model = opt.model()
            assignments = {}
            start_times = {}

            for i in tasks:
                for j in range(m):
                    if z3.is_true(model.evaluate(a[i, j], model_completion=True)):
                        assignments[str(i)] = j
                start_times[str(i)] = float(model.evaluate(s[i], model_completion=True).as_decimal(5).replace("?", ""))

            total_cost = float(model.evaluate(alpha * total_energy + beta * total_latency + gamma * total_compute,
                                              model_completion=True).as_decimal(5).replace("?", ""))

            json.dump({
                "status": "SAT",
                "assignments": assignments,
                "start_times": start_times,
                "total_cost": total_cost
            }, f, indent=2)
        else:
            json.dump({"status": "UNSAT"}, f, indent=2)
