from collections import OrderedDict


class LRUCache:
    """
    LRU cache for disk blocks. A hit means we can skip the physical
    seek entirely; a miss means we have to go to disk and then
    remember the block for next time.
    """

    def __init__(self, cache_size=8):
        self.cache_size = cache_size
        self._store = OrderedDict()
        self.hits = 0
        self.misses = 0

    def access(self, block):
        if block in self._store:
            self._store.move_to_end(block)
            self.hits += 1
            return True

        self.misses += 1
        self._insert(block)
        return False

    def _insert(self, block):
        if block in self._store:
            self._store.move_to_end(block)
            return
        self._store[block] = True
        if len(self._store) > self.cache_size:
            self._evict()

    def _evict(self):
        self._store.popitem(last=False)

    def contains(self, block):
        return block in self._store

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


# Backwards-compatible alias: existing code imports `Cache`.
Cache = LRUCache


class AdaptiveCache(LRUCache):
    """
    Behaves like a plain LRU cache for normal access patterns, but
    detects sequential scans (3+ consecutive blocks accessed in
    increasing or decreasing order by block number) and switches to
    MRU eviction while the scan is in progress.

    Sequential scans blow out an LRU cache: every block is touched
    exactly once, so caching any of them buys nothing, and they evict
    blocks from the working set that will actually be reused. Evicting
    the most-recently-used (scan) block instead protects that working
    set until the scan ends.
    """

    SCAN_THRESHOLD = 3

    def __init__(self, cache_size=8):
        super().__init__(cache_size=cache_size)
        self._last_block = None
        self._scan_direction = 0
        self._scan_run = 1
        self.mru_evictions = 0
        self.lru_evictions = 0

    def access(self, block):
        self._update_scan_state(block)
        return super().access(block)

    def _update_scan_state(self, block):
        if self._last_block is not None:
            delta = block - self._last_block
            direction = 1 if delta > 0 else (-1 if delta < 0 else 0)
            if direction != 0 and direction == self._scan_direction and abs(delta) == 1:
                self._scan_run += 1
            else:
                self._scan_direction = direction
                self._scan_run = 1
        self._last_block = block

    @property
    def _is_scanning(self):
        return self._scan_run >= self.SCAN_THRESHOLD

    def _evict(self):
        if self._is_scanning:
            self._store.popitem(last=True)  # MRU eviction during a scan
            self.mru_evictions += 1
        else:
            self._store.popitem(last=False)  # normal LRU eviction
            self.lru_evictions += 1


if __name__ == "__main__":
    cache = LRUCache(cache_size=3)
    for block in [1, 2, 3, 1, 4, 2, 5]:
        print(block, "HIT" if cache.access(block) else "MISS")
    print(f"LRU hit rate: {cache.hit_rate:.2%}")

    adaptive = AdaptiveCache(cache_size=3)
    # 10, 11, 12, 13, 14 is a sequential scan; 1 and 2 are the working set
    for block in [1, 2, 10, 11, 12, 13, 14, 1, 2]:
        print(block, "HIT" if adaptive.access(block) else "MISS")
    print(f"Adaptive hit rate: {adaptive.hit_rate:.2%}")
