"""Review the saved KiCad bias with OP, 1 Hz AC, and nearby DC points.

Derived results are separate from the original KiCad baseline evidence.
The source schematic and its stored component parameters are never edited.
"""
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta

from run_cascode_kicad import Ngspice, ROOT, LAB, PROJECT, sha, close


def gain(op, rl, re):
    m1, m2 = op['devices']['M1'], op['devices']['M2']
    k1 = m1['gm'] + m1['gmbs'] + m1['gds']
    k2 = m2['gm'] + m2['gmbs'] + m2['gds']
    a = m1['gm'] / (1 + k1 * re)
    b = m1['gds'] / (1 + k1 * re)
    return -rl * a * k2 / (k2 + b * (1 + m2['gds'] * rl))


def main():
    kicad = Path(os.environ['LOCALAPPDATA']) / 'Programs/KiCad/10.0/bin'
    schematic = PROJECT / 'cascode-dc.kicad_sch'
    original_hash = sha(schematic)
    output = LAB / 'saved-bias-review'
    output.mkdir(exist_ok=True)
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix='cascode-bias-review-') as temporary:
        temporary = Path(temporary)
        exported = temporary / 'export.cir'
        subprocess.run([str(kicad/'kicad-cli.exe'), 'sch', 'export', 'netlist',
                        '--format', 'spice', '-o', str(exported), str(schematic)],
                       check=True, capture_output=True, text=True,
                       creationflags=subprocess.CREATE_NO_WINDOW, timeout=60)
        text = exported.read_text(encoding='utf-8')
        cards = {line.split()[0].upper(): line.split() for line in text.splitlines()
                 if line and line[0].upper() in 'MRVC' and not line.startswith('*')}
        expected = {'M1':['/X','/VIN','/E','/VSS'], 'M2':['/OUT','/VB','/X','/VSS'],
                    'R1':['/VDD','/OUT'], 'R2':['/E','/VSS'], 'C1':['/OUT','0'],
                    'V1':['/VDD','0'], 'V2':['/VIN','0'], 'V3':['/VB','0'], 'V4':['/VSS','0']}
        if set(cards) != set(expected):
            raise RuntimeError('Review topology before evaluating a different circuit')
        for name, pins in expected.items():
            if cards[name][1:1+len(pins)] != pins:
                raise RuntimeError(f'Terminal mismatch: {name}')
        vin, vb = float(cards['V2'][4]), float(cards['V3'][4])
        rl, re_value = float(cards['R1'][3]), float(cards['R2'][3])
        # AC=1 measures the derivative at the stored DC bias.
        text = re.sub(r'(?m)^(V2\s+[^\n]*?)\s*$', r'\1 AC 1', text)
        saved_deck = text.replace((LAB/'models.lib').as_posix(), '../models.lib')
        simulator = Ngspice(kicad/'ngspice.dll')
        simulator.command('version')
        try:
            os.chdir(temporary)
            simulator.circuit(text)
            snapshot = lambda: simulator.snapshot({'OUT':'/OUT','E':'/E','X':'/X'}, 'V1', 'M1', 'M2')
            nominal = snapshot()
            simulator.command('ac lin 1 1 1')
            simulator.command('let review_real = real(v(/OUT))')
            simulator.command('let review_imag = imag(v(/OUT))')
            av = simulator.vector('review_real')[0]
            imag = simulator.vector('review_imag')[0]
            predicted = gain(nominal, rl, re_value)
            close(av, predicted, 'AC vs independent small-signal closed form', rtol=2e-5)
            delta = 1e-5
            simulator.command(f'alter V2 {vin-delta:.12g}')
            lower = snapshot()['OUT_V']
            simulator.command(f'alter V2 {vin+delta:.12g}')
            upper = snapshot()['OUT_V']
            slope = (upper-lower)/(2*delta)
            close(slope, av, 'DC derivative vs AC', rtol=2e-5)
            simulator.command(f'alter V2 {vin:.12g}')
            points = []
            for offset in (-0.05, -0.02, -0.01, 0, 0.01, 0.02, 0.05):
                value = vin + offset
                simulator.command(f'alter V2 {value:.12g}')
                op = snapshot()
                points.append({'VIN_V':value, 'op':op, 'local_gain_V_V':gain(op, rl, re_value)})
            simulator.command(f'alter V2 {vin:.12g}')
            bias_points = []
            for offset in (-0.05, 0, 0.05, 0.1, 0.15):
                value = vb + offset
                simulator.command(f'alter V3 {value:.12g}')
                op = snapshot()
                bias_points.append({'VB_V':value, 'op':op, 'local_gain_V_V':gain(op, rl, re_value)})
            simulator.command(f'alter V3 {vb:.12g}')
            # Check nearby input points after redistributing cascode headroom.
            trial_vb = vb + 0.15
            simulator.command(f'alter V3 {trial_vb:.12g}')
            trial_input_points = []
            for offset in (-0.02, 0, 0.02):
                value = vin + offset
                simulator.command(f'alter V2 {value:.12g}')
                op = snapshot()
                trial_input_points.append({'VIN_V':value, 'VB_V':trial_vb,
                                           'op':op, 'local_gain_V_V':gain(op, rl, re_value)})
            simulator.command(f'alter V2 {vin:.12g}')
            trial_op = snapshot()
            simulator.command('ac lin 1 1 1')
            simulator.command('let trial_real = real(v(/OUT))')
            trial_ac = simulator.vector('trial_real')[0]
            close(trial_ac, gain(trial_op, rl, re_value), 'Trial bias AC vs closed form', rtol=2e-5)
            simulator.command(f'alter V3 {vb:.12g}')
            log = '\n'.join(simulator.log) + '\n'
            if re.search(r'(?im)\b(error|fatal)\b|no such vector|simulation\(s\) aborted|Controlled exit', log):
                raise RuntimeError(log)
        finally:
            os.chdir(previous)
    if sha(schematic) != original_hash:
        raise RuntimeError('Schematic changed during review; rerun for a consistent snapshot')
    report = {'run_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
              'schematic_sha256':original_hash, 'models_sha256':sha(LAB/'models.lib'),
              'script_sha256':sha(Path(__file__)), 'ngspice_dll_sha256':sha(kicad/'ngspice.dll'),
              'kicad_version':subprocess.check_output([str(kicad/'kicad-cli.exe'),'version'],text=True).strip(),
              'exported_cards':cards, 'nominal_op':nominal,
              'AC_1Hz':{'real_V_V':av,'imag_V_V':imag,'magnitude_dB':20*math.log10(math.hypot(av,imag))},
              'independent_gain_V_V':predicted, 'central_DC_slope_V_V':slope,
              'VIN_nearby_points':points, 'VB_nearby_points':bias_points,
              'trial_VB_input_points':trial_input_points,
              'trial_VB_AC_1Hz':{'VB_V':trial_vb, 'real_V_V':trial_ac},
              'checks':['Unchanged saved schematic hash', 'Original terminal connectivity',
                        'AC agrees with independent closed form populated by simulated OP parameters',
                        'Central DC derivative agrees with AC',
                        'Trial bias AC agrees with independent closed form'], 'all_checks_passed':True}
    (output/'evaluated.cir').write_text(saved_deck,encoding='utf-8')
    (output/'ngspice.log').write_text(log,encoding='utf-8')
    (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
