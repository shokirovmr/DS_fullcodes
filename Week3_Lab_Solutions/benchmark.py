"""Week 3 Lab - Part E: benchmarking (reference solution).

    python benchmark.py
Prints Table 5 and saves plot_random.png and plot_sorted.png.
"""
import bisect
import math
import random
import time

from week3_lab import BST, AVLTree
from rbtree import RBTree


class SortedList:
    """Python list kept sorted with bisect; same interface as the trees."""

    def __init__(self):
        self.a = []

    def insert(self, key):
        i = bisect.bisect_left(self.a, key)
        if i == len(self.a) or self.a[i] != key:   # ignore duplicates, like the trees
            self.a.insert(i, key)

    def search(self, key):
        i = bisect.bisect_left(self.a, key)
        return i < len(self.a) and self.a[i] == key

    def height(self):
        return None  # not a tree: n/a


def run(cls, keys):
    """E1: returns (insert ms, search ms, height)."""
    t = cls()
    start = time.perf_counter()
    for k in keys:
        t.insert(k)
    insert_ms = (time.perf_counter() - start) * 1000
    probe = random.sample(keys, 1000)
    start = time.perf_counter()
    for k in probe:
        t.search(k)
    search_ms = (time.perf_counter() - start) * 1000
    return insert_ms, search_ms, t.height()


def measure(cls, keys):
    run(cls, keys)          # warm-up run, discarded (handout tip)
    return run(cls, keys)


STRUCTS = [("Plain BST", BST), ("AVL tree", AVLTree),
           ("Red-Black tree", RBTree), ("Sorted list + bisect", SortedList)]
SIZES = [1000, 2000, 4000, 8000]


def main():
    random.seed(2026)
    results = {}   # (name, order, n) -> (insert ms, search ms, height)
    for n in SIZES:
        sorted_keys = list(range(n))
        random_keys = sorted_keys[:]
        random.shuffle(random_keys)
        for order, keys in (("random", random_keys), ("sorted", sorted_keys)):
            for name, cls in STRUCTS:
                results[name, order, n] = measure(cls, keys)
        print(f"n = {n:,} done")

    print("\nFull results (insert ms / 1,000 searches ms / height):")
    for order in ("random", "sorted"):
        for name, _ in STRUCTS:
            row = "  ".join(f"{results[name, order, n][0]:8.1f}/{results[name, order, n][1]:6.2f}/{results[name, order, n][2]!s:>4}"
                            for n in SIZES)
            print(f"  {order:6} {name:22} {row}")

    n = 8000
    print(f"\nTable 5 (n = {n:,})")
    print(f"{'Structure':22} {'Ins ms (rand)':>14} {'Ins ms (sort)':>14} {'1k search ms (sort)':>20} {'Height (sort)':>14}")
    for name, _ in STRUCTS:
        r, s = results[name, "random", n], results[name, "sorted", n]
        print(f"{name:22} {r[0]:14.1f} {s[0]:14.1f} {s[1]:20.2f} {s[2] if s[2] is not None else 'n/a':>14}")

    bst_s, avl_s = results["Plain BST", "sorted", n][1], results["AVL tree", "sorted", n][1]
    print(f"\nE4(a) sorted-input search, BST / AVL at n={n:,}: {bst_s / avl_s:.0f}x slower")

    plot(results)


def plot(results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    trees = ["Plain BST", "AVL tree", "Red-Black tree"]
    ref = [math.log2(n) for n in SIZES]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in trees:
        ax.plot(SIZES, [results[name, "random", n][2] for n in SIZES], marker="o", label=name)
    ax.plot(SIZES, ref, "k--", label="log2 n")
    ax.set(title="Tree height vs n (random input)", xlabel="n (keys)", ylabel="height (edges)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig("plot_random.png", dpi=150)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    for name in trees:
        ax.plot(SIZES, [results[name, "sorted", n][2] for n in SIZES], marker="o", label=name)
    ax.plot(SIZES, ref, "k--", label="log2 n")
    ax.set_yscale("log")
    ax.set(title="Tree height vs n (sorted input, log y-axis)", xlabel="n (keys)", ylabel="height (edges)")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig("plot_sorted.png", dpi=150)
    print("saved plot_random.png and plot_sorted.png")


if __name__ == "__main__":
    main()
