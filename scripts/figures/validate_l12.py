"""Fail-closed plotting adapter for completed, actual L12 campaign data only."""
from pathlib import Path
import argparse
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAMPAIGN = ROOT / 'data/xi_sweep'
GRID = [-1/11, -.05, 0., .1, .2, .3, .4, .5, .6, .7, .8, .85, .9, .95,
        .97, .98, .99, .995, .999, 1.]
SAMPLES = [0, 1, 2, 3, 4, 5, 10, 20, 40, 80, 150, 250, 400]
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, default=CAMPAIGN)
    parser.add_argument('--check-only', action='store_true',
                        help='Retained for compatibility. This command validates saved data.')
    args = parser.parse_args()
    records, _, _ = validate_campaign(args.campaign.resolve())
    print(f'Validated complete interface: {len(records)} actual L12 curves.')
