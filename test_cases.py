from __future__ import annotations

from disk import Disk
from request_generator import generate_random_requests
from scheduling_algorithms import fcfs, sstf, look, scan, c_scan
from cache import LRUCache
from predictor import BlockPredictor


def test_disk_access():
    disk = Disk(total_blocks=50, head=10)
    result = disk.access(25)
    assert result["block"] == 25
    assert disk.head == 25
    assert disk.current_track == 25


def test_cache_basic():
    cache = LRUCache(capacity=2)
    cache.put(1, "a")
    cache.put(2, "b")
    assert cache.get(1) == "a"
    assert cache.hit_rate() > 0


def test_predictor():
    predictor = BlockPredictor(history_size=5, lookahead=2)
    for value in [10, 10, 12, 10, 12]:
        predictor.update(value)
    prediction = predictor.predict_next()
    assert prediction


def test_scheduling_algorithms():
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    assert fcfs(requests, 53) == requests
    assert sstf(requests, 53)
    assert scan(requests, 53, 1, 200)
    assert look(requests, 53, 1)
    assert c_scan(requests, 53, 1, 200)


def run_all_tests():
    test_disk_access()
    test_cache_basic()
    test_predictor()
    test_scheduling_algorithms()
    print("All tests passed.")


if __name__ == "__main__":
    run_all_tests()
