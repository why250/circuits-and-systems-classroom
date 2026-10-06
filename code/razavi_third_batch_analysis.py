"""Independent broadband I/O, CTLE and DFE models; no PDK or measured data.

Requires NumPy and Matplotlib. Figures resolve relative to the repository.
The corrected T-coil polynomials are checked against coupled-inductor MNA.
The channel ABCD chain is checked against a separately stamped nodal ladder.
"""
from pathlib import Path
from statistics import NormalDist
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
RESULTS = {}


def finish(fig, name):
    for ax in fig.axes:
        ax.grid(True, alpha=.25)
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=170)
    plt.close(fig)


def tcoil(s, inductance, mutual, ce, cb, ga=0, gb=0, ca=0, cp=0, currents=(1,0,0)):
    """Va--L1--Vx--L2--Vb, bridge Va-Vb; i1/i2 flow left to right."""
    matrix = np.array([
        [ga+s*(ca+cb), 0, -s*cb, 1, 0],
        [0, s*ce, 0, -1, 1],
        [-s*cb, 0, gb+s*(cp+cb), 0, -1],
        [1, -1, 0, -s*inductance, -s*mutual],
        [0, 1, -1, -s*mutual, -s*inductance],
    ], dtype=complex)
    return np.linalg.solve(matrix, [*currents,0,0])[:3]


def corrected_polynomials(s, l, m, ce, cb, r):
    numerator = cb*ce*(l*l-m*m)*s**4+(2*cb*(l+m)-ce*m)*s*s+1
    denominator = cb*ce*(l*l-m*m)*s**4+2*cb*ce*r*(l+m)*s**3+(2*cb*(l+m)+ce*l)*s*s+r*ce*s+1
    return numerator, denominator


def io_models():
    r, ce, k = 50, 400e-15, .5
    l = r*r*ce/(2*(1+k))
    m, cb = k*l, ce*(1-k)/(4*(1+k))
    f = np.logspace(7, 11.5, 650)
    s = 2j*np.pi*f
    va, vx, vb = np.array([tcoil(z,l,m,ce,cb,gb=1/r) for z in s]).T
    n, d = corrected_polynomials(s,l,m,ce,cb,r)
    np.testing.assert_allclose(vb, r*n/d, rtol=1e-10)
    np.testing.assert_allclose(va, r, rtol=1e-10)
    tau, beta = r*ce/2, (l-m)*ce/2
    allpass = (1-tau*s+beta*s*s)/(1+tau*s+beta*s*s)
    lowpass = 1/(1+tau*s+beta*s*s)
    np.testing.assert_allclose(vb/r, allpass, rtol=1e-10)
    np.testing.assert_allclose(vx/r, lowpass, rtol=1e-10)
    np.testing.assert_allclose(np.abs(allpass), 1, rtol=1e-12)
    # General corrected polynomial, with component values deliberately detuned.
    for factor in [.6,1.4]:
        n0,d0 = corrected_polynomials(s,l,m,ce,cb*factor,r)
        direct = [tcoil(z,l,m,ce,cb*factor,gb=1/r)[2] for z in s]
        np.testing.assert_allclose(direct,r*n0/d0,rtol=1e-10)
    # Symmetric current-mode transfer does not depend on bridge capacitance.
    for capacitance in [0,cb,2*cb]:
        vcurrent = np.array([tcoil(z,l,m,ce,capacitance,ga=1/r,gb=1/r,currents=(0,1,0))[2] for z in s])
        np.testing.assert_allclose(vcurrent,(r/2)*lowpass,rtol=1e-10)
    ctot = 470e-15
    unpeaked_bw = 1/(2*np.pi*(r/2)*ctot)
    unpeaked_return = 1/(3*np.pi*r*ctot)
    wn = 1/math.sqrt(beta)
    zeta = tau*wn/2
    wd = wn*math.sqrt(1-zeta*zeta)
    t = np.linspace(0,80e-12,1000)
    step_b = 1-2*tau/(beta*wd)*np.exp(-zeta*wn*t)*np.sin(wd*t)
    step_x = 1-np.exp(-zeta*wn*t)*(np.cos(wd*t)+zeta*wn/wd*np.sin(wd*t))
    RESULTS['io'] = dict(unpeaked_f3dB_GHz=unpeaked_bw/1e9,
        unpeaked_minus10dB_return_GHz=unpeaked_return/1e9, l_pH=l*1e12, cb_fF=cb*1e15,
        natural_frequency_GHz=wn/(2*np.pi)/1e9, zeta=zeta,
        ideal_allpass_step_min_normalized=float(step_b.min()),
        voltage_driver_figure250pH_implied_CE_fF=250e-12*2*(1+k)/(r*r)*1e15)
    fig, axes = plt.subplots(2,2,figsize=(12,8))
    gamma_rc = np.abs(-s*r*ctot/(2+s*r*ctot))
    axes[0,0].semilogx(f/1e9,20*np.log10(gamma_rc),label='Unpeaked 470 fF')
    for cp in [0,70e-15]:
        zout = np.array([tcoil(z,l,m,ce,cb,ga=1/r,cp=cp,currents=(0,0,1))[2] for z in s])
        gamma = np.maximum(np.abs((zout-r)/(zout+r)),1e-6)
        axes[0,0].semilogx(f/1e9,20*np.log10(gamma),label=f'T-coil; Cp = {cp*1e15:g} fF')
        gain = np.array([tcoil(z,l,m,ce,cb,ga=1/r,gb=1/r,cp=cp,currents=(0,1,0))[2] for z in s])
        axes[0,1].semilogx(f/1e9,20*np.log10(np.abs(gain/(r/2))),label=f'Cp = {cp*1e15:g} fF')
    axes[0,0].axhline(-10,color='gray',linestyle=':')
    axes[0,0].set(xlabel='Frequency (GHz)',ylabel='20 log |Γ| (dB)',ylim=(-65,0),title='Output matching; ideal lossless coils')
    axes[0,0].text(.03,.93,'Cp = 0: Γ = 0 (below plotted range)',transform=axes[0,0].transAxes,fontsize=9)
    axes[0,1].set(xlabel='Frequency (GHz)',ylabel='Normalized current-mode gain (dB)',ylim=(-40,3),title='Center current injection; RT = RL = 50 Ω')
    axes[1,0].semilogx(f/1e9,20*np.log10(np.abs(vb/r)),label='Far node: all-pass')
    axes[1,0].semilogx(f/1e9,20*np.log10(np.abs(vx/r)),label='Center node: low-pass')
    axes[1,0].set(xlabel='Frequency (GHz)',ylabel='Normalized gain (dB)',ylim=(-40,3),title='Classic end injection; same component values')
    axes[1,1].plot(t*1e12,step_b,label='Ideal voltage-mode TX / DC value')
    axes[1,1].plot(t*1e12,step_x,label='Center-node RX / DC value')
    axes[1,1].set(xlabel='Time (ps)',ylabel='Unit-step response',title='Flat magnitude does not imply a clean step')
    for ax in axes.flat: ax.legend(fontsize=8)
    finish(fig,'broadband_io_tcoil_models.png')


