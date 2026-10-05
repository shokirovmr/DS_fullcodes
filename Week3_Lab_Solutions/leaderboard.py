"""Week 3 Lab - Mini challenge: order-statistic AVL leaderboard (reference solution).

    python leaderboard.py            # 200,000 players, checks both versions agree
    python leaderboard.py --scale    # time per update at 200k, 1M and 2M players
"""
import bisect
import random
import sys
import time

sys.setrecursionlimit(10000)


class Node:
    __slots__ = ("key", "left", "right", "height", "size")

    def __init__(self, key):
        self.key = key
        self.left = self.right = None
        self.height = 0
        self.size = 1


def h(n):
    return n.height if n else -1


def sz(n):
    return n.size if n else 0


def update(n):
    n.height = 1 + max(h(n.left), h(n.right))
    n.size = 1 + sz(n.left) + sz(n.right)      # size maintained with height


def balance(n):
    return h(n.left) - h(n.right)              # BF = left - right


class OSTree:
    """AVL tree with subtree sizes: insert, delete, select, rank in O(log n)."""

    def __init__(self):
        self.root = None

    def __len__(self):
        return sz(self.root)

    # ---- rotations (update the lower node first) ----
    def _rot_left(self, x):
        y = x.right
        x.right, y.left = y.left, x
        update(x)
        update(y)
        return y

    def _rot_right(self, y):
        x = y.left
        y.left, x.right = x.right, y
        update(y)
        update(x)
        return x

    def _rebalance(self, n):
        update(n)
        bf = balance(n)
        if bf > 1:
            if balance(n.left) < 0:            # LR; BF 0 after delete -> LL
                n.left = self._rot_left(n.left)
            return self._rot_right(n)
        if bf < -1:
            if balance(n.right) > 0:           # RL; BF 0 after delete -> RR
                n.right = self._rot_right(n.right)
            return self._rot_left(n)
        return n

    # ---- insert / delete ----
    def insert(self, key):
        self.root = self._insert(self.root, key)

    def _insert(self, n, key):
        if n is None:
            return Node(key)
        if key < n.key:
            n.left = self._insert(n.left, key)
        elif key > n.key:
            n.right = self._insert(n.right, key)
        else:
            return n
        return self._rebalance(n)

    def delete(self, key):
        self.root = self._delete(self.root, key)

    def _delete(self, n, key):
        if n is None:
            return None
        if key < n.key:
            n.left = self._delete(n.left, key)
        elif key > n.key:
            n.right = self._delete(n.right, key)
        else:
            if n.left is None:
                return n.right
            if n.right is None:
                return n.left
            succ = n.right                      # two children: use successor
            while succ.left:
                succ = succ.left
            n.key = succ.key
            n.right = self._delete(n.right, succ.key)
        return self._rebalance(n)

    # ---- order statistics ----
    def select(self, k):
        """k-th smallest key, 0-based."""
        if not 0 <= k < len(self):
            raise IndexError(k)
        n = self.root
        while True:
            left = sz(n.left)
            if k < left:
                n = n.left
            elif k == left:
                return n.key
            else:
                k -= left + 1
                n = n.right

    def rank(self, key):
        """Number of keys strictly smaller than key."""
        r, n = 0, self.root
        while n:
            if key <= n.key:
                n = n.left
            else:
                r += sz(n.left) + 1
                n = n.right
        return r

    def top(self, k):
        """Stretch: the k smallest keys (= k best players) in O(log n + k)."""
        out, stack, n = [], [], self.root
        while (stack or n) and len(out) < k:
            while n:
                stack.append(n)
                n = n.left
            n = stack.pop()
            out.append(n.key)
            n = n.right
        return out

    # ---- validation ----
    def is_valid(self):
        def check(n, lo, hi):
            if n is None:
                return -1, 0
            if (lo is not None and n.key <= lo) or (hi is not None and n.key >= hi):
                raise AssertionError("order")
            hl, sl = check(n.left, lo, n.key)
            hr, sr = check(n.right, n.key, hi)
            assert n.height == 1 + max(hl, hr), "height"
            assert abs(hl - hr) <= 1, "balance"
            assert n.size == 1 + sl + sr, "size"
            return n.height, n.size
        try:
            check(self.root, None, None)
            return True
        except AssertionError:
            return False


