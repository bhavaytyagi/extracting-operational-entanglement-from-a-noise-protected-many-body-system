"""
Independent check of E_N^inf = log || (P_sym/N_L)^{T_A} ||_1.

Deliberately a DIFFERENT construction from the dense-projector route used in the
pipeline, so an error common to that route cannot hide here:

  P_sym = sum_O |u_O><u_O|,  |u_O> = m_O^{-1/2} sum_{s in O} |s>,
          O = orbits of the dihedral group D_L on computational basis states.
  (proof: (P_sym)_{s,s'} = |Stab_O|/2L for s,s' in the same orbit, and
   |Stab_O| m_O = 2L, so the orbit block is J_O/m_O.)

Then rho^{T_A} is assembled directly in sparse form from
  (|s><s'|)^{T_A} = |s'_A s_B><s_A s'_B|,
which has at most sum_O m_O^2 <= 2L*2^L nonzeros -- i.e. it is very sparse.
rho^{T_A} is real symmetric, so ||.||_1 = sum |eigenvalues|; we split it into
connected components and diagonalise each densely.
"""
import sys, numpy as np, scipy.sparse as sp
from scipy.sparse.csgraph import connected_components

def orbits(L):
    D = 1 << L
    mask = D - 1
    def rot(s, a): return ((s << a) | (s >> (L - a))) & mask if a else s
    def refl(s):
        r = 0
        for j in range(L):
            if (s >> j) & 1: r |= 1 << (L - 1 - j)
        return r
    seen = np.zeros(D, dtype=bool)
    out = []
    for s in range(D):
        if seen[s]: continue
        orb = set()
        for a in range(L):
            orb.add(rot(s, a)); orb.add(rot(refl(s), a))
        for x in orb: seen[x] = True
        out.append(sorted(orb))
    return out

def EN_inf(L, NA):
    LB = L - NA
    maskB = (1 << LB) - 1
    orbs = orbits(L)
    NL = len(orbs)
    rows, cols, vals = [], [], []
    for orb in orbs:
        m = len(orb)
        w = 1.0 / (NL * m)
        for s in orb:
            sA, sB = s >> LB, s & maskB
            for t in orb:
                tA, tB = t >> LB, t & maskB
                rows.append((tA << LB) | sB)
                cols.append((sA << LB) | tB)
                vals.append(w)
    D = 1 << L
    M = sp.coo_matrix((vals, (rows, cols)), shape=(D, D)).tocsr()
    M.sum_duplicates()
    assert abs(M.diagonal().sum() - 1.0) < 1e-12, M.diagonal().sum()
    asym = abs(M - M.T).max()
    assert asym < 1e-14, asym
    n, lab = connected_components(M, directed=False)
    print(f"  L={L} N_L={NL} nnz={M.nnz} components={n} "
          f"largest={np.bincount(lab).max()}")
    order = np.argsort(lab, kind="stable")
    lab_s = lab[order]
    bounds = np.flatnonzero(np.diff(lab_s)) + 1
    total = 0.0
    for idx in np.split(order, bounds):
        blk = M[idx][:, idx].toarray()
        total += np.abs(np.linalg.eigvalsh(blk)).sum()
    return np.log(total), NL

if __name__ == "__main__":
    ref = {10: 0.823820166737, 12: 0.941952409196, 14: 1.033609849}
    for L in [int(x) for x in sys.argv[1:]]:
        v, NL = EN_inf(L, L // 2)
        r = ref.get(L)
        tag = "" if r is None else f"   ref {r:.12f}   diff {abs(v-r):.2e}"
        print(f"  E_N^inf(L={L}) = {v:.12f}   ebits {v/np.log(2):.4f}   "
              f"bound log2L = {np.log(2*L):.4f}{tag}")
