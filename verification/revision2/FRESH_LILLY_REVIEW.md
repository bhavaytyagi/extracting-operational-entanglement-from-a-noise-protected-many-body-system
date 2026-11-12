# Independent final artifact audit — Lilly — 2026-11-11

**Verdict: no unresolved critical or major challenge in the bounded scopes below.**
Status: `agent-verified` for this artifact audit, by Lilly (GPT-6.1 Sol, High).
This is an independent review of the actual paper and supplied primary/data/code
artifacts, not an audit of another review. I read no project handoff, worklog,
earlier review, author rationale, or other agent's scientific reasoning. After my
independent first result, a narrowly identified numeric-record attribution was
resolved using the separately hashed raw supplement described below.

## Frozen artifacts and executed evidence

All 64 entries of `input/INPUT_HASHES.json` matched exactly. In particular:

| Artifact | SHA256 |
|---|---|
| `letter_prl_revision_2.tex` | `b523f0ec5e8a31673f3c565d9a75fe73e2624ca27d484e0202f91de0e65766db` |
| `letter_prl_revision_2.pdf` | `5bab10481f5219f437182e9efbda4245705e032a76c3c50a8651b7f245dedf7c` |
| `References_revision_2.bib` | `a9d4c21d64a0e7c4c3c6c36ff77595ccb8c4b405d7ab979adcefb8dd6f550846` |
| `Figures/combined_opening.pdf` | `64bb262ef9d13ceaa27be6c2d81754a6448bc63bd97205d892a87bc4587698eb` |
| `Figures/negativity_L12_correlations.pdf` | `e482026d2437469caf3d57b0a9b29ae12a73f13e4e2938a8ca1f368e9d4fa1ea` |
| `Figures/xi_resource_L12_all20.pdf` | `6ae75d56e473e3794afbda28869d4ed46ae711fb07caeb493346cfddffaf6940` |

Commands actually run from the project root:

```
/opt/anaconda3/envs/noisy_env/bin/python reviews/revision2-final-fresh-2026-11-11/reviewer/independent_checks.py > reviews/revision2-final-fresh-2026-11-11/reviewer/independent_checks.out 2>&1
/opt/anaconda3/envs/noisy_env/bin/python reviews/revision2-final-fresh-2026-11-11/reviewer/record_attribution.py > reviews/revision2-final-fresh-2026-11-11/reviewer/record_attribution.out
```

Both exited zero. Code and full stdout are alongside this report. Floating
comparisons were predeclared at absolute tolerance `1e-10`, except the archived
ideal-versus-full observable comparison at `1e-9`; hashes, Fraction arithmetic,
integer ranks, row indices and useful-time sets were exact. The first script was
extended to check explicit teleportation after its initial successful run, then
rerun successfully. No heavy production trajectory, full L12 eigenspectrum,
length gate, or word-count operation was run.

## Argument audit

1. **Conventions and stationarity.** TeX36–60,132,145–151 consistently specify
   Ising → kick → accumulated dephasing, `Z=diag(1,-1)`, `J=pi/4`, `b=-pi/4`,
   uniform `h=1`, `gamma=.1`, site zero as most significant bit, first-half
   partial transpose, and natural logarithm. The Gaussian convention gives the
   matrix-element multiplier `exp[-gamma/2 * delta_z^T Xi delta_z]`, agreeing
   with the producer's `-.05*(4*(1-xi)*Hamming+xi*delta_M^2)`. There is no
   missing factor of two or collective factor of L. Group averaging is an
   orthogonal projector; commuting coherent layers and collective jump make
   its normalized density stationary, without making every supported density
   noise-invariant. The text makes that distinction explicitly.
2. **Peripheral characterization, TeX134–139 / Eq.(9).** For gamma>0 the
   Hilbert–Schmidt equality condition indeed removes all unequal-magnetization
   blocks. Thus `E(Y)=Y=lambda X`, and both X and Y commute with Jz. Because
   UI commutes with Jz, conjugation supplies commutation with
   `UK Jz UK† = cos(2b)Jz - sin(2b)Jy`. At the stated nonzero sine this gives
   all collective-spin commutators, hence UK commutation and the remaining
   UI-eigenoperator relation. The converse is immediate. The polarized vector's
   one-dimensional weight space gives Xv=cv; the UI eigenoperator relation
   then forces c=0 for lambda!=1. No unjustified claim that the full global
   fixed algebra is scalar occurs.
3. **Convergence, TeX141.** In the invariant sector, complete positivity,
   unitality and trace preservation make Schwarz's positive difference have
   zero trace. Consequently X†X is fixed. Conditional scalarity makes a
   nonzero peripheral X invertible, contradicting Xv=0 at lambda!=1. Bounded
   powers exclude nontrivial Jordan blocks on the unit circle. The result is
   ordinary convergence of every supported density, rather than only a Cesaro
   statement. Applying the global argument to a sector operator is legitimate:
   all generators preserve the sector and its orthogonal complement, so the
   operator may be extended by zero. There is no hidden assumption of a
   globally unique stationary state.
