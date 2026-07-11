# Assignment 6: Medians, Order Statistics & Elementary Data Structures

**Author:** Parthasarathi Ponnapalli
**Course:** MSCS-532 — Algorithms and Data Structures
**University:** University of the Cumberlands — Summer 2026

---

## How to Run

### Requirements
- Python 3.8 or higher
- No external libraries required (standard library only: `random`, `time`, `sys`, `collections`)

### Part 1 — Selection Algorithms

```bash
python Selection_algorithms.py
```

Runs 9 correctness tests on both Median of Medians and Randomized Quickselect (minimum, maximum, median, single element, duplicates, edge cases), then benchmarks both algorithms finding the median (k = n//2) across four input distributions at sizes n = 100, 500, 1000, 2000, 5000.

### Part 2 — Elementary Data Structures

```bash
python elementary_ds.py
```

Runs 36 correctness tests across all five data structures (DynamicArray, Matrix, ArrayStack, ArrayQueue, SinglyLinkedList, RootedTree), then benchmarks key operations at n = 1,000, 5,000, and 10,000.

---

## Summary of Findings

### Part 1: Selection Algorithms

Both algorithms find the k-th smallest element in linear expected/worst-case time, but with meaningfully different constant factors. Randomized Quickselect is consistently **3–5x faster** than Median of Medians across all distributions and sizes tested. At n = 5,000, Quickselect took ~0.9ms with ~13,000 comparisons versus MoM's ~2.5–4.9ms with ~45,000–47,000 comparisons.

The difference is that MoM's O(n) guarantee comes with significant overhead: it makes two recursive calls (one for median-of-medians on n/5 elements, one for the main selection), and the constant in its O(n) bound is large (~10× the constant for Quickselect). In practice, Quickselect's random pivot nearly always lands near the median, so its expected performance is close to the theoretical best case. MoM should be preferred only when worst-case guarantees are critical, such as in real-time or adversarial environments.

### Part 2: Elementary Data Structures

Array-based structures (DynamicArray, ArrayStack, ArrayQueue) outperform SinglyLinkedList on all sequential operations due to cache-friendly memory layout. Stack push/pop and Queue enqueue/dequeue are the fastest operations (< 0.5ms for 1,000 operations) due to O(1) access patterns.

The clearest trade-off observed: inserting at the front of a DynamicArray at n = 10,000 takes 45.8ms (O(n) per operation × 100 operations), while insert_front on SinglyLinkedList at the same size takes 8.8ms total for 10,000 inserts — demonstrating that linked lists genuinely win when insertions are front-heavy. Traversal, however, is faster on arrays (~0.9ms) than linked lists (~1.9ms) at n = 10,000 due to pointer-following overhead.

---

## Files

| File | Description |
|---|---|
| `Selection_algorithms.py` | Median of Medians + Randomized Quickselect with benchmarks |
| `elementary_ds.py` | DynamicArray, Matrix, ArrayStack, ArrayQueue, SinglyLinkedList, RootedTree |
| `README.md` | This file |

---

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.