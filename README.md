# edge-sched

**edge-sched** is a Python-based SMT optimization tool for latency- and energy-aware task scheduling on edge devices. It takes task graphs and device profiles as input and uses Z3 to find an optimal task-to-device assignment with start times under multi-objective constraints.

---

## Features

- Task graph input (DAG) with payload sizes
- Device profiles including capacity, energy models, and latency parameters
- Piecewise energy modeling per device utilization
- Latency model based on startup time and payload-dependent cost
- Support for multi-objective optimization: energy, latency, and compute cost
- CLI tool for input generation and problem solving
- Output includes clean assignments and task start times

---

## Installation
This command creates a synthetic DAG with 10 tasks and 3 devices:
```bash
pip install -e .
```

## Usage
Solve a generated instance using Z3 SMT solver:
```bash
edge-sched generate --tasks 10 --devices 3 --output input.json --layered
```
```bash
edge-sched solve input.json --alpha 1 --beta 1 --gamma 1
```
Where:
- alpha: Weight on total energy
- beta: Weight on total latency
- gamma: Weight on compute cost

The output `output.json` will include:
- Task → device assignment
- Task start times
- Total cost minimized