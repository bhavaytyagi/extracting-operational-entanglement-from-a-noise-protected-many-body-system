"""Complete text-free twelve-spin extraction and teleportation review draft."""
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/joe-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/private/tmp/joe-cache')
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle,Polygon,Arc,PathPatch,FancyArrowPatch
from matplotlib.path import Path as MPath
import pymupdf

HERE=Path(__file__).resolve().parent
INK='#203448';BLUE='#24558b';ORANGE='#b86626';CLASSICAL='#657789'
W,H=650.,385.
fig=plt.figure(figsize=(7.05,7.05*H/W),facecolor='white')
ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,W),ylim=(H,0));ax.axis('off')
inventory={'L':12,'gate_events':[],'quantum_paths':[],'classical_paths':[],
 'selectors':[],'branch_enables':[],'visual_dictionary':{
 'blank_blue_square':'H','circled_plus':'X or CNOT target',
 'diamond_central_dot':'Z','empty_diamond':'classically enabled identity/pass or discard',
 'meter':'computational-Z measurement','pattern_filled_open':'predetermined1/0'}}

def line(points,color=INK,lw=1.,gid=None,dash=False,zorder=1):
    xx,yy=zip(*points)
    obj,=ax.plot(xx,yy,color=color,lw=lw,solid_capstyle='round',zorder=zorder,
                 linestyle=(0,(3,2)) if dash else '-')
    if gid:obj.set_gid(gid)
    return obj

def quantum(name,points,color):
    line(points,color,1.15,gid='quantum-'+name)
    inventory['quantum_paths'].append({'id':name,'points':points,'color':color})

def classical(name,points):
    # White gaps at unrelated vertical quantum crossings make no connection.
    fragments=[]
    for p,q in zip(points[:-1],points[1:]):
        if p[1]==q[1]:
            crosses=[x for x,ymax in ((255,310),(545,350))
                     if min(p[0],q[0])<x<max(p[0],q[0]) and 35<p[1]<ymax]
            direction=1 if q[0]>p[0] else -1
            cursor=p
            for x in sorted(crosses,reverse=direction<0):
                fragments.append([cursor,(x-4*direction,p[1])])
                cursor=(x+4*direction,p[1])
            fragments.append([cursor,q])
        elif name=='reject-zero' and p[0]==q[0] and min(p[1],q[1])<183<max(p[1],q[1]):
            direction=1 if q[1]>p[1] else -1
            fragments.extend([[p,(p[0],183-4*direction)],[(p[0],183+4*direction),q]])
        else:fragments.append([p,q])
    for i,fragment in enumerate(fragments):
        line(fragment,CLASSICAL,.95,gid=f'classical-{name}-{i}',dash=True,zorder=2)
    inventory['classical_paths'].append({'id':name,'points':points,'dash_pattern_pt':[3,2]})

def dot(x,y,r=2.6,color=INK,filled=True):
    ax.add_patch(Circle((x,y),r,fc=color if filled else 'white',ec=color,lw=1,zorder=8))

def plus(x,y,r=5.5,color=INK):
    dot(x,y,r,color,False)
    line([(x-r*.7,y),(x+r*.7,y)],color,1,zorder=9)
    line([(x,y-r*.7),(x,y+r*.7)],color,1,zorder=9)

def cnot(x,control_y,target_y,control,target,party):
    line([(x,control_y),(x,target_y)],INK,.95,zorder=3)
    dot(x,control_y);plus(x,target_y)
    inventory['gate_events'].append({'kind':'CNOT','party':party,'control':control,
        'target':target,'x':x,'control_y':control_y,'target_y':target_y})

def meter(x,y,wire,stage):
    ax.add_patch(Rectangle((x-9,y-7.5),18,15,fc='white',ec=INK,lw=.95,zorder=5))
    ax.add_patch(Arc((x,y+2),11,10,theta1=180,theta2=360,color=INK,lw=.8,zorder=6))
    line([(x,y+3),(x+4,y-3)],INK,.9,zorder=7)
    inventory['gate_events'].append({'kind':'measure-Z','wire':wire,'stage':stage,'x':x,'y':y})

def and_gate(x,y,width,height,name):
    # Cubic midpoint must coincide exactly with declared right-side port.
    right_control=x+width*(1-.25*.35)/.75
    verts=[(x,y-height/2),(x+width*.35,y-height/2),
           (right_control,y-height/2),(right_control,y+height/2),
           (x+width*.35,y+height/2),(x,y+height/2),(x,y-height/2)]
    codes=[MPath.MOVETO,MPath.LINETO,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4,
           MPath.LINETO,MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(verts,codes),fc='#f5f7f9',ec=CLASSICAL,lw=.9,zorder=3))

# Two local decoders acting on an existing joint twelve-spin ring state.
for party,base,color in [('A',20,BLUE),('B',285,ORANGE)]:
    ys=[35+24*j for j in range(6)]
    retained_end=255 if party=='A' else 545
    quantum(f'{party}1-retained',[(base,35),(retained_end,35),
             (retained_end,310 if party=='A' else 350)],color)
    for j in range(1,6):
        quantum(f'{party}{j+1}',[(base,ys[j]),(base+151,ys[j])],color)
        cnot(base+25+24*(j-1),35,ys[j],f'{party}1',f'{party}{j+1}',party)
        meter(base+151,ys[j],f'{party}{j+1}','extraction')
        classical(f'{party}-record-{j+1}',[(base+160,ys[j]),(base+187,ys[j])])
    and_gate(base+187,107,35,116,f'{party}-fixed-record-selector')
    for j,bit in enumerate([1,0,1,0,1],start=1):
        dot(base+197,ys[j],3.0,CLASSICAL,bool(bit))
    inventory['selectors'].append({'party':party,'record_order':[f'{party}{j}' for j in range(2,7)],
        'expected_bits':[1,0,1,0,1],'symbol_x':base+197,'symbol_ys':ys[1:]})

