# ============================================================
#  Assignment 7 — Part 1
#  Hash Functions: Design, Analysis, and Comparison
#
#  Author : Parthasarathi Ponnapalli
#  Course : MSCS-532 — Algorithms and Data Structures
# ============================================================

import random
import math
import time


# ============================================================
#  DISTRIBUTION METRICS
#  Measures how evenly a hash function spreads keys across slots.
#  A perfect hash function fills every slot equally.
#  A poor hash function clusters keys into few slots.
#
#  Chi-Squared Score: measures deviation from uniform distribution.
#    Score = sum((observed - expected)^2 / expected) for each slot.
#    Lower is better. Score near 0 = perfectly uniform.
#    Score much larger than m = severe clustering.
# ============================================================


class DistributionMetrics:
    def __init__(self, table_size):
        self.table_size  = table_size
        self.slot_counts = [0] * table_size   # how many keys landed in each slot
        self.collisions  = 0                   # keys that hit an already-occupied slot

    def record(self, slot_index):
        """Record that a key hashed to slot_index."""
        if self.slot_counts[slot_index] > 0:
            self.collisions += 1
        self.slot_counts[slot_index] += 1

    def max_chain_length(self):
        return max(self.slot_counts)

    def empty_slots(self):
        return sum(1 for count in self.slot_counts if count == 0)

    def chi_squared_score(self):
        """
        Chi-squared goodness-of-fit against uniform distribution.
        expected count per slot = n / m (total_keys / table_size).
        Lower score = more uniform. Score >> m indicates clustering.
        """
        total_keys = sum(self.slot_counts)
        if total_keys == 0:
            return 0.0
        expected = total_keys / self.table_size
        return sum((count - expected) ** 2 / expected for count in self.slot_counts)

    def reset(self):
        self.slot_counts = [0] * self.table_size
        self.collisions  = 0


# ============================================================
#  HASH FUNCTION 1 — DIVISION METHOD
#
#  h(k) = k mod m
#
#  The simplest possible hash function. Fast — just one modulo.
#  But behavior depends critically on the choice of m:
#    - If m = 2^p: only the last p bits of k matter.
#      Even keys → all hash values even → half the table unused.
#    - If m = 10^d: only the last d decimal digits matter.
#      Structured IDs with common suffixes → heavy clustering.
#    - If m is prime and not close to a power of 2: much better.
#
#  Ref: CLRS 4th ed., Section 11.3.1
# ============================================================


class DivisionHash:
    def __init__(self, table_size):
        self.table_size = table_size
        self.name       = f"Division (m={table_size})"

    def hash(self, key):
        """h(k) = k mod m."""
        return int(key) % self.table_size

    def __repr__(self):
        return self.name


# ============================================================
#  HASH FUNCTION 2 — MULTIPLICATION METHOD
#
#  h(k) = floor(m * frac(k * A))
#  where frac(x) = x - floor(x) is the fractional part of x
#  and A = (sqrt(5) - 1) / 2 ≈ 0.6180 (the golden ratio conjugate)
#
#  The value of m does not need to be prime — the distribution
#  quality comes from A, not m. Works well even for m = 2^p.
#  Slightly slower than division due to floating-point multiply.
#
#  Ref: CLRS 4th ed., Section 11.3.2 (Knuth's choice of A)
# ============================================================


GOLDEN_RATIO_CONJUGATE = (math.sqrt(5) - 1) / 2   # ≈ 0.6180339887


class MultiplicationHash:
    def __init__(self, table_size):
        self.table_size = table_size
        self.name       = f"Multiplication (A=golden ratio, m={table_size})"

    def hash(self, key):
        """h(k) = floor(m * frac(k * A))."""
        fractional_part = (int(key) * GOLDEN_RATIO_CONJUGATE) % 1.0
        return int(self.table_size * fractional_part)

    def __repr__(self):
        return self.name


# ============================================================
#  HASH FUNCTION 3 — POLYNOMIAL ROLLING HASH (for string keys)
#
#  h(s) = (sum of s[i] * BASE^(n-1-i)) mod m
#
#  Each character contributes to the hash at a position-weighted
#  value. The base multiplier mixes characters so that anagrams
#  ("abc" vs "bca") produce different hash values.
#
#  BASE = 31 is a standard choice (used in Java's String.hashCode).
#  m should be prime to avoid systematic collisions.
#
#  Vulnerability: with a fixed BASE and seed, adversaries can
#  construct strings that all hash to the same value
#  (hash flooding). Python addressed this by adding randomization.
# ============================================================


