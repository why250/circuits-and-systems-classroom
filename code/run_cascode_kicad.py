"""Export the saved KiCad schematic and run its DC OP with KiCad's ngspice DLL.

Windows: python code/run_cascode_kicad.py [--check-baseline]
No third-party Python packages or separate ngspice installation are needed.
The GUI and this script both derive the circuit from cascode-dc.kicad_sch.
"""
import argparse
import ctypes as ct
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'simulations/source-degenerated-cascode'
PROJECT = ROOT / 'circuits/source-degenerated-cascode/kicad'


class VectorInfo(ct.Structure):
    _fields_ = [('name', ct.c_char_p), ('type', ct.c_int), ('flags', ct.c_short),
                ('real', ct.POINTER(ct.c_double)), ('complex', ct.c_void_p),
                ('length', ct.c_int)]


class Ngspice:
    """Synchronous calls through the documented sharedspice.h C API."""
    def __init__(self, dll):
        self.directory = os.add_dll_directory(str(dll.parent))
        self.dll = ct.CDLL(str(dll))
        self.log = []
        send = ct.CFUNCTYPE(ct.c_int, ct.c_char_p, ct.c_int, ct.c_void_p)
        leave = ct.CFUNCTYPE(ct.c_int, ct.c_int, ct.c_bool, ct.c_bool, ct.c_int, ct.c_void_p)
        self.send = send(self._message)
        self.status = send(lambda *args: 0)
        self.leave = leave(self._leave)
        self.dll.ngSpice_Init.argtypes = [send, send, leave, ct.c_void_p, ct.c_void_p, ct.c_void_p, ct.c_void_p]
        self.dll.ngSpice_Init.restype = ct.c_int
        if self.dll.ngSpice_Init(self.send, self.status, self.leave, None, None, None, None):
            raise RuntimeError('ngspice initialization failed')
        self.dll.ngSpice_Command.argtypes = [ct.c_char_p]
        self.dll.ngSpice_Command.restype = ct.c_int
        self.dll.ngSpice_Circ.argtypes = [ct.POINTER(ct.c_char_p)]
        self.dll.ngSpice_Circ.restype = ct.c_int
        self.dll.ngGet_Vec_Info.argtypes = [ct.c_char_p]
        self.dll.ngGet_Vec_Info.restype = ct.POINTER(VectorInfo)

    def _message(self, value, *args):
        self.log.append(value.decode('utf-8', errors='replace'))
        return 0

    def _leave(self, status, immediate, quit_requested, *args):
        self.log.append(f'Controlled exit: {status}; quit={quit_requested}')
        return 0

    def command(self, command):
        if self.dll.ngSpice_Command(command.encode()):
            raise RuntimeError(f'ngspice rejected {command}:\n' + '\n'.join(self.log[-15:]))

    def circuit(self, text):
        lines = [line.encode() for line in text.splitlines()]
        array = (ct.c_char_p * (len(lines) + 1))(*lines, None)
        if self.dll.ngSpice_Circ(array):
            raise RuntimeError('Circuit load failed:\n' + '\n'.join(self.log[-15:]))

    def vector(self, name):
        ptr = self.dll.ngGet_Vec_Info(name.encode())
        if not ptr or not ptr.contents.real or ptr.contents.length < 1:
            raise RuntimeError(f'Missing real vector {name}:\n' + '\n'.join(self.log[-15:]))
        result = [ptr.contents.real[i] for i in range(ptr.contents.length)]
        if not all(math.isfinite(v) for v in result):
            raise RuntimeError(f'Nonfinite vector {name}')
        return result

    def snapshot(self, nodes, supply, m1, m2):
        self.command('op')
        result = {f'{name}_V': self.vector(f'v({node})')[0] for name, node in nodes.items()}
        result['supply_current_A'] = -self.vector(f'i({supply})')[0]
        result['devices'] = {}
        for label, device in [('M1',m1), ('M2',m2)]:
            values = {p:self.vector(f'@{device.lower()}[{p}]')[0] for p in ('id','vgs','von','vds','vdsat','gm','gds','gmbs')}
            values['saturation_margin_V'] = values['vds'] - values['vdsat']
            result['devices'][label] = values
        return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def close(a,b,label,rtol=2e-5,atol=1e-10):
    if not math.isclose(a,b,rel_tol=rtol,abs_tol=atol):
        raise RuntimeError(f'{label}: {a} != {b}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kicad-dir',type=Path,default=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/KiCad/10.0')
    parser.add_argument('--check-baseline',action='store_true',help='Require original nominal settings and compare both 50-ohm and 10-kohm OPs with the original decks')
    args=parser.parse_args()
    cli=args.kicad_dir/'bin/kicad-cli.exe'
    dll=args.kicad_dir/'bin/ngspice.dll'
    if not cli.is_file() or not dll.is_file():
        raise FileNotFoundError(f'Use --kicad-dir to select an installation containing bin/kicad-cli.exe and bin/ngspice.dll: {args.kicad_dir}')
    output=LAB/'kicad-results'
    output.mkdir(exist_ok=True)
    netlist=output/'cascode-export.cir'
    result=subprocess.run([str(cli),'sch','export','netlist','--format','spice','-o',str(netlist),str(PROJECT/'cascode-dc.kicad_sch')],capture_output=True,text=True,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW,timeout=60)
    if result.returncode or 'warning' in result.stderr.lower() or 'error' in result.stderr.lower():
        raise RuntimeError(result.stdout+result.stderr)
    text=netlist.read_text(encoding='utf-8')
    # Keep the exported deck relocatable; all model parameters remain in the shared library.
    model_path=(LAB/'models.lib').as_posix()
    if f'.include "{model_path}"' not in text:
        raise RuntimeError('Schematic must bind to the shared educational models.lib')
    text=text.replace(f'.include "{model_path}"','.include "../models.lib"')
    netlist.write_text(text,encoding='utf-8')
    cards={line.split()[0].upper():line.split() for line in text.splitlines() if line and line[0].upper() in 'MRVC' and not line.startswith('*')}
    expected={'M1':['/X','/VIN','/E','/VSS'],'M2':['/OUT','/VB','/X','/VSS'],'R1':['/VDD','/OUT'],'R2':['/E','/VSS'],'C1':['/OUT','0'],'V1':['/VDD','0'],'V2':['/VIN','0'],'V3':['/VB','0'],'V4':['/VSS','0']}
    if set(cards)!=set(expected):
        raise RuntimeError('Unexpected device set; review this topology-specific bridge after structural edits')
    for device,pins in expected.items():
        if cards[device][1:1+len(pins)]!=pins:
            raise RuntimeError(f'{device}: terminal mismatch {cards[device]}')
    previous=Path.cwd()
    try:
        os.chdir(output)
        simulator=Ngspice(dll.resolve())
        simulator.command('version')
        simulator.circuit(text)
        current=simulator.snapshot({'OUT':'/OUT','E':'/E','X':'/X'},'V1','M1','M2')
        simulator.command('show m1 m2')
        checks=['Exact D/G/S/B and passive/source connectivity against the original topology']
        comparisons={}
        if args.check_baseline:
            # Re-run the original decks with the SAME shared engine, independently of KiCad export.
            for case,rl in [('baseline',50),('load-10k',10000)]:
                simulator.circuit(text)
                if case=='load-10k':simulator.command('alter R1 10k')
                exported=simulator.snapshot({'OUT':'/OUT','E':'/E','X':'/X'},'V1','M1','M2')
                reference=(LAB/f'{case}-op.cir').read_text(encoding='utf-8').split('.control')[0]
                reference=reference.replace('.include models.lib','.include "../models.lib"').replace('.include cascode-core.cir','.include "../cascode-core.cir"')+'\n.end\n'
                simulator.circuit(reference)
                original=simulator.snapshot({'OUT':'out','E':'xdut.e','X':'xdut.x'},'VDD','m.xdut.m1','m.xdut.m2')
                for key in ('OUT_V','E_V','X_V','supply_current_A'):close(exported[key],original[key],f'{case} {key}')
                for device in ('M1','M2'):
                    for key in exported['devices'][device]:close(exported['devices'][device][key],original['devices'][device][key],f'{case} {device} {key}')
                comparisons[case]={'exported':exported,'original':original,'all_checks_passed':True}
            checks.append('Both 50-ohm and 10-kohm OPs agree with original hierarchical decks, including currents, gm, gds, gmbs and saturation margins')
        log='\n'.join(simulator.log)+'\n'
        if re.search(r'(?im)\b(error|fatal)\b|no such vector|simulation\(s\) aborted|Controlled exit',log):
            raise RuntimeError(log)
        (output/'ngspice.log').write_text(log,encoding='utf-8')
        report={'run_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),'kicad_version':subprocess.check_output([str(cli),'version'],text=True).strip(),'ngspice_dll':str(dll),'ngspice_dll_sha256':sha(dll),'schematic_sha256':sha(PROJECT/'cascode-dc.kicad_sch'),'models_sha256':sha(LAB/'models.lib'),'netlist_sha256':sha(netlist),'current_schematic_op':current,'baseline_comparisons':comparisons,'checks':checks,'all_checks_passed':True}
        (output/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'current_schematic_op':current,'all_checks_passed':True,'results':str(output)},indent=2))
    finally:
        os.chdir(previous)


if __name__=='__main__':
    main()
