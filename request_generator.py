from __future__ import annotations

import random
from typing import List


def generate_random_requests(count: int, max_block: int, seed: int | None = None) -> List[int]:
    """Generate random disk requests within the valid block range."""
    rng = random.Random(seed)
    return [rng.randint(0, max_block - 1) for _ in range(count)]


def generate_sequential_requests(start: int, count: int, step: int = 1, max_block: int = 1000) -> List[int]:
    """Generate a locally sequential request stream."""
    requests: List[int] = []
    current = start
    for _ in range(count):
        current = min(max(0, current), max_block - 1)
        requests.append(current)
        current += step
    return requests


def generate_bursty_requests(count: int, center: int, spread: int, max_block: int = 1000, seed: int | None = None) -> List[int]:
    """Generate clustered requests around a central block value."""
    rng = random.Random(seed)
    requests: List[int] = []
    for _ in range(count):
        block = int(rng.gauss(center, spread))
        block = max(0, min(block, max_block - 1))
        requests.append(block)
    return requests


if __name__ == "__main__":
    print(generate_random_requests(10, 100, seed=7))
