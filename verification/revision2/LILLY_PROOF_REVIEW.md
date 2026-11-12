# Revision2 proof bridges: artifact-only adversarial report

Date: 2026-11-11. Reviewer: Lilly (GPT-6.1 Sol High). Writer of reviewed proof: Manny. Status: **conditional algebraic argument accepted; no critical or major mathematical challenge found.** This is a bounded independent review, not a certification of all finite-rank outputs or numerical trajectories.

## Materials and boundary

Reviewed only the current mathematical artifacts:

- `notebook/projects/correlated-noise/review-package-2026-11-11/manny/PROOF_BRIDGES_SPEC.md`.
- `notebook/projects/correlated-noise/review-package-2026-11-11/manny/PROOF_BRIDGES.md`, all numbered steps.
- `notebook/projects/correlated-noise/review-package-2026-11-11/manny/letter_prl_revision_2.tex`, especially lines 37–54,73–82,130–152 and176–238.

No historical review, project status, author chat reasoning, production code or earlier check output was used as evidence. The proof packet states the rank outputs as evidence inputs but names no concrete certificate-file paths. No elimination output was inspected or rerun in this pass. Thus the finite-output claims remain external premises of this report; the implication from a valid full modular rank to convergence is what was reviewed. No new simulation or CAS run was performed. The verification method is direct independent reconstruction of the finite-dimensional argument below.

## Conditions actually required

Finite L>=3; physical finite-dimensional Hilbert space with its usual inner product and trace; gamma>0; real b with sin(2b) nonzero; periodic uniform Ising/longitudinal layer UI commuting with Jz; collective dephasing E=exp[-(gamma/2)ad_Sz^2] with Sz=2Jz; a reducing invariant-vector sector S containing the polarized vector v. Conditional attraction additionally requires a scalar fixed algebra on S. The certificate implication uses J=pi/4, exact integer orbit-generator matrices and genuine full cyclic rank at the size claimed. The manuscript uses h=1 and b=-pi/4 and does not earn an all-size extension from this finite certificate.

## Step-by-step attack and disposition

