from dataclasses import dataclass

@dataclass
class SabotageConfig:
    intensity: float  # 0.0-1.0 to tune scrambling strength

def basic_scramble(intensity: float):
    # Placeholder logical effect: with some probability, flip or randomize the bit
    # Physical realization will be a gate stack; here we emulate outcome skew.
    def apply(alice_bit, bob_basis):
        # 50% error target when armed: randomize Bob’s outcome regardless of bases
        return None  # signal to runtime to randomize measurement outcome
    return apply

