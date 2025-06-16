import glob
import json
import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd


def calculate_avg_rps(num_reqs_per_sec):
    """Calculate average requests per second from the num_reqs_per_sec dictionary"""
    total_requests = sum(num_reqs_per_sec.values())
    if not num_reqs_per_sec:
        return 0
    return total_requests / len(num_reqs_per_sec)


def plot_results(df, timestamp):
    """Create plots from the benchmark results"""
    plots_dir = "plots"
    os.makedirs(plots_dir, exist_ok=True)

    # Set style
    plt.style.use("seaborn-v0_8-darkgrid")

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

    # Plot 1: Requests per Second
    bars1 = ax1.bar(df["framework"], df["requests_per_second"], color="#2ecc71")
    ax1.set_title("Requests per Second by Framework", pad=20, fontsize=14)
    ax1.set_ylabel("Requests/Second", fontsize=12)
    ax1.grid(True, linestyle="--", alpha=0.7)

    # Add value labels on top of bars
    for bar in bars1:
        height = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}",
            ha="center",
            va="bottom",
        )

    # Plot 2: Average Response Time
    bars2 = ax2.bar(df["framework"], df["avg_response_time"], color="#e74c3c")
    ax2.set_title("Average Response Time by Framework", pad=20, fontsize=14)
    ax2.set_ylabel("Response Time (ms)", fontsize=12)
    ax2.grid(True, linestyle="--", alpha=0.7)

    # Add value labels on top of bars
    for bar in bars2:
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.1f}",
            ha="center",
            va="bottom",
        )

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(
        f"{plots_dir}/benchmark_results_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()


def analyze_results():
    results_dir = "results"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_file = f"benchmark_summary_{timestamp}.csv"

    # Initialize data for summary
    summary_data = []

    # Process each framework's results
    for result_file in glob.glob(f"{results_dir}/*.json"):
        framework = os.path.basename(result_file).split("_")[0]

        with open(result_file, "r") as f:
            data = json.load(f)

            # Calculate total metrics across all endpoints
            total_requests = sum(endpoint["num_requests"] for endpoint in data)
            total_response_time = sum(
                endpoint["total_response_time"] for endpoint in data
            )

            # Calculate average RPS across all endpoints
            all_reqs_per_sec = {}
            for endpoint in data:
                for timestamp, count in endpoint["num_reqs_per_sec"].items():
                    all_reqs_per_sec[timestamp] = (
                        all_reqs_per_sec.get(timestamp, 0) + count
                    )

            avg_rps = calculate_avg_rps(all_reqs_per_sec)
            avg_response_time = (
                total_response_time / total_requests if total_requests > 0 else 0
            )

            summary_data.append(
                {
                    "framework": framework,
                    "total_requests": total_requests,
                    "requests_per_second": avg_rps,
                    "avg_response_time": avg_response_time,
                }
            )

    # Create DataFrame and save to CSV
    df = pd.DataFrame(summary_data)
    df.to_csv(summary_file, index=False)
    print(f"\nResults saved to {summary_file}")

    # Generate plots
    plot_results(df, timestamp)
    print(f"Plots saved to plots/benchmark_results_{timestamp}.png")


if __name__ == "__main__":
    analyze_results()
