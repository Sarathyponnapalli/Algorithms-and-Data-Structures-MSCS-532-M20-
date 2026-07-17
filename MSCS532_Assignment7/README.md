# Assignment 7: Exploring Hash Tables and Their Practical Applications

**Author:** Parthasarathi Ponnapalli
**Course:** MSCS-532 — Algorithms and Data Structures
**University:** University of the Cumberlands — Summer 2026

---

## How to Run

### Requirements
- Python 3.8 or higher
- No external libraries required (standard library only: `random`, `math`, `time`)

### Part 1 — Hash Functions

```bash
python hash_functions.py
```

Benchmarks four hash functions (Division, Multiplication, Polynomial, Universal) across three key distributions (Sequential, Clustered, Random) at load factor α = 1.0. Reports collision count, max chain length, empty slots, and chi-squared distribution score per function per distribution. Also demonstrates the division method's failure when m is a power of 2 and keys are even integers.

### Part 2 — Collision Resolution

```bash
python collision_resolution.py
```

Runs 27 correctness tests across all three implementations (Separate Chaining, Linear Probing, Double Hashing), then benchmarks all three at five load factors (α = 0.25, 0.50, 0.70, 0.85, 0.95) tracking time, comparisons, and average probes per operation. Also demonstrates tombstone accumulation in linear probing over repeated insert-delete cycles.

---

## Summary of Findings

### Part 1: Hash Functions

The Division method is fast but dangerously sensitive to key structure. On clustered keys (multiples of the table size), it mapped all 1,000 keys to a single slot — 999 collisions, max chain 1,000, chi-squared score of 999,000 — a complete failure. On sequential keys, it accidentally produced a perfect hash (chi-squared 0.0) because consecutive integers map evenly across consecutive slots. This unpredictability makes it unsuitable for production use without careful key analysis.

The Universal Carter-Wegman hash function handled all three distributions consistently, with chi-squared scores staying near the expected range (~400–1,300) across sequential, clustered, and random inputs. The Multiplication method (golden ratio constant) also performed well on clustered keys (chi-squared 374) where Division failed completely. These results confirm that universal hashing provides the strongest consistency guarantee regardless of input structure.

### Part 2: Collision Resolution

Separate chaining scales most gracefully with load factor. Average comparisons grew linearly from 0.11 at α=0.25 to 0.44 at α=0.95 — well-behaved at every load. Linear probing at α=0.95 required an average of 6.60 probes per insert versus chaining's 0.44 comparisons — a 15x difference. Double hashing reduced this to 3.36 probes at α=0.95, confirming that eliminating primary clustering significantly improves high-load performance.

The tombstone demonstration showed that repeated delete-insert cycles cause probes to grow from 1.00 at cycle 0 to 4.02 at cycle 3, even though the number of live keys remains constant. Tombstones occupy ~19% of the table by cycle 5, and the only fix is a full rehash. This makes open addressing with frequent deletions expensive to maintain in practice.

---

## Files

| File | Description |
|---|---|
| `hash_functions.py` | Division, Multiplication, Polynomial, Universal hash functions with benchmarks |
| `collision_resolution.py` | Separate Chaining, Linear Probing, Double Hashing with correctness tests and benchmarks |
| `README.md` | This file |

---

## References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press.
- Carter, J. L., & Wegman, M. N. (1979). Universal classes of hash functions. *Journal of Computer and System Sciences*, 18(2), 143–154.
- Knuth, D. E. (1998). *The Art of Computer Programming, Vol. 3: Sorting and Searching* (2nd ed.). Addison-Wesley.
