# ============================================================
#  Insertion Sort - Monotonically Decreasing Order
# #
#  What is Insertion Sort?
#  -----------------------
#  Imagine you're holding playing cards in your left hand.
#  You pick up one card at a time from the table with your
#  right hand and slide it into the correct spot in your
#  left hand — so your left hand is always sorted.
#
#  This program does the same thing, but sorts numbers from
#  BIGGEST to SMALLEST (that's what "decreasing order" means).
# ============================================================


def insertion_sort(arr):
    """
    Sorts a list of numbers from biggest to smallest using the insertion sort algorithm.

    How it works (step by step):
      - We will go through the list one number at a time.
      - We pick up the current number (call it the 'key').
      - We look at all the numbers to the LEFT of it.
      - If a number to the left is SMALLER than our key,
        we slide it one spot to the right to make room.
      - We keep sliding until we find the right spot,
        then we drop the key in.

    Example:
      Start : [5, 2, 4, 6, 1, 3]
      End   : [6, 5, 4, 3, 2, 1]
    """

    # We start at index 1 because a single element is already "sorted"
    for i in range(1, len(arr)):

        key = arr[i]   # This is the card we just picked up

        # Start comparing with the element just to the LEFT of key
        j = i - 1

        # Keep moving left as long as:
        #   1. We haven't gone past the beginning of the list
        #   2. The element to the left is SMALLER than our key
        #      (In normal increasing sort, you'd check if it's BIGGER.
        #       We flip it to get decreasing order!)
        while j >= 0 and arr[j] < key:
            arr[j + 1] = arr[j]   # Slide the smaller element one spot right
            j -= 1                # Move one step further left

        # We found the right spot — place the key here
        arr[j + 1] = key

    return arr


# ── Run some tests to see it in action ──────────────────────
if __name__ == "__main__":

    print("-" * 50)
    print("  Insertion Sort — Biggest to Smallest")
    print("-" * 50)

    test_cases = [
        [5, 2, 4, 6, 1, 3],        # Example straight from the CLRS textbook
        # Another CLRS example (has a duplicate: 41)
        [31, 41, 59, 26, 41, 58],
        # Already in increasing order (hardest case)
        [1, 2, 3, 4, 5],
        # Already in decreasing order (easiest case)
        [9, 8, 7, 6, 5],
        [7],                         # Only one number
        [],                          # Empty list
        [4, 4, 4, 4],               # All the same number
    ]

    for arr in test_cases:
        original = arr.copy()                        # Save original before sorting
        insertion_sort(arr)               # Sort it!
        correct = arr == sorted(original, reverse=True)
        mark = "PASS" if correct else "FAIL"

        print(f"\n  [{mark}]")
        print(f"  Before : {original}")
        print(f"  After  : {arr}")

    print("\n" + "-" * 50)


# ============================================================
#  TIME COMPLEXITY
#  ---------------
#  Best Case  : O(n)     — list is already sorted biggest to smallest
#  Worst Case : O(n^2)   — list is sorted smallest to biggest
#  This means it works great for small lists!
# ============================================================
