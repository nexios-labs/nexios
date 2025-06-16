# Web Framework Benchmarks

This directory contains benchmark tests for comparing the performance of different Python web frameworks with Nexios:
- FastAPI
- Flask
- Sanic
- Quart
- Nexios

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) package manager

## Directory Structure

```
benchmarks/
├── apps/              # Framework application implementations
├── locustfiles/       # Locust test files for each framework
├── plots/            # Generated performance plots
├── results/          # Raw benchmark results
├── analyze_results.py # Analysis and plotting script
├── run_benchmarks.py  # Main benchmark runner
├── requirements.txt   # Python dependencies
├── run_benchmarks.ps1 # PowerShell script for Windows
└── run_benchmarks.sh  # Shell script for Unix-like systems
```

## Running the Benchmarks

### Windows
```powershell
.\run_benchmarks.ps1
```

### Unix-like Systems (Linux/macOS)
```bash
chmod +x run_benchmarks.sh
./run_benchmarks.sh
```

## What Gets Tested

Each framework is tested with the following endpoints:
- GET / - Simple text response
- GET /json - JSON response
- POST /echo - Echo JSON payload
- GET /delay/0.1 - Simulated delay endpoint

## Metrics Collected

- Total Requests
- Requests per Second
- Average Response Time

## Results

After running the benchmarks, you'll find:
1. A CSV summary in the root directory (`benchmark_summary_*.csv`)
2. Performance plots in the `plots` directory
3. Raw JSON results in the `results` directory

## Customization

To modify the benchmark parameters:
1. Edit `run_benchmarks.py` to change:
   - Number of users
   - Spawn rate
   - Test duration
2. Edit `locustfiles/*_test.py` to modify:
   - Request patterns
   - Test scenarios
   - Endpoints to test 