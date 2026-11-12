"""Annotate the frozen complete circuit without changing its gate geometry."""
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/joe-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/private/tmp/joe-cache')
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import pymupdf

HERE=Path(__file__).resolve().parent
OUT=HERE/'circuit_candidate'
OUT.mkdir(exist_ok=True)
ROOT=HERE.parents[1]
OLD=HERE/'circuit_original'
SOURCE=OLD/'draw_full_protocol.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(ROOT)):sha(p) for p in OLD.rglob('*') if p.is_file()}
source=SOURCE.read_text()
assert source.count('assert not [t for t in fig.findobj')==1
# Execute only frozen vector construction; never execute old output operations.
namespace={'__file__':str(SOURCE),'__name__':'frozen_vector_construction'}
exec(compile(source.split('assert not [t for t in fig.findobj')[0],str(SOURCE),'exec'),namespace)
fig,ax,inventory=namespace['fig'],namespace['ax'],namespace['inventory']
original=json.loads((OLD/'circuit_inventory.json').read_text())
for key in ['gate_events','quantum_paths','classical_paths','selectors','branch_enables']:
    assert json.loads(json.dumps(inventory[key]))==original[key],key
old_lines=list(ax.lines);old_patches=list(ax.patches)
geometry_lines=[(l.get_xdata().copy(),l.get_ydata().copy(),l.get_linestyle(),l.get_color()) for l in old_lines]
geometry_patches=[({'endpoints':list(p._posA_posB),'mutation_scale':p.get_mutation_scale(),
    'arrowstyle':type(p.get_arrowstyle()).__name__} if isinstance(p,FancyArrowPatch)
    else {'vertices':p.get_path().vertices.copy(),'patch_transform':p.get_patch_transform().get_matrix().copy()})
    for p in old_patches]
plt.rcParams['svg.fonttype']='none'
fig.set_size_inches(7.05,7.05*490/720)
ax.set_xlim(-45,675);ax.set_ylim(430,-60)

def label(x,y,text,size=14,color='#203448',ha='center',weight='normal',role='annotation'):
    artist=ax.text(x,y,text,ha=ha,va='center',fontsize=size,color=color,
                   fontweight=weight,zorder=15)
    artist.set_gid('label-'+str(len(labels)))
    labels.append({'text':text,'x':x,'y':y,'fontsize_native_pt':size,'role':role})
    return artist

labels=[]
for x,y,w,h,title,title_x,title_y in [(-35,-50,700,307,'Entanglement extraction',310,-32),
                                     (-35,260,700,156,'Teleportation',100,285)]:
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size=9',
        fc='none',ec='#b7c3cd',lw=.9,zorder=0))
    label(title_x,title_y,title,16,weight='bold',role='phase')
label(100,5,'Alice',15,color='#24558b',weight='bold',role='party')
label(370,5,'Bob',15,color='#b86626',weight='bold',role='party')
for party,x,color in [('A',14,'#24558b'),('B',283,'#b86626')]:
    for j in range(1,7):
        label(x,35+24*(j-1),rf'${party}_{j}$',14,color,ha='right',role='input-qubit')
label(219,7,'10101',16,role='fixed-record')
label(484,7,'10101',16,role='fixed-record')
label(190,209,'Herald',16,ha='right',role='herald')
label(327,170,'Discard',16,ha='left',role='reject')
label(378,208,'Accept',16,ha='left',role='accept')
label(296,275,r'$|\psi\rangle$',16,ha='right',role='unknown-input')
label(245,310,r'$A$',16,color='#24558b',ha='right',role='retained-A')
label(535,350,r'$B$',16,color='#b86626',ha='right',role='retained-B')
label(399,275,'H',14,role='gate-H')
label(575,372,'X',16,role='gate-X')
label(605,372,'Z',16,role='gate-Z')
label(643,372,r'$\rho_{\rm out}$',16,role='output-state')
label(565,399,'Teleported qubit',16,role='output-caption')

