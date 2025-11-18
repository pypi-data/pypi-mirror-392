import matplotlib.pyplot as plt

def plot_qber_window(results, window=50, title="Rolling QBER"):
    """
    Plot rolling QBER over a sliding window of rounds.
    results: list of dicts with keys 'kept', 'alice_bit', 'bob_bit'
    window: number of rounds per window
    """
    qbers = []
    rounds = []

    for i in range(len(results)):
        # take last `window` rounds
        subset = results[max(0, i-window+1):i+1]
        kept = [r for r in subset if r['kept']]
        if kept:
            errs = sum(1 for r in kept if r['alice_bit'] != r['bob_bit'])
            qber = errs / len(kept)
            qbers.append(qber)
            rounds.append(i+1)

    plt.figure(figsize=(8,4))
    plt.plot(rounds, qbers, label="QBER")
    plt.xlabel("Round")
    plt.ylabel("QBER (windowed)")
    plt.title(title)
    plt.ylim(0,1)
    plt.grid(True)
    plt.legend()
    plt.show()
