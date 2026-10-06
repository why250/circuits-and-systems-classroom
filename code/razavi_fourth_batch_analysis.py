"""Independent mm-wave VCO, divider and PLL models; no transistor/EM simulation.

Requires NumPy and Matplotlib. Paths resolve from this file. Circuit KCL,
Boolean state transitions and scaling identities check independent formulas.
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
integrate = np.trapezoid if hasattr(np, 'trapezoid') else np.trapz


def save(fig, name):
    for ax in fig.axes:
        ax.grid(True, alpha=.25)
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=170)
    plt.close(fig)


def vco_models():
    f0, lh, ql, current, temp = 30e9, 53e-12, 32, 2e-3, 350
    omega = 2*np.pi*f0
    rp = omega*lh*ql
    swing = 4/np.pi*current*rp
    source_pn = np.pi**2*1.38e-23*temp*2/(2*rp*current**2)*(f0/(2*ql*1e6))**2
    rewritten = 2*np.pi*1.38e-23*temp*2/(current*swing)*(f0/(2*ql*1e6))**2
    np.testing.assert_allclose(source_pn, rewritten)
    qvar = 1/(1/ql + (1/21)/20)
    qbank = 1/(1/ql + (140/610)/32)
    qbank_source = 1/(1/ql + (140/750)/32)
    # Capacitor + switch-R + switch-C: direct KCL versus impedance reduction.
    ca, cp, ron = 140e-15, 140e-15, 1/(omega*140e-15*32)
    freqs = np.logspace(9, 11, 400)
    s = 2j*np.pi*freqs
    y = s*ca*(1/ron+s*cp)/(s*(ca+cp)+1/ron)
    ynode=[]
    for z in s:
        vn = z*ca/(1/ron+z*(ca+cp))
        ynode.append(z*ca*(1-vn))
    np.testing.assert_allclose(y, ynode, rtol=1e-12)
    effective_q = y.imag/y.real
    ceff = y.imag/(2*np.pi*freqs)
    c_off = ca*cp/(ca+cp)
    assert abs(c_off-70e-15)<1e-25
    q_at30 = float(np.interp(f0, freqs, effective_q))
    # Charge fundamental for a nonlinear C(v)=C0+b*v^2 model.
    fixed, cv, b = 500e-15, 25e-15, 250e-15
    theta=np.linspace(0,2*np.pi,20001)
    amplitudes=np.linspace(.05,.5,180)
    analytic_c=cv+b*amplitudes**2/4
    for a in [.1,.4]:
        v=a*np.cos(theta)
        charge=cv*v+b*v**3/3
        numerical_c=integrate(charge*np.cos(theta),theta)/(np.pi*a)
        np.testing.assert_allclose(numerical_c,cv+b*a*a/4,rtol=1e-12)
    tune_cap = lambda f: 1/((2*np.pi*f)**2*lh)
    RESULTS['vco'] = dict(half_tank_rp_ohm=rp,square_steering_swing_Vpp=swing,
        source_eq1_at1MHz_dB=10*np.log10(source_pn),
        required_Q_for_eq2_minus100=math.sqrt(2*np.pi*1.38e-23*350*2/(.002*.8)*(30e9/(2e6))**2/1e-10),
        capacitance_28GHz_fF=tune_cap(28e9)*1e15,capacitance_32GHz_fF=tune_cap(32e9)*1e15,
        varactor_loaded_Q=qvar,varactor_Q_drop_percent=100*(1-qvar/ql),
        switched_loaded_Q_fixed470fF=qbank,source_using_C1_610fF_Q=qbank_source,
        source_bank_Q_penalty_dB=20*np.log10(ql/qbank_source),
        exact_bank_Q_penalty_dB=20*np.log10(ql/qbank),
        switch_ron_for_Q32_ohm=ron,switch_with_Cp_Q_at30=q_at30,
        control_ripple_peak_for_minus60_mV=(2*200e6/1.9e9*1e-3)*1e3,
        one_sided_control_ASD_for_SSBminus110_nV=math.sqrt(2*1e-11)*1e6/1.9e9*1e9,
        single_ended_off_cap_fF=c_off*1e15,
        differential_switch_off_cap_fF=ca*(cp/2)/(ca+cp/2)*1e15,
        final_core_plus_reference_power_mW=.95*(.001+.0004)*1e3)
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    caps=np.linspace(440,700,300)
    axes[0,0].plot(caps,1/(2*np.pi*np.sqrt(lh*caps*1e-15))/1e9)
    axes[0,0].set(xlabel='Total capacitance per half tank (fF)',ylabel='Frequency (GHz)',title='LC model: 53 pH per half tank')
    fraction=np.linspace(0,.4,200)
    for qc in [10,20,32]:
        axes[0,1].plot(fraction,1/(1/ql+fraction/qc),label=f'Capacitor Q = {qc}')
    axes[0,1].set(xlabel='Lossy capacitor fraction of total C',ylabel='Loaded tank Q',title='Add loss conductances at resonance')
    axes[0,1].legend(fontsize=8)
    axes[1,0].semilogx(freqs/1e9,effective_q,label='Exact branch including Cp')
    axes[1,0].semilogx(freqs/1e9,1/(2*np.pi*freqs*ca*ron),'--',label='Series-R approximation')
    axes[1,0].set(xlabel='Frequency (GHz)',ylabel='Branch Q',title='Ca = Cp = 140 fF; Ron = 1.184 Ω')
    axes[1,0].legend(fontsize=8)
    f_amp=1/(2*np.pi*np.sqrt(lh*(fixed+analytic_c)))
    axes[1,1].plot(amplitudes,f_amp/1e9)
    axes[1,1].set(xlabel='Single-ended sine amplitude (V peak)',ylabel='Frequency (GHz)',title='Illustrative nonlinear C: amplitude changes frequency')
    save(fig,'millimeter_wave_vco_models.png')


def div23_period(mc):
    state=(0,0)
    seen={}
    for t in range(12):
        if state in seen:
            return t-seen[state]
        seen[state]=t
        q1,q2=state
        # True internal FF states; output FF1 is complemented at the AND gate.
        state=(int(mc and q2),int((not q1) and (not q2)))
    raise AssertionError('No repeating state')


def divider_models():
    assert div23_period(0)==2 and div23_period(1)==3
    codes=np.arange(512)
    bits=((codes[:,None]>>np.arange(9))&1)
    ratios=512+bits@(2**np.arange(9))
    np.testing.assert_array_equal(ratios,np.arange(512,1024))
    cin=.92e-3/(30e9*.95**2)
    # Sharing is charge conservation, not a MOS transient simulation.
    cq,cn=4e-15,2e-15
    shared=(cq*0+cn*.95)/(cq+cn)
    leakage_limit=cq*.3/10e-9
    ratio=575
    RESULTS['divider']=dict(div23_periods=[div23_period(0),div23_period(1)],
        nine_module_range=[int(ratios.min()),int(ratios.max())],
        code_for_575=575-512,code_for_560=560-512,code_for_640=640-512,
        frequency_at30GHz_div575_MHz=30e9/ratio/1e6,
        buffer_equivalent_C_fF=cin*1e15,illustrative_charge_share_V=shared,
        leakage_limit_for_4fF_300mV_10ns_nA=leakage_limit*1e9,
        divider_by3_input_PN_shift_dB=20*math.log10(3))
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    axes[0,0].plot(codes,ratios)
    axes[0,0].set(xlabel='Unsigned code B9...B1',ylabel='Divide ratio',title='Nine modular stages: N = 512 + code')
    f=np.linspace(5,60,250)
    axes[0,1].plot(f,f*1e9*cin*.95**2*1e3,label='Equivalent C inferred from source buffer power')
    axes[0,1].axhline(.4,color='gray',linestyle=':',label='Source first-module core at 30 GHz')
    axes[0,1].set(xlabel='Input frequency (GHz)',ylabel='Power (mW)',title='Clock load alone: Ceff = 33.98 fF')
    axes[0,1].legend(fontsize=8)
    r=np.linspace(0,2,200)
    axes[1,0].plot(r,.95*r/(1+r))
    axes[1,0].set(xlabel='Internal-node C / output-node C',ylabel='Low-state sharing disturbance (V)',title='Illustrative sharing: internal node initially at VDD')
    t=np.linspace(0,15,250)
    for leak in [40e-9,120e-9,200e-9]:
        axes[1,1].plot(t,np.maximum(.95-leak*t*1e-9/cq,0),label=f'Ileak = {leak*1e9:g} nA')
    axes[1,1].set(xlabel='Store time (ns)',ylabel='Stored high voltage (V)',title='Illustrative leakage: Cnode = 4 fF')
    axes[1,1].legend(fontsize=8)
    save(fig,'millimeter_wave_divider_models.png')


def impedance(s,r,c1,c2):
    return (1+s*r*c1)/(s*(c1+c2)+s*s*r*c1*c2)


def loop(s,n=300,r=8700,c1=15.2e-12,c2=.5e-12,ip=.5e-3,kv=2*np.pi*2.08e9):
    return ip/(2*np.pi)*impedance(s,r,c1,c2)*kv/(n*s)


def cp_phase_one_sided(n,fref,ip=.5e-3,tres=25e-12,temp=348.15,vov=.2):
    noise_each=4*1.38e-23*temp*(2*ip/vov)
    return (2*np.pi*n/ip)**2*2*noise_each*tres*fref


def pll_models():
    n,r,c1,c2,ip,kv=300,8700,15.2e-12,.5e-12,.5e-3,2*np.pi*2.08e9
    f=np.logspace(2,11,20000)
    s=2j*np.pi*f
    z=impedance(s,r,c1,c2)
    # Current injection into control node, R1 to C1 node, C2 to ground.
    for index in range(0,len(s),600):
        ss=s[index]
        va,vb=np.linalg.solve([[1/r+ss*c2,-1/r],[-1/r,1/r+ss*c1]],[1,0])
        np.testing.assert_allclose(va,z[index],rtol=1e-10)
    l=loop(s)
    h=l/(1+l)
    v=1/(1+l)
    wn=math.sqrt(ip*kv/(2*np.pi*c1*n))
    damping=r/2*math.sqrt(ip*kv*c1/(2*np.pi*n))
    # C2=0: independently derive normalized closed-loop polynomial.
    h2=(2*damping*wn*s+wn*wn)/(s*s+2*damping*wn*s+wn*wn)
    l2=loop(s,c2=0)
    np.testing.assert_allclose(l2/(1+l2),h2,rtol=1e-12)
    factor=math.sqrt(1+2*damping**2+math.sqrt((1+2*damping**2)**2+1))
    # Full third-order characteristic must be stable.
    k=ip*kv/(2*np.pi*n)
    roots=np.roots([r*c1*c2,c1+c2,k*r*c1,k])
    assert np.all(roots.real<0)
    fu=float(np.interp(0, (20*np.log10(abs(l)))[::-1], f[::-1]))
    pm=180+float(np.interp(fu,f,np.unwrap(np.angle(l))*180/np.pi))
    f3=float(np.interp(-3.01029995664,(20*np.log10(abs(h)))[::-1],f[::-1]))
    # Two distinct transformations: static area/current vs simulation speed.
    alpha=4
    np.testing.assert_allclose(loop(s,ip=ip/alpha,r=r*alpha,c1=c1/alpha,c2=c2/alpha),l,rtol=1e-12)
    for scale in [300/8,300/16,300/32,300/64]:
        np.testing.assert_allclose(loop(s*scale,n=n/scale,c1=c1/scale,c2=c2/scale),l,rtol=1e-12)
    # Scale-frequency integration makes ideal noise scaling explicit.
    base_ref_phase=2*1e-17*n*n*abs(h)**2
    base_cp_phase=cp_phase_one_sided(n,100e6)*abs(h)**2
    ref_variance=integrate(base_ref_phase,f)
    cp_variance=integrate(base_cp_phase,f)
    scale=37.5
    hs=loop(s*scale,n=n/scale,c1=c1/scale,c2=c2/scale)
    hs=hs/(1+hs)
    scaled_ref=integrate(2*1e-17*(n/scale)**2*abs(hs)**2,f*scale)
    scaled_cp=integrate(cp_phase_one_sided(n/scale,100e6*scale)*abs(hs)**2,f*scale)
    np.testing.assert_allclose(scaled_ref/ref_variance,1/scale,rtol=1e-12)
    np.testing.assert_allclose(scaled_cp/cp_variance,1,rtol=1e-12)
    jitter_conversion=lambda variance:math.sqrt(variance)/(2*np.pi*30e9)*1e15
    source_projection={str(nn):jj*math.sqrt(300/nn) for nn,jj in [(8,41),(16,47),(32,60),(64,90)]}
    RESULTS['pll']=dict(natural_frequency_MHz=wn/(2*np.pi)/1e6,damping=damping,
        second_order_bandwidth_MHz=factor*wn/(2*np.pi)/1e6,
        full_filter_bandwidth_MHz=f3/1e6,unity_frequency_MHz=fu/1e6,phase_margin_deg=pm,
        third_pole_MHz=(c1+c2)/(2*np.pi*r*c1*c2)/1e6,
        source_eq8_multiplier_error=4*np.pi**2,
        source_ideal_jitter_fs=math.sqrt(8*n*n*1e-17*6e6)/(2*np.pi*30e9)*1e15,
        reference_output_floor_dBc=10*math.log10(n*n*1e-17),
        source_cp_eq12_atN8_dB=10*math.log10(cp_phase_one_sided(8,3.75e9)),
        consistent_one_sided_to_SSB_cp_atN8_dBc=10*math.log10(cp_phase_one_sided(8,3.75e9)/2),
        ideal_wide_band_reference_jitter_fs=jitter_conversion(ref_variance),
        ideal_wide_band_cp_jitter_fs=jitter_conversion(cp_variance),
        ref_variance_scaling=scaled_ref/ref_variance,cp_variance_scaling=scaled_cp/cp_variance,
        article_sqrtK_projections_fs=source_projection,
        nominal_steps_500ns_at5ps=500e-9/5e-12,
        spur_ripple_peak_mV_for_minus50_at100MHz=2*100e6/2.08e9*10**(-50/20)*1e3)
    fig,axes=plt.subplots(2,2,figsize=(12,8))
    for cc in [.1e-12,.5e-12,3.04e-12]:
        ll=loop(s,c2=cc)
        axes[0,0].semilogx(f/1e6,20*np.log10(abs(ll/(1+ll))),label=f'C2 = {cc*1e12:g} pF')
    axes[0,0].set(xlim=(.1,200),ylim=(-30,8),xlabel='Offset frequency (MHz)',ylabel='Normalized reference transfer (dB)',title='Complete passive filter: ripple pole changes response')
    axes[0,0].legend(fontsize=8)
    for nn in [300,64,32,16,8]:
        kk=300/nn
        ll=loop(s,n=nn,c1=c1/kk,c2=c2/kk)
        axes[0,1].semilogx(f/1e6,20*np.log10(abs(ll/(1+ll))),label=f'N = {nn}')
    axes[0,1].set(xlim=(.1,2000),ylim=(-30,5),xlabel='Offset frequency (MHz)',ylabel='Normalized reference transfer (dB)',title='Ideal loop scaling; no fixed parasitic C')
    axes[0,1].legend(fontsize=8)
    scales=np.linspace(1,37.5,200)
    axes[1,0].plot(scales,jitter_conversion(ref_variance)/np.sqrt(scales),label='Fixed white reference phase PSD')
    axes[1,0].plot(scales,np.full_like(scales,jitter_conversion(cp_variance)),label='CP: fixed reset width, duty-aware noise')
    axes[1,0].set(xlabel='Simulation speed scale K',ylabel='RMS jitter (fs)',title='Ideal white sources have different scaling laws')
    axes[1,0].legend(fontsize=8)
    axes[1,1].plot([8,16,32,64],[source_projection[str(nn)] for nn in [8,16,32,64]],'o-')
    axes[1,1].axhline(200,color='gray',linestyle=':',label='Source target')
    axes[1,1].set(xlabel='Source scaled-loop divide ratio',ylabel='Source √K extrapolation (fs)',title='Reported source jitter is not a full-loop validation')
    axes[1,1].legend(fontsize=8)
    save(fig,'millimeter_wave_pll_models.png')


def main():
    OUT.mkdir(exist_ok=True)
    vco_models()
    divider_models()
    pll_models()
    print(json.dumps(RESULTS,indent=2))
    print('VCO switch/charge, divider Boolean, filter KCL and loop/noise scaling checks passed.')


if __name__=='__main__':
    main()
