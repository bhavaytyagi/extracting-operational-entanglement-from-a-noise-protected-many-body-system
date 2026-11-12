# Integrated revision2: independent bounded review

Date: 2026-11-11. Reviewer: Lilly (GPT-6.1 Sol High). Artifact: `Working_paper/coauthor-review-2026-11-11/letter_prl_revision_2.tex` and its seven-page PDF, after the figure-environment/negative-space repairs, finite-time abstract-last-sentence correction, factual attribution update, and Fig3 list-break repair.

Reviewed snapshot SHA256:

- TeX: `b523f0ec5e8a31673f3c565d9a75fe73e2624ca27d484e0202f91de0e65766db`.
- PDF: `5bab10481f5219f437182e9efbda4245705e032a76c3c50a8651b7f245dedf7c`.

**Disposition: accepted for the bounded revised argument and coauthor-review package, with the minor/author-owned limitations below. No critical or major scientific inconsistency remains in the revised body/proof/source comparison examined here.** This is not a claim of exhaustive novelty, universal numerical recertification, journal acceptance, or human author approval.

## What was checked

The initial mathematical report `REPORT.md` remains unchanged and checks every numbered proof step against the model and proof specification. For this additional integrated review I read the actual integrated TeX, visually inspected every page of the updated PDF, inspected the direct primary sources for the three new positioning references, compared their Crossref identity records with the new BibTeX entries, inspected the integer certificate producer and saved rank outputs, and directly checked the saved scalar records supporting the added finite-time examples. No historical review was used to settle a claim. Current-package author notes/inventory were used only to locate evidence and formulate questions; conclusions below rely on the artifacts specified.

No full trajectory or spectrum was recomputed. The bounded saved-record check is `check_saved_claims.py`, with its expected checks/tolerances declared in the script docstring before execution. Command:

```
/opt/anaconda3/envs/noisy_env/bin/python reviews/revision2-proof-2026-11-11/lilly/check_saved_claims.py > reviews/revision2-proof-2026-11-11/lilly/check_saved_claims.stdout.txt
```

It exited zero. It verifies the supplied manifest digest, all twenty output digests, 401 resource times and thirteen spectral-record times per curve, the fidelity/Bell-overlap identity, the stated useful-time sets at xi=.99 and .999, displayed rounding of the xi=.995,t400 example, and ideal terminal scalar anchors to absolute1e-12. It establishes consistency and provenance binding of saved records, not the correctness of the production trajectory algorithm or its underlying eigenvalues.

## Mathematical and semantic checks

