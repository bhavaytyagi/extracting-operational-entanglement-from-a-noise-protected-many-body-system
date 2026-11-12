# Independent acceptance review — 2026-10-29

Reviewer: Codex, fresh artifact-only context. Status: **agent-verified within the finite scope below; no critical or major finding.** This report does not certify all sizes, attraction at arbitrary time, imperfect-correlation dynamics, or physical device performance.

Only this campaign packet was read. The reviewer inspected `SPEC.md`, the three scientific scripts, the bundled reference material, saved tables, the prior independent checker's code/output, and `README.md`. The prior checker supplied no acceptance report. Its independent constructions were inspected rather than treated as established conclusions, copied into this directory, adapted to the J=0 sampling schedule, and rerun. Additional independent sparse-group and rational-arithmetic checks were written here. Scientific sources/data were not changed. All new outputs and test sources are in this directory.

Checker correction retained in the error trail: the original `review/independent_check.py` requested negativity at t=4 even for J=0, although the control only stores t=0,1,10,400. That branch would access a missing key. The final copy selects the actual control sample set and recomputes all four values; the original file is preserved unchanged. This was a checker scheduling defect, not a production-data defect or a weakened tolerance.

## Dated erratum — 2026-10-29, before acceptance integration

Root identified a minor error in the first report's step 5.3: it stated, “For these target blocks the two Bell weights are f and 1-f.” This is true only for even half length. Odd half length has three nonzero Bell weights f, (1-f)/2 and (1-f)/2. The corrected step now gives both exhaustive parity cases explicitly. A new exact-fraction Bell-basis transformation of every saved L4–30 pair state passed in `parity_check.py`, with results in `parity-check.json` and stdout in `parity-check.out`. The ordinary negativity formula `f-1/2`, all saved numerical data, and the L12 README statement remain correct. No scientific source or data was changed. This note preserves the original erroneous statement and its correction.

## Verdict and findings

- **Critical: none found.**
- **Major: none found.** The target charge/reflection decomposition, physical half-cut partial transpose, selected Ising–kick–noise order, reduced ideal dynamics and fixed alternating decoder pass the checks described below.
- **Minor, corrected:** the report initially generalized the two-component Bell decomposition across both parity cases; see the dated erratum and corrected step 5.3. Exact parity checks now pass at every listed size.
- **Minor / portability limitation:** the author's `dynamics.py reference` and `dynamics.py 10` still read two surrounding-project dependencies. They cannot run from the campaign directory alone after extraction. The README now explicitly discloses those dependencies. The L12 trajectory, target calculation and target extraction are self-contained within the packet. This is a reproducibility limitation of two development regression entry points, not a discrepancy in the new results.

Acceptance is for the recorded normalized dihedral target at even sizes 4–16, the specified ideal trajectories at L10/L12 through period 400, and the fixed target-extraction protocol at even sizes 4–30, with the distinctions between direct reruns, regression agreement and analytical checks below. No conclusion about the adequacy of these results for a particular journal is made.

## Independent derivation of the reductions

Conventions: write a computational label as `(a,b)`, where Alice is the most significant L/2 bits, Bob the remaining bits. Let `w(a)` count ones. Let G be the 2L spatial dihedral permutations. The state under test is `rho_* = P/N`, where `P = sum_g U_g/(2L)` and `N = Tr(P)`. Logarithmic negativity is the natural logarithm of the complete physical partial-transpose trace norm.

1. **Projector and orbit basis.**
   1.1. A vector fixed by every spatial permutation is constant on each computational-string orbit. Normalized disjoint orbit sums therefore form an orthonormal basis B of this invariant-vector subspace.
   1.2. Group averaging fixes precisely those vectors and kills their orthogonal complement, so `P = BB†`. An orbit of size s contributes entries `1/s` between its members. Dividing by the number N of orbits gives the target entries used in `target.py`.
   1.3. This is the spatial dihedral invariant-vector sector, not the fully permutation-symmetric spin sector.

2. **Charge blocks after Alice partial transpose.**
   2.1. Every spatial permutation preserves total occupation. Consequently `P[(c,b),(a,d)]` can be nonzero only when `w(c)+w(b)=w(a)+w(d)`.
   2.2. By the definition of Alice transpose, `rho_*^TA[(a,b),(c,d)] = rho_*[(c,b),(a,d)]`. Rearranging 2.1 gives `w(b)-w(a)=w(d)-w(c)`. Thus the exact block label is the difference q used by the implementation.
   2.3. Global bit complement commutes with every spatial permutation. It factors locally into real X gates, so it also commutes with `rho_*^TA`. It maps q to -q and is unitary. Positive and negative q blocks therefore have identical spectra and multiplicity two; q=0 has multiplicity one. No additional complement split inside q=0 is needed.

