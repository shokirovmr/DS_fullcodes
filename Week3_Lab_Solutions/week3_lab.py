"""Week 3 Lab - Advanced Trees: REFERENCE SOLUTION (instructor copy).

Run this file to test the solution:
    python week3_lab.py
All four lines must print PASS. The test functions are unchanged from the starter.
"""
import bisect
import random
import sys
import time

sys.setrecursionlimit(10000)


# ======================================================== Part A: plain BST
class BSTNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        """A1: iterative insertion (no recursion). Ignore duplicates."""
        new = BSTNode(key)
        if self.root is None:
            self.root = new
            return
        cur = self.root
        while True:
            if key < cur.key:
                if cur.left is None:
                    cur.left = new
                    return
                cur = cur.left
            elif key > cur.key:
                if cur.right is None:
                    cur.right = new
                    return
                cur = cur.right
            else:
                return  # duplicate

    def search(self, key):
        """A2: iterative search. Return True if key is present."""
        cur = self.root
        while cur is not None:
            if key == cur.key:
                return True
            cur = cur.left if key < cur.key else cur.right
        return False

    def height(self):
        """A3: height in edges (empty tree = -1), using an explicit stack."""
        if self.root is None:
            return -1
        best = 0
        stack = [(self.root, 0)]
        while stack:
            node, depth = stack.pop()
            if depth > best:
                best = depth
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))
        return best


# ======================================================== Part B: rotations
def rotate_left(x):
    """B1: rotate left at x and return the new subtree root y.

        x                y
       / \\              / \\
      T1  y     ->     x   T3
         / \\          / \\
        T2  T3       T1  T2
    """
    y = x.right
    x.right = y.left   # T2 changes parent
    y.left = x
    return y


def rotate_right(y):
    """B2: rotate right at y and return the new subtree root x (mirror of B1)."""
    x = y.left
    y.left = x.right   # T2 changes parent
    x.right = y
    return x


# ======================================================== Part C: AVL tree
class AVLNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 0


def h(node):
    return node.height if node else -1


def update(node):
    node.height = 1 + max(h(node.left), h(node.right))


def balance(node):
    # Convention: BF = height(left) - height(right). Positive = left-heavy.
    return h(node.left) - h(node.right)


