import os
import shutil
import subprocess
import time
from datetime import datetime

import requests


def clean_previous_results():
    """Clean up previous results and plots"""
    # Clean results directory
    results_dir = "results"
    if os.path.exists(results_dir):
        shutil.rmtree(results_dir)
    os.makedirs(results_dir)

    # Clean plots directory
    plots_dir = "plots"
    if os.path.exists(plots_dir):
        shutil.rmtree(plots_dir)
    os.makedirs(plots_dir)

    # Remove previous summary files
    for file in os.listdir("."):
        if file.startswith("benchmark_summary_") and file.endswith(".csv"):
            os.remove(file)


def wait_for_server(url, max_retries=30, retry_delay=1):
    """Wait for server to be ready"""
    for i in range(max_retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(retry_delay)
    return False


def run_server(server_file, port):
    return subprocess.Popen(
        ["uv", "run", server_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def run_locust_test(test_file, framework_name):
    # Run locust for 60 seconds with 10 users
    cmd = [
        "locust",
        "-f",
        test_file,
        "--headless",
        "--users",
        "10",
        "--spawn-rate",
        "10",
        "--run-time",
        "60s",
        "--only-summary",
        "--json",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    with open(f"{results_dir}/{framework_name}_{timestamp}.json", "w") as f:
        f.write(result.stdout)

    return result.stdout


def main():
    # Clean previous results before starting new benchmarks
    print("Cleaning previous results...")
    clean_previous_results()

    # Start all servers
    servers = []
    frameworks = {
        "fastapi": 8000,
        "flask": 8001,
        "sanic": 8002,
        "quart": 8003,
        "nexios": 8005,
    }

    # Start servers and wait for them to be ready
    for framework, port in frameworks.items():
        print(f"Starting {framework} server...")
        server_file = f"apps/{framework}_app.py"
        server = run_server(server_file, port)
        servers.append(server)

        # Wait for server to be ready
        url = f"http://127.0.0.1:{port}/"
        if wait_for_server(url):
            print(f"{framework} server is ready")
        else:
            print(f"Warning: {framework} server failed to start properly")

    try:
        # Run benchmarks
        results = {}
        for framework in frameworks:
            print(f"\nBenchmarking {framework}...")
            test_file = f"locustfiles/{framework}_test.py"
            results[framework] = run_locust_test(test_file, framework)
            print(f"Completed {framework} benchmark")

    finally:
        # Cleanup: stop all servers
        print("\nStopping servers...")
        for server in servers:
            server.terminate()
            server.wait()

        # Run analysis
        print("\nAnalyzing results...")
        subprocess.run(["uv", "run", "analyze_results.py"])


if __name__ == "__main__":
    main()
