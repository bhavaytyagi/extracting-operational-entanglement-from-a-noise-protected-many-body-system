# Twelve-spin dynamics and sixteen-spin target spectrum

Date: 2026-10-29. Author: Luke (Codex), integrated by root (Codex). Verification label: **agent-verified**, finite numerical and protocol scope only. Fresh reviewer: Codex in artifact-only context `/root/campaign_acceptance`.

## Claims accepted

**LAPTOP-TARGET-16-20261029.** Complete numerical partial-transpose spectra of the normalized dihedral invariant-vector projector at even sizes 4–16, contiguous equal halves, natural logarithm, reproduce the previous target values. At 16 the sector dimension is 2250 and logarithmic negativity is 1.088191469164693. The charge/reflection decomposition and complement multiplicity are complete, not spectral truncations. Memory/runtime for this implementation on the measured 16 GiB machine are recorded, not general hardware guarantees.

**LAPTOP-DYNAMICS-12-20261029.** The uniform plus product evolved by Ising, kick, then ideal collective dephasing, J=pi/4, b=-pi/4, h=1, gamma=0.1, through integer periods 0–400 yields the saved full-ring negativity samples and every-period fixed-protocol resource metrics at 12 spins. At period 400, logarithmic negativity is 0.9419524091957566 and Frobenius distance to P/224 is 4.7965e-15. The exact target's conditional teleportation fidelity is 19/21 and preparation probability 1/192, with ideal within-half coherent decoding and heralding before unknown input. The corresponding zero-Ising control has no resolved sampled negativity or teleportation advantage. The reproduced 10-spin trajectory provides a regression baseline.

## Evidence and independent verification

[Campaign and reproduction instructions](../numerical_campaigns/prl-2026-10-29/README.md), [predeclared checks](../numerical_campaigns/prl-2026-10-29/SPEC.md), [fresh report](../numerical_campaigns/prl-2026-10-29/review/final/REPORT.md), and executable checks/output under the same `review/final/` directory. Numerical code and data hashes are recorded in the review outputs and final campaign manifest.

- Direct group-average targets and full spectra at sizes 4,6,8,10 independently agree within 2.23e-16, with the specified small-case tolerance 1e-11.
- Full selected-map comparison at sizes 4,6,10, both interacting and zero-Ising, agrees within 9e-16. At 12, an independently constructed orbit-space unitary reproduces all 401 resource points: maximum error 1.89e-15 interacting and 4.58e-13 control, below 1e-10.
- Independent 12-spin full negativity at interacting periods 1,4,400 agrees within 1.69e-13; all four control samples agree within 4.49e-14. Remaining interacting samples are supported by inspected implementation, invariants and these comparisons, not claimed as separately recomputed.
- At 16, independent group-average sparse matrix checks verify charge support, local reflection/complement, complete orthonormal block bases and total trace. The saved spectrum matches the older rounded value to 3.54e-11, within the 1e-9 regression tolerance. The reviewer did not rerun the 16-spin eigensolver.
- All exact target extraction records at even sizes 4–30 are independently checked and also exactly reproduce the previously accepted records. This reuse does not extend dynamics to 30.
- A reviewer scheduling defect for the zero-Ising sample grid and an overgeneralized Bell-decomposition sentence were corrected with their original errors retained. The final report has no critical or major finding. A documented minor portability limitation remains: two legacy regression commands require surrounding-project files.

## Limits

This promotes finite numerical calculations and the scoped decoder result, not all-size attraction, an infinite-size entanglement floor, new imperfect-correlation dynamics, an optimized extraction protocol or device throughput. The ideal-sector reduction cannot be used unchanged for imperfect correlations. Existing convergence certificates and other scientific claims retain their prior verification status. The numerical stationary target is not itself a proof of dynamical attraction.

No main manuscript or bibliography changed. Generated figures are diagnostics awaiting manuscript design. The code/data package has not been uploaded or made public.
