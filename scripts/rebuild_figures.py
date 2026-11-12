"""Redraw the final figures from packaged data and editable sources.
Run in a disposable copy for audit: figures and local rendering receipts update.
No physical simulation is performed. Figure1(a)'s archived AI raster is an input.
"""
from pathlib import Path
import subprocess,sys,shutil
root=Path(__file__).resolve().parents[1]
f=root/'scripts/figures';out=root/'build/figures';out.mkdir(parents=True,exist_ok=True)
def run(*args): subprocess.run([sys.executable,*map(str,args)],cwd=root,check=True)
run(f/'draw_labeled_candidate.py')
run(f/'compose_candidate.py')
shutil.copy2(root/'Figures/combined_opening_candidate.pdf',root/'Figures/combined_opening.pdf')
run(f/'draw_l12_labeled.py','--out',out/'fig2')
shutil.copy2(out/'fig2/negativity_L12_correlations.pdf',root/'Figures/negativity_L12_correlations.pdf')
evidence=out/'fig3';evidence.mkdir(exist_ok=True)
run(f/'draw_resources.py','--out',evidence,'--evidence',evidence)
shutil.copy2(evidence/'xi_resource_L12_all20.pdf',root/'Figures/xi_resource_L12_all20.pdf')
print('PASS: all three figures rebuilt; no trajectory generated.')
