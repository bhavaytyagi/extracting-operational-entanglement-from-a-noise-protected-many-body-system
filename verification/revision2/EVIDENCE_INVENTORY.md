# Physics and numerical evidence inventory

Luke, 2026-11-11. **Saved-evidence audit passed; no new scientific-label promotion.** Root owns final integration, independent review, shared records and commit. Manny owns manuscript prose. Joe owns artwork and portable execution. `SPEC.md` preceded new scalar auditing. `LEMMA_NOTES.md` is a self-contained author derivation requiring separate fresh review.

## Findings that constrain the revision

The retained L12 ideal target and extraction numbers have bounded existing independent receipts. The finite full-density correlation campaign has twenty401-point resource curves and260 sampled complete-spectrum negativity calculations. All frozen input/output hashes, parameter bindings, row grids, scalar resource identities, original invariant summaries and ideal exact anchors pass the new read-only audit. No production state or eigenspectrum was recomputed.

The ideal target is separately stationary under each layer, but arbitrary states supported in S evolve. At imperfect xi the averaged map remains dihedrally covariant while support in the invariant-vector sector need not persist. The one-down coherence and W-state witnesses in lemma4 make this precise, including the allowed negative endpoint. These facts do not establish an imperfect-noise asymptotic mixing theorem. Keep that part finite-time scoped.

The old ideal-sector trajectory has a saved t400 Frobenius target distance. The newer full-density sweep does **not** have a saved final density or its own terminal target-distance diagnostic. A broad recursive search finds one NPZ, but its metadata identify a preflight L4,xi=.37,t12,horizon12 resume test, shape16×16; it is not the L12 terminal state. The producer deliberately removes completed checkpoints after writing JSON summaries. Full raw eigenvalue arrays and intermediate matrices are not archived. Honest methods wording can describe complete eigenspectrum evaluation and retained summary records, not an archive containing every eigenvalue or a fresh residual inferred from a plateau.

## Exact model and data binding

Campaign: `numerical_campaigns/xi-sweep-L12-2026-11-03/`. Manifest SHA256 `b45bbcc00aa4bf601ef90d428f2ea49696e486a79e1e38ee2d9d3c32c96f3e0f`. `manifest.json` declares L12,J=pi/4,b=−pi/4,h=1,gamma=.1,Ising→kick→accumulated-dephasing,complex128,site0 most-significant bit,first-six/last-six cut,natural logarithm,2 BLAS threads. It binds20 source/check/provenance files. `progress/complete.json` binds all20 exact output JSON files.

Canonical xi grid: −1/11,−.05,0,.1,.2,.3,.4,.5,.6,.7,.8,.85,.9,.95,.97,.98,.99,.995,.999,1. Resources at every integer t=0,...,400. Negativity only at0,1,2,3,4,5,10,20,40,80,150,250,400. The production run used full4096×4096 densities also at xi1. No sector restriction at imperfect xi.

Original environment in manifest: Python3.13.2,NumPy2.1.3,SciPy1.15.2,macOS26.6.2,x86_64,executable `/opt/anaconda3/envs/noisy_env/bin/python`. These are recorded production versions, not a claim that unrecorded plotting dependencies had identical versions. Plot generation additionally uses Matplotlib and PyMuPDF. No dependencies were installed in this audit.

## Checks actually established and their limitations

| Check | Original tolerance | Recorded result/evidence |
|---|---:|---|
| Trace at each period | absolute error<1e-10 | max3.3306700603864844e-15 |
| Hermiticity at each period | maximum-entry residual<1e-10 | max2.6851967994446385e-18 |
| Density positivity at13 spectral samples/curve | min eigenvalue≥−1e-10 | minimum−1.1380111968688946e-14; preserved roundoff |
| Density/PT spectral trace at those samples | absolute error<1e-10 | both maxima2.2426505097428162e-14 |
| Generic L4 explicit Lindblad reference and J0 controls | maximum-entry state/decoder error<1e-10 | historical independent max state6.940151931578151e-16; no rerun now |
| Independent L12 t1 resources at all20xi | absolute error<1e-10 | max Bell overlap3.885780586188048e-16 |
| Independent full L12 xi.99,t1 spectrum | absolute error<1e-10 | negativity error4.440892098500626e-16 |
| Full-density xi1 versus old ideal-sector baseline | absolute observable error<1e-9 | all401resource rows/13spectral points; max negativity error7.016609515630989e-14 |
| Current saved-record audit | original1e-10; hashes exact |20frozen sources,20outputs,8020resource/260spectral rows pass |
| Current L12 modular cyclicity rerun | exact integer arithmetic | rank224 at1000003 and1000033; J0 cyclic rank13 |

