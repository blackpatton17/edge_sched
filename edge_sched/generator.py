import random
import networkx as nx
import json
import statistics

def layered_dag(num_tasks, num_layers=3, max_edges_per_node=2):
    import math
    dag = nx.DiGraph()
    dag.add_nodes_from(range(num_tasks))

    # Split nodes into layers
    layers = [[] for _ in range(num_layers)]
    for i, node in enumerate(range(num_tasks)):
        layer_index = min(i * num_layers // num_tasks, num_layers - 1)
        layers[layer_index].append(node)

    for i in range(num_layers - 1):
        for u in layers[i]:
            fanout = random.randint(1, max_edges_per_node)
            targets = random.sample(layers[i + 1], min(fanout, len(layers[i + 1])))
            for v in targets:
                dag.add_edge(u, v)

    assert nx.is_directed_acyclic_graph(dag)
    return dag


def random_dag(num_tasks, max_fanout=3):
    dag = nx.DiGraph()
    dag.add_nodes_from(range(num_tasks))

    for i in range(num_tasks):
        possible_targets = list(range(i + 1, num_tasks))
        if not possible_targets:
            continue
        fanout = random.randint(0, min(max_fanout, len(possible_targets)))
        targets = random.sample(possible_targets, fanout)
        for j in targets:
            dag.add_edge(i, j)

    assert nx.is_directed_acyclic_graph(dag)
    return dag


def gen_devices(num_devices):
    devices = []
    for i in range(num_devices):
        devices.append({
            "id": i,
            "capacity": random.uniform(10248, 20480),  # CPU tokens
            "energy_budget": random.uniform(1000.0, 2000.0),
            "zeta": round(random.uniform(0.1, 0.5), 2),
            "eta": round(random.uniform(0.01, 0.1), 3),
            "U1": 0.3,
            "U2": 0.7,
            "epsilon": 1.0,
            "delta": 5.0,
            "mu": 2.0,
            "nu": 4.0,
            "processing_rate": round(random.uniform(5.0, 20.0), 2),
        })
    return devices


def gen_deadlines(tasks, devices, payloads, edges, slack=5.0):
    dag = nx.DiGraph()
    dag.add_nodes_from(tasks)
    dag.add_edges_from(edges)

    # Estimate base latency per device per task
    base_latency = {
        task: statistics.median([
            dev["zeta"] + dev["eta"] * payloads[str(task)] for dev in devices
        ])
        for task in tasks
    }

    deadlines = {}

    # Walk the DAG in topological order
    for task in nx.topological_sort(dag):
        preds = list(dag.predecessors(task))
        if not preds:
            earliest_start = 0
        else:
            earliest_start = max(deadlines[str(p)] for p in preds)

        # Deadline = earliest this task could start + its own runtime + slack
        deadlines[str(task)] = round(earliest_start + base_latency[task] + slack, 2)

    return deadlines


def save_json(dag, devices, filename):
    tasks = list(dag.nodes)
    edges = list(dag.edges)
    payloads = {str(task): round(random.uniform(1.0, 30.0), 2) for task in tasks}
    deadlines = gen_deadlines(tasks, devices, payloads, edges)

    data = {
        "tasks": tasks,
        "edges": edges,
        "devices": devices,
        "payloads": payloads,
        "deadlines": deadlines
    }

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
