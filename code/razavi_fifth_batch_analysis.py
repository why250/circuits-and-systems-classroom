"""Independent phase-interpolation and CDR models; no PDK/noise reproduction.

Requires NumPy and Matplotlib. Check phasors against waveform crossings,
predistortion, feedback KCL, Alexander truth tables, and loop state equations.
"""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
RESULTS = {}


def save(fig, name):
    for ax in fig.axes:
        ax.grid(True, alpha=.25)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=170)
    plt.close(fig)


def angle_from_weights(w):
    q = np.r_[0, np.cumsum(w)]
    return np.arctan2(q, w.sum()-q)


def pi_models():
    f, n = 28e9, 16
    omega=2*np.pi*f
    theta=angle_from_weights(np.ones(n))
    delay=theta/omega
    steps=np.diff(delay)
    # Direct weighted sinusoidal zero crossings independently check atan2.
    for m in range(17):
        a=m/n
        waveform=lambda x: (1-a)*np.sin(x)+a*np.sin(x-np.pi/2)
        assert abs(waveform(theta[m]))<1e-14
    # Independent phase-perturbation derivative of a complex quadrature sum.
    for gi,gq in [(3.,1.),(1.,1.),(1.,3.)]:
        eps=1e-7
        base=complex(gi,gq)
        derivative=(np.angle(gi*np.exp(1j*eps)+1j*gq)-np.angle(base))/eps
        np.testing.assert_allclose(derivative,gi*gi/(gi*gi+gq*gq),rtol=2e-7)
    target=np.linspace(0,np.pi/2,n+1)
    # Fixed total conductance: cumulative Q fraction gives uniform angles.
    fraction=np.sin(target)/(np.sin(target)+np.cos(target))
    ideal_weights=np.diff(fraction)
    np.testing.assert_allclose(angle_from_weights(ideal_weights),target,atol=1e-14)
    assert np.all(ideal_weights>0)
    resistors=np.array([500,500,1000,1000,2000,2000,3000,3000,
                       3000,3000,2000,2000,1000,1000,500,500])
    practical_theta=angle_from_weights(1/(resistors+1000))
    # Thermometer monotonicity under static positive but unequal conductances.
    rng=np.random.default_rng(20261005)
    for _ in range(100):
        assert np.all(np.diff(angle_from_weights(np.exp(rng.normal(0,.3,n))))>0)
    # Finite inverter gain and virtual summing node: stamp output relation/KCL.
    g=np.full(n,1/1000)
    gf=1/3000
    aopen=20/(1+2j*np.pi*28e9/10e9)
    cx=5e-15
    u=np.r_[np.ones(8),-1j*np.ones(8)]
    den=g.sum()+(1+aopen)*gf+1j*omega*cx
    vout=-aopen*np.dot(g,u)/den
    vx,vo=np.linalg.solve([[g.sum()+gf+1j*omega*cx,-gf],[aopen,1]],
                          [np.dot(g,u),0])
    np.testing.assert_allclose(vo,vout,rtol=1e-12)
    # Two equal sigmoid edges: gap causes a shallow midpoint, slow edges also hurt.
    separation=1/(4*f)
    taus=np.linspace(.7e-12,20e-12,1000)
    slopes=.95/(2*taus)/np.cosh(separation/(2*taus))**2
    jitter=1e-3/slopes
    best=int(np.argmin(jitter))
    # Single fine branch: monotonic ordering requires fine weight < every coarse unit.
    for weights in [np.ones(n),ideal_weights/ideal_weights.mean()]:
        fine=.4*weights.min()
        values=sorted([float((sum(weights[:k])+b*fine)/(sum(weights)+fine))
                       for k in range(n+1) for b in [0,1]])
        assert np.all(np.diff(values)>0)
        for k in range(n):
            assert sum(weights[:k])+fine<sum(weights[:k+1])
    RESULTS['pi']=dict(UI_56Gbps_ps=1e12/56e9,clock_period_28GHz_ps=1e12/f,
        quadrant_ps=separation*1e12,minimum_uniform_intervals_for_400fs=math.ceil(separation/.4e-12),
        equal16_min_step_fs=steps.min()*1e15,equal16_max_step_fs=steps.max()*1e15,
        uniform16_step_fs=separation/n*1e15,uniform32_step_fs=separation/32*1e15,
        first_equal16_angle_deg=theta[1]*180/np.pi,
        three_I_one_Q_angle_deg=math.degrees(math.atan(1/3)),
        midpoint_independent_input_phase_variance_ratio=.5,
        midpoint_common_input_phase_variance_ratio=1.,
        ideal_predistortion_conductance_spread=ideal_weights.max()/ideal_weights.min(),
        ideal_predistortion_max_INL_fs=float(np.max(abs(target-angle_from_weights(ideal_weights)))/omega*1e15),
        two_input_buffer_power_mW=2*28e9*16e-15*.95**2*1e3,
        illustrative_sigmoid_best_tau_ps=taus[best]*1e12,
        illustrative_sigmoid_min_jitter_fs=jitter[best]*1e15,
        largest_source_step_uniform_quantization_RMS_fs=362/math.sqrt(12),
        finite_gain_KCL_output_real=float(vo.real),finite_gain_KCL_output_imag=float(vo.imag))
    fig,axs=plt.subplots(2,2,figsize=(12,8))
    axs[0,0].plot(range(17),theta*180/np.pi,'o-',label='Equal conductance')
    axs[0,0].plot(range(17),target*180/np.pi,'--',label='Uniform angle target')
    axs[0,0].set(xlabel='Branches switched from I to Q',ylabel='Angle (degrees)',title='Linear weights do not give uniform time steps')
    axs[0,0].legend(fontsize=8)
    axs[0,1].plot(range(1,17),steps*1e15,'o-',label='Equal conductance')
    axs[0,1].plot(range(1,17),np.diff(practical_theta)/omega*1e15,'s-',label='Source R pattern + illustrative 1 kΩ output R')
    axs[0,1].axhline(separation/n*1e15,linestyle='--',color='gray',label='Ideal uniform 16 intervals')
    axs[0,1].set(xlabel='Step number',ylabel='Time step (fs)',title='Static phasor examples; not transistor waveform results')
    axs[0,1].legend(fontsize=7)
    axs[1,0].plot(range(1,17),ideal_weights/ideal_weights.mean(),'o-')
    axs[1,0].set(xlabel='Thermometer unit',ylabel='Conductance / mean conductance',title='Exact ideal fixed-sum weights for uniform angle')
    axs[1,1].plot(taus*1e12,jitter*1e15)
    axs[1,1].set(ylim=(0,250),xlabel='Sigmoid edge parameter τ (ps)',ylabel='Timing noise (fs RMS)',title='Illustrative: Δ = 8.93 ps, σV = 1 mV')
    save(fig,'phase_interpolator_models.png')


