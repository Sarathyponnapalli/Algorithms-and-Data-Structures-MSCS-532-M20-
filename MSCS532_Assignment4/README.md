# Assignment 4: Heap Data Structures — Implementation, Analysis, and Applications

**Author:** Parthasarathi Ponnapalli
**Course:** MSCS-532 — Algorithms and Data Structures
**University:** University of the Cumberlands — Summer 2026

---

## How to Run

### Requirements
- Python 3.8 or higher
- No external libraries required (standard library only: `random`, `time`, `sys`)

### Part 1 — Heapsort Comparison

```bash
python heapsort.py
```

Runs correctness checks on 8 edge cases for all three algorithms (Heapsort, Merge Sort, Randomized Quicksort), then benchmarks all three side-by-side across four input distributions (Random, Sorted, Reverse-Sorted, Repeated) at sizes n = 100, 500, 1000, 2000, 5000.

### Part 2 — Priority Queue

```bash
python priority_queue.py
```

Runs 12 correctness tests covering all operations (insert, extract_max, increase_key, decrease_key, peek_max, is_empty, tie-breaking, error handling), then a scheduler simulation with 10 tasks of varying priorities and deadlines, followed by an operation benchmark at n = 100 to 10,000.

---

## Summary of Findings

### Part 1: Heapsort

Heapsort delivers consistent O(n log n) performance on all input distributions — sorted, reverse-sorted, random, and repeated — with no variance between cases. Merge Sort is consistently faster in wall-clock time (~30–40% faster at n = 5,000) due to better cache performance and fewer comparisons, but requires O(n) auxiliary memory. Quicksort matches or beats Heapsort on random input but requires O(log n) stack space.

At n = 5,000 on sorted input: Heapsort took ~14ms with 112,126 comparisons; Merge Sort took ~6ms with 29,804 comparisons; Quicksort took ~8.5ms with 72,976 comparisons. Heapsort's higher comparison count on all inputs stems from its access pattern — the heap structure produces non-sequential memory access that hurts cache performance relative to Merge Sort's sequential passes.

Key trade-off: Heapsort is the only algorithm that guarantees O(n log n) worst case, O(1) extra space (iterative heapify), and no input can degrade its performance.

### Part 2: Priority Queue

The array-based max-heap priority queue maintains O(log n) insert and extract_max across all tested sizes. At n = 10,000, inserting all 10,000 tasks took 6.4ms (22,615 comparisons); extracting all 10,000 tasks took 51ms (216,657 comparisons). The higher extract cost reflects that sift-down traverses the full heap height, while sift-up on insert typically terminates early.

The scheduler simulation processed all 10 tasks in strict priority order, with all three CRITICAL priority-9 tasks (engine fault, brake warning, speed limiter) served first. All 10 deadlines were met, demonstrating that a max-heap priority queue correctly enforces priority-based scheduling.

---

## Files

| File | Description |
|---|---|
| `heapsort.py` | Heapsort + Merge Sort + Quicksort with benchmarks |
| `priority_queue.py` | Task class + Max-Heap Priority Queue + scheduler simulation ||
| `README.md` | This file |

---

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.