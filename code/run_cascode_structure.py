"""Study the saved KiCad cascode through structure-specific experiments.

Run: python code/run_cascode_structure.py
Uses KiCad's bundled ngspice DLL and NumPy/SciPy/Matplotlib. The saved
schematic is read-only; historical decks and results remain separate.
"""
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import root

from run_cascode_kicad import Ngspice, ROOT, LAB, PROJECT, sha
from run_cascode import analytic, matrix, expect, finite_load, cgain, falling_cross, roots_from_log, integrate

FIG = ROOT / 'figures/source-degenerated-cascode/current'
RESULT = LAB / 'current-study'
FREQ = 'dec 80 1 100T'
KBT4 = 4 * 1.380649e-23 * 300.15
PARAMS = ('id', 'gm', 'gmbs', 'gds', 'vgs', 'vds', 'von', 'vdsat', 'cgs', 'cgd', 'cgb', 'w', 'l', 'm')


def write_csv(path, array, header):
    np.savetxt(path, array, delimiter=',', header=header, comments='', fmt='%.15g')


def device_current(vg, vd, vs, device):
    """Independent LEVEL=1 equations, including body effect and triode."""
    vt = 0.45 + 0.4 * (np.sqrt(0.7 + vs) - np.sqrt(0.7))
    vov, vds = vg - vs - vt, vd - vs
    if vov <= 0:
        return 0.
    beta = 200e-6 * device['w'] / device['l'] * device['m']
    channel = vov * vds - 0.5 * vds**2 if vds < vov else 0.5 * vov**2
    return beta * channel * (1 + 0.03 * vds)


def dc_solution(vin, vb, vdd, rl, re_value, devices, guess, source_offset=0.):
    # Scale current unknown and equations in mA for numerical conditioning.
    def equations(u):
        current, vx = u[0] * 1e-3, u[1]
        ve, vo = current * re_value + source_offset, vdd - current * rl
        return np.array([device_current(vin, vx, ve, devices['M1']) - current,
                         device_current(vb, vo, vx, devices['M2']) - current]) * 1e3
    answer = root(equations, guess, tol=1e-11)
    if not answer.success and np.linalg.norm(equations(answer.x), np.inf) > 1e-9:
        raise RuntimeError(f'Independent DC solve failed at VIN={vin}: {answer.message}')
    return answer.x


def harmonics(time, voltage, frequency=1000.):
    keep = time >= 0.006
    t, y = time[keep], voltage[keep]
    basis = [np.ones_like(t)]
    for harmonic in range(1, 9):
        basis.extend([np.sin(2*np.pi*frequency*harmonic*t), np.cos(2*np.pi*frequency*harmonic*t)])
    coefficients = np.linalg.lstsq(np.column_stack(basis), y, rcond=None)[0]
    amplitudes = np.hypot(coefficients[1::2], coefficients[2::2])
    return {'DC_V':float(coefficients[0]), 'fundamental_peak_V':float(amplitudes[0]),
            'H2_percent':float(100*amplitudes[1]/amplitudes[0]),
            'THD_2_to_8_percent':float(100*np.linalg.norm(amplitudes[1:])/amplitudes[0])}


def savefig(name, figure, directory):
    for axis in figure.axes:
        axis.grid(True, alpha=.2)
    figure.savefig(directory/f'{name}.png', dpi=160)
    figure.savefig(directory/f'{name}.svg')
    plt.close(figure)


