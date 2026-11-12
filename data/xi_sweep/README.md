# L12 correlation sweep through400 periods

Author: Luke (GPT-6 Astra High), 2026-11-03. Status: **unverified numerical
preparation** until fresh preflight review; future output remains provisional
until independent final review. No manuscript, figure or previous campaign is
modified. The author selects12spins and20correlations and permits overnight work.

Start with SPEC.md (conventions, scope and predeclared tolerances), KERNEL.md
(exact kick factorization), scripts/run.py (map and operational guarantees), and
checks/*.json plus corresponding stdout logs. Those files and copied source/data
fixtures are bound by immutable manifest.json. The manifest deliberately omits
mutable progress/data/review outputs. Do not edit frozen files after approval.

## Numerical method

The full4096x4096 complex128 density matrix is used at every xi. Ising phases,
exact local kicks and the complete-graph correlated-dephasing mask are applied
in the selected order. The kick uses the exact D-H-D identity at b=-pi/4 to reduce
array multiplication; no state-space reduction or truncation is performed.
Dense Hermitian eigensolvers compute complete density and physical first-six-site
partial-transpose spectra at13specified times. The output retains spectral
summaries (negativity, minima and trace errors), not all eigenvalue arrays.
The fallback_fidelity field explicitly chooses the classical fallback when the
fixed protocol offers no advantage; raw probability, conditional fidelity and
weighted advantage are retained without clipping. Resource metrics use the
previously reviewed fixed alternating-string/complement
local coherent decoder and Phi+ reference appropriate to six-site halves.

The initial unchanged local-gate benchmark took approximately8s/step and projected
20hours. Its measurements remain in checks/benchmark.json. The separate Walsh
trial and full entrywise/sustained checks are retained in checks/walsh-trial.json
and checks/L12-kernel.json. The latter is the selected-kernel resource estimate;
projection is not a guarantee against changing laptop load. The3GiB memory
ceiling remains enforced; run only one heavy process. Thread environment caps
OPENBLAS/OMP/MKL/VECLIB at2 before NumPy or SciPy is imported.

## Launch and resume (root owns detached launch)

Use /opt/anaconda3/envs/noisy_env/bin/python. From the repository root:

```
/opt/anaconda3/envs/noisy_env/bin/python numerical_campaigns/xi-sweep-L12-2026-11-03/scripts/run.py all --approval numerical_campaigns/xi-sweep-L12-2026-11-03/review/preflight/approval.json
```

The fresh reviewer/root supplies approval.json only after no critical/major
preflight issue remains and resource feasibility is accepted. Its exact schema:

```
{"status":"accepted-for-production","manifest_sha256":"SHA256 of campaign/manifest.json"}
```

Execution follows manifest.config.execution_order: xi=1 first, then .999 down
to -1/11. The canonical plotting grid remains ascending and unchanged. Full
ideal-baseline agreement is therefore checked before imperfect curves begin.

Rerun the identical command to resume. A nonblocking OS writer lock refuses a
second process. Every saved source/fixture hash and numerical environment must
match the immutable manifest before production or resumption. Existing completed
curve files are checked against complete row schemas, finite invariant summaries,
resource algebra, initial known-state values and spectral bounds before skipping.
The same requirements govern checkpoint histories. Their names are data/L12_xi{xi:.9f}.json.
Existing completed output is never overwritten; partial curve output is never
presented as completed.

progress/checkpoint.npz contains the exact complex128 physical density, its
SHA256 and metadata (curve/time, manifest fingerprint, all completed rows and
invariant maxima). It is atomically replaced after every10periods, each of the13
spectral times, and the final time. Maximum lost nonspectral work on abrupt
termination is9steps. Completed output is atomically created before checkpoint
removal; restart validates and cleans up the checkpoint if interrupted between
those operations. A later curve's checkpoint is preserved while skipping earlier
completed output. A bad/incompatible checkpoint fails loudly. Successful output
removes its temporary full density state to avoid accumulating20large matrices.
No clipping, normalization, symmetrization or positivity projection is applied.

progress/status.json is atomically refreshed before each step, each density/PT
eigensolver, each checkpoint write, and after each period/curve. It includes
UTC time, PID, current xi/time/stage and peakRSS. Normal measured operations
between updates are below60seconds; use OS PID checks to distinguish a busy
native eigensolver from a dead process. Root's external monitor must not run a
second heavy computation. Errors are recorded in progress/error.json and raised.

progress/complete.json is created only after all20completed curves validate. It
contains manifest_sha256, output_sha256 mapping all20relative filenames to their
hashes, counts curves=20/resource_rows=8020/spectral_rows=260, completed_utc, and
status="production-complete-pending-independent-final-review". It is not a
scientific verification receipt. Each curve records L,xi,J,b,h,gamma,horizon,
negativity_samples,401rows and invariant maxima. Only13rows contain
log_negativity_nats; other values are deliberately absent. Figures must use
actual samples and retain the finite-time qualification.

## Reproduction checks

Each of these commands is serial and owns the same OS lock:

```
python scripts/checks.py small
python scripts/checks.py l10
python scripts/check_l12_kernel.py
python scripts/checks.py l12
```

Use the specified interpreter, not an arbitrary python. The first checks dense
L4 Lindblad exponentials, explicit-index PT, known states, J0controls, exact kick
identity, repeated generic mixed states and operational restart safeguards. The
second compares the generic L10map and all time0..5 resource/spectral values at
xi=.5,.99,1 against frozen old data. The third compares every entry of a generic
full-rank L12 mixed-state step to the original kernel, checks the L12 negative
endpoint, and measures10sustained selected steps, exact spectra and checkpointIO.
The fourth compares full-space L12 ideal evolution with the frozen established
ideal-sector baseline: every resource point0..4 and negativity at0,1,4. Production
also compares the complete401-point ideal trajectory and13spectral values to
that baseline before its curve can be accepted.

Rerunning author checks after freezing overwrites timing-bearing check files and
will intentionally invalidate manifest hashes. A fresh reviewer should save
independent outputs only inside review/preflight/ or another separate review
directory. If code fixes are required, preserve the old manifest and review,
then explicitly freeze a new manifest and repeat review before production.

## Limits and pending work

Preflight verifies implementation and operational feasibility, not20uncomputed
curves. Final independent review must inspect all completed hashes/grids/invariant
reports and independently reproduce a representative L12 imperfect-noise case.
No lifetime fit, optimized decoder, infinite-time imperfect-correlation survival,
or larger-spin result is inferred. Root owns final integration, shared worklog,
HANDOFF and scoped version-control save; this packet never edits them itself.
