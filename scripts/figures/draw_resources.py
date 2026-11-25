"""Draw the coauthor resource heatmaps from the frozen twelve-spin sweep."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as effects
import matplotlib.pyplot as plt
import numpy as np
import pymupdf
from matplotlib.collections import LineCollection
from matplotlib.colors import LogNorm, Normalize

from validate_l12 import validate_campaign
from typography_checks import check_ink

PROJECT = Path(__file__).resolve().parents[2]
CAMPAIGN = PROJECT / "data" / "xi_sweep"
DEFAULT_OUTPUT = PROJECT / "build" / "figures" / "fig3"

BENCHMARK = 2 / 3
BENCHMARK_TOLERANCE = 1e-10
COLOR_LAYER_DPI = 1200


def hashes(paths):
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def true_runs(mask):
    transitions = np.flatnonzero(np.diff(mask.astype(int), prepend=0, append=0))
    return transitions.reshape(-1, 2)


def threshold_segments(mask, xedges, yedges):
    """Merge adjoining internal edges along each stripe of the cell grid."""
    segments = []
    for col, different in enumerate((mask[:, :-1] != mask[:, 1:]).T, start=1):
        x = xedges[col]
        segments.extend(((x, yedges[lo]), (x, yedges[hi]))
                        for lo, hi in true_runs(different))
    for row, different in enumerate(mask[:-1] != mask[1:], start=1):
        y = yedges[row]
        segments.extend(((xedges[lo], y), (xedges[hi], y))
                        for lo, hi in true_runs(different))
    return segments


def verify_boundary(segments, mask, xedges, yedges):
    """Compare the artist's edges to the four neighbors of every above cell."""
    nrows, ncols = mask.shape
    expected = set()
    for row, col in np.argwhere(mask):
        if col and not mask[row, col - 1]:
            expected.add(("vertical", col, row))
        if col + 1 < ncols and not mask[row, col + 1]:
            expected.add(("vertical", col + 1, row))
        if row and not mask[row - 1, col]:
            expected.add(("horizontal", row, col))
        if row + 1 < nrows and not mask[row + 1, col]:
            expected.add(("horizontal", row + 1, col))

    xindex = {value: i for i, value in enumerate(xedges)}
    yindex = {value: i for i, value in enumerate(yedges)}
    actual = []
    for (x0, y0), (x1, y1) in segments:
        if x0 == x1:
            actual.extend(("vertical", xindex[x0], row)
                          for row in range(yindex[y0], yindex[y1]))
        else:
            assert y0 == y1, "A benchmark segment is not a cell edge"
            actual.extend(("horizontal", yindex[y0], col)
                          for col in range(xindex[x0], xindex[x1]))
    assert len(actual) == len(expected) and set(actual) == expected, \
        "Benchmark stroke does not match the discrete cell boundary"
    return len(actual)


def draw_cells(ax, values, xedges, yedges, cmap, norm, *, benchmark):
    mesh = ax.pcolormesh(
        xedges, yedges, values, shading="flat", cmap=cmap, norm=norm,
        linewidth=0, antialiased=False, rasterized=True, snap=True,
    )
    assert mesh.norm is norm and mesh.cmap is cmap, "Heatmap colors were renormalized"
    assert np.array_equal(np.asarray(mesh.get_array()), values), "Altered saved cells"
    xy = mesh.get_coordinates()
    assert np.array_equal(xy[0, :, 0], xedges), "Altered time edges"
    assert np.array_equal(xy[:, 0, 1], yedges), "Altered correlation edges"

    receipt = {"saved_cells": int(values.size), "benchmark_edges": 0}
    if benchmark:
        mask = values > BENCHMARK + BENCHMARK_TOLERANCE
        segments = threshold_segments(mask, xedges, yedges)
        receipt["above_benchmark_cells"] = int(mask.sum())
        stroke = LineCollection(
            segments, colors="#151515", linewidths=0.8, linestyles=(0, (3, 2)),
            zorder=3, path_effects=[effects.Stroke(linewidth=1.5, foreground="white"),
                                    effects.Normal()],
        )
        ax.add_collection(stroke)
        receipt["benchmark_edges"] = verify_boundary(
            stroke.get_segments(), mask, xedges, yedges,
        )
    return receipt


