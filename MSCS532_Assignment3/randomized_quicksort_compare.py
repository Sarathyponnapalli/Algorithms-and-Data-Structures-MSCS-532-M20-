# ============================================================
#  Assignment 3 — Part 1
#  Randomized Quicksort vs Deterministic Quicksort
#
#  Author : Parthasarathi Ponnapalli
#  Course : MSCS-532 — Algorithms and Data Structures
# this file contains the implementation of both randomized and deterministic quicksort algorithms, along with a benchmarking framework to compare their performance on various input distributions. The code also includes a correctness validator that checks both implementations against Python's built-in sort function on a variety of edge cases. The results are formatted in a clear and informative way, highlighting any cases where the deterministic version experiences significant performance degradation due to its pivot selection strategy.
# ============================================================

import random
import time
import sys

sys.setrecursionlimit(100_000)


# ============================================================
#  METRICS TRACKER
#  Counts comparisons and swaps during sorting so we can
#  compare algorithmic work — not just wall-clock time.
# ============================================================


class SortMetrics:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0

    def reset(self):
        self.comparisons = 0
        self.swaps = 0


# Global metrics object shared by both sort implementations
metrics = SortMetrics()


# ============================================================
#  PARTITION  (Lomuto scheme — CLRS Ch. 7.1)
#  Pivot is always the LAST element of the subarray.
#  Returns the final resting index of the pivot.
# ============================================================


def partition(input_array, left_index, right_index):
    pivot_value = input_array[right_index]
    boundary = left_index - 1

    for current_index in range(left_index, right_index):
        metrics.comparisons += 1
        if input_array[current_index] <= pivot_value:
            boundary += 1
            input_array[boundary], input_array[current_index] = (
                input_array[current_index],
                input_array[boundary],
            )
            metrics.swaps += 1

    # Place pivot in its final sorted position
    input_array[boundary + 1], input_array[right_index] = (
        input_array[right_index],
        input_array[boundary + 1],
    )
    metrics.swaps += 1

    return boundary + 1


# ============================================================
#  RANDOMIZED QUICKSORT  (PRIMARY IMPLEMENTATION)
#
#  Pivot is chosen UNIFORMLY AT RANDOM from the subarray.
#  Swap it to the last position, then run standard partition.
#
#  Expected time complexity : O(n log n)  — for ALL input types
#  Worst-case (theoretical) : O(n^2)      — probability negligible
#  Space (call stack)       : O(log n)    — expected recursion depth
#
#  Ref: CLRS 4th ed., Section 7.3
# ============================================================


def quicksort_randomized(input_array, left_index, right_index):
    if left_index >= right_index:
        return

    # Pick a random pivot and move it to the last position
    random_pivot_index = random.randint(left_index, right_index)
    input_array[random_pivot_index], input_array[right_index] = (
        input_array[right_index],
        input_array[random_pivot_index],
    )
    metrics.swaps += 1

    pivot_final_index = partition(input_array, left_index, right_index)

    quicksort_randomized(input_array, left_index, pivot_final_index - 1)
    quicksort_randomized(input_array, pivot_final_index + 1, right_index)


# ============================================================
#  DETERMINISTIC QUICKSORT  (FOR BENCHMARKING / COMPARISON ONLY)
#
#  Pivot is always the FIRST element of the subarray.
#  Degrades to O(n^2) on sorted and reverse-sorted inputs.
#
#  Expected time complexity : O(n log n)  — random input only
#  Worst-case               : O(n^2)      — sorted / reverse-sorted
#  Space (call stack)       : O(n)        — worst case (sorted input)
#
#  Ref: CLRS 4th ed., Section 7.1
# ============================================================


def quicksort_deterministic(input_array, left_index, right_index):
    if left_index >= right_index:
        return

    # Move the first element to the last position to use as pivot
    input_array[left_index], input_array[right_index] = (
        input_array[right_index],
        input_array[left_index],
    )
    metrics.swaps += 1

    pivot_final_index = partition(input_array, left_index, right_index)

    quicksort_deterministic(input_array, left_index, pivot_final_index - 1)
    quicksort_deterministic(input_array, pivot_final_index + 1, right_index)


# ============================================================
#  BENCHMARK RUNNER
#  Runs a sort function on a copy of the input array.
#  Returns: elapsed time (ms), comparisons, swaps.
#  Returns (inf, -1, -1) on RecursionError (O(n^2) blowup).
# ============================================================


def run_benchmark(sort_function, original_array):
    array_copy = original_array[:]
    metrics.reset()

    start_time = time.perf_counter()
    try:
        sort_function(array_copy, 0, len(array_copy) - 1)
        elapsed_time_ms = (time.perf_counter() - start_time) * 1000
        comparisons = metrics.comparisons
        swaps = metrics.swaps
    except RecursionError:
        elapsed_time_ms = float("inf")
        comparisons = -1
        swaps = -1

    return elapsed_time_ms, comparisons, swaps


