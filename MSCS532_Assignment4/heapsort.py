# ============================================================
#  Assignment 4 — Part 1
#  Heapsort vs Quicksort vs Merge Sort
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
#  HEAPSORT  (PRIMARY IMPLEMENTATION)
#
#  A max-heap stores the largest element at the root (index 0).
#  For any node at index i:
#    Left  child : 2i + 1
#    Right child : 2i + 2
#    Parent      : (i - 1) // 2
#
#  Algorithm steps (CLRS Ch. 6):
#    1. BUILD-MAX-HEAP  — rearrange the array into a valid max-heap.
#       Runs in O(n) time (not O(n log n) — see analysis in report).
#    2. EXTRACT MAX n-1 times — swap root with last element,
#       shrink heap, restore the heap property via heapify.
#       Each extraction costs O(log n) → total O(n log n).
#
#  Time complexity  : O(n log n) — worst, average, and best case
#  Space complexity : O(log n)   — recursion stack for heapify
#                    (O(1) if heapify is implemented iteratively)
# ============================================================


def max_heapify(input_array, heap_size, root_index):
    """
    Restores the max-heap property for the subtree rooted at root_index.
    Assumes both child subtrees are already valid max-heaps.

    Compares root with its left and right children. If a child is larger,
    swap root with the largest child, then recurse on the affected subtree.

    Time complexity: O(log n) — height of the heap is floor(log n).

    Parameters:
      input_array — the array being sorted (modified in place)
      heap_size   — number of elements currently in the heap
      root_index  — index of the subtree root to heapify
    """
    largest_index = root_index
    left_child = 2 * root_index + 1
    right_child = 2 * root_index + 2

    # Check if left child exists and is larger than current largest
    if left_child < heap_size:
        metrics.comparisons += 1
        if input_array[left_child] > input_array[largest_index]:
            largest_index = left_child

    # Check if right child exists and is larger than current largest
    if right_child < heap_size:
        metrics.comparisons += 1
        if input_array[right_child] > input_array[largest_index]:
            largest_index = right_child

    # If root is not the largest, swap and recurse downward
    if largest_index != root_index:
        input_array[root_index], input_array[largest_index] = (
            input_array[largest_index],
            input_array[root_index],
        )
        metrics.swaps += 1
        max_heapify(input_array, heap_size, largest_index)


def build_max_heap(input_array):
    """
    Converts an arbitrary array into a valid max-heap in O(n) time.

    All leaf nodes (indices n//2 to n-1) are trivially valid heaps.
    We only need to heapify internal nodes, starting from the last
    internal node (index n//2 - 1) and working up to the root.

    The O(n) bound (not O(n log n)) comes from the fact that most
    heapify calls operate on subtrees of small height — only the
    root requires a full O(log n) traversal.

    Ref: CLRS 4th ed., Section 6.3, Theorem 6.1
    """
    heap_size = len(input_array)
    last_internal = heap_size // 2 - 1  # last non-leaf node

    for node_index in range(last_internal, -1, -1):
        max_heapify(input_array, heap_size, node_index)


def heapsort(input_array, left_index=None, right_index=None):
    """
    Sorts input_array in ascending order using Heapsort.

    Note: left_index and right_index are accepted but ignored —
    Heapsort operates on the full array. They exist only so this
    function shares the same signature as quicksort for the
    benchmark runner.

    Steps:
      1. Build a max-heap from the array — O(n).
      2. Repeatedly extract the max (root) by swapping it with
         the last element and shrinking the heap by one — O(n log n).

    Ref: CLRS 4th ed., Section 6.4
    """
    build_max_heap(input_array)

    # Extract elements one by one from the heap
    for last_position in range(len(input_array) - 1, 0, -1):
        # Swap root (maximum) with the last unsorted element
        input_array[0], input_array[last_position] = (
            input_array[last_position],
            input_array[0],
        )
        metrics.swaps += 1

        # Restore the heap property on the reduced heap
        max_heapify(input_array, last_position, 0)


# ============================================================
#  MERGE SORT  (FOR COMPARISON)
#
#  Stable, O(n log n) in all cases, but requires O(n) extra space.
#  Included to contrast with Heapsort's in-place O(1) space.
# ============================================================


def merge_sort(input_array, left_index=None, right_index=None):
    """
    Sorts input_array in ascending order using Merge Sort.
    Uses a helper to merge two sorted halves.
    """
    n = len(input_array)
    if n <= 1:
        return input_array

    mid = n // 2
    left_half = merge_sort(input_array[:mid])
    right_half = merge_sort(input_array[mid:])

    return _merge(input_array, left_half, right_half)