Source/check contract: campaign `SPEC.md`, `scripts/run.py:173–184` (invariants),`:209–233` (spectra),`:252–299` (row schema/bounds),`:349–389` (sampling and summaries). Prior independent scope: `results/xi-sweep-L12-2026-11-04.md`, `reviews/l12-final-2026-11-04/reviewer/REPORT.md`, `results.json`, `acceptance.json`, `check_final.py`. The earlier reviewer did not independently repeat20full trajectories. New audit simply rechecks archived evidence and does not increase that scope.

The fixed-decoder fidelities use Bell Phi+ at L12; they are not the fallback_fidelity field. The saved fallback implements a maximum with zero so a known subthreshold resource can be declined; the exact stationary benchmark has positive advantage so the manuscript's stationary formula agrees. Initial p=1/1024,F=2/3; ideal target p=1/192,F=19/21.

## Terminal residual: exact provenance and norm

`numerical_campaigns/xi-sweep-L12-2026-11-03/provenance/dynamics_L12_xi1.json:3296` records distance_target_frobenius=4.796463671315687e-15 at400. Its immutable origin is `numerical_campaigns/prl-2026-10-29/data/dynamics_L12_xi1.json`, SHA256 `3741dcc40d7d76209078c97b311fe6319e0e316bb9b18b720dffee92f95ac3c5`. `scripts/dynamics.py:114` of that older campaign computes `np.linalg.norm(rho-target)` with target=I224/224 in the **orthonormal** orbit-sum sector basis (`setup`:basis weights1/sqrt(orbit size),orthonormality asserted). Isometric embedding preserves Frobenius norm, so it represents distance to P/224 for that separate ideal-sector computation. It is not a residual measured from the newer full-density state.

The older file also records target_stationarity_residual=1.0408398128305076e-17. Its producer at `scripts/dynamics.py:100` defines this as maximum entry of M(target)−target in the sector basis, **not Frobenius norm** and not a terminal-state distance. The accepted bounded receipt is `results/laptop-campaign-2026-10-29.md`; separate original fresh review is `numerical_campaigns/prl-2026-10-29/review/final/REPORT.md`. That reviewer independently checked all L12 resources and negativity at1,4,400, not every spectrum nor an all-time theorem.

## Finite useful times, not lifetime inference

New classification uses the predeclared threshold F>2/3+1e-10 at integer times only. All intervals are in `saved-audit.json`; selected examples:

| xi | All useful integer intervals in0...400 | F400 | Interpretation |
|---:|---|---:|---|
| .95 |2–34|.5000000012069703|next integer35 is subthreshold |
| .99 |2–178|.5211021528009709|next integer179 is subthreshold |
| .995 |2–358|.6426028775842515|next integer359 is subthreshold |
| .999 |2–400|.8555919881400182|still useful at observation boundary |
|1|2–400|.9047619047619047|finite data consistent with separately proved target |

No interpolation, no monotonic-window theorem, no extrapolation beyond400. At .995,400 the saved EN=.009888097886421723>0 and F=.6426028775842515<2/3, p=.0014793259157734261. This directly witnesses positive ring negativity without advantage for the chosen decoder, leaving other protocols open. At small xi some curves have no useful sampled time; that is not an impossibility theorem for extraction.

## Certificates and exact resource evidence

Minimal rank code: `paper_pipeline/verification/verify_cyclic_irreducibility_20260910.py` imports `verify_closed_form_independent.py` from its own directory; dependencies NumPy/SciPy/standard library. Archival stdout `verify_cyclic_irreducibility_20260910.out` and `verify_cyclic_irreducibility_second_prime_20260911.out` provide all manuscript sizes. First prime covers every3...16; second covers even4...16 plus13,15. Current rerun is L12 only, with exact stdout in this directory. Full rank modular evidence requires no floating tolerance; no all-L inference follows. `LEMMA_NOTES.md` bridges generators to scalar commutant and convergence.

Existing independent L12 block, rational p/f/F, PT eigenvalues, exhaustive64-input CNOT record and both L12 primes: `reviews/prl-comprehensive-2026-11-09/lilly/independent_checks.py` and its output. It uses independently enumerated bit-string orbits and Fraction rational entries; the pair PT float check uses1e-12. Include these as prior independent evidence, not the present author's independent review of the revised manuscript.