def main():
    kicad = Path(os.environ['LOCALAPPDATA'])/'Programs/KiCad/10.0/bin'
    schematic = PROJECT/'cascode-dc.kicad_sch'
    source_hash = sha(schematic)
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix='cascode-structure-') as temporary:
        work = Path(temporary)
        figure_dir = work/'figures'
        figure_dir.mkdir()
        export = work/'export.cir'
        subprocess.run([str(kicad/'kicad-cli.exe'), 'sch', 'export', 'netlist', '--format', 'spice',
                        '-o', str(export), str(schematic)], check=True, capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW, timeout=60)
        subprocess.run([str(kicad/'kicad-cli.exe'), 'sch', 'export', 'svg', '--exclude-drawing-sheet',
                        '--output', str(figure_dir), str(schematic)],check=True,capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW,timeout=60)
        # KiCad's stroked SVG uses M/L/Z paths in absolute page coordinates.
        # Crop page whitespace using the actual exported drawing extents.
        svg_path = figure_dir/'cascode-dc.svg'
        svg_text = svg_path.read_text(encoding='utf-8')
        svg_root = ET.fromstring(svg_text)
        pairs = []
        for path in svg_root.iter('{http://www.w3.org/2000/svg}path'):
            d = path.attrib['d']
            if set(re.findall('[A-Za-z]',d)) - set('MLZ'):
                raise RuntimeError('Review SVG cropping for a new path command')
            coordinates = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?',d)]
            pairs.extend(zip(coordinates[::2],coordinates[1::2]))
        x0,y0 = min(x for x,y in pairs)-4,min(y for x,y in pairs)-4
        width,height = max(x for x,y in pairs)-x0+4,max(y for x,y in pairs)-y0+4
        svg_text = re.sub(r'width="[^"]+" height="[^"]+" viewBox="[^"]+"',
                          f'width="{width:.4f}mm" height="{height:.4f}mm" viewBox="{x0:.4f} {y0:.4f} {width:.4f} {height:.4f}"',svg_text,count=1)
        svg_path.write_text(svg_text,encoding='utf-8')
        original = export.read_text(encoding='utf-8')
        model_include = f'.include "{(LAB/"models.lib").as_posix()}"'
        if model_include not in original:
            raise RuntimeError('Expected the existing shared educational model binding')
        cards = {line.split()[0].upper():line.split() for line in original.splitlines()
                 if line and line[0].upper() in 'MRVC' and not line.startswith('*')}
        expected = {'M1':['/X','/VIN','/E','/VSS'], 'M2':['/OUT','/VB','/X','/VSS'],
                    'R1':['/VDD','/OUT'], 'R2':['/E','/VSS'], 'C1':['/OUT','0'],
                    'V1':['/VDD','0'], 'V2':['/VIN','0'], 'V3':['/VB','0'], 'V4':['/VSS','0']}
        if set(cards) != set(expected):
            raise RuntimeError('Review the testbench after changing topology')
        for name, pins in expected.items():
            if cards[name][1:1+len(pins)] != pins:
                raise RuntimeError(f'Unexpected terminal tuple for {name}')
        vdd, vin, vb = (float(cards[k][4]) for k in ('V1','V2','V3'))
        rl, re_value = (float(cards[k][3]) for k in ('R1','R2'))
        if float(cards['V4'][4]) != 0 or cards['C1'][3].lower() != '1p':
            raise RuntimeError('This study expects VSS=0 and CL=1p')
        cl = 1e-12
        base = original.rsplit('.end', 1)[0].rstrip() + '\n'
        decks, logs, data = {}, {}, {}
        simulator = Ngspice(kicad/'ngspice.dll')
        simulator.command('version')
        engine_log = '\n'.join(simulator.log)
        def run(name, body, commands):
            text = body + '.end\n'
            # Runnable ngspice control decks accompany the shared-DLL run.
            control = ['set wr_singlescale', 'set wr_vecnames', 'set numdgt=15', *commands]
            deck = body + '.control\n' + '\n'.join(control) + '\nquit\n.endc\n.end\n'
            decks[name] = deck.replace(model_include, '.include "../models.lib"')
            start = len(simulator.log)
            simulator.circuit(text)
            for command in control:
                # Sharedspice command arguments need normalized device/node names.
                simulator.command(command.lower())
            log = '\n'.join(simulator.log[start:])+'\n'
            if re.search(r'(?im)\b(error|fatal)\b|no such vector|aborted|Controlled exit', log):
                raise RuntimeError(f'{name}: {log}')
            logs[name] = log
        def ac_body(body, source='V2'):
            return re.sub(rf'(?m)^({source}\s+[^\n]*?)\s*$', r'\1 AC 1', body)
        node_vectors = 'v(/OUT) v(/E) v(/X) i(V2)'
        try:
            os.chdir(work)
            run('op', base, ['op', 'show all'])
            devices = {f'M{i}':{p:simulator.vector(f'@m{i}[{p}]')[0] for p in PARAMS} for i in (1,2)}
            op = {name:simulator.vector(f'v(/{name})')[0] for name in ('OUT','E','X')}
            current = -simulator.vector('i(V1)')[0]
            for name, d in devices.items():
                d['saturation_margin_V'] = d['vds']-d['vdsat']
                if d['id'] <= 0 or d['saturation_margin_V'] <= 0:
                    raise RuntimeError(f'{name} is not conducting in saturation at the saved bias')
            expect([op['E']/re_value, (vdd-op['OUT'])/rl, devices['M1']['id']], current, 'DC KCL', rtol=1e-7)
            g = matrix(devices, rl, re_value)
            theory = analytic(devices, rl, re_value)
            a, b = devices['M1'], devices['M2']
            c = np.diag([a['cgs'], a['cgd']+b['cgs'], cl+b['cgd']])
            for name, body in [('ac-input', ac_body(base)), ('ac-bypass', ac_body(base)+'CB /E /VSS 100u\n'),
                               ('ac-bias', ac_body(base,'V3')), ('ac-output', base+'ITEST 0 /OUT DC 0 AC 1\n')]:
                run(name, body, ['op', f'ac {FREQ}', f'wrdata {name}.dat {node_vectors}'])
                data[name] = finite_load(work/f'{name}.dat')
            # The bypass is open at DC; independently verify an unchanged OP.
            run('bypass-op', base+'CB /E /VSS 100u\n', ['op','show all'])
            for name, value in op.items():
                expect(simulator.vector(f'v(/{name})')[0], value, f'Bypass preserves {name} DC', rtol=1e-9)
            f = data['ac-input'][:,0]
            s = 2j*np.pi*f
            gf = g[None,:,:] + s[:,None,None]*c[None,:,:]
            rhs = np.array([a['gm'],-a['gm'],0.])[None,:] + s[:,None]*np.array([a['cgs'],a['cgd'],0.])[None,:]
            solutions = np.linalg.solve(gf, rhs[...,None])[...,0]
            errors = {}
            def compare(name, prediction):
                observed = data[name]
                expect(observed[:,0], f, f'{name} frequency grid')
                for column in range(3):
                    values = observed[:,1+2*column] + 1j*observed[:,2+2*column]
                    expect(values, prediction[:,column], f'{name} complex node {column}', rtol=3e-4, atol=1e-13)
                errors[name] = float(np.max(abs(cgain(observed)-prediction[:,0])/np.maximum(abs(prediction[:,0]),1e-20)))
            # Acquisitions are OUT/E/X; matrix unknowns are E/X/OUT.
            compare('ac-input', solutions[:,[2,0,1]])
            cb = c.copy(); cb[0,0] += 100e-6
            bypass_solution = np.linalg.solve(g[None,:,:]+s[:,None,None]*cb[None,:,:],rhs[...,None])[...,0]
            compare('ac-bypass', bypass_solution[:,[2,0,1]])
            bias_rhs = np.array([0.,b['gm'],-b['gm']])[None,:]+s[:,None]*np.array([0.,b['cgs'],b['cgd']])[None,:]
            bias_solution = np.linalg.solve(gf,bias_rhs[...,None])[...,0]
            compare('ac-bias',bias_solution[:,[2,0,1]])
            output_solution = np.linalg.solve(gf,np.broadcast_to(np.array([0.,0.,1.])[None,:,None],(len(f),3,1)))[...,0]
            compare('ac-output',output_solution[:,[2,0,1]])
            observed_i = data['ac-input'][:,7]+1j*data['ac-input'][:,8]
            predicted_y = s*(a['cgs']*(1-solutions[:,0])+a['cgd']*(1-solutions[:,1])+a['cgb'])
            expect(-observed_i,predicted_y,'Input capacitor currents',rtol=3e-4,atol=1e-18)
            gain = cgain(data['ac-input'])
            bypass_gain = cgain(data['ac-bypass'])
            expect(gain[0].real,theory['gain'],'Signed LF gain',rtol=1e-7)
            expect(cgain(data['ac-output'])[0].real,theory['rout_ohm'],'Loaded resistance',rtol=1e-7)
            intrinsic = np.linalg.solve(matrix(devices,np.inf,re_value),[0,0,1])[2]
            expect(intrinsic,theory['rstack_ohm'],'Unloaded KCL vs closed form',rtol=1e-9)
            noise_commands = [f'noise v(/OUT) v2 {FREQ} 1','setplot previous',
                              'wrdata noise.dat onoise_spectrum inoise_spectrum onoise_m1 onoise_m2 onoise_r2 onoise_r1']
            run('noise',ac_body(base),noise_commands)
            noise = finite_load(work/'noise.dat'); data['noise'] = noise
            q = np.array([[1,-1,0],[0,1,-1],[1,0,0],[0,0,1]],dtype=float)
            h = np.linalg.solve(gf,np.broadcast_to(q.T,(len(f),3,4)))[:,2,:]
            source_psd = KBT4*np.array([2/3*a['gm'],2/3*b['gm'],1/re_value,1/rl])
            predicted_noise = abs(h)**2*source_psd[None,:]
            expect(noise[:,0],f,'Noise frequency grid')
            expect(noise[:,3:7]**2,predicted_noise,'Every thermal noise source vs current-injection MNA',rtol=3e-4)
            expect(np.sum(noise[:,3:7]**2,axis=1),noise[:,1]**2,'Noise source power sum',rtol=1e-7)
            expect(noise[:,1]/abs(gain),noise[:,2],'Noise input referral',rtol=1e-7)
            pz_body = re.sub(r'(?m)^V2[^\n]*\n',
                             f'VCM cm 0 DC {vin:g}\nRDC signal 0 1G\nEIN /VIN cm signal 0 1\n',base)
            run('poles-zeros',pz_body,['pz signal 0 /OUT 0 vol pz','print all'])
            roots = roots_from_log(re.sub(r'(?m)^stdout ', '', logs['poles-zeros']))
            predicted_poles = np.linalg.eigvals(-np.linalg.solve(c,g))
            ae = 1/re_value + theory['k1_S']
            numerator = b['gm']+b['gmbs']+b['gds']
            zero_coefficients = numerator*np.array([a['cgs']*a['cgd'],
                ae*a['cgd']+(theory['k1_S']-a['gm'])*a['cgs'], -a['gm']/re_value])
            predicted_zeros = np.roots(zero_coefficients)
            expect(sorted(p.real for p in roots['pole']),sorted(predicted_poles),'C/G eigenvalue poles',rtol=1e-5)
            expect(sorted(z.real for z in roots['zero']),sorted(predicted_zeros),'Transfer numerator zeros',rtol=1e-5)
            reconstructed = np.full(len(f),theory['gain'],dtype=complex)
            for z in roots['zero']: reconstructed *= 1-s/z
            for p in roots['pole']: reconstructed /= 1-s/p
            expect(reconstructed,gain,'Complex PZ reconstruction',rtol=3e-4,atol=1e-13)
            dc_commands = ['save all @m1[vdsat] @m2[vdsat]',
                           f'dc V2 {vin-.09:.12g} {vin+.08:.12g} 0.0005',
                           'let margin1=v(/X)-v(/E)-@m1[vdsat]',
                           'let margin2=v(/OUT)-v(/X)-@m2[vdsat]',
                           'wrdata dc-transfer.dat v(/OUT) v(/E) v(/X) margin1 margin2']
            run('dc-transfer',base,dc_commands)
            dc = finite_load(work/'dc-transfer.dat'); data['dc-transfer'] = dc
            predicted_dc = []
            guess = np.array([current*1e3,op['X']])
            for value in dc[:,0]:
                guess = dc_solution(value,vb,vdd,rl,re_value,devices,guess)
                predicted_dc.append([vdd-guess[0]*1e-3*rl,guess[0]*1e-3*re_value,guess[1]])
            predicted_dc = np.array(predicted_dc)
            expect(dc[:,1:4],predicted_dc,'Independent nonlinear DC solve',rtol=1e-7,atol=2e-9)
            # A central derivative at the nominal input checks the signed AC gain.
            ix = int(np.argmin(abs(dc[:,0]-vin)))
            local_slope = (dc[ix+1,1]-dc[ix-1,1])/(dc[ix+1,0]-dc[ix-1,0])
            expect(local_slope,theory['gain'],'DC central slope',rtol=2e-6)
            curve_second = (dc[ix+1,1]-2*dc[ix,1]+dc[ix-1,1])/0.0005**2
            sine_metrics = {}
            sine_predictions = {}
            clamped_base = re.sub(r'(?m)^R2[^\n]*\n',f'VFIX /E /VSS DC {op["E"]:.16g}\n',base)
            run('clamp-op',clamped_base,['op','show all'])
            for name,value in op.items():
                expect(simulator.vector(f'v(/{name})')[0],value,f'Source clamp preserves {name} OP',rtol=1e-9)
            experiments = [(f'sine-{int(amplitude*1000)}mV',amplitude,base,re_value,0.)
                           for amplitude in (0.005,0.01,0.02,0.05)]
            experiments.append(('sine-clamped-10mV',0.01,clamped_base,0.,op['E']))
            for name, amplitude, experiment_base, experiment_re, source_offset in experiments:
                body = re.sub(r'(?m)^V2[^\n]*\n',f'V2 /VIN 0 SIN({vin:g} {amplitude:g} 1k)\n',experiment_base)
                commands = ['save all @m1[vdsat] @m2[vdsat]', 'tran 1u 10m 0 1u',
                            'let margin1=v(/X)-v(/E)-@m1[vdsat]',
                            'let margin2=v(/OUT)-v(/X)-@m2[vdsat]',
                            f'wrdata {name}.dat v(/VIN) v(/OUT) margin1 margin2']
                run(name,body,commands)
                wave = finite_load(work/f'{name}.dat'); data[name] = wave
                metrics = harmonics(wave[:,0],wave[:,2])
                second, slope = curve_second, local_slope
                if experiment_re == 0:
                    dc_values = []
                    for value in (vin-0.0005,vin,vin+0.0005):
                        trial = dc_solution(value,vb,vdd,rl,0.,devices,[current*1e3,op['X']],source_offset)
                        dc_values.append(vdd-trial[0]*1e-3*rl)
                    second = (dc_values[2]-2*dc_values[1]+dc_values[0])/0.0005**2
                    slope = (dc_values[2]-dc_values[0])/0.001
                metrics.update({'input_peak_V':amplitude,
                    'fundamental_gain_magnitude':metrics['fundamental_peak_V']/amplitude,
                    'minimum_M1_margin_V':float(wave[:,3].min()),
                    'minimum_M2_margin_V':float(wave[:,4].min()),
                    'small_amplitude_H2_prediction_percent':float(100*abs(second)*amplitude/(4*abs(slope)))})
                # Reconstruct the waveform from independent device equations at measured VIN.
                # Frequency is far below the output pole, so a quasistatic prediction applies.
                predicted_wave = []
                guess = np.array([current*1e3,op['X']])
                for value in wave[:,1]:
                    guess = dc_solution(value,vb,vdd,rl,experiment_re,devices,guess,source_offset)
                    predicted_wave.append(vdd-guess[0]*1e-3*rl)
                predicted_wave = np.array(predicted_wave)
                independent_metrics = harmonics(wave[:,0],predicted_wave)
                expect(metrics['fundamental_peak_V'],independent_metrics['fundamental_peak_V'],
                       f'{name} quasistatic fundamental',rtol=2e-4)
                expect(metrics['THD_2_to_8_percent'],independent_metrics['THD_2_to_8_percent'],
                       f'{name} quasistatic THD',rtol=2e-3)
                metrics['independent_quasistatic_THD_percent'] = independent_metrics['THD_2_to_8_percent']
                sine_metrics[name] = metrics
                sine_predictions[name] = predicted_wave
            # A small pulse tests the dominant-pole prediction at the same bias.
            tau = rl*cl
            step_body = re.sub(r'(?m)^V2[^\n]*\n',
                f'V2 /VIN 0 PULSE({vin:g} {vin+0.0001:.12g} {10*tau:.12g} {tau/50:.12g} {tau/50:.12g} {20*tau:.12g} {50*tau:.12g})\n',base)
            run('step',step_body,[f'tran {tau/100:.12g} {40*tau:.12g} 0 {tau/100:.12g}',
                                 'wrdata step.dat v(/VIN) v(/OUT)'])
            step = finite_load(work/'step.dat'); data['step'] = step
            initial = float(np.mean(step[step[:,0]<9*tau,2]))
            plateau = float(np.mean(step[(step[:,0]>25*tau)&(step[:,0]<29*tau),2]))
            expect((plateau-initial)/0.0001,theory['gain'],'Step plateau vs AC',rtol=4e-4)
            slow_pole = max(p.real for p in roots['pole'])
            slow_tau = -1/slow_pole
            edge_end = 10*tau+tau/50
            from run_cascode import last_exit
            relative_step_error = abs(step[:,2]-plateau)/abs(plateau-initial)
            settling = {str(epsilon):last_exit(step[:,0],relative_step_error,edge_end,30*tau,epsilon)
                        for epsilon in (0.01,0.001)}
            for epsilon in (0.01,0.001):
                expect(settling[str(epsilon)],slow_tau*np.log(1/epsilon),'Dominant-pole settling',rtol=.03)
            lf_sources = noise[0,3:7]**2
            integrand = noise[:,2]**2
            thermal_rms = float(np.sqrt(integrate(f,integrand,10,1e5)))
            bypass_ix = int(np.argmin(abs(f-1e4)))
            cin_lf = a['cgs']*(1-theory['E_gain'])+a['cgd']*(1-theory['X_gain'])+a['cgb']
            report = {'run_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
                'kicad_version':subprocess.check_output([str(kicad/'kicad-cli.exe'),'version'],text=True).strip(),
                'ngspice_version_log':engine_log, 'ngspice_dll_sha256':sha(kicad/'ngspice.dll'),
                'schematic_sha256':source_hash, 'models_sha256':sha(LAB/'models.lib'), 'script_sha256':sha(Path(__file__)),
                'parameters':{'VDD_V':vdd,'VSS_V':0,'VIN_V':vin,'VB_V':vb,'RL_ohm':rl,'RE_ohm':re_value,'CL_F':cl},
                'devices':devices,'op':op,'current_A':current,'power_W':vdd*current,'theory':theory,
                'measured_gain_V_V':float(gain[0].real),'DC_slope_V_V':float(local_slope),
                'degeneration':{'factor_approx':1+(a['gm']+a['gmbs'])*re_value,
                    'bypass_gain_at_10kHz_real_V_V':float(bypass_gain[bypass_ix].real),
                    'bypass_gain_at_10kHz_imag_V_V':float(bypass_gain[bypass_ix].imag)},
                'input_capacitance_F':float(cin_lf), 'full_AC_relative_errors':errors,
                'noise':{'input_V_sqrtHz':float(noise[0,2]),'output_V_sqrtHz':float(noise[0,1]),
                    'sources':{label:{'output_V_sqrtHz':float(noise[0,3+i]),
                        'input_V_sqrtHz':float(noise[0,3+i]/abs(gain[0])),
                        'PSD_percent':float(100*lf_sources[i]/lf_sources.sum())} for i,label in enumerate(('M1','M2','RE','RL'))},
                    'M2_to_M1_PSD_ratio':float(lf_sources[1]/lf_sources[0]),
                    'input_RMS_10Hz_100kHz_V':thermal_rms},
                'poles_rad_s':[p.real for p in roots['pole']], 'zeros_rad_s':[z.real for z in roots['zero']],
                'bandwidth_minus3dB_Hz':falling_cross(f,20*np.log10(abs(gain)),20*np.log10(abs(gain[0]))-3.),
                'unity_Hz':falling_cross(f,20*np.log10(abs(gain)),0.),
                'sine':sine_metrics, 'step':{'predicted_change_V':theory['gain']*0.0001,
                    'measured_change_V':plateau-initial,'slow_tau_s':slow_tau,'settling_s':settling},
                'sampled_VIN_both_saturated_V':[float(dc[(dc[:,4]>0)&(dc[:,5]>0),0].min()),
                                              float(dc[(dc[:,4]>0)&(dc[:,5]>0),0].max())],
                'checks':['Saved topology and source hash','DC KCL and conducting saturation',
                    'Unchanged DC bias with AC bypass and ideal source-clamp control','Independent complex KCL for OUT/E/X and input current',
                    'Loaded output injection and intrinsic resistance closed form vs KCL',
                    'Independent per-source thermal current injections and PSD sum/input referral',
                    'C/G poles, numerator zeros, and full complex PZ reconstruction',
                    'Independent nonlinear DC equations and local DC slope vs AC',
                    'Independent quasistatic sinusoid fundamentals and harmonic distortion',
                    'Small-step plateau and dominant-pole settling'], 'all_checks_passed':True}
            make_plots(data,report,solutions,bypass_solution,predicted_noise,predicted_dc,sine_predictions,figure_dir)
        finally:
            os.chdir(previous)
        if sha(schematic) != source_hash:
            raise RuntimeError('Saved schematic changed during the study; rerun')
        for name, deck in decks.items():
            (work/f'{name}.cir').write_text(deck,encoding='utf-8')
            (work/f'{name}.log').write_text(logs[name],encoding='utf-8')
        for name, array in data.items():
            if name.startswith('ac-'): header='frequency_Hz,OUT_real,OUT_imag,E_real,E_imag,X_real,X_imag,V2_current_real_A,V2_current_imag_A'
            elif name=='noise': header='frequency_Hz,output_V_sqrtHz,input_V_sqrtHz,M1_output_V_sqrtHz,M2_output_V_sqrtHz,RE_output_V_sqrtHz,RL_output_V_sqrtHz'
            elif name=='dc-transfer': header='VIN_V,OUT_V,E_V,X_V,M1_margin_V,M2_margin_V'
            elif name=='step': header='time_s,VIN_V,OUT_V'
            else: header='time_s,VIN_V,OUT_V,M1_margin_V,M2_margin_V'
            write_csv(work/f'{name}.csv',array,header)
        report['deck_sha256'] = {name:sha(work/f'{name}.cir') for name in decks}
        (work/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        RESULT.mkdir(exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
        for path in work.iterdir():
            if path.is_file() and path.name != 'export.cir': shutil.copy2(path,RESULT/path.name)
        for path in figure_dir.iterdir(): shutil.copy2(path,FIG/path.name)
    print(json.dumps(report,indent=2))


def make_plots(data,r,solution,bypass,predicted_noise,predicted_dc,sine_prediction,directory):
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'figure.constrained_layout.use':True})
    f = data['ac-input'][:,0]; gain = cgain(data['ac-input'])
    fig,ax = plt.subplots(1,2,figsize=(12,4.3))
    ax[0].semilogx(f,20*np.log10(abs(gain)),label='Saved circuit: ngspice')
    ax[0].semilogx(f,20*np.log10(abs(cgain(data['ac-bypass']))),label='100 uF source bypass: ngspice')
    ax[0].semilogx(f,20*np.log10(abs(bypass[:,2])),ls='--',color='black',alpha=.6,label='Independent bypass KCL')
    ax[0].set(xlim=(1,1e10),ylim=(-20,15),xlabel='Frequency (Hz)',ylabel='Voltage gain magnitude (dB)',title='Degeneration changes signal transconductance')
    ax[0].legend(fontsize=8)
    for values,prediction,label in [(data['ac-input'][:,3]+1j*data['ac-input'][:,4],solution[:,0],'|E / VIN|: source feedback'),
                                    (data['ac-input'][:,5]+1j*data['ac-input'][:,6],solution[:,1],'|X / VIN|: M1 drain'),
                                    (gain,solution[:,2],'|OUT / VIN|')]:
        line,=ax[1].semilogx(f,abs(values),label=label)
        ax[1].semilogx(f,abs(prediction),ls='--',color=line.get_color(),alpha=.6)
    ax[1].set(xlim=(1,1e10),xlabel='Frequency (Hz)',ylabel='Transfer magnitude (V/V)',title='Internal-node motion explains the structure')
    ax[1].legend(fontsize=8);savefig('degeneration-and-nodes',fig,directory)
    fig,ax = plt.subplots(1,2,figsize=(12,4.3))
    rout = cgain(data['ac-output'])
    ax[0].loglog(f,abs(rout),label='Loaded OUT injection: ngspice')
    ax[0].axhline(r['theory']['rstack_ohm'],ls='--',color='darkorange',label='Intrinsic DC resistance: model calculation')
    ax[0].set(xlim=(1,1e11),xlabel='Frequency (Hz)',ylabel='Output impedance magnitude (ohm)',title='Cascode resistance and the 1 kohm load')
    ax[0].legend(fontsize=8)
    a = r['devices']['M1']; ae,axgain = r['theory']['E_gain'],r['theory']['X_gain']
    labels = ['Cgs1 (1 - AE)','Cgd1 (1 - AX)','Total input']
    values = [a['cgs']*(1-ae),a['cgd']*(1-axgain),r['input_capacitance_F']]
    ax[1].bar(labels,np.array(values)*1e15,color=['#3482b8','#e3a43b','#278b70'])
    ax[1].set(ylabel='Low-frequency input capacitance (fF)',title='Use the M1 drain gain in its Miller term')
    savefig('cascode-and-input',fig,directory)
    noise = data['noise']; labels = ['M1','M2','RE','RL']
    fig,ax = plt.subplots(1,2,figsize=(12,4.5))
    for i,label in enumerate(labels):
        line, = ax[0].loglog(f,noise[:,3+i]/abs(gain)*1e9,label=label+' ngspice')
        ax[0].loglog(f,np.sqrt(predicted_noise[:,i])/abs(gain)*1e9,ls='--',color=line.get_color(),alpha=.55)
    ax[0].loglog(f,noise[:,2]*1e9,color='black',lw=2,label='Total')
    ax[0].set(xlim=(1,1e13),xlabel='Frequency (Hz)',ylabel='Input noise density (nV / sqrt(Hz))',title='Thermal noise: solid simulation, dashed KCL')
    ax[0].legend(fontsize=8)
    fractions = [r['noise']['sources'][label]['PSD_percent'] for label in labels]
    ax[1].bar(labels,fractions,color=['#3482b8','#a06bba','#278b70','#e3a43b'])
    ax[1].set(yscale='log',ylim=(1e-4,100),ylabel='Fraction of total output PSD (%)',title='Low-frequency contributions at the saved bias')
    for i,value in enumerate(fractions):ax[1].text(i,value*1.3,f'{value:.4g}%',ha='center',fontsize=9)
    savefig('thermal-noise',fig,directory)
    dc = data['dc-transfer']
    fig,ax = plt.subplots(1,2,figsize=(12,4.4))
    ax[0].plot(dc[:,0],dc[:,1],label='ngspice DC transfer')
    ax[0].plot(dc[:,0],predicted_dc[:,0],ls='--',color='black',label='Independent MOS1 nonlinear solve')
    nominal = r['parameters']['VIN_V']
    ax[0].plot(dc[:,0],r['op']['OUT']+r['measured_gain_V_V']*(dc[:,0]-nominal),ls=':',label='Nominal small-signal tangent')
    ax[0].set(xlabel='Input DC voltage (V)',ylabel='Output DC voltage (V)',title='Gain is a local slope')
    ax[0].legend(fontsize=8)
    ax[1].plot(dc[:,0],dc[:,4]*1e3,label='M1')
    ax[1].plot(dc[:,0],dc[:,5]*1e3,label='M2')
    ax[1].axhline(0,color='black',lw=.8); ax[1].axvline(nominal,color='gray',ls=':')
    ax[1].set(xlabel='Input DC voltage (V)',ylabel='VDS - VDSsat (mV)',title='Signal range is limited by internal headroom')
    ax[1].legend();savefig('signal-range',fig,directory)
    fig,ax = plt.subplots(1,2,figsize=(12,4.5))
    for name in ('sine-10mV','sine-50mV'):
        wave = data[name]; keep=(wave[:,0]>=.008)&(wave[:,0]<=.009)
        ax[0].plot((wave[keep,0]-.008)*1e3,(wave[keep,2]-r['op']['OUT'])*1e3,label=name+' ngspice')
        ax[0].plot((wave[keep,0]-.008)*1e3,(sine_prediction[name][keep]-r['op']['OUT'])*1e3,ls='--',color='black',alpha=.45)
    ax[0].set(xlabel='Time within one cycle (ms)',ylabel='Output change from nominal (mV)',title='1 kHz sinusoids; dashed independent DC solution')
    ax[0].legend(fontsize=8)
    normal = [m for name,m in r['sine'].items() if 'clamped' not in name]
    amplitudes = [m['input_peak_V']*1e3 for m in normal]
    thd = [m['THD_2_to_8_percent'] for m in normal]
    predicted = [m['independent_quasistatic_THD_percent'] for m in normal]
    ax[1].plot(amplitudes,thd,'o-',label='ngspice transient')
    ax[1].plot(amplitudes,predicted,'x--',label='Independent quasistatic prediction')
    ax[1].set(xlabel='Input peak amplitude (mV)',ylabel='THD, harmonics 2-8 (%)',title='Saturation does not imply zero distortion')
    ax[1].legend(fontsize=8);savefig('sinusoidal-distortion',fig,directory)
    fig,ax = plt.subplots(1,2,figsize=(12,4.4))
    ax[0].semilogx(f,20*np.log10(abs(gain)),label='ngspice AC')
    ax[0].semilogx(f,20*np.log10(abs(solution[:,2])),ls='--',label='Independent G + sC')
    ax[0].axvline(r['bandwidth_minus3dB_Hz'],color='gray',ls=':')
    ax[0].set(xlim=(1e5,1e11),ylim=(-50,15),xlabel='Frequency (Hz)',ylabel='Voltage gain magnitude (dB)',title='Fixed bias and load: frequency response')
    ax[0].legend(fontsize=8)
    step=data['step']; tau=r['parameters']['RL_ohm']*r['parameters']['CL_F']
    shifted=step[:,0]-10*tau
    prediction=r['step']['predicted_change_V']*(1-np.exp(-np.maximum(shifted,0)/r['step']['slow_tau_s']))
    ax[1].plot(shifted*1e9,(step[:,2]-r['op']['OUT'])*1e6,label='ngspice 100 uV step')
    ax[1].plot(shifted*1e9,prediction*1e6,ls='--',label='Instantaneous-step dominant pole')
    ax[1].set(xlim=(-1,10),xlabel='Time from rising-edge start (ns)',ylabel='Output change (uV)',title='Small-signal open-loop settling')
    ax[1].legend(fontsize=8);savefig('frequency-and-step',fig,directory)


if __name__ == '__main__':
    main()
