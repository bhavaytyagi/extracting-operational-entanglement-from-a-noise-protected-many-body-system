"""Exact finite-field cyclicity check for the dephasing bracelet-sector algebra.

Declared checks before execution:
* The existing independent dihedral orbits have the exact Burnside count.
* In the unnormalised orbit-sum basis, sum X_j has integer entries and
  agrees exactly with a full computational-basis action at L <= 8.
* With the ZZ involution removed (J=0), the cyclic space has dimension L+1,
  the unique maximal-spin carrier, NOT the whole bracelet space.
* At self-dual J=pi/4, compare cyclic rank with the previous commutant
  nullity-one evidence for L=4,6,8,10,12; L=13,14,15,16 are research checks.

A full rank modulo a prime implies full rank over Q and C; no floating-point
rank tolerance is used. A deficient modular rank alone is not a complex-rank
certificate. This tests finite sizes, not the all-L conjecture.
No production model or manuscript is changed.
"""
from collections import deque
from math import gcd
import argparse
import numpy as np
from scipy import sparse
from verify_closed_form_independent import orbits


def bracelet_count(n):
    rotations = sum(2**gcd(n, k) for k in range(n))
    reflections = (n * 2**((n+1)//2) if n % 2 else
                   (n//2) * (2**(n//2) + 2**(n//2+1)))
    assert (rotations + reflections) % (2*n) == 0
    return (rotations + reflections) // (2*n)


def integer_model(n):
    obs = orbits(n)
    dim = len(obs)
    assert dim == bracelet_count(n)
    owner = np.full(2**n, -1, dtype=np.int64)
    weight = np.empty(dim, dtype=np.int64)
    parity = np.empty(dim, dtype=np.int64)
    rows, cols, values = [], [], []
    mask = 2**n - 1
    for i, orb in enumerate(obs):
        assert np.all(owner[orb] == -1)
        owner[orb] = i
        w = {int(s).bit_count() for s in orb}
        dw = {(s ^ (((s << 1) | (s >> (n-1))) & mask)).bit_count()
              for s in orb}
        assert len(w) == len(dw) == 1
        walls = dw.pop()
        assert walls % 2 == 0
        weight[i] = w.pop()
        parity[i] = (walls//2) % 2
    assert np.all(owner >= 0)
    # Coefficient at one representative of TARGET orbit i in T |SOURCE j>.
    for i, orb in enumerate(obs):
        targets = owner[[orb[0] ^ (1 << k) for k in range(n)]]
        for j, count in zip(*np.unique(targets, return_counts=True)):
            rows.append(i)
            cols.append(j)
            values.append(int(count))
    flip = sparse.csr_matrix((values, (rows, cols)), shape=(dim, dim), dtype=np.int64)
    sizes = np.array([len(o) for o in obs], dtype=np.int64)
    gram_flip = sparse.diags(sizes, dtype=np.int64) @ flip
    assert (gram_flip - gram_flip.T).nnz == 0
    assert np.all(np.abs(weight[np.array(rows)] - weight[np.array(cols)]) == 1)
    if n <= 8:
        rng = np.random.default_rng(20260910+n)
        for _ in range(3):
            v = rng.integers(-99, 100, size=dim, dtype=np.int64)
            full = v[owner]
            direct = sum(full[np.arange(2**n) ^ (1 << k)] for k in range(n))
            np.testing.assert_array_equal((flip @ v)[owner], direct)
    return flip, weight, parity, int(owner[0])


def cyclic_rank(flip, weight, parity, initial, prime):
    assert prime > len(weight) and all(prime % d for d in range(2, int(prime**.5)+1))
    labels = sorted(set(zip(weight.tolist(), parity.tolist())))
    indices = {label: np.flatnonzero((weight == label[0]) & (parity == label[1]))
               for label in labels}
    basis = {label: {} for label in labels}
    queue = deque()
    accepted = 0

    def insert(label, vector):
        nonlocal accepted
        vector = np.array(vector % prime, dtype=np.int64, copy=True)
        for pivot, previous in sorted(basis[label].items()):
            if vector[pivot]:
                vector = (vector - int(vector[pivot]) * previous) % prime
        nz = np.flatnonzero(vector)
        if not len(nz):
            return
        pivot = int(nz[0])
        vector = (vector * pow(int(vector[pivot]), -1, prime)) % prime
        assert vector[pivot] == 1
        basis[label][pivot] = vector
        queue.append((label, vector))
        accepted += 1

    start_label = (int(weight[initial]), int(parity[initial]))
    start = np.zeros(len(indices[start_label]), dtype=np.int64)
    start[np.flatnonzero(indices[start_label] == initial)[0]] = 1
    insert(start_label, start)
    edges = {}
    for source in labels:
        edges[source] = []
        for target in labels:
            if abs(target[0] - source[0]) != 1:
                continue
            block = flip[indices[target]][:, indices[source]]
            if block.nnz:
                edges[source].append((target, block))
    while queue:
        source, vector = queue.popleft()
        for target, block in edges[source]:
            insert(target, block @ vector)
    # Every retained block vector is independent by distinct unit pivots.
    assert accepted == sum(len(v) for v in basis.values())
    # A separate final closure pass checks the whole computed span.
    for source, vectors in basis.items():
        for vector in vectors.values():
            for target, block in edges[source]:
                residual = block @ vector % prime
                for pivot, previous in sorted(basis[target].items()):
                    residual = (residual - int(residual[pivot]) * previous) % prime
                assert not np.any(residual), (source, target)
    return accepted, [(label, len(basis[label]), len(indices[label])) for label in labels]


def run(n, prime):
    flip, weight, parity, initial = integer_model(n)
    control, _ = cyclic_rank(flip, weight, np.zeros_like(parity), initial, prime)
    assert control == n+1, (n, "J=0 control", control)
    rank, blocks = cyclic_rank(flip, weight, parity, initial, prime)
    print(f"CYCLIC L={n} prime={prime} rank={rank} dim_S={len(weight)} "
          f"J0_rank={control} all_blocks_full={all(r == d for _,r,d in blocks)}",
          flush=True)
    if n in (4,6,8,10,12):
        assert rank == len(weight), "Disagrees with established small-size irreducibility"
    if rank != len(weight):
        print(f"DEFICIENT_BLOCKS {[(lab,r,d) for lab,r,d in blocks if r != d]}", flush=True)
    return rank, len(weight)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[4,6,8,10,12,13,14,15,16])
    parser.add_argument("--prime", type=int, default=1000003)
    args = parser.parse_args()
    assert all(3 <= n <= 16 for n in args.sizes), "Validated domain 3 <= L <= 16"
    for size in args.sizes:
        run(size, args.prime)
    print("ALL DECLARED CYCLICITY CHECKS PASS; NO ALL-L CLAIM", flush=True)
