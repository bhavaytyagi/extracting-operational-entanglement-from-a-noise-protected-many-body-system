"""Exact full-density L12 sweep, atomic resumable state, no symmetry reduction."""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_key] = '2'
import argparse
import contextlib
import datetime
import fcntl
import hashlib
import json
import platform
import resource
import sys
import tempfile
import time
from pathlib import Path
import numpy as np
import scipy
from scipy.linalg import eigvalsh

HERE = Path(__file__).resolve().parents[1]
TOL = 1e-10
SAMPLES = [0,1,2,3,4,5,10,20,40,80,150,250,400]
GRID = [-1/11,-.05,0,.1,.2,.3,.4,.5,.6,.7,.8,.85,.9,.95,.97,.98,.99,.995,.999,1.]
CONFIG = dict(L=12, J=np.pi/4, b=-np.pi/4, h=1., gamma=.1, horizon=400,
              xi_grid=GRID, execution_order=list(reversed(GRID)), negativity_samples=SAMPLES, checkpoint_period=10,
              coherent_kernel='exact-D-Hadamard-D-b=-pi/4',
              dtype='complex128', protocol='Ising-kick-accumulated-dephasing',
              cut='first-six-vs-last-six', logarithm='natural', threads=2,
              tolerance=TOL, peak_rss_limit_bytes=3*2**30)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def array_digest(a):
    require(a.flags.c_contiguous, 'checkpoint state must be C contiguous')
    return hashlib.sha256(memoryview(a).cast('B')).hexdigest()


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def peak():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == 'darwin' else value*1024)


