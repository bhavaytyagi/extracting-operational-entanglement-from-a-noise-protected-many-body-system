"""Separate POSIX/macOS/Linux reproduction adapter; frozen producer stays unchanged.

Example: python portable_rerun.py --campaign data/xi_sweep --out rerun-smoke --smoke
Full new L12 curve: same arguments with --xi .99 instead of --smoke.
All 20 curves: --all. This is expensive and is never a default action.
Only a new output directory is accepted. Final density checkpoints are retained.
"""
import argparse, hashlib, importlib.util, json, os, platform, sys
from pathlib import Path
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
    os.environ[key]='2'
import numpy as np
import scipy
from scipy.linalg import expm

EXPECTED_MANIFEST='b45bbcc00aa4bf601ef90d428f2ea49696e486a79e1e38ee2d9d3c32c96f3e0f'
TOL=1e-10
REG=1e-9
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
def write(p,d): p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
def require(value,message):
    if not value: raise RuntimeError(message)

def load_source(campaign):
    require(sha(campaign/'manifest.json')==EXPECTED_MANIFEST,'Wrong frozen campaign manifest')
    manifest=read(campaign/'manifest.json')
    for rel,value in manifest['source_sha256'].items():
        require(sha(campaign/rel)==value,'Changed or missing original source: '+rel)
    done=read(campaign/'progress/complete.json')
    require(done['manifest_sha256']==EXPECTED_MANIFEST,'Wrong completion binding')
    for rel,value in done['output_sha256'].items(): require(sha(campaign/rel)==value,'Changed archived result: '+rel)
    spec=importlib.util.spec_from_file_location('frozen_l12_kernels',campaign/'scripts/run.py')
    c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
    require(c.CONFIG==manifest['config'],'Imported kernel configuration mismatch')
    return c,manifest

def smoke(c,out):
    n=4; d=1<<n; I=np.eye(d); one=np.eye(2)
    Z=np.diag([1.,-1.]); X=np.array([[0.,1.],[1.,0.]])
    def site(a,j):
        ans=np.array([[1.]])
        for k in range(n):ans=np.kron(ans,a if k==j else one)
        return ans
    zs=[site(Z,j) for j in range(n)]; xs=[site(X,j) for j in range(n)]
    ui=expm(-1j*(np.pi/4*sum(zs[j]@zs[(j+1)%n] for j in range(n))+sum(zs)))
    uk=expm(1j*np.pi/4*sum(xs));uf=uk@ui
    rng=np.random.default_rng(20261111);a=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d))
    rho=a@a.conj().T;rho/=np.trace(rho)
    errors={}
    for xi in [-1/3,0.,.37,1.]:
        covariance=(1-xi)*np.eye(n)+xi*np.ones((n,n))
        generator=np.zeros((d*d,d*d),complex)
        for i in range(n):
            for j in range(n):
                product=zs[j]@zs[i]
                generator+=.1*covariance[i,j]*(np.kron(zs[j].T,zs[i])-.5*np.kron(I,product)-.5*np.kron(product.T,I))
        coherent=uf@rho@uf.conj().T
        reference=(expm(generator)@coherent.reshape(-1,order='F')).reshape(d,d,order='F')
        phase,mask=c.setup(n,xi);got=c.step(rho,n,phase,mask)
        error=float(np.max(abs(reference-got)))
        require(error<TOL,f'Dense reference mismatch xi={xi}: {error}')
        c.invariants(got);errors[str(xi)]=error
    product=np.ones((d,d),complex)/d;r=c.extraction(product,n)
    require(abs(r['probability']-4/d)<TOL and abs(r['teleportation_fidelity']-2/3)<TOL,'Product reference mismatch')
    sigma=c.spectra(product,n)
    require(abs(sigma['log_negativity_nats'])<TOL,'Product negativity mismatch')
    path=out/'smoke-density.npz';np.savez(path,rho=got)
    with np.load(path,allow_pickle=False) as saved: require(np.array_equal(saved['rho'],got),'Density roundtrip mismatch')
    return dict(status='smoke-pass',scope='L4 generic dense Lindblad reference only; no L12 production',state_entry_tolerance=TOL,reference_max_errors=errors,product=r,density_file=path.name)

def reproduce(c,campaign,out,xi,horizon):
    # Use the original trajectory with unchanged physical assertions and kernels.
    # Its manifest/environment lifecycle is deliberately not invoked: this adapter
    # separately verifies source bytes and records a new environment/run identity.
    folder=out/c.tag(12,xi)
    result=c.trajectory(folder,12,xi,horizon,EXPECTED_MANIFEST)
    c.result_check(result,12,xi,horizon,EXPECTED_MANIFEST)
    old=read(campaign/'data'/f'{c.tag(12,xi)}.json')
    keys=['probability','bell_overlap','teleportation_fidelity','weighted_advantage','fallback_fidelity',
          'log_negativity_nats','min_density_eigenvalue','min_pt_eigenvalue']
    errors={k:0. for k in keys}
    for row in result['rows']:
        ref=old['rows'][row['t']]
        for k in keys:
            if k in row:
                errors[k]=max(errors[k],abs(row[k]-ref[k]))
                require(errors[k]<REG,f'Archived regression mismatch xi={xi},t={row["t"]},field={k},error={errors[k]}')
    c.atomic_json(folder/'result.json',result,immutable=True)
    receipt=dict(xi=xi,horizon=horizon,status='reproduction-pass',archived_regression_tolerance=REG,
                 max_observable_errors=errors,result_sha256=sha(folder/'result.json'),
                 checkpoint_sha256=sha(folder/'checkpoint.npz'))
    write(folder/'comparison.json',receipt)
    return receipt

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--smoke',action='store_true');group.add_argument('--all',action='store_true');group.add_argument('--xi',type=float)
    p.add_argument('--horizon',type=int,default=400)
    args=p.parse_args();campaign=args.campaign.resolve();out=args.out.resolve()
    require(0<=args.horizon<=400,'Horizon must be an integer from0 through400')
    require(out!=campaign and campaign not in out.parents,'Output must be outside frozen campaign')
    require(not out.exists(),'Output already exists; choose a new output directory')
    c,manifest=load_source(campaign)
    if args.xi is not None:require(args.xi in c.GRID,'xi must exactly match a published grid value; for lower endpoint pass -0.09090909090909091')
    out.mkdir(parents=True)
    invocation=dict(source_manifest_sha256=EXPECTED_MANIFEST,adapter_sha256=sha(Path(__file__)),
                    campaign=str(campaign),requested_horizon=args.horizon,mode='smoke' if args.smoke else 'all' if args.all else 'single',
                    environment=dict(python=sys.version,executable=sys.executable,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform()),
                    note='New run; original archived environment lock remains unchanged. No original outputs overwritten.')
    write(out/'invocation.json',invocation)
    try:
        answer=smoke(c,out) if args.smoke else [reproduce(c,campaign,out,x,args.horizon) for x in (c.GRID if args.all else [args.xi])]
        write(out/'receipt.json',dict(status='pass',result=answer));print(json.dumps(answer,indent=2))
    except Exception as exc:
        write(out/'failure.json',dict(type=type(exc).__name__,message=str(exc)));raise
if __name__=='__main__':main()
