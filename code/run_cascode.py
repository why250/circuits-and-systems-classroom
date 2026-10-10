"""Run 26 ngspice testbenches and independently check the supplied cascode.

python code/run_cascode.py --ngspice /path/to/ngspice [--generate-decks]
Generation is opt-in: ordinary reruns preserve authored/edited testbenches.
Requires NumPy and Matplotlib; no PDK is required for the teaching models.
"""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'simulations/source-degenerated-cascode'
FIG = ROOT / 'figures/source-degenerated-cascode'
CASES = {'baseline': 50., 'load-10k': 10000.}
DECKS = ('op', 'ac-input', 'ac-bias', 'ac-output', 'ac-psrr-positive',
         'ac-psrr-negative', 'noise', 'noise-flicker', 'poles-zeros',
         'dc-transfer', 'bias-sweep', 'transient')
PARAMS = ('id', 'gm', 'gds', 'gmbs', 'vgs', 'vds', 'von', 'vdsat', 'cgs', 'cgd', 'cgb')
SWEEPS = {'load-sweep': ('rl', (50, 100, 200, 500, 1000, 2000, 5000, 10000, 15000, 20000, 25000, 30000, 40000)),
          'degeneration-sweep': ('re', (0.1, 10, 50, 100, 500, 1000, 2000, 5000))}
FREQ = 'dec 100 1 100T'
KBT4 = 4 * 1.380649e-23 * 300.15


def generate_decks():
    setup = ['set noaskquit', 'set wr_singlescale', 'set wr_vecnames', 'set numdgt=15']
    opvectors = 'v(out) v(xdut.e) v(xdut.x) i(VDD)'
    devicevectors = ' '.join(f'@m.xdut.m{i}[{p}]' for i in (1, 2) for p in PARAMS)
    for case, rl in CASES.items():
        for deck in DECKS:
            title = f'Cascode {case}: {deck}; teaching LEVEL=1, not SKY130'
            cards = [title, '.include models.lib', '.include cascode-core.cir', '.temp 27',
                     '.options reltol=1e-8 abstol=1e-15 vntol=1e-12']
            cards += ['VDD vdd 0 DC 1.8' + (' AC 1' if deck == 'ac-psrr-positive' else ''),
                      'VSS vss 0 DC 0' + (' AC 1' if deck == 'ac-psrr-negative' else ''),
                      'VB vb 0 DC 1.25' + (' AC 1' if deck == 'ac-bias' else '')]
            tau = rl * 1e-12
            if deck == 'poles-zeros':
                cards += ['VCM cm 0 0.75', 'RDC signal 0 1G', 'EIN vin cm signal 0 1']
            elif deck == 'transient':
                cards += [f'VIN vin 0 PULSE(0.75 0.7501 {10*tau:.12g} {tau/50:.12g} {tau/50:.12g} {20*tau:.12g} {50*tau:.12g})']
            else:
                cards += ['VIN vin 0 DC 0.75' + (' AC 1' if deck in ('ac-input', 'noise', 'noise-flicker') else '')]
            cards += [f'XDUT vdd vss vin out vb cascode RLVAL={rl:g} REVAL=50', 'CL out 0 1p']
            if deck == 'ac-output':
                cards += ['ITEST 0 out DC 0 AC 1']
            control = setup.copy()
            if deck == 'op':
                control += ['op', 'show all', f'wrdata {case}-op.dat {opvectors}',
                            f'wrdata {case}-devices.dat {devicevectors}',
                            f'wrdata {case}-model.dat @nmos_edu[tox] @nmos_edu[ld] @m.xdut.m1[w] @m.xdut.m1[l] @m.xdut.m2[w] @m.xdut.m2[l]']
            elif deck.startswith('ac-'):
                control += [f'ac {FREQ}', f'wrdata {case}-{deck}.dat v(out) v(xdut.e) v(xdut.x) i(VIN)']
            elif deck in ('noise', 'noise-flicker'):
                if deck == 'noise-flicker':
                    control += ['altermod NMOS_EDU kf=2e-33', 'altermod NMOS_EDU af=1', 'op',
                                f'wrdata {case}-flicker-op.dat {opvectors}']
                control += [f'noise v(out) VIN {FREQ} 1', 'setplot noise1']
                nvectors = ('onoise_spectrum inoise_spectrum onoise_m.xdut.m1 onoise_m.xdut.m2 '
                            'onoise_r.xdut.re onoise_r.xdut.rl')
                if deck == 'noise-flicker':
                    nvectors += (' onoise_m.xdut.m1_1overf onoise_m.xdut.m2_1overf'
                                 ' onoise_m.xdut.m1_id onoise_m.xdut.m2_id')
                control += [f'wrdata {case}-{deck}.dat {nvectors}']
            elif deck == 'poles-zeros':
                control += ['pz signal 0 out 0 vol pz', 'print all']
            elif deck in ('dc-transfer', 'bias-sweep'):
                control += ['save all @m.xdut.m1[vdsat] @m.xdut.m2[vdsat] @m.xdut.m1[gm] @m.xdut.m2[gm]',
                            'dc VIN 0.45 1.05 0.0005' if deck == 'dc-transfer' else 'dc VB 0.9 1.7 0.002',
                            'let margin1=v(xdut.x)-v(xdut.e)-@m.xdut.m1[vdsat]',
                            'let margin2=v(out)-v(xdut.x)-@m.xdut.m2[vdsat]',
                            f'wrdata {case}-{deck}.dat {opvectors} margin1 margin2 @m.xdut.m1[gm] @m.xdut.m2[gm]']
            elif deck == 'transient':
                control += [f'tran {tau/100:.12g} {40*tau:.12g} 0 {tau/100:.12g}',
                            f'wrdata {case}-transient.dat v(out) v(vin) v(xdut.e) v(xdut.x)']
            cards += ['.control', *control, 'quit', '.endc', '.end']
            (LAB / f'{case}-{deck}.cir').write_text('\n'.join(cards)+'\n', encoding='utf-8')
    for deck, (resistor, values) in SWEEPS.items():
        cards = [f'Cascode {deck}; each point recomputes bias and unit AC gain', '.include models.lib',
                 '.include cascode-core.cir', '.temp 27', '.options reltol=1e-8 abstol=1e-15 vntol=1e-12',
                 'VDD vdd 0 1.8', 'VSS vss 0 0', 'VIN vin 0 DC 0.75 AC 1', 'VB vb 0 1.25',
                 'XDUT vdd vss vin out vb cascode RLVAL=10000 REVAL=50', 'CL out 0 1p', '.control', *setup]
        for i, value in enumerate(values):
            cards += [f'alter r.xdut.{resistor} {value:g}', 'op',
                      f'wrdata {deck}-{i}-op.dat {opvectors}',
                      f'wrdata {deck}-{i}-devices.dat {devicevectors}',
                      'ac lin 1 1 1', f'wrdata {deck}-{i}-ac.dat v(out)']
        cards += ['quit', '.endc', '.end']
        (LAB / f'{deck}.cir').write_text('\n'.join(cards)+'\n', encoding='utf-8')


