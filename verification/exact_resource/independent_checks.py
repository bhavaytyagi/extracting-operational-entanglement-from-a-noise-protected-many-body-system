from collections import Counter, deque
from fractions import Fraction
import numpy as np


def orbit(x, length):
    mask = (1 << length) - 1
    reverse = int(f'{x:0{length}b}'[::-1], 2)
    out = set()
    for y in (x, reverse):
        for k in range(length):
            out.add(((y << k) | (y >> (length-k))) & mask)
    return out


def bracelets(length):
    where, orbits = {}, []
    for x in range(1 << length):
        if x in where:
            continue
        ox = orbit(x, length)
        idx = len(orbits)
        orbits.append(ox)
        for y in ox:
            where[y] = idx
    return where, orbits


def label(x, length):
    s = f'{x:0{length}b}'
    walls = sum(s[k] != s[(k+1) % length] for k in range(length))
    assert walls % 2 == 0
    return x.bit_count(), (walls//2) % 2


def rank_certificate(where, orbits, length, prime):
    n = len(orbits)
    reps = [min(o) for o in orbits]
    matrix = np.zeros((n, n), dtype=np.int64)
    # Coefficient on a representative of the target orbit in A sum_{source} |x>.
    for i, x in enumerate(reps):
        for j in range(length):
            matrix[i, where[x ^ (1 << j)]] += 1
    labels = [label(x, length) for x in reps]
    masks = [np.array([v == k for v in labels]) for k in sorted(set(labels))]
    echelon = {}
    queue = deque()

    def add(vector):
        vector = vector.copy() % prime
        for pivot, row in sorted(echelon.items()):
            if vector[pivot]:
                vector = (vector - int(vector[pivot]) * row) % prime
        nz = np.flatnonzero(vector)
        if not len(nz):
            return
        pivot = int(nz[0])
        vector = vector * pow(int(vector[pivot]), -1, prime) % prime
        echelon[pivot] = vector
        queue.append(vector)

    start = np.zeros(n, dtype=np.int64)
    start[where[0]] = 1
    add(start)
    while queue and len(echelon) < n:
        v = queue.popleft()
        add(matrix @ v % prime)
        for m in masks:
            add(v * m)
    return len(echelon)


expected_dims = {4: 6, 6: 13, 8: 30, 10: 78, 12: 224, 14: 687, 16: 2250}
cache = {}
for length, expected in expected_dims.items():
    where, orbits = bracelets(length)
    cache[length] = where, orbits
    assert len(orbits) == expected, (length, len(orbits), expected)
    half = length//2
    a = ''.join(str(j % 2) for j in range(half))
    abar = ''.join(str(1-int(c)) for c in a)
    strings = [int(u+v, 2) for u in (a, abar) for v in (a, abar)]
    block = [[Fraction(1, len(orbits[where[y]])*len(orbits)) if where[x] == where[y] else Fraction(0)
              for y in strings] for x in strings]
    probability = sum(block[j][j] for j in range(4))
    phi = (block[0][0]+block[0][3]+block[3][0]+block[3][3])/(2*probability)
    psi = (block[1][1]+block[1][2]+block[2][1]+block[2][2])/(2*probability)
    f = phi if length % 4 == 0 else psi
    print(f'L={length}: N={len(orbits)}, p={probability}, Bell={f}, F={(2*f+1)/3}, mean preparations={1/probability}')
    if length == 12:
        assert probability == Fraction(1, 192)
        assert phi == Fraction(6, 7) and psi == Fraction(1, 7)
        pair = np.array([[float(v/probability) for v in row] for row in block])
        pt = pair.reshape(2, 2, 2, 2).transpose(2, 1, 0, 3).reshape(4, 4)
        spectrum = np.linalg.eigvalsh(pt)
        assert np.max(np.abs(spectrum-np.array([-5/14, 5/14, 1/2, 1/2]))) < 1e-12
        print('L=12 pair partial-transpose spectrum:', spectrum)

where, orbits = cache[12]
for prime in (1000003, 1000033):
    rank = rank_certificate(where, orbits, 12, prime)
    print(f'L=12 modular cyclic rank prime {prime}: {rank}')
    assert rank == 224

accepted = []
for x in range(64):
    s = f'{x:06b}'
    record = ''.join(str(int(c)^int(s[0])) for c in s[1:])
    if record == '10101':
        accepted.append((s, s[0]))
assert accepted == [('010101', '0'), ('101010', '1')]
print('Exhaustive 64-input CNOT selection:', accepted)
print('ALL PREDECLARED CHECKS PASSED')
