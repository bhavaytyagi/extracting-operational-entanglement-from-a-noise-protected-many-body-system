"""Native page composition; source artwork is embedded unchanged.

Curves are hand-specified schematic Bezier paths, NOT numerical results.
Run with the project's noisy_env Python. Exact TeX footprint from probe.log.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
import pymupdf

ROOT = Path(__file__).resolve().parent
W_PT, H_PT = 246.0, 158.98184  # TeX points, from live REVTeX probe
W, H = W_PT / 72.27, H_PT / 72.27
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5,
                     'mathtext.fontset': 'dejavusans', 'pdf.fonttype': 42})
fig = plt.figure(figsize=(W, H), facecolor='white')
# Native layout placement; no edits to source image pixels.
art = fig.add_axes([0, .344, 1, .518])
art.imshow(plt.imread(ROOT.parent / 'figure1-option4-refinement-2026-09-26' / 'warm-bath-art.png'), aspect='equal')
art.axis('off')
overlay = fig.add_axes([0, 0, 1, 1], frameon=False)
overlay.set(xlim=(0, 1), ylim=(0, 1)); overlay.axis('off')
colors = ['#545c64', '#aa621f', '#204f86']
for x, title, symbol, color in zip([1/6, .5, 5/6],
    ['Independent', 'Near-collective', 'Collective'],
    [r'$\xi=0$', r'$\xi\rightarrow 1$', r'$\xi=1$'], colors):
    overlay.text(x, .986, title, ha='center', va='top', fontsize=8.5, color=color)
    overlay.text(x, .904, symbol, ha='center', va='top', fontsize=8.5, color=color)
overlay.annotate('', xy=(.94,.364), xytext=(.06,.364),
                 arrowprops={'arrowstyle':'->', 'lw':.7, 'color':'#99422d'})
overlay.text(.5,.382,'Increasing spatial correlation',ha='center',va='bottom',
             fontsize=8.5,color='#733727')
ax = fig.add_axes([.15, .115, .57, .205])
ax.set(xlim=(0,1), ylim=(0,1), xticks=[], yticks=[])
for side in ['right','top']: ax.spines[side].set_visible(False)
for side in ['left','bottom']: ax.spines[side].set_linewidth(.7)
ax.set_xlabel('Time',fontsize=8.5,labelpad=1)
ax.set_ylabel('Negativity',fontsize=8.5,labelpad=2)
curves = [
    ([(0,0),(.05,.90),(.18,.96),(.27,.26),(.32,0),(.40,0),(.48,0),(1,0)],colors[0],(0,(3,2))),
    ([(0,0),(.08,1.0),(.20,.96),(.38,.48),(.67,0),(.78,0),(.88,0),(1,0)],colors[1],(0,(4,2,1,2))),
    ([(0,0),(.10,.98),(.23,.96),(.36,.68),(.52,.46),(.70,.48),(1,.48)],colors[2],'solid'),
]
for vertices,color,style in curves:
    codes=[MPath.MOVETO]+[MPath.CURVE4]*6
    if len(vertices)==8: codes.append(MPath.LINETO)
    path=MPath(vertices,codes)
    ax.add_patch(PathPatch(path,fill=False,color=color,lw=1.0,ls=style,clip_on=False))
for y, text, color, style in zip([.292,.214,.136],
        [r'$\xi=0$',r'$\xi\rightarrow1$',r'$\xi=1$'],colors,
        [(0,(3,2)),(0,(4,2,1,2)),'solid']):
    overlay.plot([.77,.835],[y,y],color=color,lw=1,ls=style)
    overlay.text(.85,y,text,ha='left',va='center',fontsize=8.5,color=color)
fig.savefig(ROOT/'figure1-warm-compact.pdf')
fig.savefig(ROOT/'figure1-warm-compact.png',dpi=450)
plt.close(fig)
doc=pymupdf.open(ROOT/'figure1-warm-compact.pdf')
page=doc[0]
expected=(W*72,H*72)
assert abs(page.rect.width-expected[0])<.01
assert abs(page.rect.height-expected[1])<.01
sizes=[s['size'] for b in page.get_text('dict')['blocks'] if b['type']==0
       for l in b['lines'] for s in l['spans'] if s['text'].strip()]
assert sizes and min(sizes)>=7.99, min(sizes)
report={'width_mm':W*25.4,'height_mm':H*25.4,'min_font_pt':min(sizes),
        'font_sizes':sorted(set(round(s,3) for s in sizes)),
        'curves':'hand-specified schematic paths, no simulated data',
        'artwork':'unchanged PNG embedded; labels and curves are vector'}
(ROOT/'layout-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
