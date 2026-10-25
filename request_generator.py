import random
from unittest import result
def generate_random_requests(n, num_tracks=200, seed=42):
    
    #Pure random requests -- no pattern at all. 
    rng = random.Random(seed) #making our own random number generator so we can control the seed for reproducibility. same seed generates same sequence everytime which is used for comparing with same data between different algos
    result = []
    for _ in range(n):
        result.append(rng.randint(0, num_tracks - 1))
    return result


def generate_patterned_requests(n, num_tracks=200, seed=42, locality_chance=0.8, jump_radius=5):
    """
    Simulates 'locality of reference': most of the time the next request
    is near the last one (like reading through a file sequentially),
    but occasionally it jumps somewhere completely different (like
    switching to a different program/file).

    This is the trace you should use for your main demo -- it's what
    makes predictive caching actually show a benefit.
    """
    rng = random.Random(seed)
    requests = [rng.randint(0, num_tracks - 1)]

    for _ in range(n - 1):
        if rng.random() < locality_chance:
            # stay local: nearby track, clamped to valid range
            offset = rng.randint(-jump_radius, jump_radius)
            next_track = requests[-1] + offset
            next_track = max(0, min(num_tracks - 1, next_track))
        else:
            # jump elsewhere entirely
            next_track = rng.randint(0, num_tracks - 1)
        requests.append(next_track)

    return requests


def generate_mixed_requests(n, seed=42, num_tracks=200, locality_chance=0.85, jump_radius=3):
    """
    Generates a mix of local access AND sequential scans.

    First half: a sequential scan, blocks 10, 11, 12, 13, ... (simulating
    a file copy or backup job streaming straight through the disk).
    Second half: patterned local access, same locality logic as
    generate_patterned_requests, re-anchored at track 10 -- the start of
    the scan -- to represent going back to the same file/region once the
    scan finishes.

    This workload demonstrates when adaptive cache (LRU+MRU) beats plain
    LRU: a plain LRU cache ends the scan holding only the last few
    scanned blocks (whatever was most recently inserted), while an
    adaptive cache switches to MRU eviction during the scan and keeps
    protecting the first few scanned blocks instead -- and those are
    exactly the blocks the second half keeps revisiting.
    """
    rng = random.Random(seed)
    scan_length = n // 2

    requests = [min(10 + i, num_tracks - 1) for i in range(scan_length)]

    anchor = 10
    second_half = [anchor]
    for _ in range(n - scan_length - 1):
        if rng.random() < locality_chance:
            offset = rng.randint(-jump_radius, jump_radius)
            next_track = second_half[-1] + offset
            next_track = max(0, min(num_tracks - 1, next_track))
        else:
            next_track = rng.randint(0, num_tracks - 1)
        second_half.append(next_track)

    if not requests:
        return second_half

    requests.extend(second_half)
    return requests


if __name__ == "__main__":
    random_trace = generate_random_requests(20)
    patterned_trace = generate_patterned_requests(20)
    mixed_trace = generate_mixed_requests(20)

    print("Random trace:   ", random_trace)
    print("Patterned trace:", patterned_trace)
    print("Mixed trace:    ", mixed_trace)