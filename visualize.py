from __future__ import annotations

from typing import Iterable, List


def plot_request_trace(requests: Iterable[int], title: str = "Disk Request Trace") -> None:
    """Print a lightweight textual bar chart of request blocks."""
    values = [int(block) for block in requests]
    if not values:
        print(f"{title}: no requests")
        return
    max_value = max(values)
    print(f"{title}")
    for block in values:
        bar_length = max(1, int((block / max_value) * 20)) if max_value else 1
        print("#" * bar_length + f" {block}")


if __name__ == "__main__":
    plot_request_trace([10, 20, 15, 40, 70])
