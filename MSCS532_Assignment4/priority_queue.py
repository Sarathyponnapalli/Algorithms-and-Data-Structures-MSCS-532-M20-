# ============================================================
#  Assignment 4 — Part 2
#  Priority Queue using a Max-Heap
#
#  Author : Parthasarathi Ponnapalli
#  Course : MSCS-532 — Algorithms and Data Structures
# ============================================================

import random
import time


# ============================================================
#  METRICS TRACKER
#  Counts comparisons and swaps per operation so we can
#  measure actual algorithmic work, not just wall-clock time.
# ============================================================


class HeapMetrics:
    def __init__(self):
        self.comparisons = 0
        self.swaps       = 0

    def reset(self):
        self.comparisons = 0
        self.swaps       = 0


metrics = HeapMetrics()


# ============================================================
#  TASK CLASS
#
#  Represents a schedulable unit of work in the priority queue.
#
#  Design choice: priority is the primary ordering key.
#    Higher priority value → processed first (max-heap).
#    Ties broken by arrival_time (earlier arrival wins),
#    then by task_id for determinism.
#
#  Fields:
#    task_id      — unique identifier (int or str)
#    priority     — scheduling priority (higher = more urgent)
#    arrival_time — when the task entered the system (seconds)
#    deadline     — latest acceptable completion time (seconds)
#    description  — human-readable label for the task
# ============================================================


class Task:
    def __init__(self, task_id, priority, arrival_time=0.0,
                 deadline=float("inf"), description=""):
        self.task_id      = task_id
        self.priority     = priority
        self.arrival_time = arrival_time
        self.deadline     = deadline
        self.description  = description

    def __repr__(self):
        return (
            f"Task(id={self.task_id}, priority={self.priority}, "
            f"arrival={self.arrival_time:.1f}s, deadline={self.deadline}s)"
        )

    def __gt__(self, other):
        """Higher priority wins. Ties resolved by earlier arrival, then smaller ID."""
        if self.priority != other.priority:
            return self.priority > other.priority
        if self.arrival_time != other.arrival_time:
            return self.arrival_time < other.arrival_time
        return self.task_id < other.task_id

    def __lt__(self, other):
        return other.__gt__(self)

    def __eq__(self, other):
        return self.task_id == other.task_id

    def __ge__(self, other):
        return self == other or self.__gt__(other)

    def __le__(self, other):
        return self == other or self.__lt__(other)


# ============================================================
#  PRIORITY QUEUE  (Max-Heap based)
#
#  Design Choices:
#  ───────────────
#  1. Array (Python list) representation:
#       - O(1) access to any node via index arithmetic.
#       - Parent of node i   : (i - 1) // 2
#       - Left child of i    : 2i + 1
#       - Right child of i   : 2i + 2
#       - No pointer overhead — cache-friendly layout.
#       - Simpler to implement than a tree of node objects.
#
#  2. Max-heap (highest priority extracted first):
#       - Models a real-world scheduler: most urgent task
#         runs next, regardless of arrival order.
#       - Root always holds the highest-priority task → O(1) peek.
#
#  Operations and Expected Time Complexity (CLRS Ch. 6):
#    insert(task)                 : O(log n)  — sift up from leaf
#    extract_max()                : O(log n)  — remove root, sift down
#    increase_key(index, new_p)   : O(log n)  — priority rose → sift up
#    decrease_key(index, new_p)   : O(log n)  — priority fell → sift down
#    peek_max()                   : O(1)      — read root
#    is_empty()                   : O(1)      — check length
#
#  Ref: CLRS 4th ed., Section 6.5 — Priority Queues
# ============================================================


