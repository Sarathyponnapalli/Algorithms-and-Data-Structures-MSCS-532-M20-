# ============================================================
#  Assignment 7 — Part 2
#  Collision Resolution: Separate Chaining vs Open Addressing
#
#  Implements and compares:
#    1. Separate Chaining  — linked list per slot
#    2. Linear Probing     — open addressing: h(k,i) = (h(k)+i) % m
#    3. Double Hashing     — open addressing: h(k,i) = (h1(k)+i*h2(k)) % m
#
#  Author : Parthasarathi Ponnapalli
#  Course : MSCS-532 — Algorithms and Data Structures
# ============================================================

import random
import time

# ============================================================
#  OPERATION METRICS
#  Tracks comparisons and probes per operation so we measure
#  algorithmic work independently of wall-clock timing.
# ============================================================


class OperationMetrics:
    def __init__(self):
        self.comparisons = 0  # key equality checks
        self.probes = 0  # slots examined (open addressing only)

    def reset(self):
        self.comparisons = 0
        self.probes = 0


metrics = OperationMetrics()


# ============================================================
#  BASE HASH FUNCTION  (shared by all three implementations)
#  Universal Carter-Wegman hash: h(k) = ((a*k + b) mod p) mod m
#  Guarantees Pr[collision] <= 1/m for any two distinct keys.
# ============================================================


_PRIME = 10_000_019


def _make_hash_fn(table_size):
    """Returns a universal hash function for a given table size."""
    _a = random.randint(1, _PRIME - 1)
    _b = random.randint(0, _PRIME - 1)
    return lambda k: ((_a * int(k) + _b) % _PRIME) % table_size


def _make_secondary_hash_fn(table_size):
    """
    Secondary hash function for double hashing.
    Must never return 0 (would make h2 useless) and must be
    coprime to m to ensure all slots are reachable.
    h2(k) = 1 + (k mod (m - 1))  guarantees h2 in [1, m-1].
    """
    return lambda k: 1 + (int(k) % (table_size - 1))


# ============================================================
#  HASH TABLE 1 — SEPARATE CHAINING
#
#  Each slot holds a Python list acting as a linked chain.
#  Keys that hash to the same slot are stored in that list.
#
#  Operations and Expected Complexity:
#    insert(key, value)   : O(1) — hash + append to chain
#    search(key)          : O(1 + α) — hash + traverse chain of length α
#    delete(key)          : O(1 + α) — hash + traverse + remove
#
#  Where α = n/m is the load factor. When m = Θ(n), all O(1).
#  Handles α > 1 gracefully (chains just grow longer).
#  No tombstone problem — deletion is a clean chain removal.
#
#  Ref: CLRS 4th ed., Section 11.2
# ============================================================


class HashTableChaining:

    def __init__(self, table_size):
        self.table_size = table_size
        self.n_elements = 0
        self.chains = [[] for _ in range(table_size)]
        self._hash = _make_hash_fn(table_size)

    def insert(self, key, value):
        """Insert or update key-value pair. O(1 + chain length at slot)."""
        slot = self._hash(key)
        chain = self.chains[slot]
        for i, (k, _) in enumerate(chain):
            metrics.comparisons += 1
            if k == key:
                chain[i] = (key, value)  # update existing
                return
        chain.append((key, value))
        self.n_elements += 1

    def search(self, key):
        """Return value for key, or None if not found. O(1 + α)."""
        slot = self._hash(key)
        for k, v in self.chains[slot]:
            metrics.comparisons += 1
            if k == key:
                return v
        return None

    def delete(self, key):
        """Remove key from table. Returns True if found. O(1 + α)."""
        slot = self._hash(key)
        chain = self.chains[slot]
        for i, (k, _) in enumerate(chain):
            metrics.comparisons += 1
            if k == key:
                chain.pop(i)
                self.n_elements -= 1
                return True
        return False

    def load_factor(self):
        return self.n_elements / self.table_size

    def max_chain_length(self):
        return max(len(c) for c in self.chains) if self.chains else 0

    def avg_chain_length(self):
        nonempty = [len(c) for c in self.chains if c]
        return sum(nonempty) / len(nonempty) if nonempty else 0.0


