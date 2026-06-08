# Assignment 3: Understanding Algorithm Efficiency and Scalability

**Author:** Parthasarathi Ponnapalli
**Course:** MSCS-532 — Algorithms and Data Structures
**University:** University of the Cumberlands — Summer 2026

---

## How to Run

### Requirements
- Python 3.8 or higher
- No external libraries required (standard library only: `random`, `time`, `sys`)

### Part 1 — Randomized Quicksort

```bash
python randomized_quicksort_compare.py
```

Runs correctness checks on 8 edge cases, then benchmarks Randomized vs Deterministic Quicksort across four input distributions (Random, Sorted, Reverse-Sorted, Repeated) at sizes n = 100, 500, 1000, 2000, 5000.

### Part 2 — Hash Table with Chaining

```bash
python hash_table.py
```

Runs correctness checks on 13 edge cases, then two benchmarks:
- Benchmark 1: Insert, Search, Delete performance as n grows (100 → 50,000)
- Benchmark 2: Fixed-size table showing how load factor α affects search performance

---

## Summary of Findings

### Part 1: Randomized Quicksort

Randomized Quicksort consistently achieves O(n log n) performance across all input types by choosing pivots uniformly at random. Deterministic Quicksort (first-element pivot) matches this performance on random data but degrades to O(n²) on sorted and reverse-sorted inputs.

At n = 5,000 on sorted input, the deterministic version took **~1,050 ms** (12,497,500 comparisons) while the randomized version took **~13 ms** (~70,000 comparisons) — an 83x difference. On reverse-sorted input the gap reached **121x**. On random and repeated inputs, both algorithms performed comparably.

### Part 2: Hash Table with Chaining

The hash table uses a Carter-Wegman universal hash function and dynamic resizing at load factor α > 0.75 to maintain expected O(1) Insert, Search, and Delete operations.

When tested without resizing, average search comparisons grew linearly with α — from 1.05 comparisons at α ≈ 0.10 to 4.22 at α ≈ 0.98 — confirming the O(1 + α) theoretical prediction. With dynamic resizing enabled, after 50,000 insertions the table maintained a max chain length of 1 and an average chain length of 1.0, demonstrating that resizing successfully preserves O(1) expected performance.

---

## Files

| File | Description |
|---|---|
| `randomized_quicksort_compare.py` | Part 1 — Randomized vs Deterministic Quicksort with benchmarks |
| `hash_table.py` | Part 2 — Hash Table with Chaining, benchmarks, and correctness tests |
| `README.md` | This file |