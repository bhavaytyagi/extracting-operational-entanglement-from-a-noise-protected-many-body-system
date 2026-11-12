# Ideal collective-noise reference calculation

These are the canonical unchanged calculation kernels underlying the final paper's separate ideal-sector reference. The reference output is `../../data/xi_sweep/provenance/dynamics_L12_xi1.json`. Duplicate kernel copies are excluded from the final package.

The original CLI and `dynamics.run(12)` expect the original output-directory layout; they are supplied for inspection and are not advertised as portable entry points. Do not run them in place. This reduction is valid only for ideal collective noise and must not be used for imperfect correlations. The current portable full-density driver is `../numerics/portable_rerun.py`; it writes to a new output directory and preserves the original selected-map kernels and numerical checks.

The stated Frobenius distance belongs to this separate ideal-sector reference, not to a retained terminal density matrix from the full-density sweep.