def matrix(devices, rl, re_):
    a, b = devices['M1'], devices['M2']
    k1, k2 = (d['gm']+d['gmbs']+d['gds'] for d in (a, b))
    return np.array([[1/re_+k1, -a['gds'], 0],
                     [-k1, a['gds']+k2, -b['gds']],
                     [0, -k2, 1/rl+b['gds']]])


def analytic(devices, rl, re_):
    a, b = devices['M1'], devices['M2']
    k1, k2 = (d['gm']+d['gmbs']+d['gds'] for d in (a, b))
    d1 = 1+k1*re_
    aa, bb = a['gm']/d1, a['gds']/d1
    den = k2+bb*(1+b['gds']*rl)
    r1 = d1/a['gds']
    rstack = (k2+bb)/(bb*b['gds'])
    gshort = aa*k2/(k2+bb)
    rout = 1/(1/rl+1/rstack)
    return {'gain': -rl*aa*k2/den, 'E_gain': re_*aa*k2/den,
            'X_gain': -aa*(1+b['gds']*rl)/den, 'bias_gain': -rl*bb*b['gm']/den,
            'r1_ohm': r1, 'rstack_ohm': rstack, 'rout_ohm': rout, 'gm_short_S': gshort,
            'gain_approx': -a['gm']*rl/(1+(a['gm']+a['gmbs'])*re_),
            'psrr_positive_transfer': rstack/(rstack+rl), 'k1_S': k1, 'k2_S': k2}


def finite_load(path):
    a = np.loadtxt(path, skiprows=1, ndmin=2)
    if not np.isfinite(a).all():
        raise ValueError(f'Nonfinite acquisition: {path}')
    return a


def devices_from_row(row):
    return {f'M{i}': dict(zip(PARAMS, map(float, row[1+(i-1)*len(PARAMS):1+i*len(PARAMS)]))) for i in (1, 2)}


def cgain(data):
    return data[:, 1]+1j*data[:, 2]


def falling_cross(f, values, level):
    indices = np.flatnonzero((values[:-1] >= level) & (values[1:] < level))
    if not len(indices):
        return None
    i = indices[0]
    return float(10**np.interp(level, values[i:i+2][::-1], np.log10(f[i:i+2])[::-1]))


def integrate(f, psd, low, high):
    grid = np.r_[low, f[(f > low) & (f < high)], high]
    vals = np.interp(np.log(grid), np.log(f), psd)
    return float(np.trapezoid(vals, grid))


def expect(actual, predicted, label, rtol=2e-5, atol=0):
    if not np.allclose(actual, predicted, rtol=rtol, atol=atol):
        raise ValueError(f'{label}: observed {actual}, predicted {predicted}')


def roots_from_log(log):
    matches = re.findall(r'(?im)^\s*(pole|zero)\((\d+)\)\s*=\s*([+-]?[\d.eE+-]+)\s*,\s*([+-]?[\d.eE+-]+)', log)
    roots = {kind: [] for kind in ('pole', 'zero')}
    for kind, _, real, imag in matches:
        roots[kind].append(complex(float(real), float(imag)))
    if not roots['pole'] or not roots['zero']:
        raise ValueError('Missing extracted PZ roots')
    return roots


def last_exit(t, error, edge_end, edge_fall, tolerance):
    valid = (t >= edge_end) & (t < edge_fall)
    indices = np.flatnonzero(valid)
    bad = indices[error[valid] > tolerance]
    if not len(bad):
        return 0.
    i = bad[-1]
    if i+1 >= len(t) or t[i+1] >= edge_fall:
        raise ValueError('Transient never settles inside pulse')
    cross = np.interp(tolerance, error[i:i+2][::-1], t[i:i+2][::-1])
    return float(cross-edge_end)


