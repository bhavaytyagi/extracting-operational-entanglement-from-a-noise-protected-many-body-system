"""Ideal collective-dephasing dynamics in the vector-fixed dihedral sector.

This reduction MUST NOT be used for imperfect correlations.
"""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='2'
import sys,json,time,resource
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.linalg import eigvalsh
from target import orbits,split_involution,maxabs,peak_rss_bytes
HERE=Path(__file__).resolve().parents[1]; ROOT=HERE.parents[1]
TOL=1e-10

def setup(n,j):
    assert isinstance(n,int) and 4<=n<=12 and n%2==0, 'validated even sizes4..12 only'
    assert np.isfinite(j), 'finite Ising coupling required'
    oo=orbits(n); d=1<<n; k=len(oo)
    which=np.empty(d,np.int32); sizes=np.array([len(o) for o in oo]); reps=np.array([o[0] for o in oo])
    for i,o in enumerate(oo): which[o]=i
    weights=1/np.sqrt(sizes[which])
    basis=sparse.csr_matrix((weights,(np.arange(d),which)),shape=(d,k))
    assert maxabs(basis.T@basis-sparse.eye(k))<TOL
    bits=(np.arange(d)[:,None]>>np.arange(n-1,-1,-1))&1; z=1-2*bits
    energy=j*(z*np.roll(z,1,axis=1)).sum(axis=1)+z.sum(axis=1)
    assert np.max(abs(energy-energy[reps][which]))<TOL
    ukq=basis.toarray().astype(complex)*np.exp(-1j*energy[:,None])
    b=-np.pi/4; c=np.cos(b);s=np.sin(b)
    for bit in range(n):
        block=ukq.reshape(d>>(bit+1),2,1<<bit,k)
        zero=block[:,0].copy()
        block[:,0]=c*zero-1j*s*block[:,1]
        block[:,1]=-1j*s*zero+c*block[:,1]
    unitary=basis.T@ukq
    leakage=float(np.max(abs(ukq-basis@unitary)))
    assert leakage<TOL
    unitary_error=float(np.max(abs(unitary.conj().T@unitary-np.eye(k))))
    assert unitary_error<TOL
    zz=z.sum(axis=1)[reps]; mask=np.exp(-.05*(zz[:,None]-zz[None,:])**2)
    initial=np.sqrt(sizes/d).astype(complex)
    return dict(orbits=oo,which=which,weights=weights,sizes=sizes,basis=basis,u=unitary,mask=mask,initial=initial,unitarity_error=unitary_error,leakage=leakage)

def decode(a,s):
    return a[s['which'][:,None],s['which'][None,:]]*s['weights'][:,None]*s['weights'][None,:]

def extraction(a,s,n):
    m=n//2; x=int(('01'*m)[:m],2); y=(1<<m)-1-x
    ii=np.array([(r<<m)|c for r in (x,y) for c in (x,y)])
    sigma=a[s['which'][ii,None],s['which'][None,ii]]*s['weights'][ii,None]*s['weights'][None,ii]
    p=float(np.trace(sigma).real); assert p>0
    bell=np.array([0,1,1,0] if m%2 else [1,0,0,1])/np.sqrt(2)
    f=float(np.vdot(bell,sigma@bell).real)/p; fidelity=(1+2*f)/3
    return dict(probability=p,bell_overlap=f,teleportation_fidelity=fidelity,weighted_advantage=p*(fidelity-2/3),fallback_fidelity=2/3+max(0.,p*(fidelity-2/3)))

def negativity(rho,n):
    d=1<<n;m=n//2;half=1<<m
    pt=rho.reshape(half,half,half,half).transpose(2,1,0,3).reshape(d,d)
    reverse=np.array([int(f'{x:0{m}b}'[::-1],2) for x in range(half)])
    idx=np.arange(d); refl=(reverse[idx>>m]<<m)|reverse[idx&(half-1)]
    assert np.max(abs(pt[np.ix_(refl,refl)]-pt))<TOL
    left=idx[idx<refl];fixed=idx[idx==refl]; norm=0.;trace=0.;minimum=1.
    for sign in (1,-1):
        rr=list(left)+list(refl[left]);cc=list(range(len(left)))*2
        vv=[1/np.sqrt(2)]*len(left)+[sign/np.sqrt(2)]*len(left)
        if sign==1:
            rr.extend(fixed);cc.extend(range(len(left),len(left)+len(fixed)));vv.extend([1.]*len(fixed))
        cols=len(left)+(len(fixed) if sign==1 else 0)
        basis=sparse.csr_matrix((vv,(rr,cc)),shape=(d,cols))
        block=(basis.T@pt)@basis
        assert np.max(abs(block-block.conj().T))<TOL
        ev=eigvalsh(block,overwrite_a=True,check_finite=False,driver='evr')
        norm+=float(abs(ev).sum());trace+=float(ev.sum());minimum=min(minimum,float(ev[0]))
    assert abs(trace-1)<TOL,trace
    return float(np.log(norm)),minimum

