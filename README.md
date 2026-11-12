# Extracting Operational Entanglement from a Noise-Protected Many-Body System

Repository: [bhavaytyagi/extracting-operational-entanglement-from-a-noise-protected-many-body-system](https://github.com/bhavaytyagi/extracting-operational-entanglement-from-a-noise-protected-many-body-system).

This is the complete **current final-state package**. It contains the manuscript, final figures, editable figure-generation code, all saved numerical data, numerical calculation scripts and the evidence supporting the paper. Older manuscripts, unused renderer variants, duplicate previews and editing-stage records are excluded from the active tree. They remain in Git history and the author's local research archive.

## Manuscript

- `letter_prl_revision_2.tex`: the sole main manuscript, with integrated End Matter.
- `letter_prl_revision_2.pdf`: compiled reading copy.
- `References_revision_2.bib`: current bibliography.
- `Figures/`: exactly the three figure PDFs referenced by the manuscript.
- `latexmkrc`: build configuration.

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error letter_prl_revision_2.tex
python verification/check_package.py
```

The author's latest acknowledgement and commented End Matter AI/check paragraph are preserved verbatim. No historical supplemental manuscript or compatibility wrapper is part of the current paper.

## Figure generation and editable inputs

`scripts/rebuild_figures.py` regenerates all three current figures. `scripts/figures/` contains the actual current renderers and their required circuit-construction primitives. `scripts/figures/circuit_candidate/` contains the final circuit PDF, editable SVG and inventory; the directory's inherited name does not designate an alternative manuscript figure. `circuit_original/` contains the geometry constructor and inventory executed by the current labeled renderer. Removing either would break reproduction.

`provenance/fig1/` contains the ring/reservoir raster, prompt/edit record and foundation PDFs required by the final Figure1 composition. In particular, `combined-before.pdf` is a required composition input, not an older manuscript. `rebuild_schematic.py` and `rebuild_foundation.py` retain the editable construction of the schematic/foundation. Generated previews and superseded full-figure variants are excluded.

Run regeneration in a disposable copy because renderers create intermediate products and audit outputs:

```sh
python scripts/rebuild_figures.py
```

Figure1(a)'s ring/reservoir artwork was generated/edited with image_gen. Labels, curves and the circuit use Python/vector construction. Figures2/3 use the saved numerical data. Reproduction uses the supplied raster and never calls an image-generation model.

## Complete numerical calculations and saved outputs

`data/xi_sweep/` contains all twenty correlation records for the twelve-spin calculation, original campaign configuration/manifest, completion marker, the frozen producer/check scripts, and required regression/reference inputs. All42campaign files are retained. Earlier dated L10 reference records are required numerical regression baselines used by the final checks, not earlier paper versions. Their hashes and the original20-source/20-output closure are immutable.

`scripts/numerics/portable_rerun.py` is the portable driver for the current full-density map. It imports unchanged campaign kernels, checks the frozen closure, writes new runs to a separate directory, and retains new terminal checkpoints. Original campaign provenance/environment gates are not weakened.

`scripts/ideal_sector/` contains the canonical ideal collective-noise calculation kernels underlying the separate ideal-sector reference record. These kernels have their original execution-layout limitations, documented in that directory. Duplicate copies have been removed; they are not a second producer for imperfect correlations.

Use the recorded Python3.13.2 environment and the versions in `requirements.txt`. The author's environment is `/opt/anaconda3/envs/noisy_env/bin/python`; an equivalently provisioned POSIX environment can run the portable interface. Merely compiling the paper requires no numerical simulation.

```sh
python scripts/numerics/portable_rerun.py --campaign data/xi_sweep --out rerun-smoke --smoke
python scripts/numerics/portable_rerun.py --campaign data/xi_sweep --out rerun-xi099 --xi .99
```

The first command is the existing dense four-spin reference check. The second requests a full expensive production curve; use `--all` only deliberately. The saved full-density campaign contains observables/diagnostics, not terminal full-density matrices or complete eigenvalue arrays. The paper's terminal Frobenius distance is from the separate ideal-sector calculation. No missing arrays or newly verified production run are implied.

## Proof, checks and final evidence

- `verification/certificates/`: finite cyclic-rank algorithms and saved outputs.
- `verification/exact_resource/`: exact selected-resource/orbit checks.
- `verification/saved_sweep/`: portable independent saved-campaign checker; its full command also performs additional numerical checks.
- `verification/revision2/`: final independent review, proof/literature/evidence notes and recorded exact/saved-data results. Superseded editing fragments and preliminary review reports have been removed.
- `provenance/scientific-evidence/`: supporting raw reference results and executed final-check evidence. They establish only their recorded scopes; original isolated-review code retains its layout limitations.
- `provenance/source-map.json` and `portable-adapters.json`: retained source origins and portability mapping. Origin hashes describe the source material; `MANIFEST.json` is authoritative for current package bytes.

```sh
python verification/exact_resource/independent_checks.py
python verification/revision2/check_saved_claims.py
python verification/certificates/verify_cyclic_irreducibility_20260910.py --sizes 12 --prime 1000003
python verification/certificates/verify_cyclic_irreducibility_20260910.py --sizes 12 --prime 1000033
```

The final artifact review is `verification/revision2/FRESH_LILLY_REVIEW.md`. Its bounded proof, decoder, source and saved-data acceptance does not establish all-size attraction, asymptotic imperfect-noise usefulness, practical production rates or a fresh full L12 trajectory/eigenspectrum rerun. Packaging cleanup does not promote scientific claims. Broader abstract/title choices remain with the authors.

## GitHub and Overleaf have different contents

GitHub contains this complete current final-state package and **no `old_project/` or `old_paper/` directory**. Overleaf contains only current manuscript compilation dependencies and its separately requested historical manuscript archive. Transfer current manuscript edits and required figures explicitly. Do not pull the full research repository into Overleaf or propagate Overleaf's research-file deletions into GitHub. READMEs differ intentionally.

`MANIFEST.json` covers exactly the current deliverables, excluding itself and build/cache products. `verification/check_package.py` verifies every current hash and the immutable numerical closure and rejects historical manuscript archive directories in this package. Local historical files and earlier receipts are kept outside this directory.
