from __future__ import annotations

from typing import Iterable, List


def fcfs(requests: Iterable[int], start: int = 0) -> List[int]:
    """First-Come, First-Served scheduling."""
    return [int(block) for block in list(requests)]


def sstf(requests: Iterable[int], start: int = 0) -> List[int]:
    """Shortest Seek Time First scheduling."""
    remaining = [int(block) for block in list(requests)]
    ordered: List[int] = []
    current = int(start)
    while remaining:
        next_block = min(remaining, key=lambda b: abs(b - current))
        remaining.remove(next_block)
        ordered.append(next_block)
        current = next_block
    return ordered


def scan(requests: Iterable[int], start: int = 0, direction: int = 1, max_block: int = 1000) -> List[int]:
    """SCAN scheduling: sweep across the disk in a single direction."""
    pending = sorted(int(block) for block in list(requests))
    ordered: List[int] = []
    current = int(start)
    if direction >= 0:
        for block in range(current, max_block):
            if block in pending:
                ordered.append(block)
        for block in range(max_block - 1, -1, -1):
            if block in pending and block < current:
                ordered.append(block)
    else:
        for block in range(current, -1, -1):
            if block in pending:
                ordered.append(block)
        for block in range(0, max_block):
            if block in pending and block > current:
                ordered.append(block)
    return ordered


def look(requests: Iterable[int], start: int = 0, direction: int = 1) -> List[int]:
    """LOOK scheduling: reverses direction only when there are remaining requests."""
    pending = sorted(int(block) for block in list(requests))
    current = int(start)
    ordered: List[int] = []
    while pending:
        if direction >= 0:
            next_b = next((b for b in pending if b >= current), None)
            if next_b is None:
                direction = -1
                continue
            pending.remove(next_b)
            ordered.append(next_b)
            current = next_b
        else:
            next_b = max((b for b in pending if b <= current), default=None)
            if next_b is None:
                direction = 1
                continue
            pending.remove(next_b)
            ordered.append(next_b)
            current = next_b
    return ordered


def c_scan(requests: Iterable[int], start: int = 0, direction: int = 1, max_block: int = 1000) -> List[int]:
    """Circular-SCAN scheduling."""
    pending = sorted(int(block) for block in list(requests))
    current = int(start)
    ordered: List[int] = []
    if direction >= 0:
        for block in range(current, max_block):
            if block in pending:
                ordered.append(block)
        for block in range(0, max_block):
            if block in pending and block < current:
                ordered.append(block)
    else:
        for block in range(current, -1, -1):
            if block in pending:
                ordered.append(block)
        for block in range(max_block - 1, -1, -1):
            if block in pending and block > current:
                ordered.append(block)
    return ordered


if __name__ == "__main__":
    sample = [10, 25, 70, 40, 5]
    print(fcfs(sample, 0))
    print(sstf(sample, 0))
