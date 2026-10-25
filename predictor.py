from collections import defaultdict, Counter


class Predictor:
    """
    Simple Markov-chain predictor: learns which block tends to follow
    which, then uses that to guess what's coming next so we can
    prefetch it into the cache before it's actually requested.
    """

    def __init__(self, history_size=20, lookahead=3):
        self.history_size = history_size
        self.lookahead = lookahead
        self.transitions = defaultdict(Counter)
        self.history = []
        self._last_block = None

    def record(self, block):
        if self._last_block is not None:
            self.transitions[self._last_block][block] += 1
        self._last_block = block

        self.history.append(block)
        if len(self.history) > self.history_size:
            self.history.pop(0)

    def predict(self, block):
        counter = self.transitions.get(block)
        if not counter:
            return []
        most_common = counter.most_common(self.lookahead)
        return [next_block for next_block, _ in most_common]


if __name__ == "__main__":
    predictor = Predictor(lookahead=2)
    sequence = [10, 20, 10, 20, 10, 30, 10, 20]
    for block in sequence:
        predictor.record(block)

    print("Predictions after block 10:", predictor.predict(10))
    print("Recent history:", predictor.history)
