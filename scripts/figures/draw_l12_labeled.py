"""Single-panel Figure 2 from immutable, actual twelve-spin spectra."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/joe-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/private/tmp/joe-cache')
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.ticker import FixedLocator, FixedFormatter
import pymupdf as fitz

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAMPAIGN = ROOT / 'data/xi_sweep'
VALIDATOR = HERE / 'validate_l12.py'
spec = importlib.util.spec_from_file_location('immutable_l12_validator', VALIDATOR)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def draw(campaign=CAMPAIGN, out=HERE):
    records, marker, manifest = validator.validate_campaign(campaign)
    snapshot = {path: digest(path) for path in [marker, manifest, *[p for p, _ in records]]}
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 8, 'axes.labelsize': 8,
        'xtick.labelsize': 7, 'ytick.labelsize': 7,
        'axes.spines.top': False, 'axes.spines.right': False,
        'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig = plt.figure(figsize=(3.4, 2.55))
    main = fig.add_axes([.16, .18, .60, .775])
    bar_ax = fig.add_axes([.795, .18, .030, .775])
    cmap = plt.colormaps['viridis_r']
    norm = Normalize(vmin=-1/11, vmax=1.)
    audit = {'status': 'visualization checks only; independent final review pending',
        'L': 12, 'inputs': [], 'artists': [],
        'data_policy': 'Exact calculated samples; connecting segments are visual guides only.',
        'main_color_normalization': {'type': 'linear', 'vmin': norm.vmin, 'vmax': norm.vmax},
        'physical_interval': [-1/11, 1.], 'titles': [], 'trajectory_panels': 1}
    for path, rec in records:
        rows = [r for r in rec['rows'] if 'log_negativity_nats' in r]
        t = [r['t'] for r in rows]
        y = [r['log_negativity_nats'] for r in rows]
        marker_map={.95:'s',.99:'^',.995:'D',.999:'v',1.:'o'}
        line, = main.plot(t, y, marker_map.get(rec['xi'],'o')+'-', color=cmap(norm(rec['xi'])),
            lw=1.15 if rec['xi'] == 1 else .65, ms=2.8 if rec['xi'] in marker_map else 2., mew=0,
            label=fr"$\xi={rec['xi']:g}$" if rec['xi'] in marker_map else '_nolegend_',
            zorder=3 if rec['xi'] == 1 else 2)
        assert line.get_xdata().tolist() == t, 'Altered times'
        assert line.get_ydata().tolist() == y, 'Altered saved spectra'
        assert np.array_equal(matplotlib.colors.to_rgba(line.get_color()), cmap(norm(rec['xi'])))
        audit['inputs'].append({'path': str(path.relative_to(ROOT)),
            'sha256': digest(path), 'xi': rec['xi']})
        audit['artists'].append({'panel': 'main', 'kind': 'trajectory',
            'xi': rec['xi'], 't': line.get_xdata().tolist(),
            'log_negativity_nats': line.get_ydata().tolist(),
            'color_rgba': list(matplotlib.colors.to_rgba(line.get_color())),
            'linewidth': line.get_linewidth(), 'marker': line.get_marker(),
            'markersize': line.get_markersize(), 'linestyle': line.get_linestyle()})
    main.legend(loc='upper right',frameon=False,fontsize=7,handlelength=1.4,
                borderaxespad=.2,labelspacing=.25,handletextpad=.35)
    bar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=bar_ax,
        orientation='vertical')
    bar.set_ticks([-1/11, 0, .5, 1], labels=['$-1/11$', '0', '0.5', '1'])
    bar.ax.tick_params(labelsize=7, length=2, pad=2)
    bar.set_label(r'$\xi$', fontsize=8, labelpad=1)
    main.set_xscale('symlog', linthresh=5)
    main.set_xlim(-.6, 470)
    main.xaxis.set_major_locator(FixedLocator([0, 5, 20, 100, 400]))
    main.xaxis.set_major_formatter(FixedFormatter(['0', '5', '20', '100', '400']))
    values = [y for artist in audit['artists'] for y in artist['log_negativity_nats']]
    main.set_ylim(min(-.08, min(values)-.02), max(values)*1.10)
    main.set_ylabel('Logarithmic negativity (nats)', labelpad=3)
    main.set_xlabel('Periods', labelpad=2)
    main.grid(alpha=.14, lw=.45)
    main.tick_params(pad=2, length=3)
    main.minorticks_off()
    fig.canvas.draw()
    assert main.get_title() == '' and not fig.texts, 'Unexpected title/subtitle'
    assert len(fig.axes) == 2 and len(main.lines) == 20, 'Wrong panel or curve count'
    assert sum(len(a['t']) for a in audit['artists']) == 260, 'Wrong actual sample count'
    assert bar.orientation == 'vertical' and bar_ax.get_position().x0 > main.get_position().x1
    audit['figure_inches'] = fig.get_size_inches().tolist()
    audit['axis_limits'] = {'main': {'x': list(main.get_xlim()), 'y': list(main.get_ylim())}}
    audit['time_scale'] = {'type': main.get_xscale(), 'linthresh': main.xaxis.get_transform().linthresh}
    audit['colorbar'] = {'orientation': bar.orientation, 'right_of_main': True,
        'label': bar.ax.get_ylabel()}
    audit['marker_extent_checks'] = []
    bounds = main.get_window_extent()
    for line in main.lines:
        radius = .5 * line.get_markersize() * fig.dpi / 72
        xy = main.transData.transform(np.column_stack((line.get_xdata(), line.get_ydata())))
        clearance = min(float(np.min(xy[:, 0]-bounds.x0)), float(np.min(bounds.x1-xy[:, 0])),
            float(np.min(xy[:, 1]-bounds.y0)), float(np.min(bounds.y1-xy[:, 1])))
        assert clearance-radius >= .5*fig.dpi/72, ('Clipped marker', clearance, radius)
        audit['marker_extent_checks'].append({'minimum_center_to_edge_px': clearance,
            'marker_radius_px': radius, 'extra_clearance_pt': (clearance-radius)*72/fig.dpi})
    texts = [t for t in fig.findobj(matplotlib.text.Text) if t.get_text() and t.get_visible()]
    audit['nominal_font_sizes_pt'] = sorted({float(t.get_fontsize()) for t in texts})
    assert min(audit['nominal_font_sizes_pt']) >= 7
    renderer = fig.canvas.get_renderer()
    audit['text_extent_checks'] = []
    for text in texts:
        box = text.get_window_extent(renderer)
        assert box.x0 >= 0 and box.y0 >= 0 and box.x1 <= fig.bbox.x1 and box.y1 <= fig.bbox.y1, (
            'Text outside figure', text.get_text(), list(box.bounds))
        audit['text_extent_checks'].append({'text': text.get_text(), 'bounds_px': list(box.bounds)})
    for ext in ('pdf', 'png'):
        fig.savefig(out / f'negativity_L12_correlations.{ext}', dpi=300, facecolor='white',
            metadata={'Title': 'Twelve-spin correlation trajectories'})
    plt.close(fig)
    with fitz.open(out / 'negativity_L12_correlations.pdf') as pdf:
        assert len(pdf) == 1
        page = pdf[0]
        assert abs(page.rect.width-3.4*72) < .001 and abs(page.rect.height-2.55*72) < .001
        spans = [s for b in page.get_text('dict')['blocks'] if 'lines' in b
                 for line in b['lines'] for s in line['spans']]
        assert min(s['size'] for s in spans) >= 6.999, 'PDF fonts smaller than 7pt'
        audit['pdf_font_sizes_pt'] = sorted({s['size'] for s in spans})
        audit['pdf_page_points'] = [page.rect.width, page.rect.height]
        audit['pdf_text'] = page.get_text()
        page.get_pixmap(matrix=fitz.Matrix(3, 3)).save(out / 'negativity_L12_correlations_pdf_raster.png')
    validator.validate_campaign(campaign)
    assert all(digest(path) == value for path, value in snapshot.items()), 'Campaign mutated'
    audit['comparison_tolerance'] = 0
    audit['input_hashes_unchanged'] = True
    audit['campaign_metadata'] = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p)} for p in (marker, manifest)]
    audit['sources'] = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p)} for p in (Path(__file__).resolve(), VALIDATOR)]
    audit['output_sha256'] = digest(out / 'negativity_L12_correlations.pdf')
    (out / 'figure_checks.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps({'status': 'pass', 'curves': len(audit['artists']), 'actual_samples': 260,
        'comparison_tolerance': 0, 'dimensions_inches': audit['figure_inches'],
        'minimum_marker_extra_clearance_pt': min(c['extra_clearance_pt'] for c in audit['marker_extent_checks']),
        'pdf_sha256': audit['output_sha256']}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, default=CAMPAIGN)
    parser.add_argument('--out', type=Path, default=HERE)
    args = parser.parse_args()
    draw(args.campaign.resolve(), args.out.resolve())