class MaxHeapPriorityQueue:

    def __init__(self):
        self._heap = []   # Internal array — index 0 is the root (max)

    # ── Index Helpers ─────────────────────────────────────────

    def _parent_index(self, child_index):
        return (child_index - 1) // 2

    def _left_child_index(self, parent_index):
        return 2 * parent_index + 1

    def _right_child_index(self, parent_index):
        return 2 * parent_index + 2

    def _swap(self, index_a, index_b):
        self._heap[index_a], self._heap[index_b] = (
            self._heap[index_b], self._heap[index_a]
        )
        metrics.swaps += 1

    # ── Internal Heap Operations ──────────────────────────────

    def _sift_up(self, child_index):
        """
        Moves a node upward until the heap property is restored.
        Used after INSERT — the new element starts at the bottom
        and bubbles up as long as it is greater than its parent.

        Time complexity: O(log n) — tree height is floor(log n).
        """
        while child_index > 0:
            parent = self._parent_index(child_index)
            metrics.comparisons += 1
            if self._heap[child_index] > self._heap[parent]:
                self._swap(child_index, parent)
                child_index = parent
            else:
                break   # Heap property satisfied — stop

    def _sift_down(self, parent_index):
        """
        Moves a node downward until the heap property is restored.
        Used after EXTRACT_MAX — the replacement element starts at
        the root and sinks to its correct position.

        Time complexity: O(log n) — at most height swaps.
        """
        heap_size = len(self._heap)

        while True:
            largest = parent_index
            left    = self._left_child_index(parent_index)
            right   = self._right_child_index(parent_index)

            if left < heap_size:
                metrics.comparisons += 1
                if self._heap[left] > self._heap[largest]:
                    largest = left

            if right < heap_size:
                metrics.comparisons += 1
                if self._heap[right] > self._heap[largest]:
                    largest = right

            if largest != parent_index:
                self._swap(parent_index, largest)
                parent_index = largest
            else:
                break   # Heap property satisfied — stop

    # ── Core Public Operations ────────────────────────────────

    def insert(self, task):
        """
        Adds a new Task to the priority queue.

        Steps:
          1. Append the task to the end of the heap array. O(1)
          2. Sift it upward to restore the heap property.  O(log n)

        Time complexity: O(log n)
        """
        self._heap.append(task)
        self._sift_up(len(self._heap) - 1)

    def extract_max(self):
        """
        Removes and returns the highest-priority Task.

        Steps:
          1. Record the root (maximum) to return.              O(1)
          2. Move the last element to the root position.       O(1)
          3. Remove the last slot.                             O(1)
          4. Sift the new root downward to restore heap.       O(log n)

        Time complexity: O(log n)

        Raises ValueError if the queue is empty.
        """
        if self.is_empty():
            raise ValueError("Cannot extract from an empty priority queue.")

        max_task              = self._heap[0]
        last_task             = self._heap.pop()   # Remove last element

        if self._heap:
            self._heap[0] = last_task              # Place it at root
            self._sift_down(0)                     # Restore heap property

        return max_task

    def increase_key(self, task_index, new_priority):
        """
        Increases the priority of the task at task_index.

        A higher priority means the task moves closer to the root.
        After updating, sift the task upward.

        Time complexity: O(log n)

        Raises ValueError if new_priority is less than current priority.
        """
        if new_priority < self._heap[task_index].priority:
            raise ValueError(
                "increase_key: new priority must be >= current priority. "
                "Use decrease_key to lower a priority."
            )
        self._heap[task_index].priority = new_priority
        self._sift_up(task_index)

    def decrease_key(self, task_index, new_priority):
        """
        Decreases the priority of the task at task_index.

        A lower priority means the task moves away from the root.
        After updating, sift the task downward.

        Time complexity: O(log n)

        Raises ValueError if new_priority exceeds current priority.
        """
        if new_priority > self._heap[task_index].priority:
            raise ValueError(
                "decrease_key: new priority must be <= current priority. "
                "Use increase_key to raise a priority."
            )
        self._heap[task_index].priority = new_priority
        self._sift_down(task_index)

    def peek_max(self):
        """
        Returns the highest-priority Task without removing it.
        Time complexity: O(1)
        """
        if self.is_empty():
            raise ValueError("Cannot peek an empty priority queue.")
        return self._heap[0]

    def is_empty(self):
        """
        Returns True if the priority queue has no tasks.
        Time complexity: O(1)
        """
        return len(self._heap) == 0

    def size(self):
        """Returns the number of tasks currently in the queue."""
        return len(self._heap)

    def find_task_index(self, task_id):
        """
        Finds the heap index of a task by its task_id.
        Time complexity: O(n) — linear scan (no direct index map).
        """
        for index, task in enumerate(self._heap):
            if task.task_id == task_id:
                return index
        return -1   # Not found


