"""Read-only, exact-sample Figure 2 preview; no numerical evolution."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/joe-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/private/tmp/joe-cache')
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.ticker import FixedLocator, FixedFormatter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_DATA = ROOT / 'data/xi_sweep/data'
DETAIL_XI = (.95, .99, .995, .999, 1.)


def load_records(data, size):
    paths = sorted(data.glob(f'L{size}_xi*.json'))
    records = [(path, json.loads(path.read_text())) for path in paths]
    records.sort(key=lambda item: item[1]['xi'])
    assert len(records) >= 20, f'Need at least 20 saved correlations; got {len(records)}'
    xis = [r['xi'] for _, r in records]
    assert len(xis) == len(set(xis)), 'Duplicate correlations'
    assert abs(xis[0] + 1 / (size - 1)) < 1e-9 and xis[-1] == 1., 'Incomplete physical range'
    reference = records[0][1]
    for path, rec in records:
        assert rec['L'] == size and rec['horizon'] == reference['horizon'], path
        for key in ('J', 'b', 'h', 'gamma', 'negativity_samples'):
            assert rec[key] == reference[key], (path, key)
        rows = [r for r in rec['rows'] if 'log_negativity_nats' in r]
        assert [r['t'] for r in rows] == rec['negativity_samples'], path
        assert np.isfinite([r['log_negativity_nats'] for r in rows]).all(), path
    return records


def draw(data=DEFAULT_DATA, out=HERE, size=10, *, main_ylim=(-.04, 2.5),
         detail_ylim=(-.025, 1.1)):
    records = load_records(data, size)
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size': 8, 'axes.labelsize': 8,
        'axes.titlesize': 8, 'xtick.labelsize': 7, 'ytick.labelsize': 7,
        'legend.fontsize': 7, 'axes.spines.top': False,
        'axes.spines.right': False, 'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig = plt.figure(figsize=(3.4, 4.0))
    grid = fig.add_gridspec(3, 1, height_ratios=(1., .07, 1.02),
        left=.16, right=.975, bottom=.1, top=.875, hspace=.57)
    main = fig.add_subplot(grid[0])
    bar_ax = fig.add_subplot(grid[1])
    detail = fig.add_subplot(grid[2])
    cmap = plt.colormaps['viridis_r']
    norm = Normalize(vmin=-1 / (size - 1), vmax=1.)
    audit = {'status': 'unverified preview; not installed', 'L': size,
        'data_policy': 'Exact calculated samples; connecting segments are visual guides only.',
        'inputs': [], 'artists': [], 'main_color_normalization':
        {'type': 'linear', 'vmin': norm.vmin, 'vmax': norm.vmax},
        'physical_interval': [-1 / (size - 1), 1.]}
    handles = {}

    def trace(ax, panel, rec, rows, color, linewidth, label=None):
        t = [r['t'] for r in rows]
        y = [r['log_negativity_nats'] for r in rows]
        line, = ax.plot(t, y, 'o-', color=color, lw=linewidth,
            ms=2.5 if panel == 'detail' else 2.0, mew=0, label=label,
            zorder=3 if rec['xi'] == 1 else 2)
        audit['artists'].append({'panel': panel, 'kind': 'trajectory',
            'xi': rec['xi'], 't': line.get_xdata().tolist(),
            'log_negativity_nats': line.get_ydata().tolist(),
            'color': matplotlib.colors.to_hex(line.get_color(), keep_alpha=True),
            'linewidth': line.get_linewidth(), 'marker': line.get_marker(),
            'markersize': line.get_markersize(), 'linestyle': line.get_linestyle()})
        return line

    detail_colors = dict(zip(DETAIL_XI, ['#a84d19', '#d4941c', '#309878', '#2074ad', '#482777']))
    for path, rec in records:
        audit['inputs'].append({'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'xi': rec['xi']})
        rows = [r for r in rec['rows'] if 'log_negativity_nats' in r]
        trace(main, 'main', rec, rows, cmap(norm(rec['xi'])), 1.3 if rec['xi'] == 1 else .65)
        if rec['xi'] in DETAIL_XI:
            handles[rec['xi']] = trace(detail, 'detail', rec,
                [r for r in rows if r['t'] >= 20], detail_colors[rec['xi']],
                1.3 if rec['xi'] == 1 else .9, label=fr"$\xi={rec['xi']:g}$")
    assert set(handles) == set(DETAIL_XI), 'Missing near-collective detail correlations'
    bar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=bar_ax,
        orientation='horizontal')
    bar.set_ticks([-1 / (size - 1), 0, .5, 1], labels=[f'$-1/{size-1}$', '0', '0.5', '1'])
    bar.ax.tick_params(labelsize=7, length=2, pad=1)
    bar.set_label(fr'Physical correlation $\xi$ ({len(records)} sampled values)', fontsize=7, labelpad=1)
    main.set_title('(a) Complete physical correlation interval', loc='left', pad=4)
    main.set_xscale('symlog', linthresh=5)
    main.set_xlim(0, 400)
    main.xaxis.set_major_locator(FixedLocator([0, 5, 20, 100, 400]))
    main.xaxis.set_major_formatter(FixedFormatter(['0', '5', '20', '100', '400']))
    main.set_ylim(*main_ylim)
    detail.set_title('(b) Late-time persistence near collective noise', loc='left', pad=4)
    detail.set_xscale('log')
    detail.set_xlim(20, 400)
    detail.xaxis.set_major_locator(FixedLocator([20, 40, 80, 150, 250, 400]))
    detail.xaxis.set_major_formatter(FixedFormatter(['20', '40', '80', '150', '250', '400']))
    detail.minorticks_off()
    detail.set_ylim(*detail_ylim)
    detail.legend(loc='upper right',
        frameon=False, ncol=3, handlelength=1.1, handletextpad=.3,
        columnspacing=.7, labelspacing=.15, borderaxespad=.1)
    for ax in (main, detail):
        ax.set_ylabel('Logarithmic negativity (nats)', labelpad=3)
        ax.set_xlabel('Periods', labelpad=2)
        ax.grid(alpha=.14, lw=.45)
        ax.tick_params(pad=2, length=3)
    fig.suptitle(f'{size}-spin preview: saved correlation sweep', x=.16, ha='left', y=.982, fontsize=9)
    fig.text(.16, .935, 'Markers: calculated spectra; lines: visual guides', fontsize=7)
    for ext in ('pdf', 'png'):
        fig.savefig(out / f'xi_negativity_L{size}_preview.{ext}', dpi=240, facecolor='white',
            metadata={'Title': f'L={size} saved-data preview; no interpolation'})
    audit['nominal_font_sizes_pt'] = sorted(set(float(text.get_fontsize()) for text in
        fig.findobj(matplotlib.text.Text) if text.get_text()))
    audit['axis_limits'] = {name: {'x': list(ax.get_xlim()), 'y': list(ax.get_ylim())}
        for name, ax in (('main', main), ('detail', detail))}
    (out / f'xi_negativity_L{size}_artist_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    plt.close(fig)
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--out', type=Path, default=HERE)
    parser.add_argument('--size', type=int, default=10)
    args = parser.parse_args()
    audit = draw(args.data.resolve(), args.out.resolve(), args.size)
    print(f"Wrote L={args.size} preview: {len(audit['inputs'])} correlations, {len(audit['artists'])} trajectories.")
