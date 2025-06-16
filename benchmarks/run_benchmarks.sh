#!/bin/bash

# Install dependencies using uv
echo "Installing dependencies..."
uv pip install -r requirements.txt

# Run the benchmarks
echo "Running benchmarks..."
uv run run_benchmarks.py

# Open the results directory (if on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open ./plots
# Open the results directory (if on Linux)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open ./plots
fi 