POLYNOMIAL_BASE = 31


class PolynomialHash:
    def __init__(self, table_size):
        self.table_size = table_size
        self.name       = f"Polynomial (base={POLYNOMIAL_BASE}, m={table_size})"

    def hash(self, key):
        """Polynomial rolling hash for string keys."""
        key_str   = str(key)
        hash_val  = 0
        for character in key_str:
            hash_val = (hash_val * POLYNOMIAL_BASE + ord(character)) % self.table_size
        return hash_val

    def __repr__(self):
        return self.name


# ============================================================
#  HASH FUNCTION 4 — UNIVERSAL HASH (Carter-Wegman Family)
#
#  h(k) = ((a * k + b) mod p) mod m
#
#  where:
#    p — a large prime (larger than the key universe)
#    a — random integer in [1, p-1]
#    b — random integer in [0, p-1]
#
#  Guarantee: for any two distinct keys x ≠ y,
#    Pr[h(x) = h(y)] ≤ 1/m
#  regardless of what the keys are.
#
#  This is what makes it "universal" — the probabilistic collision
#  bound holds for any key set, not just random ones.
#
#  Ref: Carter & Wegman (1979); CLRS 4th ed., Section 11.3.3
# ============================================================


LARGE_PRIME = 10_000_019   # Prime larger than any key we expect


class UniversalHash:
    def __init__(self, table_size):
        self.table_size = table_size
        self.random_a   = random.randint(1, LARGE_PRIME - 1)
        self.random_b   = random.randint(0, LARGE_PRIME - 1)
        self.name       = f"Universal Carter-Wegman (m={table_size})"

    def hash(self, key):
        """h(k) = ((a*k + b) mod p) mod m."""
        return ((self.random_a * int(key) + self.random_b) % LARGE_PRIME) % self.table_size

    def __repr__(self):
        return self.name


# ============================================================
#  KEY GENERATORS
#  Three distributions that expose different hash function weaknesses.
# ============================================================


def generate_sequential_keys(n):
    """Keys are consecutive integers: 0, 1, 2, ..., n-1."""
    return list(range(n))


def generate_clustered_keys(n, table_size):
    """
    Keys are EVEN multiples of table_size.
    Division method with m=table_size will map ALL to slot 0.
    Demonstrates the worst-case failure of division hash.
    """
    return [i * table_size * 2 for i in range(n)]


def generate_random_keys(n, max_val=None):
    """Keys are random integers spread across a wide range."""
    if max_val is None:
        max_val = n * 10
    return random.sample(range(max_val), min(n, max_val))


# ============================================================
#  OUTPUT HELPERS
# ============================================================

COLOR_GREEN  = "\033[92m"
COLOR_RED    = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN   = "\033[96m"
COLOR_BOLD   = "\033[1m"
COLOR_RESET  = "\033[0m"

TOTAL_WIDTH  = 100


def divider(char="─", width=TOTAL_WIDTH):
    return char * width


def section_header(title):
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}{title}{COLOR_RESET}")
    print(divider("═"))


def quality_color(chi_squared, n_keys, table_size):
    """Color-code the chi-squared score relative to expected."""
    # Perfect = 0, acceptable < 2*table_size, poor > 5*table_size
    if chi_squared < table_size * 1.5:
        return COLOR_GREEN
    elif chi_squared < table_size * 5:
        return COLOR_YELLOW
    else:
        return COLOR_RED


# ============================================================
#  BENCHMARK — Compare all hash functions on all key distributions
# ============================================================


