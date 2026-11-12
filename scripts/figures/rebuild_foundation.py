"""Compose unchanged warm-bath PDF artwork with a native vector blueprint.

Conceptual illustration only. Original illustrative curves are preserved.
Run with noisy_env Python. Source PDFs remain unchanged.
"""
from pathlib import Path
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT=ROOT/'verification/foundation_regenerated'
OUT.mkdir(parents=True,exist_ok=True)
W, H = 245., 308.
B_SHIFT = 68.
SOURCE_SCALE = .94
INK, GRAY, BLUE, ORANGE = '#203448', '#9ba8b2', '#24558b', '#b86626'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'pdf.fonttype': 42, 'svg.fonttype': 'none'})
fig, ax = plt.subplots(figsize=(W/72, H/72))
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax.set(xlim=(0, W), ylim=(H, 0)); ax.axis('off')

def text(x, y, s, size=8, **kw):
    ax.text(x, y+B_SHIFT, s, ha='center', va='center', color=INK,
            fontsize=size, linespacing=1.18, **kw)

def arrow(a, b):
    a, b = (a[0], a[1]+B_SHIFT), (b[0], b[1]+B_SHIFT)
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>',
        mutation_scale=8, lw=.85, color='#697986'))

def ring(x, y, split=False, radius=19):
    y += B_SHIFT
    theta=np.linspace(0,2*np.pi,8,endpoint=False)+np.pi/8
    xy=np.column_stack((x+radius*np.cos(theta),y+radius*np.sin(theta)))
    for j in range(8):
        ax.plot(xy[[j,(j+1)%8],0],xy[[j,(j+1)%8],1],color=GRAY,lw=.8,zorder=1)
    for j,(xx,yy) in enumerate(xy):
        color=(BLUE if j<4 else ORANGE) if split else '#627d95'
        ax.add_patch(Circle((xx,yy),2.7,fc=color,ec='white',lw=.3,zorder=3))

ax.text(7,11,'(a) Noise channels',va='center',ha='left',fontsize=9,
        fontweight='bold',color=INK)
ax.plot([7,238],[106+B_SHIFT,106+B_SHIFT],color='#d9e0e6',lw=.6)
ax.text(7,117+B_SHIFT,'(b) Preparation, protection and use',va='center',ha='left',
        fontsize=9,fontweight='bold',color=INK)
text(39,140,'Product\nstate')
text(122,140,'Entangled\nsteady state')
text(207,140,'Extracted\npair')
ring(39,172)
ring(122,172,split=True)
arrow((63,172),(96,172))
arrow((148,172),(181,172))
ax.plot([197,217],[172+B_SHIFT,172+B_SHIFT],color=GRAY,lw=1.2)
for x,c in [(197,BLUE),(217,ORANGE)]:
    ax.add_patch(Circle((x,172+B_SHIFT),4.8,fc=c,ec='white',lw=.5))
arrow((207,182),(207,220))
text(207,231,'Teleportation')
fig.savefig(HERE/'vector-overlay.pdf',facecolor='white')
plt.close(fig)

# Embed the entire original page, with one uniform reduction and no crop.
# Original raster assets, vectors, text, and all three regimes remain intact.
art=pymupdf.open(ROOT/'provenance/fig1/fig1_option4_warm.pdf')
original_source = ROOT/'provenance/fig1/fig1_option4_warm.pdf'
assert hashlib.sha256(original_source.read_bytes()).digest() == hashlib.sha256(
    (ROOT/'provenance/fig1/fig1_option4_warm.pdf').read_bytes()).digest(), 'Original/copied artwork differs'
overlay=pymupdf.open(HERE/'vector-overlay.pdf')
doc=pymupdf.open();page=doc.new_page(width=W,height=H)
page.show_pdf_page(page.rect,overlay,0)
source_rect = art[0].rect
destination = pymupdf.Rect(7, 22,
    7+SOURCE_SCALE*source_rect.width, 22+SOURCE_SCALE*source_rect.height)
page.show_pdf_page(destination,art,0,keep_proportion=True)
# Exact bare-label substitution from archived Nov4 remove_titles.py; all other stream bytes untouched.
for xref in range(1,doc.xref_length()):
    if not doc.xref_is_stream(xref):continue
    raw=doc.xref_stream(xref);updated=raw
    for old,new in [('(a) Noise channels','(a)'),('(b) Preparation, protection and use','(b)')]:
        old=b'('+old.encode('utf-16-be')+b')';new=b'('+new.encode('utf-16-be')+b')'
        updated=updated.replace(old,new)
    if updated!=raw:doc.update_stream(xref,updated)
path=OUT/'combined_opening.pdf'
doc.save(path,garbage=4,deflate=True)
page.get_pixmap(matrix=pymupdf.Matrix(2.5,2.5)).save(OUT/'combined_opening.png')
sizes=[s['size'] for b in page.get_text('dict')['blocks'] if b['type']==0
       for l in b['lines'] for s in l['spans'] if s['text'].strip()]
# PDF clipping retains out-of-clip source objects. Inspect visible output,
# rather than treating extraction of invisible source text as visible labels.
(HERE/'dimensions.json').write_text(json.dumps({'width_pt':W,'height_pt':H,
    'new_label_min_font_pt':8.,'source_art':'entire unchanged original PDF page',
    'source_rect_pt':list(source_rect), 'destination_rect_pt':list(destination),
    'source_uniform_scale':SOURCE_SCALE, 'panel_b_translation_pt':[0,B_SHIFT],
    'kind':'conceptual schematic, no numeric data'},indent=2)+'\n')
print(path)
