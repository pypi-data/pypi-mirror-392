import numpy as np

class Alice:
    def __init__(self, rng=None):
        self.rng = rng or np.random.default_rng()

    def next_bit_basis(self):
        return int(self.rng.integers(0, 2)), int(self.rng.integers(0, 2))

