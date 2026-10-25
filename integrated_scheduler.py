from disk import Disk
from cache import LRUCache, AdaptiveCache
from predictor import Predictor


# NOTE on why this isn't "run SSTF on the miss-list": SSTF's total head
# movement is a function of the *set* of distinct blocks it visits, not
# of how many times each one appears -- once sorted, a repeated block
# sits right next to its earlier visit at distance 0. A cache only ever
# removes repeat (non-first) occurrences of a block, and every block's
# *first* occurrence is always a genuine miss. So the distinct set a
# cache leaves behind for SSTF to schedule is always identical to the
# full request set's distinct values, and re-running SSTF on it always
# gives the exact same number (248 for the demo trace) -- which is the
# bug that was reported: all 4 modes collapsing to one value.
#
# To make caching actually show up in head_movement, requests have to
# be serviced as they arrive, one at a time, the way a real disk
# controller sees them -- it doesn't get to see the whole future trace
# and re-sort it. A cache hit then means the head truly never moves for
# that request, which changes the position the *next* real seek starts
# from, and that's what produces a genuine, varying improvement.


def _plain_sstf(requests, head_start, num_tracks):
    """
    Baseline: no cache at all, so every request is a real seek,
    serviced directly as it arrives (there's nothing to reorder --
    SSTF only has a choice when multiple requests are pending at once,
    and here they arrive and get serviced one at a time).
    """
    disk = Disk(num_tracks=num_tracks, head_start=head_start)
    for block in requests:
        disk.seek(block)

    return {
        "head_movement": disk.total_movement,
        "hit_rate": 0.0,
        "seeks_avoided": 0,
    }


def _sstf_with_cache(requests, head_start, num_tracks, cache_size, use_predictor, cache_cls=LRUCache):
    """
    Service requests as they arrive. Each one checks the cache first:
    a hit means the head doesn't move at all for that request. A miss
    means a real seek straight to that block. Prefetching a predicted
    block into the cache is a background operation and never costs a
    seek of its own -- it only affects whether a *later* real request
    finds its block already cached. `cache_cls` selects which cache
    implementation backs this run (plain LRU or AdaptiveCache).
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
