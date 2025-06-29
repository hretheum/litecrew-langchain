#!/bin/bash
# Run extended benchmark using existing envs

cd /Users/hretheum/dev/bezrobocie/litecrew/benchmark

# First install psutil and importlib-metadata in all envs
echo "Installing required packages in all environments..."
for env in envs/*/; do
    echo "Installing in $env"
    source "$env/bin/activate"
    pip install psutil importlib-metadata setuptools >/dev/null 2>&1
    deactivate
done

# Run the benchmark
echo "Running extended benchmark..."
python3 -m venv bench_venv
source bench_venv/bin/activate
pip install psutil rich
python3 extended_benchmark.py "$@"
deactivate