def channel_response(f, sections=12, rs=50, rl=50):
    s = 2j*np.pi*np.asarray(f)
    z1 = 5.55*s*470e-12/(5.55+s*470e-12)
    yx = s*200e-15/(1+s*2e3*200e-15)+s*80e-15/(1+s*100*80e-15)
    z2, yb = s*77.3e-12, s*30.9e-15
    def series(z):
        result = np.zeros((*z.shape,2,2),complex)
        result[...,0,0]=result[...,1,1]=1
        result[...,0,1]=z
        return result
    def shunt(y):
        result = series(np.zeros_like(y))
        result[...,1,0]=y
        return result
    section = series(z1) @ shunt(yx) @ series(z2) @ shunt(yb)
    total = np.linalg.matrix_power(section,sections)
    a,b,c,d = total[...,0,0],total[...,0,1],total[...,1,0],total[...,1,1]
    return 1/(a+b/rl+rs*(c+d/rl))


def channel_nodal(f, sections=12, rs=50, rl=50):
    s = 2j*np.pi*f
    z1 = 5.55*s*470e-12/(5.55+s*470e-12)
    yx = s*200e-15/(1+s*2e3*200e-15)+s*80e-15/(1+s*100*80e-15)
    z2, yb = s*77.3e-12, s*30.9e-15
    matrix=np.zeros((2*sections+1,2*sections+1),complex)
    def branch(i,j,y):
        matrix[i,i]+=y
        matrix[j,j]+=y
        matrix[i,j]-=y
        matrix[j,i]-=y
    for index in range(sections):
        previous,mid,end=2*index,2*index+1,2*index+2
        branch(previous,mid,1/z1)
        branch(mid,end,1/z2)
        matrix[mid,mid]+=yx
        matrix[end,end]+=yb
    matrix[0,0]+=1/rs
    matrix[-1,-1]+=1/rl
    rhs=np.zeros(2*sections+1,complex)
    rhs[0]=1/rs
    return np.linalg.solve(matrix,rhs)[-1]


def ctle_response(s,gm=.01,rd=400,rs=400,cs=150e-15,cl=20e-15,ld=0):
    zs=rs/(1+s*rs*cs)
    zd=(rd+s*ld)/(1+s*cl*(rd+s*ld))
    return -gm*zd/(1+gm*zs/2)


