"""Measured full-space L12 mixed-state workload; serial, BLAS2, no production."""
import run as candidate
from checks import old_module
import json
import time
from pathlib import Path
import numpy as np


def main():
    folder = candidate.HERE/'checks/benchmark'
    folder.mkdir(exist_ok=True)
    with candidate.writer_lock(candidate.HERE/'progress'):
        candidate.status(folder,stage='L12-setup',L=12,xi=.99,t=0)
        tick=time.monotonic(); phase,mask=candidate.setup(12,.99); setup_seconds=time.monotonic()-tick
        rho=np.ones((4096,4096),complex)/4096
        candidate.invariants(rho)
        steps=[]
        for t in range(1,3):
            candidate.status(folder,stage='L12-step',L=12,xi=.99,t=t)
            tick=time.monotonic();rho=old_module().step(rho,12,phase,mask);steps.append(time.monotonic()-tick)
            tr,he=candidate.invariants(rho)
        row=dict(t=2,**candidate.extraction(rho,12))
        row.update(candidate.spectra(rho,12,lambda stage:candidate.status(folder,stage=stage,L=12,xi=.99,t=2)))
        candidate.status(folder,stage='L12-checkpoint-write',L=12,xi=.99,t=2)
        tick=time.monotonic();candidate.checkpoint(folder/'state.npz',rho,dict(benchmark=True,t=2));write_seconds=time.monotonic()-tick
        size=(folder/'state.npz').stat().st_size
        (folder/'state.npz').unlink()
        total_curve=400*max(steps)+13*(row['density_spectrum_seconds']+row['pt_spectrum_seconds'])+53*write_seconds
        result=dict(L=12,xi=.99,setup_seconds=setup_seconds,step_seconds=steps,
                    spectrum=row,checkpoint_write_seconds=write_seconds,checkpoint_bytes=size,
                    trace_error=tr,hermiticity_error=he,peak_rss_bytes=candidate.peak(),
                    measured_threads=2,projected20curve_hours=20*total_curve/3600,
                    caveat='Projection from two steps and one pair of spectra; excludes load changes and invariant/heartbeat IO.')
        candidate.require(candidate.peak()<=candidate.CONFIG['peak_rss_limit_bytes'],'benchmark peak exceeds memory ceiling')
        candidate.atomic_json(candidate.HERE/'checks/benchmark.json',result)
        print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
