"""Independent final audit. Writes only its own reviewer directory; no production.

Predeclared tolerances: state/PT/decoder and invariants 1e-10; frozen trajectory
comparisons 1e-9. Independent dense reference uses explicit tensor operators,
a 256x256 Lindblad superoperator exponential, direct PT indices, local Kraus
decoder, and direct unitary exponentials. No author's validation functions.
"""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='2'
import hashlib, importlib.util, json, math, sys
sys.dont_write_bytecode=True
from pathlib import Path
import numpy as np
from scipy.linalg import expm, eigvalsh

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]/'data/xi_sweep'
TOL=1e-10
REG=1e-9
GRID=[-1/11,-.05,0,.1,.2,.3,.4,.5,.6,.7,.8,.85,.9,.95,.97,.98,.99,.995,.999,1.]
SAMPLES=[0,1,2,3,4,5,10,20,40,80,150,250,400]
RES={'probability','bell_overlap','teleportation_fidelity','weighted_advantage','fallback_fidelity'}
SPEC={'log_negativity_nats','min_density_eigenvalue','min_pt_eigenvalue','density_spectral_trace_error','pt_spectral_trace_error','density_spectrum_seconds','pt_spectrum_seconds'}
results={}
def read(rel): return json.loads((ROOT/rel).read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def close(a,b,tol=TOL):
    err=float(np.max(np.abs(np.asarray(a)-np.asarray(b))))
    assert err<tol,(err,tol)
    return err
def save():
    (OUT/'results.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
def announce(k,v):
    results[k]=v;save();print(k,json.dumps(v),flush=True)

manifest=read('manifest.json');complete=read('progress/complete.json');fingerprint=sha(ROOT/'manifest.json')
assert fingerprint==complete['manifest_sha256']
missing=[]
for rel,digest in manifest['source_sha256'].items():
    if not (ROOT/rel).exists(): missing.append(rel)
    else: assert sha(ROOT/rel)==digest,rel
origins=read('provenance/ORIGINS.json')
for rel,v in origins.items(): assert sha(ROOT/'provenance'/rel)==v['sha256'],rel
expected={f'data/L12_xi{x:.9f}.json' for x in GRID}
assert set(complete['output_sha256'])==expected
assert {str(p.relative_to(ROOT)) for p in (ROOT/'data').glob('*')}==expected
for rel,digest in complete['output_sha256'].items(): assert sha(ROOT/rel)==digest,rel
assert complete['curves']==20 and complete['resource_rows']==8020 and complete['spectral_rows']==260
assert manifest['config']['xi_grid']==GRID
assert manifest['config']['execution_order']==list(reversed(GRID))
assert manifest['config']['negativity_samples']==SAMPLES
announce('hashes',dict(manifest_sha256=fingerprint,verified_output_count=20,
    verified_present_source_count=len(manifest['source_sha256'])-len(missing),missing_manifest_files=missing))

curves={}
maxima={'trace':0.,'hermiticity':0.,'density_spectral_trace':0.,'pt_spectral_trace':0.,'peak_rss_bytes':0}
mins={'density':1.,'negativity':1.}
resources=spectra=0
for xi in GRID:
    o=read(f'data/L12_xi{xi:.9f}.json');curves[xi]=o
    fields={'L','xi','J','b','h','gamma','horizon','negativity_samples','rows','max_trace_error','max_hermiticity_error','seconds','peak_rss_bytes','manifest_sha256','resumed_from_t'}
    if xi==1: fields.add('ideal_baseline_regression')
    assert set(o)==fields
    for k,v in dict(L=12,xi=xi,J=np.pi/4,b=-np.pi/4,h=1.,gamma=.1,horizon=400,negativity_samples=SAMPLES,manifest_sha256=fingerprint).items(): assert o[k]==v,(xi,k)
    assert o['resumed_from_t'] is None or (type(o['resumed_from_t']) is int and 0<=o['resumed_from_t']<=400)
    for k in ('max_trace_error','max_hermiticity_error'):
        assert math.isfinite(o[k]) and 0<=o[k]<TOL
    maxima['trace']=max(maxima['trace'],o['max_trace_error']);maxima['hermiticity']=max(maxima['hermiticity'],o['max_hermiticity_error'])
    assert math.isfinite(o['seconds']) and o['seconds']>0
    assert type(o['peak_rss_bytes']) is int and 0<o['peak_rss_bytes']<=3*2**30
    maxima['peak_rss_bytes']=max(maxima['peak_rss_bytes'],o['peak_rss_bytes'])
    rows=o['rows'];assert len(rows)==401
    for t,r in enumerate(rows):
        resources+=1
        assert set(r)=={'t'}|RES|(SPEC if t in SAMPLES else set()),(xi,t)
        assert type(r['t']) is int and r['t']==t
        assert all(type(v) in (int,float) and math.isfinite(v) for v in r.values())
        p=r['probability'];q=r['bell_overlap'];f=r['teleportation_fidelity']
        assert 0<p<=1+TOL and -TOL<=q<=1+TOL and 1/3-TOL<=f<=1+TOL
        close(f,(1+2*q)/3);close(r['weighted_advantage'],p*(f-2/3))
        close(r['fallback_fidelity'],2/3+max(0,p*(f-2/3)))
        assert 2/3-TOL<=r['fallback_fidelity']<=1+TOL
        if t in SAMPLES:
            spectra+=1
            en=r['log_negativity_nats'];den=r['min_density_eigenvalue'];pt=r['min_pt_eigenvalue']
            assert -TOL<=en<=6*np.log(2)+TOL
            assert -TOL<=den<=1/4096+TOL
            assert max(-.5,-np.expm1(en)/2)-TOL<=pt<=1/4096+TOL
            mins['density']=min(mins['density'],den);mins['negativity']=min(mins['negativity'],en)
            for k in ('density','pt'):
                er=r[k+'_spectral_trace_error'];assert 0<=er<TOL
                maxima[k+'_spectral_trace']=max(maxima[k+'_spectral_trace'],er)
                assert r[k+'_spectrum_seconds']>0
        if t==0:
            for k,v in dict(probability=1/1024,bell_overlap=.5,teleportation_fidelity=2/3,weighted_advantage=0,fallback_fidelity=2/3,log_negativity_nats=0,min_density_eigenvalue=0,min_pt_eigenvalue=0).items(): close(r[k],v)
assert resources==8020 and spectra==260
announce('full_schema_and_bounds',dict(resource_rows=resources,spectral_rows=spectra,maxima=maxima,minima=mins))

baseline=read('provenance/dynamics_L12_xi1.json')
assert [r['t'] for r in baseline['rows']]==list(range(401))
err={k:0. for k in RES|{'log_negativity_nats','min_pt_eigenvalue'}}
for r,ref in zip(curves[1.]['rows'],baseline['rows']):
    for k in err:
        if k in r and k in ref: err[k]=max(err[k],close(r[k],ref[k],REG))
assert baseline['negativity_samples']==SAMPLES
announce('frozen_ideal_regression',dict(resource_times=401,spectral_times=13,tolerance=REG,max_errors=err,
    caveat='Density minima are not directly comparable: baseline density is sector-restricted, production full-space.'))

modspec=importlib.util.spec_from_file_location('frozen_runner',ROOT/'scripts/run.py')
runner=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(runner)
assert runner.CONFIG==manifest['config']
X=np.array([[0,1],[1,0]],complex);Z=np.diag([1.,-1.]);I=np.eye(2)
def kronall(ops):
    a=np.array([[1.]])
    for op in ops:a=np.kron(a,op)
    return a
def operators(n,op):return [kronall([op if i==j else I for i in range(n)]) for j in range(n)]
def unitary(n,j=np.pi/4):
    zz=operators(n,Z);xx=operators(n,X)
    hi=sum(j*zz[k]@zz[(k+1)%n]+zz[k] for k in range(n))
    return expm(1j*np.pi/4*sum(xx))@expm(-1j*hi)
def lindblad(n,xi):
    zz=operators(n,Z);d=2**n;ident=np.eye(d)
    gen=np.zeros((d*d,d*d),complex)
    for j in range(n):
        for k in range(n):
            c=.1*(1 if j==k else xi);zkzj=zz[k]@zz[j]
            gen+=c*(np.kron(zz[k].T,zz[j])-.5*np.kron(ident,zkzj)-.5*np.kron(zkzj.T,ident))
    return expm(gen)
def direct_step(rho,u,channel):
    evolved=u@rho@u.conj().T
    return (channel@evolved.reshape(-1,order='F')).reshape(rho.shape,order='F')
def pt_direct(rho,n):
    h=2**(n//2);pt=np.empty_like(rho)
    for a in range(h):
        for b in range(h):
            for c in range(h):
                for d in range(h):pt[a*h+b,c*h+d]=rho[c*h+b,a*h+d]
    return pt
def decoder_direct(rho,n):
    m=n//2;h=2**m;k=np.zeros((2,h))
    bits=[i%2 for i in range(m)]
    a=sum(v*2**(m-1-i) for i,v in enumerate(bits));b=h-1-a
    k[0,a]=1;k[1,b]=1;kk=np.kron(k,k)
    s=kk@rho@kk.T;p=np.trace(s).real
    bell=np.array([1,0,0,1] if m%2==0 else [0,1,1,0])/np.sqrt(2)
    q=(bell@s@bell).real/p;f=(1+2*q)/3
    return dict(probability=p,bell_overlap=q,teleportation_fidelity=f,weighted_advantage=p*(f-2/3),fallback_fidelity=2/3+max(0,p*(f-2/3)))
def obs_check(rho,n):
    out=runner.extraction(rho,n);ref=decoder_direct(rho,n)
    de=max(close(out[k],ref[k]) for k in RES)
    got=runner.spectra(rho,n);pv=eigvalsh(pt_direct(rho,n));ev=eigvalsh(rho)
    se=max(close(got['log_negativity_nats'],np.log(np.abs(pv).sum())),close(got['min_pt_eigenvalue'],pv[0]),close(got['min_density_eigenvalue'],ev[0]))
    return de,se
rng=np.random.default_rng(410217);g=rng.normal(size=(16,16))+1j*rng.normal(size=(16,16));rho0=g@g.conj().T;rho0/=np.trace(rho0)
state_err=decoder_err=spectral_err=0.
for xi in [-1/3,0,.5,.99,1.]:
    u=unitary(4);ch=lindblad(4,xi);phase,mask=runner.setup(4,xi)
    a=rho0.copy();b=rho0.copy()
    for t in range(1,6):
        a=direct_step(a,u,ch);b=runner.step(b,4,phase,mask)
        state_err=max(state_err,close(a,b))
        de,se=obs_check(b,4);decoder_err=max(decoder_err,de);spectral_err=max(spectral_err,se)
    # Product input, J=0: correlated random local rotations preserve separability.
    phase,mask=runner.setup(4,xi,0);u0=unitary(4,0);a=np.ones((16,16),complex)/16;b=a.copy()
    for t in range(41):
        if t:a=direct_step(a,u0,ch);b=runner.step(b,4,phase,mask)
        state_err=max(state_err,close(a,b))
        close(np.log(abs(eigvalsh(pt_direct(a,4))).sum()),0)
        assert decoder_direct(a,4)['teleportation_fidelity']<=2/3+TOL
for n in [4,6]:
    d=2**n
    for rho in [np.ones((d,d),complex)/d,np.eye(d,dtype=complex)/d]:
        close(runner.spectra(rho,n)['log_negativity_nats'],0);de,se=obs_check(rho,n)
        decoder_err=max(decoder_err,de);spectral_err=max(spectral_err,se)
    m=n//2;aa=int(''.join(str(i%2) for i in range(m)),2);bb=2**m-1-aa
    v=np.zeros(d,complex)
    inds=[aa*2**m+aa,bb*2**m+bb] if m%2==0 else [aa*2**m+bb,bb*2**m+aa]
    v[inds]=1/np.sqrt(2);rho=np.outer(v,v.conj())
    de,se=obs_check(rho,n);decoder_err=max(decoder_err,de);spectral_err=max(spectral_err,se)
    close(runner.spectra(rho,n)['log_negativity_nats'],np.log(2))
    close(runner.extraction(rho,n)['probability'],1);close(runner.extraction(rho,n)['teleportation_fidelity'],1)
announce('independent_dense_reference',dict(sizes=[4,6],generic_L4_steps=5,xi=[-1/3,0,.5,.99,1],J0_steps=40,
    max_state_error=state_err,max_decoder_error=decoder_err,max_spectral_error=spectral_err,tolerance=TOL))

# Independent cheap L12 first-step resource reference: tensor single-site kick,
# explicit Ising energy and covariance quadratic form, only decoder submatrix.
n=12;d=4096;m=6;bits=np.array([list(map(int,format(i,'012b'))) for i in range(d)]);z=1-2*bits
energy=np.array([sum(np.pi/4*row[j]*row[(j+1)%n]+row[j] for j in range(n)) for row in z])
v=np.exp(-1j*energy)/np.sqrt(d);gate=expm(1j*np.pi/4*X)
for site in range(n):
    ar=np.moveaxis(v.reshape([2]*n),site,0)
    ar=np.einsum('ab,b...->a...',gate,ar)
    v=np.moveaxis(ar,0,site).reshape(-1)
aa=int('010101',2);bb=int('101010',2);ids=[a*64+b for a in (aa,bb) for b in (aa,bb)]
first_err={k:0. for k in RES}
for xi in GRID:
    cov=np.full((n,n),xi);np.fill_diagonal(cov,1.)
    s=np.empty((4,4),complex)
    for a,i in enumerate(ids):
        for b,j in enumerate(ids):
            diff=z[i]-z[j];s[a,b]=v[i]*v[j].conjugate()*np.exp(-.1/2*(diff@cov@diff))
    p=np.trace(s).real;bell=np.array([1,0,0,1])/np.sqrt(2);q=(bell@s@bell).real/p;f=(1+2*q)/3
    expected=dict(probability=p,bell_overlap=q,teleportation_fidelity=f,weighted_advantage=p*(f-2/3),fallback_fidelity=2/3+max(0,p*(f-2/3)))
    for k in RES:first_err[k]=max(first_err[k],close(curves[xi]['rows'][1][k],expected[k]))
announce('independent_L12_t1_all_grid',dict(curves=20,max_errors=first_err,tolerance=TOL))

# One full actual imperfect L12 state and both complete spectra, independently
# constructed from the pure kicked amplitudes and covariance quadratic form.
xi=.99;cov=np.full((n,n),xi);np.fill_diagonal(cov,1.)
zc=z@cov;quad=np.einsum('ij,ij->i',zc,z)
decay=zc@z.T
decay*=-2;decay+=quad[:,None];decay+=quad[None,:]
decay*=(-.1/2);np.exp(decay,out=decay)
rho=v[:,None]*v.conj()[None,:];rho*=decay
del decay
ev=eigvalsh(rho,check_finite=True)
# Independently transpose the A blocks by explicit indexing (64x64 blocks).
pt=np.empty_like(rho)
for a in range(64):
    for c in range(64):pt[a*64:(a+1)*64,c*64:(c+1)*64]=rho[c*64:(c+1)*64,a*64:(a+1)*64]
pv=eigvalsh(pt,check_finite=True)
close(np.trace(rho),1);close(ev.sum(),1);close(pv.sum(),1)
assert ev[0]>=-TOL
ref=dict(log_negativity_nats=float(np.log(abs(pv).sum())),min_density_eigenvalue=float(ev[0]),min_pt_eigenvalue=float(pv[0]))
actual_errors={k:close(curves[xi]['rows'][1][k],value) for k,value in ref.items()}
announce('independent_full_L12_imperfect_point',dict(xi=xi,t=1,reference=ref,max_errors=actual_errors,
    density_trace_error=float(abs(ev.sum()-1)),pt_trace_error=float(abs(pv.sum()-1)),tolerance=TOL))
del rho,pt,ev,pv

for n,xi in [(12,-1/9),(12,float('nan')),(12,float('inf')),(4,-.34),(4,1.01),(2,0),(5,0),(True,0),(4.0,0)]:
    try:runner.setup(n,xi)
    except (ValueError,RuntimeError):pass
    else:raise AssertionError(('accepted invalid input',n,xi))
announce('invalid_domains',dict(rejected=9))

reg_errors={k:0. for k in RES|{'log_negativity_nats','min_pt_eigenvalue'}}
for xi in [.5,.99,1.]:
    old=read(f'provenance/L10_xi{xi:.9f}.json');rho=np.ones((1024,1024),complex)/1024;phase,mask=runner.setup(10,xi)
    for t in range(6):
        if t:rho=runner.step(rho,10,phase,mask)
        got={**runner.extraction(rho,10),**runner.spectra(rho,10)}
        for k in reg_errors:
            if k in old['rows'][t]:reg_errors[k]=max(reg_errors[k],close(got[k],old['rows'][t][k],REG))
announce('frozen_L10_regression',dict(curves=3,times=6,max_errors=reg_errors,tolerance=REG))
announce('completion',dict(status='all-executed-checks-pass',scope='finite L12 full-density twenty-xi grid, resources t=0..400, exact spectral evaluations only at thirteen scheduled times',
    environment=dict(executable=sys.executable,numpy=np.__version__)))
