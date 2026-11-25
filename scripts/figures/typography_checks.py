"""Actual-ink text checks on the same Matplotlib artists and transforms.
Renderer buffers are transparent and contain one visible Text artist at a time.
No data or geometry is altered. DPI300 gives0.0847mm source-pixel pitch.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
from matplotlib.text import Text


def check_ink(fig, output, final_scale=1., require_no_overlaps=True):
    fig.set_dpi(300)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    texts=[t for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
    records=[]
    for artist in texts:
        renderer.clear()
        artist.draw(renderer)
        a=np.asarray(renderer.buffer_rgba())[:,:,3]
        ys,xs=np.where(a>32)
        if not len(xs):
            continue
        box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
        assert box[0]>0 and box[1]>0 and box[2]<a.shape[1] and box[3]<a.shape[0],('Ink at canvas edge',artist.get_text(),box)
        caps=[]
        if '$' not in artist.get_text():
            for char in sorted(set(artist.get_text())):
                if not(char.isupper() or char.isdecimal()):continue
                t=Text(*artist.get_position(),text=char,fontproperties=artist.get_fontproperties(),
                    color=artist.get_color(),transform=artist.get_transform(),
                    horizontalalignment=artist.get_horizontalalignment(),
                    verticalalignment=artist.get_verticalalignment())
                t.set_figure(fig)
                renderer.clear();t.draw(renderer)
                mask=np.asarray(renderer.buffer_rgba())[:,:,3]>32
                yy,xx=np.where(mask)
                assert len(yy),(artist.get_text(),char)
                mm=(yy.max()+1-yy.min())/fig.dpi*25.4*final_scale
                caps.append({'char':char,'height_mm':float(mm)})
        records.append({'text':artist.get_text(),'fontsize_source_pt':artist.get_fontsize(),
            'fontsize_final_pt':artist.get_fontsize()*final_scale,'ink_bbox_px':box,
            'ink_height_final_mm':(box[3]-box[1])/fig.dpi*25.4*final_scale,
            'plain_capital_numeral_measurements':caps})
    overlaps=[]
    for i,a in enumerate(records):
        x0,y0,x1,y1=a['ink_bbox_px']
        for b in records[i+1:]:
            u0,v0,u1,v1=b['ink_bbox_px']
            if x0<u1 and u0<x1 and y0<v1 and v0<y1:
                overlaps.append([a['text'],b['text']])
    result={'renderer':'Matplotlib Agg300dpi, alpha>32','final_scale':final_scale,
        'records':records,'actual_ink_bbox_overlaps':overlaps,
        'minimum_plain_capital_numeral_height_mm':min(
            c['height_mm'] for r in records for c in r['plain_capital_numeral_measurements'])}
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    assert result['minimum_plain_capital_numeral_height_mm']>=2.,('Capital/numeral ink smaller than2mm',result['minimum_plain_capital_numeral_height_mm'])
    assert not require_no_overlaps or not overlaps,('Actual ink bounding boxes overlap',overlaps)
    fig.canvas.draw()
    return result