def run_hash_function_benchmark():
    section_header("HASH FUNCTION BENCHMARK")
    print(f"  Comparing four hash functions on three key distributions.")
    print(f"  n = 1,000 keys inserted into a table of m = 1,000 slots (load factor α = 1.0).")
    print(f"  Chi-Squared: measures deviation from uniform. Lower = more uniform.")
    print(f"  {COLOR_GREEN}Green{COLOR_RESET} = good distribution  "
          f"{COLOR_YELLOW}Yellow{COLOR_RESET} = moderate clustering  "
          f"{COLOR_RED}Red{COLOR_RESET} = severe clustering\n")

    N          = 1000
    TABLE_SIZE = 1000   # deliberately power-of-10 to expose division method failure

    hash_functions = [
        DivisionHash(TABLE_SIZE),
        MultiplicationHash(TABLE_SIZE),
        PolynomialHash(TABLE_SIZE),
        UniversalHash(TABLE_SIZE),
    ]

    key_distributions = [
        ("Sequential",  generate_sequential_keys(N)),
        ("Clustered",   generate_clustered_keys(N, TABLE_SIZE)),
        ("Random",      generate_random_keys(N)),
    ]

    col_fn   = 42
    col_dist = 14
    col_coll = 12
    col_max  = 10
    col_emp  = 10
    col_chi  = 16

    print(f"  {'Hash Function':<{col_fn}}  {'Distribution':<{col_dist}}  "
          f"{'Collisions':>{col_coll}}  {'MaxChain':>{col_max}}  "
          f"{'EmptySlots':>{col_emp}}  {'Chi-Squared':>{col_chi}}")
    print(f"  {divider('─', col_fn)}  {divider('─', col_dist)}  "
          f"{divider('─', col_coll)}  {divider('─', col_max)}  "
          f"{divider('─', col_emp)}  {divider('─', col_chi)}")

    for dist_label, keys in key_distributions:
        for hf in hash_functions:
            m = DistributionMetrics(TABLE_SIZE)
            t_start = time.perf_counter()
            for key in keys:
                slot = hf.hash(key)
                m.record(slot)
            elapsed_ms = (time.perf_counter() - t_start) * 1000

            chi    = m.chi_squared_score()
            color  = quality_color(chi, N, TABLE_SIZE)
            chi_display = f"{color}{chi:>{col_chi}.1f}{COLOR_RESET}"

            print(
                f"  {str(hf):<{col_fn}}  {dist_label:<{col_dist}}  "
                f"{m.collisions:>{col_coll},}  {m.max_chain_length():>{col_max}}  "
                f"{m.empty_slots():>{col_emp}}  {chi_display}"
            )

        dot_char = "\u00b7"
        print(f"  {divider(dot_char, col_fn + col_dist + col_coll + col_max + col_emp + col_chi + 12)}")


# ============================================================
#  DEMONSTRATE DIVISION METHOD FAILURE
#  Shows explicitly how choosing m = 2^p breaks with even keys.
# ============================================================


def demonstrate_division_method_failure():
    section_header("DIVISION METHOD FAILURE DEMONSTRATION")
    print(f"  Showing what happens when m is a power of 2 and keys are even integers.\n")

    table_size_bad  = 1024   # power of 2 — bad choice
    table_size_good = 1021   # prime — good choice
    n_keys          = 500
    even_keys       = [i * 2 for i in range(n_keys)]   # all even

    for label, table_size in [("m = 1024 (power of 2, BAD)", table_size_bad),
                               ("m = 1021 (prime,    GOOD)", table_size_good)]:
        hf = DivisionHash(table_size)
        m  = DistributionMetrics(table_size)
        for key in even_keys:
            m.record(hf.hash(key))

        chi    = m.chi_squared_score()
        color  = quality_color(chi, n_keys, table_size)
        print(f"  {label}")
        print(f"    Collisions     : {m.collisions:,}")
        print(f"    Max chain      : {m.max_chain_length()}")
        print(f"    Empty slots    : {m.empty_slots():,} / {table_size:,}")
        print(f"    Chi-Squared    : {color}{chi:.1f}{COLOR_RESET}")
        print()


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":
    run_hash_function_benchmark()
    demonstrate_division_method_failure()

    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Division Hash h(k) = k mod m:{COLOR_RESET}
    Time        : O(1)   — single modulo operation
    Distribution: Poor when m is a power of 2 or 10 and keys are structured
    Best m      : Prime, not close to a power of 2

  {COLOR_CYAN}Multiplication Hash h(k) = floor(m * frac(k * A)):{COLOR_RESET}
    Time        : O(1)   — one multiply and one truncation
    Distribution: Good for any m; m need not be prime
    Best A      : Golden ratio conjugate (sqrt(5)-1)/2 ≈ 0.618 (Knuth)

  {COLOR_CYAN}Polynomial Hash h(s) = sum(s[i] * base^i) mod m:{COLOR_RESET}
    Time        : O(L)   — L = key length (one multiply per character)
    Distribution: Good for string keys with varied structure
    Weakness    : Fixed seed enables hash flooding attacks

  {COLOR_CYAN}Universal Hash h(k) = ((a*k + b) mod p) mod m:{COLOR_RESET}
    Time        : O(1)   — two multiplications and two modulos
    Guarantee   : Pr[h(x) = h(y)] <= 1/m for any two distinct keys x, y
    Best choice : When key distribution is unknown or potentially adversarial
    """)