3. **Local reflection blocks.**
   3.1. For L=2m, the spatial reflection `j -> m-1-j (mod 2m)` reverses the order within both halves and preserves each half. It is a dihedral element and factors as a real local permutation on Alice and Bob.
   3.2. Conjugation by this reflection leaves the target and the entire invariant-vector supported trajectory unchanged. Local real conjugation remains conjugation after Alice transpose; hence the partial transpose commutes with the same reflection R. R also preserves q for the target.
   3.3. For each exchanged pair x,Rx, `(e_x+e_Rx)/sqrt(2)` and `(e_x-e_Rx)/sqrt(2)` are orthonormal eigenvectors. A fixed x contributes only `e_x` to the plus block. These vectors exhaust every computational basis vector. The two dimensions are `(D_q +/- F_q)/2`, where F_q counts fixed strings. Therefore this is a complete spectrum decomposition, not a truncation.
   3.4. A general kicked trajectory does not conserve q. The dynamics negativity routine correctly uses reflection alone, without the target's charge split.

4. **Reduced ideal evolution.**
   4.1. With the packet's conventions, `U = exp(-i b sum_j X_j) exp[-i(J sum_j Z_j Z_(j+1) + h sum_j Z_j)]`, with periodic neighbours. Both factors commute with all spatial dihedral permutations; they preserve the range of B. Thus `U_B = B† U B` is unitary and `UB = B U_B`.
   4.2. `S=sum_j Z_j` is constant on each orbit, with value s_i. The ideal dephasing interval multiplies an orbit density entry by `exp[-gamma (s_i-s_j)^2/2]`. At gamma=0.1 this is the implemented coefficient 0.05. It is the same factor independently reconstructed in the reference checks.
   4.3. The plus product has reduced amplitudes `sqrt(orbit_size/2^L)`. Therefore its exact supported density evolves by `a -> (U_B a U_B†) .* damping`, and the full physical density is `B a B†`. This justifies the L12 reduction without equating it to full imperfect-noise evolution.
   4.4. `I_N/N` is stationary because the reduced unitary is unitary and damping equals one on its diagonal. Stationarity alone does not prove attraction or a convergence rate.
   4.5. At J=0 both coherent layers are products of single-spin gates. The dephasing factor is a Gaussian average of collective Z rotations, each also a product operation. Starting from a product, the trajectory is a mixture of product states at every step. Thus zero entanglement for this control is an independent limiting-case prediction, not a baseline fitted to the calculation. Its lack of approach to the dihedral target is expected.

5. **Extraction and teleportation.**
   5.1. The fixed local filter maps the alternating half-string and its complement coherently to logical 0 and 1. Its unnormalized two-qubit state is exactly the selected 4 by 4 principal block. Its trace is the success probability; division by that trace is conditioning on the physical herald, not a density repair.
   5.2. The target's block entries were independently reconstructed with exact fractions by direct rotations and reversed rotations of the four selected strings. The orbit count was independently obtained from the fixed strings of every permutation.
   5.3. The fixed Bell target is Phi+ for even half length and Psi+ for odd half length. A fixed local X correction in the latter case reduces to the standard Phi+ teleportation convention. Bell measurement and Pauli correction give a Pauli channel whose identity probability is f, hence uniform-input average fidelity `(1+2f)/3`.
      5.3.1. CASE even half length: the Bell weights in order (Phi+, Phi-, Psi+, Psi-) are `(f, 0, 1-f, 0)`. There are two nonzero Bell components.
      5.3.2. CASE odd half length: the Bell weights in the same order are `((1-f)/2, (1-f)/2, f, 0)`. There are three nonzero Bell components; the equal Phi+ and Phi- mixture cancels their 00–11 coherence.
      5.3.3. The cases are exhaustive. For any Bell-diagonal two-qubit state with weights p_i, the partial-transpose eigenvalues are the multiset `1/2-p_i`. In both cases f is the largest weight and exceeds 1/2 for the checked even sizes 4–30. Thus the ordinary pair negativity is `f-1/2` in both cases. `parity-check.json` verifies all off-diagonal Bell-basis entries vanish, the complete exact Bell weights follow these cases, and the saved negativity agrees, for every target table row.
   5.4. The L12 block is exactly `(6/7)Phi+ + (1/7)Psi+` in projector notation: p=1/192, F=19/21, pair negativity=5/14, and classical fallback average `2/3+5/4032`. These are distinct from the full-ring logarithmic negativity.

## Executed checks and exact scope

All commands below ran successfully using `/opt/anaconda3/envs/noisy_env/bin/python`. Each command's stdout is saved as the corresponding `.out`; structured results include current source hashes. Independent numerical checks set one BLAS thread. Jobs were sequential. Largest recorded independent-review peak was below 0.24 GB, well below the 3 GiB cap. The production peaks below are inspected author records, not new production reruns.

```text
python review/final/independent_check.py
python review/final/independent_check.py trajectory 12
python review/final/independent_check.py trajectory 12 --j0
python review/final/independent_check.py trajectory 10
python review/final/supplement.py
python review/final/facts.py
python review/final/parity_check.py
```

