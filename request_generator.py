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


if __name__ == "__main__":
    random_trace = generate_random_requests(20)
    patterned_trace = generate_patterned_requests(20)

    print("Random trace:   ", random_trace)
    print("Patterned trace:", patterned_trace)