4. **Finite certificate and its implication, TeX143.** Periodic even domain
   wall number yields `UI=e^(-i*pi*L/4) R e^(-i*2hJz)`. Therefore R and joint
   weight/R projectors belong to the generated algebra. Cyclicity alone need
   not mean irreducibility, but here the explicitly available polarized rank-one
   projector q completes the argument: every commutant operator has Cv=cv and
   acts as c on every Av, which spans the sector. This is a valid scalarity
   proof. I independently constructed binary dihedral orbits, integer flip
   blocks and block Krylov elimination; full rank modulo **1000033** was
   obtained freshly for **every L=3..16**, with dimensions
   `4,6,8,13,18,30,46,78,126,224,380,687,1224,2250`. I did not import the
   supplied rank implementation or orbit builder. Full modular rank certifies
   a nonzero integer minor over C. Products used in int64 elimination stay far
   below overflow. These checks establish finite-size scalarity, not an
   all-size theorem or a relaxation-rate bound.
5. **Imperfect correlations and covariance, TeX51–53,83,177–239.** The two
   covariance eigenvalues and their multiplicities are correct, including both
   endpoints. At xi=1 the normalized eigenvector cancels the apparent L factor.
   For xi<1 the target has positive equal-weight off-diagonal orbit entries
   connecting distinct strings. Their collective contribution vanishes but
   the strictly positive `(1-xi)*||delta_z||^2` damps them, so the same target
   is not stationary. Covariance under dihedral permutations does not preserve
   support in the invariant-vector sector. An independent dense L4 calculation
   confirms target change and positive sector leakage at `-1/3,0,.5,.99`, and
   stationarity/support at 1. This does not settle any alternative attractor
   or useful-resource asymptotic at imperfect noise; the paper disclaims those.

## Physical decoder and task

The five CNOTs coherently send both six-bit accepted strings to the same measured
record `10101`, retaining their first-bit distinction. Thus the stated local K is
the actual physical successful Kraus map. I checked the exact dihedral orbits by
independent enumeration: 224 L12 orbits; selected same-half strings share an orbit
of size 2 and crossed strings another of size 12. Exact Fraction arithmetic gives
the displayed Eq.(12), `p=1/192`, `f=6/7`, and `F=19/21`. The partial-transpose
eigenvalues are `-5/14,5/14,1/2,1/2`, as stated.

I also independently simulated all four Bell-measurement outcomes and all Pauli
corrections on the accepted target and three generic mixed two-qubit states.
A uniform six-state spherical 2-design gives exactly the pure-input mean needed
here, and agrees with `(1+2<Phi+|r|Phi+>)/3` within `1e-10`. This is a check of
the specified standard protocol; it does not assume Bell-diagonal arbitrary
trajectory pairs, optimize a fully entangled fraction, or postselect the
teleportation outcomes. The circuit's CNOT controls/targets and correction wires
agree with this protocol when inspected at enlarged resolution.

The extraction precedes supplying the input, so the classical `2/3` benchmark is
appropriate for accepted attempts. The one-attempt fallback expression evaluates
to `2/3+5/4032`; independent resets cost 192 preparations on average. Actual gate
errors, durations, waiting-pair storage and rate are explicitly idealized at
TeX115; the finite probability is not presented as a measured device rate.

## Numerical evidence and its limits

- Exact manifest closure: every frozen producer/provenance/check hash matched.
  The twenty xi values, all 401 resource rows per curve, thirteen spectral times
  per curve and the stated model parameters match the manuscript.
- I independently verified 8020 probability/overlap/fidelity/weighted-advantage/
  fallback identities, bounds and plus-input limits, and 260 saved spectral
  diagnostic bounds/trace checks. No saved value was repaired or clipped.
- Fresh dense L4 one-step comparisons at five correlations, including both
  endpoints, give maximum matrix-entry discrepancy `2.102e-17` from the actual
  frozen production kernel. This checks the elementary map and its conventions,
  not a fresh recertification of the long L12 trajectories.
- At the paper's exact threshold `F>2/3+1e-10`, useful saved integer times are
  exactly 2..178 for xi=.99 and 2..400 for xi=.999. Right censoring is correctly
  stated. At xi=.995,t=400 the saved values are
  `EN=.009888097886421723`, `F=.6426028775842515`,
  `p=.0014793259157734261`, agreeing with the rounded example.
- Full saved xi=1 data versus the distinct frozen ideal-sector reference agree
  at all common times: largest probability error `3.643e-16`, Bell-overlap
  `7.217e-16`, fidelity `5.552e-16`, negativity `7.017e-14`, all below `1e-9`.
  The ideal-sector saved final Frobenius residual is `4.796463671315687e-15`.
  TeX151 correctly attributes it to that reference and explicitly does not
  call it an archived terminal-density residual of the full sweep.

