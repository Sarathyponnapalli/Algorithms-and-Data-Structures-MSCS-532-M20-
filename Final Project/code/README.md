# Data Locality vs. Pointer-Chasing: A Python Benchmark

Prototype for the MSCS-532 final project, "Optimization in High-Performance Computing." It
empirically compares four sequence data structures that differ only in memory layout, to test
whether the cache/data-locality lessons from Azad, Iqbal, Hassan, & Roy's 2023 empirical study of
HPC performance bugs ("An Empirical Study of High Performance Computing (HPC) Performance Bugs,"
MSR 2023) transfer from C++ to Python.

The paper documents real commits where projects replaced pointer-based containers with contiguous
ones for spatial locality — e.g. `TileDB-d51b082` (`std::forward_list` → `std::vector`) and
`CGAL-8855eb5` (list → vector). This prototype builds the same shape of comparison in Python.

## Structures compared

| Structure       | Layout                                                         | C++ analogue         |
|------------------|-----------------------------------------------------------------|-----------------------|
| `LinkedList`     | Singly linked list of individually heap-allocated `Node` objects | `std::forward_list`  |
| `PyListSequence` | Python `list` — a contiguous array of *pointers* to boxed `float` objects scattered on the heap | (no direct equivalent — Python has no unboxed dynamic array) |
| `ArraySequence`  | `array.array('d', ...)` — contiguous raw C doubles, stdlib only | `std::vector<double>` |
| `NumpySequence`  | `numpy.ndarray(dtype=float64)` — contiguous raw doubles with vectorized reductions | `std::vector<double>` + SIMD |

All four share a minimal interface (`append`, `sum_traverse`, `get`) so `benchmark.py` can drive
them identically.

## Running it

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python benchmark.py
```

This writes `results.csv` in this folder and three chart PNGs to `../report/figures/`:
`traversal_time.png`, `random_access_time.png`, `peak_memory.png`.

Sizes tested: N ∈ {10,000, 100,000, 1,000,000}. Sequential-traversal timings are best-of-N reps
(fewer reps at larger N to bound total run time). Random-access timings use 2,000 random lookups
for the array-backed structures; `LinkedList` is capped at 200 lookups since each lookup is O(N)
and its cost would otherwise dominate the whole run — the exact lookup count used is recorded per
row in `results.csv` rather than hidden.

## Findings (from the run captured in `results.csv`)

- **Random access is where the theory holds up cleanly.** At N=1,000,000, `LinkedList` random
  access costs ~8,606 μs/lookup versus 0.11–0.48 μs/lookup for the array-backed structures —
  roughly an 18,000x gap, exactly the O(N) vs. O(1) difference the paper's commits were fixing.
  A smaller but real gap also opens up *between* the two contiguous structures at this scale:
  `ArrayArray` (0.11 μs/lookup) pulls ahead of `PyList` (0.48 μs/lookup), consistent with `PyList`
  still chasing one pointer indirection per element even though the *container* itself is
  contiguous.
- **Sequential traversal tells a more nuanced story.** A pure-Python `for` loop over `PyList` and
  `ArrayArray` performs almost identically (~13–24 ns/element at every N tested) — the Python
  interpreter's per-iteration bytecode overhead dominates regardless of whether the underlying
  storage is boxed pointers or raw doubles, so contiguity alone buys little in a Python-level loop.
  `NumpyArray`'s vectorized `.sum()` is the outlier, ~27–33x faster than all three loop-based
  structures because it pushes the reduction into compiled, SIMD-capable C code and never enters
  the Python bytecode loop per element.
- **Lesson for the report:** the paper's C++ lesson ("replace pointer-chasing lists with
  contiguous vectors") transfers to Python only partially and only under certain access patterns.
  It transfers strongly for *random access* (contiguity + O(1) indexing wins regardless of
  language). It does **not** automatically transfer to *sequential Python-loop* traversal, because
  a plain Python `list` is contiguous *pointers*, not contiguous *values* — the real analogue of
  `std::vector<double>` locality benefits in Python requires both a contiguous store (`array` or
  NumPy) *and* pushing the traversal itself out of the Python interpreter (NumPy vectorization).

## Files

- `linked_vs_contiguous.py` — the four structure implementations.
- `benchmark.py` — construction/traversal/random-access timing harness, CSV + chart output.
- `results.csv` — raw measurements from the run described above.
- `requirements.txt` — `numpy`, `matplotlib` (stdlib `array` needs nothing extra).