def atomic_bytes(path, value, immutable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.'+path.name+'.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(value)
            stream.flush()
            os.fsync(stream.fileno())
        if immutable:
            os.link(temp, path)  # atomic create, fails if target already exists
            os.unlink(temp)
        else:
            os.replace(temp, path)
        dirfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def atomic_json(path, value, immutable=False):
    atomic_bytes(path, (json.dumps(value, indent=2, allow_nan=False)+'\n').encode(), immutable)


def status(folder, **values):
    data = dict(updated_utc=now(), pid=os.getpid(), peak_rss_bytes=peak(), **values)
    atomic_json(Path(folder)/'status.json', data)
    print(json.dumps(data), flush=True)


@contextlib.contextmanager
def writer_lock(folder):
    Path(folder).mkdir(parents=True, exist_ok=True)
    with (Path(folder)/'writer.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError('Another campaign process holds the writer lock') from exc
        yield


def freeze():
    paths = [HERE/'SPEC.md', HERE/'KERNEL.md', HERE/'README.md', *sorted((HERE/'scripts').glob('*.py')),
             *sorted(p for p in (HERE/'provenance').glob('*') if p.is_file()), *sorted((HERE/'checks').glob('*.json'))]
    obj = dict(created_utc=now(), config=CONFIG,
               source_sha256={str(p.relative_to(HERE)): digest(p) for p in paths},
               environment=dict(python=sys.version, executable=sys.executable,
                                numpy=np.__version__, scipy=scipy.__version__,
                                platform=platform.platform()))
    atomic_json(HERE/'manifest.json', obj, immutable=True)
    print(digest(HERE/'manifest.json'))


def validate_manifest():
    obj = json.loads((HERE/'manifest.json').read_text())
    require(obj['config'] == CONFIG, 'Configuration differs from immutable manifest')
    for rel, sha in obj['source_sha256'].items():
        require(digest(HERE/rel) == sha, f'Frozen input changed: {rel}')
    env = obj['environment']
    require(env['executable'] == sys.executable and env['numpy'] == np.__version__
            and env['scipy'] == scipy.__version__ and env['python'] == sys.version,
            'Numerical environment differs from frozen manifest')
    return digest(HERE/'manifest.json')


def setup(n, xi, j=np.pi/4):
    if isinstance(n, bool) or not isinstance(n, int) or n not in (4,6,8,10,12):
        raise ValueError('validated even sizes4..12 only')
    if not np.isfinite(xi) or not -1/(n-1) <= xi <= 1:
        raise ValueError('xi outside complete-graph covariance interval')
    if not np.isfinite(j):
        raise ValueError('finite J required')
    d = 1 << n
    idx = np.arange(d)
    bits = (idx[:,None] >> np.arange(n-1,-1,-1)) & 1
    z = 1-2*bits
    energy = j*(z*np.roll(z,1,axis=1)).sum(axis=1)+z.sum(axis=1)
    phase = np.exp(-1j*energy)
    distance = np.zeros((d,d), np.int16)
    for k in range(n):
        distance += bits[:,k,None] != bits[None,:,k]
    mz = z.sum(axis=1)
    exponent = -.05*(4*(1-xi)*distance+xi*(mz[:,None]-mz[None,:])**2)
    require(float(np.max(exponent)) < TOL, 'dephasing exponent positive')
    mask = np.exp(exponent)
    require(float(np.max(abs(np.diag(mask)-1))) < TOL, 'dephasing diagonal is not1')
    return phase, mask


def step(rho,n,phase,mask):
    # U_K = D^tensor(n) H^tensor(n) D^tensor(n), D=diag(1,i).
    # Each unnormalized Walsh transform supplies sqrt(d); two sides give1/d.
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


def invariants(rho):
    # Chunked to avoid creating full-size conjugate/residual temporary matrices.
    require(rho.ndim == 2 and rho.shape[0] == rho.shape[1], 'density shape')
    herm = 0.
    for begin in range(0, len(rho), 128):
        block = rho[begin:begin+128]
        require(bool(np.isfinite(block).all()), 'non-finite density')
        herm = max(herm, float(np.max(abs(block-rho[:,begin:begin+128].conj().T))))
    tr = float(abs(np.trace(rho)-1))
    require(max(tr, herm) < TOL, f'density invariants failed: trace={tr}, herm={herm}')
    return tr, herm


def extraction(rho, n):
    m = n//2
    a = int(('01'*m)[:m], 2)
    b = (1 << m)-1-a
    ii = [(r << m)|c for r in (a,b) for c in (a,b)]
    sigma = rho[np.ix_(ii,ii)]
    probability = float(np.trace(sigma).real)
    require(0 < probability <= 1+TOL, 'decoder probability out of range')
    bell = np.array([0,1,1,0] if m%2 else [1,0,0,1])/np.sqrt(2)
    overlap = float(np.vdot(bell,sigma@bell).real)/probability
    require(-TOL <= overlap <= 1+TOL, 'decoder Bell overlap out of range')
    fidelity = (1+2*overlap)/3
    advantage = probability*(fidelity-2/3)
    return dict(probability=probability, bell_overlap=overlap,
                teleportation_fidelity=fidelity, weighted_advantage=advantage,
                fallback_fidelity=2/3+max(0., advantage))


def spectra(rho, n, callback=None):
    if callback:
        callback('density-spectrum')
    start = time.monotonic()
    ev = eigvalsh(rho, check_finite=False)
    density_seconds = time.monotonic()-start
    require(bool(np.isfinite(ev).all()), 'non-finite density spectrum')
    require(float(ev[0]) >= -TOL, f'density positivity failed: {ev[0]}')
    require(abs(float(ev.sum())-1) < TOL, 'density spectral trace failed')
    if callback:
        callback('partial-transpose-spectrum')
    d = 1 << n
    h = 1 << (n//2)
    pt = rho.reshape(h,h,h,h).transpose(2,1,0,3).reshape(d,d)
    start = time.monotonic()
    pv = eigvalsh(pt, check_finite=False)
    pt_seconds = time.monotonic()-start
    require(bool(np.isfinite(pv).all()), 'non-finite partial-transpose spectrum')
    require(abs(float(pv.sum())-1) < TOL, 'partial-transpose spectral trace failed')
    return dict(log_negativity_nats=float(np.log(abs(pv).sum())),
                min_density_eigenvalue=float(ev[0]), min_pt_eigenvalue=float(pv[0]),
                density_spectral_trace_error=abs(float(ev.sum())-1),
                pt_spectral_trace_error=abs(float(pv.sum())-1),
                density_spectrum_seconds=density_seconds, pt_spectrum_seconds=pt_seconds)


def checkpoint(path, rho, metadata):
    meta = dict(metadata, density_sha256=array_digest(rho))
    path = Path(path)
    fd, temp = tempfile.mkstemp(prefix='.checkpoint.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            np.savez(stream, rho=rho, metadata=np.array(json.dumps(meta, allow_nan=False)))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        dirfd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


RESOURCE_FIELDS = {'probability','bell_overlap','teleportation_fidelity',
                   'weighted_advantage','fallback_fidelity'}
SPECTRAL_FIELDS = {'log_negativity_nats','min_density_eigenvalue','min_pt_eigenvalue',
                   'density_spectral_trace_error','pt_spectral_trace_error',
                   'density_spectrum_seconds','pt_spectrum_seconds'}


def finite_number(value):
    return type(value) in (int,float) and np.isfinite(value)


def validate_summaries(obj):
    for key in ('max_trace_error','max_hermiticity_error'):
        require(key in obj and finite_number(obj[key]) and 0 <= obj[key] < TOL,
                f'invalid invariant summary: {key}')


def validate_rows(rows, n, last_t):
    require(type(rows) is list and len(rows) == last_t+1, 'row count mismatch')
    for t, row in enumerate(rows):
        expected = {'t'} | RESOURCE_FIELDS | (SPECTRAL_FIELDS if t in SAMPLES else set())
        require(type(row) is dict and set(row) == expected, f'row {t} field schema mismatch')
        require(type(row['t']) is int and row['t'] == t, f'row {t} time mismatch')
        require(all(finite_number(value) for value in row.values()), f'nonfinite/non-numeric row {t}')
        p, overlap, fidelity = row['probability'], row['bell_overlap'], row['teleportation_fidelity']
        require(0 < p <= 1+TOL and -TOL <= overlap <= 1+TOL and 1/3-TOL <= fidelity <= 1+TOL,
                f'resource bounds failed at {t}')
        advantage = p*(fidelity-2/3)
        require(abs(fidelity-(1+2*overlap)/3) < TOL and
                abs(row['weighted_advantage']-advantage) < TOL and
                abs(row['fallback_fidelity']-(2/3+max(0.,advantage))) < TOL,
                f'resource algebra identities failed at {t}')
        if t in SAMPLES:
            en = row['log_negativity_nats']
            require(-TOL <= en <= (n//2)*np.log(2)+TOL, f'negativity bounds failed at {t}')
            require(-TOL <= row['min_density_eigenvalue'] <= 1/(1<<n)+TOL,
                    f'density spectral bound failed at {t}')
            # No PT eigenvalue can exceed its spectral average as the minimum;
            # its negative magnitude cannot exceed the total negative spectral mass.
            require(-np.expm1(en)/2-TOL <= row['min_pt_eigenvalue'] <= 1/(1<<n)+TOL,
                    f'PT spectral bound failed at {t}')
            for key in ('density_spectral_trace_error','pt_spectral_trace_error'):
                require(0 <= row[key] < TOL, f'invalid {key} at {t}')
            for key in ('density_spectrum_seconds','pt_spectrum_seconds'):
                require(row[key] >= 0, f'negative spectrum runtime at {t}')
        if t == 0:
            require(abs(p-4/(1<<n)) < TOL and abs(overlap-.5) < TOL and
                    abs(fidelity-2/3) < TOL and abs(row['log_negativity_nats']) < TOL,
                    'initial plus-product reference failed')


def load_checkpoint(path, fingerprint, n, xi, horizon, j):
    with np.load(path, allow_pickle=False) as archive:
        rho = archive['rho']
        meta = json.loads(str(archive['metadata']))
    for key, value in dict(fingerprint=fingerprint,L=n,xi=xi,horizon=horizon,J=j).items():
        require(meta.get(key) == value, f'checkpoint {key} mismatch')
    require(rho.shape == (1 << n, 1 << n) and rho.dtype == np.complex128,
            'checkpoint density shape/dtype mismatch')
    require(meta['density_sha256'] == array_digest(rho), 'checkpoint density checksum mismatch')
    t = meta['t']
    require(type(t) is int and 0 <= t <= horizon, 'checkpoint time invalid')
    validate_rows(meta['rows'],n,t)
    validate_summaries(meta)
    require(finite_number(meta['elapsed_seconds']) and meta['elapsed_seconds'] >= 0, 'invalid checkpoint elapsed time')
    invariants(rho)
    return rho, meta


def tag(n, xi):
    return f'L{n}_xi{xi:.9f}'


def result_check(obj, n, xi, horizon, fingerprint):
    for key, value in dict(L=n,xi=xi,horizon=horizon,J=np.pi/4,b=-np.pi/4,h=1.,gamma=.1,
                           manifest_sha256=fingerprint).items():
        require(obj.get(key) == value, f'completed result {key} mismatch')
    require(obj['negativity_samples'] == [t for t in SAMPLES if t <= horizon], 'bad samples')
    validate_rows(obj['rows'],n,horizon)
    validate_summaries(obj)
    require(finite_number(obj['seconds']) and obj['seconds'] >= 0, 'invalid result runtime')
    require(type(obj['peak_rss_bytes']) is int and 0 < obj['peak_rss_bytes'] <= CONFIG['peak_rss_limit_bytes'],
            'invalid result peak RSS')


def trajectory(folder, n, xi, horizon, fingerprint, j=np.pi/4, stop_at=None):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    cp = folder/'checkpoint.npz'
    start = time.monotonic()
    status(folder, stage='setup', L=n, xi=xi, t=None)
    phase, mask = setup(n, xi, j)
    if cp.exists():
        rho, meta = load_checkpoint(cp, fingerprint, n, xi, horizon, j)
        rows = meta['rows']
        maxtr, maxherm = meta['max_trace_error'], meta['max_hermiticity_error']
        resumed = meta['t']
        elapsed_before = meta['elapsed_seconds']
        next_t = resumed+1
    else:
        d = 1 << n
        rho = np.ones((d,d), complex)/d
        rows = []
        maxtr = maxherm = elapsed_before = 0.
        resumed = None
        next_t = 0
    for t in range(next_t, horizon+1):
        if t > 0:
            status(folder, stage='step', L=n, xi=xi, t=t, completed_t=t-1)
            rho = step(rho, n, phase, mask)
        tr, herm = invariants(rho)
        maxtr, maxherm = max(maxtr,tr), max(maxherm,herm)
        row = dict(t=t, **extraction(rho,n))
        if t in SAMPLES:
            row.update(spectra(rho, n, lambda stage: status(folder,stage=stage,L=n,xi=xi,t=t)))
            if t == 0 or j == 0:
                require(abs(row['log_negativity_nats']) < TOL, 'zero-negativity reference failed')
        if j == 0:
            require(row['teleportation_fidelity'] <= 2/3+TOL, 'J0 fidelity control failed')
        rows.append(row)
        require(peak() <= CONFIG['peak_rss_limit_bytes'], 'measured peak RSS exceeds configured ceiling')
        if t % CONFIG['checkpoint_period'] == 0 or t in SAMPLES or t == horizon or t == stop_at:
            meta = dict(fingerprint=fingerprint,L=n,xi=xi,J=j,horizon=horizon,t=t,rows=rows,
                        max_trace_error=maxtr,max_hermiticity_error=maxherm,
                        elapsed_seconds=elapsed_before+time.monotonic()-start)
            status(folder, stage='checkpoint', L=n, xi=xi, t=t)
            checkpoint(cp, rho, meta)
        status(folder, stage='period-complete', L=n, xi=xi, t=t,
               trace_error=tr, hermiticity_error=herm)
        if t == stop_at:
            return None
    result = dict(L=n,xi=xi,J=j,b=-np.pi/4,h=1.,gamma=.1,horizon=horizon,
                  negativity_samples=[t for t in SAMPLES if t <= horizon],rows=rows,
                  max_trace_error=maxtr,max_hermiticity_error=maxherm,
                  seconds=elapsed_before+time.monotonic()-start,peak_rss_bytes=peak(),
                  manifest_sha256=fingerprint,resumed_from_t=resumed)
    return result


def ideal_regression(result):
    if result['L'] != 12 or result['xi'] != 1.:
        return
    old = json.loads((HERE/'provenance/dynamics_L12_xi1.json').read_text())
    keys = ('probability','bell_overlap','teleportation_fidelity')
    resource_error = max(abs(r[k]-old['rows'][r['t']][k]) for r in result['rows'] for k in keys)
    negativity_error = max(abs(r['log_negativity_nats']-old['rows'][r['t']]['log_negativity_nats'])
                           for r in result['rows'] if 'log_negativity_nats' in r)
    require(max(resource_error, negativity_error) < 1e-9, 'L12 ideal baseline regression failed')
    result['ideal_baseline_regression'] = dict(resource_max_error=resource_error,
                                              negativity_max_error=negativity_error)


def cleanup_completed_checkpoint(folder, result, fingerprint):
    """Close the crash window between atomic result creation and checkpoint unlink."""
    cp = Path(folder)/'checkpoint.npz'
    if not cp.exists():
        return
    with np.load(cp, allow_pickle=False) as archive:
        meta = json.loads(str(archive['metadata']))
    if meta.get('xi') != result['xi']:
        return  # checkpoint can belong to a later, unfinished curve
    _, meta = load_checkpoint(cp, fingerprint, result['L'], result['xi'],
                              result['horizon'], result['J'])
    require(meta['t'] == result['horizon'] and meta['rows'] == result['rows'],
            'completed result and stale checkpoint disagree')
    cp.unlink()


def production(approval):
    fingerprint = validate_manifest()
    approved = json.loads(Path(approval).read_text())
    require(approved.get('status') == 'accepted-for-production' and
            approved.get('manifest_sha256') == fingerprint, 'fresh review approval missing or stale')
    folder = HERE/'progress'
    with writer_lock(folder):
        # Completed curves can be skipped only after their identity and grids pass.
        for xi in CONFIG['execution_order']:
            out = HERE/'data'/f'{tag(12,xi)}.json'
            if out.exists():
                existing = json.loads(out.read_text())
                result_check(existing,12,xi,400,fingerprint)
                cleanup_completed_checkpoint(folder,existing,fingerprint)
                continue
            result = trajectory(folder,12,xi,400,fingerprint)
            result_check(result,12,xi,400,fingerprint)
            ideal_regression(result)
            atomic_json(out,result,immutable=True)
            cleanup_completed_checkpoint(folder,result,fingerprint)
            status(folder,stage='curve-complete',L=12,xi=xi,t=400,result=str(out.relative_to(HERE)))
        outputs = {f'data/{tag(12,xi)}.json': digest(HERE/'data'/f'{tag(12,xi)}.json') for xi in GRID}
        complete = dict(completed_utc=now(),manifest_sha256=fingerprint,output_sha256=outputs,
                        curves=20,resource_rows=8020,spectral_rows=260,
                        status='production-complete-pending-independent-final-review')
        if (folder/'complete.json').exists():
            prior_complete = json.loads((folder/'complete.json').read_text())
            require(prior_complete['manifest_sha256'] == fingerprint and prior_complete['output_sha256'] == outputs,
                    'existing completion receipt differs from current immutable outputs')
        else:
            atomic_json(folder/'complete.json',complete,immutable=True)
        status(folder,stage='complete',curves=20)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['freeze','all'])
    parser.add_argument('--approval')
    args = parser.parse_args()
    if args.command == 'freeze':
        freeze()
    else:
        require(args.approval is not None, '--approval required')
        try:
            production(args.approval)
        except BaseException as exc:
            atomic_json(HERE/'progress/error.json',dict(time_utc=now(),type=type(exc).__name__,message=str(exc)))
            raise


if __name__ == '__main__':
    main()
