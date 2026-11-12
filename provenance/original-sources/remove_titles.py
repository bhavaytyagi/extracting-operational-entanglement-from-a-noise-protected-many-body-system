"""Remove exactly two title suffixes from the preserved native vector PDF.

Run from the project root with noisy_env Python. Baseline remains immutable.
Only the two UTF-16 text operands are shortened; all PDF graphics and text
positions, fonts, source artwork, and other stream bytes remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pymupdf

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'before-figure.pdf'
ROOT = HERE.parents[2]
OUT = ROOT / 'Working_paper/prl-revision-2026-10-30/Figures'
EXPECTED_BASE = '42452c58e5d025fad93ac4f41fa0c2dd47728d4650a0d116633b885aeb9ca392'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def pdf_literal(s):
    data = s.encode('utf-16-be')
    return data.replace(b'\\', b'\\\\').replace(b'(', b'\\(').replace(b')', b'\\)')

assert digest(BASE) == EXPECTED_BASE, 'Baseline changed'
before = pymupdf.open(BASE)
after = pymupdf.open(BASE)
changes = [
    ('(a) Noise channels', '(a)'),
    ('(b) Preparation, protection and use', '(b)'),
]
modified = []
for xref in range(1, after.xref_length()):
    if not after.xref_is_stream(xref):
        continue
    stream = after.xref_stream(xref)
    revised = stream
    for old, new in changes:
        operand = b'(' + pdf_literal(old) + b')'
        if operand in revised:
            assert revised.count(operand) == 1
            revised = revised.replace(operand, b'(' + pdf_literal(new) + b')')
    if revised != stream:
        after.update_stream(xref, revised, compress=True)
        modified.append(xref)
assert len(modified) == 1, modified
candidate = HERE / 'combined_opening.pdf'
after.save(candidate, no_new_id=True)
after.close()
after = pymupdf.open(candidate)
assert len(before) == len(after) == 1
assert before[0].rect == after[0].rect
assert before[0].mediabox == after[0].mediabox
assert before[0].cropbox == after[0].cropbox
assert before.xref_length() == after.xref_length()
for xref in range(1, before.xref_length()):
    if xref in modified:
        expected = before.xref_stream(xref)
        for old, new in changes:
            expected = expected.replace(b'(' + pdf_literal(old) + b')',
                                        b'(' + pdf_literal(new) + b')')
        assert after.xref_stream(xref) == expected
    else:
        assert before.xref_object(xref) == after.xref_object(xref), xref
        if before.xref_is_stream(xref):
            assert before.xref_stream_raw(xref) == after.xref_stream_raw(xref), xref

old_text = before[0].get_text()
expected_text = old_text
for old, new in changes:
    assert expected_text.count(old) == 1
    expected_text = expected_text.replace(old, new)
assert after[0].get_text() == expected_text
old_spans = [s for b in before[0].get_text('dict')['blocks'] if b['type'] == 0
             for line in b['lines'] for s in line['spans']]
new_spans = [s for b in after[0].get_text('dict')['blocks'] if b['type'] == 0
             for line in b['lines'] for s in line['spans']]
assert len(old_spans) == len(new_spans)
for old, new in zip(old_spans, new_spans):
    if old['text'] in dict(changes):
        assert new['text'] == dict(changes)[old['text']]
        for key in ['origin', 'font', 'size', 'flags', 'color', 'alpha']:
            assert old[key] == new[key], key
    else:
        assert old == new

pixel_receipts = []
for scale in [2.5, 6.0]:
    p0 = before[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
    p1 = after[0].get_pixmap(matrix=pymupdf.Matrix(scale, scale))
    a0 = np.frombuffer(p0.samples, dtype=np.uint8).reshape(p0.height, p0.width, p0.n)
    a1 = np.frombuffer(p1.samples, dtype=np.uint8).reshape(p1.height, p1.width, p1.n)
    changed = np.any(a0 != a1, axis=2)
    # Predeclared title-only regions in page points, excluding the retained labels.
    regions = [(24, 4, 102, 17), (24, 178, 189, 191)]
    allowed = np.zeros(changed.shape, dtype=bool)
    for x0, y0, x1, y1 in regions:
        allowed[int(y0*scale):int(np.ceil(y1*scale)),
                int(x0*scale):int(np.ceil(x1*scale))] = True
    assert not np.any(changed & ~allowed), 'Pixels changed outside title suffixes'
    boxes = []
    for y0, y1 in [(0, 30), (170, 200)]:
        ys, xs = np.where(changed & (np.indices(changed.shape)[0] >= y0*scale)
                           & (np.indices(changed.shape)[0] < y1*scale))
        assert len(xs) > 0
        boxes.append([int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1)])
    pixel_receipts.append({'scale': scale, 'dimensions_px': [p0.width, p0.height],
                           'changed_pixels': int(changed.sum()), 'difference_boxes_px': boxes,
                           'outside_title_regions_changed_pixels': 0})
    if scale == 2.5:
        # This exact raster scale was used by the original generator.
        p1.save(HERE / 'combined_opening.png')
        p0.save(HERE / 'baseline-rerender.png')
        baseline_png = pymupdf.Pixmap(HERE.parent / 'before-figure.png')
        assert baseline_png.samples == p0.samples, 'Saved baseline PNG differs from PDF render'
    if scale == 6.0:
        p1.save(HERE / 'inspection-432dpi.png')

receipt = {'baseline_pdf_sha256': digest(BASE), 'output_pdf_sha256': digest(candidate),
           'output_png_sha256': digest(HERE / 'combined_opening.png'),
           'modified_content_stream_xrefs': modified,
           'other_pdf_objects_and_raw_streams': 'bit-exact',
           'text_extraction': 'exact baseline text with only two title suffixes removed',
           'label_fonts_origins_sizes_colors': 'exactly retained',
           'page_dimensions_pt': list(after[0].rect), 'pixels': pixel_receipts,
           'pymupdf_version': pymupdf.VersionBind}
(HERE / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
OUT.joinpath('combined_opening.pdf').write_bytes(candidate.read_bytes())
OUT.joinpath('combined_opening.png').write_bytes((HERE / 'combined_opening.png').read_bytes())
print(json.dumps(receipt, indent=2))