def _merge(output_array, left_half, right_half):
    """Merges two sorted halves back into output_array."""
    left_pos = right_pos = write_pos = 0

    while left_pos < len(left_half) and right_pos < len(right_half):
        metrics.comparisons += 1
        if left_half[left_pos] <= right_half[right_pos]:
            output_array[write_pos] = left_half[left_pos]
            left_pos += 1
        else:
            output_array[write_pos] = right_half[right_pos]
            right_pos += 1
        write_pos += 1

    # Copy remaining elements from whichever half has items left
    while left_pos < len(left_half):
        output_array[write_pos] = left_half[left_pos]
        left_pos += 1
        write_pos += 1

    while right_pos < len(right_half):
        output_array[write_pos] = right_half[right_pos]
        right_pos += 1
        write_pos += 1

    return output_array


# ============================================================
#  RANDOMIZED QUICKSORT  (FOR COMPARISON)
#  Same implementation as Assignment 3 — included here
#  so we have a direct three-way comparison.
#
#  Ref: CLRS 4th ed., Section 7.3
# ============================================================


def quicksort_partition(input_array, left_index, right_index):
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


def quicksort_randomized(input_array, left_index=None, right_index=None):
    """Randomized Quicksort — random pivot selection."""
    if left_index is None:
        left_index = 0
    if right_index is None:
        right_index = len(input_array) - 1

    if left_index >= right_index:
        return

    random_pivot_index = random.randint(left_index, right_index)
    input_array[random_pivot_index], input_array[right_index] = (
        input_array[right_index],
        input_array[random_pivot_index],
    )
    metrics.swaps += 1

    pivot_final_index = quicksort_partition(input_array, left_index, right_index)
    quicksort_randomized(input_array, left_index, pivot_final_index - 1)
    quicksort_randomized(input_array, pivot_final_index + 1, right_index)


# ============================================================
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


# ============================================================
#  OUTPUT HELPERS
# ============================================================

# ANSI color codes for terminal highlighting
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

COL_DIST = 16
COL_N = 6
COL_TIME = 11
COL_CMP = 13
COL_SWP = 11

TOTAL_WIDTH = 2 + COL_DIST + 2 + COL_N + 2 + (COL_TIME + COL_CMP + COL_SWP + 2) * 3 + 4


def divider(char="─", width=TOTAL_WIDTH):
    return char * width


def section_header(title):
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}{title}{COLOR_RESET}")
    print(divider("═"))


def fmt_time(t):
    if t == float("inf"):
        return COLOR_RED + f"{'BLOWUP':>{COL_TIME}}" + COLOR_RESET
    return f"{t:>{COL_TIME}.3f}"


def fmt_count(c, width):
    if c == -1:
        return COLOR_RED + f"{'BLOWUP':>{width}}" + COLOR_RESET
    return f"{c:>{width},}"


# ============================================================
#  CORRECTNESS VALIDATOR
# ============================================================


