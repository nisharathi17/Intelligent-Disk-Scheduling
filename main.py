from __future__ import annotations

from disk import Disk
from request_generator import generate_random_requests
from scheduling_algorithms import fcfs, sstf, scan, look, c_scan
from metrics import average_seek_time, total_head_movement
from intelligent_scheduler import IntelligentDiskScheduler


def run_demo() -> None:
    requests = generate_random_requests(20, 200, seed=42)
    head = 50

    print("Generated requests:", requests)
    print("FCFS:", fcfs(requests, head))
    print("SSTF:", sstf(requests, head))
    print("SCAN:", scan(requests, head, 1, 200))
    print("LOOK:", look(requests, head, 1))
    print("C-SCAN:", c_scan(requests, head, 1, 200))

    print("Total head movement:", total_head_movement(requests, head))
    print("Average seek time:", average_seek_time(requests, head))

    scheduler = IntelligentDiskScheduler(total_blocks=200, cache_size=8)
    result = scheduler.process(requests, head)
    print("Intelligent scheduler result:", result)

    disk = Disk(total_blocks=200, head=head)
    disk.generate_sequence(requests)
    print("Disk requests recorded:", disk.requests[:10], "...")


if __name__ == "__main__":
    run_demo()