1. **Attraction proof:** The integrated End matter A carries the reviewed bridges: equality acts first on UF X UF†, conjugation is forward with the correct rotated-spin sign, collective-spin commutation gives the fixed/peripheral descriptions, CP Schwarz plus faithful trace gives X†X fixed, scalarity makes a nonzero peripheral operator invertible, and the polarized eigenvector excludes nontrivial phases. Power boundedness excludes peripheral Jordan blocks. The cyclicity/rank-one-projector argument discharges scalarity at certified finite sizes. No generic ergodicity is assumed in place of an argument. See the full step ledger in `REPORT.md`.
2. **Finite-size inputs now inspectable:** The integrated `verification/certificates/` contains the integer producer, its orbit dependency, and both archival stdout files. The first lists every L=3,...,16 at prime1000003; the second lists L=4,6,8,10,12,13,14,15,16 at1000033, agreeing exactly with the manuscript's dimensions/coverage. The new L12 stdout at both primes is also present. I inspected this source/output evidence, but did not rerun the elimination. The integer flip matrix uses target-representative multiplicities, checks its Gram-weighted symmetry and has explicit computational action checks at small sizes. The modular closure algorithm preserves each joint weight/parity block and checks final closure. No arithmetic overflow concern arises in the displayed validated range: values reduced modulo approximately10^6 and bounded flip multiplicities fit signed64-bit intermediates. This source inspection strengthens access to the rank premise; it is not an independent all-size recertification.
3. **Support versus state invariance:** The integrated body correctly distinguishes sector support, invariance of P/N, and attraction. It does not present S as a noiseless memory for arbitrary supported coherences or a globally unique basin. Its uniform separable input has the required support.
4. **Imperfect noise:** The author artifact `verification/revision2/LEMMA_NOTES.md`4.1–4.3 supplies a checkable narrow witness for the body statement that the old target ceases to be stationary at every allowed xi<1. For two distinct one-down strings, Delta_z has zero sum and squared norm8, giving the dephasing factor exp[-4gamma(1-xi)]<1, including the lower singular endpoint. Their target coherence is nonzero1/(LN); UF already fixes the target, so the full map changes that entry. The W-state mixture likewise witnesses allowed leakage outside the invariant-vector sector without asserting every input leaks immediately. I reconstructed these entrywise calculations and found no gap. They do not prove global mixing or eventual loss of fidelity. The revised body and abstract last sentence now respect that distinction.
5. **Decoder and task:** The physical filter/record mapping and exact4x4 target block remain internally consistent. The input-independent herald, standard teleportation ensemble, all retained Bell outcomes and conditional fidelity/yield distinction are explicit. Repeated resets and ideal pair storage are now acknowledged. Low yield does not invalidate the operational-resource statement. This integrated pass did not rerun the full pair-spectrum calculation.
6. **Noise normalization:** End matter C diagonalizes the coefficient-space covariance correctly, with lambda0=1+(L-1)xi and lambda_perp=1-xi. At xi1, normalized v0 cancels the covariance eigenvalue's L, giving L0=sqrt(gamma)sum Z and the manuscript generator. Dark coefficient directions do not imply arbitrary coherences survive. No factor-of-two/L mismatch was found against the model or proof contraction factor.
7. **Numerical provenance boundaries:** End matter A correctly distinguishes the older ideal-sector Frobenius residual from the newer full-density sweep, whose terminal density and full eigenvalue arrays are not retained. The statement is not smuggled into a claimed full-density residual. The producer explicitly checks trace/Hermiticity and computes complete sampled spectra with the stated tolerances, retaining roundoff rather than clipping. Saved summaries and code support what was done; this review did not reproduce the spectra themselves.

## Primary-source comparison audit

The integrated introduction's three new references are supported by direct local source text. The new BibTeX DOI/title/year/volume/page identities match the supplied Crossref response records. These records establish bibliographic identity, not the scientific content; the content was checked separately below.

- **Buča/Prosen2012:** `manny/literature/BucaProsen2012.txt` lines2367–2374, Appendix Eq.(12), distinguishes individual commutation of the Hamiltonian/jumps from channel-level covariance; Theorem4.1, lines2433–2455, gives invariant operator blocks and diagonal-sector fixed points. Short source quotation at line2438: “each diagonal operator space contains at least one ﬁxed point”. The manuscript uses this as framework and supplies its own stroboscopic proof; it does not pretend the time-independent theorem directly certifies the map.
- **Moharramipour etal2024:** `manny/literature/Moharramipour2024.txt` lines8–16, PDFp1, explicitly treats strongly symmetric unital channels preserving a “global on-site symmetry” and entanglement/distillation of the maximally mixed invariant sector. The abstract and later definition discussion support the current narrow summary. The manuscript distinguishes its spatial permutation action and gives a direct target/filter calculation; it does not import the on-site entanglement classification merely because D_L is non-Abelian. This is a representation distinction, not a proved priority claim.
- **Popp etal2005:** `manny/literature/Popp2005.txt` lines10–12, PDFp1, describes localizing entanglement on average between retained spins by local measurements on the others. The introduction correctly calls the extraction question related, then explicitly allows coherent operations within each half and fixes one heralded branch. It does not claim to compute optimized localizable entanglement or yield.

