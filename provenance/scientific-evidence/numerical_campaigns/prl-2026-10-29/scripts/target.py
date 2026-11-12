"""Exact finite target spectrum, with checked charge/reflection/complement blocks."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[name]='2'
import sys, json, time, resource, math, platform
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.linalg import eigvalsh
HERE=Path(__file__).resolve().parents[1]
TOL=1e-10

def orbits(n):
    mask=(1<<n)-1; seen=np.zeros(1<<n,bool); ans=[]
    for x in range(1<<n):
        if seen[x]: continue
        rev=int(f'{x:0{n}b}'[::-1],2)
        o=sorted({((y<<r)|(y>>(n-r)))&mask for y in (x,rev) for r in range(n)})
        seen[o]=True; ans.append(np.array(o,dtype=np.int32))
    assert seen.all()
    return ans

def projector_pt(n,oo):
    m=n//2; mask=(1<<m)-1
    count=sum(len(o)**2 for o in oo)
    rows=np.empty(count,np.int32); cols=np.empty(count,np.int32); vals=np.empty(count)
    start=0
    for o in oo:
        k=len(o); stop=start+k*k; a=o>>m; b=o&mask
        rows[start:stop]=((a[None,:]<<m)|b[:,None]).ravel()
        cols[start:stop]=((a[:,None]<<m)|b[None,:]).ravel()
        vals[start:stop]=1/(k*len(oo)); start=stop
    out=sparse.coo_matrix((vals,(rows,cols)),shape=(1<<n,1<<n)).tocsr()
    assert maxabs(out-out.T)<TOL
    return out

def maxabs(a):
    return float(np.max(np.abs(a.data),initial=0))

def split_involution(a,permutation):
    """Orthonormal +/- eigenbases of an explicitly checked involution."""
    size=a.shape[0]; ii=np.arange(size)
    assert np.array_equal(permutation[permutation],ii)
    assert maxabs(a[permutation][:,permutation]-a)<TOL
    left=ii[ii<permutation]; fixed=ii[ii==permutation]
    result=[]
    for sign in (1,-1):
        reps=np.concatenate((left,fixed)) if sign==1 else left
        rr=list(left)+list(permutation[left]); cc=list(range(len(left)))*2
        vv=[1/np.sqrt(2)]*len(left)+[sign/np.sqrt(2)]*len(left)
        if sign==1:
            rr.extend(fixed); cc.extend(range(len(left),len(reps))); vv.extend([1.]*len(fixed))
        q=sparse.csr_matrix((vv,(rr,cc)),shape=(size,len(reps)))
        assert maxabs(q.T@q-sparse.eye(len(reps)))<TOL
        result.append((q.T@a@q,q,reps))
    assert sum(v[0].shape[0] for v in result)==size
    assert maxabs(result[1][1].T@a@result[0][1])<TOL
    return result

def peak_rss_bytes():
    value=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system()=='Darwin' else value*1024)

def run(n):
    assert isinstance(n,int) and 4<=n<=16 and n%2==0, 'validated even sizes4..16 only'
    start=time.monotonic(); oo=orbits(n); matrix=projector_pt(n,oo)
    m=n//2; d=1<<n; mask=(1<<m)-1; idx=np.arange(d)
    pop=np.array([x.bit_count() for x in range(1<<m)])
    charge=pop[idx&mask]-pop[idx>>m]
    coo=matrix.tocoo(); assert np.all(charge[coo.row]==charge[coo.col]); del coo
    complement=d-1-idx
    assert maxabs(matrix[complement][:,complement]-matrix)<TOL
    reverse=np.array([int(f'{x:0{m}b}'[::-1],2) for x in range(1<<m)])
    reflection=(reverse[idx>>m]<<m)|reverse[idx&mask]
    assert maxabs(matrix[reflection][:,reflection]-matrix)<TOL
    tn=0.; trace=0.; minimum=1.; rows=[]
    for q in range(m+1):
        selected=np.flatnonzero(charge==q); lookup=np.full(d,-1,dtype=np.int32);lookup[selected]=np.arange(len(selected))
        a=matrix[selected][:,selected]; reflected=lookup[reflection[selected]]
        blocks=split_involution(a,reflected)
        for rsign,(a,qbasis,reps) in enumerate(blocks):
            subblocks=[a]
            if q==0:
                # Complement commutes with reflection, and acts as a permutation
                # with possible signs in the odd-reflection basis. Use q=0
                # reflection blocks directly to avoid an unneeded signed split.
                pass
            for bmat in subblocks:
                if bmat.shape[0]==0:  # A symmetry character may be absent.
                    rows.append(dict(charge=q,reflection_sign=1 if rsign==0 else -1,size=0,seconds=0,multiplicity=1 if q==0 else 2))
                    continue
                size=bmat.shape[0]
                assert size*size*8 < 700*1024**2, (n,q,size,size*size*8)
                tick=time.monotonic(); dense=bmat.toarray(order='F')
                ev=eigvalsh(dense,overwrite_a=True,check_finite=False,driver='evr')
                mult=1 if q==0 else 2
                tn+=mult*float(abs(ev).sum()); trace+=mult*float(ev.sum());minimum=min(minimum,float(ev[0]))
                row=dict(charge=q,reflection_sign=1 if rsign==0 else -1,size=size,seconds=time.monotonic()-tick,multiplicity=mult)
                rows.append(row); print(json.dumps(dict(L=n,**row)),flush=True)
                del dense,ev
    assert abs(trace-1)<TOL,trace
    result=dict(L=n,sector_dimension=len(oo),log_negativity_nats=float(np.log(tn)),trace=trace,min_pt_eigenvalue=minimum,seconds=time.monotonic()-start,peak_rss_bytes=peak_rss_bytes(),blocks=rows)
    known={4:.223143551314,6:.449715774145,8:.646491039733,10:.823820166738,12:.941952409196,14:1.033609848549,16:1.0881914692}
    if n in known: assert abs(result['log_negativity_nats']-known[n])<1e-9
    (HERE/'data'/f'target_L{n}.json').write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    for n in map(int,sys.argv[1:] or [4,6,8,10,12,14,16]): run(n)
