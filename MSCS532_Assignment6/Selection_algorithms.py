# ============================================================
#  Assignment 6 — Part 1
#  Selection Algorithms: Median of Medians & Randomized Quickselect
#
#  Author : Parthasarathi Ponnapalli
#  Course : MSCS-532 — Algorithms and Data Structures
# ============================================================

import random
import time
import sys

sys.setrecursionlimit(100_000)


# ============================================================
#  METRICS TRACKER
#  Counts comparisons so we measure algorithmic work
#  independently of wall-clock timing noise.
# ============================================================


class SelectionMetrics:
    def __init__(self):
        self.comparisons = 0

    def reset(self):
        self.comparisons = 0


metrics = SelectionMetrics()


# ============================================================
#  RANDOMIZED QUICKSELECT  (PRIMARY IMPLEMENTATION)
#
#  Finds the k-th smallest element (0-indexed) in expected O(n) time.
#
#  Strategy:
#    1. Choose a pivot UNIFORMLY AT RANDOM from the array.
#    2. Partition into three groups: less than, equal to, greater than pivot.
#    3. If k falls in the "less" group, recurse there.
#       If k falls in the "equal" group, the pivot is the answer.
#       Otherwise recurse into the "greater" group with adjusted k.
#
#  Why expected O(n)?
#    Each random pivot has a 50% chance of landing in the middle half
#    (between the 25th and 75th percentile), which guarantees reducing
#    the problem size by at least 25% on average. This gives an expected
#    recurrence that solves to O(n).
#
#  Expected time complexity : O(n)   — for ALL input distributions
#  Worst-case (theoretical) : O(n^2) — all pivots worst possible, negligible
#  Space complexity          : O(n)   — new sub-arrays at each recursive call
#                              O(log n) expected stack depth
#
#  Ref: CLRS 4th ed., Section 9.2
# ============================================================


def quickselect_randomized(input_array, k):
    """
    Returns the k-th smallest element (0-indexed) of input_array.

    Parameters:
      input_array — list of comparable elements
      k           — 0-indexed rank (0 = minimum, n-1 = maximum)

    Raises IndexError if k is out of range.
    """
    if not input_array:
        raise IndexError("Cannot select from an empty array.")
    if k < 0 or k >= len(input_array):
        raise IndexError(f"k={k} is out of range for array of length {len(input_array)}.")

    # Base case: only one element
    if len(input_array) == 1:
        return input_array[0]

    # ── Step 1: Choose a random pivot ─────────────────────────
    pivot = random.choice(input_array)

    # ── Step 2: Partition into three groups ───────────────────
    less_than_pivot    = []
    equal_to_pivot     = []
    greater_than_pivot = []

    for element in input_array:
        metrics.comparisons += 1
        if element < pivot:
            less_than_pivot.append(element)
        elif element == pivot:
            equal_to_pivot.append(element)
        else:
            greater_than_pivot.append(element)

    # ── Step 3: Determine which group contains rank k ─────────
    if k < len(less_than_pivot):
        return quickselect_randomized(less_than_pivot, k)

    elif k < len(less_than_pivot) + len(equal_to_pivot):
        return pivot   # k falls in the equal group — pivot is the answer

    else:
        adjusted_k = k - len(less_than_pivot) - len(equal_to_pivot)
        return quickselect_randomized(greater_than_pivot, adjusted_k)


# ============================================================
#  MEDIAN OF MEDIANS  (DETERMINISTIC SELECTION)
#
#  Finds the k-th smallest element in WORST-CASE O(n) time.
#
#  Strategy (CLRS Section 9.3):
#    1. Divide array into groups of at most 5 elements.
#    2. Find the median of each group by sorting it (O(1) per group,
#       since each group has at most 5 elements).
#    3. Recursively find the median of those medians — call it the pivot.
#    4. Partition the full array around the pivot.
#    5. Recurse on the appropriate partition.
#
#  Why O(n) worst case?
#    The median-of-medians pivot guarantees at least 30% of elements
#    are strictly less than it and at least 30% are strictly greater.
#    This means each recursive call reduces the problem by at least 30%,
#    giving the recurrence T(n) <= T(n/5) + T(7n/10) + O(n) = O(n).
#
#  Time complexity  : O(n)   — guaranteed worst case
#  Space complexity : O(n)   — sub-arrays created at each level
#                    O(log n) — stack depth for the 1/5 recursion
#
#  Ref: CLRS 4th ed., Section 9.3
# ============================================================

GROUP_SIZE = 5   # Standard group size — changing this affects the constant


