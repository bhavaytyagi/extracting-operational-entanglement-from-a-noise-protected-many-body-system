"""Full entrywise L12 kernel check, endpoint check and sustained selected benchmark."""
import run as c
from checks import old_module
import numpy as np
import json
import time


def main():
    folder=c.HERE/'checks/L12-kernel';folder.mkdir(exist_ok=True)
    with c.writer_lock(c.HERE/'progress'):
        c.status(folder,stage='negative-endpoint-setup',L=12,xi=-1/11,t=0)
        _,mask=c.setup(12,-1/11)
        endpoint=dict(min_mask=float(mask.min()),max_mask=float(mask.max()),
                      uniform_coherence=float(mask[0,-1]))
        c.require(0<endpoint['min_mask'] and endpoint['max_mask']<=1+1e-10 and
                  abs(endpoint['uniform_coherence']-1)<1e-10,'L12 endpoint mask failed')
        del mask
        phase,mask=c.setup(12,.37)
        rng=np.random.default_rng(12377)
        a=rng.normal(size=(4096,17))+1j*rng.normal(size=(4096,17))
        rho=a@a.conj().T
        rho[np.diag_indices(4096)]+=1.
        rho/=np.trace(rho);del a
        c.status(folder,stage='generic-original-kernel',L=12,xi=.37,t=1)
        tick=time.monotonic();reference=old_module().step(rho,12,phase,mask);old_seconds=time.monotonic()-tick
        c.status(folder,stage='generic-Walsh-kernel',L=12,xi=.37,t=1)
        tick=time.monotonic();got=c.step(rho,12,phase,mask);new_seconds=time.monotonic()-tick
        err=max(float(np.max(abs(got[k:k+64]-reference[k:k+64]))) for k in range(0,4096,64))
        c.require(err<1e-10,'full entrywise L12 old/new kernel comparison failed')
        c.invariants(got)
        del reference,rho,got,phase,mask
        phase,mask=c.setup(12,.99);rho=np.ones((4096,4096),complex)/4096
        steps=[];periods=[]
        for t in range(1,11):
            c.status(folder,stage='sustained-selected-step',L=12,xi=.99,t=t)
            period=time.monotonic();tick=time.monotonic();rho=c.step(rho,12,phase,mask)
            steps.append(time.monotonic()-tick);c.invariants(rho);c.extraction(rho,12)
            periods.append(time.monotonic()-period)
        row=dict(t=10,**c.extraction(rho,12),**c.spectra(rho,12,lambda stage:c.status(folder,stage=stage,L=12,xi=.99,t=10)))
        c.status(folder,stage='selected-checkpoint-write',L=12,xi=.99,t=10)
        tick=time.monotonic();c.checkpoint(folder/'state.npz',rho,dict(benchmark=True,t=10));io=time.monotonic()-tick
        (folder/'state.npz').unlink()
        hours=20*(400*max(periods)+13*(row['density_spectrum_seconds']+row['pt_spectrum_seconds'])+53*io)/3600
        result=dict(generic_full_density_max_error=err,generic_original_seconds=old_seconds,
                    generic_selected_seconds=new_seconds,negative_endpoint=endpoint,
                    step_seconds=steps,period_including_invariants_seconds=periods,
                    spectral_row=row,checkpoint_seconds=io,peak_rss_bytes=c.peak(),
                    projected20curve_hours=hours,
                    projection='Conservative max of10 measured periods plus13 spectral pairs and53 checkpoints per curve; hardware load may change.')
        c.require(c.peak()<=c.CONFIG['peak_rss_limit_bytes'],'L12 check exceeded memory ceiling')
        c.atomic_json(c.HERE/'checks/L12-kernel.json',result)
        print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
