from __future__ import annotations

from math import sqrt
from typing import Iterable, List


def total_head_movement(requests: Iterable[int], start: int = 0) -> int:
    """Compute total distance traveled by the disk head."""
    values = [int(block) for block in requests]
    distance = 0
    current = int(start)
    for block in values:
        distance += abs(block - current)
        current = block
    return distance


def average_seek_time(requests: Iterable[int], start: int = 0) -> float:
    values = [int(block) for block in requests]
    if not values:
        return 0.0
    return total_head_movement(values, start) / len(values)


def throughput(requests: Iterable[int], elapsed_time: float) -> float:
    values = [int(block) for block in requests]
    if elapsed_time <= 0:
        return 0.0
    return len(values) / elapsed_time


def latency_stats(requests: Iterable[int]) -> dict:
    values = [int(block) for block in requests]
    if not values:
        return {"min": 0, "max": 0, "avg": 0.0, "stddev": 0.0}
    avg = sum(values) / len(values)
    variance = sum((v - avg) ** 2 for v in values) / len(values)
    return {
        "min": min(values),
        "max": max(values),
        "avg": avg,
        "stddev": sqrt(variance),
    }


if __name__ == "__main__":
    sample = [10, 12, 50, 30]
    print(total_head_movement(sample, 0))
    print(average_seek_time(sample, 0))