def _median_of_group(group):
    """
    Returns the median of a small group (size <= GROUP_SIZE).
    Sorting a group of at most 5 elements is O(1) — constant work.
    """
    sorted_group = sorted(group)
    metrics.comparisons += len(group) * (len(group) - 1) // 2  # approximate sort comparisons
    return sorted_group[len(sorted_group) // 2]


def median_of_medians(input_array, k):
    """
    Returns the k-th smallest element (0-indexed) of input_array
    using the deterministic Median of Medians algorithm.

    Parameters:
      input_array — list of comparable elements
      k           — 0-indexed rank (0 = minimum, n-1 = maximum)

    Raises IndexError if k is out of range.
    """
    if not input_array:
        raise IndexError("Cannot select from an empty array.")
    if k < 0 or k >= len(input_array):
        raise IndexError(f"k={k} is out of range for array of length {len(input_array)}.")

    n = len(input_array)

    # Base case: small enough to sort directly
    if n <= GROUP_SIZE:
        sorted_arr = sorted(input_array)
        metrics.comparisons += n * (n - 1) // 2
        return sorted_arr[k]

    # ── Step 1: Divide into groups of GROUP_SIZE ──────────────
    groups = [
        input_array[i : i + GROUP_SIZE]
        for i in range(0, n, GROUP_SIZE)
    ]

    # ── Step 2: Find median of each group ─────────────────────
    group_medians = [_median_of_group(group) for group in groups]

    # ── Step 3: Recursively find the median of medians ────────
    pivot = median_of_medians(group_medians, len(group_medians) // 2)

    # ── Step 4: Partition full array around the pivot ─────────
    less_than_pivot    = []
    equal_to_pivot     = []
    greater_than_pivot = []

    for element in input_array:
        metrics.comparisons += 1
        if element < pivot:
            less_than_pivot.append(element)
        elif element == pivot:
            equal_to_pivot.append(element)
        else:
            greater_than_pivot.append(element)

    # ── Step 5: Recurse on the appropriate partition ──────────
    if k < len(less_than_pivot):
        return median_of_medians(less_than_pivot, k)

    elif k < len(less_than_pivot) + len(equal_to_pivot):
        return pivot

    else:
        adjusted_k = k - len(less_than_pivot) - len(equal_to_pivot)
        return median_of_medians(greater_than_pivot, adjusted_k)


# ============================================================
#  BENCHMARK RUNNER
#  Runs a selection function and measures time and comparisons.
#  Returns (elapsed_ms, comparisons).
# ============================================================


def run_benchmark(selection_function, input_array, k):
    array_copy = input_array[:]
    metrics.reset()

    start_time = time.perf_counter()
    try:
        result = selection_function(array_copy, k)
        elapsed_ms  = (time.perf_counter() - start_time) * 1000
        comparisons = metrics.comparisons
    except RecursionError:
        result      = None
        elapsed_ms  = float("inf")
        comparisons = -1

    return elapsed_ms, comparisons, result


# ============================================================
#  INPUT GENERATORS
# ============================================================


def generate_random_array(n):
    return random.sample(range(n * 2), n)

def generate_sorted_array(n):
    return list(range(n))

def generate_reverse_sorted_array(n):
    return list(range(n, 0, -1))

def generate_repeated_elements_array(n):
    return [random.randint(0, max(1, n // 10)) for _ in range(n)]


# ============================================================
#  OUTPUT HELPERS
# ============================================================

COLOR_GREEN  = "\033[92m"
COLOR_RED    = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN   = "\033[96m"
COLOR_BOLD   = "\033[1m"
COLOR_RESET  = "\033[0m"

COL_DIST  = 16
COL_N     =  6
COL_K     =  6
COL_TIME  = 11
COL_CMP   = 14

TOTAL_WIDTH = 2 + COL_DIST + 2 + COL_N + 2 + COL_K + 2 + (COL_TIME + COL_CMP + 2) * 2 + 4


def divider(char="─", width=TOTAL_WIDTH):
    return char * width


def section_header(title):
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}{title}{COLOR_RESET}")
    print(divider("═"))


def fmt_time(t):
    if t == float("inf"):
        return COLOR_RED + f"{'!! ERROR':>{COL_TIME}}" + COLOR_RESET
    return f"{t:>{COL_TIME}.3f}"


def fmt_count(c, width=COL_CMP):
    if c == -1:
        return COLOR_RED + f"{'!! ERROR':>{width}}" + COLOR_RESET
    return f"{c:>{width},}"


# ============================================================
#  CORRECTNESS VALIDATOR
# ============================================================


def verify_correctness():
    section_header("CORRECTNESS VERIFICATION")

    test_cases = [
        ([3, 1, 4, 1, 5, 9, 2, 6],  0,  "k=0 (minimum)"),
        ([3, 1, 4, 1, 5, 9, 2, 6],  7,  "k=n-1 (maximum)"),
        ([3, 1, 4, 1, 5, 9, 2, 6],  3,  "k=3 (median area)"),
        ([42],                        0,  "Single element"),
        ([5, 5, 5, 5, 5],            2,  "All identical, k=2"),
        ([2, 1],                      0,  "Two elements, k=0"),
        ([2, 1],                      1,  "Two elements, k=1"),
        (list(range(100, 0, -1)),    49,  "Reverse sorted n=100, k=49"),
        ([random.randint(0, 50) for _ in range(30)], 14, "Repeated n=30, k=14"),
    ]

    print(f"\n  {'Test Case':<30} {'k':>5}  {'Expected':>10}  {'MoM':>10}  {'QSelect':>10}  {'Match':>6}")
    print(f"  {divider('─', 30)}  {divider('─', 5)}  {divider('─', 10)}  {divider('─', 10)}  {divider('─', 10)}  {divider('─', 6)}")

    all_passed = True

    for array, k, label in test_cases:
        expected = sorted(array)[k]

        metrics.reset()
        mom_result = median_of_medians(array[:], k)
        metrics.reset()
        qs_result  = quickselect_randomized(array[:], k)

        both_ok = (mom_result == expected and qs_result == expected)
        if not both_ok:
            all_passed = False

        mark = COLOR_GREEN + "  PASS" + COLOR_RESET if both_ok else COLOR_RED + "  FAIL" + COLOR_RESET
        print(f"  {label:<30} {k:>5}  {expected:>10}  {mom_result:>10}  {qs_result:>10}  {mark}")

    print()
    print(f"  {divider('─', 70)}")
    overall = (COLOR_GREEN + "  ✔  ALL TESTS PASSED" + COLOR_RESET
               if all_passed else COLOR_RED + "  ✘  SOME TESTS FAILED" + COLOR_RESET)
    print(f"{overall}\n")
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

    section_header("EMPIRICAL BENCHMARK  —  Median of Medians vs Randomized Quickselect")
    print(f"  Searching for the MEDIAN element (k = n//2) in each array.")
    print(f"  Time in milliseconds  |  Comparisons tracked per run\n")

    det_hdr  = "\u2500\u2500 Median of Medians \u2500\u2500"
    rand_hdr = "\u2500\u2500 Quickselect \u2500\u2500"
    grp_w    = COL_TIME + COL_CMP + 2

    print(f"  {'':>{COL_DIST}}  {'':>{COL_N}}  {'':>{COL_K}}  "
          f"{det_hdr:^{grp_w}}   {rand_hdr:^{grp_w}}")
    print(
        f"  {'Distribution':<{COL_DIST}}  {'n':>{COL_N}}  {'k':>{COL_K}}  "
        f"{'Time(ms)':>{COL_TIME}} {'Comparisons':>{COL_CMP}}   "
        f"{'Time(ms)':>{COL_TIME}} {'Comparisons':>{COL_CMP}}"
    )
    print(
        f"  {divider('─', COL_DIST)}  {divider('─', COL_N)}  {divider('─', COL_K)}  "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)}   "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)}"
    )

    for n in input_sizes:
        k = n // 2   # always search for the median

        for dist_label, generator_function in input_distributions:

            input_array = generator_function(n)

            mom_time, mom_cmp, mom_result  = run_benchmark(median_of_medians,       input_array, k)
            qs_time,  qs_cmp,  qs_result   = run_benchmark(quickselect_randomized,  input_array, k)

            # Validate both returned the same answer
            expected     = sorted(input_array)[k]
            correct_mark = ""
            if mom_result != expected or qs_result != expected:
                correct_mark = f"  {COLOR_RED}MISMATCH{COLOR_RESET}"

            # Flag if MoM is significantly slower (more than 3x)
            slowdown_flag = ""
            if (mom_time != float("inf") and qs_time != float("inf")
                    and mom_time > qs_time * 3):
                slowdown_flag = f"  {COLOR_YELLOW}MoM {mom_time/qs_time:.1f}x slower{COLOR_RESET}"

            print(
                f"  {dist_label:<{COL_DIST}}  {n:>{COL_N}}  {k:>{COL_K}}  "
                f"{fmt_time(mom_time)} {fmt_count(mom_cmp)}   "
                f"{fmt_time(qs_time)}  {fmt_count(qs_cmp)}"
                f"{correct_mark}{slowdown_flag}"
            )

        dot_char = "\u00b7"
        print(f"  {divider(dot_char, TOTAL_WIDTH - 2)}")

    # ── Complexity Reference ──────────────────────────────────
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Median of Medians (Deterministic):{COLOR_RESET}
    Time complexity  :  O(n)     — guaranteed worst case for ALL inputs
    Space complexity :  O(n)     — sub-arrays created at each level
                        O(log n) — recursion stack depth (1/5 recursion)
    Pivot guarantee  :  At least 30% of elements on each side of pivot

  {COLOR_CYAN}Randomized Quickselect:{COLOR_RESET}
    Expected time    :  O(n)     — holds for ALL input distributions
    Worst case       :  O(n^2)   — all pivots land at extremes (negligible prob.)
    Space complexity :  O(n)     — sub-arrays at each recursive call
                        O(log n) — expected stack depth

  See report for full theoretical proofs.
  Ref: Cormen et al. (2022), Introduction to Algorithms, 4th ed., Ch. 9
    """)