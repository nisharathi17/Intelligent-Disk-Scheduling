from scheduling_algorithms import fcfs, sstf, look, scan
from request_generator import generate_patterned_requests

# The same worked example used in scheduling_algorithms.py's demo block,
# so these numbers can be hand-checked and cross-referenced.
REQUESTS = [98, 183, 37, 122, 14, 124, 65, 67]
HEAD = 53
NUM_TRACKS = 200


def test_fcfs_preserves_arrival_order():
    order, _ = fcfs(REQUESTS, HEAD)
    assert order == REQUESTS  # FCFS must never reorder anything


def test_fcfs_known_movement():
    _, movement = fcfs(REQUESTS, HEAD)
    assert movement == 640


def test_sstf_known_movement():
    _, movement = sstf(REQUESTS, HEAD)
    assert movement == 236


def test_sstf_always_services_every_request():
    order, _ = sstf(REQUESTS, HEAD)
    assert sorted(order) == sorted(REQUESTS)  # nothing lost, nothing duplicated


def test_look_known_movement():
    _, movement = look(REQUESTS, HEAD, direction="up")
    assert movement == 299


def test_scan_known_movement():
    _, movement = scan(REQUESTS, HEAD, NUM_TRACKS, direction="up")
    assert movement == 331


def test_scan_never_beats_look():
    """
    The key structural property: SCAN always does everything LOOK does,
    plus an extra round trip to the disk edge. So for ANY set of
    requests, scan's total movement must be >= look's. If this test
    ever failed, it would mean one of the two implementations has a bug.
    """
    _, look_movement = look(REQUESTS, HEAD, direction="up")
    _, scan_movement = scan(REQUESTS, HEAD, NUM_TRACKS, direction="up")
    assert scan_movement >= look_movement


def test_scan_never_beats_look_on_random_traces():
    """
    Same property as above, but checked against several traces from
    Step 2's generator instead of one hand-picked example -- this is
    how you gain confidence a property holds in general, not just for
    one convenient case.
    """
    for seed in range(5):
        trace = generate_patterned_requests(40, num_tracks=NUM_TRACKS, seed=seed)
        _, look_movement = look(trace, HEAD, direction="up")
        _, scan_movement = scan(trace, HEAD, NUM_TRACKS, direction="up")
        assert scan_movement >= look_movement


def test_smart_algorithms_beat_fcfs_on_this_example():
    _, fcfs_movement = fcfs(REQUESTS, HEAD)
    _, sstf_movement = sstf(REQUESTS, HEAD)
    _, look_movement = look(REQUESTS, HEAD, direction="up")
    assert sstf_movement < fcfs_movement
    assert look_movement < fcfs_movement


if __name__ == "__main__":
    test_fcfs_preserves_arrival_order()
    test_fcfs_known_movement()
    test_sstf_known_movement()
    test_sstf_always_services_every_request()
    test_look_known_movement()
    test_scan_known_movement()
    test_scan_never_beats_look()
    test_scan_never_beats_look_on_random_traces()
    test_smart_algorithms_beat_fcfs_on_this_example()
    print("All tests passed!")