# ================================================================ leaderboards
class Leaderboard:
    """Keys are (-score, player) so position 1 = highest score, ties by id."""

    def __init__(self):
        self.tree = OSTree()
        self.score = {}

    def set_score(self, player, score):
        old = self.score.get(player)
        if old is not None:
            self.tree.delete((-old, player))
        self.score[player] = score
        self.tree.insert((-score, player))

    def rank_of(self, player):
        return self.tree.rank((-self.score[player], player)) + 1

    def at(self, position):
        neg, player = self.tree.select(position - 1)
        return player, -neg

    def top(self, k):
        return [(p, -s) for s, p in self.tree.top(k)]


class ListLeaderboard:
    """Same interface backed by a sorted Python list + bisect."""

    def __init__(self):
        self.a = []
        self.score = {}

    def set_score(self, player, score):
        old = self.score.get(player)
        if old is not None:
            del self.a[bisect.bisect_left(self.a, (-old, player))]
        self.score[player] = score
        bisect.insort(self.a, (-score, player))

    def rank_of(self, player):
        return bisect.bisect_left(self.a, (-self.score[player], player)) + 1

    def at(self, position):
        neg, player = self.a[position - 1]
        return player, -neg

    def top(self, k):
        return [(p, -s) for s, p in self.a[:k]]


# ================================================================ experiments
def timed(fn):
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


def main(players=200_000, updates=100_000, queries=2_000, seed=7):
    rng = random.Random(seed)
    scores = [rng.randint(0, 1_000_000) for _ in range(players)]
    upd = [(rng.randrange(players), rng.randint(0, 1_000_000)) for _ in range(updates)]
    qs = [(rng.randrange(players), rng.randint(1, players)) for _ in range(queries)]

    boards = {"AVL order-statistic": Leaderboard(), "sorted list + bisect": ListLeaderboard()}
    answers = {}
    print(f"{players:,} players, {updates:,} updates, {queries:,} queries")
    for name, lb in boards.items():
        t_load = timed(lambda: [lb.set_score(p, s) for p, s in enumerate(scores)])
        t_upd = timed(lambda: [lb.set_score(p, s) for p, s in upd])
        out = []
        t_q = timed(lambda: out.extend((lb.rank_of(p), lb.at(k)) for p, k in qs))
        answers[name] = (out, lb.top(10))
        print(f"  {name:22} load {t_load:6.2f} s | updates {t_upd:6.2f} s "
              f"({t_upd / updates * 1e6:5.1f} us each) | queries {t_q * 1000:6.1f} ms")

    avl = boards["AVL order-statistic"]
    assert answers["AVL order-statistic"] == answers["sorted list + bisect"], "boards disagree!"
    assert avl.tree.is_valid(), "invalid AVL/size invariants"
    print("  both leaderboards agree; AVL invariants (order, height, BF, size) valid")
    print("  top 3:", avl.top(3))


def scale(sizes=(200_000, 1_000_000, 2_000_000), updates=20_000):
    print(f"time per update ({updates:,} updates each):")
    for n in sizes:
        rng = random.Random(n)
        row = []
        for cls in (Leaderboard, ListLeaderboard):
            lb = cls()
            if cls is Leaderboard:
                for p in range(n):
                    lb.set_score(p, rng.randint(0, 1_000_000))
            else:  # fast bulk load for the list, same state as n set_score calls
                lb.score = {p: rng.randint(0, 1_000_000) for p in range(n)}
                lb.a = sorted((-s, p) for p, s in lb.score.items())
            upd = [(rng.randrange(n), rng.randint(0, 1_000_000)) for _ in range(updates)]
            row.append(timed(lambda: [lb.set_score(p, s) for p, s in upd]) / updates * 1e6)
        print(f"  n = {n:>9,}: AVL {row[0]:6.2f} us/update | sorted list {row[1]:6.2f} us/update")


if __name__ == "__main__":
    if "--scale" in sys.argv:
        scale()
    else:
        main()
