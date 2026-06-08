# ============================================================
#  Assignment 3 — Part 2
#  Hash Table with Chaining
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
#  Counts operations per insert/search/delete call so we can
#  measure actual algorithmic work, not just wall-clock time.
# ============================================================


class HashMetrics:
    def __init__(self):
        self.comparisons = 0  # Number of key comparisons during chain traversal
        self.collisions = 0  # Number of times a slot already had entries on insert
        self.chain_probes = 0  # Total chain nodes visited across all operations

    def reset(self):
        self.comparisons = 0
        self.chain_probes = 0
        self.collisions = 0


# Global metrics object shared by all hash table operations
metrics = HashMetrics()


# ============================================================
#  UNIVERSAL HASH FUNCTION  (Carter-Wegman Family)
#
#  Formula:  h(k) = ((a * k + b) mod p) mod m
#
#  Where:
#    p — a prime larger than the universe of keys
#    a — random integer in [1, p-1]
#    b — random integer in [0, p-1]
#    m — number of slots in the hash table
#
#  Guarantee: for any two distinct keys x ≠ y,
#    Pr[h(x) = h(y)] ≤ 1/m
#  This holds regardless of what the keys are.
#
#  Ref: CLRS 4th ed., Section 11.3.3
# ============================================================


LARGE_PRIME = 10_000_019  # Prime larger than any key value we expect


def make_hash_function(number_of_slots):
    """
    Creates and returns a new random hash function for a table
    of size `number_of_slots`. Each call returns a different
    function — this is what makes it 'universal'.
    """
    random_a = random.randint(1, LARGE_PRIME - 1)
    random_b = random.randint(0, LARGE_PRIME - 1)

    def hash_function(key):
        # Convert string keys to integers using polynomial rolling hash
        if isinstance(key, str):
            key = sum(
                ord(character) * (31**position)
                for position, character in enumerate(key)
            )
        return ((random_a * key + random_b) % LARGE_PRIME) % number_of_slots

    return hash_function


# ============================================================
#  HASH TABLE WITH CHAINING  (PRIMARY IMPLEMENTATION)
#
#  Structure:
#    - An array of `number_of_slots` slots.
#    - Each slot holds a Python list (the "chain").
#    - Key-value pairs that hash to the same slot are stored
#      together in that slot's chain.
#
#  Operations and Expected Complexity (CLRS §11.2):
#    Insert : O(1)       — hash + prepend to chain
#    Search : O(1 + α)  — hash + traverse chain of avg length α
#    Delete : O(1 + α)  — hash + traverse + remove
#
#  Where α = n / m is the LOAD FACTOR (elements / slots).
#  When m = Θ(n), α = O(1) and all operations run in O(1).
#
#  Dynamic Resizing:
#    When α exceeds LOAD_FACTOR_THRESHOLD, the table doubles
#    in size and all keys are rehashed. This keeps α bounded
#    and maintains O(1) amortized performance.
#
#  Ref: CLRS 4th ed., Section 11.2 — Hash Tables with Chaining
# ============================================================

LOAD_FACTOR_THRESHOLD = 0.75  # Resize when n/m exceeds this
INITIAL_NUMBER_OF_SLOTS = 16  # Starting table size (power of 2)