# ============================================================
#  INPUT GENERATORS
#  Four distributions that expose different algorithm behaviors.
# ============================================================


def generate_random_array(n):
    return random.sample(range(n), n)


def generate_sorted_array(n):
    return list(range(n))


def generate_reverse_sorted_array(n):
    return list(range(n, 0, -1))


def generate_repeated_elements_array(n):
    return [random.randint(0, max(1, n // 10)) for _ in range(n)]


# ============================================================
#  OUTPUT HELPERS
#  Consistent formatting for times, counts, and table borders.
# ============================================================

# ANSI color codes for terminal highlighting
COLOR_GREEN  = "\033[92m"
COLOR_RED    = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN   = "\033[96m"
COLOR_BOLD   = "\033[1m"
COLOR_RESET  = "\033[0m"

# Fixed column widths — every cell is padded to this exact width
COL_DIST    = 16   # Distribution label
COL_N       = 6    # Array size
COL_SAMPLE  = 32   # Input preview
COL_TIME    = 11   # Time (ms)
COL_CMP     = 13   # Comparisons
COL_SWP     = 13   # Swaps

TOTAL_WIDTH = (
    2 + COL_DIST + 2 + COL_N + 2 + COL_SAMPLE + 2
    + COL_TIME + COL_CMP + COL_SWP + 2
    + COL_TIME + COL_CMP + COL_SWP + 2
)


def fmt_time(t):
    """Format a time value — red + BLOWUP label if recursion error."""
    if t == float("inf"):
        return COLOR_RED + f"{'!! BLOWUP':>{COL_TIME}}" + COLOR_RESET
    return f"{t:>{COL_TIME}.3f}"


def fmt_count(c):
    """Format a comparison/swap count — red if blowup."""
    if c == -1:
        return COLOR_RED + f"{'!! BLOWUP':>{COL_CMP}}" + COLOR_RESET
    return f"{c:>{COL_CMP},}"


def divider(char="─", width=TOTAL_WIDTH):
    return char * width


def section_header(title):
    """Centered bold section title with top/bottom border."""
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}{title}{COLOR_RESET}")
    print(divider("═"))


def print_correctness_row(label, input_preview, rand_ok, det_ok):
    rand_label = (COLOR_GREEN + "  PASS" + COLOR_RESET) if rand_ok else (COLOR_RED + "  FAIL" + COLOR_RESET)
    det_label  = (COLOR_GREEN + "  PASS" + COLOR_RESET) if det_ok  else (COLOR_RED + "  FAIL" + COLOR_RESET)
    preview    = input_preview[:28].ljust(28)
    print(f"  {label:<26}  {preview}  {rand_label}  {det_label}")


def print_benchmark_row(dist_label, n, input_sample,
                         rand_time, rand_cmp, rand_swp,
                         det_time,  det_cmp,  det_swp):

    # Highlight rows where deterministic blows up or is 5x+ slower
    is_blowup   = det_time == float("inf")
    is_slow     = (not is_blowup
                   and det_time > rand_time * 5
                   and rand_time != float("inf"))

    dist_col    = f"{dist_label:<{COL_DIST}}"
    n_col       = f"{n:>{COL_N}}"
    sample_col  = input_sample[:COL_SAMPLE].ljust(COL_SAMPLE)

    row = (
        f"  {dist_col}  {n_col}  {sample_col}  "
        f"{fmt_time(rand_time)} {fmt_count(rand_cmp)} {fmt_count(rand_swp)}   "
        f"{fmt_time(det_time)} {fmt_count(det_cmp)} {fmt_count(det_swp)}"
    )

    if is_blowup:
        row += f"  {COLOR_RED}◄ O(n²) BLOWUP{COLOR_RESET}"
    elif is_slow:
        row += f"  {COLOR_YELLOW}◄ {det_time/rand_time:.0f}x slower{COLOR_RESET}"

    print(row)


# ============================================================
#  CORRECTNESS VALIDATOR
#  Checks both implementations against Python's built-in sort.
# ============================================================


def verify_correctness():
    section_header("CORRECTNESS VERIFICATION")

    edge_cases = {
        "Empty array"          : [],
        "Single element"       : [42],
        "Already sorted"       : [1, 2, 3, 4, 5],
        "Reverse sorted"       : [5, 4, 3, 2, 1],
        "All identical"        : [7, 7, 7, 7, 7],
        "Two elements"         : [9, 1],
        "Random (30 elements)" : [random.randint(0, 100) for _ in range(30)],
        "Repeated elements"    : [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
    }

    print(f"\n  {'Test Case':<26}  {'Input Sample':<28}  {'Rand':>6}  {'Det':>6}")
    print(f"  {divider('─', 26)}  {divider('─', 28)}  {divider('─', 6)}  {divider('─', 6)}")

    all_passed = True

    for label, test_array in edge_cases.items():
        expected  = sorted(test_array)
        rand_copy = test_array[:]
        det_copy  = test_array[:]

        metrics.reset()
        try:
            quicksort_randomized(rand_copy, 0, len(rand_copy) - 1)
            rand_ok = rand_copy == expected
        except Exception:
            rand_ok = False

        metrics.reset()
        try:
            quicksort_deterministic(det_copy, 0, len(det_copy) - 1)
            det_ok = det_copy == expected
        except Exception:
            det_ok = False

        if not (rand_ok and det_ok):
            all_passed = False

        preview = str(test_array[:5]) + ("..." if len(test_array) > 5 else "")
        print_correctness_row(label, preview, rand_ok, det_ok)

    print()
    print(f"  {divider('─', 70)}")
    status = (COLOR_GREEN + "  ✔  ALL TESTS PASSED" + COLOR_RESET
              if all_passed else
              COLOR_RED   + "  ✘  SOME TESTS FAILED" + COLOR_RESET)
    print(f"{status}\n")
    return all_passed


# ============================================================
#  MAIN — EMPIRICAL BENCHMARK
# ============================================================

if __name__ == "__main__":

    verify_correctness()

    input_sizes = [100, 500, 1000, 2000, 5000]

    input_distributions = [
        ("Random",         generate_random_array),
        ("Sorted",         generate_sorted_array),
        ("Reverse-Sorted", generate_reverse_sorted_array),
        ("Repeated",       generate_repeated_elements_array),
    ]

    section_header("EMPIRICAL BENCHMARK  —  Randomized vs Deterministic Quicksort")

    # Sub-header legend
    print(f"  Time in milliseconds  |  Comparisons & Swaps tracked per run")
    print(f"  !! BLOWUP = RecursionError (call stack exhausted by O(n²) recursion depth)")
    print(f"  ◄ Nx slower = deterministic is N times slower than randomized on same input\n")

    # Column group headers
    rand_hdr = f"{'─── Randomized Quicksort ───':^{COL_TIME + COL_CMP + COL_SWP + 2}}"
    det_hdr  = f"{'─── Deterministic Quicksort ───':^{COL_TIME + COL_CMP + COL_SWP + 2}}"
    print(f"  {'':>{COL_DIST}}  {'':>{COL_N}}  {'':>{COL_SAMPLE}}  {rand_hdr}   {det_hdr}")

    # Column sub-headers
    print(
        f"  {'Distribution':<{COL_DIST}}  {'n':>{COL_N}}  {'Input Sample (first 8 elements)':<{COL_SAMPLE}}  "
        f"{'Time(ms)':>{COL_TIME}} {'Comparisons':>{COL_CMP}} {'Swaps':>{COL_SWP}}   "
        f"{'Time(ms)':>{COL_TIME}} {'Comparisons':>{COL_CMP}} {'Swaps':>{COL_SWP}}"
    )
    print(
        f"  {divider('─', COL_DIST)}  {divider('─', COL_N)}  {divider('─', COL_SAMPLE)}  "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)} {divider('─', COL_SWP)}   "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)} {divider('─', COL_SWP)}"
    )

    for n in input_sizes:

        for dist_label, generator_function in input_distributions:

            input_array  = generator_function(n)
            input_sample = ", ".join(str(x) for x in input_array[:8]) + " ..."

            rand_time, rand_cmp, rand_swp = run_benchmark(quicksort_randomized,    input_array)
            det_time,  det_cmp,  det_swp  = run_benchmark(quicksort_deterministic, input_array)

            print_benchmark_row(
                dist_label, n, input_sample,
                rand_time, rand_cmp, rand_swp,
                det_time,  det_cmp,  det_swp,
            )

        # Separator between size groups
        print(f"  {divider('·', TOTAL_WIDTH - 2)}")

    # ── Complexity Reference ──────────────────────────────────
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Randomized Quicksort:{COLOR_RESET}
    Expected time  :  O(n log n)  —  holds for ALL input distributions
    Worst case     :  O(n²)       —  theoretically possible, negligible in practice
    Stack depth    :  O(log n)    —  expected

  {COLOR_CYAN}Deterministic Quicksort (first-element pivot):{COLOR_RESET}
    Average time   :  O(n log n)  —  random input only
    Worst case     :  O(n²)       —  triggered by sorted / reverse-sorted input
    Stack depth    :  O(n)        —  worst case on sorted input (recursion danger)
    """)