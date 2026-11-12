"""Native Figure1(b) replacement; preserve Figure1(a) and old panel labels."""
from pathlib import Path
import hashlib,json,re
import numpy as np
import pymupdf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FIG=ROOT/'Figures'
SOURCE=ROOT/'provenance/fig1/full_protocol_labeled.pdf'
BASELINE=ROOT/'provenance/fig1/combined-before.pdf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)=='421cbdcf8b8881479ecd337dc3cf33f6b87a88ef3b415b4f8124b17748b19aa7'
before=pymupdf.open(BASELINE)
clean=pymupdf.open(BASELINE)
forms=clean[0].get_xobjects()
overlay=[x for x,name,invoker,box in forms if name=='fullpage'
    and np.allclose(box,[0,0,245,308],rtol=0,atol=1e-6)]
assert len(overlay)==1,overlay
stream=clean.xref_stream(overlay[0])
labels=[]
for coordinate in [b'294.515625',b'120.515625']:
    pattern=rb'q\n1 0 -0 1 7 '+re.escape(coordinate)+rb' cm\nBT\n.*?\nET\nQ'
    matches=re.findall(pattern,stream,re.S)
    assert len(matches)==1,(coordinate,len(matches))
    labels.append(matches[0])
divider=re.findall(rb'q 0 0 245 308 re W n 2 J 1 j 0\.6 w[^q]*?7 134 m\n238 134 l\n\nS\nQ',stream,re.S)
assert len(divider)==1,len(divider)
# Minimal unchanged primitives. Original source artwork remains in its own Form.
replacement=(b'/DeviceRGB CS\n/DeviceRGB cs\n1 j\n'+divider[0]+
    b'\n0.1254901961 0.2039215686 0.2823529412 rg\n'+b'\n'.join(labels)+b'\n')
clean.update_stream(overlay[0],replacement)
assert clean[0].get_text().count('(a)')==clean[0].get_text().count('(b)')==1
for old in ['Product','Entangled','Extracted','Teleportation']:
    assert old not in clean[0].get_text(),old
circuit=pymupdf.open(SOURCE)
W,H=245.,345.
scale=.447
width=circuit[0].rect.width*scale
target=pymupdf.Rect((W-width)/2,187,(W+width)/2,187+circuit[0].rect.height*scale)
doc=pymupdf.open();page=doc.new_page(width=W,height=H)
page.show_pdf_page(pymupdf.Rect(0,0,245,308),clean,0,keep_proportion=True)
circuit_xref=page.show_pdf_page(target,circuit,0,keep_proportion=True)
assert doc.xref_stream(circuit_xref)==circuit[0].read_contents(),'Circuit source content changed'
text=page.get_text()
for label in ['Entanglement extraction','Teleportation','Alice','Bob','Herald','Accept','Discard','Teleported qubit']:
    assert label in text,label
for old in ['Product','Entangled','Extracted']:
    assert old not in text,old
src_circuit_images=len(circuit[0].get_images())
assert src_circuit_images==0
assert len(page.get_images())==len(before[0].get_images())==1

def pixels(p,clip,zoom=3):
    pix=p.get_pixmap(matrix=pymupdf.Matrix(zoom,zoom),clip=clip,alpha=False)
    return np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,3)

panel_a=pymupdf.Rect(0,0,245,174)
assert np.array_equal(pixels(before[0],panel_a),pixels(page,panel_a)),'Panel(a) pixels changed'
# Reference preserves the complete approved circuit with the exact placement.
ref=pymupdf.open();rp=ref.new_page(width=W,height=H)
rp.show_pdf_page(target,circuit,0)
reference_clip=pymupdf.Rect(np.ceil(target.x0*3)/3,np.ceil(target.y0*3)/3,
    np.floor(target.x1*3)/3,np.floor(target.y1*3)/3)
assert np.array_equal(pixels(page,reference_clip),pixels(rp,reference_clip)),'Circuit placement differs from full-page reference'
matrix_objects=[]
for x,name,invoker,box in page.get_xobjects():
    obj=doc.xref_object(x)
    m=re.search(r'/Matrix\s*\[([^]]+)\]',obj)
    if m:
        values=[float(v) for v in m[1].split()]
        if abs(values[0]-scale)<1e-6:
            assert abs(values[0]-values[3])<1e-12 and values[1:3]==[0,0]
            matrix_objects.append({'xref':x,'matrix':values,'object':obj})
assert len(matrix_objects)==1,matrix_objects
out=FIG/'combined_opening.pdf'
doc.save(out,garbage=4,deflate=True)
page.get_pixmap(matrix=pymupdf.Matrix(3,3)).save(FIG/'combined_opening.png')
page.get_pixmap(matrix=pymupdf.Matrix(3,3)).save(HERE/'combined-preview.png')
receipt={'status':'pass: native composition/source-preservation checks; root build pending',
    'author':'Joe (GPT-6.1 Sol High)','baseline_sha256':sha(BASELINE),'circuit_source_sha256':sha(SOURCE),
    'combined_sha256':sha(out),'page_rect_pt':list(page.rect),
    'panel_a_rect_pt':list(panel_a),'panel_a_pixels_3x_exact':True,
    'panel_a_and_b_label_source_blocks_exact':True,'divider_source_block_exact':True,
    'circuit_source_rect_pt':list(circuit[0].rect),'circuit_destination_rect_pt':list(target),
    'circuit_uniform_scale':scale,'circuit_full_page_content_stream_exact':True,
    'circuit_full_page_reference_pixels_exact':True,'circuit_embedding_form':matrix_objects[0],
    'circuit_reference_pixel_aligned_clip_pt':list(reference_clip),
    'new_rasters':0,'original_rasters_unchanged_count':1,
    'effective_qubit_base_font_pt':14*scale,'effective_phase_font_pt':16*scale,
    'effective_party_font_pt':15*scale,'effective_H_font_pt':10.5*scale}
(HERE/'composition-checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