class HashTableWithChaining:

    def __init__(self, initial_slots=INITIAL_NUMBER_OF_SLOTS):
        self.number_of_slots = initial_slots
        self.number_of_elements = 0
        self.chains = [[] for _ in range(self.number_of_slots)]
        self.hash_function = make_hash_function(self.number_of_slots)
        self.resize_count = 0  # How many times the table has doubled

    # ── Core Operations ──────────────────────────────────────

    def insert(self, key, value):
        """
        Add or update a key-value pair.

        Steps:
          1. Hash the key to find the target slot.
          2. Walk the chain at that slot — if the key already
             exists, update its value in place.
          3. If the key is new, append it to the chain.
          4. Check the load factor and resize if needed.

        Expected time: O(1) under simple uniform hashing.
        """
        slot_index = self.hash_function(key)
        chain = self.chains[slot_index]

        if len(chain) > 0:
            metrics.collisions += 1  # Slot was not empty on arrival

        # Walk the chain to check for an existing key
        for position, (existing_key, existing_value) in enumerate(chain):
            metrics.comparisons += 1
            metrics.chain_probes += 1
            if existing_key == key:
                chain[position] = (key, value)  # Update in place
                return

        # Key not found in chain — append as new entry
        chain.append((key, value))
        self.number_of_elements += 1

        # Resize if load factor exceeded
        if self.current_load_factor() > LOAD_FACTOR_THRESHOLD:
            self._resize_to(self.number_of_slots * 2)

    def search(self, key):
        """
        Return the value for `key`, or None if not found.

        Steps:
          1. Hash the key to find the target slot.
          2. Walk the chain looking for a matching key.
          3. Return the associated value, or None.

        Expected time: O(1 + α) under simple uniform hashing.
        """
        slot_index = self.hash_function(key)
        chain = self.chains[slot_index]

        for existing_key, existing_value in chain:
            metrics.comparisons += 1
            metrics.chain_probes += 1
            if existing_key == key:
                return existing_value

        return None  # Key not present in the table

    def delete(self, key):
        """
        Remove a key-value pair. Returns True if deleted,
        False if the key was not found.

        Steps:
          1. Hash the key to find the target slot.
          2. Walk the chain to find the key.
          3. Remove it from the chain and decrement the count.

        Expected time: O(1 + α) under simple uniform hashing.
        """
        slot_index = self.hash_function(key)
        chain = self.chains[slot_index]

        for position, (existing_key, _) in enumerate(chain):
            metrics.comparisons += 1
            metrics.chain_probes += 1
            if existing_key == key:
                chain.pop(position)
                self.number_of_elements -= 1
                return True

        return False  # Key was not in the table

    # ── Internal Helpers ─────────────────────────────────────

    def current_load_factor(self):
        """α = n / m  (elements / slots)"""
        return self.number_of_elements / self.number_of_slots

    def _resize_to(self, new_number_of_slots):
        """
        Double the table size and rehash all existing entries.
        A new random hash function is generated for the new size,
        which also re-randomizes the universal hash parameters.
        """
        old_chains = self.chains
        self.number_of_slots = new_number_of_slots
        self.number_of_elements = 0
        self.chains = [[] for _ in range(self.number_of_slots)]
        self.hash_function = make_hash_function(self.number_of_slots)
        self.resize_count += 1

        # Reinsert every existing key-value pair into the new table
        for old_chain in old_chains:
            for key, value in old_chain:
                self.insert(key, value)

    def table_statistics(self):
        """Compute diagnostic statistics about the current table state."""
        all_chain_lengths = [len(chain) for chain in self.chains]
        nonempty_lengths = [length for length in all_chain_lengths if length > 0]

        return {
            "Slots  (m)": self.number_of_slots,
            "Elements  (n)": self.number_of_elements,
            "Load Factor  (α)": round(self.current_load_factor(), 4),
            "Non-empty Slots": len(nonempty_lengths),
            "Max Chain Length": max(all_chain_lengths) if all_chain_lengths else 0,
            "Avg Chain Length": (
                round(sum(nonempty_lengths) / len(nonempty_lengths), 4)
                if nonempty_lengths
                else 0
            ),
            "Resize Count": self.resize_count,
        }


# ============================================================
#  BENCHMARK RUNNER
#  Measures time and metric counts for a batch of operations.
#  Returns (elapsed_ms, comparisons, chain_probes, collisions).
# ============================================================


def run_operation_benchmark(hash_table, operation_function, keys_and_values):
    """
    Runs `operation_function` on each (key, value) pair in
    `keys_and_values`, measuring total time and metric counts.
    Used to benchmark insert, search, and delete in bulk.
    """
    metrics.reset()
    start_time = time.perf_counter()

    for key, value in keys_and_values:
        operation_function(key, value)

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    comparisons = metrics.comparisons
    chain_probes = metrics.chain_probes
    collisions = metrics.collisions

    return elapsed_ms, comparisons, chain_probes, collisions


# ============================================================
#  OUTPUT HELPERS
#  Consistent formatting and color for terminal output.
# ============================================================

COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"
COLOR_BOLD = "\033[1m"
COLOR_RESET = "\033[0m"

TOTAL_WIDTH = 100


def divider(char="─", width=TOTAL_WIDTH):
    return char * width


def section_header(title):
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}{title}{COLOR_RESET}")
    print(divider("═"))


# ============================================================
#  CORRECTNESS VALIDATOR
#  Verifies insert, search, delete, and update operations.
# ============================================================