def alexander(s1,s2,s3):
    return s1^s2,s2^s3


def cdr_models():
    # Late/early use the source's sample-pattern labels, with no assumed clock wiring.
    assert alexander(0,0,1)==(0,1) and alexander(1,1,0)==(0,1)
    assert alexander(0,1,1)==(1,0) and alexander(1,0,0)==(1,0)
    assert alexander(0,0,0)==(0,0) and alexander(1,1,1)==(0,0)
    # Symmetric gate: each triplet steers tail current to output only for equality.
    for a in [0,1]:
        for b in [0,1]:
            low_branch=(1-a)*(1-b)
            high_branch=a*b
            assert low_branch+high_branch==1-(a^b)
    fn=20e6
    wn=2*np.pi*fn
    zeta=1/math.sqrt(2)
    wp=2*zeta*wn
    kappa=wn*wn/wp
    f=np.logspace(3,10,3000)
    s=2j*np.pi*f
    l1=kappa/(s*(1+s/wp))
    h1=l1/(1+l1)
    den=s*s+2*zeta*wn*s+wn*wn
    np.testing.assert_allclose(h1,wn*wn/den,rtol=1e-12)
    for i in range(0,len(s),120):
        # Normalize the phase-velocity state by wn to avoid mixed-scale conditioning.
        phi,q=np.linalg.solve([[s[i]/wn,-1],[kappa*wp/wn**2,(s[i]+wp)/wn]],
                             [0,kappa*wp/wn**2])
        np.testing.assert_allclose(phi,h1[i],rtol=1e-12)
    # Ideal transconductance into series RC gives type II, not the above type I.
    r,c,kv=1e3,4e-12,2*np.pi*1e9
    ki=wn*wn*c/kv
    # Select R for matched illustrative damping; source R is considered separately.
    matched_r=2*zeta*wn/(ki*kv)
    l2=ki*kv*(matched_r+1/(s*c))/s
    h2=l2/(1+l2)
    np.testing.assert_allclose(h2,(2*zeta*wn*s+wn*wn)/den,rtol=1e-12)
    for i in range(0,len(s),120):
        # Normalize capacitor voltage by wn/kv; equations still come from KCL.
        phi,vc=np.linalg.solve([[(s[i]+kv*matched_r*ki)/wn,-1],
                                [1,s[i]*c*wn/(kv*ki)]],
                               [kv*matched_r*ki/wn,1])
        np.testing.assert_allclose(phi,h2[i],rtol=1e-12)
    # Actual source-labeled R,C: independently stamp finite transconductor ro.
    ro=10e3
    z_eff=ro*(1+s*r*c)/(1+s*(r+ro)*c)
    for i in range(0,len(s),120):
        vctrl,vc=np.linalg.solve([[1/ro+1/r,-1/r],[-1/r,1/r+s[i]*c]],[1,0])
        np.testing.assert_allclose(vctrl,z_eff[i],rtol=1e-12)
    np.testing.assert_allclose(1-h1,(s*s+wp*s)/den,rtol=1e-11)
    np.testing.assert_allclose(1-h2,s*s/den,rtol=1e-10,atol=1e-14)
    # Averaged bang-bang smoothing by a specified Gaussian timing distribution.
    rho,vstep,sigmat=.5,.02,200e-15
    sigmaphi=2*np.pi*56e9*sigmat
    effective_gain=rho*vstep*math.sqrt(2/np.pi)/sigmaphi
    e=np.linspace(-.3,.3,401)
    mean=rho*vstep*np.array([math.erf(x/(math.sqrt(2)*sigmaphi)) for x in e])
    eps=1e-7
    numeric_gain=rho*vstep*math.erf(eps/(math.sqrt(2)*sigmaphi))/eps
    np.testing.assert_allclose(effective_gain,numeric_gain,rtol=1e-10)
    # No-transition phase drift: constant mismatch versus integrated leakage ramp.
    run_bits=np.arange(0,1001)
    run_time=run_bits/56e9
    fractional_error=100e-6
    dt_offset=fractional_error*run_time
    leak=20e-9
    dt_leak=(1e9*leak/(2*c*56e9))*run_time**2
    # Charge and frequency integral are independently checked over 100 ns.
    t=np.linspace(0,100e-9,10001)
    dv=leak*t/c
    integrated=np.trapezoid(1e9*dv,t) if hasattr(np,'trapezoid') else np.trapz(1e9*dv,t)
    np.testing.assert_allclose(integrated/56e9,1e9*leak*t[-1]**2/(2*c*56e9))
    RESULTS['cdr']=dict(typeI_example_fn_MHz=fn/1e6,typeI_correct_zeta=zeta,
        source_zeta_if_missing_half=math.sqrt(wp/kappa),
        matched_typeII_R_ohm=matched_r,source_RC_zero_MHz=1/(2*np.pi*r*c)/1e6,
        source_series_RC_with_10kohm_ro_pole_MHz=1/(2*np.pi*(r+ro)*c)/1e6,
        illustrative_Gaussian_Kpd_V_per_rad=effective_gain,
        typeI_example_100ppm_steady_phase_error_deg=(2*np.pi*56e9*100e-6/kappa)*180/np.pi,
        drift_at1000bits_100ppm_ps=float(dt_offset[-1]*1e12),
        leakage_control_drift_100ns_mV=dv[-1]*1e3,
        leakage_timing_drift_100ns_ps=integrated/56e9*1e12,
        degree50_at56GHz_ps=(50/360)/56e9*1e12,
        degree10_at56GHz_ps=(10/360)/56e9*1e12,
        VCO_buffer_source_power_mW=.95*.003*1e3,
        two_XOR_tail_subtotal_mW=.95*4*.0002*1e3,
        ideal_half_tank_100pH_60fF_GHz=1/(2*np.pi*math.sqrt(100e-12*60e-15))/1e9)
    fig,axs=plt.subplots(2,2,figsize=(12,8))
    axs[0,0].plot(e*180/np.pi,mean*1e3,label='Averaged detector')
    axs[0,0].plot(e*180/np.pi,e*effective_gain*1e3,'--',label='Local slope')
    axs[0,0].set(ylim=(-15,15),xlabel='Corrective phase error (degrees)',ylabel='Average detector output (mV)',title='Illustrative Gaussian smoothing: ρ = 0.5, σt = 200 fs')
    axs[0,0].legend(fontsize=8)
    for h,label in [(h1,'Type I: single-pole voltage filter'),(h2,'Type II: current into series RC')]:
        axs[0,1].semilogx(f/1e6,20*np.log10(abs(h)),label=label)
        axs[1,0].semilogx(f/1e6,20*np.log10(abs(1-h)),label=label)
    axs[0,1].set(xlim=(.1,1000),ylim=(-45,5),xlabel='Modulation frequency (MHz)',ylabel='Clock / data phase (dB)',title='Matched poles; different transfer numerators')
    axs[0,1].legend(fontsize=7)
    axs[1,0].set(xlim=(.1,1000),ylim=(-90,5),xlabel='Modulation frequency (MHz)',ylabel='Relative sampling error / data phase (dB)',title='Ideal residual timing: high-pass does not mean monotonic')
    axs[1,0].legend(fontsize=7)
    axs[1,1].plot(run_bits,dt_offset*1e12,label='Constant 100-ppm frequency mismatch')
    axs[1,1].plot(run_bits,dt_leak*1e12,label='Only 20-nA control leakage; Kf = 1 GHz/V')
    axs[1,1].set(xlabel='Consecutive identical bits at 56 Gb/s',ylabel='Timing drift (ps)',title='Illustrative holdover; no fresh transition information')
    axs[1,1].legend(fontsize=7)
    save(fig,'clock_data_recovery_models.png')


def main():
    OUT.mkdir(exist_ok=True)
    pi_models()
    cdr_models()
    print(json.dumps(RESULTS,indent=2))
    print('Phasor/zero-crossing, predistortion, KCL, truth-table and loop/state checks passed.')


if __name__=='__main__':
    main()
