# Twelve-spin twenty-correlation sweep: predeclared numerical contract

Author: Luke (GPT-6 Astra High), 2026-11-03. Status: unverified preparation;
production requires fresh artifact-only review and root authorization to launch.
The author explicitly selects L12 and permits an overnight calculation.

## Given

1. L=12 spins on a periodic ring, computational site0 the most significant bit,
   Z=diag(1,-1). Period and dissipative interval1. Initial rho=|+><+|^12.
2. J=pi/4, b=-pi/4, uniform h=1, dephasing gamma=.1. Each step applies
   exp(-i sum(J Z_j Z_(j+1)+h Z_j)), then exp(-i b sum X_j), then the exact
   accumulated dephasing channel. No continuous-noisy-Ising substitute.
3. Complete-graph covariance Xi has diagonal1, off-diagonal xi. Grid:
   [-1/11,-.05,0,.1,.2,.3,.4,.5,.6,.7,.8,.85,.9,.95,.97,.98,.99,.995,.999,1].
   The negative endpoint is exactly evaluated as -1/11; L10's -1/9 is invalid.
4. Compute the full mixed-state density matrix at every correlation, including
   xi=1. No restriction to the invariant-vector dihedral sector at imperfect xi.
5. E_N=ln ||rho^(T_A)||_1, A=first6 sites, B=last6. Exact complete Hermitian
   eigenspectra at times [0,1,2,3,4,5,10,20,40,80,150,250,400]. Resource
   probability and fixed conditional teleportation fidelity at all times0..400.
6. Extraction is the previously reviewed alternating-string/complement local
   coherent decoder. For six-site halves its Bell reference is Phi+. Preserve
   the prior definitions of probability, overlap and F=(1+2 overlap)/3.

## To deliver

Twenty immutable completed per-curve JSON records, 8020 resource rows and260
spectral evaluations; an inspectable resumable runner, progress heartbeat and
actual resource benchmark. Uncomputed negativity entries stay absent. No fits,
interpolation presented as spectra, asymptotic claims, clipping, renormalization,
or density projection. Results remain provisional pending final independent
review. Root owns manuscript/figure integration and shared institutional logs.

## Checks written before implementation

- Generic complex positive L4 matrices versus independently assembled dense
  Ising/kick and full Lindblad exponential, xi=-1/3,0,.5,.99,1: maximum
  entry error <1e-10. Same tolerance for direct-index PT and decoder checks.
- Invalid xi including -1/9 at L12, NaN/infinity and sizes must raise.
- Product and maximally mixed states: E_N=0 within1e-10. Encoded Bell
  state: E_N=ln2, p=1, F=1 within1e-10. L4 J0 controls at the negative
  endpoint,0,.99,1 stay E_N=0 and F<=2/3+1e-10 through40 periods.
- Reproduce old full L10 xi=.5,.99,1 short trajectory resources and scheduled
  spectra (through5) against frozen data: absolute error <1e-9. Generic mixed
  L10 one-step equality to old full implementation: entry error <1e-10.
- L12 xi=1 full-space selected points t=0,1,4 (full state evolution;
  resource comparisons every time through4) against frozen reviewed ideal data:
  absolute resource and negativity error <1e-9. Later production compares all
  common ideal times and401 resource records against that same baseline.
- Every period: finite density, trace1 and maximum Hermiticity residual <1e-10.
  Every scheduled spectrum: density minimum >=-1e-10, density and PT spectral
  traces1 within1e-10. Initial negativity absolute value <1e-10. No repairs.
- Resume versus uninterrupted small trajectory: identical rows and density
  bytes, with a deliberate stop/restart, including restart at a spectral time.
  Refuse corrupted checkpoints and changed config/source manifest; refuse a
  second concurrent writer. Atomic replace for all mutable checkpoint/status
  files; immutable completed output (existing values are checked, never replaced).
- Real L12 benchmark measures setup, steps, density+PT exact spectra, checkpoint
  IO and peak resident memory under2 BLAS threads. Initial memory ceiling3GiB;
  any change requires measured justification on the16GiB machine. No concurrent
  heavy processes; no20-curve production before review and resource acceptance.

## Input provenance

The reviewed full map is numerical_campaigns/xi-sweep-2026-10-30/scripts/sweep.py;
its SPEC.md, review/fresh/REPORT.md and results/xi-sweep-2026-10-30.md establish
prior scope. L12 ideal reference is numerical_campaigns/prl-2026-10-29/data/
dynamics_L12_xi1.json, with results/laptop-campaign-2026-10-29.md and its review.
Copied source/data and exact SHA256 hashes will be frozen in provenance and
manifest.json before review. These references are regressions, not independent
validation of the new runner. The fresh reviewer receives only this packet.

## Preflight review amendment — 2026-11-04

Fresh reviewer found major incomplete-row validation on restart/skip. The
first frozen review packet and reproducer remain in review/preflight/input and
review/preflight/reviewer. Closure requires complete exact row-field schemas,
finite/nonnegative invariant summaries, probability/overlap/fidelity bounds,
F/weighted-advantage/classical-fallback identities, initial plus-product
limits, and spectral bounds at tolerance1e-10, enforced on both checkpoint
histories and completed outputs. New systematic corruption tests must pass.
For the balanced cut E_N<=ln(2^(L/2)): trace-norm<=sqrt(2^L) times the
Hilbert-Schmidt norm, PT preserves that norm, and a density matrix has norm<=1.
Density/PT minimum eigenvalues cannot exceed their trace average; the negative
PT minimum magnitude cannot exceed total negative mass (exp(E_N)-1)/2, with
the same roundoff tolerance. No new trajectories or altered tolerances.

Root selects execution order reversed from the canonical ascending grid: xi=1
first (including full401-point/13-spectrum frozen-ideal regression), then .999
down to -1/11. This prioritizes useful curves and full ideal validation without
changing any requested grid point, observable or output filename.
