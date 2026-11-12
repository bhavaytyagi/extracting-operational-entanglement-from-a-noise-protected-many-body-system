# Coauthor review package — revision 2

This directory is the active review package. The earlier manuscript and research workspace remain preserved separately. Main source: `letter_prl_revision_2.tex`; bibliography: `References_revision_2.bib`; compiled review copy: `letter_prl_revision_2.pdf`. The tiny `letter_Working_doc.tex` wrapper supports the existing Overleaf main-document setting. It loads revision2; it is not a second manuscript.

## Build and read

Use TeX Live with REVTeX4.2, physics and standard AMS/hyperref packages:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error letter_prl_revision_2.tex
```

`latexmkrc` selects that source by default. End Matter is included in the same source. Historical Supplemental Material is not an additional current submission document. The earlier original remains in the workspace/remote archive; its results must not be conflated with this revision.

## Contents and provenance

- `Figures/`: three actual manuscript figures.
- `scripts/figures/`: editable Python renderers, vector circuit and schematic construction, plus rendering receipts. `scripts/rebuild_figures.py` rebuilds the final versions from packaged inputs.
- `data/xi_sweep/`: complete twenty-correlation twelve-spin saved observables, original manifest, completion marker, source-code closure and frozen comparison inputs. Source/observable hashes are immutable. Original producer retains its original environment gate.
- `scripts/numerics/portable_rerun.py`: separate portable execution adapter importing unchanged checked kernels. It records a new environment, writes to a new directory, retains final checkpoints and compares new observables against archived data. It does not weaken or rewrite the original producer's provenance gates.
- `scripts/ideal_sector/`: earlier ideal-sector kernels and explicit execution-scope note.
- `verification/`: exact finite-size rank scripts/outputs, selected-pair checks, saved-data checks and revision2 review evidence. A saved review receipt is evidence of its stated bounded checks, not a new independent recertification of every trajectory.
- `provenance/`: original figure sources, AI artwork prompt/edit records, historical source mapping and historical scientific evidence. The source map records original hashes; MANIFEST.json gives the definitive current package hashes. Original sources may retain historical workspace paths; runnable portable adapters are in `scripts/` and `verification/saved_sweep/`.

Figure1(a)'s ring/reservoir raster was generated/edited with image_gen. Its prompt, edit record and final raster are supplied. Labels, curves and circuit are composed by Python/vector code. The numerical Figure2/3 data are not AI-generated illustrations. Regeneration starts with the archived raster; it does not rerun an image model.

## Reproduce figures and bounded checks

The portable numerical producer supports POSIX/macOS/Linux (Windows users need WSL), because the unchanged kernel imports POSIX lifecycle modules. The recorded Python is3.13.2. Package versions are pinned in `requirements.txt`. The established project environment is `/opt/anaconda3/envs/noisy_env/bin/python`; substitute an equivalently provisioned Python on another machine. No installation or expensive numerical campaign is needed merely to compile/read the paper.

Run figure regeneration in a disposable copy because it updates figure files/receipts:

```sh
python scripts/rebuild_figures.py
python scripts/numerics/portable_rerun.py --campaign data/xi_sweep --out rerun-smoke --smoke
python verification/certificates/verify_cyclic_irreducibility_20260910.py --sizes 12 --prime 1000003
python verification/certificates/verify_cyclic_irreducibility_20260910.py --sizes 12 --prime 1000033
python verification/exact_resource/independent_checks.py
```

The smoke check is a dense four-spin Lindblad reference, including independent, collective and anticorrelated cases; it is not a twelve-spin production rerun. The saved-data independent checker `verification/saved_sweep/check_final.py` includes additional explicit small-system/dynamical calculations and writes results beside itself; its only adapter change redirects the input root to packaged `data/xi_sweep`. See its docstring for predeclared tolerances. No full campaign was rerun to assemble this package.

A new full curve is optional and expensive:

```sh
python scripts/numerics/portable_rerun.py --campaign data/xi_sweep --out rerun-xi099 --xi .99
```

Use `--all` only deliberately. The original full-density campaign retained observables/diagnostics rather than terminal density matrices or full eigenvalue arrays. The quoted terminal Frobenius distance belongs to the separately archived ideal-sector run, not the full-density sweep. No asymptotic imperfect-noise theorem or all-size attraction theorem is claimed.

## Review status

The correction ledger and fresh review receipts are collected under `verification/revision2/`. Title and the broader abstract revision are separate author-taste work; any minimal abstract consistency correction is explicitly recorded. Human coauthor review of significance and provenance remains distinct from automated mathematical/data checks.

`MANIFEST.json` inventories deliverable files and SHA256 hashes (excluding itself, caches/build products). Use `python verification/check_package.py` to check it after download. Remote history is preserved before migration; `old_project/` is historical and is not part of the active package or a dependency of its manuscript.

Final independent artifact review: `verification/revision2/FRESH_LILLY_REVIEW.md`. Its code/stdout/hash records are archived under `provenance/scientific-evidence/revision2-fresh/` with their isolated-layout scope note; the portable reproduction commands above remain the runnable package interface.
