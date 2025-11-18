import csv

def compute_qber(results):
    kept = [r for r in results if r['kept']]
    if not kept: return 0.0
    errs = sum(1 for r in kept if r['alice_bit'] != r['bob_bit'])
    return errs / len(kept)

def save_to_csv(results, filename):
    keys = results[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

