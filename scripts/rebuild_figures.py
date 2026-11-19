"""Reproduce the three manuscript figures from the archived inputs."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts' / 'figures'


def run(script, *arguments):
    subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, arguments)],
                   cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure', choices=('all', '1', '2', '3'), default='all')
    args = parser.parse_args()
    output = ROOT / 'build' / 'figures'
    if args.figure in ('all', '1'):
        # The frozen vector circuit is sufficient to reproduce the composition.
        run('compose_candidate.py', '--out', output / 'fig1')
    if args.figure in ('all', '2'):
        # Logarithmic negativity at the saved spectral sample times.
        run('draw_l12_labeled.py', '--out', output / 'fig2')
    if args.figure in ('all', '3'):
        # Conditional teleportation fidelity and heralding probability.
        target = output / 'fig3'
        run('draw_resources.py', '--out', target, '--evidence', target)
    print(f'Figure PDFs and reproduction receipts are in {output}')


if __name__ == '__main__':
    main()
