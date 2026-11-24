"""Replot selected trajectories from the frozen twelve-spin sweep."""

import argparse
import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from validate_l12 import SAMPLES, validate_campaign

PROJECT = Path(__file__).resolve().parents[2]
CAMPAIGN = PROJECT / "data" / "xi_sweep"
DEFAULT_OUTPUT = PROJECT / "build" / "figures" / "fig2"

TRAJECTORIES = {
    0.0: ("o", "#222222"),
    0.2: ("s", "#9e3d07"),
    0.4: ("v", "#64762d"),
    0.6: ("D", "#ba5377"),
    0.8: ("^", "#007a75"),
    0.9: ("P", "#975e14"),
    0.95: ("X", "#6950a1"),
    0.99: (">", "#366798"),
    0.999: ("h", "#1a85ac"),
    1.0: ("*", "#152d58"),
}


def hashes(paths):
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def draw(campaign, output):
    records, marker, manifest = validate_campaign(campaign)
    inputs = [marker, manifest, *(path for path, _ in records)]
    before = hashes(inputs)
    by_xi = {record["xi"]: record["rows"] for _, record in records}

    plt.rcParams.update({
        "font.size": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
    })
    fig = plt.figure(figsize=(3.4, 2.55))
    ax = fig.add_axes([0.15, 0.18, 0.82, 0.77])
    inset = ax.inset_axes([0.59, 0.51, 0.38, 0.49])
    main_times = [t for t in SAMPLES if t >= 5]
    early_times = [t for t in SAMPLES if t <= 5]
    for xi, (symbol, color) in TRAJECTORIES.items():
        for panel, times in ((ax, main_times), (inset, early_times)):
            values = [by_xi[xi][t]["log_negativity_nats"] for t in times]
            panel.plot(
                times, values, color=color, lw=1 if xi == 1 else 0.65,
                marker=symbol, ms=(5 if xi == 1 else 3.7) if panel is ax else 2.5,
                mfc="white", mew=0.85 if panel is ax else 0.65, label=f"{xi:g}",
            )

    ax.set_xscale("log")
    ax.set_xlim(4.6, 465)
    ax.set_ylim(-0.095, 2.85)
    ax.set_yticks([0, 0.5, 1, 1.5, 2])
    ticks = [5, 10, 20, 50, 100, 400]
    ax.set_xticks(ticks, labels=[str(t) for t in ticks])
    ax.minorticks_off()
    ax.set_xlabel("Floquet periods", labelpad=2)
    ax.set_ylabel(r"$E_{\mathcal{N}}(t)$", labelpad=2)
    ax.tick_params(pad=2, length=3)
    ax.grid(alpha=0.18, lw=0.45)

    inset.set_xlim(-0.27, 5.27)
    inset.set_ylim(-0.14, 2.88)
    inset.set_xticks(early_times)
    inset.set_yticks([0, 1, 2])
    inset.tick_params(labelsize=7, pad=1.5, length=2)
    inset.grid(alpha=0.18, lw=0.38)
    for spine in inset.spines.values():
        spine.set_visible(True)
        spine.set_color("#777777")
        spine.set_linewidth(0.5)

    legend = ax.legend(
        title=r"Noise correlation $\xi$", title_fontsize=8,
        loc="upper left", bbox_to_anchor=(0.07, 1.035),
        ncols=2, alignment="left", fontsize=8,
        frameon=True, fancybox=False, framealpha=1, facecolor="white",
        edgecolor="#c4c8ce", handlelength=0.8, handletextpad=0.45,
        columnspacing=1.05, labelspacing=0.24, borderaxespad=0.65,
        borderpad=0.55,
    )
    legend.get_frame().set_linewidth(0.55)
    for handle in legend.get_lines():
        handle.set_linestyle("None")
    fig.canvas.draw()

    assert ax.get_xscale() == "log" and inset.get_xscale() == "linear"
    assert set(main_times) | set(early_times) == set(SAMPLES)
    assert set(main_times) & set(early_times) == {5}
    assert [item.get_text() for item in legend.texts] == [f"{xi:g}" for xi in TRAJECTORIES]
    for panel, times in ((ax, main_times), (inset, early_times)):
        assert [line.get_marker() for line in panel.lines] == [v[0] for v in TRAJECTORIES.values()]
        for line, xi in zip(panel.lines, TRAJECTORIES):
            assert line.get_xdata().tolist() == times
            assert line.get_ydata().tolist() == [by_xi[xi][t]["log_negativity_nats"] for t in times]
    assert all(abs(line.get_ydata()[0]) <= 1e-10 for line in inset.lines)
    renderer = fig.canvas.get_renderer()
    legend_bounds = legend.get_window_extent(renderer)
    inset_bounds = inset.get_tightbbox(renderer)
    assert not legend_bounds.overlaps(inset_bounds), (legend_bounds, inset_bounds)
    for line in ax.lines:
        path = ax.transData.transform_path(line.get_path())
        assert not path.intersects_bbox(legend_bounds, filled=False), "Legend obscures data"
        assert not path.intersects_bbox(inset_bounds, filled=False), "Inset obscures data"
    assert hashes(inputs) == before, "Frozen campaign changed during plotting"

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        output, metadata={"Title": "Logarithmic negativity of the twelve-spin ring", "CreationDate": None}
    )
    print(f"Verified {len(ax.lines)} trajectories, {len(ax.lines) * len(SAMPLES)} exact sample coordinates, and {len(before)} input hashes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=CAMPAIGN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    draw(args.campaign.resolve(), args.out.resolve() / "negativity_L12_correlations.pdf")
