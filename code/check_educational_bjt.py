"""Check shared BJT v1 against the frozen differential-pair teaching model.

Runs representative existing decks in temporary directories. This checks model
reuse, not independent device calibration; equation checks remain in the lab.
Requires NumPy; paths resolve from this script, not the current directory.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'simulations/models/edu-bjt-gummel-poon'
LAB = ROOT / 'simulations/bjt-degenerated-differential-pair'
CASES = ('op', 'ac-dm', 'ac-cm', 'noise-white', 'noise-flicker', 'transient')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(executable, directory, name):
    options = {}
    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = 0
        options.update(startupinfo=info, creationflags=subprocess.CREATE_NO_WINDOW)
    result = subprocess.run([str(executable), '-b', '-o', name+'.log', name+'.cir'],
                            cwd=directory, capture_output=True, text=True,
                            timeout=60, **options)
    log_path = directory / (name+'.log')
    log = log_path.read_text(errors='replace') if log_path.exists() else ''
    if result.returncode or not log or re.search(
            r'(?im)^\s*(?:error\b|fatal\b|doAnalyses:)|unknown parameter|no such vector|simulation\(s\) aborted', log):
        raise RuntimeError(f'{name} failed:\n{log}\n{result.stderr}')
    data = np.loadtxt(directory / (name+'.dat'), skiprows=1, ndmin=2)
    if not np.isfinite(data).all() or data.size == 0:
        raise ValueError(f'Nonfinite or empty output: {name}')
    return data, log


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ngspice', default=os.environ.get('NGSPICE_BIN', 'ngspice'))
    args = parser.parse_args()
    executable = Path(shutil.which(args.ngspice) or args.ngspice).resolve()
    if not executable.is_file():
        raise FileNotFoundError(executable)
    inputs = [LIBRARY/'v1.lib', LAB/'models.lib', Path(__file__),
              *(LAB/'testbenches'/(name+'.cir') for name in CASES)]
    comparisons, versions = [], set()
    with tempfile.TemporaryDirectory(prefix='educational-bjt-') as temporary:
        work = Path(temporary)
        for name in CASES:
            original = (LAB/'testbenches'/(name+'.cir')).read_text(encoding='utf-8')
            outputs = {}
            for variant in ('snapshot', 'shared-v1'):
                destination = work/name/variant
                destination.mkdir(parents=True)
                model = LAB/'models.lib' if variant == 'snapshot' else LIBRARY/'v1.lib'
                shutil.copy2(model, destination/'models.lib')
                deck = original
                if variant == 'shared-v1' and name == 'noise-flicker':
                    # Replace the original inline card with shared v1 and a
                    # process-local override, leaving the white baseline frozen.
                    inline = (LAB/'models.lib').read_text(encoding='utf-8').replace('KF=0 ', 'KF=1e-14 ')
                    if inline not in deck:
                        raise ValueError('Frozen flicker card no longer matches; review the extension')
                    deck = deck.replace(inline, '.include models.lib\n', 1)
                    deck = deck.replace('.control\n', '.control\naltermod NPN_EDU KF=1e-14 AF=1\n', 1)
                (destination/(name+'.cir')).write_text(deck, encoding='utf-8')
                outputs[variant], log = run(executable, destination, name)
                versions.update(re.findall(r'ngspice-([^\s]+) done', log))
            baseline, shared = outputs['snapshot'], outputs['shared-v1']
            if baseline.shape != shared.shape or not np.array_equal(baseline[:, 0], shared[:, 0]):
                raise ValueError(f'Acquisition shape or axis mismatch: {name}')
            # Zero absolute tolerance also checks cancelled zeros and tiny noise.
            if not np.allclose(shared, baseline, rtol=1e-8, atol=0):
                raise ValueError(f'Shared model changed {name}')
            nonzero = baseline != 0
            error = float(np.max(np.abs((shared[nonzero]-baseline[nonzero])/baseline[nonzero]))) if nonzero.any() else 0
            comparisons.append({'deck': name, 'shape': list(shared.shape),
                                'max_relative_error': error, 'passed': True})
        report = {
            'executed_UTC': datetime.now(timezone.utc).isoformat(),
            'library_version': '1.0.0', 'model_name': 'NPN_EDU',
            'simulator_detected_version': sorted(versions),
            'simulator_executable_sha256': digest(executable),
            'input_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in inputs},
            'shared_model_matches_snapshot_bytes': (LIBRARY/'v1.lib').read_bytes() == (LAB/'models.lib').read_bytes(),
            'executed_decks': 2*len(CASES), 'comparison_rtol': 1e-8, 'comparison_atol': 0,
            'comparisons': comparisons,
            'scope': 'Snapshot/shared model reuse consistency; not independent equations or PDK performance.'}
        # Publish evidence only after all comparisons pass; retain both staged
        # decks/logs and the shared raw data, without overwriting the source lab.
        results = LIBRARY/'results'
        results.mkdir(parents=True, exist_ok=True)
        for name in CASES:
            for variant in ('snapshot', 'shared-v1'):
                destination = results/name/variant
                destination.mkdir(parents=True, exist_ok=True)
                suffixes = ('.cir', '.log', '.dat') if variant == 'shared-v1' else ('.cir', '.log')
                for suffix in suffixes:
                    shutil.copy2(work/name/variant/(name+suffix), destination/(name+suffix))
                shutil.copy2(work/name/variant/'models.lib', destination/'models.lib')
        (results/'summary.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
