# Data Locality Over Pointer-Chasing

**Evaluating cache-conscious data structure optimization for HPC, from C++ to Python**

MSCS-532 (Algorithms and Data Structures) final project. A Python prototype and benchmark
testing whether a data-locality optimization technique documented in a real empirical study of
HPC performance bugs — replacing pointer-chasing linked structures with contiguous ones —
actually transfers from C++ to Python.

**Author:** Parthasarathi Ponnapalli &nbsp;|&nbsp; **Instructor:** Dr. Michael Solomon &nbsp;|&nbsp; MSCS-532

## The empirical study

This project is grounded in:

> Azad, M. A. K., Iqbal, N., Hassan, F., & Roy, P. (2023). An empirical study of high performance
> computing (HPC) performance bugs. In *2023 IEEE/ACM 20th International Conference on Mining
> Software Repositories (MSR)* (pp. 194-206). IEEE.
> [https://doi.org/10.1109/MSR59073.2023.00037](https://doi.org/10.1109/MSR59073.2023.00037)

The authors mined 1,729 candidate performance commits from 23 open-source HPC projects and
manually confirmed 186 true performance bug fixes. Data-locality optimization — replacing
pointer-based structures with contiguous ones — is the largest single fix sub-category they
identify (19.4% of all fixes), grounded in real commits such as `TileDB-d51b082`
(`std::forward_list` traversal was slow due to poor data locality) and `CGAL-8855eb5` (lists
changed to vectors for spatial locality).

## What this project tests

C++'s `std::vector` gets its cache efficiency from storing contiguous *values*. Python's built-in
`list`, however, stores contiguous *pointers* to separately heap-allocated objects — not
contiguous values. Does the paper's optimization lesson still hold in Python? The prototype in
[`code/`](code/) benchmarks four sequence structures — a pointer-chasing linked list, a plain
Python list, a stdlib `array.array`, and a NumPy array — to find out.

**Answer, in short:** it holds strongly for random access (an array-backed structure is ~18,000x
faster than a linked list at one million elements) but only partially for sequential traversal —
a Python `list` and a raw-double `array.array` perform almost identically in a plain loop, because
Python's per-element interpreter overhead dominates regardless of contiguity. The full benefit
only appears once storage is *both* contiguous *and* traversed with vectorized (NumPy) operations.
See [`report/HPC_Optimization_Report.docx`](report/HPC_Optimization_Report.docx) for the complete
analysis.

## Repository structure

```text
code/                    The prototype: four data structures + benchmark harness
  linked_vs_contiguous.py   LinkedList, PyListSequence, ArraySequence, NumpySequence
  benchmark.py               Timing/memory harness -> results.csv + charts
  results.csv                 Real output from the benchmark run described in the report
  README.md                   How to run it, and a summary of findings
  requirements.txt

report/
  HPC_Optimization_Report.docx   Part 1: APA 7 report (6+ pages, cited, with figures)
  figures/                        Benchmark charts embedded in the report

presentation/
  HPC_Optimization_Presentation.pptx   Part 2: narrated slide deck (full script in each slide's Notes pane)
  index.html                            Browser-viewable version of the same deck (Notes toggle included)

source_code_doc/
  Source_Code_and_Screenshots.docx   Source code + output, for Blackboard submission
```

## Running the benchmark

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1        # or: source .venv/bin/activate  (macOS/Linux)
pip install -r code/requirements.txt
python code/benchmark.py
```

This regenerates `code/results.csv` and the three chart PNGs in `report/figures/`. See
[`code/README.md`](code/README.md) for the structures compared, benchmark design, and a full
write-up of the findings.

## Viewing the presentation

Open [`presentation/index.html`](presentation/index.html) directly in a browser (no server or
build step needed) — arrow keys or the on-screen buttons move between slides, and the **Notes**
button toggles the speaker-notes panel for each slide.
`presentation/HPC_Optimization_Presentation.pptx` is the submitted PowerPoint version with the
same content; the full narration script lives in each slide's Notes pane in both files.

## References

1. Azad, M. A. K., Iqbal, N., Hassan, F., & Roy, P. (2023). An empirical study of high
   performance computing (HPC) performance bugs. *2023 IEEE/ACM 20th International Conference on
   Mining Software Repositories (MSR)*, 194-206. https://doi.org/10.1109/MSR59073.2023.00037
2. Chilimbi, T. M., Hill, M. D., & Larus, J. R. (2000). Making pointer-based data structures
   cache conscious. *Computer, 33*(12), 67-74. https://doi.org/10.1109/2.889095
3. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to
   algorithms* (4th ed.). MIT Press.
4. Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., et al. (2020).
   Array programming with NumPy. *Nature, 585*, 357-362. https://doi.org/10.1038/s41586-020-2649-2
5. Jin, G., Song, L., Shi, X., Scherpelz, J., & Lu, S. (2012). Understanding and detecting
   real-world performance bugs. *ACM SIGPLAN Notices, 47*(6), 77-88.
   https://doi.org/10.1145/2345156.2254075
6. Python Software Foundation. (n.d.). *array — Efficient arrays of numeric values*. Python 3
   documentation. https://docs.python.org/3/library/array.html
7. Rao, J., & Ross, K. A. (1999). Cache conscious indexing for decision-support in main memory.
   *Proceedings of VLDB '99*, 78-89. Morgan Kaufmann.
8. Rao, J., & Ross, K. A. (2000). Making B+-trees cache conscious in main memory. *ACM SIGMOD
   Record, 29*(2), 475-486. https://doi.org/10.1145/335191.335449

## Course

MSCS-532: Algorithms and Data Structures — Final Project, Part 1 & Part 2.
