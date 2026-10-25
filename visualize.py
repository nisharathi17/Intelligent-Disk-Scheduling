import matplotlib.pyplot as plt


def bar_chart_comparison(results_dict):
    """Bar chart of total head movement per scheduling algorithm."""
    names = list(results_dict.keys())
    values = list(results_dict.values())

    plt.figure(figsize=(8, 5))
    plt.bar(names, values, color="steelblue")
    plt.xlabel("Algorithm")
    plt.ylabel("Total Head Movement")
    plt.title("Head Movement by Scheduling Algorithm")
    plt.tight_layout()
    plt.show()


def plot_request_trace(requests):
    """Line plot of requested block numbers over time."""
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(requests)), requests, marker="o", markersize=3, linewidth=1)
    plt.xlabel("Request Index")
    plt.ylabel("Block / Track Number")
    plt.title("Disk Request Trace")
    plt.tight_layout()
    plt.show()


def plot_cache_hit_rate(modes_results):
    """Bar chart comparing cache hit rate across the 3 integrated modes."""
    names = list(modes_results.keys())
    hit_rates = [stats["hit_rate"] * 100 for stats in modes_results.values()]

    plt.figure(figsize=(8, 5))
    plt.bar(names, hit_rates, color="seagreen")
    plt.xlabel("Mode")
    plt.ylabel("Cache Hit Rate (%)")
    plt.title("Cache Hit Rate by Mode")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    from request_generator import generate_patterned_requests
    from metrics import compare_algorithms
    from integrated_scheduler import run_integrated_simulation

    requests = generate_patterned_requests(100, seed=42)

    bar_chart_comparison(compare_algorithms(requests, num_tracks=200, head_start=53))
    plot_request_trace(requests)
    plot_cache_hit_rate(run_integrated_simulation(requests))
