# Self-contained attraction bridges for fresh review

Luke, 2026-11-11. **Unverified author derivation pending fresh artifact-only review.** These are mathematical notes for Manny, not manuscript replacement prose. Their hypotheses and conclusions are explicit so the reviewer need not receive chat history. No citation from memory is used; the proofs below supply the finite-dimensional algebra. Finite rank evidence is a separate artifact, not an assumption disguised as a theorem.

## 0. Problem and conventions

0.1. Given L spin-half sites on a periodic ring, Pauli matrices Z=diag(1,-1), J^a=(1/2)sum_j sigma_j^a, uniform field h, UI=exp[-i(J sum_j Z_j Z_(j+1)+2hJz)], UK=exp[-i2bJx], UF=UK UI. One period is M=E Ad_UF, where E=exp(D1), D1=gamma D[2Jz], D[A](X)=AXA†−{A†A,X}/2, gamma>0. Assume sin(2b) nonzero. Statements concern finite matrices, unit dissipative interval and the Schrödinger-picture unital, trace-preserving CP map.

0.2. Given spatial dihedral spin permutations U(g), P=(1/2L)sum_g U(g), S=range(P), N=dim S. The generators UI,UK,Jz commute with P, so S and S-perpendicular are reducing spaces. The channel restricted to B(S) is unital and trace preserving, with identity P. The restriction preserves supports in S; it need not fix each density on S. Uniform plus product lies in S, as does v=|0>^L.

0.3. To show: (i) characterize peripheral eigenoperators, (ii) scalar commutant on S implies ordinary convergence of every S-supported density to P/N, and (iii) explain why full modular cyclicity rank for the stated generators establishes that scalar commutant. This is not global uniqueness, an all-L certificate or a relaxation-time bound.

## 1. Peripheral characterization

1.1. In a Jz eigenbasis with eigenvalues m,n, E(|m,a><n,b|)=exp[-2gamma(m−n)^2]|m,a><n,b|. This follows directly by applying gamma D[2Jz]. All factors lie in (0,1], and a factor equals1 exactly when m=n. Squaring Hilbert–Schmidt norms entrywise proves ||E(Y)||2≤||Y||2 with equality exactly when [Jz,Y]=0; then E(Y)=Y.

1.2. ASSUME M(X)=lambda X, |lambda|=1 and X nonzero. Put Y=UF X UF†. Unitary norm invariance and 1.1 give ||X||2=||M(X)||2=||E(Y)||2≤||Y||2=||X||2. Hence equality, E(Y)=Y=lambda X, and [Jz,X]=0.

1.3. Conjugating [Jz,X]=0 by UF and using Y=lambda X gives [UF Jz UF†,X]=0. Since [UI,Jz]=0, UF Jz UF†=UK Jz UK†=cos(2b)Jz−sin(2b)Jy. This rotation identity follows by differentiating the conjugation with respect to2b and using [Jx,Jz]=−iJy,[Jx,Jy]=iJz. By sin(2b) nonzero and 1.2, [Jy,X]=0. The commutator of Jy and Jz is iJx, so [Jx,X]=0.

1.4. By 1.3 X commutes UK, so Y=lambda X is equivalent to UI X UI†=lambda X. Conversely, an X commuting all Ja and obeying that UI eigenrelation is fixed by E after the coherent period and hence is peripheral for M. At lambda=1 the fixed algebra is exactly {Jx,Jy,Jz,UI}'. Q.E.D.

1.5. Every X in 1.4 has Xv=cv: [Jz,X]=0 and the eigenspace of Jz at L/2 is the one-dimensional span of v. Since UI v is a scalar phase times v, evaluating UI X UI†=lambda X on v yields c=lambda c. Thus lambda≠1 implies Xv=0. This direct argument avoids an unnecessary representation-theoretic appeal to the whole maximal-spin carrier.

## 2. Scalar fixed algebra gives ordinary attraction

2.1. ASSUME the fixed algebra in 1.4 restricted to B(S) is C P. Then the only fixed density supported in S is P/N, since trace one fixes its scalar. This density is separately invariant under each coherent layer and E by 0.2 and [Jz,P]=0.

2.2. For clarity, the CP Schwarz inequality used here has an explicit finite-dimensional proof. Write a unital CP map as M(A)=V† pi(A)V with V†V=I, where pi(A)=A tensor I and V is the stacked Kraus isometry. Then M(X†X)−M(X)†M(X)=V†pi(X)†(I−VV†)pi(X)V is positive semidefinite. This algebra applies also to the restriction in 0.2.

2.3. For a unit-modulus eigenoperator X on S, trace preservation gives trace(M(X†X)−M(X)†M(X))=trace(X†X)−|lambda|²trace(X†X)=0. A positive semidefinite matrix of zero trace is zero (all its eigenvalues are nonnegative and sum zero). Therefore M(X†X)=X†X.