def verify_correctness():
    section_header("CORRECTNESS VERIFICATION")

    table = HashTableWithChaining()
    all_passed = True

    def check(test_label, condition):
        nonlocal all_passed
        status = (
            COLOR_GREEN + "PASS" + COLOR_RESET
            if condition
            else COLOR_RED + "FAIL" + COLOR_RESET
        )
        if not condition:
            all_passed = False
        print(f"  {status}  {test_label}")

    print()

    # Basic insert and search
    table.insert(1, "one")
    table.insert(2, "two")
    table.insert(1000, "thousand")
    check("Insert and search integer key (1)", table.search(1) == "one")
    check("Insert and search integer key (2)", table.search(2) == "two")
    check("Insert and search integer key (1000)", table.search(1000) == "thousand")
    check("Search missing key returns None", table.search(999) is None)

    # String keys
    table.insert("engine_fault", "SPN 100 FMI 3")
    table.insert("brake_fault", "SPN 521 FMI 5")
    check(
        "Insert and search string key", table.search("engine_fault") == "SPN 100 FMI 3"
    )
    check(
        "Insert and search second string key",
        table.search("brake_fault") == "SPN 521 FMI 5",
    )

    # Update existing key
    table.insert(1, "ONE UPDATED")
    check("Update existing key in place", table.search(1) == "ONE UPDATED")

    # Delete
    deleted = table.delete(2)
    check("Delete returns True for existing key", deleted is True)
    check("Search deleted key returns None", table.search(2) is None)
    deleted_missing = table.delete(999)
    check("Delete returns False for missing key", deleted_missing is False)

    # Repeated insertions (stress collisions)
    collision_table = HashTableWithChaining(
        initial_slots=4
    )  # Tiny table to force collisions
    for i in range(20):
        collision_table.insert(i, i * 10)
    all_found = all(collision_table.search(i) == i * 10 for i in range(20))
    check("All 20 keys found after forced collisions (4-slot table)", all_found)

    # Empty table
    empty_table = HashTableWithChaining()
    check("Search on empty table returns None", empty_table.search("anything") is None)
    check(
        "Delete on empty table returns False", empty_table.delete("anything") is False
    )

    print()
    print(f"  {divider('─', 60)}")
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

    # ── Benchmark 1: Operation Performance vs Table Size ─────
    section_header("BENCHMARK 1  —  Operation Performance vs Number of Elements")

    print(f"  Measures insert, search, and delete time as n grows.")
    print(
        f"  Load factor α is kept bounded by dynamic resizing at α > {LOAD_FACTOR_THRESHOLD}.\n"
    )

    element_counts = [100, 500, 1000, 5000, 10000, 50000]

    col_n = 8
    col_op = 12
    col_cmp = 14
    col_prob = 14
    col_col = 12
    col_lf = 10

    print(
        f"  {'n':>{col_n}}  {'Operation':<{col_op}}  "
        f"{'Time(ms)':>{col_op}}  {'Comparisons':>{col_cmp}}  "
        f"{'ChainProbes':>{col_prob}}  {'Collisions':>{col_col}}  "
        f"{'Load Factor':>{col_lf}}"
    )
    print(
        f"  {divider('─', col_n)}  {divider('─', col_op)}  "
        f"{divider('─', col_op)}  {divider('─', col_cmp)}  "
        f"{divider('─', col_prob)}  {divider('─', col_col)}  "
        f"{divider('─', col_lf)}"
    )

    for n in element_counts:

        # Build fresh table and generate keys
        insert_table = HashTableWithChaining()
        all_keys = list(range(n))
        kv_pairs = [(k, k * 10) for k in all_keys]
        search_pairs = [(k, None) for k in all_keys]  # value unused in search
        delete_pairs = [(k, None) for k in all_keys[: n // 4]]  # delete 25% of keys

        # INSERT benchmark
        ins_ms, ins_cmp, ins_probe, ins_col = run_operation_benchmark(
            insert_table, lambda k, v: insert_table.insert(k, v), kv_pairs
        )
        load_factor_after_insert = insert_table.current_load_factor()

        print(
            f"  {n:>{col_n},}  {'Insert':<{col_op}}  "
            f"{ins_ms:>{col_op}.3f}  {ins_cmp:>{col_cmp},}  "
            f"{ins_probe:>{col_prob},}  {ins_col:>{col_col},}  "
            f"{load_factor_after_insert:>{col_lf}.4f}"
        )

        # SEARCH benchmark (on the same populated table)
        search_table = insert_table
        sch_ms, sch_cmp, sch_probe, sch_col = run_operation_benchmark(
            search_table, lambda k, v: search_table.search(k), search_pairs
        )

        print(
            f"  {n:>{col_n},}  {'Search':<{col_op}}  "
            f"{sch_ms:>{col_op}.3f}  {sch_cmp:>{col_cmp},}  "
            f"{sch_probe:>{col_prob},}  {sch_col:>{col_col},}  "
            f"{'—':>{col_lf}}"
        )

        # DELETE benchmark (delete 25% of keys)
        del_ms, del_cmp, del_probe, del_col = run_operation_benchmark(
            insert_table, lambda k, v: insert_table.delete(k), delete_pairs
        )
        load_factor_after_delete = insert_table.current_load_factor()

        print(
            f"  {n:>{col_n},}  {'Delete(25%)':<{col_op}}  "
            f"{del_ms:>{col_op}.3f}  {del_cmp:>{col_cmp},}  "
            f"{del_probe:>{col_prob},}  {del_col:>{col_col},}  "
            f"{load_factor_after_delete:>{col_lf}.4f}"
        )

        print(f"  {divider('·', 96)}")

    # ── Benchmark 2: Load Factor Effect ──────────────────────
    section_header("BENCHMARK 2  —  Load Factor Effect on Search Performance")

    print(f"  Fixed table size (no resizing). Measures how α = n/m")
    print(f"  affects average search comparisons as the table fills up.\n")

    FIXED_TABLE_SIZE = 1024

    print(
        f"  {'Elements (n)':>14}  {'Load Factor (α)':>16}  "
        f"{'Avg Search Comparisons':>24}  {'Avg Chain Probe Depth':>22}  {'Max Chain':>10}"
    )
    print(
        f"  {divider('─', 14)}  {divider('─', 16)}  "
        f"{divider('─', 24)}  {divider('─', 22)}  {divider('─', 10)}"
    )

    load_factor_table = HashTableWithChaining(initial_slots=FIXED_TABLE_SIZE)
    # Disable auto-resizing for this benchmark by patching threshold
    load_factor_table._original_threshold = LOAD_FACTOR_THRESHOLD

    step_sizes = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    inserted_so_far = 0

    for target_n in step_sizes:
        # Insert until we reach target_n elements
        while inserted_so_far < target_n:
            load_factor_table.chains  # just touch to ensure table exists
            key = inserted_so_far
            slot = load_factor_table.hash_function(key)
            load_factor_table.chains[slot].append((key, key * 10))
            load_factor_table.number_of_elements += 1
            inserted_so_far += 1

        # Measure search across all inserted keys
        metrics.reset()
        for key in range(inserted_so_far):
            load_factor_table.search(key)

        current_alpha = load_factor_table.current_load_factor()
        avg_comparisons = round(metrics.comparisons / inserted_so_far, 4)
        avg_probe_depth = round(metrics.chain_probes / inserted_so_far, 4)
        chain_lengths = [len(c) for c in load_factor_table.chains]
        max_chain = max(chain_lengths)

        print(
            f"  {inserted_so_far:>14,}  {current_alpha:>16.4f}  "
            f"{avg_comparisons:>24.4f}  {avg_probe_depth:>22.4f}  {max_chain:>10}"
        )

    # ── Table Statistics ─────────────────────────────────────
    section_header("FINAL TABLE STATISTICS  —  After Full Benchmark 1 (n = 50,000)")

    final_table = HashTableWithChaining()
    for i in range(50_000):
        final_table.insert(i, i * 10)

    stats = final_table.table_statistics()
    print()
    for stat_label, stat_value in stats.items():
        value_str = (
            f"{stat_value:,}" if isinstance(stat_value, int) else str(stat_value)
        )
        print(f"  {stat_label:<28}  {value_str}")

    # ── Complexity Reference ──────────────────────────────────
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Hash Table with Chaining (Simple Uniform Hashing):{COLOR_RESET}
    Insert      :  O(1)        expected — hash + chain prepend
    Search      :  O(1 + α)   expected — hash + traverse chain of avg length α
    Delete      :  O(1 + α)   expected — hash + traverse + remove
    Space       :  O(n + m)   — n elements + m slot pointers

  {COLOR_CYAN}Load Factor α = n / m:{COLOR_RESET}
    When m = Θ(n) → α = O(1) → all operations O(1) expected
    Dynamic resizing at α > {LOAD_FACTOR_THRESHOLD} keeps α bounded below threshold

  {COLOR_CYAN}Universal Hashing (Carter-Wegman Family):{COLOR_RESET}
    h(k) = ((a·k + b) mod p) mod m
    Collision probability for any two distinct keys ≤ 1/m""")
