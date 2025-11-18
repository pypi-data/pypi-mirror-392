from dataclasses import dataclass
import numpy as np

@dataclass
class BB84RoundResult:
    kept: bool
    alice_bit: int
    alice_basis: int
    bob_bit: int
    bob_basis: int
    eavesdropped: bool

class BB84Channel:
    def __init__(self, rng=None):
        self.rng = rng or np.random.default_rng()

    def prepare(self, bit: int, basis: int):
        # Logical representation; physical circuit applied at runtime layer
        return {'bit': bit, 'basis': basis}

    def measure(self, prep, bob_basis: int, outcome_bit: int):
        kept = (prep['basis'] == bob_basis)
        return BB84RoundResult(
            kept=kept,
            alice_bit=prep['bit'],
            alice_basis=prep['basis'],
            bob_bit=outcome_bit,
            bob_basis=bob_basis,
            eavesdropped=False
        )

def qber(results):
    kept = [r for r in results if r.kept]
    if not kept: return 0.0
    errs = sum(1 for r in kept if r.alice_bit != r.bob_bit)
    return errs / len(kept)
