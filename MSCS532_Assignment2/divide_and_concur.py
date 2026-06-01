import time
import tracemalloc
import random
import sys

# ─────────────────────────────────────────────────────────────────────────────
# ALGORITHM 1: BINARY SEARCH
# Divide-and-conquer approach to searching a sorted array.
# Extremely important in embedded systems: O(log n) lookup in lookup tables,
# calibration data, sorted sensor maps, etc.
# ─────────────────────────────────────────────────────────────────────────────


def binary_search(input_array, target, low=None, high=None):
    """
    Recursive Binary Search using divide-and-conquer method.

    Strategy:
      - Divide: split the search space in half each call
      - Conquer: recurse on the half that may contain the target element
      - Combine: return the index found (no merge step needed)

    Time Complexity:
      Best:    O(1)      -- target is always at midpoint
      Average: O(log n)
      Worst:   O(log n)  -- target not present or at extreme

    Space Complexity: O(log n) call stack (recursive)

    Parameters:
        arr    : sorted list of comparable elements
        target : element to search for
        low    : lower bound index (defaults to 0)
        high   : upper bound index (defaults to len(arr)-1)

    Returns:
        index of target in arr, or -1 if not found
    """
    # Set default bounds on the first call
    if low is None:
        low = 0
    if high is None:
        high = len(input_array) - 1

    # BASE CASE: search space exhausted — target not in array
    if low > high:
        return -1

    # DIVIDE: find the midpoint to split the array in half
    mid = (low + high) // 2

    # CONQUER: check the midpoint
    if input_array[mid] == target:
        # Found the target — return its index
        return mid
    elif input_array[mid] < target:
        # Target must be in the RIGHT half — discard the left
        return binary_search(input_array, target, mid + 1, high)
    else:
        # Target must be in the LEFT half — discard the right
        return binary_search(input_array, target, low, mid - 1)


# ─────────────────────────────────────────────────────────────────────────────
# ALGORITHM 2: KARATSUBA MULTIPLICATION
# Divide-and-conquer fast integer multiplication.
# Reduces O(n^2) grade-school multiplication to O(n^1.585).
# Used in cryptography, big-number arithmetic, DSP, and anywhere
# large integer math is needed (e.g., RSA key generation).
# ─────────────────────────────────────────────────────────────────────────────

def karatsuba(x, y):
    """
    Karatsuba Fast Multiplication using divide-and-conquer.

    For two n-digit numbers x and y:
      Split: x = x1 * 10^m + x0,  y = y1 * 10^m + y0
             where m = n // 2

    Then:
      x * y = z2 * 10^(2m) + z1 * 10^m + z0

      where:
        z2 = x1 * y1           (high parts)
        z0 = x0 * y0           (low parts)
        z1 = (x1+x0)*(y1+y0) - z2 - z0  (cross term — the KEY insight!)

    Classic approach needs 4 multiplications; Karatsuba uses only 3.

    Recurrence: T(n) = 3*T(n/2) + O(n)
    By Master Theorem (case 1): T(n) = Θ(n^log2(3)) ≈ Θ(n^1.585)

    Parameters:
        x, y : non-negative integers to multiply

    Returns:
        x * y as an integer
    """
    # BASE CASE: single-digit (or zero) — use direct multiplication
    if x < 10 or y < 10:
        return x * y

    # Determine the split point m (half the number of digits)
    # We base this on the larger of the two numbers
    n = max(len(str(x)), len(str(y)))
    m = n // 2

    # DIVIDE: split x and y at position m
    # x = x1 * 10^m + x0
    power = 10 ** m
    x1, x0 = divmod(x, power)   # high and low halves of x
    y1, y0 = divmod(y, power)   # high and low halves of y

    # CONQUER: three recursive multiplications (instead of four)
    z2 = karatsuba(x1, y1)          # high * high
    z0 = karatsuba(x0, y0)          # low  * low
    z1 = karatsuba(x1 + x0, y1 + y0) - z2 - z0  # cross term

    # COMBINE: reassemble using the Karatsuba identity
    result = z2 * (10 ** (2 * m)) + z1 * (10 ** m) + z0
    return result