def reference():
    sys.path.insert(0,str(ROOT/'paper_pipeline/production_ukui'))
    import selected
    errors={}
    for n in (4,6):
        for j in (0.,np.pi/4):
            s=setup(n,j);rho=np.outer(s['initial'],s['initial'].conj());full=decode(rho,s)
            facade=selected.DephasingEvolver(n,1.,.1,j=j)
            worst=0.
            for t in range(4):
                rho=(s['u']@rho@s['u'].conj().T)*s['mask'];full=facade.step(full)
                worst=max(worst,float(np.max(abs(full-decode(rho,s)))))
            assert worst<TOL
            pt=selected.partial_transpose(full,n,range(n//2))
            direct=float(np.log(abs(eigvalsh(pt)).sum()))
            got,_=negativity(full,n);assert abs(direct-got)<TOL
            errors[f'L{n}_J{j}']=dict(map_max_error=worst,negativity_error=abs(direct-got))
    (HERE/'checks'/'dynamics-reference.json').write_text(json.dumps(errors,indent=2)+'\n')

def run(n,j=np.pi/4,horizon=400):
    start=time.monotonic(); s=setup(n,j);k=len(s['sizes']); rho=np.outer(s['initial'],s['initial'].conj())
    target=np.eye(k)/k;u=s['u'];mask=s['mask'];stationarity=float(np.max(abs((u@target@u.conj().T)*mask-target)))
    assert stationarity<TOL
    samples=([0,1,2,3,4,5,10,20,40,80,150,250,400] if j else [0,1,10,400])
    rows=[];maxtrace=0.;maxherm=0.;minpos=1.;tag=f'dynamics_L{n}_xi1'+('_J0' if j==0 else '')
    for t in range(horizon+1):
        traceerr=float(abs(np.trace(rho)-1));hermerr=float(np.max(abs(rho-rho.conj().T)))
        assert max(traceerr,hermerr)<TOL
        maxtrace=max(maxtrace,traceerr);maxherm=max(maxherm,hermerr)
        row=dict(t=t,**extraction(rho,s,n))
        if j==0:assert row['teleportation_fidelity']<=2/3+TOL
        if t in samples:
            tick=time.monotonic();mineig=float(eigvalsh(rho,check_finite=False)[0]);assert mineig>=-TOL;minpos=min(minpos,mineig)
            full=decode(rho,s);en,lmin=negativity(full,n);del full
            if j==0 or t==0:assert abs(en)<TOL
            row.update(log_negativity_nats=en,min_sector_density_eigenvalue=mineig,min_pt_eigenvalue=lmin,distance_target_frobenius=float(np.linalg.norm(rho-target)),negativity_seconds=time.monotonic()-tick)
            print(tag,json.dumps(row),flush=True)
        rows.append(row)
        if t<horizon:rho=(u@rho@u.conj().T)*mask
    result=dict(L=n,sector_dimension=k,J=j,b=-np.pi/4,h=1.,gamma=.1,xi=1.,horizon=horizon,negativity_samples=samples,rows=rows,seconds=time.monotonic()-start,peak_rss_bytes=peak_rss_bytes(),max_trace_error=maxtrace,max_hermiticity_error=maxherm,minimum_sampled_sector_density_eigenvalue=minpos,target_stationarity_residual=stationarity,projected_unitarity_error=s['unitarity_error'],unitary_leakage=s['leakage'],target_metrics=extraction(target,s,n))
    if n==10:
        old=json.loads((ROOT/'checks/resource-calculation-2026-10-26/dynamics'/('L10_xi1.00'+('_J0' if j==0 else '')+'.json')).read_text())
        err=max(abs(row[key]-old['rows'][row['t']][key]) for row in rows for key in ('probability','teleportation_fidelity'))
        negerr=max(abs(row['log_negativity_nats']-old['rows'][row['t']]['log_negativity']) for row in rows if 'log_negativity_nats' in row and 'log_negativity' in old['rows'][row['t']])
        assert max(err,negerr)<1e-9,(err,negerr); result['old_L10_errors']=dict(resource=err,negativity=negerr)
    (HERE/'data'/f'{tag}.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)
    return result

if __name__=='__main__':
    if sys.argv[1:] == ['reference']:reference()
    else:
        n=int(sys.argv[1]);j=0. if '--j0' in sys.argv else np.pi/4
        run(n,j)