# ============================================================
#  HASH TABLE 2 — LINEAR PROBING (Open Addressing)
#
#  All keys stored directly in the table array itself.
#  Probe sequence: h(k, i) = (h(k) + i) mod m  (i = 0, 1, 2, ...)
#
#  Problem — Primary Clustering:
#    Long runs of consecutive occupied slots form and grow.
#    A key landing in a cluster extends the cluster, making future
#    inserts into that region even slower. Performance degrades
#    sharply as α approaches 1 (unusable above α ≈ 0.8).
#
#  Expected probes (unsuccessful search): (1 + 1/(1-α)^2) / 2
#  Expected probes (successful search)  : (1 + 1/(1-α)) / 2
#
#  Deletion requires TOMBSTONE markers (DELETED sentinel) to
#  preserve probe chain integrity. Tombstones accumulate over
#  time and must be cleaned up periodically via rehashing.
#
#  Ref: CLRS 4th ed., Section 11.4
# ============================================================


_EMPTY = object()  # sentinel: slot has never been used
_DELETED = object()  # sentinel: slot held a key that was deleted (tombstone)


class HashTableLinearProbing:

    def __init__(self, table_size):
        self.table_size = table_size
        self.n_elements = 0
        self.n_deleted = 0  # count tombstones for analysis
        self.slots = [_EMPTY] * table_size
        self.values = [None] * table_size
        self._hash = _make_hash_fn(table_size)

    def insert(self, key, value):
        """
        Insert key-value pair using linear probing.
        Raises RuntimeError if table is completely full.
        """
        if self.n_elements + self.n_deleted >= self.table_size:
            raise RuntimeError("Table is full — cannot insert.")

        slot = self._hash(key)
        first_tomb = None  # track first tombstone encountered (reuse for insert)

        for i in range(self.table_size):
            probe = (slot + i) % self.table_size
            metrics.probes += 1

            if self.slots[probe] is _EMPTY:
                # Empty slot — insert here (or at earlier tombstone)
                target = first_tomb if first_tomb is not None else probe
                self.slots[target] = key
                self.values[target] = value
                self.n_elements += 1
                if first_tomb is not None:
                    self.n_deleted -= 1  # reused a tombstone
                return

            elif self.slots[probe] is _DELETED:
                if first_tomb is None:
                    first_tomb = probe  # remember first tombstone

            else:
                metrics.comparisons += 1
                if self.slots[probe] == key:
                    self.values[probe] = value  # update existing key
                    return

        raise RuntimeError("Table full — no empty slot found.")

    def search(self, key):
        """Search for key using linear probing. Returns value or None."""
        slot = self._hash(key)

        for i in range(self.table_size):
            probe = (slot + i) % self.table_size
            metrics.probes += 1

            if self.slots[probe] is _EMPTY:
                return None  # hit empty slot — key definitely not here

            elif self.slots[probe] is not _DELETED:
                metrics.comparisons += 1
                if self.slots[probe] == key:
                    return self.values[probe]
            # If DELETED: skip tombstone and continue probing

        return None

    def delete(self, key):
        """
        Delete key by replacing its slot with a TOMBSTONE.
        The tombstone preserves the probe chain for keys beyond it.
        Returns True if deleted, False if not found.
        """
        slot = self._hash(key)

        for i in range(self.table_size):
            probe = (slot + i) % self.table_size
            metrics.probes += 1

            if self.slots[probe] is _EMPTY:
                return False

            elif self.slots[probe] is not _DELETED:
                metrics.comparisons += 1
                if self.slots[probe] == key:
                    self.slots[probe] = _DELETED  # plant tombstone
                    self.values[probe] = None
                    self.n_elements -= 1
                    self.n_deleted += 1
                    return True

        return False

    def load_factor(self):
        return self.n_elements / self.table_size

    def tombstone_ratio(self):
        """Fraction of table slots occupied by tombstones."""
        return self.n_deleted / self.table_size


