# ============================================================
#  Assignment 6 — Part 2
#  Elementary Data Structures
#
#  Implements: DynamicArray, Matrix, ArrayStack, ArrayQueue,
#              SinglyLinkedList, RootedTree
#
#  Author : Parthasarathi Ponnapalli
#  Course : MSCS-532 — Algorithms and Data Structures
# ============================================================

import time
from collections import deque   # used only for RootedTree BFS — not as Queue implementation


# ============================================================
#  DYNAMIC ARRAY
#
#  Python lists are already dynamic arrays, but we build our
#  own to demonstrate the underlying operations explicitly.
#
#  Key insight: access is O(1) because arrays are contiguous
#  in memory — index i is at address (base + i * element_size).
#  Insertion/deletion at an arbitrary position is O(n) because
#  all subsequent elements must shift.
#
#  Operations:
#    access(index)        : O(1)
#    append(value)        : O(1) amortized  (occasional O(n) resize)
#    insert(index, value) : O(n) — elements after index must shift right
#    delete(index)        : O(n) — elements after index must shift left
#    search(value)        : O(n) — unsorted linear scan
# ============================================================


class DynamicArray:

    INITIAL_CAPACITY = 4

    def __init__(self):
        self._capacity = self.INITIAL_CAPACITY
        self._size     = 0
        self._data     = [None] * self._capacity

    # ── Core Operations ───────────────────────────────────────

    def access(self, index):
        """Return element at index. O(1)."""
        self._check_index(index)
        return self._data[index]

    def append(self, value):
        """Add value to the end. O(1) amortized."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def insert(self, index, value):
        """Insert value at index, shifting elements right. O(n)."""
        if index < 0 or index > self._size:
            raise IndexError(f"Insert index {index} out of range.")
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        # Shift elements right to make room
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index):
        """Remove element at index, shifting elements left. O(n)."""
        self._check_index(index)
        removed = self._data[index]
        # Shift elements left to fill the gap
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._size - 1] = None
        self._size -= 1
        return removed

    def search(self, value):
        """Return index of first occurrence of value, or -1. O(n)."""
        for i in range(self._size):
            if self._data[i] == value:
                return i
        return -1

    def size(self):
        return self._size

    def to_list(self):
        return [self._data[i] for i in range(self._size)]

    # ── Internal Helpers ──────────────────────────────────────

    def _resize(self, new_capacity):
        """Double (or halve) internal storage. O(n)."""
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data     = new_data
        self._capacity = new_capacity

    def _check_index(self, index):
        if index < 0 or index >= self._size:
            raise IndexError(f"Index {index} out of range for size {self._size}.")

    def __repr__(self):
        return f"DynamicArray({self.to_list()})"


# ============================================================
#  MATRIX
#
#  Represented as a list of lists (row-major order).
#  Accessing element [i][j] is O(1).
#  Inserting or deleting a row is O(cols).
#  Inserting or deleting a column is O(rows).
#
#  Operations:
#    access(row, col)         : O(1)
#    set(row, col, value)     : O(1)
#    insert_row(row_index)    : O(cols)
#    insert_col(col_index)    : O(rows)
#    delete_row(row_index)    : O(rows)
#    delete_col(col_index)    : O(rows * cols)
# ============================================================


class Matrix:

    def __init__(self, rows, cols, default=0):
        self._rows = rows
        self._cols = cols
        self._data = [[default] * cols for _ in range(rows)]

    def access(self, row, col):
        """Return element at (row, col). O(1)."""
        self._check(row, col)
        return self._data[row][col]

    def set_value(self, row, col, value):
        """Set element at (row, col). O(1)."""
        self._check(row, col)
        self._data[row][col] = value

    def insert_row(self, row_index, values=None):
        """Insert a new row at row_index. O(cols)."""
        if values is None:
            values = [0] * self._cols
        self._data.insert(row_index, list(values))
        self._rows += 1

    def delete_row(self, row_index):
        """Remove row at row_index. O(rows)."""
        if row_index < 0 or row_index >= self._rows:
            raise IndexError(f"Row index {row_index} out of range.")
        self._data.pop(row_index)
        self._rows -= 1

    def insert_col(self, col_index, values=None):
        """Insert a new column at col_index. O(rows)."""
        if values is None:
            values = [0] * self._rows
        for i, row in enumerate(self._data):
            row.insert(col_index, values[i])
        self._cols += 1

    def shape(self):
        return (self._rows, self._cols)

    def _check(self, row, col):
        if row < 0 or row >= self._rows or col < 0 or col >= self._cols:
            raise IndexError(f"Index ({row},{col}) out of range for {self._rows}x{self._cols} matrix.")

    def __repr__(self):
        rows_str = "\n  ".join(str(row) for row in self._data)
        return f"Matrix({self._rows}x{self._cols}):\n  {rows_str}"


# ============================================================
#  ARRAY STACK
#
#  LIFO (Last In, First Out) structure backed by a DynamicArray.
#  All core operations are O(1) because we only ever touch the end.
#
#  Operations:
#    push(value)  : O(1) amortized — appends to end
#    pop()        : O(1)           — removes from end
#    peek()       : O(1)           — reads end without removing
#    is_empty()   : O(1)
#    size()       : O(1)
# ============================================================


class ArrayStack:

    def __init__(self):
        self._data = []   # Python list as underlying storage

    def push(self, value):
        """Push value onto the top of the stack. O(1) amortized."""
        self._data.append(value)

    def pop(self):
        """Remove and return the top element. O(1). Raises if empty."""
        if self.is_empty():
            raise IndexError("Cannot pop from an empty stack.")
        return self._data.pop()

    def peek(self):
        """Return the top element without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("Cannot peek an empty stack.")
        return self._data[-1]

    def is_empty(self):
        """Return True if the stack has no elements. O(1)."""
        return len(self._data) == 0

    def size(self):
        return len(self._data)

    def __repr__(self):
        return f"ArrayStack(top={self._data[-1] if self._data else 'empty'}, size={self.size()})"