The final density matrices and full eigenvalue arrays are absent. Therefore the
saved-row checks cannot newly prove every density remained positive, reconstruct
all spectra, or independently regenerate every reported trajectory. These are
saved-record consistency and bounded-kernel checks, together with the separate
exact target/algebra proof. The paper's numerical description states this archive
boundary honestly.

I initially could not attribute the exact `6.95e-16` recorded-comparison bound in
TeX151 to the main packet's `author-small.json`. A raw supplement was then added
inside the isolated input directory, without changing the original hashes.
`supplemental-numeric-evidence/results.json`, SHA256
`7372d968a3e72c9743b1167466ce2f14ae81b9fec54af53cec0cca23c3c22722`, records
`max_state_error=6.940151931578151e-16` and
`max_decoder_error=1.1102230246251565e-16`. Its `check_final.py`114–185 defines
the explicit dense Lindblad/decoder comparisons underlying those fields; code
SHA256 is `b9cc5e5b9adfe27b9cb80e10272680273efde9f82921954c5c7174244c686adb`.
I checked hashes and attribution, but did not rerun that supplemental script or
adopt its other results as fresh checks. This resolves the attribution challenge.

## Primary-source comparison audit

These were checked in the actual supplied primary texts, rather than relying on
memory or the bibliography's own claims:

- `BucaProsen2012.txt`2363–2373 defines weak versus strong symmetry;
  2426–2456, Theorem 4.1, gives invariant operator sectors and at least one fixed
  point per diagonal sector: “each diagonal operator space contains at least one
  fixed point”. This supports TeX26's sector statement; it does not independently
  prove this paper's convergence, which is separately supplied.
- `Moharramipour2024.txt`8–15 explicitly says “preserves a global on-site
  symmetry”. Results 2–3 at 422–485 give mixed invariant-sector entanglement and
  a distillation strategy; III.1 at 867–875 explicitly uses on-site symmetry.
  Thus the text's restrained statement that such states *can* be entangled and
  have distillable entanglement is supported. Its spatial-permutation symmetry
  distinction at TeX34 is real, and the paper does not import the on-site
  theorem to establish the dihedral state's entanglement.
- `Popp2005.txt`182–232, Sec.II.A / Eqs.(1)–(2), defines the optimized average
  localized entanglement and specifies that measurements are “on individual
  spins”. TeX26 correctly says related to localizable entanglement and explicitly
  states the wider allowed coherent half-ring operations and lack of yield
  optimization. It does not claim to evaluate Popp's optimization.
- `Horodecki1999.txt`514–565, Eq.(30) and the classical benchmark discussion,
  supports the singlet-fraction/fidelity relation and `2/(d+1)`. That source uses
  F for singlet fraction and f for fidelity; the manuscript uses the opposite
  names but explicitly defines them. Its optimized theorem was not mistaken
  for proof that this fixed decoder is optimal. The direct protocol check above
  additionally establishes the precise fixed-reference relation used here.
- `Bertini2019.txt`270–291 / Eqs.(4)–(5) gives
  `|J|=|b|=pi/4`, with the same selected signs and arbitrary longitudinal fields.
  Its opening text and relevant sections concern exact coherent entanglement
  dynamics. `Zanardi1997.txt`11–17 and `Knill2000.txt`23–29 support the collective
  coupling/noiseless-code background. No noisy stationary or imperfect-noise
  robustness claim is inferred from coherent duality or those code results.

The three new Crossref JSON DOI/title records match the corresponding Buča–Prosen,
Moharramipour and Popp BibTeX entries. This is not an independent verification of
every legacy reference: in particular no separate Bertini2018 primary text was
in the packet. No significance, novelty or PRL editorial judgment is certified.

## Actual PDF inspection and remaining minor observations

I rendered and visually inspected **all seven final PDF pages**, using emitted
images `renders/page-1.png` through `page-7.png`, plus an enlarged rendering of the
actual first figure, `renders/figure1.png`. Text extraction alone was not used as
layout acceptance. Equations, matrices, references, figure captions, axes, color
bars, End matter and margins have no visible clipping or overlap. Figure 3's
nonuniform xi spacing is explicitly described as equally spaced rows; its time
cells and mixed linear/log axes are explained. The first figure is clearly
identified as schematic where appropriate.

Minor observations, not blocking:

1. The data-availability sentence breaks between p4's “re-” and p5's “tained”.
   This is visually awkward but readable.
2. Figure 1's circuit labels are small at final single-column scale. Enlarged
   artwork is legible; the protocol is also completely specified in the text.
3. Page 5 has substantial whitespace around the references before the explicit
   End matter page break. This is a layout observation, not a length/journal-fit
   assessment or a recommendation to shorten anything.

No critical/major challenge remains in the stated artifact/proof/decoder/saved-
record/primary-comparison/layout scopes. Finite-time data, finite-size algebra,
absent terminal densities, implementation-rate assumptions, and unaudited legacy
references retain the limits stated above.
