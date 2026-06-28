# Assignment 5: Quicksort Algorithm — Implementation, Analysis, and Randomization

**Author:** Parthasarathi Ponnapalli
**Course:** MSCS-532 — Algorithms and Data Structures
**University:** University of the Cumberlands — Summer 2026

---

## How to Run

### Requirements
- Python 3.8 or higher
- No external libraries required (standard library only: `random`, `time`, `sys`)

### Run the Benchmark

```bash
python quicksort.py
```

Runs correctness checks on 8 edge cases (empty, single, sorted, reverse, identical, two elements, random, repeated) for both Deterministic and Randomized Quicksort, then benchmarks both across four input distributions (Random, Sorted, Reverse-Sorted, Repeated) at sizes n = 100, 500, 1000, 2000, 5000.

---

## Summary of Findings

Deterministic Quicksort (first-element pivot) and Randomized Quicksort perform comparably on random and repeated-element inputs — both achieve O(n log n) in practice. The difference becomes dramatic on sorted and reverse-sorted inputs.

At n = 5,000 on sorted input, Deterministic Quicksort took **~508 ms** with exactly **12,497,500 comparisons** (= n(n−1)/2, the signature of O(n²)), while Randomized Quicksort took **~7.3 ms** with only ~68,000 comparisons — a **70x slowdown** for the deterministic version. On reverse-sorted input at the same size, the gap widened to **122x** (853 ms vs 7.0 ms), with the deterministic version also performing 6,259,998 swaps versus 39,825 for the randomized version.

The reason is structural: a fixed pivot choice means the first element of a sorted (or reverse-sorted) array is always the minimum (or maximum), producing the worst possible partition split — size 0 and n−1 — at every recursive level. A randomly chosen pivot makes this outcome astronomically unlikely regardless of how the input is arranged, which is why randomization guarantees O(n log n) expected performance for *any* input distribution, not just random ones.

---

## Files

| File | Description |
|---|---|
| `quicksort.py` | Deterministic and Randomized Quicksort implementations with benchmarks |
| `Assignment5_Report.docx` | Full report: implementation details, complexity analysis, empirical comparison |
| `README.md` | This file |

---

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.