"""Author checks, predeclared in SPEC; fresh independent review still required."""
import run as c
import importlib.util
import copy
import subprocess
import tempfile
import json
import time
from pathlib import Path
import numpy as np
from scipy.linalg import expm, eigvalsh

FIELDS=('probability','bell_overlap','teleportation_fidelity','weighted_advantage','fallback_fidelity')


def old_module():
    spec=importlib.util.spec_from_file_location('old_sweep',c.HERE/'provenance/sweep_L10.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    return old


def dense_reference():
    n=4;d=1<<n;x=np.array([[0,1],[1,0]]);z=np.diag([1.,-1.]);eye=np.eye(2)
    def site(op,k):
        a=np.ones((1,1))
        for q in range(n):a=np.kron(a,op if q==k else eye)
        return a
    zs=[site(z,k) for k in range(n)];xs=[site(x,k) for k in range(n)]
    ui=expm(-1j*sum(np.pi/4*zs[k]@zs[(k+1)%n]+zs[k] for k in range(n)))
    uk=expm(1j*np.pi/4*sum(xs));u=uk@ui
    rng=np.random.default_rng(20261103)
    a=rng.normal(size=(d,d))+1j*rng.normal(size=(d,d));rho=a@a.conj().T;rho/=np.trace(rho)
    errors={}
    for xi in (-1/3,0,.5,.99,1.):
        cov=(1-xi)*np.eye(n)+xi*np.ones((n,n));gen=np.zeros((d*d,d*d),complex)
        for j in range(n):
            for k in range(n):
                q=zs[k]@zs[j]
                gen+=.1*cov[j,k]*(np.kron(zs[k].T,zs[j])-.5*np.kron(np.eye(d),q)-.5*np.kron(q.T,np.eye(d)))
        ref=(expm(gen)@(u@rho@u.conj().T).reshape(-1,order='F')).reshape(d,d,order='F')
        phase,mask=c.setup(n,xi);got=c.step(rho,n,phase,mask)
        err=float(np.max(abs(ref-got)));c.require(err<1e-10,'dense Lindblad reference mismatch')
        pt=np.empty_like(ref)
        for a in range(4):
            for b in range(4):
                for aa in range(4):
                    for bb in range(4):pt[aa*4+b,a*4+bb]=ref[a*4+b,aa*4+bb]
        en=float(np.log(abs(eigvalsh(pt)).sum()))
        err_pt=abs(en-c.spectra(got,n)['log_negativity_nats'])
        c.require(err_pt<1e-10,'explicit-index PT mismatch')
        errors[str(xi)]=dict(density_max_error=err,negativity_error=err_pt)
    return errors


def boundary_checks():
    rejected=[]
    for n,xi in [(12,-1/9),(12,-1/11-1e-12),(12,1+1e-12),(12,np.nan),(12,np.inf),(True,0),(3,0),(14,0)]:
        try:c.setup(n,xi)
        except ValueError:rejected.append([str(n),str(xi)])
        else:raise RuntimeError('invalid inputs accepted')
    # Endpoint exponents are checked in the real L12 setup, without a second large allocation.
    for n in (4,6):
        for xi in (-1/(n-1),1.):
            _,mask=c.setup(n,xi)
            c.require(np.min(mask)>0 and np.max(mask)<=1+1e-10,'endpoint mask invalid')
            if xi==1:c.require(mask[1,2]==1.,'collective same-charge coherence not fixed')
            else:c.require(abs(mask[0,-1]-1)<1e-10,'anticorrelated uniform coherence not fixed')
    return rejected


def known_states():
    result={}
    for n in (4,6):
        d=1<<n;m=n//2;a=int(('01'*m)[:m],2);b=(1<<m)-1-a
        ii=[(r<<m)|s for r in (a,b) for s in (a,b)]
        for name,rho,expected_en,expected_p,expected_f in [
            ('plus',np.ones((d,d),complex)/d,0.,4/d,2/3),
            ('mixed',np.eye(d,dtype=complex)/d,0.,4/d,.5)]:
            got=c.extraction(rho,n);en=c.spectra(rho,n)['log_negativity_nats']
            err=max(abs(en-expected_en),abs(got['probability']-expected_p),abs(got['teleportation_fidelity']-expected_f))
            c.require(err<1e-10,'known product/mixed state failed');result[f'L{n}_{name}']=err
        v=np.zeros(d,complex);pair=(1,2) if m%2 else (0,3);v[np.array(ii)[list(pair)]]=1/np.sqrt(2)
        rho=np.outer(v,v.conj());got=c.extraction(rho,n);en=c.spectra(rho,n)['log_negativity_nats']
        err=max(abs(en-np.log(2)),abs(got['probability']-1),abs(got['teleportation_fidelity']-1))
        c.require(err<1e-10,'encoded Bell state failed');result[f'L{n}_bell']=err
    return result


def controls():
    result={}
    for xi in (-1/3,0,.99,1.):
        phase,mask=c.setup(4,xi,0.);rho=np.ones((16,16),complex)/16;worst=0.;maxf=0.
        for t in range(41):
            c.invariants(rho);got=c.extraction(rho,4);maxf=max(maxf,got['teleportation_fidelity'])
            if t in c.SAMPLES:worst=max(worst,abs(c.spectra(rho,4)['log_negativity_nats']))
            if t<40:rho=c.step(rho,4,phase,mask)
        c.require(worst<1e-10 and maxf<=2/3+1e-10,'J0 control failed')
        result[str(xi)]=dict(max_absolute_negativity=worst,max_fidelity=maxf)
    return result


def l10_regression():
    result={};old=old_module()
    rng=np.random.default_rng(713)
    a=rng.normal(size=(1024,32))+1j*rng.normal(size=(1024,32));rho=a@a.conj().T;rho/=np.trace(rho)
    phase,mask=c.setup(10,.37);oldphase,oldmask=old.setup(10,.37)
    err=float(np.max(abs(c.step(rho,10,phase,mask)-old.step(rho,10,oldphase,oldmask))))
    c.require(err<1e-10,'generic L10 old kernel mismatch');result['generic_state_error']=err
    del a,rho,phase,mask,oldphase,oldmask
    for xi in (.5,.99,1.):
        baseline=json.loads((c.HERE/'provenance'/f'L10_xi{xi:.9f}.json').read_text())
        phase,mask=c.setup(10,xi);rho=np.ones((1024,1024),complex)/1024;resource_error=negative_error=0.
        for t in range(6):
            c.invariants(rho);got=c.extraction(rho,10);base=baseline['rows'][t]
            resource_error=max(resource_error,max(abs(got[k]-base[k]) for k in FIELDS))
            negative_error=max(negative_error,abs(c.spectra(rho,10)['log_negativity_nats']-base['log_negativity_nats']))
            if t<5:rho=c.step(rho,10,phase,mask)
        c.require(max(resource_error,negative_error)<1e-9,'L10 regression failed')
        result[str(xi)]=dict(resource_max_error=resource_error,negativity_max_error=negative_error)
    return result


def resume_checks():
    # Temp directories live inside owned campaign; remove automatically after check.
    with tempfile.TemporaryDirectory(dir=c.HERE/'checks') as tmp:
        root=Path(tmp);straight=root/'straight';resumed=root/'resumed'
        a=c.trajectory(straight,4,.99,10,'test-fingerprint')
        c.require(c.trajectory(resumed,4,.99,10,'test-fingerprint',stop_at=4) is None,'stop hook failed')
        b=c.trajectory(resumed,4,.99,10,'test-fingerprint')
        def stable(rows):
            return [{k:v for k,v in row.items() if not k.endswith('_seconds')} for row in rows]
        c.require(stable(a['rows'])==stable(b['rows']),'resume numerical rows not bit-identical')
        ar,am=c.load_checkpoint(straight/'checkpoint.npz','test-fingerprint',4,.99,10,np.pi/4)
        br,bm=c.load_checkpoint(resumed/'checkpoint.npz','test-fingerprint',4,.99,10,np.pi/4)
        c.require(np.array_equal(ar,br),'resume density not bit-identical')
        # Simulate process death after atomic output creation and before checkpoint unlink.
        c.result_check(b,4,.99,10,'test-fingerprint')
        c.cleanup_completed_checkpoint(resumed,b,'test-fingerprint')
        c.require(not (resumed/'checkpoint.npz').exists(),'stale completed checkpoint survived')
        # Unfinished later-curve checkpoint must not be removed while skipping an older output.
        c.trajectory(resumed,4,.5,10,'test-fingerprint',stop_at=4)
        before=c.digest(resumed/'checkpoint.npz')
        c.cleanup_completed_checkpoint(resumed,b,'test-fingerprint')
        c.require(c.digest(resumed/'checkpoint.npz')==before,'later curve checkpoint removed')
        # Use the complete uninterrupted copy for subsequent corruption checks.
        resumed=straight
        rejected=[]
        for label,params in [('fingerprint',('wrong',4,.99,10,np.pi/4)),('xi',('test-fingerprint',4,.5,10,np.pi/4))]:
            try:c.load_checkpoint(resumed/'checkpoint.npz',*params)
            except RuntimeError:rejected.append(label)
            else:raise RuntimeError('checkpoint mismatch accepted')
        br[0,0]+=1e-6
        with (root/'corrupt.npz').open('wb') as f:np.savez(f,rho=br,metadata=np.array(json.dumps(bm)))
        try:c.load_checkpoint(root/'corrupt.npz','test-fingerprint',4,.99,10,np.pi/4)
        except RuntimeError:rejected.append('density-checksum')
        else:raise RuntimeError('corrupt checkpoint accepted')
        with c.writer_lock(root):
            p=subprocess.run([c.sys.executable,'-c',
                'import sys;sys.path.insert(0,sys.argv[1]);import run;\nwith run.writer_lock(sys.argv[2]): pass',
                str(c.HERE/'scripts'),str(root)],capture_output=True,text=True)
            c.require(p.returncode!=0 and 'Another campaign process' in p.stderr,'duplicate writer accepted')
        immutable=root/'immutable.json';c.atomic_json(immutable,{'value':1},immutable=True)
        try:c.atomic_json(immutable,{'value':2},immutable=True)
        except FileExistsError:rejected.append('output-overwrite')
        else:raise RuntimeError('immutable output overwritten')
        c.require(json.loads(immutable.read_text())=={'value':1},'immutable contents changed')
        return dict(rows_bit_identical=True,density_bit_identical=True,completed_checkpoint_cleanup=True,later_checkpoint_preserved=True,rejected=rejected,duplicate_writer_rejected=True)


def l12_ideal():
    folder=c.HERE/'checks/L12-ideal';folder.mkdir(exist_ok=True)
    baseline=json.loads((c.HERE/'provenance/dynamics_L12_xi1.json').read_text())
    with c.writer_lock(c.HERE/'progress'):
        c.status(folder,stage='setup',L=12,xi=1,t=0)
        phase,mask=c.setup(12,1.);rho=np.ones((4096,4096),complex)/4096
        rows=[];resource_error=negative_error=0.
        for t in range(5):
            c.invariants(rho);row=dict(t=t,**c.extraction(rho,12));base=baseline['rows'][t]
            resource_error=max(resource_error,max(abs(row[k]-base[k]) for k in FIELDS))
            if t in (0,1,4):
                row.update(c.spectra(rho,12,lambda stage:c.status(folder,stage=stage,L=12,xi=1,t=t)))
                negative_error=max(negative_error,abs(row['log_negativity_nats']-base['log_negativity_nats']))
            rows.append(row)
            if t<4:
                c.status(folder,stage='step',L=12,xi=1,t=t+1);rho=c.step(rho,12,phase,mask)
        c.require(max(resource_error,negative_error)<1e-9,'full-space L12 ideal regression failed')
        result=dict(rows=rows,resource_max_error=resource_error,negativity_max_error=negative_error,peak_rss_bytes=c.peak())
        c.atomic_json(c.HERE/'checks/L12-ideal.json',result)
        print(json.dumps(result,indent=2),flush=True)



def kernel_identity():
    old=old_module();d=np.diag([1,1j]);h=np.array([[1,1],[1,-1]])/np.sqrt(2)
    x=np.array([[0,1],[1,0]])
    error=float(np.max(abs(d@h@d-expm(1j*np.pi/4*x))))
    c.require(error<1e-10,'single-site DHD identity failed')
    rng=np.random.default_rng(13631);errors={}
    for n in (4,6):
        a=rng.normal(size=(1<<n,1<<n))+1j*rng.normal(size=(1<<n,1<<n))
        initial=a@a.conj().T;initial/=np.trace(initial)
        for xi in (-1/(n-1),0,.99,1.):
            phase,mask=c.setup(n,xi);rho=initial.copy();ref=initial.copy();worst=0.
            for t in range(8):
                rho=c.step(rho,n,phase,mask);ref=old.step(ref,n,phase,mask)
                worst=max(worst,float(np.max(abs(rho-ref))))
            c.require(worst<1e-10,'repeated generic mixed-state kernel mismatch')
            errors[f'L{n}_xi{xi}']=worst
    return dict(single_site_error=error,repeated_generic_state_errors=errors)


def manifest_guards():
    original=c.HERE
    with tempfile.TemporaryDirectory(dir=original/'checks') as tmp:
        c.HERE=Path(tmp)
        try:
            code=c.HERE/'kernel.py';code.write_text('original source')
            obj=dict(config=c.CONFIG,source_sha256={'kernel.py':c.digest(code)},
                     environment=dict(executable=c.sys.executable,python=c.sys.version,
                                      numpy=np.__version__,scipy=c.scipy.__version__))
            c.atomic_json(c.HERE/'manifest.json',obj)
            c.validate_manifest()
            code.write_text('modified source')
            try:c.validate_manifest()
            except RuntimeError:pass
            else:raise RuntimeError('changed code accepted')
            code.write_text('original source');obj['config']=dict(c.CONFIG,horizon=399)
            c.atomic_json(c.HERE/'manifest.json',obj)
            try:c.validate_manifest()
            except RuntimeError:pass
            else:raise RuntimeError('changed config accepted')
        finally:c.HERE=original
    return dict(changed_source_rejected=True,changed_config_rejected=True)


def output_integrity_guards():
    with tempfile.TemporaryDirectory(dir=c.HERE/'checks') as tmp:
        folder=Path(tmp)
        base=c.trajectory(folder,4,.99,10,'validation-test')
        c.result_check(base,4,.99,10,'validation-test')
        rejected=[]
        def reject(label, obj):
            try:c.result_check(obj,4,.99,10,'validation-test')
            except (RuntimeError,KeyError,TypeError,ValueError):rejected.append(label)
            else:raise RuntimeError('invalid saved result accepted: '+label)
        for t in (0,6):
            for field in base['rows'][t]:
                obj=copy.deepcopy(base);del obj['rows'][t][field];reject(f'missing-{t}-{field}',obj)
        for field in base['rows'][0]:
            obj=copy.deepcopy(base);obj['rows'][0][field]=float('nan');reject('nonfinite-'+field,obj)
        for field in ('max_trace_error','max_hermiticity_error','seconds','peak_rss_bytes'):
            obj=copy.deepcopy(base);obj[field]=float('nan');reject('nonfinite-summary-'+field,obj)
            obj=copy.deepcopy(base);obj[field]=-1.;reject('negative-summary-'+field,obj)
        for field,value in [('teleportation_fidelity',1.),('weighted_advantage',.1),('fallback_fidelity',1.),
                            ('min_density_eigenvalue',-.01),('min_density_eigenvalue',.5),
                            ('min_pt_eigenvalue',.5),('log_negativity_nats',10.),
                            ('density_spectral_trace_error',-1e-12),('density_spectrum_seconds',-1.),('t',False)]:
            obj=copy.deepcopy(base);obj['rows'][0][field]=value;reject(f'inconsistent-{field}-{value}',obj)
        obj=copy.deepcopy(base);obj['rows'][0]['probability']=.3;reject('wrong-initial-probability',obj)
        obj=copy.deepcopy(base)
        for row in obj['rows']:row.pop('min_density_eigenvalue',None)
        reject('reviewer-all-density-minima-missing',obj)
        obj=copy.deepcopy(base)
        for row in obj['rows']:
            del row['weighted_advantage'];del row['fallback_fidelity']
        reject('reviewer-all-derived-resources-missing',obj)
        # Ensure identical requirements govern resumed metadata, not only final JSON.
        rho,meta=c.load_checkpoint(folder/'checkpoint.npz','validation-test',4,.99,10,np.pi/4)
        for label in ('missing-resource','missing-spectral','nan-summary','bad-formula'):
            bad=copy.deepcopy(meta)
            if label=='missing-resource':del bad['rows'][0]['fallback_fidelity']
            elif label=='missing-spectral':del bad['rows'][0]['min_density_eigenvalue']
            elif label=='nan-summary':bad['max_hermiticity_error']=float('nan')
            else:bad['rows'][0]['teleportation_fidelity']=1.
            with (folder/'bad.npz').open('wb') as stream:np.savez(stream,rho=rho,metadata=np.array(json.dumps(bad)))
            try:c.load_checkpoint(folder/'bad.npz','validation-test',4,.99,10,np.pi/4)
            except (RuntimeError,KeyError,TypeError,ValueError):rejected.append('checkpoint-'+label)
            else:raise RuntimeError('bad checkpoint history accepted: '+label)
        return dict(valid_output_accepted=True,rejected_count=len(rejected),rejected_cases=rejected)

def main():
    mode=c.sys.argv[1]
    if mode=='small':
        with c.writer_lock(c.HERE/'progress'):
            result=dict(output_integrity_guards=output_integrity_guards(),kernel_identity=kernel_identity(),manifest_guards=manifest_guards(),dense_reference=dense_reference(),invalid_inputs_rejected=boundary_checks(),
                        known_states=known_states(),J0_controls=controls(),resume=resume_checks())
        c.atomic_json(c.HERE/'checks/author-small.json',result);print(json.dumps(result,indent=2),flush=True)
    elif mode=='l10':
        with c.writer_lock(c.HERE/'progress'):result=l10_regression()
        c.atomic_json(c.HERE/'checks/L10-regression.json',result);print(json.dumps(result,indent=2),flush=True)
    elif mode=='l12':l12_ideal()
    else:raise ValueError('unknown checks mode')


if __name__=='__main__':main()
