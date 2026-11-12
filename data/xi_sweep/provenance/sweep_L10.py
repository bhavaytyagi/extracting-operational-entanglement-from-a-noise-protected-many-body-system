"""Full physical density evolution; no ideal-sector restriction at xi<1.

Factored coherent layer adapted from verify_large_amplitude_20260910.py;
fixed decoder adapted from resource-calculation-2026-10-26/dynamics/run.py.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='2'
from pathlib import Path
import sys,json,time,resource,platform
import numpy as np
from scipy.linalg import eigvalsh,expm
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]
TOL=1e-10
GRID=[-1/9,-.05,0,.1,.2,.3,.4,.5,.6,.7,.8,.85,.9,.95,.97,.98,.99,.995,.999,1.]
SAMPLES=[0,1,2,3,4,5,10,20,40,80,150,250,400]

def setup(n,xi,j=np.pi/4):
    if isinstance(n,bool) or not isinstance(n,int) or n not in (4,6,8,10):
        raise ValueError('validated full sweep sizes4,6,8,10 only')
    if not np.isfinite(xi) or not -1/(n-1)<=xi<=1:
        raise ValueError('xi outside complete-graph covariance interval')
    if not np.isfinite(j):raise ValueError('finite J required')
    d=1<<n; idx=np.arange(d); bits=(idx[:,None]>>np.arange(n-1,-1,-1))&1;z=1-2*bits
    energy=j*(z*np.roll(z,1,axis=1)).sum(axis=1)+z.sum(axis=1)
    phase=np.exp(-1j*energy)
    distance=np.zeros((d,d),np.int16)
    for k in range(n):distance+=bits[:,k,None]!=bits[None,:,k]
    mz=z.sum(axis=1)
    exponent=-.05*(4*(1-xi)*distance+xi*(mz[:,None]-mz[None,:])**2)
    assert np.max(exponent)<TOL
    mask=np.exp(exponent)
    assert np.max(abs(np.diag(mask)-1))<TOL
    return phase,mask

def step(rho,n,phase,mask):
    d=1<<n
    state=np.array(phase[:,None]*rho*phase.conj()[None,:],order='C',copy=True)
    c,s=np.cos(-np.pi/4),np.sin(-np.pi/4)
    for p in range(n):
        block=state.reshape(d>>(p+1),2,1<<p,d);zero=block[:,0].copy()
        block[:,0]=c*zero-1j*s*block[:,1];block[:,1]=-1j*s*zero+c*block[:,1]
    for p in range(n):
        block=state.reshape(d,d>>(p+1),2,1<<p);zero=block[:,:,0].copy()
        block[:,:,0]=c*zero+1j*s*block[:,:,1];block[:,:,1]=1j*s*zero+c*block[:,:,1]
    state*=mask
    return state

def extraction(rho,n):
    m=n//2;a=int(('01'*m)[:m],2);b=(1<<m)-1-a
    ii=[(r<<m)|c for r in (a,b) for c in (a,b)]
    sigma=rho[np.ix_(ii,ii)];p=float(np.trace(sigma).real)
    assert p>0
    bell=np.array([0,1,1,0] if m%2 else [1,0,0,1])/np.sqrt(2)
    overlap=float(np.vdot(bell,sigma@bell).real)/p
    f=(1+2*overlap)/3;adv=p*(f-2/3)
    assert -TOL<=overlap<=1+TOL
    return dict(probability=p,bell_overlap=overlap,teleportation_fidelity=f,weighted_advantage=adv,fallback_fidelity=2/3+max(0.,adv))

def spectra(rho,n):
    d=1<<n;h=1<<(n//2)
    ev=eigvalsh(rho,check_finite=False);pos=float(ev[0]);assert pos>=-TOL
    pt=rho.reshape(h,h,h,h).transpose(2,1,0,3).reshape(d,d)
    pv=eigvalsh(pt,check_finite=False);assert abs(pv.sum()-1)<TOL
    return dict(log_negativity_nats=float(np.log(abs(pv).sum())),min_density_eigenvalue=pos,min_pt_eigenvalue=float(pv[0]))

def peak():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform=='darwin' else value*1024)

def run(n,xi,horizon=400,j=np.pi/4,save=True):
    start=time.monotonic();phase,mask=setup(n,xi,j);d=1<<n;rho=np.ones((d,d),complex)/d
    samples=[t for t in SAMPLES if t<=horizon];rows=[];maxtr=0.;maxherm=0.
    tag=f'L{n}_xi{xi:.9f}'+('_J0' if j==0 else '')
    for t in range(horizon+1):
        traceerr=float(abs(np.trace(rho)-1));hermerr=float(np.max(abs(rho-rho.conj().T)))
        assert max(traceerr,hermerr)<TOL,(tag,t,traceerr,hermerr)
        maxtr=max(maxtr,traceerr);maxherm=max(maxherm,hermerr)
        row=dict(t=t,**extraction(rho,n))
        if t in samples:
            row.update(spectra(rho,n))
            if t==0 or j==0:assert abs(row['log_negativity_nats'])<TOL
        if j==0:assert row['teleportation_fidelity']<=2/3+TOL
        rows.append(row)
        if t<horizon:rho=step(rho,n,phase,mask)
    result=dict(L=n,xi=xi,J=j,b=-np.pi/4,h=1.,gamma=.1,horizon=horizon,negativity_samples=samples,rows=rows,max_trace_error=maxtr,max_hermiticity_error=maxherm,seconds=time.monotonic()-start,peak_rss_bytes=peak())
    if save:(HERE/'data'/f'{tag}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    return result

def checks():
    n=4;d=1<<n;eye=np.eye(2);x=np.array([[0,1],[1,0]]);z=np.diag([1.,-1.])
    def site(op,k):
        a=np.ones((1,1))
        for q in range(n):a=np.kron(a,op if q==k else eye)
        return a
    zs=[site(z,k) for k in range(n)];xs=[site(x,k) for k in range(n)]
    u=expm(1j*np.pi/4*sum(xs))@expm(-1j*sum(np.pi/4*zs[k]@zs[(k+1)%n]+zs[k] for k in range(n)))
    rng=np.random.default_rng(20261030);a=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));rho=a@a.conj().T;rho/=np.trace(rho)
    errors={}
    for xi in (-1/3,0,.5,.99,1.):
        phase,mask=setup(n,xi);cov=(1-xi)*np.eye(n)+xi*np.ones((n,n));gen=np.zeros((d*d,d*d),complex)
        for j in range(n):
            for k in range(n):
                q=zs[k]@zs[j]
                gen+=.1*cov[j,k]*(np.kron(zs[k].T,zs[j])-.5*np.kron(np.eye(d),q)-.5*np.kron(q.T,np.eye(d)))
        ref=(expm(gen)@(u@rho@u.conj().T).reshape(-1,order='F')).reshape((d,d),order='F')
        err=float(np.max(abs(ref-step(rho,n,phase,mask))));assert err<TOL;errors[str(xi)]=err
    rejected=0
    for xi in (-.334,1.001,float('nan')):
        try:setup(n,xi)
        except ValueError:rejected+=1
    assert rejected==3
    controls=[run(4,xi,40,j=0,save=False) for xi in (-1/3,0,.99,1.)]
    result=dict(dense_lindblad_errors=errors,rejected_invalid_inputs=rejected,controls=controls)
    (HERE/'checks'/'author-reference.json').write_text(json.dumps(result,indent=2)+'\n')

def regress():
    errors={}
    for xi in (.95,.99,1.):
        old=json.loads((HERE/'provenance'/f'L10_xi{xi:.2f}.json').read_text())
        new=json.loads((HERE/'data'/f'L10_xi{xi:.9f}.json').read_text())
        resources=max(abs(a[k]-old['rows'][a['t']][k]) for a in new['rows'] for k in ('probability','bell_overlap','teleportation_fidelity'))
        negatives=max(abs(a['log_negativity_nats']-old['rows'][a['t']]['log_negativity']) for a in new['rows'] if 'log_negativity_nats' in a and 'log_negativity' in old['rows'][a['t']])
        assert max(resources,negatives)<1e-9
        errors[str(xi)]=dict(resource_max_error=resources,negativity_max_error=negatives)
    (HERE/'checks'/'prior-regression.json').write_text(json.dumps(errors,indent=2)+'\n')
    print(errors)

if __name__=='__main__':
    command=sys.argv[1]
    if command=='checks':checks()
    elif command=='benchmark':run(10,.99,horizon=10,save=False)
    elif command=='regress':regress()
    elif command=='all':
        for xi in GRID:run(10,xi)
    elif command=='one':run(int(sys.argv[2]),float(sys.argv[3]))
    else:raise ValueError('unknown command')
