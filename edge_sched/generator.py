"""generator.py
Generate synthetic task DAGs and edge device pools.
"""
import random, itertools, json, yaml, networkx as nx

def random_dag(num_tasks:int, max_out=3, p_edge=0.3, seed=None):
    rnd = random.Random(seed)
    G = nx.DiGraph()
    G.add_nodes_from(range(num_tasks))
    for i in range(num_tasks):
        for j in range(i+1, min(num_tasks, i+1+max_out)):
            if rnd.random() < p_edge:
                G.add_edge(i, j)
    # ensure acyclic (by construction) and connectivity
    return G

def gen_devices(num_devices:int, seed=None):
    rnd = random.Random(seed)
    devices=[]
    for j in range(num_devices):
        device={
            'id': f'd{j}',
            'capacity': rnd.randint(4,16),          # CPU tokens
            'energy_budget': rnd.randint(200,400),  # arbitrary units
            'latency_base': rnd.uniform(1,5)        # ms
        }
        devices.append(device)
    return devices

def save_yaml(tasks_dag, devices, path):
    # convert edge tuples to plain lists
    edge_list = [[u, v] for u, v in tasks_dag.edges()]
    data = {
        "num_tasks": len(tasks_dag),
        "dag": edge_list,
        "devices": devices,
    }
    import yaml
    with open(path, "w") as f:
        yaml.safe_dump(data, f)

if __name__=='__main__':
    import argparse, pathlib
    ap = argparse.ArgumentParser()
    ap.add_argument('-t','--tasks',type=int,default=50)
    ap.add_argument('-d','--devices',type=int,default=10)
    ap.add_argument('-o','--output',default='instance.yaml')
    args=ap.parse_args()
    dag=random_dag(args.tasks)
    devices=gen_devices(args.devices)
    save_yaml(dag, devices, args.output)
    print('saved', args.output)