def verify_correctness():
    section_header("CORRECTNESS VERIFICATION")

    edge_cases = {
        "Empty array": [],
        "Single element": [42],
        "Already sorted": [1, 2, 3, 4, 5],
        "Reverse sorted": [5, 4, 3, 2, 1],
        "All identical": [7, 7, 7, 7, 7],
        "Two elements": [9, 1],
        "Random (30 elements)": [random.randint(0, 100) for _ in range(30)],
        "Repeated elements": [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
    }

    algorithms = [
        ("Heapsort", heapsort),
        ("MergeSort", merge_sort),
        ("Quicksort", quicksort_randomized),
    ]

    print(
        f"\n  {'Test Case':<26}  {'Input Sample':<28}  {'Heap':>5}  {'Merge':>6}  {'Quick':>6}"
    )
    print(
        f"  {divider('─', 26)}  {divider('─', 28)}  {divider('─', 5)}  {divider('─', 6)}  {divider('─', 6)}"
    )

    all_passed = True

    for label, test_array in edge_cases.items():
        expected = sorted(test_array)
        results = []

        for _, sort_fn in algorithms:
            arr_copy = test_array[:]
            metrics.reset()
            try:
                sort_fn(arr_copy)
                ok = arr_copy == expected
            except Exception:
                ok = False
            if not ok:
                all_passed = False
            results.append(ok)

        preview = str(test_array[:5]) + ("..." if len(test_array) > 5 else "")
        status = [
            (
                (COLOR_GREEN + " PASS" + COLOR_RESET)
                if ok
                else (COLOR_RED + " FAIL" + COLOR_RESET)
            )
            for ok in results
        ]
        print(f"  {label:<26}  {preview:<28}  {status[0]}  {status[1]}  {status[2]}")

    print()
    print(f"  {divider('─', 70)}")
    overall = (
        COLOR_GREEN + "  ✔  ALL TESTS PASSED" + COLOR_RESET
        if all_passed
        else COLOR_RED + "  ✘  SOME TESTS FAILED" + COLOR_RESET
    )
    print(f"{overall}\n")
    return all_passed


# ============================================================
#  MAIN — EMPIRICAL BENCHMARK
# ============================================================

if __name__ == "__main__":

    verify_correctness()

    input_sizes = [100, 500, 1000, 2000, 5000]

    input_distributions = [
        ("Random", generate_random_array),
        ("Sorted", generate_sorted_array),
        ("Reverse-Sorted", generate_reverse_sorted_array),
        ("Repeated", lambda n: [random.randint(0, max(1, n // 10)) for _ in range(n)]),
    ]

    algorithms = [
        ("Heapsort", heapsort),
        ("MergeSort", merge_sort),
        ("Quicksort", quicksort_randomized),
    ]

    section_header("EMPIRICAL BENCHMARK  —  Heapsort vs Merge Sort vs Quicksort")
    print(f"  Time in milliseconds  |  Comparisons and Swaps per run\n")

    # Group headers
    grp_w = COL_TIME + COL_CMP + COL_SWP + 2
    print(
        f"  {'':>{COL_DIST}}  {'':>{COL_N}}  "
        f"{'─── Heapsort ───':^{grp_w}}  "
        f"{'─── Merge Sort ───':^{grp_w}}  "
        f"{'─── Quicksort ───':^{grp_w}}"
    )
    print(
        f"  {'Distribution':<{COL_DIST}}  {'n':>{COL_N}}  "
        f"{'Time(ms)':>{COL_TIME}} {'Compares':>{COL_CMP}} {'Swaps':>{COL_SWP}}  "
        f"{'Time(ms)':>{COL_TIME}} {'Compares':>{COL_CMP}} {'Swaps':>{COL_SWP}}  "
        f"{'Time(ms)':>{COL_TIME}} {'Compares':>{COL_CMP}} {'Swaps':>{COL_SWP}}"
    )
    print(
        f"  {divider('─', COL_DIST)}  {divider('─', COL_N)}  "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)} {divider('─', COL_SWP)}  "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)} {divider('─', COL_SWP)}  "
        f"{divider('─', COL_TIME)} {divider('─', COL_CMP)} {divider('─', COL_SWP)}"
    )

    for n in input_sizes:
        for dist_label, generator_function in input_distributions:

            input_array = generator_function(n)
            row_results = []

            for _, sort_fn in algorithms:
                t, c, s = run_benchmark(sort_fn, input_array)
                row_results.append((t, c, s))

            heap_t, heap_c, heap_s = row_results[0]
            merge_t, merge_c, merge_s = row_results[1]
            quick_t, quick_c, quick_s = row_results[2]

            print(
                f"  {dist_label:<{COL_DIST}}  {n:>{COL_N}}  "
                f"{fmt_time(heap_t)} {fmt_count(heap_c, COL_CMP)} {fmt_count(heap_s, COL_SWP)}  "
                f"{fmt_time(merge_t)} {fmt_count(merge_c, COL_CMP)} {fmt_count(merge_s, COL_SWP)}  "
                f"{fmt_time(quick_t)} {fmt_count(quick_c, COL_CMP)} {fmt_count(quick_s, COL_SWP)}"
            )

        print(f"  {divider('·', TOTAL_WIDTH - 2)}")

    # ── Complexity Reference ──────────────────────────────────
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Heapsort:{COLOR_RESET}
    All cases (worst/avg/best) : O(n log n)  — no input can avoid this
    Space                      : O(log n)    — recursion stack for heapify
                                 O(1)        — if heapify implemented iteratively
    Stable?                    : No

  {COLOR_CYAN}Merge Sort:{COLOR_RESET}
    All cases                  : O(n log n)
    Space                      : O(n)        — requires auxiliary arrays
    Stable?                    : Yes

  {COLOR_CYAN}Randomized Quicksort:{COLOR_RESET}
    Expected                   : O(n log n)
    Worst case (theoretical)   : O(n²)       — negligible probability
    Space                      : O(log n)    — expected call stack depth
    Stable?                    : No
    """)