for l,record in zip(old_lines,geometry_lines):
    assert np.array_equal(l.get_xdata(),record[0]) and np.array_equal(l.get_ydata(),record[1])
    assert l.get_linestyle()==record[2] and l.get_color()==record[3]
for patch,vertices in zip(old_patches,geometry_patches):
    if isinstance(patch,FancyArrowPatch):
        assert list(patch._posA_posB)==vertices['endpoints']
        assert patch.get_mutation_scale()==vertices['mutation_scale']
        assert type(patch.get_arrowstyle()).__name__==vertices['arrowstyle']
    else:
        assert np.array_equal(patch.get_path().vertices,vertices['vertices'])
        assert np.array_equal(patch.get_patch_transform().get_matrix(),vertices['patch_transform'])
classical=[l for l in old_lines if (l.get_gid() or '').startswith('classical-')]
assert len(classical)==38 and all(l.is_dashed() for l in classical)
fig.canvas.draw();renderer=fig.canvas.get_renderer()
text_artists=[t for t in fig.findobj(matplotlib.text.Text) if t.get_text()]
boxes=[]
for text in text_artists:
    box=text.get_window_extent(renderer)
    assert box.x0>=0 and box.y0>=0 and box.x1<=fig.bbox.width and box.y1<=fig.bbox.height,('clipped text',text.get_text())
    boxes.append((text.get_text(),box))
overlaps=[]
for i,(name,bbox) in enumerate(boxes):
    for other,ob in boxes[i+1:]:
        if bbox.overlaps(ob):overlaps.append([name,other])
assert not overlaps,('Overlapping labels',overlaps)
for ext in ['pdf','svg','png']:
    fig.savefig(OUT/f'full_protocol_labeled.{ext}',facecolor='white',dpi=450,
        metadata={'Title':'Labeled extraction and teleportation review draft'})
plt.close(fig)
svg=ET.parse(OUT/'full_protocol_labeled.svg')
svgtext=svg.findall('.//{http://www.w3.org/2000/svg}text')
assert svgtext,'SVG labels must stay editable text'
doc=pymupdf.open(OUT/'full_protocol_labeled.pdf');page=doc[0]
assert not page.get_images() and 'Entanglement extraction' in page.get_text()
page.get_pixmap(matrix=pymupdf.Matrix(3,3)).save(OUT/'full_protocol_labeled_pdf_render.png')
preview=pymupdf.open();pp=preview.new_page(width=244.8,height=244.8*490/720)
pp.show_pdf_page(pp.rect,doc,0)
preview.save(OUT/'full_protocol_labeled_3p4in.pdf',garbage=4,deflate=True)
pp.get_pixmap(matrix=pymupdf.Matrix(4,4)).save(OUT/'full_protocol_labeled_3p4in.png')
inventory['labels']=labels
inventory['checks']={'original_gate_and_path_inventory_exact':True,
    'original_data_paths_and_gate_geometry_exact':True,
    'arrow_endpoints_styles_mutation_sizes_exact':True,'classical_dashed_fragments':38,
    'editable_svg_text_nodes':len(svgtext),'text_pair_overlaps':overlaps,
    'native_dimensions_pt':list(page.rect),'preview_dimensions_pt':list(pp.rect),
    'preview_scale_factor':3.4/7.05,
    'phase_party_qubit_preview_font_pt':{'phase':16*3.4/7.05,'party':15*3.4/7.05,'qubit':14*3.4/7.05}}
inventory['source']={'path':str(SOURCE.relative_to(ROOT)),'sha256':sha(SOURCE)}
inventory['output_hashes']={p.name:sha(p) for p in [OUT/f'full_protocol_labeled.{ext}' for ext in ['pdf','svg','png']]}
assert all(sha(ROOT/p)==h for p,h in before.items()),'Old frozen draft changed'
(OUT/'circuit_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
(OUT/'preserved-old-draft-hashes.json').write_text(json.dumps(before,indent=2)+'\n')
print(json.dumps({'status':'labeled render ready for visual/fresh review',**inventory['checks']},indent=2))