# ============================================================
#  HASH TABLE 3 — DOUBLE HASHING (Open Addressing)
#
#  Probe sequence: h(k,i) = (h1(k) + i * h2(k)) mod m
#
#  The secondary hash function h2(k) makes the step size key-
#  dependent. This eliminates primary clustering because keys
#  with the same h1 value use different step sizes and spread
#  across the table independently.
#
#  Requirement: h2(k) must never be 0 AND must be coprime to m
#  to ensure the full probe sequence visits all m slots.
#  Standard choice: h2(k) = 1 + (k mod (m - 1))
#  When m is prime, any non-zero h2 is automatically coprime to m.
#
#  Expected probes (unsuccessful): 1/(1-α)
#  Expected probes (successful)  : (1/α) * ln(1/(1-α))
#
#  These are significantly better than linear probing at high α.
#
#  Ref: CLRS 4th ed., Section 11.4.3
# ============================================================


class HashTableDoubleHashing:

    def __init__(self, table_size):
        self.table_size = table_size
        self.n_elements = 0
        self.n_deleted = 0
        self.slots = [_EMPTY] * table_size
        self.values = [None] * table_size
        self._hash1 = _make_hash_fn(table_size)
        self._hash2 = _make_secondary_hash_fn(table_size)

    def _probe_index(self, key, i):
        """Compute the i-th probe slot for the given key."""
        return (self._hash1(key) + i * self._hash2(key)) % self.table_size

    def insert(self, key, value):
        """Insert using double hashing probe sequence."""
        if self.n_elements + self.n_deleted >= self.table_size:
            raise RuntimeError("Table is full — cannot insert.")

        first_tomb = None

        for i in range(self.table_size):
            probe = self._probe_index(key, i)
            metrics.probes += 1

            if self.slots[probe] is _EMPTY:
                target = first_tomb if first_tomb is not None else probe
                self.slots[target] = key
                self.values[target] = value
                self.n_elements += 1
                if first_tomb is not None:
                    self.n_deleted -= 1
                return

            elif self.slots[probe] is _DELETED:
                if first_tomb is None:
                    first_tomb = probe

            else:
                metrics.comparisons += 1
                if self.slots[probe] == key:
                    self.values[probe] = value
                    return

        raise RuntimeError("Table full — no empty slot found.")

    def search(self, key):
        """Search using double hashing probe sequence."""
        for i in range(self.table_size):
            probe = self._probe_index(key, i)
            metrics.probes += 1

            if self.slots[probe] is _EMPTY:
                return None

            elif self.slots[probe] is not _DELETED:
                metrics.comparisons += 1
                if self.slots[probe] == key:
                    return self.values[probe]

        return None

    def delete(self, key):
        """Delete using tombstone, same as linear probing."""
        for i in range(self.table_size):
            probe = self._probe_index(key, i)
            metrics.probes += 1

            if self.slots[probe] is _EMPTY:
                return False

            elif self.slots[probe] is not _DELETED:
                metrics.comparisons += 1
                if self.slots[probe] == key:
                    self.slots[probe] = _DELETED
                    self.values[probe] = None
                    self.n_elements -= 1
                    self.n_deleted += 1
                    return True

        return False

    def load_factor(self):
        return self.n_elements / self.table_size

    def tombstone_ratio(self):
        return self.n_deleted / self.table_size


# ============================================================
#  OUTPUT HELPERS
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
# ============================================================


