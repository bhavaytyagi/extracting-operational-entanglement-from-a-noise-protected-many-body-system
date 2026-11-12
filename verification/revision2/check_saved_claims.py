"""Predeclared bounded saved-record checks, no numerical evolution.

Require exact hashes against the supplied completion marker, twenty curves,
401 integer resource times, thirteen stated spectral times, and exact stated
useful-time integer sets for xi=.99/.999 at F>2/3+1e-10. Require manuscript
rounded .995 terminal values to their displayed rounding tolerances. Ideal
terminal p/F agree with analytic anchors to absolute 1e-12. These checks
validate saved-record consistency, not the simulation that produced it.
"""
from pathlib import Path
import hashlib
import json

p = Path(__file__).resolve().parents[2]/'data/xi_sweep'
marker = json.loads((p/'progress/complete.json').read_text())
assert hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest() == marker['manifest_sha256']
assert len(marker['output_sha256']) == 20
spectral = [0,1,2,3,4,5,10,20,40,80,150,250,400]
data = {}
for name, digest in marker['output_sha256'].items():
    file = p/name
    assert hashlib.sha256(file.read_bytes()).hexdigest() == digest, name
    item = json.loads(file.read_text())
    assert item['L'] == 12 and item['gamma'] == .1 and item['h'] == 1
    assert item['negativity_samples'] == spectral
    assert [r['t'] for r in item['rows']] == list(range(401))
    assert [r['t'] for r in item['rows'] if 'log_negativity_nats' in r] == spectral
    for r in item['rows']:
        assert abs(r['teleportation_fidelity']-(2*r['bell_overlap']+1)/3) < 1e-12
    data[item['xi']] = item['rows']
for xi, stop in ((.99,178),(.999,400)):
    useful = [r['t'] for r in data[xi] if r['teleportation_fidelity'] > 2/3+1e-10]
    assert useful == list(range(2,stop+1)), (xi,useful)
    print('Useful saved integer times:',xi,useful[0],useful[-1])
r = data[.995][-1]
assert abs(r['log_negativity_nats']-.00989) < .000005
assert abs(r['teleportation_fidelity']-.6426) < .00005
assert abs(r['probability']-.00148) < .000005
print('xi=.995 t400:',{k:r[k] for k in ('log_negativity_nats','teleportation_fidelity','probability')})
assert abs(data[1.][-1]['probability']-1/192) < 1e-12
assert abs(data[1.][-1]['teleportation_fidelity']-19/21) < 1e-12
print('PASS: manifest digest,20 output digests,8020 resource rows,260 spectral records, stated useful sets/rounded example/ideal scalar anchors')
