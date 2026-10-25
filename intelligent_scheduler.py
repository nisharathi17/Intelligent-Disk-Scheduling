from disk import Disk
from cache import AdaptiveCache
from predictor import Predictor


def run_simulation(requests, cache_size=8, use_predictor=False, head_start=53, num_tracks=200):
    """
    Service `requests` in order, through an adaptive cache and
    (optionally) a Markov predictor that prefetches blocks it expects
    to be needed soon. Returns a dict of stats describing how well
    that worked.
    """
    disk = Disk(num_tracks=num_tracks, head_start=head_start)
    cache = AdaptiveCache(cache_size=cache_size)
    predictor = Predictor()

    seeks_avoided = 0
    useful_prefetches = 0
    wasted_prefetches = 0
    # blocks we prefetched but haven't yet seen requested or disproven
    pending_prefetches = set()

    for block in requests:
        if cache.contains(block) and block in pending_prefetches:
            useful_prefetches += 1
            pending_prefetches.discard(block)

        predictor.record(block)

        hit = cache.access(block)
        if hit:
            seeks_avoided += 1
        else:
            disk.seek(block)

        if use_predictor:
            predicted = predictor.predict(block)
            for predicted_block in predicted:
                if not cache.contains(predicted_block):
                    cache.access(predicted_block)
                    pending_prefetches.add(predicted_block)

    # anything still pending at the end was never actually requested again
    wasted_prefetches = len(pending_prefetches)

    return {
        "hits": cache.hits,
        "misses": cache.misses,
        "hit_rate": cache.hit_rate,
        "seeks_avoided": seeks_avoided,
        "useful_prefetches": useful_prefetches,
        "wasted_prefetches": wasted_prefetches,
        "head_movement": disk.total_movement,
    }


if __name__ == "__main__":
    from request_generator import generate_patterned_requests

    requests = generate_patterned_requests(100, seed=42)

    plain = run_simulation(requests, use_predictor=False)
    predicted = run_simulation(requests, use_predictor=True)

    print("Without predictor:", plain)
    print("With predictor:   ", predicted)
