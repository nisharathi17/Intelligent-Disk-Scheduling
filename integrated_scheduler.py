from disk import Disk
from cache import LRUCache, AdaptiveCache
from predictor import Predictor
from scheduling_algorithms import sstf


# head_movement for every cache mode is now computed by running SSTF on
# the cache MISSES only (arrival order decides what's a hit/miss, SSTF
# decides how the real disk work is scheduled). This guarantees
# head_movement can never exceed plain batch SSTF on the full request
# list, which is the correctness property that matters here.
#
# One consequence worth knowing up front: SSTF's total movement is a
# function of the *set* of distinct blocks it visits, not of how many
# times each one repeats -- once sorted, a repeated block sits right
# next to its earlier visit at distance 0. A cache only ever removes
# repeat (non-first) occurrences, and a block's *first* occurrence is
# always a genuine miss. So the distinct miss set is usually identical
# to the full request set's distinct values, and head_movement for
# every cache mode typically TIES the plain SSTF baseline rather than
# beating it -- that's expected, not a bug. Caching's real benefit
# shows up in seeks_avoided and hit_rate (fewer/cheaper real disk
# operations), even on traces where the head_movement number doesn't
# move. It can go strictly below baseline only when a predicted
# prefetch manages to cache a block before its first real request.


def _plain_sstf(requests, head_start, num_tracks):
    """Baseline: full SSTF reorder of every request, no cache at all."""
    _, movement = sstf(requests, head_start)
    return {
        "head_movement": movement,
        "hit_rate": 0.0,
        "seeks_avoided": 0,
    }


def _sstf_with_cache(requests, head_start, num_tracks, cache_size, use_predictor, cache_cls=LRUCache):
    """
    Check the cache in arrival order (that's what the application is
    actually requesting); every miss is queued up. Prefetching a
    predicted block into the cache is a background operation and never
    queues a seek of its own -- it only affects whether a *later* real
    request finds its block already cached. Once every request has
    been checked, the genuine misses are serviced with SSTF scheduling,
    so head_movement can never exceed the no-cache SSTF baseline.
    `cache_cls` selects which cache implementation backs this run
    (plain LRU or AdaptiveCache).
    """
    cache = cache_cls(cache_size=cache_size)
    predictor = Predictor()
    seeks_avoided = 0
    misses = []

    for block in requests:
        predictor.record(block)

        if cache.access(block):
            seeks_avoided += 1
        else:
            misses.append(block)

        if use_predictor:
            for predicted_block in predictor.predict(block):
                if not cache.contains(predicted_block):
                    cache.access(predicted_block)

    _, movement = sstf(misses, head_start) if misses else ([], 0)

    return {
        "head_movement": movement,
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
