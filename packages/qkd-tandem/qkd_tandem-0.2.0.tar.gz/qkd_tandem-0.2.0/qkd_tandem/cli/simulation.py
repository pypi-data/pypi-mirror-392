import numpy as np
from qkd_tandem.sabotage.star_qft import run_star_qft

def parse_counts_key(key: str, i: int):
    """Extract Alice, Bob, Charly bits for round i from a long outcome string."""
    # Each logical bit uses 3 qubits, measured into 3 classical bits
    a = int(key[i*3])     # Alice
    b = int(key[i*3+1])   # Bob
    c = int(key[i*3+2])   # Charly
    return a, b, c

def simulate(n_bits=192, attack_rate=0.3, ks_trigger=0.15, seed=42):
    rng = np.random.default_rng(seed)
    bb84_results, ks_results = [], []
    ks_armed = False

    # Pre-run sabotage circuit for all bits
    sabotage_counts = run_star_qft(n_bits=n_bits, shots=4096)
    sabotage_outcomes = []
    for key, count in sabotage_counts.items():
        sabotage_outcomes.extend([key] * count)
    rng.shuffle(sabotage_outcomes)

    window = 16
    for i in range(n_bits):
        alice_bit = rng.integers(0,2)
        alice_basis = rng.integers(0,2)
        bob_basis   = rng.integers(0,2)
        tampered    = rng.random() < attack_rate

        # --- BB84 outcome logic ---
        if alice_basis == bob_basis and not tampered:
            bob_bit_bb84 = alice_bit
        elif alice_basis != bob_basis and not tampered:
            bob_bit_bb84 = rng.integers(0,2)
        else:
            bob_bit_bb84 = alice_bit ^ rng.integers(0,2) if alice_basis == bob_basis else rng.integers(0,2)

        kept = (alice_basis == bob_basis)
        bb84_results.append({
            'kept': kept, 'alice_bit': alice_bit, 'bob_bit': bob_bit_bb84,
            'alice_basis': alice_basis, 'bob_basis': bob_basis, 'eaves': tampered
        })

        # --- Kill Switch arming logic ---
        recent = [r for r in ks_results[-window:] if r['kept']]
        qber_recent = (sum(1 for r in recent if r['alice_bit'] != r['bob_bit']) / len(recent)) if recent else 0.0
        if tampered or qber_recent >= ks_trigger:
            ks_armed = True

        # --- Kill Switch outcome ---
        if not ks_armed:
            bob_bit_ks = bob_bit_bb84
        else:
            key = sabotage_outcomes[i % len(sabotage_outcomes)]
            _, bob_bit_s, _ = parse_counts_key(key, i)
            bob_bit_ks = bob_bit_s

        ks_results.append({
            'kept': kept, 'alice_bit': alice_bit, 'bob_bit': bob_bit_ks,
            'alice_basis': alice_basis, 'bob_basis': bob_basis,
            'eaves': tampered, 'armed': ks_armed
        })

    # --- Final QBERs ---
    def qber(results):
        kept = [r for r in results if r['kept']]
        if not kept: return 0.0
        errs = sum(1 for r in kept if r['alice_bit'] != r['bob_bit'])
        return errs / len(kept)

    return {
        'bb84_qber': qber(bb84_results),
        'ks_qber': qber(ks_results),
        'bb84_abort': qber(bb84_results) > 0.11,
        'ks_armed': any(r['armed'] for r in ks_results),
        'bb84_results': bb84_results,
        'ks_results': ks_results
    }
