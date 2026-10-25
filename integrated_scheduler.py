from disk import Disk
from cache import LRUCache, AdaptiveCache
from predictor import Predictor
from scheduling_algorithms import sstf


def _plain_sstf(requests, head_start, num_tracks):
    order, movement = sstf(requests, head_start)
    return {
        "head_movement": movement,
        "hit_rate": 0.0,
        "seeks_avoided": 0,
    }


def _sstf_with_cache(requests, head_start, num_tracks, cache_size, use_predictor, cache_cls=LRUCache):
    """
    Service requests as they actually arrive, one at a time (an OS
    can't batch-sort requests it hasn't received yet, unlike the
    idealized 'Plain SSTF' baseline which gets to see the whole trace
    up front). Each request first checks the cache; on a hit the head
    doesn't move at all, so whatever seek that request would have cost
    is avoided outright. On a miss, the disk head seeks directly there.
    If use_predictor is set, prefetch the Markov predictor's guesses
    into the cache after each real request, so later requests have a
    better chance of already being cached. `cache_cls` selects which
    cache implementation backs this run (plain LRU or AdaptiveCache).
    """
    disk = Disk(num_tracks=num_tracks, head_start=head_start)
    cache = cache_cls(cache_size=cache_size)
    predictor = Predictor()
    seeks_avoided = 0

    for block in requests:
        predictor.record(block)

        if cache.access(block):
            seeks_avoided += 1
        else:
            disk.seek(block)

        if use_predictor:
            for predicted_block in predictor.predict(block):
                if not cache.contains(predicted_block):
                    cache.access(predicted_block)

    return {
        "head_movement": disk.total_movement,
        "hit_rate": cache.hit_rate,
        "seeks_avoided": seeks_avoided,
    }


def run_integrated_simulation(requests, head_start=53, cache_size=8, num_tracks=200):
    """Run the four comparison modes and return their results."""
    return {
        "Plain SSTF": _plain_sstf(requests, head_start, num_tracks),
        "SSTF + LRU Cache": _sstf_with_cache(
            requests, head_start, num_tracks, cache_size, use_predictor=False, cache_cls=LRUCache
        ),
        "SSTF + LRU Cache + Prediction": _sstf_with_cache(
            requests, head_start, num_tracks, cache_size, use_predictor=True, cache_cls=LRUCache
        ),
        "SSTF + Adaptive Cache + Prediction": _sstf_with_cache(
            requests, head_start, num_tracks, cache_size, use_predictor=True, cache_cls=AdaptiveCache
        ),
    }


def compare_modes(requests, head_start=53, cache_size=8, num_tracks=200):
    """Run all 4 modes and print a comparison table."""
    results = run_integrated_simulation(
        requests, head_start=head_start, cache_size=cache_size, num_tracks=num_tracks
    )

    header = f"{'Mode':36s} | {'Head Movement':>14s} | {'Hit Rate':>9s} | {'Seeks Avoided':>13s}"
    print(header)
    print("-" * len(header))
    for mode, stats in results.items():
        print(
            f"{mode:36s} | {stats['head_movement']:14d} | "
            f"{stats['hit_rate']:9.2%} | {stats['seeks_avoided']:13d}"
        )

    return results


if __name__ == "__main__":
    from request_generator import generate_patterned_requests

    requests = generate_patterned_requests(100, seed=42)
    compare_modes(requests)
