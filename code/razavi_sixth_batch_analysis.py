"""Independent ideal-model checks for the CMOS inverter applications series.

No PDK or source transistor waveforms are reproduced. Outputs are relative to
this script, and all frequencies in calculations are Hz or rad/s as stated.
"""
from pathlib import Path
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'figures'


def close(a, b):
    np.testing.assert_allclose(a, b, rtol=1e-9, atol=1e-12)


def active_z(s, gm, go, rf, c):
    return (1 + rf * (go + s*c)) / (gm + go + s*c)


def ctle(s, g1, g2, g3, g4, c):
    return -(g1*g4 + s*c*(g1+g3)) / (g2*g4 + s*c*(g2+g4))


def amplifier(s, gm, conductance, caps, rm, cm, gmff=0):
    y = s*cm/(1+s*rm*cm)
    g1,g2,g3=conductance
    c1,c2,c3=caps
    a=np.array([[g1+s*c1+y,-y,0],
                [gm[1]-y,g2+s*c2+y,0],
                [0,gm[2],g3+s*c3]],dtype=complex)
    return np.linalg.solve(a,[-gm[0],0,-gmff])[2]


def main():
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.grid':True,'grid.alpha':.3})
    gm,ro,rf=.044,90.,500.
    rin=(rf+ro)/(1+gm*ro)
    close(rin,118.9516129032258)
    # Feedback input impedance checked by solving the output-node KCL.
    for f in np.geomspace(1e4,1e11,61):
        s=2j*np.pi*f; go=1/ro; c=20e-15
        vy=-(gm-1/rf)/(go+s*c+1/rf)
        close(1/((1-vy)/rf),active_z(s,gm,go,rf,c))
    # Signal and output-current noise solved separately in a two-node LNA.
    rs=50.; gf=1/rf; gs=1/rs; go=1/ro
    matrix=np.array([[gs+gf,-gf],[gm-gf,go+gf]])
    hv=np.linalg.solve(matrix,[gs,0])[1]
    hi=np.linalg.solve(matrix,[0,1])[1]
    close(abs(hi/hv),(1+rs/rf)/(gm-gf))
    # Four-transconductor CTLE: capacitor links the two output nodes.
    g1,g2,g3,g4,c=.001,.003,.008,.002,25e-15
    for f in np.geomspace(1e3,1e12,61):
        s=2j*np.pi*f
        v=np.linalg.solve([[g2+s*c,-s*c],[-s*c,g4+s*c]],[-g1,-g3])
        close(v[0],ctle(s,g1,g2,g3,g4,c))
    wz=g1*g4/((g1+g3)*c); wp=g2*g4/((g2+g4)*c)
    boost=(g1+g3)*g2/((g2+g4)*g1)
    close(wp/wz,boost)
    # Compensation MNA versus independent capacitor-state equations.
    gm3=np.array([.004,.004,.004]); gs3=np.array([.0005]*3)
    caps=np.array([50e-15,50e-15,500e-15]); rm=600.; cm=1e-12
    state=np.array([[-(gs3[0]+1/rm)/caps[0],1/(rm*caps[0]),0,1/(rm*caps[0])],
                    [(-gm3[1]+1/rm)/caps[1],-(gs3[1]+1/rm)/caps[1],0,-1/(rm*caps[1])],
                    [0,-gm3[2]/caps[2],-gs3[2]/caps[2],0],
                    [1/(rm*cm),-1/(rm*cm),0,-1/(rm*cm)]])
    inp=np.array([-gm3[0]/caps[0],0,0,0])
    for f in np.geomspace(1e3,1e12,61):
        s=2j*np.pi*f
        v=np.linalg.solve((s*np.eye(4)-state)/1e10,inp/1e10)[2]
        close(v,amplifier(s,gm3,gs3,caps,rm,cm))
    # Pierce active port impedance: enforce one ampere between A and B.
    gc=.01; c1=c2=10e-12; w=2*np.pi*25e6
    z=1/(1j*w*c1)+1/(1j*w*c2)+gc/((1j*w)**2*c1*c2)
    va=1/(1j*w*c1); vb=(-1-gc*va)/(1j*w*c2)
    close(va-vb,z)
    ls,cs,cp,rser=.0126,3.4e-15,1.2e-12,20.
    fs=1/(2*np.pi*np.sqrt(ls*cs)); fp=fs*np.sqrt(1+cs/cp)
    # Ring scaling and supply-to-phase integration in the flicker model.
    n=3.; close((1/n)**2/n,1/n**3)
    # Discrete charge transfer versus explicit sharing of capacitor charges.
    cx,cy,fck,vdd=100e-15,2e-12,100e6,.25
    a=cy/(cx+cy); v=0.; history=[v]
    for _ in range(100):
        v=(cy*v+cx*2*vdd)/(cx+cy); history.append(v)
    close(history,2*vdd*(1-a**np.arange(101)))
    tau_exact=-1/(2*fck*np.log(a)); tau_approx=cy/(2*fck*cx)
    # SC integrator finite-gain equations stamped for a retained ideal C3.
    c_s=c_f=.2e-12; gain=8.; charge_state=.1; vi=.02
    # charge_state=-Q_old/C_f is retained charge-equivalent voltage, not old output.
    # C_s(vx+vi)+C_f(vx-vo)= -C_f*charge_state, vo=-gain*vx.
    mat=np.array([[c_s+c_f,-c_f],[gain,1]])
    vx,vo=np.linalg.solve(mat,[-c_f*charge_state-c_s*vi,0])
    close(vo,(charge_state+(c_s/c_f)*vi)/(1+(1+c_s/c_f)/gain))
    # Independently retained C_f charge reproduces the previous-output recurrence.
    previous=.1; charge_state=(1+1/gain)*previous; ratio=c_s/c_f
    vx,vo=np.linalg.solve(mat,[-c_f*charge_state-c_s*vi,0])
    leak=(1+1/gain)/(1+(1+ratio)/gain)
    step=ratio/(1+(1+ratio)/gain)
    close(vo,leak*previous+step*vi)
    # FIA endpoint gain from time-varying gm and output conductance.
    cl=.2e-12; t=np.linspace(0,2e-9,2001); gm0=.001
    gt=gm0*np.exp(-t/.4e-9); gd=gt/10
    gain_dyn=0.; gains=[]
    for g,d in zip(gt,gd):
        gains.append(gain_dyn)
        dt=t[1]-t[0]
        # Exact propagation for coefficients frozen during this short interval.
        gain_dyn=gain_dyn*np.exp(-d*dt/cl)+(g/d)*(1-np.exp(-d*dt/cl))
    integrated=10*(1-np.exp(-gm0*.4e-9*(1-np.exp(-t/.4e-9))/(10*cl)))
    np.testing.assert_allclose(gains,integrated,atol=.006,rtol=.003)
    # Sampled white-noise kernel versus constant-coefficient state covariance.
    # One-sided S_i corresponds to (S_i/2)*delta(t-t') in time covariance.
    g_noise=.0001; si=4e-24; window=2e-9
    tn=np.linspace(0,window,20001)
    variance_integral=np.trapezoid(si*np.exp(-2*g_noise*(window-tn)/cl),tn)/(2*cl**2)
    variance_state=si/(4*g_noise*cl)*(1-np.exp(-2*g_noise*window/cl))
    np.testing.assert_allclose(variance_integral,variance_state,rtol=1e-8)
    for correlation in [0.,.5,1.]:
        covariance=np.array([[1.,correlation],[correlation,1.]])
        weight=np.array([.5,.5])
        close(weight@covariance@weight,(1+correlation)/2)
    # PAM4 KCL including the matched channel load.
    levels=[]
    for bmsb,blsb in [(0,0),(0,1),(1,0),(1,1)]:
        vs=(bmsb/(1.5*50)+blsb/(3*50))/(1/(1.5*50)+1/(3*50)+1/50)
        levels.append(vs)
    close(levels,np.arange(4)/6)
    # Matched SST bridge energy versus resistor dissipation at a fixed bit.
    vv=.95; z0=50.; iss=vv/(4*z0)
    close(vv*iss,iss**2*(4*z0))
    # Class-D differential voltage and power reconstructed from two legs.
    amp_leg=.375; p_diff=(2*amp_leg)**2/(2*8)
    close(p_diff,.03515625)
    # Equal-slope phase mixing checks the skew attenuation model.
    r_drive=50.; r_equal=20.; skew_ratio=r_equal/(r_equal+2*r_drive)
    v1,v2=np.linalg.solve([[1/r_drive+1/r_equal,-1/r_equal],[-1/r_equal,1/r_drive+1/r_equal]],[1/r_drive,0])
    close(v1-v2,skew_ratio)
    # CP duty lock: derivative has correct restoring sign.
    iup,idn=50e-6,50e-6; kdv=-.2; cc=.5e-12
    lock=iup/(iup+idn); pole=-(iup+idn)*kdv/cc
    assert pole>0; close(lock,.5)
    ambiguity=.5/200; sigma=.01
    p_amb=math.erf(ambiguity/(np.sqrt(2)*sigma))
    # FFE pulse taps convolved with an illustrative symbol channel.
    pulse=np.array([1,.08,.03]); filt=np.array([1,-.08])
    close(np.convolve(pulse,filt),[1,0,.0236,-.0024])
    results={
        'LNA_Rin_44mS_90ohm_500ohm':rin,
        'LNA_RF_for_50ohm':50*(1+gm*ro)-ro,
        'CTLE_zero_GHz':wz/(2*np.pi*1e9),'CTLE_pole_GHz':wp/(2*np.pi*1e9),
        'CTLE_boost_dB':20*np.log10(boost),
        'Pierce_negative_series_ohm':float(z.real),
        'crystal_series_MHz':fs/1e6,'crystal_unloaded_parallel_MHz':fp/1e6,
        'crystal_parallel_equivalent_ohm':ls**2*w**2/rser,
        'pump_tau_exact_ns':tau_exact/1e-9,'pump_tau_approx_ns':tau_approx/1e-9,
        'pump_Rout_approx_kohm':1/(2*fck*cx)/1e3,
        'FIA_model_endpoint_gain':float(gains[-1]),
        'sampled_white_current_noise_variance_V2':float(variance_integral),
        'SC_integrator_state_retention':leak,'SC_integrator_input_coefficient':step,
        'FIA_source_energy_pJ':160e-6/100e6/1e-12,
        'PUF_ambiguity_mV':ambiguity*1e3,'PUF_ambiguity_probability':p_amb,
        'SST_static_bridge_mW':vv*iss*1e3,'CML_comparator_mW':vv**2/z0*1e3,
        'PAM4_levels_per_VDD':levels,
        'ClassD_750mVpp_differential_mW':.75**2/(8*8)*1e3,
        'ClassD_750mVpp_each_leg_mW':p_diff*1e3,
        'ClassD_reported_efficiency':35/45,
        'clock_full_swing_2x100fF_56GHz_mW':2*100e-15*56e9*vv**2*1e3,
        'TDC_signed_span_ps':6/7e9/1e-12,'TDC_full_signed_intervals':math.ceil((6/7e9)/1.4e-12),
        'TDC_magnitude_intervals':math.ceil((3/7e9)/1.4e-12),
        'DTC_430ps_units':math.ceil(430/.35),
        'DCC_180mV_offset_correction_ps':2*.18/(.95/10e-12)/1e-12,
        'DCC_restoring_rate_per_s':pole,'illustrative_skew_ratio':skew_ratio,
        'Npath_5p1GHz_quarter_period_ps':1/(4*5.1e9)/1e-12,
        'gyrator_380nanoohm_per_Hz_nH':380e-9/(2*np.pi)/1e-9,
    }
    f=np.geomspace(1e7,1e11,500); s=2j*np.pi*f
    fig,ax=plt.subplots(2,2,figsize=(11,8))
    for rout in [90,180]:ax[0,0].plot(np.linspace(0,1000,101),(np.linspace(0,1000,101)+rout)/(1+gm*rout),label=f'ro={rout} ohm')
    ax[0,0].axhline(50,color='gray',ls=':');ax[0,0].set(xlabel='Feedback resistance (ohm)',ylabel='Input resistance (ohm)',title='Finite output resistance matters');ax[0,0].legend()
    ax[0,1].semilogx(f/1e9,20*np.log10(abs(ctle(s,g1,g2,g3,g4,c))));ax[0,1].set(xlabel='Frequency (GHz)',ylabel='Gain (dB)',title='Ideal capacitor-bridge CTLE')
    for res in [0,600]:
        h=np.array([amplifier(x,gm3,gs3,caps,res,cm) for x in s]);ax[1,0].semilogx(f/1e9,20*np.log10(abs(h)),label=f'RM={res} ohm')
    ax[1,0].set(xlabel='Frequency (GHz)',ylabel='Gain (dB)',title='Illustrative compensated cascade');ax[1,0].legend()
    cneg=np.linspace(0,8,101);ax[1,1].plot(cneg,10-cneg*2);ax[1,1].axhline(0,color='red',ls=':');ax[1,1].set(xlabel='Cross-coupled capacitor (fF), gain=3',ylabel='Effective node capacitance (fF)',title='Cancellation can exceed the available load')
    fig.tight_layout();fig.savefig(FIG/'inverter_analog_models.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(2,2,figsize=(11,8))
    ns=np.arange(1,9);eff=(50/3)**(1/ns);ax[0,0].plot(ns,ns*eff,'o-');ax[0,0].set(xlabel='Number of buffer stages',ylabel='Normalized delay',title='50-fF load / 3-fF first gate; zero parasitic')
    nn=np.arange(1,11);ax[0,1].plot(nn,-20*np.log10(nn),label='Added capacitance');ax[0,1].plot(nn,-30*np.log10(nn),label='More stages / ideal area scaling');ax[0,1].set(xlabel='Frequency reduction factor',ylabel='Phase-noise change (dB)',title='Same power, ideal flicker scaling');ax[0,1].legend()
    count=np.arange(501)
    span_line=ax[1,0].plot(count,count*1.4,label='Nominal span',color='tab:blue')
    mismatch_axis=ax[1,0].twinx()
    mismatch_line=mismatch_axis.plot(count,.2*np.sqrt(count),label='Independent mismatch',color='tab:orange')
    mismatch_axis.set_ylabel('Mismatch (ps RMS)',color='tab:orange');mismatch_axis.grid(False)
    ax[1,0].set(xlabel='Vernier stages',ylabel='Nominal span (ps)',title='Resolution, span and cumulative errors')
    ax[1,0].legend(span_line+mismatch_line,[line.get_label() for line in span_line+mismatch_line],loc='upper left')
    tc=np.linspace(0,50e-9,501);ax[1,1].plot(tc/1e-9,.5+.1*np.exp(-pole*tc));ax[1,1].set(xlabel='Time (ns)',ylabel='Output high duty',title='Illustrative averaged duty-correction loop')
    fig.tight_layout();fig.savefig(FIG/'inverter_timing_models.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(2,2,figsize=(11,8))
    ax[0,0].plot(np.arange(101)/(2*fck)*1e9,history,label='Explicit charge sharing');ax[0,0].plot(np.arange(101)/(2*fck)*1e9,2*vdd*(1-np.exp(-np.arange(101)/(2*fck)/tau_approx)),ls='--',label='RC approximation');ax[0,0].set(xlabel='Time (ns)',ylabel='Unloaded doubler output (V)',title='Ideal clock-delivered charge');ax[0,0].legend()
    ax[0,1].plot(t/1e-9,gains);ax[0,1].axhline(10,color='gray',ls=':',label='Frozen gm/go');ax[0,1].set(xlabel='Amplification time (ns)',ylabel='Differential gain magnitude',title='FIA gain depends on the time window');ax[0,1].legend()
    ax[1,0].plot(np.arange(4),levels,'o-');ax[1,0].set(xlabel='Binary value',ylabel='Single-ended output / VDD',title='Loaded ideal PAM4 levels')
    freq=np.geomspace(1e6,1e11,500);err=.01;td=.5e-12;residual=abs(1-(1+err)*np.exp(-2j*np.pi*freq*td));ax[1,1].semilogx(freq/1e9,20*np.log10(residual));ax[1,1].set(xlabel='Frequency (GHz)',ylabel='Residual / local TX (dB)',title='Hybrid: 1% gain error and 0.5-ps skew')
    fig.tight_layout();fig.savefig(FIG/'inverter_charge_driver_models.png',dpi=180);plt.close(fig)
    print(json.dumps(results,indent=2))
    print('Independent KCL, capacitor-state, charge-sharing, timing, noise and power checks passed.')


if __name__=='__main__':main()
