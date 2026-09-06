from __future__ import annotations

from typing import Dict, Iterable, List

from cache import LRUCache
from predictor import BlockPredictor
from scheduling_algorithms import fcfs, sstf, scan, look, c_scan


class IntelligentDiskScheduler:
    """Composite scheduler that uses a cache and predictive hints."""

    def __init__(self, total_blocks: int = 1000, cache_size: int = 16):
        self.total_blocks = total_blocks
        self.cache = LRUCache(cache_size)
        self.predictor = BlockPredictor(history_size=12, lookahead=4)
        self.history: List[int] = []

    def process(self, requests: Iterable[int], head: int = 0) -> Dict[str, List[int] | float | dict]:
        sequence = [int(r) for r in requests]
        for request in sequence:
            self.history.append(request)
            self.predictor.update(request)
            self.cache.put(request, {"block": request})

        predicted = self.predictor.predict_next(self.history)
        fcfs_order = fcfs(sequence, head)
        sstf_order = sstf(sequence, head)
        scan_order = scan(sequence, head, 1, self.total_blocks)
        look_order = look(sequence, head, 1)
        cscan_order = c_scan(sequence, head, 1, self.total_blocks)

        return {
            "requests": sequence,
            "predicted": predicted,
            "cache_hit_rate": self.cache.hit_rate(),
            "orders": {
                "fcfs": fcfs_order,
                "sstf": sstf_order,
                "scan": scan_order,
                "look": look_order,
                "c_scan": cscan_order,
            },
        }


if __name__ == "__main__":
    scheduler = IntelligentDiskScheduler(1000, 8)
    result = scheduler.process([98, 183, 37, 122, 14, 124, 65, 67])
    print(result)
