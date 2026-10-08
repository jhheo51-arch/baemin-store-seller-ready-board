"""Execute the saved notebook without modifying it in CI; --write refreshes outputs."""
import argparse
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--write', action='store_true')
args = parser.parse_args()
path = ROOT / 'analysis/seller-onboarding-analysis.ipynb'
notebook = nbformat.read(path, as_version=4)
nbformat.validate(notebook)
NotebookClient(notebook, timeout=120, kernel_name='python3', resources={'metadata': {'path': str(ROOT)}}).execute()
if args.write:
    nbformat.write(notebook, path)
print('PASS: notebook executed from the published CSV inputs, including policy recomputation.')
