"""Verify the delivered manifest and immutable scientific input closure; remote old_project archive is separate."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def selected(p):
 rel=p.relative_to(root)
 return p.is_file() and not any(x in {'__pycache__','.git','build','old_project'} for x in rel.parts) and p.suffix!='.pyc' and not (len(rel.parts)==1 and (p.name=='MANIFEST.json' or p.name.startswith('letter_prl_revision_2') and p.suffix in {'.aux','.log','.out','.fls','.fdb_latexmk','.bbl','.blg','.gz'} or p.name=='letter_prl_revision_2Notes.bib'))
m=json.loads((root/'MANIFEST.json').read_text())
actual={str(p.relative_to(root)) for p in root.rglob('*') if selected(p)}
assert actual==set(m['files']),{'missing':sorted(set(m['files'])-actual),'unexpected':sorted(actual-set(m['files']))}
for rel,item in m['files'].items():
 p=root/rel;assert sha(p)==item['sha256'],rel;assert p.stat().st_size==item['bytes'],rel
campaign=root/'data/xi_sweep';original=json.loads((campaign/'manifest.json').read_text());done=json.loads((campaign/'progress/complete.json').read_text())
assert sha(campaign/'manifest.json')==done['manifest_sha256']
for rel,h in original['source_sha256'].items():assert sha(campaign/rel)==h,rel
for rel,h in done['output_sha256'].items():assert sha(campaign/rel)==h,rel
print(f"PASS: {len(actual)} package files, {len(original['source_sha256'])} frozen source hashes, {len(done['output_sha256'])} data hashes. No trajectory rerun.")