def check_case(case, rl, work, logs):
    op = finite_load(work/f'{case}-op.dat')[0, 1:]
    devices = devices_from_row(finite_load(work/f'{case}-devices.dat')[0])
    model = finite_load(work/f'{case}-model.dat')[0, 1:]
    data = {d: finite_load(work/f'{case}-{d}.dat') for d in DECKS if d not in ('op', 'poles-zeros')}
    g = matrix(devices, rl, 50.)
    theory = analytic(devices, rl, 50.)
    a, b = devices['M1'], devices['M2']
    # Independent unloaded-matrix test also catches double-counting gd2 in k2.
    unloaded_matrix_rout = np.linalg.solve(matrix(devices, np.inf, 50.), [0., 0., 1.])[2]
    cascoded_resistance = 1/b['gds']+(1+(b['gm']+b['gmbs'])/b['gds'])*theory['r1_ohm']
    expect([unloaded_matrix_rout, cascoded_resistance], theory['rstack_ohm'], 'intrinsic stack resistance with RL AC removed', rtol=1e-8)
    f = data['ac-input'][:, 0]
    if len(f) != 1401 or data['dc-transfer'].shape[0] != 1201 or data['bias-sweep'].shape[0] != 401 or len(data['transient']) < 4000:
        raise ValueError('Incomplete frequency/DC/transient acquisition')
    gain = cgain(data['ac-input'])
    margin = {name: d['vds']-d['vdsat'] for name, d in devices.items()}
    if min(margin.values()) <= 0 or min(d['gm'] for d in devices.values()) <= 0:
        raise ValueError('Nominal devices not conducting in saturation')
    expect(a['id'], b['id'], 'series current balance', rtol=1e-6)
    expect([op[1]/50., (1.8-op[0])/rl], [a['id'], b['id']], 'resistor DC KCL', rtol=1e-6)
    for name, d, w, l, source_v in [('M1', a, model[2], model[3], op[1]), ('M2', b, model[4], model[5], op[2])]:
        vth = 0.45+0.4*(np.sqrt(0.7+source_v)-np.sqrt(0.7))
        current = 200e-6/2*w/l*(d['vgs']-vth)**2*(1+0.03*d['vds'])
        expect(d['von'], vth, f'{name} body-effect threshold', rtol=1e-6)
        expect(d['id'], current, f'{name} independent DC square law', rtol=1e-6)
    cin = np.array([a['cgs'], a['cgd'], 0.])
    capacitance = np.diag([a['cgs'], a['cgd']+b['cgs'], 1e-12+b['cgd']])
    s = 2j*np.pi*f
    gf = g[None, :, :]+s[:, None, None]*capacitance[None, :, :]
    bvin = np.array([a['gm'], -a['gm'], 0.])
    bvb = np.array([0., b['gm'], -b['gm']])
    bdd = np.array([0., 0., 1/rl])
    bss = np.array([1/50.+a['gmbs'], b['gmbs']-a['gmbs'], -b['gmbs']])
    transfers = {'ac-input': bvin[None, :]+s[:, None]*cin[None, :],
                 'ac-bias': bvb[None, :]+s[:, None]*np.array([0., b['cgs'], b['cgd']])[None, :],
                 'ac-output': np.tile([0., 0., 1.], (len(f), 1)),
                 'ac-psrr-positive': np.tile(bdd, (len(f), 1)),
                 'ac-psrr-negative': np.tile(bss, (len(f), 1))}
    mna_error = {}
    for deck, rhs in transfers.items():
        observed = data[deck]
        expect(observed[:, 0], f, 'identical AC grids')
        solution = np.linalg.solve(gf, rhs[..., None])[..., 0]
        for column, node in ((1, 2), (3, 0), (5, 1)):
            complex_observed = observed[:, column]+1j*observed[:, column+1]
            expect(complex_observed, solution[:, node], f'{deck} full-frequency MNA node {node}', rtol=3e-4, atol=1e-15)
        mna_error[deck] = float(np.max(abs(cgain(observed)/solution[:, 2]-1)))
    expect([gain[0].real, data['ac-input'][0, 3], data['ac-input'][0, 5], data['ac-bias'][0, 1], data['ac-output'][0, 1]],
           [theory['gain'], theory['E_gain'], theory['X_gain'], theory['bias_gain'], theory['rout_ohm']], 'closed-form scalar equations')
    input_current = data['ac-input'][:, 7]+1j*data['ac-input'][:, 8]
    ein, xin = transfers['ac-input'], np.linalg.solve(gf, transfers['ac-input'][..., None])[..., 0]
    predicted_current = s*(a['cgs']*(1-xin[:, 0])+a['cgd']*(1-xin[:, 1])+a['cgb'])
    expect(-input_current, predicted_current, 'source current vs capacitor input admittance', rtol=3e-4, atol=1e-18)
    input_c_lf = float((-input_current[0]/s[0]).real)
    bandwidth = falling_cross(f, 20*np.log10(abs(gain)), 20*np.log10(abs(gain[0]))-3)
    unity = falling_cross(f, 20*np.log10(abs(gain)), 0) if abs(gain[0]) > 1 else None
    dc = data['dc-transfer']
    center = np.argmin(abs(dc[:, 0]-.75))
    slope = (dc[center+1, 1]-dc[center-1, 1])/(dc[center+1, 0]-dc[center-1, 0])
    expect(slope, theory['gain'], 'central DC slope vs AC', rtol=1e-3)
    roots = roots_from_log(logs[f'{case}-poles-zeros'])
    eigen_poles = np.linalg.eigvals(-np.linalg.solve(capacitance, g))
    expect(sorted(p.real for p in roots['pole']), sorted(eigen_poles), 'independent C/G eigenvalue poles', rtol=1e-5)
    if any(p.real >= 0 for p in roots['pole']):
        raise ValueError('Unstable educational open-loop poles')
    # Cramer's rule for output. Ce=Cgs1; Cx=Cgd1+Cgs2; Co=CL+Cgd2.
    ce, cgd, ge = a['cgs'], a['cgd'], 1/50.
    numerator = [ce*cgd, (ge+theory['k1_S'])*cgd+(theory['k1_S']-a['gm'])*ce, -a['gm']*ge]
    independent_zeros = np.roots(numerator)
    expect(sorted(z.real for z in roots['zero']), sorted(independent_zeros), 'independent numerator zeros', rtol=1e-5)
    reconstruction = np.full(len(f), theory['gain'], dtype=complex)
    for z in roots['zero']:
        reconstruction *= 1-s/z
    for p in roots['pole']:
        reconstruction /= 1-s/p
    expect(reconstruction, gain, 'full PZ reconstruction vs AC', rtol=3e-4, atol=1e-15)
    # Current injections for M1, M2, RE, RL in E/X/OUT ordering.
    injections = np.array([[1., -1., 0.], [0., 1., -1.], [1., 0., 0.], [0., 0., 1.]])
    h = np.linalg.solve(gf, np.broadcast_to(injections.T, (len(f), 3, 4)))[:, 2, :]
    thermal_current_psd = KBT4*np.array([2/3*a['gm'], 2/3*b['gm'], 1/50., 1/rl])
    predicted_noise_psd = abs(h)**2*thermal_current_psd[None, :]
    noise, flicker = data['noise'], data['noise-flicker']
    expect(noise[:, 0], f, 'noise/AC grids')
    expect(noise[:, 3:7]**2, predicted_noise_psd, 'full-frequency per-source thermal noise MNA', rtol=3e-4)
    expect((noise[:, 3:7]**2).sum(axis=1), noise[:, 1]**2, 'thermal source power sum')
    expect(noise[:, 1]/abs(gain), noise[:, 2], 'input-referred thermal noise')
    noise_scalar = KBT4*((2/3)/a['gm']+50*(theory['k1_S']/a['gm'])**2+
                         (2/3)*b['gm']*(a['gds']/(a['gm']*theory['k2_S']))**2+
                         1/(theory['gm_short_S']**2*rl))
    expect(noise[0, 2]**2, noise_scalar, 'closed-form total LF noise', rtol=3e-4)
    cox = 3.9*8.854214871e-12/model[0]
    kf_match = re.search(r'altermod NMOS_EDU kf=([\d.eE+-]+)', (LAB/f'{case}-noise-flicker.cir').read_text())
    kf = float(kf_match[1])
    af = float(re.search(r'altermod NMOS_EDU af=([\d.eE+-]+)', (LAB/f'{case}-noise-flicker.cir').read_text())[1])
    expect(af, 1., 'AF=1 analytic integral assumption')
    flicker_current_b = np.array([kf*d['id']**af/(model[2+2*i]*(model[3+2*i]-2*model[1])*cox**2) for i, d in enumerate((a,b))])
    predicted_flicker_psd = abs(h[:, :2])**2*flicker_current_b[None, :]/f[:, None]
    expect(flicker[:, 7:9]**2, predicted_flicker_psd, 'full-frequency per-source MOS1 flicker noise', rtol=3e-4)
    expect(flicker[:, 9:11]**2, noise[:, 3:5]**2, 'thermal baseline unchanged by KF')
    expect(flicker[:, 3:5]**2, flicker[:, 7:9]**2+flicker[:, 9:11]**2, 'MOS flicker/thermal powers add')
    expect(flicker[:, 5:7], noise[:, 5:7], 'resistor noise unchanged')
    expect((flicker[:, 3:7]**2).sum(axis=1), flicker[:, 1]**2, 'total source powers add')
    expect(flicker[:, 1]/abs(gain), flicker[:, 2], 'flicker total input referral')
    expect(finite_load(work/f'{case}-flicker-op.dat')[0, 1:], op, 'KF preserves DC bias', rtol=1e-8)
    input_flicker = (flicker[:, 7:9]**2).sum(axis=1)/abs(gain)**2
    b_input = float(input_flicker[0]*f[0])
    corner = falling_cross(f, 10*np.log10(input_flicker/noise[:, 2]**2), 0.)
    integrals = []
    for low, high in ((1.,1000.), (10.,1000.), (1.,100000.), (10.,100000.)):
        whitevar = integrate(f, noise[:, 2]**2, low, high)
        flickervar = integrate(f, input_flicker, low, high)
        totalvar = integrate(f, flicker[:, 2]**2, low, high)
        predictedvar = noise_scalar*(high-low)+b_input*np.log(high/low)
        expect(totalvar, whitevar+flickervar, 'integrated variances add')
        expect(totalvar, predictedvar, 'LF white+B/f integral', rtol=3e-4)
        integrals.append({'band_Hz':[low,high], 'thermal_input_rms_V': float(np.sqrt(whitevar)),
                          'flicker_input_rms_V':float(np.sqrt(flickervar)), 'total_input_rms_V':float(np.sqrt(totalvar)),
                          'thermal_output_rms_V':float(np.sqrt(integrate(f, noise[:,1]**2,low,high))),
                          'lf_formula_total_input_rms_V':float(np.sqrt(predictedvar))})
    tran = data['transient']
    tau_rc = theory['rout_ohm']*(1e-12+b['cgd'])
    tau_pz = -1/max(p.real for p in roots['pole'])
    delay, rise = 10*rl*1e-12, rl*1e-12/50
    plateau = (tran[:,0] > delay+15*rl*1e-12) & (tran[:,0] < delay+19*rl*1e-12)
    final = float(tran[plateau,1].mean())
    movement = final-op[0]
    expect(movement/1e-4, theory['gain'], 'small input step gain', rtol=1e-3)
    error = abs((tran[:,1]-final)/movement)
    settling = {}
    for eps in (.01, .001):
        measured = last_exit(tran[:,0], error, delay+rise, delay+rise+20*rl*1e-12, eps)
        predicted = tau_pz*np.log(1/eps)
        expect(measured, predicted, f'{eps:g} open-loop settling vs slow pole', rtol=.02)
        settling[str(eps)] = {'measured_s': measured, 'dominant_pole_s':float(predicted)}
    bias = data['bias-sweep']
    sat = (bias[:,5]>0)&(bias[:,6]>0)&(bias[:,7]>0)&(bias[:,8]>0)
    avb = cgain(data['ac-bias'])[0].real
    j = np.argmin(abs(bias[:,0]-1.25))
    bias_slope = (bias[j+1,1]-bias[j-1,1])/(bias[j+1,0]-bias[j-1,0])
    expect(bias_slope, avb, 'bias DC slope vs AC', rtol=1e-3)
    asplus, asminus = (cgain(data[k])[0].real for k in ('ac-psrr-positive','ac-psrr-negative'))
    predicted_plus, predicted_minus = (np.linalg.solve(g,r)[2] for r in (bdd,bss))
    expect([asplus,asminus],[predicted_plus,predicted_minus], 'supply LF KCL')
    thermal_fractions = noise[0,3:7]**2/noise[0,1]**2
    metric = {'conditions': {'VDD_V':1.8,'VSS_V':0.,'VIN_V':.75,'VB_V':1.25,'CL_F':1e-12,'RL_ohm':rl,'RE_ohm':50.,'temperature_C':27.},
              'operating_point': dict(zip(('OUT_V','E_V','X_V','I_VDD_A'),map(float,op))),
              'current_A':a['id'], 'power_W': float(1.8*abs(op[3])), 'devices':devices,
              'saturation_margin_V':margin, 'analytic':theory,
              'gain_V_per_V':float(gain[0].real),'gain_dB':float(20*np.log10(abs(gain[0]))),
              'input_capacitance_F':input_c_lf,'bandwidth_3dB_Hz':bandwidth,'unity_crossing_Hz':unity,
              'scalar_output_pole_Hz':float(1/(2*np.pi*tau_rc)),
              'internal_X_pole_estimate_Hz':float((a['gds']+theory['k2_S'])/(2*np.pi*(a['cgd']+b['cgs']))),
              'input_source_E_pole_estimate_Hz':float((1/50+theory['k1_S'])/(2*np.pi*a['cgs'])),
              'bias_gain_V_per_V':float(avb),'bias_center_dc_slope':float(bias_slope),'input_center_dc_slope':float(slope),
              'bias_sweep_sampled_saturation_VB_V':[float(bias[sat,0].min()),float(bias[sat,0].max())],
              'supply_transfer_V_per_V':{'positive':float(asplus),'negative':float(asminus)},
              'PSRR_dB':{'positive':float(20*np.log10(abs(gain[0]/asplus))),'negative':float(20*np.log10(abs(gain[0]/asminus)))},
              'MNA_max_relative_error':mna_error,'PZ_max_relative_error':float(np.max(abs(reconstruction/gain-1))),
              'poles_rad_s':[[p.real,p.imag] for p in roots['pole']], 'zeros_rad_s':[[z.real,z.imag] for z in roots['zero']],
              'noise':{'thermal_input_V_sqrtHz':float(noise[0,2]),'thermal_output_V_sqrtHz':float(noise[0,1]),
                       'thermal_source_fraction':dict(zip(('M1','M2','RE','RL'),map(float,thermal_fractions))),
                       'thermal_formula_PSD_V2_per_Hz':float(noise_scalar), 'KF':kf,'AF':af,'Cox_F_per_m2':float(cox),
                       'total_input_1Hz_V_sqrtHz':float(flicker[0,2]),'flicker_B_V2':b_input,
                       'corner_Hz':corner,'corner_LF_Hz':float(b_input/noise_scalar),'integrated_bands':integrals},
              'transient':{'step_V':1e-4,'delay_s':delay,'rise_s':rise,'final_movement_V':float(movement),
                           'dominant_tau_s':float(tau_pz),'settling':settling},
              'checks':['nominal conducting saturation; series and resistor DC KCL',
                        'independent square-law DC currents and body thresholds',
                        'closed-form signal/bias gains, node movements and loaded output resistance; unloaded-matrix intrinsic resistance',
                        'full-frequency E/X/OUT MNA for signal, bias, impedance and both supplies',
                        'input admittance from capacitor currents; DC derivatives vs AC',
                        'C/G eigenvalue poles, independent numerator zeros and full complex PZ reconstruction',
                        'full-frequency per-source thermal and flicker MNA; power sums and input referral',
                        'KF preserves OP and resistor/channel thermal baseline; finite-band noise integrals',
                        'small-step gain and last-exit 1%/0.1% open-loop settling']}
    return metric, data, reconstruction


