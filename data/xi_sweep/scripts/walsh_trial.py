"""Candidate exact kick factorization, retained trial benchmark and reference."""
import run as c
import numpy as np
import time
import json


def step_walsh(rho,n,phase,mask):
    d=1<<n
    indices=np.arange(d)
    count=np.zeros(d,np.int16)
    for bit in range(n):count+=(indices>>bit)&1
    dp=(1j)**count
    inner=phase*dp
    state=np.array(inner[:,None]*rho*inner.conj()[None,:],order='C',copy=True)
    for p in range(n):
        block=state.reshape(d>>(p+1),2,1<<p,d);zero=block[:,0].copy()
        np.add(zero,block[:,1],out=block[:,0])
        np.subtract(zero,block[:,1],out=block[:,1])
    for p in range(n):
        block=state.reshape(d,d>>(p+1),2,1<<p);zero=block[:,:,0].copy()
        np.add(zero,block[:,:,1],out=block[:,:,0])
        np.subtract(zero,block[:,:,1],out=block[:,:,1])
    state*=dp[:,None]
    state*=dp.conj()[None,:]
    state/=d
    state*=mask
    return state


def main():
    folder=c.HERE/'checks/walsh-trial';folder.mkdir(exist_ok=True)
    with c.writer_lock(c.HERE/'progress'):
        c.status(folder,stage='L12-walsh-setup',L=12,xi=.99,t=0)
        phase,mask=c.setup(12,.99);rho=np.ones((4096,4096),complex)/4096
        steps=[]
        for t in range(1,3):
            c.status(folder,stage='L12-walsh-step',L=12,xi=.99,t=t)
            tick=time.monotonic();rho=step_walsh(rho,12,phase,mask);steps.append(time.monotonic()-tick)
            c.invariants(rho)
        row=dict(t=2,**c.extraction(rho,12),**c.spectra(rho,12,lambda stage:c.status(folder,stage=stage,L=12,xi=.99,t=2)))
        prior=json.loads((c.HERE/'checks/benchmark.json').read_text())['spectrum']
        err=max(abs(row[k]-prior[k]) for k in ('probability','teleportation_fidelity','log_negativity_nats','min_density_eigenvalue','min_pt_eigenvalue'))
        c.require(err<1e-10,'L12 original-kernel benchmark regression failed')
        result=dict(step_seconds=steps,peak_rss_bytes=c.peak(),row=row,prior_metrics_max_error=err)
        c.atomic_json(c.HERE/'checks/walsh-trial.json',result)
        print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
