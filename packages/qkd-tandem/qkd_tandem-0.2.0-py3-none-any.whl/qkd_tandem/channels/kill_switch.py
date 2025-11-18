from dataclasses import dataclass
from .bb84 import BB84RoundResult

@dataclass
class KillSwitchState:
    armed: bool = False

class KillSwitchChannel:
    def __init__(self, sabotage_fn):
        self.state = KillSwitchState()
        self.sabotage_fn = sabotage_fn

    def arm(self):
        self.state.armed = True

    def prepare(self, bit: int, basis: int):
        return {'bit': bit, 'basis': basis}

    def measure(self, prep, bob_basis: int, outcome_bit: int):
        if self.state.armed:
            outcome_bit = None  # signal for randomized measurement
        kept = (prep['basis'] == bob_basis)
        return BB84RoundResult(
            kept=kept,
            alice_bit=prep['bit'],
            alice_basis=prep['basis'],
            bob_bit=outcome_bit if outcome_bit is not None else -1,
            bob_basis=bob_basis,
            eavesdropped=False
        )