def savefig(name, figure):
    FIG.mkdir(parents=True, exist_ok=True)
    for ax in figure.axes:
        ax.grid(True, alpha=.22)
    figure.savefig(FIG/f'{name}.png', dpi=165)
    figure.savefig(FIG/f'{name}.svg')
    plt.close(figure)


def plot(all_data, metrics, reconstructed, sweeps):
    colors = {'baseline':'#2574b7','load-10k':'#bd5329'}
    labels = {'baseline':'Original RL = 50 ohm','load-10k':'Experiment RL = 10 kohm'}
    fig, ax = plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for case,d in all_data.items():
        c,l=colors[case],labels[case]
        dc,bias=d['dc-transfer'],d['bias-sweep']
        ax[0,0].plot(dc[:,0],dc[:,1],color=c,label=l)
        ax[0,1].plot(bias[:,0],bias[:,1],color=c,label=l)
        ax[1,0].plot(bias[:,0],bias[:,5],color=c,label=l+' M1')
        ax[1,0].plot(bias[:,0],bias[:,6],color=c,linestyle='--',label=l+' M2')
        ax[1,1].plot(dc[:,0],-dc[:,4]*1e6,color=c,label=l)
    ax[0,0].set(xlabel='Input DC (V)',ylabel='OUT (V)',title='DC transfer; VB = 1.25 V')
    ax[0,1].set(xlabel='Bias VB (V)',ylabel='OUT (V)',title='Cascode bias sensitivity; VIN = 0.75 V')
    ax[1,0].axhline(0,color='black',lw=.7)
    ax[1,0].set(xlabel='Bias VB (V)',ylabel='VDS - VDSsat (V)',title='Positive margin: saturation')
    ax[1,1].set(xlabel='Input DC (V)',ylabel='Supply current (uA)',title='Increasing input changes current and headroom')
    for a in ax.flat:a.legend(fontsize=8)
    savefig('bias-and-dc',fig)
    fig,ax=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for case,d in all_data.items():
        c,l=colors[case],labels[case]
        f=d['ac-input'][:,0]; h=cgain(d['ac-input']); m=metrics[case]
        ax[0,0].semilogx(f,20*np.log10(abs(h)),color=c,label=l)
        ax[0,0].semilogx(f,20*np.log10(abs(reconstructed[case])),color=c,ls='--',alpha=.65)
        ax[0,1].semilogx(f,np.unwrap(np.angle(-h))*180/np.pi,color=c,label=l)
        ax[1,0].semilogx(f,abs(cgain(d['ac-output'])),color=c,label=l)
        ax[1,1].semilogx(f,20*np.log10(abs(d['ac-input'][:,3]+1j*d['ac-input'][:,4])),color=c,label=l+' E')
        ax[1,1].semilogx(f,20*np.log10(abs(d['ac-input'][:,5]+1j*d['ac-input'][:,6])),color=c,ls='--',label=l+' X')
    for a in ax.flat:a.set(xlabel='Frequency (Hz)');a.legend(fontsize=8)
    ax[0,0].set(ylabel='Gain magnitude (dB)',title='AC and full PZ reconstruction (dashed)')
    ax[0,1].set(ylabel='Phase of -Av (deg)',title='Phase referenced to LF inversion')
    ax[1,0].set(yscale='log',ylabel='Output impedance (ohm)',title='RL limits the loaded output resistance')
    ax[1,1].set(ylabel='Internal voltage gain (dB)',title='X has little Miller multiplication')
    savefig('ac-and-impedance',fig)
    fig,ax=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    for case,d in all_data.items():
        f=d['ac-input'][:,0]; source_i=d['ac-input'][:,7]+1j*d['ac-input'][:,8]
        y=-source_i; c,l=colors[case],labels[case]
        ax[0].loglog(f,1/abs(y),color=c,label=l)
        ax[0].loglog(f,1/(2*np.pi*f*metrics[case]['input_capacitance_F']),color=c,ls='--',alpha=.65)
        ax[1].semilogx(f,np.angle(1/y)*180/np.pi,color=c,label=l)
    ax[0].set(xlabel='Frequency (Hz)',ylabel='Input impedance magnitude (ohm)',title='Actual input current; LF capacitance dashed')
    ax[1].set(xlabel='Frequency (Hz)',ylabel='Input impedance phase (deg)',title='Ideal source; gate leakage omitted')
    for a in ax:a.legend(fontsize=8)
    savefig('input-impedance',fig)
    fig,ax=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    for case,d in all_data.items():
        c,l=colors[case],labels[case];f=d['ac-input'][:,0];h=cgain(d['ac-input'])
        for name,ls in [('ac-psrr-positive','-'),('ac-psrr-negative','--'),('ac-bias',':')]:
            transfer=cgain(d[name]);suffix={'ac-psrr-positive':'+','ac-psrr-negative':'-','ac-bias':'VB'}[name]
            ax[0].semilogx(f,20*np.log10(abs(transfer)),color=c,ls=ls,label=l+' '+suffix)
            ax[1].semilogx(f,20*np.log10(abs(h/transfer)),color=c,ls=ls,label=l+' '+suffix)
    ax[0].set(xlabel='Frequency (Hz)',ylabel='Transfer magnitude (dB)',title='Supply and cascode-bias coupling')
    ax[1].set(xlabel='Frequency (Hz)',ylabel='Input-referred rejection (dB)',title='PSRR +/-; bias rejection shown as VB')
    for a in ax:a.legend(fontsize=7)
    savefig('psrr-and-bias',fig)
    fig,ax=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for case,d in all_data.items():
        c,l=colors[case],labels[case];f=d['noise'][:,0];h=cgain(d['ac-input'])
        n,nf=d['noise'],d['noise-flicker']
        ax[0,0].loglog(f,n[:,2]*1e9,color=c,label=l+' thermal')
        ax[0,0].loglog(f,nf[:,2]*1e9,color=c,ls='--',label=l+' thermal + 1/f')
        ax[0,1].loglog(f,n[:,1]*1e9,color=c,label=l)
        for i,name in enumerate(('M1','M2','RE','RL')):
            ax[1,0].loglog(f,n[:,3+i]/abs(h)*1e9,ls='-' if case=='baseline' else '--',label=l+' '+name)
        lows=np.geomspace(1,1e4,75)
        ax[1,1].semilogx(lows,[np.sqrt(integrate(f,n[:,2]**2,x,1e5))*1e6 for x in lows],color=c,label=l+' thermal')
        ax[1,1].semilogx(lows,[np.sqrt(integrate(f,nf[:,2]**2,x,1e5))*1e6 for x in lows],color=c,ls='--',label=l+' +1/f')
    ax[0,0].set(xlabel='Frequency (Hz)',ylabel='Input noise (nV/sqrt(Hz))',title='MOS1 illustrative KF = 2e-33; AF = 1')
    ax[0,1].set(xlabel='Frequency (Hz)',ylabel='Output noise (nV/sqrt(Hz))',title='Thermal output density')
    ax[1,0].set(xlabel='Frequency (Hz)',ylabel='Input source noise (nV/sqrt(Hz))',title='Each source referred through the actual Av')
    ax[1,1].set(xlabel='Lower integration cutoff (Hz)',ylabel='Input RMS (uV)',title='Fixed upper cutoff 100 kHz')
    for a in ax.flat:a.legend(fontsize=6)
    savefig('noise',fig)
    fig,ax=plt.subplots(2,2,figsize=(11,7),constrained_layout=True)
    for col,(case,d) in enumerate(all_data.items()):
        t=d['transient'][:,0];m=metrics[case]['transient'];out=d['transient'][:,1]
        start=m['delay_s']+m['rise_s']; scale=1e9
        final=metrics[case]['operating_point']['OUT_V']+m['final_movement_V']
        ax[0,col].plot((t-start)*scale,(out-metrics[case]['operating_point']['OUT_V'])*1e6,label='ngspice')
        tt=np.linspace(0,20*m['dominant_tau_s'],700)
        ax[0,col].plot(tt*scale,m['final_movement_V']*1e6*(1-np.exp(-tt/m['dominant_tau_s'])),ls='--',label='Dominant pole')
        valid=(t>=start)&(t<start+19*CASES[case]*1e-12)
        err=abs((out[valid]-final)/m['final_movement_V'])
        ax[1,col].semilogy((t[valid]-start)*scale,np.maximum(err,1e-9),label='ngspice last-exit error')
        ax[1,col].semilogy(tt*scale,np.exp(-tt/m['dominant_tau_s']),ls='--',label='Dominant pole')
        for eps in (.01,.001):ax[1,col].axhline(eps,color='grey',lw=.7)
        ax[0,col].set(title=labels[case]+'; 100 uV step',ylabel='Output movement (uV)')
        ax[1,col].set(ylabel='Relative error',ylim=(1e-6,2))
        for a in ax[:,col]:a.set(xlabel='Time after rising edge ends (ns)');a.legend(fontsize=8)
    savefig('settling',fig)
    fig,ax=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    for case,m in metrics.items():
        for kind,marker in [('poles_rad_s','x'),('zeros_rad_s','o')]:
            arr=np.array(m[kind]); hz=arr[:,0]/(2*np.pi)
            ax[0].scatter(hz,np.zeros(len(hz))+(0 if case=='baseline' else 1),marker=marker,label=labels[case]+' '+kind.split('_')[0])
    ax[0].set_xscale('symlog',linthresh=1e6)
    ax[0].set_xticks([-1e13,-1e10,-1e7,0,1e9,1e12],
                    labels=['-10 THz','-10 GHz','-10 MHz','0','+1 GHz','+1 THz'])
    ax[0].set(xlabel='Signed Re(root) / (2 pi) (Hz)',yticks=[0,1],yticklabels=['RL 50 ohm','RL 10 kohm'],title='Three LHP poles; one LHP and one RHP zero')
    load=sweeps['load-sweep'];sat=np.array([x['conducting_saturation'] for x in load])
    values=np.array([x['resistance_ohm'] for x in load]);gain=np.array([abs(x['gain_V_per_V']) for x in load]);out=np.array([x['OUT_V'] for x in load])
    ax[1].semilogx(values,gain,'o-',label='Measured |Av|')
    ax[1].scatter(values[~sat],gain[~sat],color='red',marker='x',s=65,label='A device outside saturation')
    ax[1].set(xlabel='RL (ohm)',ylabel='Gain magnitude (V/V)',title='Increasing RL eventually consumes headroom')
    for a in ax:a.legend(fontsize=7)
    savefig('poles-and-load',fig)
    fig,ax=plt.subplots(1,2,figsize=(11,4),constrained_layout=True)
    rows=sweeps['degeneration-sweep'];res=np.array([r['resistance_ohm'] for r in rows])
    ax[0].semilogx(res,[abs(r['gain_V_per_V']) for r in rows],'o-',label='ngspice AC')
    ax[0].semilogx(res,[abs(r['closed_form_gain']) for r in rows],'--',label='KCL closed form')
    ax[0].set(xlabel='RE (ohm)',ylabel='Gain magnitude (V/V)',title='RL = 10 kohm; bias recomputed at every RE')
    ax[1].semilogx(res,[r['current_A']*1e6 for r in rows],'o-',label='Series current')
    ax[1].set(xlabel='RE (ohm)',ylabel='Current (uA)',title='Degeneration also changes DC current and gm')
    for a in ax:a.legend(fontsize=8)
    savefig('degeneration',fig)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ngspice', default=os.environ.get('NGSPICE_BIN','ngspice'))
    parser.add_argument('--generate-decks',action='store_true')
    args=parser.parse_args()
    if args.generate_decks:generate_decks()
    exe=shutil.which(args.ngspice) or str(Path(args.ngspice).resolve())
    if not Path(exe).is_file():raise FileNotFoundError(exe)
    names=[f'{case}-{deck}' for case in CASES for deck in DECKS]+list(SWEEPS)
    with tempfile.TemporaryDirectory(prefix='classroom-cascode-') as temp:
        work=Path(temp)
        sources=[LAB/f'{name}.cir' for name in names]+[LAB/'cascode-core.cir',LAB/'models.lib']
        for p in sources:shutil.copy2(p,work/p.name)
        logs={}
        for name in names:
            kwargs={}
            if os.name=='nt':
                info=subprocess.STARTUPINFO();info.dwFlags=subprocess.STARTF_USESHOWWINDOW;info.wShowWindow=0
                kwargs={'startupinfo':info,'creationflags':subprocess.CREATE_NO_WINDOW}
            result=subprocess.run([exe,'-b','-o',f'{name}.log',f'{name}.cir'],cwd=work,capture_output=True,text=True,timeout=60,**kwargs)
            log=(work/f'{name}.log').read_text(errors='replace')
            if result.returncode or re.search(r'(?im)^\s*(error\b|fatal\b|doAnalyses:)|simulation\(s\) aborted|no such vector',log):
                raise RuntimeError(f'{name}: exit={result.returncode}\n{log}')
            logs[name]=log
        metrics,data,reconstructed={},{},{}
        for case,rl in CASES.items():
            metrics[case],data[case],reconstructed[case]=check_case(case,rl,work,logs)
        sweeps={}
        for deck,(resistor,values) in SWEEPS.items():
            rows=[]
            for i,value in enumerate(values):
                op=finite_load(work/f'{deck}-{i}-op.dat')[0,1:]
                devices=devices_from_row(finite_load(work/f'{deck}-{i}-devices.dat')[0])
                observed=finite_load(work/f'{deck}-{i}-ac.dat')[0,1]
                rl,re_= (value,50.) if resistor=='rl' else (10000.,value)
                theory=analytic(devices,rl,re_)
                expect(observed,theory['gain'],f'{deck} {value:g} closed-form vs AC',rtol=2e-5)
                margins=[d['vds']-d['vdsat'] for d in devices.values()]
                rows.append({'resistance_ohm':value,'OUT_V':float(op[0]),'E_V':float(op[1]),'X_V':float(op[2]),
                             'current_A':devices['M1']['id'],'gain_V_per_V':float(observed),
                             'closed_form_gain':theory['gain'],'saturation_margins_V':margins,
                             'conducting_saturation': bool(min(margins)>0 and min(d['gm'] for d in devices.values())>0)})
            sweeps[deck]=rows
        # Publish execution evidence only once the entire independent check set passes.
        results=LAB/'results';results.mkdir(parents=True,exist_ok=True)
        for path in work.iterdir():
            if path.suffix in ('.dat','.log'):shutil.copy2(path,results/path.name)
        headers={'ac':'frequency_Hz,OUT_real,OUT_imag,E_real,E_imag,X_real,X_imag,VIN_current_real_A,VIN_current_imag_A',
                 'noise':'frequency_Hz,output_V_sqrtHz,input_V_sqrtHz,M1_V_sqrtHz,M2_V_sqrtHz,RE_V_sqrtHz,RL_V_sqrtHz',
                 'noise-flicker':'frequency_Hz,output_V_sqrtHz,input_V_sqrtHz,M1_total,M2_total,RE_thermal,RL_thermal,M1_flicker,M2_flicker,M1_channel,M2_channel',
                 'dc-transfer':'VIN_V,OUT_V,E_V,X_V,I_VDD_A,M1_margin_V,M2_margin_V,M1_gm_S,M2_gm_S',
                 'bias-sweep':'VB_V,OUT_V,E_V,X_V,I_VDD_A,M1_margin_V,M2_margin_V,M1_gm_S,M2_gm_S',
                 'transient':'time_s,OUT_V,VIN_V,E_V,X_V'}
        for case,acquired in data.items():
            for deck,array in acquired.items():
                header=headers['ac' if deck.startswith('ac-') else deck]
                if deck=='ac-output':header=header.replace('OUT_real,OUT_imag','Zout_real_ohm,Zout_imag_ohm')
                np.savetxt(results/f'{case}-{deck}.csv',array,delimiter=',',header=header,comments='',fmt='%.15g')
            rows=[]
            for kind,key in [('pole','poles_rad_s'),('zero','zeros_rad_s')]:
                for real,imag in metrics[case][key]:rows.append(f'{kind},{real:.15g},{imag:.15g},{real/(2*np.pi):.15g}')
            (results/f'{case}-poles-zeros.csv').write_text('kind,real_rad_s,imag_rad_s,signed_real_Hz\n'+'\n'.join(rows)+'\n',encoding='utf-8')
        for deck,rows in sweeps.items():
            np.savetxt(results/f'{deck}.csv',[[r['resistance_ohm'],r['OUT_V'],r['E_V'],r['X_V'],r['current_A'],r['gain_V_per_V'],*r['saturation_margins_V'],int(r['conducting_saturation'])] for r in rows],
                       delimiter=',',header='resistance_ohm,OUT_V,E_V,X_V,current_A,gain_V_per_V,M1_margin_V,M2_margin_V,conducting_saturation',comments='',fmt='%.15g')
        plot(data,metrics,reconstructed,sweeps)
        source_files=[*sources,ROOT/'code/run_cascode.py',ROOT/'code/export_cascode.py',ROOT/'circuits/source-degenerated-cascode/Source-degenerated cascode amplifier.icproj.json',ROOT/'circuits/source-degenerated-cascode/educational.icproj.json']
        summary={'run_at':datetime.now(timezone(timedelta(hours=8))).isoformat(),
                 'environment':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
                 'simulator':{'path':exe,'sha256':sha(Path(exe)),'detected_version':'ngspice-33' if all('ngspice-33 done' in l for l in logs.values()) else 'see logs'},
                 'model_scope':'Educational MOS1 coefficients; no SKY130 PDK simulated; CL=1p; junction C defaults to zero; 150nm dimensions do not establish short-channel accuracy',
                 'executed_testbenches':names,'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in source_files},
                 'cases':metrics,'sweeps':sweeps,'all_checks_passed':True,
                 'approximation_policy':'Full MNA and exact scalar formulas are asserted; simple pole/gmRL estimates are comparisons, not forced equalities'}
        (results/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'testbenches':len(names),'all_checks_passed':True,'cases':{c:{k:m[k] for k in ('gain_V_per_V','gain_dB','current_A','bandwidth_3dB_Hz','unity_crossing_Hz')} for c,m in metrics.items()}},indent=2))


if __name__=='__main__':main()