def ctle_models():
    f=np.logspace(7,11,700)
    s=2j*np.pi*f
    channel=channel_response(f)
    for frequency in [1e8,28e9,1e11]:
        np.testing.assert_allclose(channel_response(np.array([frequency]))[0],channel_nodal(frequency),rtol=1e-10)
    gm,rd,rs,cs,cl=.01,400,400,150e-15,20e-15
    boost=1+gm*rs/2
    # Half-circuit source/output KCL, with differential bridge Zs/2.
    for z in s[::20]:
        zs=rs/(1+z*rs*cs)
        zd=rd/(1+z*rd*cl)
        vs,vo=np.linalg.solve([[2/zs+gm,0],[-gm,1/zd]],[gm,-gm])
        np.testing.assert_allclose(vo,ctle_response(z),rtol=1e-12)
    factor95={str(b):math.sqrt((1-.95**2)/(.95**2-1/b**2)) for b in [2,3]}
    RESULTS['ctle']=dict(channel_loss_28GHz_dB=float(-20*np.log10(abs(channel_response(np.array([28e9]))[0]/.5))),
        ideal_DC_gain=gm*rd/boost, boost_factor=boost, boost_dB=20*math.log10(boost),
        zero_GHz=1/(2*np.pi*rs*cs)/1e9,pole_GHz=boost/(2*np.pi*rs*cs)/1e9,
        pole_over_Nyquist_for95percent=factor95,
        exact_cap_for_pole28GHz_over3_fF=boost/(2*np.pi*(28e9/3)*rs)*1e15,
        two_identical_output_pole_BW_ratio=math.sqrt(math.sqrt(2)-1))
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for capacitance in [75e-15,150e-15,300e-15]:
        h=ctle_response(s,cs=capacitance)
        axes[0,0].semilogx(f/1e9,20*np.log10(np.abs(h)),label=f'CS = {capacitance*1e15:g} fF')
    axes[0,0].set(xlabel='Frequency (GHz)',ylabel='Gain (dB)',title='Bridge degeneration; CL = 20 fF; LD = 0')
    for inductance in [0,600e-12]:
        h=ctle_response(s,ld=inductance)
        axes[0,1].semilogx(f/1e9,20*np.log10(np.abs(h)),label=f'LD = {inductance*1e12:g} pH')
    axes[0,1].set(xlabel='Frequency (GHz)',ylabel='Gain (dB)',title='Illustrative shunt peaking; no transistor parasitics')
    axes[1,0].semilogx(f/1e9,20*np.log10(np.abs(channel/.5)),label='12-section channel / DC')
    h=ctle_response(s,ld=600e-12)**2
    axes[1,0].semilogx(f/1e9,20*np.log10(np.abs(h/h[0])),label='Two model CTLE stages / DC')
    axes[1,0].semilogx(f/1e9,20*np.log10(np.abs(channel*h/(.5*h[0]))),label='Cascade / DC')
    axes[1,0].set(xlabel='Frequency (GHz)',ylabel='Normalized gain (dB)',title='Channel fit components; CTLE load is illustrative')
    b=np.linspace(1.3,5,400)
    gain=4/b
    axes[1,1].plot(20*np.log10(b),20*np.log10(gain))
    axes[1,1].set(xlabel='Ideal boost (dB)',ylabel='DC gain (dB)',title='Fixed gmRD = 4: increasing boost spends DC gain')
    for ax in axes.flat: ax.legend(fontsize=8) if ax.lines[0].get_label()[0]!='_' else None
    finish(fig,'continuous_time_equalizer_models.png')


def decision_feedback(samples,taps,forced_error=None):
    decisions=np.zeros(len(samples))
    corrected=np.zeros(len(samples))
    for index,value in enumerate(samples):
        corrected[index]=value-sum(tap*decisions[index-delay] for delay,tap in taps.items() if index>=delay)
        decisions[index]=1 if corrected[index]>=0 else -1
        if index==forced_error: decisions[index]*=-1
    return corrected,decisions


def qfunc(x):
    return .5*math.erfc(x/math.sqrt(2))