| Step | Adversarial question and independent check | Disposition |
|---|---|---|
| 1 | Does norm equality apply to X or the coherently evolved Y? The chain explicitly sets Y=UF X UF† and applies E to Y. Both endpoints have norm ||X||2 because |lambda|=1 and Ad_UF is unitary on operator Hilbert space. | Pass. |
| 1.1 | For a matrix unit between Sz eigenvectors s,s', ad_Sz has eigenvalue s-s'; E has the strictly positive real multiplier exp[-gamma(s-s')²/2]. Distinct magnetizations contract strictly when gamma>0; degeneracies within one magnetization do not. This is consistent with the manuscript jump sqrt(gamma) Sz. | Pass; no normalization mismatch. |
| 1.2 | Equality of the squared Hilbert–Schmidt norms is a sum of nonnegative block contributions. Any unequal-s component would reduce it strictly, so it must vanish. Thus E(Y)=Y and M(X)=Y=lambda X; lambda is nonzero, giving [Jz,X]=0 as well. | Pass; the transfer back to X is established, not assumed. |
| 1.3 | Conjugating [Jz,X]=0 **forward** gives [UF Jz UF†,Y]=0. UI commutes with Jz, so this becomes [UK Jz UK†,lambda X]=0. For UK=exp[-i2bJx], the infinitesimal derivative is -i[Jx,Jz]=-Jy, so the stated rotation cos(2b)Jz-sin(2b)Jy has the correct sign. Sin(2b) nonzero gives [Jy,X]=0, and [[Jy,Jz],X]=0 gives [Jx,X]=0. No commutation of UI with Jy is used. | Pass. |
| 1.4 | Commutation with Jx implies commutation with UK and UK†, allowing removal of UK from UF X UF†=lambda X. Conversely UI X UI†=lambda X and collective-spin commutation give Ad_UF X=lambda X and E(X)=X. At lambda=1 this is precisely the commutant of the listed operators. | Pass; fixed and peripheral descriptions both directions checked. |
| 2 | Is the restriction unital/CP/trace preserving? P commutes with the unitary layers and Sz, so B(S) is an invariant corner, E(P)=P and M(P)=P. Compression of the full CPTP map to this reducing corner is CPTP with unit P. This supplies the Schwarz hypothesis on the restricted map. | Pass. |
| 2.1 | Schwarz gives positive D=M(X†X)-M(X)†M(X). Tr D=Tr X†X-|lambda|² Tr X†X=0, using actual trace preservation. In finite dimension positivity plus zero trace gives D=0. | Pass. |
| 2.2 | Scalar fixed space gives X†X=c I_S. Nonzero X implies c=Tr(X†X)/dim S>0; X is a square matrix with no kernel, hence invertible. An arbitrary positive-semidefinite scalar would not suffice without nonzero X, which is explicitly supplied. | Pass. |
| 3 | Does a supported operator extend correctly by zero? Because P reduces UF and Sz, the block diagonal extension X=PXP obeys the same commutators/eigenoperator equation in the full space. There are no off-corner terms. | Pass. |
| 3.1 | The highest Jz eigenvalue L/2 has exactly one computational eigenvector, v=all zero. Commutation with Jz implies Xv=c0v. UI is diagonal in the computational basis, so UIv=uv. This does not require a maximal-spin representation theorem. | Pass. |
| 3.2 | Applying UI X UI† to v gives u* UI(c0v)=c0v, while the eigenrelation gives lambda c0v. If lambda differs from one, c0=0. Since v belongs to S and is nonzero, this contradicts the invertibility established in 2.2. | Pass; nontrivial peripheral phases excluded under scalarity. |
| 3.3 | Each power of an HS contraction has operator norm at most one. A Jordan block of size>1 at |lambda|=1 has polynomial growth on a generalized eigenvector and cannot occur. Once the only peripheral eigenvalue is one and its eigenspace is scalar, all remaining finite-dimensional Jordan contributions decay. Trace preservation fixes the limiting scalar for a density to 1/dim S. | Pass; ordinary, not merely Cesàro, convergence follows. |
| 4 | For a periodic binary string, domain walls come in pairs and sum ZjZj+1=L-2n_DW. At J=pi/4 the phase is exp[-i pi L/4] exp[i pi n_DW/2]=exp[-i pi L/4](-1)^(n_DW/2). The longitudinal factor is exp[-i2hJz]. | Pass; phase, parity and signs correct. |
| 4.1 | In a finite-dimensional unital algebra, a function on the finite spectrum of Jz is represented by an interpolation polynomial. Thus its projectors and exp[i2hJz] are in the algebra. Multiplying UI by that exponential and the scalar phase recovers R; (I±R)/2 gives R projectors. Jz and R commute, so products give joint projectors. In orbit-sum coordinates those projectors are diagonal zero/one matrices; spin flips have integer multiplicity coefficients. | Pass. |
| 4.2 | A polynomial equal to one at Jz=L/2 and zero at the other Jz eigenvalues gives exactly q=|v><v|, including on S. The nondegenerate highest eigenspace, not generic cyclicity alone, is essential here. | Pass. |
| 4.3 | If C commutes with q, Cv=qCv belongs to span v. Commutation with every generated A then gives CAv=cAv. Full cyclic span forces equality to cI_S on all of S. Consequently the algebra commutant, which is the fixed algebra by 1.4, is scalar. | Pass. |
| 4.4 | Each word in the integer certificate generators applied to the integer-coordinate v gives an integer column. A full-rank determinant modulo a prime is an integer determinant not divisible by that prime, hence nonzero over C. Even if modular elimination uses inverses, they change only the span over that finite field; they cannot manufacture rank above the original word span. | Pass as a conditional implication; actual rank inputs not reproduced. |

## Result independently reconstructed

At a size where the stated integer cyclic-rank premise is genuine, it forces a scalar commutant. Steps 1–3 then exclude every nonconstant unit-modulus eigenoperator and exclude peripheral Jordan blocks, yielding ordinary convergence of every density supported on S to P/Tr P. There is no logical gap requiring generic ergodicity to be assumed. The product input in the manuscript is supported in S because a site permutation leaves its uniform tensor product unchanged.

The finite-size premise in manuscript line142 lists fourteen dimensions for L=3 through16 and prime1000003 at all those sizes; the second prime1000033 is stated only for even sizes and L=13,15. The implication does **not** require both primes—one valid full rank suffices—but the report does not upgrade the actual coverage or certify those computations. Attraction at L>16, a mixing rate, numerical accuracy of the plotted full-density sweep, imperfect-xi asymptotics and perturbed parameters do not follow from this review.

## Minor clarifications, not blockers

1. In the spec, “E preserves S” should be understood as preservation of the operator corner B(S), since E is a map on operators, not a Hilbert-space operator. The proof and manuscript use the correct restriction.
2. The unnormalized orbit-sum basis is generally nonorthonormal. Integer rank calculations are basis invariant, but Euclidean norm/ordinary-transpose adjoints in those coordinates are not the physical HS norm/adjoint without the Gram metric. No such incorrect identification occurs in the present proof. Preserve this separation in code explanations.
3. Concrete paths/hashes for certificate outputs would let a later reviewer inspect the external rank premises. Their absence from this deliberately bounded proof packet is a limitation, not a counterexample to the algebraic argument.

## Incidental integration issue reported immediately

The reviewed draft source opened figure environments at lines63 and69 without their closing environments before subsequent prose. This is a TeX integration/build blocker, independent of the mathematical proof. It was promptly reported to the coordinator. This report does not claim to have reviewed or built the coordinator's subsequently repaired integrated copy.

## Final disposition

**No critical/major mathematical challenge remains to the conditional proof bridges.** Accept them for the stated finite-dimensional conditional argument. This disposition does not by itself certify the finite output inputs or promote any broader numerical/scientific result. All numbered steps were checked; no unsupported theorem for imperfect noise was used to justify them.
