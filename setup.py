from setuptools import setup, find_packages

setup(
    name="edge-sched",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "networkx>=2.8",
        "pysmt>=0.9.1",
        "z3-solver>=4.8.12.0",
        "PyYAML>=6.0",
        "matplotlib>=3.5"
    ],
    entry_points={
        "console_scripts": [
            "edge-sched=edge_sched.cli:cli"
        ]
    },
)