def verify_correctness():
    section_header("CORRECTNESS VERIFICATION")
    all_passed = True

    def check(label, condition, note=""):
        nonlocal all_passed
        ok = bool(condition)
        status = (
            COLOR_GREEN + "PASS" + COLOR_RESET
            if ok
            else COLOR_RED + "FAIL" + COLOR_RESET
        )
        if not ok:
            all_passed = False
        suffix = f"  ({note})" if note else ""
        print(f"  {status}  {label}{suffix}")

    for table_class, label in [
        (HashTableChaining, "Separate Chaining"),
        (HashTableLinearProbing, "Linear Probing"),
        (HashTableDoubleHashing, "Double Hashing"),
    ]:
        print(
            f"\n  {COLOR_CYAN}── {label} ──────────────────────────────────{COLOR_RESET}"
        )
        ht = table_class(101)  # prime table size

        # Basic insert and search
        ht.insert(42, "forty-two")
        ht.insert(7, "seven")
        ht.insert(99, "ninety-nine")
        check(f"{label}: insert and search (42)", ht.search(42) == "forty-two")
        check(f"{label}: insert and search (7)", ht.search(7) == "seven")
        check(f"{label}: search missing key", ht.search(55) is None)

        # Update existing key
        ht.insert(42, "UPDATED")
        check(f"{label}: update existing key", ht.search(42) == "UPDATED")

        # Delete
        result = ht.delete(7)
        check(f"{label}: delete returns True", result is True)
        check(f"{label}: deleted key not found", ht.search(7) is None)
        check(f"{label}: delete missing returns False", ht.delete(77) is False)

        # Verify other keys unaffected after delete
        check(f"{label}: other keys intact after delete", ht.search(42) == "UPDATED")

        # Many keys
        ht2 = table_class(211)
        keys = random.sample(range(10000), 100)
        for k in keys:
            ht2.insert(k, k * 10)
        all_found = all(ht2.search(k) == k * 10 for k in keys)
        check(f"{label}: all 100 keys found after bulk insert", all_found)

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
#  LOAD FACTOR BENCHMARK
#  Shows how each strategy degrades as the table fills up.
# ============================================================


def run_load_factor_benchmark():
    section_header("LOAD FACTOR BENCHMARK  —  Performance vs Fill Level")
    print(f"  Table size m = 1,000.  Benchmark: insert n keys, then search all n keys.")
    print(f"  Probes and comparisons tracked per operation (avg per key shown).\n")

    TABLE_SIZE = 1000
    target_alphas = [0.25, 0.50, 0.70, 0.85, 0.95]

    implementations = [
        ("Chaining", HashTableChaining),
        ("Linear Probing", HashTableLinearProbing),
        ("Double Hashing", HashTableDoubleHashing),
    ]

    col_impl = 16
    col_alf = 8
    col_n = 7
    col_t = 12
    col_cmp = 13
    col_prb = 12
    col_ex = 14

    alpha_label = "\u03b1"
    print(
        f"  {'Implementation':<{col_impl}}  {alpha_label:>{col_alf}}  {'n':>{col_n}}  "
        f"{'Ins Time(ms)':>{col_t}}  {'Avg Compares':>{col_cmp}}  {'Avg Probes':>{col_prb}}  "
        f"{'Srch Time(ms)':>{col_ex}}"
    )
    print(
        f"  {divider('─', col_impl)}  {divider('─', col_alf)}  {divider('─', col_n)}  "
        f"{divider('─', col_t)}  {divider('─', col_cmp)}  {divider('─', col_prb)}  "
        f"{divider('─', col_ex)}"
    )

    for impl_label, TableClass in implementations:
        for alpha in target_alphas:
            n_keys = int(TABLE_SIZE * alpha)
            keys = random.sample(range(TABLE_SIZE * 10), n_keys)

            table = TableClass(TABLE_SIZE)

            # INSERT benchmark
            metrics.reset()
            t_start = time.perf_counter()
            inserted = 0
            for k in keys:
                try:
                    table.insert(k, k)
                    inserted += 1
                except RuntimeError:
                    break
            insert_ms = (time.perf_counter() - t_start) * 1000
            ins_cmp = metrics.comparisons / max(inserted, 1)
            ins_prb = metrics.probes / max(inserted, 1)

            # SEARCH benchmark (search all inserted keys)
            metrics.reset()
            t_start = time.perf_counter()
            for k in keys[:inserted]:
                table.search(k)
            search_ms = (time.perf_counter() - t_start) * 1000

            # Highlight rows where probes spike
            prb_display = f"{ins_prb:>{col_prb}.2f}"
            if ins_prb > 5:
                prb_display = COLOR_RED + prb_display + COLOR_RESET
            elif ins_prb > 2:
                prb_display = COLOR_YELLOW + prb_display + COLOR_RESET

            print(
                f"  {impl_label:<{col_impl}}  {alpha:>{col_alf}.2f}  {n_keys:>{col_n}}  "
                f"{insert_ms:>{col_t}.3f}  {ins_cmp:>{col_cmp}.2f}  {prb_display}  "
                f"{search_ms:>{col_ex}.3f}"
            )

        dot_char = "\u00b7"
        print(
            f"  {divider(dot_char, col_impl + col_alf + col_n + col_t + col_cmp + col_prb + col_ex + 14)}"
        )