# ============================================================
#  OUTPUT HELPERS
# ============================================================

COLOR_GREEN  = "\033[92m"
COLOR_RED    = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN   = "\033[96m"
COLOR_BOLD   = "\033[1m"
COLOR_RESET  = "\033[0m"

TOTAL_WIDTH  = 90


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

    def check(label, condition, extra=""):
        nonlocal all_passed
        ok     = bool(condition)
        status = COLOR_GREEN + "PASS" + COLOR_RESET if ok else COLOR_RED + "FAIL" + COLOR_RESET
        if not ok:
            all_passed = False
        suffix = f"  ({extra})" if extra else ""
        print(f"  {status}  {label}{suffix}")

    print()

    # ── Basic insert and extract ──────────────────────────────
    pq = MaxHeapPriorityQueue()
    check("is_empty() on fresh queue", pq.is_empty())

    pq.insert(Task("T1", priority=5))
    pq.insert(Task("T2", priority=9))
    pq.insert(Task("T3", priority=2))
    pq.insert(Task("T4", priority=7))

    check("peek_max() returns highest priority task",
          pq.peek_max().task_id == "T2", "priority 9")
    check("size() after 4 inserts", pq.size() == 4)

    extracted = pq.extract_max()
    check("extract_max() returns task with priority 9",
          extracted.priority == 9, f"got {extracted.priority}")
    check("extract_max() leaves priority 7 at root",
          pq.peek_max().priority == 7)
    check("size() after extract", pq.size() == 3)

    # ── Drain order must be descending ───────────────────────
    extracted_priorities = [extracted.priority]
    while not pq.is_empty():
        extracted_priorities.append(pq.extract_max().priority)
    check("extract_max() order is strictly decreasing",
          extracted_priorities == sorted(extracted_priorities, reverse=True),
          str(extracted_priorities))

    # ── increase_key ─────────────────────────────────────────
    pq2 = MaxHeapPriorityQueue()
    pq2.insert(Task("A", priority=3))
    pq2.insert(Task("B", priority=8))
    pq2.insert(Task("C", priority=1))
    idx_a = pq2.find_task_index("A")
    pq2.increase_key(idx_a, 10)
    check("increase_key promotes task to root",
          pq2.peek_max().task_id == "A", "priority raised from 3 → 10")

    # ── decrease_key ─────────────────────────────────────────
    idx_a = pq2.find_task_index("A")
    pq2.decrease_key(idx_a, 0)
    check("decrease_key demotes task from root",
          pq2.peek_max().task_id == "B", "priority lowered from 10 → 0")

    # ── Error cases ───────────────────────────────────────────
    empty_pq = MaxHeapPriorityQueue()
    try:
        empty_pq.extract_max()
        check("extract_max() on empty raises ValueError", False)
    except ValueError:
        check("extract_max() on empty raises ValueError", True)

    try:
        idx = pq2.find_task_index("B")
        pq2.increase_key(idx, 0)   # 0 < 8, should raise
        check("increase_key with lower value raises ValueError", False)
    except ValueError:
        check("increase_key with lower value raises ValueError", True)

    # ── Tie-breaking by arrival_time ──────────────────────────
    pq3 = MaxHeapPriorityQueue()
    pq3.insert(Task("X", priority=5, arrival_time=3.0))
    pq3.insert(Task("Y", priority=5, arrival_time=1.0))
    pq3.insert(Task("Z", priority=5, arrival_time=2.0))
    first_out = pq3.extract_max()
    check("Tie-breaking: earlier arrival_time wins",
          first_out.task_id == "Y", f"arrival_time=1.0, got {first_out.task_id}")

    print()
    print(f"  {divider('─', 60)}")
    overall = (COLOR_GREEN + "  ✔  ALL TESTS PASSED" + COLOR_RESET
               if all_passed else COLOR_RED + "  ✘  SOME TESTS FAILED" + COLOR_RESET)
    print(f"{overall}\n")
    return all_passed


