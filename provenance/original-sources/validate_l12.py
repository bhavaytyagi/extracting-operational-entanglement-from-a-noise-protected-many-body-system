"""Fail-closed plotting adapter for completed, actual L12 campaign data only."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
CAMPAIGN = ROOT / 'numerical_campaigns/xi-sweep-L12-2026-11-03'
RENDERER = ROOT / 'notebook/projects/correlated-noise/physics-results-2026-11-03/joe/draw_xi_negativity.py'
GRID = [-1/11, -.05, 0., .1, .2, .3, .4, .5, .6, .7, .8, .85, .9, .95,
        .97, .98, .99, .995, .999, 1.]
SAMPLES = [0, 1, 2, 3, 4, 5, 10, 20, 40, 80, 150, 250, 400]
DETAIL = [.95, .99, .995, .999, 1.]
PARAMETERS = {'J': math.pi/4, 'b': -math.pi/4, 'h': 1., 'gamma': .1}
TOLERANCE = 1e-14
COMPLETE_STATUS = 'production-complete-pending-independent-final-review'
EXPECTED_OUTPUT_PATHS = {f'data/L12_xi{xi:.9f}.json' for xi in GRID}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_completion_metadata(marker, manifest_sha256, actual_outputs):
    """Validate integrity metadata only; inputs here contain no scientific rows."""
    for key, expected in {'status': COMPLETE_STATUS, 'curves': 20,
                          'resource_rows': 8020, 'spectral_rows': 260}.items():
        require(marker.get(key) == expected, f'Completion marker has wrong {key}')
    require(isinstance(marker.get('completed_utc'), str) and marker['completed_utc'].strip(),
            'Completion marker lacks completion timestamp')
    require(marker.get('manifest_sha256') == manifest_sha256,
            'Completion marker refers to a different or tampered manifest')
    declared = marker.get('output_sha256')
    require(isinstance(declared, dict), 'Completion marker lacks output hash mapping')
    require(set(declared) == EXPECTED_OUTPUT_PATHS,
            'Completion marker has missing, extra or unexpected record paths')
    require(set(actual_outputs) == EXPECTED_OUTPUT_PATHS,
            'Actual outputs have missing, extra or unexpected record paths')
    require(declared == actual_outputs, 'Stale completion marker or tampered data record hash')


def validate_manifest_metadata(manifest):
    config = manifest.get('config', {})
    for key, expected in {'L': 12, 'horizon': 400, 'negativity_samples': SAMPLES,
                          'xi_grid': GRID, 'protocol': 'Ising-kick-accumulated-dephasing',
                          'cut': 'first-six-vs-last-six', 'logarithm': 'natural'}.items():
        require(config.get(key) == expected, f'Manifest has unexpected {key}')
    for key, expected in PARAMETERS.items():
        require(key in config and math.isclose(config[key], expected, rel_tol=0, abs_tol=TOLERANCE),
                f'Manifest has unexpected {key}')


def validate_record(record, expected_xi, label):
    require(record.get('L') == 12, f'{label}: requires L=12; never substitute L10')
    require(record.get('horizon') == 400, f'{label}: incomplete/wrong horizon')
    require(math.isclose(record['xi'], expected_xi, rel_tol=0, abs_tol=TOLERANCE),
            f'{label}: unexpected physical correlation')
    for key, expected in PARAMETERS.items():
        require(math.isclose(record[key], expected, rel_tol=0, abs_tol=TOLERANCE),
                f'{label}: wrong {key}')
    require(record.get('negativity_samples') == SAMPLES, f'{label}: wrong actual spectrum grid')
    rows = record['rows']
    require([row['t'] for row in rows] == list(range(401)), f'{label}: missing/duplicate periods')
    neg = [row for row in rows if 'log_negativity_nats' in row]
    require([row['t'] for row in neg] == SAMPLES, f'{label}: missing/extra actual spectra')
    require(all(math.isfinite(row['log_negativity_nats']) for row in neg),
            f'{label}: non-finite spectrum value')


def validate_campaign(campaign):
    require(campaign.is_dir(), f'L12 campaign not available: {campaign}')
    marker = campaign / 'progress/complete.json'
    manifest = campaign / 'manifest.json'
    for path in (marker, manifest):
        require(path.is_file(), f'Campaign is not complete; required input absent: {path}')
    manifest_object = json.loads(manifest.read_text())
    validate_manifest_metadata(manifest_object)
    paths = sorted((campaign / 'data').glob('L*_xi*.json'))
    actual_outputs = {str(path.relative_to(campaign)): digest(path) for path in paths}
    fingerprint = digest(manifest)
    validate_completion_metadata(json.loads(marker.read_text()), fingerprint, actual_outputs)
    records = [(path, json.loads(path.read_text())) for path in paths]
    records.sort(key=lambda item: item[1]['xi'])
    for (path, record), xi in zip(records, GRID):
        validate_record(record, xi, str(path))
        require(record.get('manifest_sha256') == fingerprint,
                f'{path}: record belongs to a different immutable manifest')
    return records, marker, manifest


def check_artists(audit, records):
    require(audit['L'] == 12, 'Wrong plotted size')
    require(audit['main_color_normalization'] == {'type': 'linear', 'vmin': -1/11, 'vmax': 1.},
            'Wrong physical xi color mapping')
    raw = {rec['xi']: rec for _, rec in records}
    counts = {'main': 0, 'detail': 0}
    samples = {'main': 0, 'detail': 0}
    seen = {'main': set(), 'detail': set()}
    for artist in audit['artists']:
        panel = artist['panel']
        require(panel in counts, 'Unexpected panel')
        xi = artist['xi']
        require(xi not in seen[panel], 'Duplicate trajectory')
        seen[panel].add(xi)
        require(artist['kind'] == 'trajectory' and artist['marker'] == 'o', 'Wrong data artist')
        rows = [row for row in raw[xi]['rows'] if 'log_negativity_nats' in row]
        if panel == 'detail':
            require(xi in DETAIL, 'Unexpected detail curve')
            rows = [row for row in rows if row['t'] >= 20]
        require(artist['t'] == [row['t'] for row in rows], 'Altered or interpolated times')
        require(artist['log_negativity_nats'] == [row['log_negativity_nats'] for row in rows],
                'Artist differs from actual saved spectra')
        bounds = audit['axis_limits'][panel]
        require(all(bounds['x'][0] <= t <= bounds['x'][1] for t in artist['t']),
                'Clipped measured time')
        require(all(bounds['y'][0] < y < bounds['y'][1] for y in artist['log_negativity_nats']),
                'Clipped measured negativity')
        counts[panel] += 1
        samples[panel] += len(rows)
    require(counts == {'main': 20, 'detail': 5}, f'Wrong curve counts: {counts}')
    require(samples == {'main': 260, 'detail': 30}, f'Wrong sample counts: {samples}')
    require(min(audit['nominal_font_sizes_pt']) >= 7, 'Nominal fonts too small')
    for item, (path, record) in zip(audit['inputs'], records):
        require(item['sha256'] == digest(path) and item['xi'] == record['xi'], 'Input identity changed')
    require(len(audit['inputs']) == 20, 'Incomplete input audit')
    return counts, samples


def plot(campaign, out):
    records, marker, manifest = validate_campaign(campaign)
    input_snapshot = {path: digest(path) for path in [marker, manifest, *[p for p, _ in records]]}
    spec = importlib.util.spec_from_file_location('joe_exact_sample_renderer', RENDERER)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    all_values = [row['log_negativity_nats'] for _, rec in records for row in rec['rows']
                  if 'log_negativity_nats' in row]
    late_values = [row['log_negativity_nats'] for _, rec in records if rec['xi'] in DETAIL
                   for row in rec['rows'] if 'log_negativity_nats' in row and row['t'] >= 20]
    main_peak, detail_peak = max(all_values), max(late_values)
    require(main_peak > 0 and detail_peak > 0, 'Nonpositive peaks; plot requires scientific inspection')
    main_ylim = (min(-.04, min(all_values)-.02), main_peak*1.10)
    detail_ylim = (min(-.025, min(late_values)-.015), detail_peak*1.38)
    audit = renderer.draw(campaign / 'data', out, 12,
                          main_ylim=main_ylim, detail_ylim=detail_ylim)
    counts, samples = check_artists(audit, records)
    validate_campaign(campaign)
    require(all(digest(path) == value for path, value in input_snapshot.items()),
            'Campaign inputs changed during plotting; output remains unaccepted')
    receipt = {'status': 'pass: exact data/artist interface only; independent review pending',
        'L': 12, 'horizon': 400, 'grid': GRID, 'actual_samples': SAMPLES,
        'curves': counts, 'measured_markers': samples, 'comparison_tolerance': 0,
        'parameter_grid_tolerance': TOLERANCE, 'interpolated_data_values': 0,
        'axis_limits': audit['axis_limits'], 'input_hashes': audit['inputs'],
        'sources': [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p)}
                    for p in (RENDERER, Path(__file__).resolve(), marker, manifest)],
        'caveats': ['No independent numerical verification by this adapter.',
                    'Final visual inspection and fresh plot review required.',
                    'Finite imperfect-xi survival is not an asymptotic plateau.']}
    (out / 'l12-plot-checks.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, default=CAMPAIGN)
    parser.add_argument('--out', type=Path, default=HERE / 'output')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if args.check_only:
        records, _, _ = validate_campaign(args.campaign.resolve())
        print(f'Validated complete interface: {len(records)} actual L12 curves; no plot written.')
    else:
        receipt = plot(args.campaign.resolve(), args.out.resolve())
        print(json.dumps({'status': receipt['status'], 'curves': receipt['curves'],
                          'measured_markers': receipt['measured_markers']}, indent=2))