Paths in this command block are relative to the campaign root; the actual invocations used the full repository-relative script paths.

### Dense small-size reference

`independent-small.json` records direct group-average matrices, independent index-level partial transpose, and full dense spectra for targets L4,6,8,10. Stored negativity differs by at most 2.23e-16; target PT matrices differ by at most 6.94e-18. These exceed the SPEC's 1e-11 requirement in accuracy.

The independent full unitary is a Kronecker product of one-spin kick matrices times the explicit diagonal Ising/field layer. Full density evolution at L4,6,10 for both J=0 and J=pi/4 agrees with reduced evolution at periods 0–4; largest full-map entry difference is below 9e-16. Independent full PT eigenspectra at periods 0,1,4 agree with the reflection routine within 3.29e-14. L10 stored physical metrics at those periods also agree. This directly checks layer order, damping normalization, spin indexing and physical cut.

### Larger target spectrum

`facts.json` compares every stored even-size L4–16 target negativity to the bundled earlier floor records at tolerance 1e-9. Every comparison passes. At L16 the new value is 1.088191469164693, compared with the rounded prior 1.0881914692 (difference 3.54e-11).

`supplement.json` independently counts all group orbits and reflection block dimensions at L12,14,16. Dimensions sum to 4096,16384,65536 respectively. For L16 it additionally builds the physical partial transpose directly from the spatial group-average permutation matrices, checks forbidden charge entries are absent, checks reflection/complement commutation, verifies numerical basis orthonormality and completeness, and computes every block trace using `(Tr(A) +/- Tr(RA))/2`. Their multiplicity-weighted sum is exactly 1 in the saved floating-point result. Rank is 2250 and largest block is 6470.

**Limit:** this reviewer did not rerun L12,14,16 target eigensolvers. L16 spectrum acceptance rests on checked matrix/reduction construction, complete block/trace checks, small-size direct diagonalization, and agreement with the independently bundled older spectrum. The older rounded scalar is a regression reference, not a directed-rounding error certificate. No claim of independently recomputing every L16 eigenvalue is made.

### L12 trajectories and L10 regression

`independent-trajectory-L12.json` reconstructs every orbit-space kick entry by summing explicit amplitudes indexed by Hamming distance, independently of the author's tensor gate application. It evolves all 401 states and checks preparation probability/fidelity at every period. Maximum resource difference is 1.89e-15; maximum difference of recorded sampled Frobenius distances is 2.03e-15. It directly assembles reflected PT blocks from indexed matrix elements and recomputes full-ring negativity at t=1,4,400; maximum difference is 1.69e-13, below 1e-10.

`independent-trajectory-L12-J0.json` repeats this for the control. All-period resource difference is at most 4.58e-13; sampled distance difference is at most 1.93e-14. All four saved control negativity samples t=0,1,10,400 are independently recomputed; largest difference is 4.49e-14. The independent values and author values are consistent with the separability prediction within 1e-10.

`independent-trajectory-L10.json` independently checks all 401 L10 resource points (maximum difference 1.09e-15) and the sampled target distances (6.86e-15). It does not recompute additional L10 negativity beyond the small dense check's t=0,1,4. The author record also reports agreement with the earlier external L10 reference; that external file was not opened in this review.

**Limits:** interacting L12 has 13 saved negativity samples; this review independently recomputed three of them, not all 13. No between-sample spectrum or state positivity is inferred from sparse output alone. Positivity of the ideal mathematical map follows from unitary evolution and random-unitary dephasing; the recorded sampled sector minimum eigenvalues are consistent with numerical roundoff. No normalization, projection or positivity repair was found in the code.

At t=400, L12 stored target distance is 4.7965e-15 and negativity 0.9419524091957566. The control instead remains at target distance about 0.26918. These finite-time observations support the README's explicit distinction between numerical agreement and an attraction theorem.

### Target teleportation and documentation

`supplement.json` independently reproduces every exact target extraction field and the entire rational pair state at even sizes 4–30. All bundled provenance import hashes match their declared values. `facts.json` binds reviewed data files and the reviewed README to hashes and checks the L12 pair/fidelity arithmetic and the stated matrix-memory arithmetic. L10 and L16 exact probabilities/fidelities also agree with the README table.

The README's measured times and peaks agree with the stored records: L16 target about 76.31 s / 400 MB; L12 interacting about 78.65 s / 1.50 GB; L12 control about 22.82 s / 1.50 GB. These are decimal memory units as explicitly stated. The 18-spin 24,380-row block and 14-spin 4 GiB full-complex allocation arithmetic are correct. Sampling descriptions match saved rows.

The README's references to pre-existing attraction certificates and prior imperfect-correlation studies are outside this packet's independently reviewed scientific scope; this report neither rechecks nor extends those results. Plots were not visually audited by this reviewer. The target values are numerical spectra, not symbolic exact answers or thermodynamic limits.