# ============================================================
#  SCHEDULER SIMULATION
#  Demonstrates the priority queue in a real scheduling context.
#  Tasks arrive over time, each with a priority and deadline.
#  The scheduler always processes the highest-priority task next.
# ============================================================


def run_scheduler_simulation():
    section_header("SCHEDULER SIMULATION  —  Max-Priority Task Processing")

    # Define a set of tasks with varying priorities and deadlines
    incoming_tasks = [
        Task("T01", priority=3,  arrival_time=0.0,  deadline=10.0, description="Background log rotation"),
        Task("T02", priority=9,  arrival_time=0.5,  deadline=2.0,  description="CRITICAL: Engine fault alert"),
        Task("T03", priority=6,  arrival_time=1.0,  deadline=5.0,  description="Sensor data flush"),
        Task("T04", priority=1,  arrival_time=1.5,  deadline=20.0, description="Telemetry archive"),
        Task("T05", priority=9,  arrival_time=2.0,  deadline=3.0,  description="CRITICAL: Brake warning"),
        Task("T06", priority=7,  arrival_time=2.5,  deadline=6.0,  description="Navigation update"),
        Task("T07", priority=4,  arrival_time=3.0,  deadline=12.0, description="Config sync"),
        Task("T08", priority=9,  arrival_time=3.5,  deadline=4.5,  description="CRITICAL: Speed limiter"),
        Task("T09", priority=2,  arrival_time=4.0,  deadline=30.0, description="Usage statistics upload"),
        Task("T10", priority=8,  arrival_time=4.5,  deadline=7.0,  description="Real-time display refresh"),
    ]

    scheduler   = MaxHeapPriorityQueue()
    current_time= 0.0
    processed   = []

    print(f"\n  Inserting {len(incoming_tasks)} tasks into priority queue...\n")
    print(f"  {'Task':<6} {'Priority':>8}  {'Arrival':>8}  {'Deadline':>9}  Description")
    print(f"  {divider('─', 6)}  {divider('─', 8)}  {divider('─', 8)}  {divider('─', 9)}  {divider('─', 30)}")

    for task in incoming_tasks:
        scheduler.insert(task)
        deadline_str = f"{task.deadline:.1f}s" if task.deadline != float('inf') else "none"
        print(
            f"  {task.task_id:<6}  {task.priority:>8}  "
            f"{task.arrival_time:>7.1f}s  {deadline_str:>9}  {task.description}"
        )

    print(f"\n  Queue size: {scheduler.size()}  |  Processing in priority order...\n")
    print(f"  {'Order':<6} {'Task':<6} {'Priority':>8}  {'Processed At':>13}  {'Met Deadline?':>14}  Description")
    print(f"  {divider('─', 6)} {divider('─', 6)}  {divider('─', 8)}  {divider('─', 13)}  {divider('─', 14)}  {divider('─', 30)}")

    process_order = 1
    processing_time_per_task = 0.5   # Each task takes 0.5s to process

    while not scheduler.is_empty():
        task          = scheduler.extract_max()
        current_time += processing_time_per_task
        met_deadline  = current_time <= task.deadline
        deadline_mark = (COLOR_GREEN + "      YES" + COLOR_RESET
                         if met_deadline else COLOR_RED + "       NO" + COLOR_RESET)
        print(
            f"  {process_order:<6} {task.task_id:<6}  {task.priority:>8}  "
            f"{current_time:>12.1f}s  {deadline_mark}  {task.description}"
        )
        processed.append((task, current_time, met_deadline))
        process_order += 1

    met_count    = sum(1 for _, _, met in processed if met)
    missed_count = len(processed) - met_count

    print(f"\n  {divider('─', 70)}")
    print(f"  Tasks processed : {len(processed)}")
    print(f"  Deadlines met   : {COLOR_GREEN}{met_count}{COLOR_RESET}")
    print(f"  Deadlines missed: {COLOR_RED}{missed_count}{COLOR_RESET}")
    print()