# ============================================================
#  ARRAY QUEUE  (Circular Buffer)
#
#  FIFO (First In, First Out) structure backed by a fixed-size
#  circular buffer. Using a circular buffer avoids the O(n)
#  shift that a naive array-based queue would require on dequeue.
#
#  When the buffer is full, it doubles in size (amortized O(1)).
#
#  Operations:
#    enqueue(value) : O(1) amortized
#    dequeue()      : O(1)
#    peek()         : O(1)
#    is_empty()     : O(1)
#    size()         : O(1)
# ============================================================


class ArrayQueue:

    INITIAL_CAPACITY = 8

    def __init__(self):
        self._capacity = self.INITIAL_CAPACITY
        self._data     = [None] * self._capacity
        self._front    = 0    # index of the oldest (front) element
        self._size     = 0    # number of elements currently stored

    def enqueue(self, value):
        """Add value to the back of the queue. O(1) amortized."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        back_index = (self._front + self._size) % self._capacity
        self._data[back_index] = value
        self._size += 1

    def dequeue(self):
        """Remove and return the front element. O(1). Raises if empty."""
        if self.is_empty():
            raise IndexError("Cannot dequeue from an empty queue.")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return value

    def peek(self):
        """Return the front element without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("Cannot peek an empty queue.")
        return self._data[self._front]

    def is_empty(self):
        """Return True if the queue has no elements. O(1)."""
        return self._size == 0

    def size(self):
        return self._size

    def _resize(self, new_capacity):
        """Rebuild the circular buffer at double size. O(n)."""
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[(self._front + i) % self._capacity]
        self._data     = new_data
        self._front    = 0
        self._capacity = new_capacity

    def __repr__(self):
        return f"ArrayQueue(front={self.peek() if not self.is_empty() else 'empty'}, size={self.size()})"


# ============================================================
#  SINGLY LINKED LIST
#
#  Each node stores a value and a pointer to the next node.
#  No random access — traversal from the head is O(n) for any
#  operation that needs to find a specific position.
#
#  Operations:
#    insert_front(value)    : O(1)  — prepend at head
#    insert_back(value)     : O(1)  — append at tail (tail pointer)
#    insert_at(index, value): O(n)  — traverse to position
#    delete_front()         : O(1)
#    delete(value)          : O(n)  — find and remove first occurrence
#    search(value)          : O(n)  — linear scan from head
#    traverse()             : O(n)  — visit all nodes
#    size()                 : O(1)  — maintained as a counter
# ============================================================


class _Node:
    """A single node in a linked list."""
    def __init__(self, value):
        self.value = value
        self.next  = None   # pointer to the next node


