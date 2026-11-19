# Extracting Operational Entanglement from a Noise-Protected Many-Body System

Manuscript, numerical data, and reproduction code for the twelve-spin kicked Ising ring study by Bhavay Tyagi, Eric R. Bittner, and Kevin E. Bassler.

## Reproduce the figures

From the repository root, use Python 3.13.2 with the versions in [requirements.txt](requirements.txt).

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python verification/check_package.py
python scripts/rebuild_figures.py
```

The command writes PDFs, previews, and check receipts under `build/figures/`. The manuscript uses the archived PDFs in [Figures/](Figures/). The rebuild reads saved data and leaves those PDFs and their inputs intact.

| Figure | Command | Python source | PDF under `build/figures/` |
| --- | --- | --- | --- |
| 1. Ring schematic and teleportation circuit | `python scripts/rebuild_figures.py --figure 1` | [compose_candidate.py](scripts/figures/compose_candidate.py) | `fig1/combined_opening.pdf` |
| 2. Logarithmic negativity | `python scripts/rebuild_figures.py --figure 2` | [draw_l12_labeled.py](scripts/figures/draw_l12_labeled.py) | `fig2/negativity_L12_correlations.pdf` |
| 3(a,b). Conditional teleportation fidelity and heralding probability | `python scripts/rebuild_figures.py --figure 3` | [draw_resources.py](scripts/figures/draw_resources.py) | `fig3/xi_resource_L12_all20.pdf` |

Figure 1 uses the archived reservoir artwork and final vector circuit. Its default build needs no image generation or extra system font. For an editable rebuild of the vector circuit, run [draw_labeled_candidate.py](scripts/figures/draw_labeled_candidate.py) in a disposable copy with the licensed Arial Narrow font installed. This optional command overwrites its circuit inputs, and the installed font affects exact rendering. The standard reproduction command uses the supplied circuit PDF with embedded fonts. [Figure 1 provenance](provenance/fig1/)

Figure 2 uses 13 saved logarithmic-negativity samples for each of 20 noise correlations. It plots lines identified by the correlation color bar. Figure 3 uses 401 integer times for each correlation. Panel (a) plots mean teleportation fidelity conditional on successful extraction and panel (b) plots the probability of that extraction. The figure scripts check plotted values against the archived arrays.

## Recompute the numerical data

The [saved sweep](data/xi_sweep/) contains the trajectories used in Figures 2 and 3, run parameters, completion hashes, and the frozen numerical kernels used to produce the data. The portable driver runs the same model with new outputs in a separate directory.

```sh
python scripts/numerics/portable_rerun.py --campaign data/xi_sweep --out rerun-smoke --smoke
python scripts/numerics/portable_rerun.py --campaign data/xi_sweep --out rerun-xi099 --xi .99
```

The first command is a four-spin reference check. The second regenerates the twelve-spin trajectory at correlation 0.99 and includes dense partial-transpose eigensolves. Full trajectories require substantially more memory and time than redrawing the saved data. Use `--all` to regenerate all twenty correlation records. The supplied sweep contains saved observables and diagnostics. New runs also retain terminal density checkpoints. [Campaign documentation](data/xi_sweep/README.md)

## Check the analytical results

- [Cyclic-rank verifier](verification/certificates/verify_cyclic_irreducibility_20260910.py) supports Appendix A. Use `--sizes 12 --prime 1000003` or `--sizes 12 --prime 1000033`.
- [Exact resource checks](verification/exact_resource/independent_checks.py) verify the extracted pair, heralding probability, and fidelity in Appendix B.
- [Saved-data checks](verification/revision2/check_saved_claims.py) check the archived finite-time calculation and its stated scope.
- [Ideal-sector code](scripts/ideal_sector/README.md) documents the separate collective-noise calculation and its original execution layout.

## Build the manuscript

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error letter_prl_revision_2.tex
```

The [Letter source](letter_prl_revision_2.tex) contains the End Matter. The [reading copy](letter_prl_revision_2.pdf), bibliography, and three figure PDFs are included. [MANIFEST.json](MANIFEST.json) records the package hashes. The package check also verifies the frozen sweep’s source and output hashes.
