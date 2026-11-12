# Exact coherent-kick factorization

Author: Luke, GPT-6 Astra High. Status: unverified pending artifact-only review.
This is an arithmetic refactor of the full-density map, not a state reduction.
Relevant conventions and check tolerances are fixed in SPEC.md.

1. ASSUME b=-pi/4, X=[[0,1],[1,0]], D=diag(1,i), and the normalized
   real Hadamard H=[[1,1],[1,-1]]/sqrt(2).
   1.1 Direct 2x2 multiplication gives D H D=[[1,i],[i,1]]/sqrt(2).
   1.2 Since X^2=I, exp(+i*pi*X/4)=(I+iX)/sqrt(2), the same matrix.
   1.3 Hence the physical single-site kick equals D H D by1.1–1.2.
2. Tensoring1.3 at every site gives U_K=D_n H_n D_n, where D_n is diagonal
   with entry i^popcount(index), and H_n is the normalized n-bit Walsh matrix.
   2.1 Independent local gates commute because they act on distinct factors.
   2.2 The tensor product of D,H,D factors distributes by ordinary matrix
       multiplication, establishing the stated product without approximation.
3. After the Ising phase on both sides of rho, multiply by the inner D_n on
   the left and its complex conjugate on the right. Apply real unnormalized
   Walsh transforms W_n=sqrt(d)H_n on row and column indices, d=2^n.
   3.1 Each one-bit butterfly replaces (a,b) with (a+b,a-b), which is exactly
       sqrt(2)H. The n distinct butterflies give W_n, by2.1.
   3.2 A saved copy of a ensures both replacements use old values. Row and
       column transforms have identical real signs since H_n^dagger=H_n.
   3.3 Scaling by1/d accounts for both missing1/sqrt(d) factors.
4. Multiply the outer D_n and its conjugate on opposite sides, then the same
   exact dephasing mask. By1–3, this gives exp(D_xi) Ad_(U_K U_I)(rho).
   Q.E.D. for the stated b; no change at other b is claimed or implemented.

Checks required: the2x2 identity, generic complex mixed states against the old
local-gate kernel (including repeated steps), independent L4 dense Lindblad
reference, and full entrywise L12 original/refactored comparison. Existing
baseline tolerances remain1e-10 for states and1e-9 for trajectories. Intermediate
Walsh values are rescaled only by the exact mathematical1/d; this is not a
trace normalization or repair. All physical trace checks are applied after the
complete step. Machine roundoff may differ from the old multiplication order.
