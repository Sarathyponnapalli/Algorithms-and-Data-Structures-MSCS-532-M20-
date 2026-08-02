"""
Benchmarks LinkedList vs PyListSequence vs ArraySequence vs NumpySequence on:
  - construction time and peak memory (tracemalloc)
  - sequential traversal/sum time
  - random-index access time

Sizes: N in {10_000, 100_000, 1_000_000}, matching the "small/medium/large"
scale progression used to expose cache/locality effects (differences that
don't show up at N=10_000 become dramatic at N=1_000_000).

Random-index access on LinkedList is O(N) per lookup (no shortcuts exist for
a singly linked list), so its lookup count is capped independently of the
other structures to keep total run time bounded; this is noted in the CSV
output via the `random_access_num_lookups` column rather than hidden.

Outputs:
  - results.csv                          (raw measurements, one row per structure x size)
  - ../report/figures/traversal_time.png
  - ../report/figures/random_access_time.png
  - ../report/figures/peak_memory.png
"""

from __future__ import annotations

import csv
import random
import time
import tracemalloc
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from linked_vs_contiguous import (
    LinkedList,
    PyListSequence,
    ArraySequence,
    NumpySequence,
    HAVE_NUMPY,
)

SIZES = [10_000, 100_000, 1_000_000]
SEQUENTIAL_REPS = {10_000: 20, 100_000: 8, 1_000_000: 3}
RANDOM_LOOKUPS = {10_000: 2000, 100_000: 2000, 1_000_000: 2000}
LINKED_LIST_MAX_LOOKUPS = 200  # O(N) per lookup; capped so runtime stays bounded

HERE = Path(__file__).resolve().parent
FIGURES_DIR = HERE.parent / "report" / "figures"
RESULTS_CSV = HERE / "results.csv"

STRUCTURES = {
    "LinkedList": LinkedList,
    "PyList": PyListSequence,
    "ArrayArray": ArraySequence,
}
if HAVE_NUMPY:
    STRUCTURES["NumpyArray"] = NumpySequence


def time_construction(cls, values):
    tracemalloc.start()
    t0 = time.perf_counter()
    seq = cls.from_iterable(values)
    elapsed = time.perf_counter() - t0
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return seq, elapsed, peak


def time_sequential_traverse(seq, reps: int) -> float:
    best = float("inf")
    for _ in range(reps):
        t0 = time.perf_counter()
        seq.sum_traverse()
        elapsed = time.perf_counter() - t0
        best = min(best, elapsed)
    return best


def time_random_access(seq, n: int, num_lookups: int) -> float:
    rng = random.Random(1234)
    indices = [rng.randrange(n) for _ in range(num_lookups)]
    t0 = time.perf_counter()
    for idx in indices:
        seq.get(idx)
    return time.perf_counter() - t0


def run():
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    for n in SIZES:
        print(f"\n=== N = {n:,} ===")
        rng = random.Random(42)
        values = [rng.random() for _ in range(n)]

        for name, cls in STRUCTURES.items():
            seq, construct_s, peak_mem = time_construction(cls, values)

            reps = SEQUENTIAL_REPS[n]
            traverse_s = time_sequential_traverse(seq, reps)
            traverse_ns_per_elem = (traverse_s / n) * 1e9

            num_lookups = RANDOM_LOOKUPS[n]
            if name == "LinkedList":
                num_lookups = min(num_lookups, LINKED_LIST_MAX_LOOKUPS)
            random_s = time_random_access(seq, n, num_lookups)
            random_us_per_lookup = (random_s / num_lookups) * 1e6

            print(
                f"{name:12s} construct={construct_s:8.4f}s  peak_mem={peak_mem/1e6:8.2f}MB  "
                f"traverse(best of {reps})={traverse_s:8.4f}s ({traverse_ns_per_elem:6.1f} ns/elem)  "
                f"random_access({num_lookups} lookups)={random_us_per_lookup:8.2f} us/lookup"
            )

            rows.append(
                {
                    "structure": name,
                    "n": n,
                    "construction_time_s": construct_s,
                    "peak_memory_bytes": peak_mem,
                    "sequential_reps": reps,
                    "traversal_time_s": traverse_s,
                    "traversal_time_ns_per_elem": traverse_ns_per_elem,
                    "random_access_num_lookups": num_lookups,
                    "random_access_total_time_s": random_s,
                    "random_access_time_us_per_lookup": random_us_per_lookup,
                }
            )

    with open(RESULTS_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {RESULTS_CSV}")

    make_charts(rows)


def make_charts(rows):
    structures = list(STRUCTURES.keys())
    colors = {
        "LinkedList": "#c0392b",
        "PyList": "#2980b9",
        "ArrayArray": "#27ae60",
        "NumpyArray": "#8e44ad",
    }

    def series(field):
        data = {name: [] for name in structures}
        for name in structures:
            for n in SIZES:
                row = next(r for r in rows if r["structure"] == name and r["n"] == n)
                data[name].append(row[field])
        return data

    # Traversal time (ns/element) vs N
    plt.figure(figsize=(7, 5))
    data = series("traversal_time_ns_per_elem")
    for name in structures:
        plt.plot(SIZES, data[name], marker="o", label=name, color=colors.get(name))
    plt.xscale("log")
    plt.xlabel("N (elements)")
    plt.ylabel("Traversal time (ns/element)")
    plt.title("Sequential Sum Traversal: Time per Element vs N")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "traversal_time.png", dpi=150)
    plt.close()

    # Random access time (us/lookup) vs N
    plt.figure(figsize=(7, 5))
    data = series("random_access_time_us_per_lookup")
    for name in structures:
        plt.plot(SIZES, data[name], marker="o", label=name, color=colors.get(name))
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("N (elements)")
    plt.ylabel("Random access time (microseconds/lookup, log scale)")
    plt.title("Random-Index Access: Time per Lookup vs N")
    plt.legend()
    plt.grid(True, which="both", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "random_access_time.png", dpi=150)
    plt.close()

    # Peak memory vs N
    plt.figure(figsize=(7, 5))
    data = series("peak_memory_bytes")
    x = range(len(SIZES))
    width = 0.8 / len(structures)
    for i, name in enumerate(structures):
        mb = [b / 1e6 for b in data[name]]
        plt.bar([xi + i * width for xi in x], mb, width=width, label=name, color=colors.get(name))
    plt.xticks([xi + width * (len(structures) - 1) / 2 for xi in x], [f"{n:,}" for n in SIZES])
    plt.xlabel("N (elements)")
    plt.ylabel("Peak memory during construction (MB)")
    plt.title("Peak Memory Usage vs N")
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "peak_memory.png", dpi=150)
    plt.close()

    print(f"Wrote charts to {FIGURES_DIR}")


if __name__ == "__main__":
    run()
