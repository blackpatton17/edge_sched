import random
import networkx as nx
import json

def layered_dag(num_tasks, num_layers=3, max_edges_per_node=2):
    """Generate a layered DAG with edges only flowing forward between layers."""
    import math

    dag = nx.DiGraph()
    dag.add_nodes_from(range(num_tasks))

    # Split nodes into layers
    layers = [[] for _ in range(num_layers)]
    for i, node in enumerate(range(num_tasks)):
        layer_index = min(i * num_layers // num_tasks, num_layers - 1)
        layers[layer_index].append(node)

    # Connect each node to random nodes in the next layer
    for i in range(num_layers - 1):
        for u in layers[i]:
            targets = random.sample(layers[i + 1], min(max_edges_per_node, len(layers[i + 1])))
            for v in targets:
                dag.add_edge(u, v)

    assert nx.is_directed_acyclic_graph(dag)
    return dag


def random_dag(num_tasks, max_fanout=3):
    """Generate a random DAG with a given number of tasks."""
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
    """Generate a list of devices with random parameters."""
    devices = []
    for i in range(num_devices):
        devices.append({
            "id": i,
            "capacity": random.randint(50, 100),
            "energy_budget": random.uniform(200.0, 500.0),
            "zeta": round(random.uniform(0.1, 2.0), 2),   # startup latency
            "eta": round(random.uniform(0.01, 0.1), 3),   # bandwidth delay factor
            "U1": 0.3,
            "U2": 0.7,
            "epsilon": 1.0,
            "delta": 5.0,
            "mu": 2.0,
            "nu": 4.0,
            "processing_rate": round(random.uniform(5.0, 20.0), 2),
        })
    return devices

def save_json(dag, devices, filename):
    """Save DAG and device info into a JSON file."""

    # Assign random payloads to tasks (e.g., 1.0 to 10.0 MB)
    tasks = list(dag.nodes)
    edges = list(dag.edges)
    payloads = {str(task): round(random.uniform(1.0, 30.0), 2) for task in tasks}

    data = {
        "tasks": tasks,
        "edges": edges,
        "devices": devices,
        "payloads": payloads,
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
