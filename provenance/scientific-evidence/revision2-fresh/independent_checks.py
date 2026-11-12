"""Lilly's bounded artifact audit. No production trajectories are regenerated.

Predeclared checks: hashes exact; ranks exact mod 1000033; orbit pair exact
Fractions; dense map comparison/support/stationarity abs 1e-10; saved row
identities and diagnostics abs 1e-10. Saved records cannot recertify spectra.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[k] = '2'
from pathlib import Path
from fractions import Fraction
from collections import deque
import hashlib, json, importlib.util, sys
sys.dont_write_bytecode=True
import numpy as np
import scipy.linalg as la
from scipy.sparse import csr_matrix
import pymupdf

HERE=Path(__file__).resolve().parent
INP=HERE.parent/'input'
TOL=1e-10

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
hashes=json.loads((INP/'INPUT_HASHES.json').read_text())
for rel,h in hashes.items(): assert digest(INP/rel)==h,rel
print('EXACT INPUT HASHES',len(hashes),'PASS')
manifest=json.loads((INP/'data/xi_sweep/manifest.json').read_text())
for rel,h in manifest['source_sha256'].items():
    assert digest(INP/'data/xi_sweep'/rel)==h,rel
print('EXACT IMMUTABLE PRODUCER CLOSURE',len(manifest['source_sha256']),'PASS')

def orbit(s):
    return {s[k:]+s[:k] for k in range(len(s))}|{s[::-1][k:]+s[::-1][:k] for k in range(len(s))}

def sectors(n):
    remaining=set(range(2**n)); orbs=[]; owner=np.zeros(2**n,dtype=int)
    while remaining:
        k=min(remaining); oo=sorted(int(s,2) for s in orbit(format(k,f'0{n}b')))
        owner[oo]=len(orbs); orbs.append(oo); remaining.difference_update(oo)
    return orbs,owner

# Independent block Krylov computation with orbit-sum coefficients. No supplied
# certificate routines or orbit builders are imported.
def rank_check(n,p=1000033):
    oo,owner=sectors(n); d=len(oo)
    labels=[]; rows=[]; cols=[]; vals=[]
    for i,o in enumerate(oo):
        s=format(o[0],f'0{n}b')
        walls=sum(s[k]!=s[(k+1)%n] for k in range(n))
        labels.append((s.count('1'),(walls//2)%2))
        cnt={}
        for k in range(n):
            j=int(owner[o[0]^(1<<k)]);cnt[j]=cnt.get(j,0)+1
        for j,c in cnt.items(): rows.append(i);cols.append(j);vals.append(c)
    mat=csr_matrix((vals,(rows,cols)),shape=(d,d),dtype=np.int64)
    grouped={l:np.array([i for i,v in enumerate(labels) if v==l]) for l in set(labels)}
    pivots={l:{} for l in grouped};q=deque()
    def add(l,v):
        v=np.array(v%p,copy=True,dtype=np.int64)
        for k,b in sorted(pivots[l].items()): v=(v-int(v[k])*b)%p
        nz=np.flatnonzero(v)
        if len(nz):
            k=int(nz[0]);v=(v*pow(int(v[k]),-1,p))%p
            pivots[l][k]=v;q.append((l,v))
    l=labels[0];v=np.zeros(len(grouped[l]),dtype=np.int64);v[0]=1;add(l,v)
    blocks={}
    for a,ia in grouped.items():
        blocks[a]=[(b,mat[ib][:,ia]) for b,ib in grouped.items() if abs(a[0]-b[0])==1]
    while q:
        a,v=q.popleft()
        for b,m in blocks[a]:
            if m.nnz: add(b,m@v)
    rank=sum(len(v) for v in pivots.values())
    assert rank==d,(n,rank,d)
    print('INDEPENDENT CYCLIC',n,'prime',p,'rank',rank,'dim',d,flush=True)
    return oo,owner

for n in range(3,17): rank_check(n)
oo,owner=sectors(12)
a='010101';b='101010';strings=[a+a,a+b,b+a,b+b]
block=[[Fraction(int(owner[int(x,2)]==owner[int(y,2)]),len(oo[owner[int(y,2)]]))*Fraction(1,len(oo)) for y in strings] for x in strings]
prob=sum(block[i][i] for i in range(4));overlap=(block[0][0]+block[3][3]+block[0][3]+block[3][0])/(2*prob)
assert len(oo)==224 and prob==Fraction(1,192) and overlap==Fraction(6,7)
print('EXACT PAIR',block,'p',prob,'f',overlap,'F',(1+2*overlap)/3)
for s in (a,b):
    out=s[0]+''.join(str(int(z)^int(s[0])) for z in s[1:])
    assert out[1:]=='10101'
print('CNOT ACCEPTANCE RECORD 10101 PASS')

# Bell measurement + every Pauli correction, with a spherical 2-design of
# six pure inputs. This directly checks the specified protocol, not optimization.
paulis=[np.eye(2),np.array([[0,1],[1,0]]),np.array([[0,-1j],[1j,0]]),np.diag([1,-1])]
phi=np.array([1,0,0,1])/np.sqrt(2)
bells=[np.kron(np.eye(2),p)@phi for p in paulis]
def tele_average(resource):
    overlaps=[]
    for axis in paulis[1:]:
        _,vectors=np.linalg.eigh(axis)
        for psi in vectors.T:
            whole=np.kron(np.outer(psi,psi.conj()),resource).reshape(4,2,4,2)
            out=np.zeros((2,2),complex)
            for bell,p in zip(bells,paulis):
                raw=np.einsum('a,aibj,b->ij',bell.conj(),whole,bell)
                out+=p@raw@p.conj().T
            assert abs(np.trace(out)-1)<TOL
            overlaps.append(np.vdot(psi,out@psi).real)
    return np.mean(overlaps)
rng=np.random.default_rng(20261111)
for k in range(4):
    if k==0:
        pair=np.array([[float(v/prob) for v in row] for row in block])
        assert np.max(abs(np.linalg.eigvalsh(pair.reshape(2,2,2,2).transpose(2,1,0,3).reshape(4,4))-np.array([-5/14,5/14,.5,.5])))<TOL
    else:
        v=rng.normal(size=(4,4))+1j*rng.normal(size=(4,4));pair=v@v.conj().T;pair/=np.trace(pair)
    got=tele_average(pair);expected=(1+2*np.vdot(phi,pair@phi).real)/3
    assert abs(got-expected)<TOL
    print('DIRECT TELEPORTATION',k,'six_input_mean',got,'formula',expected)

# Independent dense model, explicit computational states and Kronecker gates.
spec=importlib.util.spec_from_file_location('producer',INP/'data/xi_sweep/scripts/run.py')
producer=importlib.util.module_from_spec(spec);spec.loader.exec_module(producer)
n=4;d=2**n;zz=np.array([[1-2*int(c) for c in format(k,'04b')] for k in range(d)])
en=np.pi/4*np.sum(zz*np.roll(zz,1,axis=1),axis=1)+np.sum(zz,axis=1)
u=np.array([[1.]])
for _ in range(n): u=np.kron(u,la.expm(1j*np.pi/4*np.array([[0,1],[1,0]])))
u=u@np.diag(np.exp(-1j*en));delta=zz[:,None,:]-zz[None,:,:]
oo,owner=sectors(n)
P=np.array([[int(owner[i]==owner[j])/len(oo[owner[i]]) for j in range(d)] for i in range(d)])
target=P/len(oo)
rng=np.random.default_rng(20261111)
c=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));rho=c@c.conj().T;rho/=np.trace(rho)
for xi in (-1/3,0,.5,.99,1):
    cov=(1-xi)*np.eye(n)+xi*np.ones((n,n))
    damper=np.exp(-.05*np.einsum('abi,ij,abj->ab',delta,cov,delta))
    result=(u@rho@u.conj().T)*damper
    phase,mask=producer.setup(n,xi);actual=producer.step(rho,n,phase,mask)
    err=np.max(abs(result-actual)); assert err<TOL
    result=(u@target@u.conj().T)*damper
    stationarity=np.linalg.norm(result-target);leak=np.trace((np.eye(d)-P)@result).real
    if xi==1: assert stationarity<TOL and abs(leak)<TOL
    else: assert stationarity>TOL and leak>TOL
    print('DENSE MAP',xi,'max_entry_error',err,'target_change',stationarity,'sector_leak',leak)

all_records=[]
for f in sorted((INP/'data/xi_sweep/data').glob('*.json')):
    obj=json.loads(f.read_text());all_records.append(obj)
    assert obj['L']==12 and obj['horizon']==400 and len(obj['rows'])==401
    for k in ('J','b','h','gamma'):assert abs(obj[k]-manifest['config'][k])<TOL
    assert obj['negativity_samples']==manifest['config']['negativity_samples']
    assert 0<=obj['max_trace_error']<TOL and 0<=obj['max_hermiticity_error']<TOL
    for t,row in enumerate(obj['rows']):
        assert row['t']==t
        assert all(np.isfinite(v) for v in row.values())
        p=row['probability'];f0=row['bell_overlap'];F=row['teleportation_fidelity']
        assert 0<p<=1+TOL and -TOL<=f0<=1+TOL
        assert abs(F-(1+2*f0)/3)<TOL
        assert abs(row['weighted_advantage']-p*(F-2/3))<TOL
        assert abs(row['fallback_fidelity']-(2/3+max(0,p*(F-2/3))))<TOL
        assert ('log_negativity_nats' in row)==(t in obj['negativity_samples'])
        if t in obj['negativity_samples']:
            assert -TOL<=row['log_negativity_nats']<=6*np.log(2)+TOL
            assert row['min_density_eigenvalue']>=-TOL
            assert 0<=row['density_spectral_trace_error']<TOL and 0<=row['pt_spectral_trace_error']<TOL
    row=obj['rows'][0]
    assert abs(row['probability']-1/1024)<TOL and abs(row['teleportation_fidelity']-2/3)<TOL and abs(row['log_negativity_nats'])<TOL
    if obj['xi'] in (.99,.999):
        useful=[r['t'] for r in obj['rows'] if r['teleportation_fidelity']>2/3+TOL]
        expected=list(range(2,179 if obj['xi']==.99 else 401))
        assert useful==expected
        print('USEFUL TIMES',obj['xi'],useful[0],useful[-1],len(useful))
    if obj['xi']==.995: print('XI .995 PERIOD 400',obj['rows'][-1])
assert sorted(o['xi'] for o in all_records)==manifest['config']['xi_grid']
print('SAVED RECORDS 20 CURVES / 8020 RESOURCE ROWS / 260 SPECTRAL DIAGNOSTICS PASS')
ideal=json.loads((INP/'data/xi_sweep/provenance/dynamics_L12_xi1.json').read_text())
print('IDEAL REFERENCE TOP LEVEL KEYS',sorted(ideal))

doc=pymupdf.open(INP/'letter_prl_revision_2.pdf')
for i,page in enumerate(doc):
    text=page.get_text();assert text.strip()
    (HERE/f'page-{i+1}.txt').write_text(text)
    page.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25)).save(HERE/'renders'/f'page-{i+1}.png')
print('RENDERED PDF PAGES',len(doc))
