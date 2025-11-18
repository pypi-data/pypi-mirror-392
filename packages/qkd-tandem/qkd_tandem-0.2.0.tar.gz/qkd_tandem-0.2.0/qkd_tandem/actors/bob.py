import numpy as np

class Bob:
    def __init__(self, rng=None):
        self.rng = rng or np.random.default_rng()

    def next_basis(self):
        return int(self.rng.integers(0, 2))