def draw(output, evidence):
    records, marker, manifest = validate_campaign(CAMPAIGN)
    before = hashes([marker, manifest, *(path for path, _ in records)])
    records = [record for _, record in records if record["xi"] >= 0]
    xi = np.array([record["xi"] for record in records])
    assert len(xi) == 18 and xi[0] == 0 and xi[-1] == 1
    source = {
        key: np.array([[row[key] for row in record["rows"]] for record in records])
        for key in ("teleportation_fidelity", "probability")
    }
    assert all(values.shape == (18, 401) for values in source.values())
    fidelity = source["teleportation_fidelity"]
    assert np.all(fidelity[:, 0] == BENCHMARK)
    assert np.array_equal(fidelity > BENCHMARK, fidelity > BENCHMARK + BENCHMARK_TOLERANCE)
    assert np.all(fidelity[-2:, 5:] > BENCHMARK + BENCHMARK_TOLERANCE)

    centers = -np.log10(1 - xi[:-1])
    yedges = np.r_[
        centers[0] - (centers[1] - centers[0]) / 2,
        (centers[1:] + centers[:-1]) / 2,
        centers[-1] + (centers[-1] - centers[-2]) / 2,
    ]
    endpoint = np.array([yedges[-1] + 0.12, yedges[-1] + 0.36])
    ycenters = dict(zip(xi, np.r_[centers, endpoint.mean()]))
    tick_xi = [0, .4, .7, .85, .9, .95, .98, .99, .995, .999, 1]

    plt.rcParams.update({
        "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 9,
        "xtick.labelsize": 9, "ytick.labelsize": 9,
        "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42,
    })
    fig = plt.figure(figsize=(7.05, 3.5))
    cmap = plt.colormaps["YlOrRd"]
    plot_bottom, plot_height = .15, .70
    norm_types = [Normalize, LogNorm]
    titles = ["(a) Teleportation fidelity", "(b) Heralding probability"]
    bar_names = ["$F$", "$p$"]
    bar_ticks = [[.5, BENCHMARK, .8, .95], [.0005, .001, .002, .005]]
    bar_labels = [["0.5", "2/3", "0.8", "0.95"], ["0.0005", "0.001", "0.002", "0.005"]]
    sections = [
        ("early", 0, 6, "linear", "Linear time", [0, 1, 2, 3, 4, 5], 0, .106),
        ("main", 5, 401, "log", "Log time", [5, 20, 100, 400], .125, .211),
    ]
    audit = {
        "xi": xi.tolist(),
        "finite_xi_centers": centers.tolist(),
        "finite_xi_edges": yedges.tolist(),
        "xi_eq_one_edges": endpoint.tolist(),
        "benchmark": BENCHMARK,
        "benchmark_tolerance": BENCHMARK_TOLERANCE,
        "panels": {},
    }
    for panel, ((key, values), xleft, norm_type) in enumerate(zip(
        source.items(), [.105, .555], norm_types,
    )):
        norm = norm_type(vmin=float(values.min()), vmax=float(values.max()))
        fig.text(xleft, .956, titles[panel], fontsize=10, ha="left", va="top")
        fig.text(xleft + .168, .056, "Floquet periods", ha="center", va="bottom")
        panel_audit = {
            "palette": cmap.name, "norm": type(norm).__name__,
            "limits": [norm.vmin, norm.vmax], "sections": {},
        }
        audit["panels"][key] = panel_audit
        for name, start, stop, scale, label, ticks, offset, width in sections:
            ax = fig.add_axes([xleft + offset, plot_bottom, width, plot_height])
            ax.set_xscale(scale)
            xedges = np.arange(start, stop + 1) - 0.5
            ax.set_xlim(xedges[0], xedges[-1])
            ax.set_ylim(yedges[0], endpoint[-1])
            regular = draw_cells(ax, values[:-1, start:stop], xedges, yedges, cmap, norm,
                                 benchmark=panel == 0)
            collective = draw_cells(ax, values[-1:, start:stop], xedges, endpoint, cmap, norm,
                                    benchmark=panel == 0)
            panel_audit["sections"][name] = {
                "time_scale": ax.get_xscale(), "periods": [start, stop - 1],
                "finite_xi": regular, "xi_eq_one": collective,
            }
            ax.set_title(label, pad=4)
            ax.set_xticks(ticks, labels=[str(tick) for tick in ticks])
            ax.minorticks_off()
            if panel == 0 and name == "early":
                ax.set_yticks([ycenters[tick] for tick in tick_xi],
                              labels=[f"{tick:g}" for tick in tick_xi])
                ax.set_ylabel(r"Noise correlation $\xi$", labelpad=5)
            else:
                ax.set_yticks([])
            ax.tick_params(pad=2, length=2.5)

        cax = fig.add_axes([xleft + .350, plot_bottom, .015, plot_height])
        colorbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
        cax.set_title(bar_names[panel], pad=4)
        colorbar.set_ticks(bar_ticks[panel], labels=bar_labels[panel])
        cax.minorticks_off()
        cax.tick_params(length=2, pad=2)
        cax.set_ylim(norm.vmin, norm.vmax)
        colorbar.solids.set_rasterized(True)
        assert np.array_equal(cax.get_ylim(), [norm.vmin, norm.vmax])

    assert len(fig.axes) == 6, "Each observable requires an early axis, a main axis, and a bar"
    assert sum(a["saved_cells"] for panel in audit["panels"].values()
               for group in panel["sections"].values()
               for a in (group["finite_xi"], group["xi_eq_one"])) == 2 * 18 * 402
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for artist in fig.findobj(matplotlib.text.Text):
        if artist.get_visible() and artist.get_text():
            assert fig.bbox.contains(*artist.get_window_extent(renderer).min), artist.get_text()
            assert fig.bbox.contains(*artist.get_window_extent(renderer).max), artist.get_text()
    output.parent.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)
    ink = check_ink(fig, evidence / "figure3-ink.json")
    audit["minimum_plain_capital_numeral_height_mm"] = ink["minimum_plain_capital_numeral_height_mm"]
    fig.savefig(output, dpi=COLOR_LAYER_DPI,
                metadata={"Title": "Twelve-spin teleportation resources", "CreationDate": None})
    plt.close(fig)

    with pymupdf.open(output) as pdf:
        assert len(pdf) == 1
        page = pdf[0]
        assert np.allclose([page.rect.width, page.rect.height], [507.6, 252], atol=1e-4, rtol=0)
        images = page.get_image_info()
        assert images and all(
            min(image["width"] * 72 / pymupdf.Rect(image["bbox"]).width,
                image["height"] * 72 / pymupdf.Rect(image["bbox"]).height)
            >= COLOR_LAYER_DPI - 1 for image in images
        ), "Heatmap layer has insufficient resolution"
        assert page.get_drawings(), "Axes and benchmark strokes must remain vector"
        spans = [span for block in page.get_text("dict")["blocks"] if "lines" in block
                 for line in block["lines"] for span in line["spans"]]
        assert min(span["size"] for span in spans) >= 8.999
        page.get_pixmap(matrix=pymupdf.Matrix(2, 2)).save(output.with_suffix(".png"))
        audit["pdf_dimensions_pt"] = [page.rect.width, page.rect.height]
        audit["minimum_font_pt"] = min(span["size"] for span in spans)
        audit["color_layer_dpi"] = COLOR_LAYER_DPI
    assert hashes(before) == before, "Frozen campaign changed during plotting"
    audit["input_sha256"] = {str(path.relative_to(PROJECT)): digest for path, digest in before.items()}
    audit["output_sha256"] = hashes([output])[output]
    (evidence / output.with_suffix(".json").name).write_text(json.dumps(audit, indent=2) + "\n")
    print("Verified 18 correlations, 401 unique periods per observable, the discrete benchmark edges, and 22 input hashes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    draw(output / "xi_resource_L12_all20.pdf", (args.evidence or output).resolve())
