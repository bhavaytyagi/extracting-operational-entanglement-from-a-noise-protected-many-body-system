"""Figure 3: conditional teleportation fidelity and heralding probability from the saved sweep."""
from pathlib import Path
import argparse,hashlib,importlib.util,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm,TwoSlopeNorm
from matplotlib.ticker import FixedLocator,FixedFormatter
import pymupdf

HERE=Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAMPAIGN=ROOT / 'data/xi_sweep'
FIGURES=ROOT/'Figures'
DEFAULT_OUTPUT=ROOT/'build/figures/fig3'
VALIDATOR=HERE / 'validate_l12.py'
spec=importlib.util.spec_from_file_location('l12_completed_interface',VALIDATOR)
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def draw(out=DEFAULT_OUTPUT,evidence=DEFAULT_OUTPUT):
    evidence.mkdir(parents=True, exist_ok=True)
    records,marker,manifest=validator.validate_campaign(CAMPAIGN)
    sources=[marker,manifest,*[p for p,_ in records]]
    protected=[*sources,*[p for p in FIGURES.iterdir() if p.is_file()
        and p.stem!='xi_resource_L12_all20']]
    before={str(p.relative_to(ROOT)):digest(p) for p in protected}
    frozen=evidence/'preserved-figure-input-hashes.json'
    if frozen.exists():
        prior=json.loads(frozen.read_text())
        assert all(digest(ROOT/p)==sha for p,sha in prior.items()),'Frozen input changed'
    else:
        frozen.write_text(json.dumps(before,indent=2)+'\n')
    xi=np.array([r['xi'] for _,r in records])
    times=np.arange(401)
    f=np.array([[row['teleportation_fidelity'] for row in r['rows']] for _,r in records])
    probability=np.array([[row['probability'] for row in r['rows']] for _,r in records])
    assert f.shape==probability.shape==(20,401)
    assert np.isfinite(f).all() and np.isfinite(probability).all()
    assert f.min()>=1/3-1e-10 and f.max()<=1+1e-10
    assert probability.min()>0 and probability.max()<=1+1e-10
    plt.rcParams.update({'font.size':9,'axes.labelsize':9,'axes.titlesize':9,
        'xtick.labelsize':9,'ytick.labelsize':9,'axes.spines.top':False,
        'axes.spines.right':False,'pdf.fonttype':42,'ps.fonttype':42})
    fig=plt.figure(figsize=(7.05,3.5))
    axs=[fig.add_axes([.105,.24,.385,.66]),fig.add_axes([.585,.24,.385,.66])]
    caxs=[fig.add_axes([.105,.105,.385,.028]),fig.add_axes([.585,.105,.385,.028])]
    xedges=np.arange(402)-.5;yedges=np.arange(21)-.5
    norms=[TwoSlopeNorm(vmin=float(f.min()),vcenter=2/3,vmax=float(f.max())),
           LogNorm(vmin=float(probability.min()),vmax=float(probability.max()))]
    titles=['(a) Teleportation fidelity','(b) Extraction probability']
    labels=['-1/11' if x==-1/11 else f'{x:g}' for x in xi]
    meshes=[]
    text_bounds=[]
    artist_arrays={}
    for ax,cax,values,norm,cmap,title,key in zip(axs,caxs,[f,probability],norms,
            ['RdYlBu_r','viridis'],titles,['teleportation_fidelity','probability']):
        mesh=ax.pcolormesh(xedges,yedges,values,shading='flat',cmap=cmap,norm=norm,
                          rasterized=False,edgecolors='face',linewidth=.1,antialiased=False)
        meshes.append(mesh)
        # Audit the actual Matplotlib collection, not only its source array.
        actual=np.asarray(mesh.get_array())
        assert actual.shape==values.shape and np.array_equal(actual,values),key
        coordinates=mesh.get_coordinates()
        assert np.array_equal(coordinates[0,:,0],xedges)
        assert np.array_equal(coordinates[:,0,1],yedges)
        artist_arrays[key]={'shape':list(actual.shape),'values':actual.tolist(),
            'sha256_float64_C':hashlib.sha256(np.ascontiguousarray(actual).tobytes()).hexdigest(),
            'comparison_tolerance':0,'normalization':{'type':type(norm).__name__,
            'vmin':norm.vmin,'vmax':norm.vmax,
            **({'vcenter':norm.vcenter} if hasattr(norm,'vcenter') else {})}}
        ax.set_xscale('symlog',linthresh=5)
        ax.set_xlim(-.6,400.5);ax.set_ylim(-.5,19.5)
        ax.xaxis.set_major_locator(FixedLocator([0,5,20,100,400]))
        ax.xaxis.set_major_formatter(FixedFormatter(['0','5','20','100','400']))
        ax.set_xlabel('Floquet periods',labelpad=3)
        ax.set_title(title,loc='left',pad=6)
        ax.set_yticks(np.arange(20),labels=labels if ax is axs[0] else ['']*20)
        ax.tick_params(length=3,pad=2)
        ax.minorticks_off()
        bar=fig.colorbar(mesh,cax=cax,orientation='horizontal')
        # Colorbar has an independent auto-rasterization threshold.
        bar.solids.set_rasterized(False)
        bar.solids.set_edgecolor('face');bar.solids.set_linewidth(.1)
        if key=='teleportation_fidelity':
            bar.set_ticks([.5,2/3,.8,.95],labels=['0.5','2/3','0.8','0.95'])
        else:
            bar.set_ticks([.0005,.001,.002,.005],labels=['0.0005','0.001','0.002','0.005'])
        bar.ax.minorticks_off();bar.ax.tick_params(labelsize=9,length=2,pad=2)
        cax.set_xlim(norm.vmin,norm.vmax)
        assert np.array_equal(cax.get_xlim(),(norm.vmin,norm.vmax)),(
            'Colorbar ticks expanded normalization bounds',key,cax.get_xlim())
    axs[0].set_ylabel('Correlation ξ (sampled rows)',labelpad=4)
    fig.canvas.draw()
    texts=[t for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
    assert min(t.get_fontsize() for t in texts)>=7
    renderer=fig.canvas.get_renderer()
    for text in texts:
        box=text.get_window_extent(renderer)
        assert box.x0>=0 and box.y0>=0 and box.x1<=fig.bbox.x1 and box.y1<=fig.bbox.y1,(
            'Clipped text',text.get_text(),list(box.bounds))
        text_bounds.append({'text':text.get_text(),'bounds_px':list(box.bounds)})
    assert len(meshes)==2 and all(len(ax.lines)==0 for ax in axs)
    out.mkdir(parents=True,exist_ok=True)
    from typography_checks import check_ink
    ink=check_ink(fig,evidence/'actual-ink-checks.json')
    for ext in ('pdf','png'):
        fig.savefig(out/f'xi_resource_L12_all20.{ext}',dpi=300,facecolor='white',
                    metadata={'Title':'Twelve-spin correlation dependence of fixed-decoder resources'})
    pdf=pymupdf.open(out/'xi_resource_L12_all20.pdf');page=pdf[0]
    assert abs(page.rect.width-507.6)<1e-3 and abs(page.rect.height-252)<1e-3
    assert not page.get_images(),'Unexpected rasterized heatmap'
    spans=[s for b in page.get_text('dict')['blocks'] if b['type']==0
        for line in b['lines'] for s in line['spans'] if s['text'].strip()]
    assert min(s['size'] for s in spans)>=6.999,'PDF text smaller than 7pt'
    assert 'negativity' not in page.get_text().lower()
    page.get_pixmap(matrix=pymupdf.Matrix(3,3)).save(evidence/'xi_resource_L12_all20_pdf_raster.png')
    arrays={'L':12,'xi':xi.tolist(),'t':times.tolist(),'x_cell_edges':xedges.tolist(),
        'y_cell_edges':yedges.tolist(),'artists':artist_arrays}
    (evidence/'artist-arrays.json').write_text(json.dumps(arrays,indent=2)+'\n')
    validator.validate_campaign(CAMPAIGN)
    assert all(digest(ROOT/p)==sha for p,sha in before.items()),'Protected input or old figure changed'
    receipt={'status':'pass: figure/data checks; fresh independent review pending',
        'author':'Joe (GPT-6.1 Sol High)','L':12,'resource_rows_per_observable':8020,
        'panels':titles,'physical_interval':[-1/11,1.],
        'xscale':'symlog','linthresh':5,'row_spacing':'categorical, equally spaced',
        'comparison_tolerance':0,'native_vector':True,'old_assets_unchanged':True,
        'inputs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in sources],
        'sources':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in [Path(__file__),VALIDATOR]],
        'array_evidence_sha256':digest(evidence/'artist-arrays.json'),
        'text_bounds':text_bounds,'minimum_nominal_font_pt':min(t.get_fontsize() for t in texts),
        'pdf_fonts_pt':sorted(set(s['size'] for s in spans)),'dimensions_pt':list(page.rect),
        'pdf_sha256':digest(out/'xi_resource_L12_all20.pdf')}
    (evidence/'figure-checks.json').write_text(json.dumps(receipt,indent=2)+'\n')
    plt.close(fig)
    print(json.dumps({k:receipt[k] for k in ['status','L','resource_rows_per_observable',
        'native_vector','comparison_tolerance','minimum_nominal_font_pt','pdf_sha256']},indent=2))
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument('--evidence',type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args();draw(args.out.resolve(),args.evidence.resolve())