def dfe_models():
    rng=np.random.default_rng(20221005)
    symbols=rng.choice([-1,1],4096)
    cursors=np.array([1,.22,-.03,-.06])
    samples=np.convolve(symbols,cursors)[:len(symbols)]
    margins=[]
    for taps in [{},{1:.22},{1:.22,3:-.06}]:
        corrected,decisions=decision_feedback(samples,taps)
        residual=cursors.copy()
        for delay,tap in taps.items(): residual[delay]-=tap
        expected=np.convolve(symbols,residual)[:len(symbols)]
        np.testing.assert_allclose(corrected,expected,atol=1e-14)
        np.testing.assert_array_equal(decisions,symbols)
        margins.append(float(np.min(symbols[3:]*corrected[3:])))
    sigma_pair=4e-3/math.sqrt(5*.03)
    sigma_offset=math.hypot(sigma_pair,sigma_pair/2)
    sigma_noise=math.hypot(1.5e-3,2.6e-3)
    qargument=-NormalDist().inv_cdf(1e-12)
    required_eye=2*(4*sigma_offset+qargument*sigma_noise)
    ui=1/56e9
    track_tau,gain,initial=6e-12,2,.5
    recovery={str(v):track_tau*math.log(1+initial/(gain*v))*1e12 for v in [.07,.1]}
    # Impulse versus rectangular-symbol samples: causal first-order model tau=UI.
    q=math.exp(-1)
    p0=1-math.exp(-.5)
    p1=(1-q)*math.exp(-.5)
    # Independent integration of g(t-u) over the previous rectangular symbol.
    u=np.linspace(0,ui,10001)
    trap=np.trapezoid if hasattr(np,'trapezoid') else np.trapz
    p1_integral=trap(np.exp(-(1.5*ui-u)/ui)/ui,u)
    np.testing.assert_allclose(p1,p1_integral,rtol=1e-8)
    n_zero_errors=-math.log(.05)/1e-12
    RESULTS['dfe']=dict(UI_ps=ui*1e12, ideal_normalized_margins=margins,
        mismatch_sigma_mV=sigma_pair*1e3,latch_offset_sigma_mV=sigma_offset*1e3,
        total_noise_mV=sigma_noise*1e3,conservative_static_eye_mV=required_eye*1e3,
        illustrative_recovery_ps=recovery,sense_half_period_ps=ui/2*1e12,
        impulse_first_postcursor=q,rectangular_symbol_first_postcursor_at_halfUI=p1/p0,
        zero_error_95percent_required_bits=n_zero_errors,
        zero_error_95percent_required_seconds=n_zero_errors/56e9)
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    axes[0,0].bar(['No DFE','Tap 1','Taps 1 + 3'],margins)
    axes[0,0].set(ylim=(0,1.1),ylabel='Worst signed sample / main cursor',title='Noiseless symbol model: [1, 0.22, −0.03, −0.06]')
    amplitude=np.linspace(.01,.1,500)
    for offset in [0,45e-3]:
        ber=[.5*(qfunc((v-offset)/sigma_noise)+qfunc((v+offset)/sigma_noise)) for v in amplitude]
        axes[0,1].semilogy(amplitude*1e3,np.maximum(ber,1e-30),label=f'Fixed offset = {offset*1e3:g} mV')
    axes[0,1].axhline(1e-12,color='gray',linestyle=':')
    axes[0,1].set(xlabel='Half-eye amplitude (mV)',ylabel='Gaussian conditional BER',ylim=(1e-20,1),title='Static Gaussian model; RMS noise = 3.002 mV')
    v=np.linspace(.03,.2,500)
    tcross=track_tau*np.log(1+initial/(gain*v))
    axes[1,0].plot(v*1e3,tcross*1e12)
    axes[1,0].axhline(ui/2*1e12,color='gray',linestyle=':',label='UI/2 available, ideal clock')
    axes[1,0].set(xlabel='New opposite input amplitude (mV)',ylabel='Output zero-crossing time (ps)',title='Illustrative recovery: τ = 6 ps; gain = 2; old x = 0.5 V')
    sequence=np.where(np.arange(128)%2==0,1,-1)
    sequence[90:]=1
    error_counts={}
    for tap in [.22,.7]:
        received=np.convolve(sequence,[1,tap])[:len(sequence)]
        _,decisions=decision_feedback(received,{1:tap},forced_error=40)
        error=(decisions!=sequence).astype(int)
        error_counts[str(tap)]=int(error.sum())
        axes[1,1].step(np.arange(128),error+(0 if tap==.22 else 1.4),where='mid',label=f'h1 = {tap:g}')
    RESULTS['dfe']['forced_error_counts_in_example']=error_counts
    assert error_counts['0.22']==1 and error_counts['0.7']>1
    axes[1,1].set(xlabel='Symbol index',ylabel='Decision error (traces offset)',title='Force one error at k = 40; alternating data then a run')
    for ax in [axes[0,1],axes[1,0],axes[1,1]]: ax.legend(fontsize=8)
    finish(fig,'decision_feedback_equalizer_models.png')


def main():
    FIGURES.mkdir(exist_ok=True)
    io_models()
    ctle_models()
    dfe_models()
    print(json.dumps(RESULTS,indent=2))
    print('Coupled-inductor MNA, channel nodal/ABCD, CTLE KCL and DFE recurrence checks passed.')


if __name__=='__main__':
    main()