## Reproduction closure for the portable package

1. **Figure2 numeric redraw:** `checks/l12-figure2-2026-11-04/joe/draw_l12.py`; shared `notebook/projects/correlated-noise/l12-overnight-2026-11-03/joe/plot_l12.py`; campaign manifest,complete marker,20data records. Preserve path structure or explicitly documented adapter. It uses exact260saved points, marker+segments, numeric xi color normalization, symlog linthresh5. It asserts artist arrays equal saved arrays with zero tolerance. Joe owns any updated figure-specific script.
2. **Figure3 numeric redraw:** `checks/figure3-L12-resources-2026-11-04/joe/draw_resources.py`, same shared validator and campaign inputs. All8020F and8020p cells, equal categorical xi rows; symlog linthresh5. Exact artist receipts `artist-arrays.json`,`figure-checks.json`; zero-tolerance underlying-data transfer. Joe owns final updated graphic sources and Figure1 vector/provenance dependencies.
3. **Original simulation/source evidence:** all20files named by campaign manifest source_sha256 plus manifest,20data,complete marker; include numerical SPEC/KERNEL and full producer, existing numeric checks, frozen comparison sources/data. A machine-readable `dependency-manifest.json` in this directory lists these files and hashes. This closure supports inspection of original production/checks; it is distinct from a portable full-rerun entry point.
4. **Portable simulation execution:** original run.py validates exact executable and Python/NumPy/SciPy versions and original hash-frozen lifecycle before production. It will correctly fail on another installation. Preserve these original bytes; provide a clearly separate portable driver importing the same numerical kernels, checking original hashes/config/tolerances, writing exclusively new results and recording the new environment. Never silently edit or weaken original provenance gates. No all20rerun is needed to validate plotting from archived inputs. Joe/root owns implementation and smoke checks of the portable driver.
5. **Old ideal residual reproducibility:** include older `scripts/dynamics.py`,`scripts/target.py`, corresponding data and scope receipt. `dynamics.run(12)` needs these two files and NumPy/SciPy; its unrelated `reference()` path imports surrounding `paper_pipeline/production_ukui/selected.py`, and its CLI calls that reference by default. A portable adapter should call the intended function and route outputs safely, or include that transitive reference closure; do not advertise the unmodified CLI as self-contained. No ideal rerun was performed here.
6. **Independent final-check executable:** `reviews/l12-final-2026-11-04/reviewer/check_final.py` expects sibling `../input/` holding frozen campaign material. Include that input tree or a separate documented portable adapter. Merely copying the reviewer script without its expected input tree is insufficient. Its saved report/results can be included as historical receipts independently of runnable placement.
7. **Certificates:** two script dependencies plus both archival stdout files, and new L12 stdout. Avoid hauling unrelated research trees into the package. Include bounded receipt/assumptions so coauthors know which arithmetic was actually rerun.

No local evidence establishes that a configured GitHub repository currently contains the whole package, what access it offers, or a human verification procedure. Those are author/access facts. No release promise, DOI or human check should be invented. Historical model attributions are recorded in existing receipts (notably Luke GPT-6 Astra High for the L12 campaign and its separate fresh context; Manny/Lilly GPT-6.1 Sol High for the later PRL review), but such records do not certify an undocumented complete AI provenance chain.

## New commands actually executed

```
/opt/anaconda3/envs/noisy_env/bin/python notebook/projects/correlated-noise/review-package-2026-11-11/luke/audit_saved.py > notebook/projects/correlated-noise/review-package-2026-11-11/luke/saved-audit.out
/opt/anaconda3/envs/noisy_env/bin/python paper_pipeline/verification/verify_cyclic_irreducibility_20260910.py --sizes 12 --prime 1000003 > notebook/projects/correlated-noise/review-package-2026-11-11/luke/rank-1000003.out
/opt/anaconda3/envs/noisy_env/bin/python paper_pipeline/verification/verify_cyclic_irreducibility_20260910.py --sizes 12 --prime 1000033 > notebook/projects/correlated-noise/review-package-2026-11-11/luke/rank-1000033.out
```

All exited0. No manuscript edit, production trajectory, new spectrum, length gate, scientific promotion, upload or independent-review claim occurred. Remaining: Manny integrates appropriate exact prose; Joe implements and smoke-checks portable execution/figure paths; root freezes the complete revised artifact for fresh Lilly review.