# Two local success flags are ANDed. No solid cross-half quantum connection.
classical('A-success',[(242,107),(247,107),(247,203),(267,203)])
classical('B-success',[(507,107),(522,107),(522,183),(237,183),(237,217),(267,217)])
and_gate(267,210,30,30,'joint-success')
classical('joint-success-output',[(297,210),(315,210),(365,210),(365,230)])
dot(338,210,3.2,CLASSICAL,True)
classical('reject-zero',[(315,210),(315,172)])
dot(315,191,3.2,CLASSICAL,False)
line([(309,171),(321,171)],INK,1.7,zorder=9)
line([(310,166),(320,176)],INK,1.2,zorder=9)
line([(310,176),(320,166)],INK,1.2,zorder=9)
classical('accept-herald-bus',[(240,230),(535,230)])
dot(365,230,2.1,CLASSICAL)
for party,x,color in [('A',255,BLUE),('B',545,ORANGE)]:
    feed=x-15
    classical(f'herald-enable-{party}',[(feed,230),(feed,245),(x-8,245)])
    ax.add_patch(Polygon([(x,236),(x+8,245),(x,254),(x-8,245)],closed=True,
        fc='white',ec=color,lw=1.1,zorder=7))
    inventory['branch_enables'].append({'party':party,'wire':party+'1','x':x,'y':245,
        'control':'g=AND(A-record==10101,B-record==10101)','g1':'identity/continue','g0':'discard'})

# Unknown input exists only in the post-herald stage, not during extraction.
quantum('Q',[(310,275),(430,275)],INK)
ax.add_patch(FancyArrowPatch((300,275),(316,275),arrowstyle='-|>',
    mutation_scale=8,lw=1.1,color=INK,zorder=4))
quantum('A1-accepted-to-Bell',[(255,310),(430,310)],BLUE)
cnot(370,275,310,'Q','A1','teleportation')
ax.add_patch(Rectangle((390,266),18,18,fc='#dce7f0',ec=INK,lw=1.1,zorder=6))
inventory['gate_events'].append({'kind':'H','wire':'Q','x':399,'y':275,'symbol':'blank-square'})
meter(430,275,'Q','teleportation');meter(430,310,'A1','teleportation')
classical('Bell-A-to-X',[(439,310),(575,310),(575,343)])
classical('Bell-Q-to-Z',[(439,275),(605,275),(605,342)])
quantum('B1-accepted-corrections-output',[(545,350),(633,350)],ORANGE)
plus(575,350,7)
inventory['gate_events'].append({'kind':'X','wire':'B1','control_bit':'measure-A1','x':575,'y':350,'order':1})
ax.add_patch(Polygon([(605,342),(613,350),(605,358),(597,350)],closed=True,
    fc='white',ec=INK,lw=1.1,zorder=7));dot(605,350,2.6)
inventory['gate_events'].append({'kind':'Z','wire':'B1','control_bit':'measure-Q','x':605,'y':350,'order':2})
ax.add_patch(FancyArrowPatch((625,350),(640,350),arrowstyle='-|>',
    mutation_scale=9,lw=1.2,color=ORANGE,zorder=4))

assert not [t for t in fig.findobj(matplotlib.text.Text) if t.get_text()]
classical_artists=[l for l in ax.lines if (l.get_gid() or '').startswith('classical-')]
assert classical_artists and all(l.is_dashed() for l in classical_artists)
inventory['checks']={'nonempty_text_objects':0,'all_classical_lines_dashed':True,
    'classical_line_fragment_count':len(classical_artists),'unknown_input_starts_postherald':True,
    'native_dimensions_pt':[7.05*72,7.05*72*H/W]}
for ext in ['pdf','svg','png']:
    fig.savefig(HERE/f'full_protocol_draft.{ext}',facecolor='white',dpi=450,
        metadata={'Title':''})
plt.close(fig)
svg=ET.parse(HERE/'full_protocol_draft.svg')
assert not svg.findall('.//{http://www.w3.org/2000/svg}text')
doc=pymupdf.open(HERE/'full_protocol_draft.pdf');page=doc[0]
assert not page.get_text().strip() and not page.get_fonts() and not page.get_images()
page.get_pixmap(matrix=pymupdf.Matrix(3,3)).save(HERE/'full_protocol_pdf_render.png')
# Honest one-column fit, without changing topology or trimming any circuit part.
preview=pymupdf.open();pp=preview.new_page(width=3.4*72,height=3.4*72*H/W)
pp.show_pdf_page(pp.rect,doc,0)
preview.save(HERE/'full_protocol_3p4in_preview.pdf',garbage=4,deflate=True)
pp.get_pixmap(matrix=pymupdf.Matrix(4,4)).save(HERE/'full_protocol_3p4in_preview.png')
inventory['output_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
    for p in [HERE/f'full_protocol_draft.{ext}' for ext in ['pdf','svg','png']]}
(HERE/'circuit_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
print(json.dumps({'status':'rendered draft; Luke topology review pending',
    'no_text':True,'classical_lines_dashed':True,'native_pdf':True,
    'full_width_pt':page.rect.width,'preview_width_pt':pp.rect.width},indent=2))
