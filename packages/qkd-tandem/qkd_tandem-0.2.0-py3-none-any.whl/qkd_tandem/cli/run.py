import argparse
import os
import matplotlib.pyplot as plt
from qkd_tandem.experiments.config import DEFAULTS
from qkd_tandem.cli.simulation import simulate

def rolling_qber(results, window=16):
    qbers = []
    for i in range(len(results)):
        recent = [r for r in results[max(0, i-window):i+1] if r['kept']]
        if recent:
            errs = sum(1 for r in recent if r['alice_bit'] != r['bob_bit'])
            qbers.append(errs / len(recent))
        else:
            qbers.append(0.0)
    return qbers

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sweep", action="store_true", help="Run sweep of attack rates")
    args = parser.parse_args()

    if args.sweep:
        # sweep logic here...
        pass
    else:
        out = simulate(
            n_bits=DEFAULTS["n_bits"],
            attack_rate=DEFAULTS["attack_rate"],
            ks_trigger=DEFAULTS["ks_trigger"],
            seed=DEFAULTS["seed"]
        )
        print(f"BB84 QBER: {out['bb84_qber']:.4f}")
        print(f"Kill Switch QBER: {out['ks_qber']:.4f}")

        # Rolling QBER plot
        bb84_curve = rolling_qber(out['bb84_results'])
        ks_curve   = rolling_qber(out['ks_results'])

        plt.figure(figsize=(10,6))
        plt.plot(bb84_curve, label="BB84 Rolling QBER", color="blue")
        plt.plot(ks_curve, label="Kill Switch Rolling QBER", color="red")
        plt.axhline(0.11, linestyle="--", color="gray", label="Abort threshold")
        plt.xlabel("Bit index")
        plt.ylabel("QBER (fraction)")
        plt.title("Rolling QBER Comparison: BB84 vs Kill Switch")
        plt.legend()
        plt.grid(True)

        # Save to benchmarks folder
        repo_root = os.path.dirname(os.path.dirname(__file__))
        save_path = os.path.join(repo_root, "benchmarks", "qber_comparison.png")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300)


        # Show interactively if you want
        plt.show()
        plt.close()

if __name__ == "__main__":
    main()
