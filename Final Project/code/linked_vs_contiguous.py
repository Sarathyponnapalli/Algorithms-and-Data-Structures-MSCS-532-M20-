"""
Three equivalent sequence structures used to compare cache/data-locality
behavior, mirroring the C++ std::forward_list -> std::vector migrations
described in Azad, Iqbal, Hassan, & Roy (2023):

  1. LinkedList      - singly linked list of boxed Node objects (pointer-chasing,
                        analogous to std::forward_list / TileDB-d51b082 before the fix).
  2. PyListSequence   - Python's built-in list (array of pointers to boxed floats;
                        contiguous *references*, not contiguous *values*).
  3. ArraySequence    - array.array('d', ...), contiguous raw doubles, no NumPy needed.
  4. NumpySequence    - numpy.ndarray(dtype=float64), contiguous raw doubles,
                        analogous to std::vector<double> / CGAL-8855eb5 after the fix.

All four expose the same minimal interface (append, sum_traverse, get) so
benchmark.py can drive them identically.
"""

from __future__ import annotations

import array
from typing import Iterable, Optional

try:
    import numpy as np
    HAVE_NUMPY = True
except ImportError:
    np = None
    HAVE_NUMPY = False


class Node:
    __slots__ = ("value", "next")

    def __init__(self, value: float, next: Optional["Node"] = None):
        self.value = value
        self.next = next


class LinkedList:
    """Singly linked list: each element is a separately heap-allocated Node,
    scattered across memory. Traversal chases pointers with no spatial locality."""

    def __init__(self):
        self._head: Optional[Node] = None
        self._tail: Optional[Node] = None
        self._length = 0

    @classmethod
    def from_iterable(cls, values: Iterable[float]) -> "LinkedList":
        ll = cls()
        for v in values:
            ll.append(v)
        return ll

    def append(self, value: float) -> None:
        node = Node(value)
        if self._tail is None:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._length += 1

    def sum_traverse(self) -> float:
        total = 0.0
        node = self._head
        while node is not None:
            total += node.value
            node = node.next
        return total

    def get(self, index: int) -> float:
        node = self._head
        for _ in range(index):
            node = node.next
        return node.value

    def __len__(self) -> int:
        return self._length


class PyListSequence:
    """Python list: contiguous array of *pointers* to boxed float objects.
    Better than LinkedList (no per-node heap indirection for the container
    itself, O(1) random access) but each element access still dereferences
    a separate PyFloat object living wherever the allocator put it."""

    def __init__(self):
        self._data: list[float] = []

    @classmethod
    def from_iterable(cls, values: Iterable[float]) -> "PyListSequence":
        seq = cls()
        seq._data = list(values)
        return seq

    def append(self, value: float) -> None:
        self._data.append(value)

    def sum_traverse(self) -> float:
        total = 0.0
        for v in self._data:
            total += v
        return total

    def get(self, index: int) -> float:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)


class ArraySequence:
    """array.array('d', ...): contiguous raw C doubles, no NumPy dependency.
    Closest pure-stdlib analogue to std::vector<double>."""

    def __init__(self):
        self._data = array.array("d")

    @classmethod
    def from_iterable(cls, values: Iterable[float]) -> "ArraySequence":
        seq = cls()
        seq._data = array.array("d", values)
        return seq

    def append(self, value: float) -> None:
        self._data.append(value)

    def sum_traverse(self) -> float:
        total = 0.0
        for v in self._data:
            total += v
        return total

    def get(self, index: int) -> float:
        return self._data[index]

    def __len__(self) -> int:
        return len(self._data)


class NumpySequence:
    """numpy.ndarray(dtype=float64): contiguous raw doubles with vectorized
    (SIMD/BLAS-backed) reduction operations, the direct analogue of
    std::vector<double> plus the CGAL-8855eb5-style optimization."""

    def __init__(self):
        if not HAVE_NUMPY:
            raise RuntimeError("numpy is not installed")
        self._data = np.empty(0, dtype=np.float64)

    @classmethod
    def from_iterable(cls, values: Iterable[float]) -> "NumpySequence":
        if not HAVE_NUMPY:
            raise RuntimeError("numpy is not installed")
        seq = cls.__new__(cls)
        seq._data = np.fromiter(values, dtype=np.float64)
        return seq

    def append(self, value: float) -> None:
        # Not used in benchmarks (arrays are built via from_iterable);
        # included only to satisfy the shared interface.
        self._data = np.append(self._data, value)

    def sum_traverse(self) -> float:
        return float(self._data.sum())

    def get(self, index: int) -> float:
        return float(self._data[index])

    def __len__(self) -> int:
        return len(self._data)