# ============================================================
#  BENCHMARK — Operation Performance vs Queue Size
# ============================================================


def run_operation_benchmark():
    section_header("BENCHMARK  —  Operation Performance vs Queue Size")
    print(f"  Measures insert and extract_max time as n grows.\n")

    col_n   = 8
    col_op  = 14
    col_t   = 12
    col_cmp = 14
    col_swp = 12

    print(
        f"  {'n':>{col_n}}  {'Operation':<{col_op}}  "
        f"{'Time(ms)':>{col_t}}  {'Comparisons':>{col_cmp}}  {'Swaps':>{col_swp}}"
    )
    print(
        f"  {divider('─', col_n)}  {divider('─', col_op)}  "
        f"{divider('─', col_t)}  {divider('─', col_cmp)}  {divider('─', col_swp)}"
    )

    for n in [100, 500, 1000, 5000, 10000]:

        tasks = [Task(i, priority=random.randint(1, 1000)) for i in range(n)]

        # INSERT benchmark
        pq = MaxHeapPriorityQueue()
        metrics.reset()
        start = time.perf_counter()
        for task in tasks:
            pq.insert(task)
        insert_ms  = (time.perf_counter() - start) * 1000
        insert_cmp = metrics.comparisons
        insert_swp = metrics.swaps

        print(
            f"  {n:>{col_n},}  {'insert (x n)':<{col_op}}  "
            f"{insert_ms:>{col_t}.3f}  {insert_cmp:>{col_cmp},}  {insert_swp:>{col_swp},}"
        )

        # EXTRACT_MAX benchmark
        metrics.reset()
        start = time.perf_counter()
        while not pq.is_empty():
            pq.extract_max()
        extract_ms  = (time.perf_counter() - start) * 1000
        extract_cmp = metrics.comparisons
        extract_swp = metrics.swaps

        print(
            f"  {n:>{col_n},}  {'extract_max (x n)':<{col_op}}  "
            f"{extract_ms:>{col_t}.3f}  {extract_cmp:>{col_cmp},}  {extract_swp:>{col_swp},}"
        )

        print(f"  {divider('·', col_n + col_op + col_t + col_cmp + col_swp + 10)}")

    # ── Complexity Reference ──────────────────────────────────
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}Max-Heap Priority Queue (array-based):{COLOR_RESET}
    insert(task)               : O(log n)  — sift up from leaf to root
    extract_max()              : O(log n)  — sift down from root to leaf
    increase_key(index, p)     : O(log n)  — sift up after priority raised
    decrease_key(index, p)     : O(log n)  — sift down after priority lowered
    peek_max()                 : O(1)      — read root element
    is_empty()                 : O(1)      — check array length
    find_task_index(id)        : O(n)      — linear scan (no index map)

  Space complexity             : O(n)      — n tasks stored in array

  Ref: Cormen et al. (2022), Introduction to Algorithms, 4th ed., Section 6.5
    """)


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":
    verify_correctness()
    run_scheduler_simulation()
    run_operation_benchmark()