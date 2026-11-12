# Final independent L12 production review

Reviewer: Luke, GPT-6 Astra High. Date: 2026-11-04.
Decision: **accepted-for-figure-with-finite-scope**.
Critical findings: none. Major findings: none. Minor scientific findings: none.

This is acceptance of the completed twenty-curve production artifact, not a
preflight approval. The reviewed manifest SHA256 is
`b45bbcc00aa4bf601ef90d428f2ea49696e486a79e1e38ee2d9d3c32c96f3e0f`.
All twenty source entries in that manifest, all five independent provenance
origin entries, the manifest binding in the completion receipt, and all twenty
completed output hashes match the isolated packet. Supplementary manifest files
were supplied during review; author check receipts were hashed but not used as
scientific validation. No earlier review report or author reasoning was read.

## Scope and evidence

The accepted data are the full-density L=12 periodic Ising–kick–accumulated-
dephasing map specified in the packet, J=pi/4, b=-pi/4, h=1, gamma=.1, initial
plus product state, the specified twenty xi values including exactly -1/11 and
1, and the balanced first-six/last-six cut. Resources are available at every
integer time 0 through 400: 8020 rows. Natural-log negativity was evaluated by
complete Hermitian spectra at the thirteen scheduled times: 260 evaluations.
The decoder is fixed, alternating-string/complement, with the six-site-half
Phi+ reference. Its probability, conditional fidelity and weighted/fallback
quantities must retain their distinct meanings in the figure.

`check_final.py` independently checks exact output schemas, grids, parameter
identity, finite values, trace/Hermiticity summary bounds, positivity minima,
spectral trace errors, initial-product limits, resource identities and physical
bounds, and balanced-cut negativity/PT spectral bounds. It does not call the
author's row, result or manifest validators. Observed maxima are:

| Check | Observed value | Required limit |
|---|---:|---:|
| Recorded per-period trace error | 3.331e-15 | 1e-10 |
| Recorded per-period Hermiticity error | 2.686e-18 | 1e-10 |
| Recorded density/PT spectral trace error | 2.243e-14 | 1e-10 |
| Most negative density minimum | -1.139e-14 | >= -1e-10 |
| Most negative reported log negativity | -3.331e-16 | >= -1e-10 |
| Recorded peak RSS | 1,336,832,000 bytes | <= 3 GiB |

Tiny negative values within roundoff tolerance are retained without clipping.

Independent numerical work was performed with the existing noisy_env Python,
NumPy 2.1.3 and two BLAS threads:

1. Constructed the L4 dense Ising and kick unitaries from explicit tensor Pauli
   operators, and a 256-by-256 Lindblad generator using the covariance matrix.
   Exponentiated that generator directly. Five repeated steps from a seeded
   generic complex positive density at xi=-1/3,0,.5,.99,1 agree with the frozen
   runner. Independent J=0 product-state controls remain separable with
   conditional fidelity at most 2/3 through forty steps at the same xi values.
   Worst entry error, including controls: 6.941e-16 against 1e-10.
2. Constructed partial transposes with explicit indices and the decoder using
   explicit local Kraus matrices. Compared density/PT eigenvalue observables
   and all resource fields. Checked product, maximally mixed and encoded Bell
   states, including L6's odd-half Bell convention. Decoder discrepancy is at
   most 1.111e-16; tested spectral observables agree to displayed precision.
3. Independently built L12 kicked pure amplitudes using local 2-by-2 gates and
   explicit periodic Ising energies. Applied the covariance quadratic form to
   the decoder submatrix. All twenty actual production t=1 resource rows
   agree; worst discrepancy 3.886e-16 against 1e-10.
4. Independently reconstructed the complete imperfect-correlation L12 state at
   xi=.99,t=1 from those amplitudes and the covariance quadratic form. Computed
   its full density spectrum and full PT spectrum, the latter using an explicit
   block-index transpose distinct from the runner's reshape/transpose path.
   The reference log negativity is 1.3784424458551445; saved negativity differs
   by 4.441e-16. Density/PT minima differ by at most 2.776e-16. Spectral traces
   differ from one by at most 9.993e-16. All are below 1e-10.
5. Compared **every** shared resource field for all 401 xi=1 times and both
   common spectral observables (log negativity and minimum PT eigenvalue) at
   all thirteen times against the frozen ideal baseline. Maximum negativity
   error 7.017e-14, maximum resource error 7.217e-16, maximum PT-minimum error
   3.677e-15: all below the original 1e-9 tolerance. Density minima are not
   compared across spaces: the baseline density is sector restricted whereas
   the new density is full-space and includes extra zero eigenvalues.
6. Recomputed the frozen L10 regressions at xi=.5,.99,1 through t=5, including
   every scheduled spectrum and shared resource field. Worst discrepancy
   1.444e-15 against the original 1e-9 tolerance. Nine invalid-domain cases,
   including L12 xi=-1/9, nonfinite xi and unsupported sizes, correctly raise.

Inspection of the frozen runner agrees with the stated Ising-first, kick-next,
dephasing-last convention. The D-Hadamard-D factorization has the required
positive imaginary kick sign for b=-pi/4, and its two unnormalized Walsh
transforms are compensated by exactly 1/d. The code evolves full densities;
the new imperfect-correlation data do not reuse a reduced ideal sector. No
clipping, state projection or trace renormalization occurs.

## Limits of acceptance

This audit independently recomputes a full actual imperfect L12 spectral point
and small-system maps/controls, and checks all stored production records and
ideal-baseline points. It does not rerun all twenty 400-period trajectories.
The archived JSON contains spectral summaries, not arrays of all eigenvalues
or every intermediate density; late imperfect-correlation physical invariants
are checked as recorded assertions and consistent output summaries, supported
by inspected source and hash binding. Hashes establish artifact consistency,
not by themselves a proof that a calculation occurred.

Acceptance makes no claim about negativity at unsampled times, interpolation,
infinite-time behavior, exact threshold crossings between samples, optimized
teleportation protocols, other sizes, other parameters or thermodynamic limits.
It does not independently re-audit checkpoint crash/restart or concurrent-writer
handling; these are outside the final finite numerical acceptance here. Source
and data tolerances have not been relaxed.

## Reproduction

From the project root:

```sh
/opt/anaconda3/envs/noisy_env/bin/python reviews/l12-final-2026-11-04/reviewer/check_final.py > reviews/l12-final-2026-11-04/reviewer/stdout.txt 2>&1
```

The run completed with exit code 0. `stdout.txt` and `results.json` contain the
executed comparisons. `acceptance.json` binds the production outputs and reviewer
artifacts. After that run, the script was amended only to disable Python bytecode
cache writes before importing the frozen source; an automatically generated
cache was removed. Scientific inputs, numerical checks and results were unchanged.