Manny's `LITERATURE_COMPARISON.md` and `literature/QUOTATIONS.md` are faithful as a **bounded comparison**, with no unsupported first-ever or exhaustive-absence claim. I also checked surrounding source context for the noiseless-subsystem and coherent kicked-Ising comparisons: Knill2000 lines69–86 discusses protected subsystem information, while Bertini2019 abstract lines10–15 concerns exact coherent entanglement for a class of separable inputs. The quoted Knill fragment “the most general method of” is too generic to support a claim in isolation, but the surrounding lines do supply the relevant statement. This is a quotation-ledger quality note, not a manuscript attribution defect.

The combination of spatial preparation and an explicit task may still need a broader primary-source search if the authors want a stronger novelty or PRL-significance argument. This pass does not decide that judgment. The text's present modest “explicit preparation-to-task connection” is consistent with the bounded comparison.

## Saved-record conclusions checked directly

- xi=.99: all sampled useful integer times under F>2/3+1e-10 are exactly2,...,178.
- xi=.999: exactly2,...,400, so the observation is right-censored at400.
- xi=.995,t400: saved EN=.009888097886421723, F=.6426028775842515, p=.0014793259157734261, agreeing with the printed rounded values.
- The ideal saved terminal p and F agree with1/192 and19/21 to absolute1e-12.
- Twenty output files match their supplied exact completion-marker hashes, with8020 resource rows and260 spectral records. This does not turn finite samples into an all-time theorem or determine a physical preparation rate.

## Actual visual outcome, separated from build warnings

Every updated PDF page1–7 was inspected using PyMuPDF renderings in `integrated-rendered/updated-page-*.png`. After the final attribution/list-break changes, changed pages3–7 were inspected again in `integrated-rendered/final-page-*.png`; all seven final page renderings are saved.

- **Corrected:** The earlier Fig1-caption/main-text collision on page2 is gone after removing the inherited negative vertical skip. The two missing figure environment closures are repaired. All three figures are present.
- **Pass:** No clipped equations, missing glyphs, unresolved visible citation/reference markers, overlapping body text, or cropped plot panels were observed. End matter A/B/C are present and readable. The enlarged Fig1 circuit and added Fig2 marker legend are materially easier to inspect.
- **Final minor repair verified:** Page3 Fig3 caption's previously stretched first lines now render normally after allowing breaks in the unchanged xi list. All twenty numerical values are retained. Page2 still places the continuation “blad generator” well below the large float, separated from the preceding-page “Lind-”; awkward, but it is a continuation, not missing text. The final data statement wraps from page4 to page5 without overlap or omitted text. These continuation choices are not scientific blockers.
- **Warning disposition:** A REVTeX deferred-float/stuck warning is reported by the coordinator, but the actual PDF has all three figures in the correct order and no missing content. The warning alone is not evidence of a missing float. I did not run another compilation or alter the source.

No word count, length gate, or journal-fit reduction was used.

## Remaining author-owned or narrow limitations

1. The held abstract still says “average probability” and “viable” and does not attach L12/ideal extraction directly to the quoted figures. These are precision/scope concerns retained for author decision under the hold, not grounds to invalidate the conditional task result. The mathematical success probability is1/192; the mean preparation cost is192.
2. The private-GitHub data statement is an author/access fact, not something established by local scientific artifacts. No repository-access or publication guarantee was inferred here. The package now makes the local evidence inspectable.
3. Final acknowledgment/methods wording now distinguishes earlier Astra assistance, current Sol revision/checks in separate contexts, and Codex coordination/integration. It does not invent a human verification history or claim these checks extend finite bounds. These descriptions are consistent with the documented current activities; the authors remain responsible for confirming the factual tool/version history. Final pages4–7 were inspected after this update.
4. Actual output/source inspection is narrower than rerunning all simulations/ranks. This report must not be cited as a new full numerical recertification, thermodynamic theorem, hardware demonstration, novelty verdict or journal approval.

Subject to those limits, the reviewed integrated argument is internally consistent and sufficiently documented for coauthor assessment. Any later scientific wording change should receive a targeted check; purely mechanical rebuilds should be visually checked for recurrence of the corrected collision.
