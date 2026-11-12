import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent.parent/'input'
a=json.loads((p/'data/xi_sweep/data/L12_xi1.000000000.json').read_text())
b=json.loads((p/'data/xi_sweep/provenance/dynamics_L12_xi1.json').read_text())
assert [r['t'] for r in a['rows']]==[r['t'] for r in b['rows']]
print('IDEAL400 residual',b['rows'][-1]['distance_target_frobenius'])
ks=['probability','bell_overlap','teleportation_fidelity','log_negativity_nats']
errors={k:max(abs(x[k]-y[k]) for x,y in zip(a['rows'],b['rows']) if k in x and k in y) for k in ks}
assert max(errors.values())<1e-9
print('IDEAL_SAVED_AGREEMENT',errors)
for f in (p/'primary-sources').glob('*.crossref.json'):
    obj=json.loads(f.read_text()); obj=obj.get('message',obj)
    print('CROSSREF',f.name,obj.get('DOI'),obj.get('title'))
sup=p/'supplemental-numeric-evidence'
hs=json.loads((sup/'HASHES.json').read_text())
assert all(hashlib.sha256((sup/k).read_bytes()).hexdigest()==h for k,h in hs.items())
print('EXACT SUPPLEMENTAL HASHES',hs)
r=json.loads((sup/'results.json').read_text())['independent_dense_reference']
assert r['max_state_error']<=6.95e-16 and r['max_decoder_error']<=6.95e-16
print('RECORDED DENSE COMPARISON',r,'NOT RERUN HERE')
