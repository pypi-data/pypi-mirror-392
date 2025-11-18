import numpy as np

class Eve:
    def __init__(self, attack_rate=0.3, rng=None, basis_strategy="random"):
        self.attack_rate = attack_rate
        self.rng = rng or np.random.default_rng()
        self.basis_strategy = basis_strategy

    def will_attack(self):
        return self.rng.random() < self.attack_rate

    def pick_basis(self, alice_basis_hint=None):
        if self.basis_strategy == "random":
            return int(self.rng.integers(0, 2))
        if self.basis_strategy == "mirror" and alice_basis_hint is not None:
            return int(alice_basis_hint)
        return int(self.rng.integers(0, 2))

