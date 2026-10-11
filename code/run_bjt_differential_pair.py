"""Run actual ngspice testbenches and compare independent hybrid-pi equations.

Usage: python code/run_bjt_differential_pair.py --ngspice /path/to/ngspice
Paths are resolved from this script. Results publish only after checks pass.
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

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from bjt_differential_pair_source import extract, schematic, SOURCE

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT/'simulations/bjt-degenerated-differential-pair'
FIG = ROOT/'figures/bjt-degenerated-differential-pair'
NODES = ['voutn','voutp','e1','e2','x','e3','vinp','vinn','vb','vdd','vss']
PINS = [(0,6,2),(1,7,3),(4,8,5)]
RESISTORS = [('RD1',9,0,1000),('RD2',9,1,1000),('R3',2,4,50),
             ('R2',3,4,50),('R1',5,10,50)]
PARAMS = ['ic','ib','gm','gpi','gmu','go','cpi','cmu','cexbc','vbe','vbc']
K = 1.380649e-23
Q = 1.602176634e-19
T = 300.15


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(executable, args, cwd):
    opts = {}
    if os.name == 'nt':
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        opts = dict(startupinfo=si, creationflags=subprocess.CREATE_NO_WINDOW)
    p = subprocess.run([executable,*args],cwd=cwd,capture_output=True,text=True,timeout=60,**opts)
    if p.returncode:
        raise RuntimeError(f'ngspice exit {p.returncode}: {p.stdout}\n{p.stderr}')
    return p


def deck(name, analysis, excitation='dm', mismatch=False, flicker=False):
    ac = {x: int(excitation == x) for x in ('dm','cm','vdd','vss','vb')}
    model = '.include models.lib'
    if flicker:
        model = (LAB/'models.lib').read_text().replace('KF=0 ', 'KF=1e-14 ')
    core = (LAB/'core.cir').read_text()
    if mismatch:
        core = core.replace('RD2 vdd voutp 1k','RD2 vdd voutp 1.01k')
    stimulus = 'DC 0'
    if name == 'transient':
        stimulus = 'PULSE(0 100u 20n 50p 50p 250n 600n)'
    return f'''BJT differential-pair teaching study: {name}
{model}
{core}
.temp 27
.options reltol=1e-7 abstol=1e-14 vntol=1e-10
VDD vdd 0 DC 3.3 AC {ac['vdd']}
VSS vss 0 DC 0 AC {ac['vss']}
VB vb 0 DC 0.85 AC {ac['vb']}
VCM vcm 0 DC 1.8 AC {ac['cm']}
VDM dm 0 {stimulus} AC {ac['dm']}
EINP vinp vcm dm 0 0.5
EINN vinn vcm dm 0 -0.5
{('ITEST 0 voutp AC 1' if name == 'output-resistance' else '')}
.control
set noaskquit
set wr_vecnames
set wr_singlescale
{analysis}
quit
.endc
.end
'''


def ac_analysis(name):
    return f'''ac dec 100 1 10G
let vd = v(voutp)-v(voutn)
let vo = (v(voutp)+v(voutn))/2
let ibp = -i(einp)
let ibn = -i(einn)
wrdata {name}.dat vd v(voutp) vo v(x) v(e1) v(e3) ibp ibn'''


def make_decks():
    op_vec = ' '.join([f'v({n})' for n in NODES[:6]] +
                      [f'@q{i}[{p}]' for i in range(1,4) for p in PARAMS])
    op = f'op\nwrdata op.dat {op_vec}'
    decks = {'op': deck('op',op)}
    for excitation in ('dm','cm','vdd','vss','vb'):
        decks['ac-'+excitation] = deck('ac-'+excitation,ac_analysis('ac-'+excitation),excitation)
    name='ac-vss-tracking-bias'
    decks[name]=deck(name,ac_analysis(name),'vss').replace('VB vb 0 DC 0.85','VB vb vss DC 0.85')
    for excitation in ('cm','vdd'):
        name = 'mismatch-'+excitation
        decks[name] = deck(name,ac_analysis(name),excitation,mismatch=True)
    name = 'output-resistance'
    decks[name] = deck(name,ac_analysis(name),'none')
    decks['dc-transfer'] = deck('dc-transfer', '''dc VDM -0.2 0.2 0.0005
let vd = v(voutp)-v(voutn)
wrdata dc-transfer.dat vd v(voutp) v(voutn) v(x) v(e1) v(e2)''')
    decks['dc-common-mode'] = deck('dc-common-mode', '''dc VCM 1.1 2.8 0.005
wrdata dc-common-mode.dat v(voutp) v(x) v(e1) v(e3) @q1[vbc] @q3[vbc]''')
    decks['transient'] = deck('transient', '''tran 0.05n 250n
let vd = v(voutp)-v(voutn)
wrdata transient.dat v(dm) vd v(voutp)''')
    for name, flicker in [('noise-white',False),('noise-flicker',True)]:
        decks[name] = deck(name,f'''noise v(voutp,voutn) VDM dec 100 1 10G
setplot noise1
wrdata {name}.dat onoise_spectrum inoise_spectrum''',flicker=flicker)
    return decks


def matrix(devices, s=0, mismatch=False):
    """Construct full nodal admittance, independently from a SPICE netlist."""
    y = np.zeros((11,11),complex)

    def passive(a,b,g):
        y[a,a] += g; y[b,b] += g
        y[a,b] -= g; y[b,a] -= g

    for (c,b,e),d in zip(PINS,devices):
        passive(c,e,d['go'])
        passive(b,e,d['gpi']+s*d['cpi'])
        passive(b,c,d['gmu']+s*d['cmu'])
        y[c,b] += d['gm']; y[c,e] -= d['gm']
        y[e,b] -= d['gm']; y[e,e] += d['gm']
        # Gummel-Poon forward charge also depends on BC voltage through Early effect.
        h=s*d['cexbc']
        y[b,b] += h; y[b,c] -= h
        y[e,b] -= h; y[e,c] += h
    for name,a,b,r in RESISTORS:
        passive(a,b,1/(r*1.01 if mismatch and name=='RD2' else r))
    passive(0,10,s*10e-12); passive(1,10,s*10e-12)
    return y


def solve(devices, frequency, excitation, mismatch=False):
    known = {'dm':[.5,-.5,0,0,0], 'cm':[1,1,0,0,0],
             'vdd':[0,0,0,1,0], 'vss':[0,0,0,0,1],
             'vb':[0,0,1,0,0], 'none':[0,0,0,0,0]}[excitation]
    result = []
    for f in frequency:
        y = matrix(devices,2j*np.pi*f,mismatch)
        rhs = -y[:6,6:]@known
        if excitation == 'none':
            rhs[1] += 1
        v = np.r_[np.linalg.solve(y[:6,:6],rhs),known]
        ib = (y@v)[6:8]
        result.append([v[1]-v[0],v[1],(v[1]+v[0])/2,v[4],v[2],v[5],*ib])
    return np.array(result)


def noise_prediction(devices, frequency, flicker=False):
    sources = []
    for i,((c,b,e),d) in enumerate(zip(PINS,devices),1):
        sources.extend([(f'Q{i} collector shot',c,e,2*Q*abs(d['ic']),False),
                        (f'Q{i} base shot',b,e,2*Q*abs(d['ib']),False)])
        if flicker:
            sources.append((f'Q{i} base flicker',b,e,1e-14*abs(d['ib']),True))
    sources.extend((name+' thermal',a,b,4*K*T/r,False) for name,a,b,r in RESISTORS)
    contribution = {name: [] for name,*_ in sources}
    for f in frequency:
        y = matrix(devices,2j*np.pi*f)
        gain = solve(devices,[f],'dm')[0,0]
        for name,a,b,power,is_flicker in sources:
            rhs = np.zeros(6)
            if a<6: rhs[a]-=1
            if b<6: rhs[b]+=1
            v = np.linalg.solve(y[:6,:6],rhs)
            h = v[1]-v[0]
            contribution[name].append(abs(h/gain)**2*power/(f if is_flicker else 1))
    return {name:np.array(values) for name,values in contribution.items()}


def load(path):
    d = np.loadtxt(path,skiprows=1,ndmin=2)
    if not np.isfinite(d).all(): raise ValueError(f'Nonfinite {path}')
    return d


def complex_data(d):
    return d[:,1::2]+1j*d[:,2::2]


def crossing(f, values, level):
    hits = np.flatnonzero((values[:-1]>=level)&(values[1:]<level))
    if not len(hits): return None
    i=hits[0]
    return float(10**np.interp(level,values[i:i+2][::-1],np.log10(f[i:i+2])[::-1]))


def checked_close(observed,predicted,rtol=3e-5,atol=1e-10):
    if not np.allclose(observed,predicted,rtol=rtol,atol=atol):
        relative = abs(observed-predicted)/np.maximum(abs(predicted),1e-20)
        index=np.unravel_index(np.argmax(abs(observed-predicted)),np.shape(relative))
        raise ValueError(f'Independent comparison failed: max relative error {np.max(relative)}; '
                         f'max absolute at {index}: observed {np.asarray(observed)[index]}, predicted {np.asarray(predicted)[index]}')


def savefig(fig, path):
    for ax in fig.axes:
        ax.grid(True,alpha=.22)
    for suffix in ('png','svg'):
        fig.savefig(path.with_suffix('.'+suffix),dpi=165)
    plt.close(fig)


def plot_frequency_metrics(f, observed, predicted, poles, zeros, bandwidth, directory):
    """Distinguish analytical s-plane roots from actual AC response data."""
    fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    root_axis,magnitude_axis,phase_axis,band_axis=axes.flat
    scale=2*np.pi*1e9
    root_axis.axvspan(-3.8,0,color='#edf5ef')
    root_axis.axvspan(0,2.8,color='#fcf0ee')
    root_axis.axhline(0,color='gray',lw=.8)
    root_axis.axvline(0,color='gray',lw=.8)
    root_axis.plot(poles.real/scale,poles.imag/scale,'x',color='#28759d',ms=10,mew=2,label='Poles: D(s) roots')
    root_axis.plot(zeros.real/scale,zeros.imag/scale,'o',color='#c56d32',ms=10,mew=2,fillstyle='none',label='Zeros: N(s) roots')
    named_roots=[('p1',max(poles),-.5),('p2',min(poles),.5),
                 ('LHP zero',min(zeros),-.5),('RHP zero',max(zeros),.5)]
    for name,value,label_y in named_roots:
        x=float(value.real/scale)
        label_x=float(np.clip(x,-3.15,2.05))
        root_axis.annotate(f'{name}\n{x:+.4f} GHz',xy=(x,0),xytext=(label_x,label_y),
                           ha='center',va='center',fontsize=9,
                           arrowprops=dict(arrowstyle='-',color='gray'))
    root_axis.set(xlabel='Re(s) / (2π), GHz',ylabel='Im(s) / (2π), GHz',
                  title='Analytical pole-zero map',xlim=(-3.8,2.8),ylim=(-1,1))
    root_axis.legend(loc='upper left',fontsize=8)
    observed_db=20*np.log10(abs(observed))
    predicted_db=20*np.log10(abs(predicted))
    magnitude_axis.semilogx(f,observed_db,label='ngspice AC')
    magnitude_axis.semilogx(f,predicted_db,'--',label='Derived rational transfer')
    phase_axis.semilogx(f,np.unwrap(np.angle(observed))*180/np.pi,label='ngspice AC')
    phase_axis.semilogx(f,np.unwrap(np.angle(predicted))*180/np.pi,'--',label='Derived rational transfer')
    root_marks=[('p1',abs(max(poles))/(2*np.pi),'#639768'),
                ('p2',abs(min(poles))/(2*np.pi),'#806eaf'),
                ('RHP zero',abs(max(zeros))/(2*np.pi),'#bd6259'),
                ('LHP zero',abs(min(zeros))/(2*np.pi),'#bd923c')]
    for label,frequency,color in root_marks:
        for axis in (magnitude_axis,phase_axis):
            axis.axvline(frequency,color=color,ls=':',lw=1.3,
                         label=f'{label}: {frequency/1e6:.2f} MHz')
    magnitude_axis.set(xlabel='Frequency (Hz)',ylabel='Differential gain (dB)',
                       title='Magnitude and root frequency scales',xlim=(1e6,1e10))
    phase_axis.set(xlabel='Frequency (Hz)',ylabel='Phase (deg)',
                   title='Phase distinguishes LHP and RHP zeros',xlim=(1e6,1e10))
    magnitude_axis.legend(fontsize=8,loc='lower left')
    phase_axis.legend(fontsize=8,loc='lower left')
    band_axis.plot(f/1e6,observed_db-observed_db[0],label='ngspice AC')
    band_axis.plot(f/1e6,predicted_db-predicted_db[0],'--',label='Derived rational transfer')
    band_axis.axhline(-3,color='gray',ls=':',label='−3 dB relative to DC gain')
    band_axis.axvline(bandwidth/1e6,color='#28759d',ls='-.',
                     label=f'Bandwidth: {bandwidth/1e6:.4f} MHz')
    band_axis.axvline(abs(max(poles))/(2*np.pi*1e6),color='#639768',ls=':',
                     label=f'Pole p1 scale: {abs(max(poles))/(2*np.pi*1e6):.4f} MHz')
    band_axis.plot(bandwidth/1e6,-3,'o',color='#28759d',ms=5)
    band_axis.set(xlabel='Frequency (MHz)',ylabel='Gain relative to DC (dB)',
                  title='Bandwidth crossing is distinct from a pole',xlim=(8,25),ylim=(-5.8,-.5))
    band_axis.legend(fontsize=8,loc='lower left')
    savefig(fig,directory/'poles-zeros-and-transfer')


def process(data, directory):
    op = data['op'][0,1:]
    devices = [dict(zip(PARAMS,op[6+i*len(PARAMS):6+(i+1)*len(PARAMS)])) for i in range(3)]
    checks = []
    for i,d in enumerate(devices,1):
        assert d['ic']>0 and d['gm']>0 and d['vbc']<0, (i,d)
    # Tail collector receives both input-pair emitter currents.
    checked_close(devices[2]['ic'],sum(d['ic']+d['ib'] for d in devices[:2]),atol=1e-13)
    checks.extend(['three conducting NPNs with reverse-biased BC junctions','emitter/tail current KCL'])
    analytic = {}
    for name in ['ac-'+x for x in ('dm','cm','vdd','vss','vb')]+['output-resistance']:
        f = data[name][:,0]
        assert len(f)==1001 and np.all(np.diff(f)>0)
        excitation = name[3:] if name.startswith('ac-') else 'none'
        analytic[name] = solve(devices,f,excitation)
        obs = complex_data(data[name])
        try:
            checked_close(obs,analytic[name],rtol=5e-5,atol=3e-10)
        except ValueError as error:
            raise ValueError(f'{name}: {error}; devices={devices}') from error
        checks.append(name+': full complex hybrid-pi sweep')
    name='ac-vss-tracking-bias'
    analytic[name]=solve(devices,data[name][:,0],'vss')+solve(devices,data[name][:,0],'vb')
    checked_close(complex_data(data[name]),analytic[name],rtol=5e-5,atol=3e-10)
    checks.append(name+': supply/bias reference superposition')
    # Mismatch changes the bias too: obtain its own OP in main.
    mop = data['op-mismatch'][0,1:]
    mdevices = [dict(zip(PARAMS,mop[6+i*len(PARAMS):6+(i+1)*len(PARAMS)])) for i in range(3)]
    for excitation in ('cm','vdd'):
        name = 'mismatch-'+excitation
        analytic[name] = solve(mdevices,data[name][:,0],excitation,True)
        checked_close(complex_data(data[name]),analytic[name],rtol=5e-5,atol=3e-10)
        checks.append(name+': independent KCL at its own bias')
    dm = complex_data(data['ac-dm']); cm = complex_data(data['ac-cm'])
    f = data['ac-dm'][:,0]
    dc = data['dc-transfer']
    center = np.argmin(abs(dc[:,0]))
    slope = (dc[center+1,1]-dc[center-1,1])/(dc[center+1,0]-dc[center-1,0])
    checked_close(slope,dm[0,0].real,rtol=2e-4)
    checks.append('DC differential center slope versus AC')
    zin = 1/((dm[0,6]-dm[0,7])/2)
    gd = devices[0]['gm']/(1+(devices[0]['gm']+devices[0]['gpi'])*50)
    adm_approx = gd*1000
    tail = devices[2]
    rt = (1+50*(tail['gm']+tail['gpi']+tail['go']))/(tail['go']*(1+50*tail['gpi']))
    acm_approx = -devices[0]['gm']*1000/(1+(devices[0]['gm']+devices[0]['gpi'])*(50+2*rt))
    def common_or_diff(ge):
        d=devices[0]
        gd=1/1000
        return (d['go']*d['gpi']-d['gm']*ge)/((gd+d['go'])*(ge+d['gpi']+gd/(gd+d['go'])*(d['gm']+d['go'])))
    acm_exact=common_or_diff(1/(50+2*rt))
    adm_exact=-common_or_diff(1/50)
    checked_close([acm_exact,adm_exact],[cm[0,1].real,dm[0,0].real],rtol=2e-6)
    checks.append('closed-form common/differential gains with beta and Early effect')
    # Half-circuit admittance pole and zero roots (s in rad/s).
    d = devices[0]
    a,b,g = d['gm'],d['gpi'],d['go']
    cpi,cmu = d['cpi'],d['cmu']
    den = np.polymul([cmu+10e-12,1/1000+g],[cpi,1/50+a+b+g])
    den[-1] -= g*(g+a)
    den[-2] += (g+a)*d['cexbc']
    num = np.array([cmu*cpi,cmu*(1/50+a+b+g)+g*cpi+(g+a)*d['cexbc'],g*b-a/50])
    poles = np.roots(den); zeros = np.roots(num)
    # Near-zero gmu is dropped in this reduced half-circuit only.
    s=2j*np.pi*f
    reduced = np.polyval(num,s)/np.polyval(den,s)
    checked_close(-reduced,dm[:,0],rtol=1e-5,atol=1e-10)
    checks.append('differential half-circuit rational transfer versus AC')
    noise_totals={}; noise_terms={}
    for name, flicker in [('noise-white',False),('noise-flicker',True)]:
        nf=data[name][:,0]
        assert len(nf)==1001 and np.all(np.diff(nf)>0)
        terms=noise_prediction(devices,nf,flicker)
        pred=sum(terms.values())
        measured=data[name][:,2]**2
        checked_close(measured,pred,rtol=8e-5,atol=1e-30)
        noise_totals[name]=pred; noise_terms[name]=terms
        checks.append(name+': independent resistor/base/collector PSD sum')
    noise_f=data['noise-white'][:,0]
    band=(noise_f>=10)&(noise_f<=1e7)
    noise_rms={name:float(np.sqrt(np.trapezoid(data[name][band,2]**2,noise_f[band])))
               for name in noise_totals}
    tran=data['transient']; time=tran[:,0]; out=tran[:,2]
    final=float(out[time>230e-9].mean())
    checked_close(final,dm[0,0].real*100e-6,rtol=3e-5)
    # Input edge ends at 20.05 ns; normalize error to the final output change.
    edge=20.05e-9
    settled={}
    for tolerance in (.01,.001):
        bad=np.flatnonzero((time>=edge)&(abs(out-final)>tolerance*abs(final)))
        i=bad[-1]+1
        assert i<len(time)
        settled[str(tolerance)]=float(time[i]-edge)
    checks.append('100 uV open-loop differential step versus AC and last-exit settling')
    cm_dc=data['dc-common-mode']
    # vbc exports below are recomputed directly because internal vectors may not refresh in DC.
    q1_bc=cm_dc[:,0]-cm_dc[:,1]
    q3_bc=.85-cm_dc[:,2]
    active=(q1_bc<0)&(q3_bc<0)
    mismatch_cm=complex_data(data['mismatch-cm'])
    mismatch_vdd=complex_data(data['mismatch-vdd'])
    noise_low = {name:float(power[0]) for name,power in noise_terms['noise-white'].items()}
    report={
      'operating_point_V':dict(zip(NODES[:6],map(float,op[:6]))),
      'devices':{f'Q{i}':d for i,d in enumerate(devices,1)},
      'differential_gain_V_per_V':float(dm[0,0].real),
      'single_ended_gain_V_per_V':float(dm[0,1].real),
      'common_mode_single_ended_gain_V_per_V':float(cm[0,1].real),
      'single_ended_cmrr_dB':float(20*np.log10(abs(dm[0,1]/cm[0,1]))),
      'tail_output_resistance_ohm':float(rt),
      'output_resistance_single_ended_ohm':float(complex_data(data['output-resistance'])[0,1].real),
      'input_resistance_differential_ohm':float(zin.real),
      'differential_gain_approximation':float(adm_approx),
      'common_mode_gain_approximation':float(acm_approx),
      'common_mode_gain_closed_form':float(acm_exact),
      'differential_gain_closed_form':float(adm_exact),
      'internal_common_mode_X_E1_E3':list(map(float,cm[0,[3,4,5]].real)),
      'supply_single_ended_transfers':{x:float(complex_data(data['ac-'+x])[0,1].real) for x in ('vdd','vss','vb')},
      'single_ended_psrr_dB':{x:float(20*np.log10(abs(dm[0,1]/complex_data(data['ac-'+x])[0,1]))) for x in ('vdd','vss')},
      'VSS_tracking_bias_single_ended_transfer':float(complex_data(data['ac-vss-tracking-bias'])[0,1].real),
      'VSS_tracking_bias_single_ended_psrr_dB':float(20*np.log10(abs(dm[0,1]/complex_data(data['ac-vss-tracking-bias'])[0,1]))),
      'matched_differential_leakage_max_V_per_V':{x:float(np.max(abs(complex_data(data['ac-'+x])[:,0]))) for x in ('cm','vdd','vss','vb')},
      'mismatch_RD2_1percent':{'common_to_differential_V_per_V':float(mismatch_cm[0,0].real),
                             'VDD_to_differential_V_per_V':float(mismatch_vdd[0,0].real)},
      'bandwidth_3dB_Hz':crossing(f,20*np.log10(abs(dm[:,0])),20*np.log10(abs(dm[0,0]))-3),
      'bandwidth_3dB_reduced_transfer_Hz':crossing(f,20*np.log10(abs(reduced)),20*np.log10(abs(reduced[0]))-3),
      'reduced_transfer_max_relative_complex_error':float(np.max(abs(-reduced-dm[:,0])/abs(dm[:,0]))),
      'poles_rad_per_s':list(map(float,poles)), 'zeros_rad_per_s':list(map(float,zeros)),
      'dc_center_slope':float(slope),
      'strict_forward_active_common_mode_sample_range_V':[float(cm_dc[active,0].min()),float(cm_dc[active,0].max())],
      'white_input_noise_nV_per_sqrt_Hz':float(data['noise-white'][0,2]*1e9),
      'flicker_corner_Hz':float((data['noise-flicker'][0,2]**2/data['noise-white'][0,2]**2-1)*noise_f[0]),
      'noise_input_rms_V_10Hz_to_10MHz':noise_rms,
      'white_noise_terms_V2_per_Hz_at_1Hz':noise_low,
      'step_final_V':final,'settling_s_after_edge':settled,
      'checks':checks,
      'analytical_parameter_origin':'SPICE OP device parameters; independent nodal assembly/solution, reduced formulas and noise propagation',
      'conditions':{'VDD_V':3.3,'Vcm_V':1.8,'Vb_V':.85,'temperature_C':27,'load_per_output_F':10e-12,
                    'noise_input':'VDM differential source via +/-0.5 controlled sources','noise_PSD':'one-sided'},
    }
    directory.mkdir(parents=True,exist_ok=True)
    # Curves are grouped by the equations they test.
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    axes[0,0].semilogx(f,20*np.log10(abs(dm[:,0])),label='ngspice differential')
    axes[0,0].semilogx(f,20*np.log10(abs(analytic['ac-dm'][:,0])),'--',label='hybrid-pi KCL')
    axes[0,0].semilogx(f,20*np.log10(abs(dm[:,1])),label='ngspice single-ended')
    axes[0,0].set(xlabel='Frequency (Hz)',ylabel='Gain (dB)',title='Differential and single-ended gains')
    axes[0,0].legend(fontsize=9)
    axes[0,1].semilogx(f,np.unwrap(np.angle(dm[:,0]))*180/np.pi)
    axes[0,1].semilogx(f,np.unwrap(np.angle(analytic['ac-dm'][:,0]))*180/np.pi,'--')
    axes[0,1].set(xlabel='Frequency (Hz)',ylabel='Phase (deg)',title='Differential transfer phase')
    axes[1,0].plot(dc[:,0]*1e3,dc[:,1],label='ngspice')
    axes[1,0].plot(dc[:,0]*1e3,dm[0,0].real*dc[:,0],'--',label='small-signal tangent')
    axes[1,0].set(xlabel='Differential input (mV)',ylabel='Differential output (V)',title='Current steering and linearity')
    axes[1,0].legend(fontsize=9)
    axes[1,1].plot(cm_dc[:,0],q1_bc,label='Q1 base - collector')
    axes[1,1].plot(cm_dc[:,0],q3_bc,label='Q3 base - collector')
    axes[1,1].axhline(0,color='black',lw=.8)
    axes[1,1].set(xlabel='Input common mode (V)',ylabel='BC voltage (V)',title='Forward-active boundary: both curves < 0')
    axes[1,1].legend(fontsize=9)
    savefig(fig,directory/'gain-and-bias')
    plot_frequency_metrics(f,dm[:,0],-reduced,poles,zeros,report['bandwidth_3dB_Hz'],directory)
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    axes[0,0].semilogx(f,abs(cm[:,1]),label='single-ended common-mode')
    axes[0,0].semilogx(f,abs(analytic['ac-cm'][:,1]),'--',label='hybrid-pi KCL')
    axes[0,0].set(xlabel='Frequency (Hz)',ylabel='Magnitude (V/V)',title='Single-ended common-mode gain')
    axes[0,0].legend(fontsize=9)
    for x in ('vdd','vss','vb'):
        axes[0,1].loglog(f,abs(complex_data(data['ac-'+x])[:,1]),label=x.upper())
    axes[0,1].loglog(f,abs(complex_data(data['ac-vss-tracking-bias'])[:,1]),'--',label='VSS, bias tracks VSS')
    axes[0,1].set(xlabel='Frequency (Hz)',ylabel='Magnitude (V/V)',title='Single-ended supply and bias coupling')
    axes[0,1].legend(fontsize=9)
    for index,label in [(3,'X'),(4,'E1'),(5,'E3')]:
        axes[1,0].semilogx(f,abs(cm[:,index]),label=label)
    axes[1,0].set(xlabel='Frequency (Hz)',ylabel='Magnitude (V/V)',title='Internal response to common-mode input')
    axes[1,0].legend(fontsize=9)
    axes[1,1].loglog(f,abs(mismatch_cm[:,0]),label='common mode to differential')
    axes[1,1].loglog(f,abs(mismatch_vdd[:,0]),label='VDD to differential')
    axes[1,1].set(xlabel='Frequency (Hz)',ylabel='Magnitude (V/V)',title='RD2 +1% breaks differential cancellation')
    axes[1,1].legend(fontsize=9)
    savefig(fig,directory/'rejection-and-nodes')
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for name,label in [('noise-white','White baseline'),('noise-flicker','KF = 1e-14, AF = 1')]:
        axes[0].loglog(noise_f,data[name][:,2]*1e9,label='ngspice: '+label)
        axes[0].loglog(noise_f,np.sqrt(noise_totals[name])*1e9,'--',label='KCL: '+label)
    axes[0].set(xlabel='Frequency (Hz)',ylabel='Input ASD (nV/sqrt(Hz))',title='One-sided differential input noise')
    axes[0].legend(fontsize=8)
    grouped={'Input collector shot':sum(noise_low[n] for n in noise_low if 'collector' in n and not n.startswith('Q3')),
             'Input base shot':sum(noise_low[n] for n in noise_low if 'base shot' in n and not n.startswith('Q3')),
             'Emitter resistors':noise_low['R2 thermal']+noise_low['R3 thermal'],
             'Collector loads':noise_low['RD1 thermal']+noise_low['RD2 thermal']}
    axes[1].barh(list(grouped),np.array(list(grouped.values()))*1e18,color='#437ca1')
    axes[1].set(xlabel='Input PSD (nV²/Hz)',title='White-noise power contributions at 1 Hz')
    savefig(fig,directory/'noise')
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    axes[0].plot((time-edge)*1e9,out*1e3,label='ngspice 100 uV step')
    tau=-1/max(poles)
    t=np.maximum(time-edge,0)
    axes[0].plot((time-edge)*1e9,final*(1-np.exp(-t/tau))*1e3,'--',label='dominant-pole estimate')
    axes[0].set(xlabel='Time after edge end (ns)',ylabel='Differential output (mV)',title='Open-loop small-step response',xlim=(-5,160))
    axes[0].legend(fontsize=9)
    axes[1].semilogy((time-edge)*1e9,np.maximum(abs(out-final)/abs(final),1e-12))
    axes[1].axhline(.001,color='gray',ls='--')
    axes[1].set(xlabel='Time after edge end (ns)',ylabel='Relative final-value error',title='Last-exit settling measurement',xlim=(0,160),ylim=(1e-7,2))
    savefig(fig,directory/'settling')
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--ngspice',default=os.environ.get('NGSPICE_BIN','ngspice'))
    args=parser.parse_args()
    exe=shutil.which(args.ngspice) or str(Path(args.ngspice).resolve())
    if not Path(exe).is_file(): raise FileNotFoundError(exe)
    source_report,structural=extract()
    decks=make_decks()
    decks['op-mismatch']=decks['op'].replace('RD2 vdd voutp 1k','RD2 vdd voutp 1.01k').replace('op.dat','op-mismatch.dat')
    with tempfile.TemporaryDirectory(prefix='bjt-differential-pair-') as temp:
        work=Path(temp)
        shutil.copy2(LAB/'models.lib',work/'models.lib')
        data={}; logs=[]
        for name,text in decks.items():
            (work/(name+'.cir')).write_text(text,encoding='utf-8')
            execute(exe,['-b','-o',name+'.log',name+'.cir'],work)
            log=(work/(name+'.log')).read_text(errors='replace')
            logs.append(log)
            if re.search(r'Error:|fatal|unknown parameter|no such vector',log,re.I):
                raise RuntimeError(f'{name}: {log}')
            data[name]=load(work/(name+'.dat'))
        report=process(data,work/'figures')
        report.update({'executed_UTC':datetime.now(timezone.utc).isoformat(),
                       'simulator_detected_version':sorted(set(re.findall(r'ngspice-([^\s]+) done','\n'.join(logs)))),
                       'simulator_executable_sha256':sha(Path(exe)),
                       'source_sha256':source_report['source_sha256'],
                       'input_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [LAB/'models.lib',LAB/'core.cir',Path(__file__),ROOT/'code/bjt_differential_pair_source.py']},
                       'testbench_count':len(decks)})
        (work/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        results=LAB/'results'
        results.mkdir(parents=True,exist_ok=True)
        (LAB/'testbenches').mkdir(parents=True,exist_ok=True)
        for name in decks:
            shutil.copy2(work/(name+'.cir'),LAB/'testbenches'/(name+'.cir'))
            for suffix in ('.dat','.log'):
                shutil.copy2(work/(name+suffix),results/(name+suffix))
        shutil.copy2(work/'checks.json',results/'checks.json')
        FIG.mkdir(parents=True,exist_ok=True)
        for p in (work/'figures').iterdir(): shutil.copy2(p,FIG/p.name)
    schematic(FIG)
    (LAB/'source-structural.cir').write_text(structural,encoding='utf-8')
    (SOURCE.parent/'provenance.json').write_text(json.dumps(source_report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
