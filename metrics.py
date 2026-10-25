from scheduling_algorithms import fcfs, sstf, look, scan


def cscan(requests, head, num_tracks=200):
    """
    Circular SCAN: sweep upward servicing requests, jump straight back
    to track 0 once the top is reached, then continue upward again --
    this keeps wait times more even than plain SCAN.
    """
    left = sorted(t for t in requests if t < head)
    right = sorted(t for t in requests if t >= head)

    order = []
    movement = 0
    current = head

    def visit(track):
        nonlocal current, movement
        movement += abs(track - current)
        current = track

    for track in right:
        visit(track)
        order.append(track)

    if left:
        visit(num_tracks - 1)
        visit(0)
        for track in left:
            visit(track)
            order.append(track)

    return order, movement


def total_head_movement(seek_sequence):
    """Sum of absolute differences between consecutive head positions."""
    movement = 0
    for prev, curr in zip(seek_sequence, seek_sequence[1:]):
        movement += abs(curr - prev)
    return movement


def average_seek_time(seek_sequence, rpm=7200, sectors_per_track=63):
    """
    Rough average seek time in ms, combining a seek-distance component
    (modeled off typical drive seek curves) with rotational latency
    derived from the given RPM.
    """
    if len(seek_sequence) < 2:
        return 0.0

    movement = total_head_movement(seek_sequence)
    num_seeks = len(seek_sequence) - 1
    avg_distance = movement / num_seeks

    # typical seek-time model: ~0.2ms per track moved, plus fixed overhead
    seek_component = 0.2 * avg_distance + 1.0

    # average rotational latency is half a revolution
    rotations_per_ms = rpm / 60000.0
    rotational_latency = 0.5 / rotations_per_ms

    return seek_component + rotational_latency


def throughput(requests, total_time):
    """Requests serviced per second."""
    if total_time <= 0:
        return 0.0
    return len(requests) / total_time


def compare_algorithms(requests, num_tracks, head_start):
    """Run FCFS, SSTF, LOOK, SCAN, C-SCAN and return total head movement for each."""
    results = {}

    _, movement = fcfs(requests, head_start)
    results["FCFS"] = movement

    _, movement = sstf(requests, head_start)
    results["SSTF"] = movement

    _, movement = look(requests, head_start, direction="up")
    results["LOOK"] = movement

    _, movement = scan(requests, head_start, num_tracks, direction="up")
    results["SCAN"] = movement

    _, movement = cscan(requests, head_start, num_tracks)
    results["C-SCAN"] = movement

    return results


if __name__ == "__main__":
    from request_generator import generate_patterned_requests

    requests = generate_patterned_requests(50, seed=42)
    results = compare_algorithms(requests, num_tracks=200, head_start=53)

    for name, movement in results.items():
        print(f"{name:7s}: {movement}")
