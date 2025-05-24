import json
import networkx as nx
import matplotlib.pyplot as plt
import sys
import os

def load_instance(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def plot_dag(tasks, edges, output_path):
    G = nx.DiGraph()
    G.add_nodes_from(tasks)
    G.add_edges_from(edges)

    # Assign levels using topological sort
    levels = {}
    for node in nx.topological_sort(G):
        preds = list(G.predecessors(node))
        if not preds:
            levels[node] = 0
        else:
            levels[node] = max(levels[p] for p in preds) + 1

    # Group by level
    level_nodes = {}
    for node, lvl in levels.items():
        level_nodes.setdefault(lvl, []).append(node)

    # Assign positions: x based on index in level, y based on level
    pos = {}
    for level, nodes in level_nodes.items():
        for i, node in enumerate(nodes):
            x = (i - len(nodes)/2) * 2
            y = -level * 2
            pos[node] = (x, y)

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, arrows=True,
            node_color='lightsteelblue', edge_color='gray', node_size=1200, font_size=10)
    plt.title("Structured Task DAG", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"DAG plot saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vis_dag.py input.json")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = os.path.splitext(input_path)[0] + "_dag.png"
    data = load_instance(input_path)
    plot_dag(data["tasks"], data["edges"], output_path)
