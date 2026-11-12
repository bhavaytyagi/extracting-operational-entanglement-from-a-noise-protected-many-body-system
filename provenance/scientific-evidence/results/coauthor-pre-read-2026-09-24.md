# Finite checks added by the coauthor pre-read audit

Status: **agent-verified**, only for the bounded statements below.
Record author: Codex (GPT-6). Independent verifier: fresh Codex
`/root/final_theory`, supplied the frozen artifact without prior reports or
author reasoning. [Full report and conventions](../reviews/coauthor-audit-2026-09-24/theory-review/report.md).

1. **CN-010 / finite certificate:** the ring-invariant vector sector is cyclic
   under the stated collective-spin and self-dual Ising generators at each
   L=3–16. Full integer ranks are certified modulo both 1000003 and 1000033;
   J=0 controls have rank L+1. The report checks the scalar-commutant inference.
   This does not extend to arbitrary size or the full-space commutant.
2. **CN-011 / Néel at L6/8/10:** weights, normalized stationary formula and
   balanced-cut negativities agree within absolute 1e-12. A separate complete
   intertwiner calculation finds fixed B1 dimensions 2,1,2 and no relevant
   nonfixed/cross-sector peripheral space. Null singular values are below
   1.12e-15, nonzero ones above 0.74, against a 1e-10 threshold. This part is
   floating-point evidence, not exact modular arithmetic; historical convergence
   rates and finite-time trace distances were not independently regenerated.
3. **CN-012 / cuts and reduced witness:** every listed L10/L12 cut value agrees
   with four-decimal rounding within 5.1e-5, with trace and dense-spectrum checks.
   The specified six-site reduction has minimum PT eigenvalue
   -0.01201724540227305 and logarithmic negativity 0.023750208476390533;
   the witness expectation and stated values agree within 1e-12. It detects
   entanglement, not the full-ring negativity from a few measured moments.

The report gives additional analytic review of the dephasing fixed/peripheral
distinction, supported basin, projector upper bound and eventual-PPT argument.
The broad CN entries retain their earlier labels because their combined scope
and dependencies exceed these executable finite checks. Lifetime tails,
amplitude/disorder scans, device assumptions, all-size and thermodynamic claims
are not promoted by this result page. Exact commands, hashes, environment,
scripts and stdout are in the linked review directory.