2.4. By 2.1–2.3, X†X=cP; for X nonzero, c>0. Thus X is injective and invertible on finite S. For lambda≠1, 1.5 instead gives Xv=0 with nonzero v in S, a contradiction. No peripheral eigenvalue except1 exists on B(S).

2.5. The map is a Hilbert–Schmidt contraction by 1.1, hence all its powers are bounded. A nontrivial Jordan block at a unit-modulus eigenvalue would give polynomial growth of powers (expand (lambda I+N)^t); such blocks cannot occur. All remaining eigenvalues have modulus below1 and their Jordan-block powers tend to zero. By 2.1 the remaining limit is a scalar P; trace preservation gives coefficient1/N for a density. Hence M^t(rho)→P/N ordinarily for every S-supported density. Q.E.D. No numerical rate follows.

## 3. What the finite modular certificate establishes

3.1. ASSUME J=pi/4. For a computational string with d domain walls, sum_j Z_j Z_(j+1)=L−2d and d is even on a ring. The ZZ layer equals exp(−i pi L/4)(−1)^(d/2). Define the Hermitian involution R=(−1)^(d/2). With uniform h, UI=exp(−i pi L/4) R exp(−i2hJz).

3.2. Let A be the unital complex *-algebra on S generated by Jx,Jy,Jz,UI. Every spectral projector of Jz is a polynomial in Jz by finite Lagrange interpolation. Exponentials exp(±i2hJz) are also polynomials on its finite spectrum. By 3.1, R belongs to A. Thus the commuting joint weight/R projectors Q_(w,r)=Q_w(I+rR)/2 belong to A, as does sum_j X_j=2Jx.

3.3. The unnormalized sum over each dihedral computational-string orbit is a basis of S. The collective spin-flip operator has integer entries in this basis; the joint projectors are diagonal0/1. v is the basis vector for the all-zero orbit. The certificate computes the vector space generated by successive actions of these generators on v by queue closure and exact elimination modulo a prime. Full rank N modulo a prime certifies N linearly independent words over C: a nonzero minor modulo p is an integer minor not equal to zero. Normalization of orbit vectors changes coordinates, not cyclic dimension.

3.4. The rank-one projector q=|v><v| is the top-weight spectral projector of Jz, hence belongs to A by3.2. For any C in the commutant A', [C,q]=0 forces Cv=cv. For every A in A, CAv=ACv=cAv. If the certificate has full cyclic rank, span{Av}=S, so C=cI_S. Thus the commutant is scalar. This discharges precisely the assumption in2.1.

3.5. Saved output at prime1000003 has full ranks for L=3,...,16, dimensions4,6,8,13,18,30,46,78,126,224,380,687,1224,2250. Saved second-prime1000033 output covers4,6,8,10,12,13,14,15,16. Current bounded audit reruns L12 at both primes only. Files: `paper_pipeline/verification/verify_cyclic_irreducibility_20260910.py`, dependency `verify_closed_form_independent.py`, corresponding first-prime `.out`, and `verify_cyclic_irreducibility_second_prime_20260911.out`. New stdout in `rank-1000003.out`, `rank-1000033.out`. No certificate beyond16 is asserted.

## 4. Imperfect covariance: narrow statement only

4.1. For the complete-graph covariance Xi=(1−xi)I+xi ee^T and gamma>0, the computational coherence |s><t| is multiplied by exp[−gamma Delta_z^T Xi Delta_z/2] during E_xi, where Delta_z is the vector of local Z eigenvalue differences. This follows entrywise from the displayed Lindblad generator; it is valid throughout the PSD interval.

4.2. Take distinct one-spin-down strings s,t. Their difference has zero sum and squared norm8, so the factor is exp[−4gamma(1−xi)]<1 for every allowed xi<1, including the singular lower endpoint. They are in the same spatial orbit and <s|P/N|t>=1/(LN)>0. UF leaves P/N unchanged. Therefore M_xi(P/N) differs in this element from P/N: the ideal target ceases to be stationary for every allowed xi<1.

4.3. The averaged map remains dihedrally covariant because the covariance and coherent layers are invariant under site permutations in D_L. Covariance does not imply support in S remains invariant. For example the normalized one-down superposition W lies in S; E_xi(|W><W|)=a|W><W|+(1−a)I_weight1/L with a=exp[−4gamma(1−xi)]<1. The weight-one part of S is one-dimensional, so the second term leaks outside S. For the whole map choose supported input UF†|W><W|UF. This proves leakage is allowed, not that every state immediately leaks.

4.4. Nothing in4.2–4.3 proves full-map mixing to I/2^L, eventual loss of useful fidelity, or monotone lifetime. Manuscript imperfect-correlation statements should stay with the observed finite samples unless another reviewed proof is supplied. For I/2^L the specified filter would produce I4/4 and F=1/2; this identity alone does not establish convergence to that input.
