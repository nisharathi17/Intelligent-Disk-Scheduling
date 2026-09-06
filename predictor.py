from __future__ import annotations

from collections import Counter
from typing import Iterable, List


class BlockPredictor:
    """Simple predictor based on recent request frequency and locality."""

    def __init__(self, history_size: int = 10, lookahead: int = 3):
        self.history_size = max(1, int(history_size))
        self.lookahead = max(1, int(lookahead))
        self.recent_history: List[int] = []

    def update(self, request: int) -> None:
        self.recent_history.append(int(request))
        if len(self.recent_history) > self.history_size:
            self.recent_history.pop(0)

    def predict_next(self, recent_requests: Iterable[int] | None = None) -> List[int]:
        history = list(recent_requests) if recent_requests is not None else self.recent_history
        if not history:
            return []
        counts = Counter(history)
        ranked = [block for block, _ in counts.most_common()]
        if not ranked:
            return []
        return ranked[: self.lookahead]

    def predict_sequence(self, requests: Iterable[int]) -> List[int]:
        history = list(requests)
        if not history:
            return []
        predictor = self.predict_next(history)
        return predictor


if __name__ == "__main__":
    predictor = BlockPredictor(history_size=5, lookahead=3)
    for request in [10, 12, 10, 11, 10, 12]:
        predictor.update(request)
    print(predictor.predict_next())