class AVLTree:
    def __init__(self):
        self.root = None
        self.rotations = 0

    def rotate_left(self, x):
        """C1: rotate left, update heights (lower node x first), count it."""
        y = x.right
        x.right = y.left
        y.left = x
        update(x)
        update(y)
        self.rotations += 1
        return y

    def rotate_right(self, y):
        """C2: mirror of rotate_left."""
        x = y.left
        y.left = x.right
        x.right = y
        update(y)
        update(x)
        self.rotations += 1
        return x

    def rebalance(self, node):
        """C3: update height; apply LL / LR / RR / RL fix if |BF| > 1."""
        update(node)
        bf = balance(node)
        if bf > 1:                                   # left-heavy
            if balance(node.left) < 0:               # LR
                node.left = self.rotate_left(node.left)
            return self.rotate_right(node)           # LL (and 2nd half of LR)
        if bf < -1:                                  # right-heavy
            if balance(node.right) > 0:              # RL
                node.right = self.rotate_right(node.right)
            return self.rotate_left(node)            # RR (and 2nd half of RL)
        return node

    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        """C4: recursive BST insertion that returns self.rebalance(node)."""
        if node is None:
            return AVLNode(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        elif key > node.key:
            node.right = self._insert(node.right, key)
        else:
            return node  # duplicate: nothing changed
        return self.rebalance(node)

    def search(self, key):
        cur = self.root
        while cur:
            if key == cur.key:
                return True
            cur = cur.left if key < cur.key else cur.right
        return False

    def height(self):
        return h(self.root)

    def is_valid(self):
        """C5: (1) BST order via lo/hi bounds, (2) stored heights correct,
        (3) every balance factor in {-1, 0, +1}."""
        def check(node, lo, hi):
            # returns the true height of the subtree, or raises ValueError
            if node is None:
                return -1
            if (lo is not None and node.key <= lo) or (hi is not None and node.key >= hi):
                raise ValueError("order")
            hl = check(node.left, lo, node.key)
            hr = check(node.right, node.key, hi)
            if node.height != 1 + max(hl, hr):
                raise ValueError("height")
            if abs(hl - hr) > 1:
                raise ValueError("balance")
            return node.height
        try:
            check(self.root, None, None)
            return True
        except ValueError:
            return False


# ======================================================== Part D: Red-Black validator
# A Red-Black tree is given as nested tuples: (key, colour, left, right)
# where colour is "R" or "B" and an empty child (NIL) is None.

class _RBViolation(Exception):
    pass


def is_valid_rb(t):
    """D3: return (True, black_height) for a valid Red-Black tree and
    (False, reason) otherwise. black_height counts the black nodes on any
    root-to-NIL path, including the root and the NIL itself."""
    if t is not None and t[1] != "B":
        return (False, f"property 2: root {t[0]} is red")

    def bh(node, lo, hi):
        if node is None:
            return 1                                   # NIL is black
        key, colour, left, right = node
        if colour not in ("R", "B"):
            raise _RBViolation(f"property 1: node {key} has colour {colour!r}")
        if (lo is not None and key <= lo) or (hi is not None and key >= hi):
            raise _RBViolation(f"BST order broken at {key}")
        if colour == "R":
            for child in (left, right):
                if child is not None and child[1] == "R":
                    raise _RBViolation(f"property 4: red node {key} has red child {child[0]}")
        lb = bh(left, lo, key)
        rb = bh(right, key, hi)
        if lb != rb:
            raise _RBViolation(f"property 5: black-height mismatch at {key} ({lb} vs {rb})")
        return lb + (1 if colour == "B" else 0)

    try:
        return (True, bh(t, None, None))
    except _RBViolation as e:
        return (False, str(e))


# ======================================================== tests (do not edit)
def run(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
    except NotImplementedError:
        print(f"TODO  {name}")
    except AssertionError as e:
        print(f"FAIL  {name}  {e}")


def inorder(n, out):
    if n:
        inorder(n.left, out)
        out.append(n.key)
        inorder(n.right, out)
    return out


def test_bst():
    t = BST()
    for k in range(2000):
        t.insert(k)
    assert t.height() == 1999, "sorted input should give a chain"
    assert t.search(1234) and not t.search(5000)


def test_rotations():
    rng = random.Random(0)
    for _ in range(100):
        t = BST()
        for k in rng.sample(range(500), 40):
            t.insert(k)
        before = inorder(t.root, [])
        t.root = rotate_left(t.root) if t.root.right else rotate_right(t.root)
        assert inorder(t.root, []) == before, "rotation changed the in-order sequence"


def test_avl():
    rng = random.Random(1)
    for order in ("sorted", "random"):
        keys = list(range(3000))
        if order == "random":
            rng.shuffle(keys)
        t = AVLTree()
        for k in keys:
            t.insert(k)
        assert t.is_valid(), f"invalid AVL tree ({order} input)"
        assert t.height() <= 1.44 * 11.56 + 1, "AVL tree too tall"


def test_rb():
    good = (13, "B", (8, "R", (1, "B", None, None), (11, "B", None, None)),
            (17, "R", (15, "B", None, None), (25, "B", None, None)))
    red_red = (20, "B", (10, "B", None, None), (30, "B", (25, "R", None, (27, "R", None, None)), None))
    assert is_valid_rb(good) == (True, 3), "tree 1 is valid with black-height 3 (counting NIL)"
    assert is_valid_rb(red_red)[0] is False, "tree 2 has a red node with a red child"


if __name__ == "__main__":
    run("Part A  BST on 2,000 sorted keys", test_bst)
    run("Part B  rotations keep in-order", test_rotations)
    run("Part C  AVL insert + validator", test_avl)
    run("Part D  Red-Black validator", test_rb)