class SinglyLinkedList:

    def __init__(self):
        self._head  = None   # pointer to the first node
        self._tail  = None   # pointer to the last node (for O(1) append)
        self._size  = 0

    def insert_front(self, value):
        """Prepend a new node at the head. O(1)."""
        new_node      = _Node(value)
        new_node.next = self._head
        self._head    = new_node
        if self._tail is None:
            self._tail = new_node   # first insertion also sets tail
        self._size += 1

    def insert_back(self, value):
        """Append a new node at the tail. O(1) with tail pointer."""
        new_node = _Node(value)
        if self._tail is None:
            self._head = self._tail = new_node
        else:
            self._tail.next = new_node
            self._tail      = new_node
        self._size += 1

    def insert_at(self, index, value):
        """Insert a new node at the given index. O(n)."""
        if index < 0 or index > self._size:
            raise IndexError(f"Index {index} out of range for size {self._size}.")
        if index == 0:
            self.insert_front(value)
            return
        if index == self._size:
            self.insert_back(value)
            return
        # Traverse to the node just before the target position
        current = self._head
        for _ in range(index - 1):
            current = current.next
        new_node       = _Node(value)
        new_node.next  = current.next
        current.next   = new_node
        self._size    += 1

    def delete_front(self):
        """Remove and return the head node's value. O(1)."""
        if self._head is None:
            raise IndexError("Cannot delete from an empty list.")
        value      = self._head.value
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return value

    def delete(self, value):
        """
        Remove the first node with the given value. O(n).
        Returns True if found and deleted, False otherwise.
        """
        if self._head is None:
            return False
        if self._head.value == value:
            self.delete_front()
            return True
        current = self._head
        while current.next is not None:
            if current.next.value == value:
                if current.next == self._tail:
                    self._tail = current   # update tail if deleting last node
                current.next = current.next.next
                self._size  -= 1
                return True
            current = current.next
        return False   # value not found

    def search(self, value):
        """Return the index of the first occurrence of value, or -1. O(n)."""
        current = self._head
        index   = 0
        while current is not None:
            if current.value == value:
                return index
            current = current.next
            index  += 1
        return -1

    def traverse(self):
        """Return a list of all values from head to tail. O(n)."""
        result  = []
        current = self._head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def size(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def __repr__(self):
        return f"SinglyLinkedList({' -> '.join(str(v) for v in self.traverse())})"


# ============================================================
#  ROOTED TREE  (using Linked List nodes)
#
#  Each node stores a value, a list of children (linked via
#  a linked list of child pointers), and a parent pointer.
#  Supports insert (as child of any node) and BFS traversal.
#
#  Operations:
#    insert(parent_value, new_value) : O(n) — find parent then O(1) attach
#    bfs_traversal()                 : O(n) — visit each node once
#    find(value)                     : O(n) — BFS scan
# ============================================================


class _TreeNode:
    """A node in a rooted tree."""
    def __init__(self, value):
        self.value    = value
        self.children = []        # list of _TreeNode children
        self.parent   = None


class RootedTree:

    def __init__(self, root_value):
        self._root = _TreeNode(root_value)
        self._size = 1

    def find(self, value):
        """BFS search — return the tree node with the given value, or None. O(n)."""
        queue = [self._root]
        while queue:
            node = queue.pop(0)
            if node.value == value:
                return node
            queue.extend(node.children)
        return None

    def insert(self, parent_value, new_value):
        """
        Insert new_value as a child of the node with parent_value. O(n).
        Returns True if successful, False if parent not found.
        """
        parent_node = self.find(parent_value)
        if parent_node is None:
            return False
        new_node        = _TreeNode(new_value)
        new_node.parent = parent_node
        parent_node.children.append(new_node)
        self._size += 1
        return True

    def bfs_traversal(self):
        """Return all node values in breadth-first order. O(n)."""
        result = []
        queue  = [self._root]
        while queue:
            node = queue.pop(0)
            result.append(node.value)
            queue.extend(node.children)
        return result

    def size(self):
        return self._size

    def __repr__(self):
        return f"RootedTree(root={self._root.value}, size={self._size}, BFS={self.bfs_traversal()})"


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

    def check(label, condition, note=""):
        nonlocal all_passed
        ok     = bool(condition)
        status = COLOR_GREEN + "PASS" + COLOR_RESET if ok else COLOR_RED + "FAIL" + COLOR_RESET
        if not ok:
            all_passed = False
        suffix = f"  ({note})" if note else ""
        print(f"  {status}  {label}{suffix}")

    print()
    print(f"  {COLOR_CYAN}── DynamicArray ─────────────────────────────────{COLOR_RESET}")
    arr = DynamicArray()
    arr.append(10); arr.append(20); arr.append(30)
    check("append and access",              arr.access(1) == 20)
    arr.insert(1, 15)
    check("insert at index 1",             arr.to_list() == [10, 15, 20, 30])
    arr.delete(0)
    check("delete at index 0",             arr.to_list() == [15, 20, 30])
    check("search existing value",         arr.search(20) == 1)
    check("search missing value",          arr.search(99) == -1)

    print(f"\n  {COLOR_CYAN}── Matrix ───────────────────────────────────────{COLOR_RESET}")
    m = Matrix(3, 3)
    m.set_value(0, 0, 1); m.set_value(1, 1, 5); m.set_value(2, 2, 9)
    check("set and access (0,0)",          m.access(0, 0) == 1)
    check("set and access (1,1)",          m.access(1, 1) == 5)
    m.insert_row(1, [7, 8, 9])
    check("insert_row changes shape",      m.shape() == (4, 3))
    check("inserted row is accessible",    m.access(1, 0) == 7)
    m.delete_row(1)
    check("delete_row restores shape",     m.shape() == (3, 3))

    print(f"\n  {COLOR_CYAN}── ArrayStack ───────────────────────────────────{COLOR_RESET}")
    stack = ArrayStack()
    check("is_empty on fresh stack",       stack.is_empty())
    stack.push(1); stack.push(2); stack.push(3)
    check("peek returns top (3)",          stack.peek() == 3)
    check("pop returns 3",                 stack.pop() == 3)
    check("pop returns 2",                 stack.pop() == 2)
    check("size after pops",               stack.size() == 1)
    stack.pop()
    check("is_empty after draining",       stack.is_empty())
    try:
        stack.pop()
        check("pop on empty raises IndexError", False)
    except IndexError:
        check("pop on empty raises IndexError", True)

    print(f"\n  {COLOR_CYAN}── ArrayQueue ───────────────────────────────────{COLOR_RESET}")
    q = ArrayQueue()
    check("is_empty on fresh queue",       q.is_empty())
    q.enqueue("A"); q.enqueue("B"); q.enqueue("C")
    check("peek returns front (A)",        q.peek() == "A")
    check("dequeue returns A (FIFO)",      q.dequeue() == "A")
    check("dequeue returns B",             q.dequeue() == "B")
    check("size after dequeues",           q.size() == 1)
    # Test circular buffer wrap-around
    for i in range(20):
        q.enqueue(i)
    all_correct = all(q.dequeue() == v for v in ["C"] + list(range(20)))
    check("circular buffer wraps correctly (21 items)", all_correct)

    print(f"\n  {COLOR_CYAN}── SinglyLinkedList ─────────────────────────────{COLOR_RESET}")
    ll = SinglyLinkedList()
    check("is_empty on fresh list",        ll.is_empty())
    ll.insert_front(2); ll.insert_front(1)
    ll.insert_back(3);  ll.insert_back(4)
    check("insert_front and insert_back",  ll.traverse() == [1, 2, 3, 4])
    ll.insert_at(2, 99)
    check("insert_at index 2",             ll.traverse() == [1, 2, 99, 3, 4])
    check("search existing value",         ll.search(99) == 2)
    check("search missing value",          ll.search(77) == -1)
    ll.delete(99)
    check("delete by value",               ll.traverse() == [1, 2, 3, 4])
    ll.delete_front()
    check("delete_front",                  ll.traverse() == [2, 3, 4])
    check("size is 3",                     ll.size() == 3)
    check("delete missing value",          ll.delete(99) is False)

    print(f"\n  {COLOR_CYAN}── RootedTree ───────────────────────────────────{COLOR_RESET}")
    tree = RootedTree("root")
    tree.insert("root", "child1")
    tree.insert("root", "child2")
    tree.insert("child1", "grandchild1")
    tree.insert("child2", "grandchild2")
    check("BFS traversal order",           tree.bfs_traversal() == ["root","child1","child2","grandchild1","grandchild2"])
    check("find existing node",            tree.find("grandchild1") is not None)
    check("find missing node",             tree.find("ghost") is None)
    check("size is 5",                     tree.size() == 5)
    check("insert returns False for missing parent", tree.insert("ghost", "x") is False)

    print()
    print(f"  {divider('─', 60)}")
    overall = (COLOR_GREEN + "  ✔  ALL TESTS PASSED" + COLOR_RESET
               if all_passed else COLOR_RED + "  ✘  SOME TESTS FAILED" + COLOR_RESET)
    print(f"{overall}\n")
    return all_passed


# ============================================================
#  OPERATION TIMING BENCHMARK
# ============================================================


def run_timing_benchmark():
    section_header("OPERATION TIMING BENCHMARK")

    sizes = [1000, 5000, 10000]

    col_ds   = 20
    col_op   = 22
    col_n    = 8
    col_t    = 14

    print(f"\n  {'Data Structure':<{col_ds}}  {'Operation':<{col_op}}  {'n':>{col_n}}  {'Time (ms)':>{col_t}}")
    print(f"  {divider('─', col_ds)}  {divider('─', col_op)}  {divider('─', col_n)}  {divider('─', col_t)}")

    for n in sizes:

        # DynamicArray
        da = DynamicArray()
        t = time.perf_counter()
        for i in range(n): da.append(i)
        print(f"  {'DynamicArray':<{col_ds}}  {'append x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        t = time.perf_counter()
        for i in range(n): da.access(i)
        print(f"  {'DynamicArray':<{col_ds}}  {'access x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        t = time.perf_counter()
        for _ in range(min(n, 100)): da.insert(0, -1)   # insert at front (worst case)
        print(f"  {'DynamicArray':<{col_ds}}  {'insert[0] x 100':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        # ArrayStack
        stk = ArrayStack()
        t = time.perf_counter()
        for i in range(n): stk.push(i)
        print(f"  {'ArrayStack':<{col_ds}}  {'push x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        t = time.perf_counter()
        for _ in range(n): stk.pop()
        print(f"  {'ArrayStack':<{col_ds}}  {'pop x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        # ArrayQueue
        q = ArrayQueue()
        t = time.perf_counter()
        for i in range(n): q.enqueue(i)
        print(f"  {'ArrayQueue':<{col_ds}}  {'enqueue x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        t = time.perf_counter()
        for _ in range(n): q.dequeue()
        print(f"  {'ArrayQueue':<{col_ds}}  {'dequeue x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        # SinglyLinkedList
        ll = SinglyLinkedList()
        t = time.perf_counter()
        for i in range(n): ll.insert_back(i)
        print(f"  {'SinglyLinkedList':<{col_ds}}  {'insert_back x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        t = time.perf_counter()
        for i in range(n): ll.insert_front(i)
        print(f"  {'SinglyLinkedList':<{col_ds}}  {'insert_front x n':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        t = time.perf_counter()
        ll.traverse()
        print(f"  {'SinglyLinkedList':<{col_ds}}  {'traverse (full)':<{col_op}}  {n:>{col_n},}  {(time.perf_counter()-t)*1000:>{col_t}.3f}")

        dot_char = "\u00b7"
        print(f"  {divider(dot_char, col_ds + col_op + col_n + col_t + 8)}")

    # ── Complexity Reference ──────────────────────────────────
    print()
    print(divider("═"))
    print(f"  {COLOR_BOLD}COMPLEXITY REFERENCE{COLOR_RESET}")
    print(divider("═"))
    print(f"""
  {COLOR_CYAN}DynamicArray:{COLOR_RESET}
    access(i)         O(1)          Contiguous memory — direct index
    append()          O(1) amort.   Occasional O(n) resize doubles capacity
    insert(i, v)      O(n)          Shifts all elements after index i
    delete(i)         O(n)          Shifts all elements after index i
    search(v)         O(n)          Linear scan

  {COLOR_CYAN}ArrayStack:{COLOR_RESET}
    push / pop / peek O(1)          Only touches the top (end of array)

  {COLOR_CYAN}ArrayQueue (circular buffer):{COLOR_RESET}
    enqueue / dequeue O(1) amort.   Front/back pointers avoid shifting

  {COLOR_CYAN}SinglyLinkedList:{COLOR_RESET}
    insert_front      O(1)          Update head pointer only
    insert_back       O(1)          Tail pointer maintained
    insert_at(i)      O(n)          Traverse to position i
    delete(v)         O(n)          Traverse to find value
    search(v)         O(n)          Linear scan from head
    traverse          O(n)          Visit every node once

  {COLOR_CYAN}RootedTree:{COLOR_RESET}
    insert            O(n)          BFS to find parent node
    bfs_traversal     O(n)          Visit every node once
    find              O(n)          BFS scan

  Ref: Cormen et al. (2022), Introduction to Algorithms, 4th ed., Ch. 10
    """)


# ============================================================
#  MAIN
# ============================================================

if __name__ == "__main__":
    verify_correctness()
    run_timing_benchmark()