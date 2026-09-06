from __future__ import annotations

from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    """A simple least-recently-used cache for disk blocks."""

    def __init__(self, capacity: int = 8):
        self.capacity = max(1, int(capacity))
        self.data: OrderedDict[int, Any] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: int) -> Optional[Any]:
        if key not in self.data:
            self.misses += 1
            return None
        value = self.data.pop(key)
        self.data[key] = value
        self.hits += 1
        return value

    def put(self, key: int, value: Any) -> None:
        if key in self.data:
            self.data.pop(key)
        elif len(self.data) >= self.capacity:
            self.data.popitem(last=False)
        self.data[key] = value

    def contains(self, key: int) -> bool:
        return key in self.data

    def clear(self) -> None:
        self.data.clear()
        self.hits = 0
        self.misses = 0

    def hit_rate(self) -> float:
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return self.hits / total

    def __contains__(self, key: int) -> bool:
        return key in self.data

    def __len__(self) -> int:
        return len(self.data)


if __name__ == "__main__":
    cache = LRUCache(3)
    cache.put(1, "A")
    cache.put(2, "B")
    print(cache.get(1))
    print(cache.hit_rate())