# ============================================================
#  TOMBSTONE ACCUMULATION DEMONSTRATION
#  Shows how repeated insert-delete cycles pollute open addressing.
# ============================================================


def demonstrate_tombstone_accumulation():
    section_header("TOMBSTONE ACCUMULATION  —  Effect of Repeated Deletions")
    print(f"  Linear probing table (m=500). Insert 400 keys, then delete-and-reinsert")
    print(
        f"  in cycles to accumulate tombstones. Tracks probe count growth over time.\n"
    )

    TABLE_SIZE = 500
    n_initial = 400  # load factor 0.8
    n_cycle = 100  # delete+reinsert this many keys per round

    table = HashTableLinearProbing(TABLE_SIZE)
    keys = list(range(n_initial))
    for k in keys:
        table.insert(k, k)

    print(
        f"  {'Cycle':<8} {'Live Keys':>10} {'Tombstones':>12} {'Tomb Ratio':>12} {'Avg Probes/Search':>20}"
    )
    print(
        f"  {divider('─', 8)} {divider('─', 10)} {divider('─', 12)} {divider('─', 12)} {divider('─', 20)}"
    )

    next_key = n_initial

    for cycle in range(6):
        # Measure current search cost
        metrics.reset()
        for k in keys[:50]:  # sample search cost
            table.search(k)
        avg_probes = metrics.probes / 50

        color = (
            COLOR_GREEN
            if avg_probes < 3
            else COLOR_YELLOW if avg_probes < 6 else COLOR_RED
        )

        print(
            f"  {cycle:<8} {table.n_elements:>10,} {table.n_deleted:>12,} "
            f"{table.tombstone_ratio():>12.3f} "
            f"{color}{avg_probes:>20.2f}{COLOR_RESET}"
        )

        # Delete n_cycle keys and reinsert new ones
        delete_targets = keys[:n_cycle]
        keys = keys[n_cycle:] + list(range(next_key, next_key + n_cycle))
        next_key += n_cycle

        for k in delete_targets:
            table.delete(k)
        for k in range(next_key - n_cycle, next_key):
            try:
                table.insert(k, k)
            except RuntimeError:
                break

    print()


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":
    verify_correctness()
    run_load_factor_benchmark()
    demonstrate_tombstone_accumulation()

    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Separate Chaining:{COLOR_RESET}
    Insert / Search / Delete  :  O(1 + \u03b1) expected
    Memory                    :  O(m + n) — chains use heap memory per node
    Load factor handling      :  Graceful at any \u03b1; works for \u03b1 > 1
    Deletion                  :  Clean — remove node from chain, no sentinel needed

  {COLOR_CYAN}Linear Probing (Open Addressing):{COLOR_RESET}
    Insert / Search           :  O(1/(1-\u03b1)^2) probes — degrades sharply near \u03b1=1
    Memory                    :  O(m) — all keys in contiguous array, no pointer overhead
    Load factor handling      :  Must keep \u03b1 < 0.7-0.8 to avoid primary clustering
    Deletion                  :  Requires tombstone; tombstones accumulate and need rehash

  {COLOR_CYAN}Double Hashing (Open Addressing):{COLOR_RESET}
    Insert / Search           :  O(1/(1-\u03b1)) probes expected — better than linear probing
    Memory                    :  O(m) — same as linear probing
    Load factor handling      :  Better than linear probing; still needs \u03b1 < 0.85
    Deletion                  :  Requires tombstone (same as linear probing)
    Key requirement           :  h2(k) must never be 0 and must be coprime to m
    """)