# ─────────────────────────────────────────────────────────────────────────────
# BENCHMARKING TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def measure(func, *args):
    """
    Measures execution time (microseconds) and peak memory usage (bytes)
    for a single function call.

    Returns:
        (result, elapsed_us, peak_memory_bytes)
    """
    tracemalloc.start()       # start tracking memory allocations
    start = time.perf_counter()  # use a high-resolution timer for accurate timing

    result = func(*args)

    end = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()  # get peak memory usage
    tracemalloc.stop()

    # convert seconds to microseconds
    elapsed_time_us = (end - start) * 1_000_000  # convert to microseconds
    return result, elapsed_time_us, peak


# ─────────────────────────────────────────────────────────────────────────────
# MAIN: TEST CASES
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sys.setrecursionlimit(100000)

    print("=" * 70)
    print("  DIVIDE-AND-CONQUER ALGORITHM BENCHMARKS")
    print("=" * 70)

    # ── BINARY SEARCH TEST CASES ──────────────────────────────────────────
    print("\n── BINARY SEARCH ──────────────────────────────────────────────────")
    print(f"{'Dataset':<30} {'Size':>8} {'Time (µs)':>12} {'Memory (B)':>12} {'Result':>10}")
    print("-" * 74)

    binarysearch_results = []

    # Test Case 1: Small sorted array — target at midpoint (best case)
    arr_small = list(range(1, 101))           # 100 elements: [1..100]
    target_mid = 50
    _, t, m = measure(binary_search, arr_small, target_mid)
    binarysearch_results.append(
        ("Small (100), mid target", 100, t, m, "Found"))
    print(f"{'Small (100), mid target':<30} {100:>8} {t:>12.2f} {m:>12} {'Found':>10}")

    # Test Case 2: Medium sorted array — target at end (near worst case)
    arr_med = list(range(1, 10001))           # 10,000 elements
    target_end = 9999
    _, t, m = measure(binary_search, arr_med, target_end)
    binarysearch_results.append(
        ("Medium (10k), end target", 10000, t, m, "Found"))
    print(f"{'Medium (10k), end target':<30} {10000:>8} {t:>12.2f} {m:>12} {'Found':>10}")

    # Test Case 3: Large sorted array — target not present (worst case)
    arr_large = list(range(0, 200000, 2))     # 100,000 even numbers
    target_miss = 99999                        # odd — not in array
    _, t, m = measure(binary_search, arr_large, target_miss)
    binarysearch_results.append(
        ("Large (100k), miss", 100000, t, m, "Not Found"))
    print(f"{'Large (100k), miss':<30} {100000:>8} {t:>12.2f} {m:>12} {'Not Found':>10}")

    # Test Case 4: Very large sorted array — random target
    arr_vlarge = list(range(1, 1000001))      # 1,000,000 elements
    target_rand = random.randint(1, 1000000)
    _, t, m = measure(binary_search, arr_vlarge, target_rand)
    binarysearch_results.append(
        ("Very Large (1M), random", 1000000, t, m, "Found"))
    print(f"{'Very Large (1M), random':<30} {1000000:>8} {t:>12.2f} {m:>12} {'Found':>10}")

    # Test Case 5: Single-element array — exact match (trivial best case)
    arr_one = [42]
    _, t, m = measure(binary_search, arr_one, 42)
    binarysearch_results.append(("Single element, exact", 1, t, m, "Found"))
    print(f"{'Single element, exact':<30} {1:>8} {t:>12.2f} {m:>12} {'Found':>10}")

    # Test Case 6: Random target in small array
    arr_rand_small = sorted(random.sample(range(1, 1001), 200))
    target_rs = random.choice(arr_rand_small)
    _, t, m = measure(binary_search, arr_rand_small, target_rs)
    binarysearch_results.append(
        ("Random small (200), hit", 200, t, m, "Found"))
    print(f"{'Random small (200), hit':<30} {200:>8} {t:>12.2f} {m:>12} {'Found':>10}")

    # Test Case 7: Random target in medium array — guaranteed miss
    arr_rand_med = sorted(random.sample(
        range(0, 100000, 2), 50000))  # even numbers only
    # odd — never present
    target_rm = random.randrange(1, 100000, 2)
    _, t, m = measure(binary_search, arr_rand_med, target_rm)
    binarysearch_results.append(
        ("Random med (50k), miss", 50000, t, m, "Not Found"))
    print(f"{'Random med (50k), miss':<30} {50000:>8} {t:>12.2f} {m:>12} {'Not Found':>10}")

    # Test Case 8: Random large array — random target (hit or miss)
    arr_rand_large = sorted(random.sample(range(1, 2000001), 500000))
    target_rl = random.randint(1, 2000001)
    result_rl = binary_search(arr_rand_large, target_rl)
    _, t, m = measure(binary_search, arr_rand_large, target_rl)
    label_rl = "Found" if result_rl != -1 else "Not Found"
    binarysearch_results.append(
        ("Random large (500k), any", 500000, t, m, label_rl))
    print(f"{'Random large (500k), any':<30} {500000:>8} {t:>12.2f} {m:>12} {label_rl:>10}")

    # ── KARATSUBA MULTIPLICATION TEST CASES ──────────────────────────────
    print("\n── KARATSUBA MULTIPLICATION ───────────────────────────────────────")
    print(f"{'Dataset':<30} {'Digits':>8} {'Time (µs)':>12} {'Memory (B)':>12} {'Correct':>10}")
    print("-" * 74)

    kara_results = []

    # Test Case 1: Small numbers (5-digit × 5-digit)
    x1, y1 = 12345, 67890
    res, t, m = measure(karatsuba, x1, y1)
    correct = (res == x1 * y1)
    kara_results.append(("5-digit × 5-digit", 5, t, m, correct))
    print(f"{'5-digit × 5-digit':<30} {5:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 2: Medium numbers (10-digit × 10-digit)
    x2 = 1234567890
    y2 = 9876543210
    res, t, m = measure(karatsuba, x2, y2)
    correct = (res == x2 * y2)
    kara_results.append(("10-digit × 10-digit", 10, t, m, correct))
    print(f"{'10-digit × 10-digit':<30} {10:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 3: Large numbers (20-digit × 20-digit)
    x3 = 12345678901234567890
    y3 = 98765432109876543210
    res, t, m = measure(karatsuba, x3, y3)
    correct = (res == x3 * y3)
    kara_results.append(("20-digit × 20-digit", 20, t, m, correct))
    print(f"{'20-digit × 20-digit':<30} {20:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 4: Very large numbers (50-digit × 50-digit) — crypto-like scale
    x4 = int("1" * 50)   # 50-digit number
    y4 = int("9" * 50)   # another 50-digit number
    res, t, m = measure(karatsuba, x4, y4)
    correct = (res == x4 * y4)
    kara_results.append(("50-digit × 50-digit", 50, t, m, correct))
    print(f"{'50-digit × 50-digit':<30} {50:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 5: Edge case — multiply by zero
    x5, y5 = 99999999999, 0
    res, t, m = measure(karatsuba, x5, y5)
    correct = (res == 0)
    kara_results.append(("Large × 0 (edge)", 11, t, m, correct))
    print(f"{'Large × 0 (edge)':<30} {11:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 6: Random 8-digit × 8-digit
    x6 = random.randint(10**7, 10**8 - 1)
    y6 = random.randint(10**7, 10**8 - 1)
    res, t, m = measure(karatsuba, x6, y6)
    correct = (res == x6 * y6)
    kara_results.append(("8-digit × 8-digit (rand)", 8, t, m, correct))
    print(f"{'8-digit × 8-digit (rand)':<30} {8:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 7: Random 30-digit × 30-digit
    x7 = random.randint(10**29, 10**30 - 1)
    y7 = random.randint(10**29, 10**30 - 1)
    res, t, m = measure(karatsuba, x7, y7)
    correct = (res == x7 * y7)
    kara_results.append(("30-digit × 30-digit (rand)", 30, t, m, correct))
    print(f"{'30-digit × 30-digit (rand)':<30} {30:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    # Test Case 8: Random 100-digit × 100-digit — stress test
    x8 = random.randint(10**99, 10**100 - 1)
    y8 = random.randint(10**99, 10**100 - 1)
    res, t, m = measure(karatsuba, x8, y8)
    correct = (res == x8 * y8)
    kara_results.append(("100-digit × 100-digit (rand)", 100, t, m, correct))
    print(f"{'100-digit × 100-digit (rand)':<30} {100:>8} {t:>12.2f} {m:>12} {str(correct):>10}")

    print("\n" + "=" * 70)
    print("  ALL TESTS COMPLETE")
    print("=" * 70)
