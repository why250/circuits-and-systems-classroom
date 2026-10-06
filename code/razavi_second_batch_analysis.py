"""Analytical checks and figures for four Analog Mind building-block notes.

NumPy/Matplotlib only. Models are explicit approximations, not PDK simulations.
Run from any working directory; figures are written relative to this file.
"""
from pathlib import Path
from statistics import NormalDist
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
KB, QE = 1.380649e-23, 1.602176634e-19
RESULTS = {}


def finish(fig, filename):
    fig.tight_layout()
    fig.savefig(FIGURES / filename, dpi=170)
    plt.close(fig)


def bandgap():
    r1, r3, rl, n = 2e3, 13e3, 5.5e3, 16
    a, b = r3 / r1, rl / r3
    temp = np.linspace(273.15, 373.15, 401)
    vbe = .75 - 1.5e-3 * (temp - 298.15)  # illustrative linear model
    delta = KB * temp / QE * np.log(n)
    current = delta / r1 + vbe / r3
    out = b * (vbe + a * delta)
    np.testing.assert_allclose(current * rl, out)
    np.testing.assert_allclose(current - vbe / r3, delta / r1)
    ideal_a = 1.5e-3 / (KB / QE * np.log(n))
    offset_gain = b * (1 + a)
    f = np.logspace(4, 9, 700)
    s = 2j * np.pi * f
    ca = cb = 1e-12
    r = rl
    transfer = rl / (1 + s * (rl*ca + rl*cb + r*cb) + s*s*rl*r*ca*cb)
    # Solve the physical two-node network, independently of its polynomial.
    direct = np.array([np.linalg.solve(
        [[1/rl + z*ca + 1/r, -1/r], [-1/r, 1/r + z*cb]], [1, 0]
    )[1] for z in s])
    np.testing.assert_allclose(transfer, direct, rtol=1e-12)
    poles = np.sort(np.abs(np.roots([rl*r*ca*cb, rl*ca+rl*cb+r*cb, 1]))) / (2*np.pi)
    RESULTS["bandgap"] = dict(current_25C_uA=float(np.interp(298.15,temp,current))*1e6,
        output_25C_V=float(np.interp(298.15,temp,out)), cancellation_ratio=ideal_a,
        offset_gain=offset_gain, offset_1p7mV_output_mV=offset_gain*1.7,
        filter_poles_MHz=(poles/1e6).tolist())
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(temp-273.15, out*1e3, label="R3/R1 = 6.5")
    axes[0].plot(temp-273.15, b*(vbe+ideal_a*delta)*1e3, "--", label="Linear cancellation")
    axes[0].set(xlabel="Temperature (°C)", ylabel="Output (mV)", title="Illustrative VBE model; no curvature/PDK")
    axes[0].legend()
    axes[1].semilogx(f/1e6, 20*np.log10(np.abs(transfer/rl)), label="Unbuffered network")
    buffered = 1/(1+s*rl*ca)**2
    axes[1].semilogx(f/1e6, 20*np.log10(np.abs(buffered)), "--", label="Two isolated RC stages")
    axes[1].set(xlabel="Frequency (MHz)", ylabel="Normalized gain (dB)", title="RL = R = 5.5 kΩ; Ca = Cb = 1 pF")
    axes[1].legend()
    for ax in axes: ax.grid(True, alpha=.3)
    finish(fig, "low_voltage_bandgap_models.png")


def ldo():
    foff, khz, lbase = 1e6, 50e6, 10**(-110/10)
    ladded = (10**.1 - 1) * lbase
    article_asd = math.sqrt(ladded) * foff/khz
    onesided_asd = math.sqrt(2*ladded) * foff/khz
    ripple = 2*10**(-60/20) * 10e6 / (khz*.01)
    # AC plant KCL with independent supply feedthrough and feedback.
    gm, go, gl, cl, beta, gain, ha = .05, 1e-3, .005, .5e-12, .9, 120-45j, .1+.02j
    s = 2j*np.pi*10e6
    zp = 1/(gl+go+s*cl)
    t = beta*gain*gm*zp
    feed = (gm*zp*(1-ha)+go*zp)/(1+t)
    gate, output = np.linalg.solve([[1, -gain*beta], [gm, 1/zp]], [ha, gm+go])
    np.testing.assert_allclose(output, feed)
    iq = .2e-3
    RESULTS["ldo"] = dict(article_noise_nV=article_asd*1e9,
        declared_one_sided_noise_nV=onesided_asd*1e9, ripple_peak_mV=ripple*1e3,
        illustrative_efficiency=1*.005/(1.2*(.005+iq)),
        capacitance_only_10mV_delay_ps=.5e-12*.01/.005*1e12)
    f = np.logspace(4, 8, 600)
    asd = 20e-9
    # Illustrative supply-sensitive oscillator, open loop, one-sided Sv.
    ladd = .5*(khz/f)**2 * asd**2
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].semilogx(f, 10*np.log10(ladd))
    axes[0].set(xlabel="Offset frequency (Hz)", ylabel="Added SSB phase noise (dBc/Hz)",
        title="20 nV/√Hz white supply noise; KDD = 50 MHz/V")
    vin = 1.2
    iload = np.linspace(.01e-3, .005, 400)
    for q in [0, .2e-3, .5e-3]:
        axes[1].plot(iload*1e3, iload/(vin*(iload+q))*100, label=f"IQ = {q*1e3:g} mA")
    axes[1].set(xlabel="Load current (mA)", ylabel="Efficiency (%)", title="Vin = 1.2 V; Vout = 1 V")
    axes[1].legend()
    for ax in axes: ax.grid(True, alpha=.3)
    finish(fig, "ldo_regulator_models.png")


def tia():
    rf, ro, a = 1e3, 1e3, 3.9
    rin = (rf+ro)/(1+a)
    zt = (ro-a*rf)/(1+a)
    np.testing.assert_allclose(zt, rin-rf)
    # KCL at input and output, current input = 1 A for normalization.
    vp, vo = np.linalg.solve([[1/rf, -1/rf], [a/ro-1/rf, 1/ro+1/rf]], [1,0])
    np.testing.assert_allclose([vp,vo], [rin,zt])
    qarg = -NormalDist().inv_cdf(1e-12)
    sigma = 25e-6/(2*qarg)
    bw = 20e9
    f = np.logspace(3, 15, 60000)
    trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    enbw = trap(1/(1+(f/bw)**2), f)
    assert abs(enbw/(np.pi*bw/2)-1) < 2e-5
    # NRZ baseband fraction: integral sinc^2 from -B/Rb to +B/Rb.
    fractions = {}
    for ratio in [.5, .7]:
        x = np.linspace(-ratio, ratio, 100001)
        fractions[str(ratio)] = float(trap(np.sinc(x)**2, x))
    noise_pre = math.sqrt(1.8e-6)/(800*math.sqrt(np.pi/2*19e9))
    noise_final = math.sqrt(1.3e-6)/(800*math.sqrt(np.pi/2*17e9))
    RESULTS["tia"] = dict(rin_A3p9_ohm=rin, zt_A3p9_ohm=zt, required_unloaded_gain=(rf+ro)/200-1,
        gaussian_q=qarg, sigma_current_uA=sigma*1e6,
        target_white_ASD_pA=sigma/math.sqrt(np.pi/2*bw)*1e12,
        nrz_power_fractions=fractions, preliminary_equivalent_ASD_pA=noise_pre*1e12,
        final_equivalent_ASD_pA=noise_final*1e12,
        ac_coupling_tau_100bits_ns=-(100/40e9)/math.log(.99)*1e9)
    f = np.logspace(7, 12, 650)
    s = 2j*np.pi*f
    rf, cin, a0 = 1e3, 75e-15, 20
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for fa in [1e9, 4e9, 16e9]:
        wa = 2*np.pi*fa
        h = -a0*rf/((1+a0)+s*(1/wa+rf*cin)+s*s*rf*cin/wa)
        amp = a0/(1+s/wa)
        direct = np.array([np.linalg.solve([[z*cin+1/rf,-1/rf],[av,1]],[1,0])[1]
            for z,av in zip(s,amp)])
        np.testing.assert_allclose(h,direct,rtol=1e-12)
        axes[0].semilogx(f/1e9, 20*np.log10(np.abs(h)), label=f"Amplifier pole = {fa/1e9:g} GHz")
    axes[0].set(xlabel="Frequency (GHz)", ylabel="Transimpedance (dBΩ)", title="A0 = 20; RF = 1 kΩ; Cin = 75 fF; Ro = 0")
    axes[0].legend(fontsize=8)
    x = np.linspace(.1, 5, 600)
    axes[1].plot(x, np.sqrt(4*KB*348.15/(x*1e3))*1e12)
    axes[1].set(xlabel="Feedback resistance (kΩ)", ylabel="Current ASD (pA/√Hz)", title="Feedback resistor alone; T = 348 K")
    for ax in axes: ax.grid(True, alpha=.3)
    finish(fig, "transimpedance_amplifier_models.png")


def bw_ratio(q, stages=1):
    d = 2**(1/stages)
    return math.sqrt((2-1/q**2 + math.sqrt((1/q**2-2)**2+4*(d-1)))/2)


def biquad():
    r1, r2, r3, rf, c1, c2, a0 = 500, 2000, 2000, 2000, 8e-12, 8e-12, 10
    a = (a0+1)**2*r1*r2*r3*rf*c1*c2
    b = (r2*rf+r1*r2+(a0+1)*r1*rf)*(a0+1)*r3*c2+(a0+1)*r1*r2*rf*c1
    c = r2*rf+r1*r2+(a0+1)*r1*rf+(a0+1)**2*r1*r2
    wn, q = math.sqrt(c/a), math.sqrt(a*c)/b
    f = np.logspace(4, 9, 500)
    s = 2j*np.pi*f
    source_approx = r2*rf*a0*a0/(a*s*s+b*s+c)
    c_exact = r2*rf+r1*r2+(a0+1)*r1*rf+a0*a0*r1*r2
    finite = r2*rf*a0*a0/(a*s*s+b*s+c_exact)
    # Differential KCL with crossed RF feedback; e is first top-minus-bottom output.
    def kcl(z, gain):
        first = -1/(gain*r1)-(1+1/gain)*(1/r2+z*c1)-1/(gain*rf)
        return np.linalg.solve([[first,1/rf],[1,1/gain+(1+1/gain)*r3*z*c2]], [1/r1,0])[1]
    np.testing.assert_allclose(finite, [kcl(z,a0) for z in s], rtol=1e-12)
    wn_ideal = 1/math.sqrt(r3*rf*c1*c2)
    qideal = r2*math.sqrt(c1/(r3*rf*c2))
    ideal = (rf/r1)*wn_ideal**2/(s*s+s*wn_ideal/qideal+wn_ideal**2)
    # State matrix directly follows conservation, independent of polynomial.
    state = np.array([np.linalg.solve([[z*c1+1/r2,1/rf],[-1/r3,z*c2]], [1/r1,0])[1] for z in s])
    np.testing.assert_allclose(ideal, state, rtol=1e-12)
    coef1 = (1+r1/rf+r1/r2)**2
    coef2 = (r1/r2)**2
    nf_asd = math.sqrt(4*KB*375*50*10**(30/10)*(10**(4/10)-10**(3.8/10)))
    RESULTS["biquad"] = dict(finite_gain_fn_MHz=wn/(2*np.pi)/1e6, finite_gain_Q=q,
        finite_gain_f3dB_MHz=wn*bw_ratio(q)/(2*np.pi)/1e6,
        exact_KCL_fn_MHz=math.sqrt(c_exact/a)/(2*np.pi)/1e6,
        exact_KCL_Q=math.sqrt(a*c_exact)/b,
        exact_KCL_f3dB_MHz=math.sqrt(c_exact/a)*bw_ratio(math.sqrt(a*c_exact)/b)/(2*np.pi)/1e6,
        cascade_ratio_Q1=bw_ratio(1,2)/bw_ratio(1),
        cascade_ratio_Butterworth=bw_ratio(1/math.sqrt(2),2),
        noise_weights=[coef1,coef2], front_end_noise_budget_nV=nf_asd*1e9,
        resistance_noise_1k_differential_nV=math.sqrt(8*KB*348.15*1000)*1e9)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].semilogx(f/1e6,20*np.log10(np.abs(ideal)),label="Ideal opamps")
    axes[0].semilogx(f/1e6,20*np.log10(np.abs(finite)),label="A0 = 10; Ro = 0")
    axes[0].semilogx(f/1e6,20*np.log10(np.abs(source_approx)),"--",label="Source large-A0 approximation")
    axes[0].set(xlim=(.1,100),ylim=(-35,16),xlabel="Frequency (MHz)",ylabel="Gain (dB)",title="TT biquad: RF/R1 = 4; C1 = C2 = 8 pF")
    axes[0].legend()
    x = np.logspace(-2,1,650)
    for q in [1/math.sqrt(2),1]:
        h = 1/(1-x*x+1j*x/q)
        for stages in [1,2]:
            axes[1].semilogx(x,20*stages*np.log10(np.abs(h)), label=f"Q = {q:.3g}, {stages} stage(s)")
    axes[1].axhline(-3.0103,color="gray",linestyle=":")
    axes[1].set(xlim=(.1,3),ylim=(-20,4),xlabel="Frequency / natural frequency",ylabel="Gain relative to DC (dB)",title="Identical stages; cascade bandwidth depends on Q")
    axes[1].xaxis.set_major_locator(FixedLocator([.1,.2,.5,1,2,3]))
    axes[1].xaxis.set_major_formatter(FixedFormatter(["0.1","0.2","0.5","1","2","3"]))
    axes[1].xaxis.set_minor_formatter(NullFormatter())
    axes[1].legend(fontsize=8)
    for ax in axes: ax.grid(True, alpha=.3)
    finish(fig, "tow_thomas_biquad_models.png")


def main():
    FIGURES.mkdir(exist_ok=True)
    bandgap()
    ldo()
    tia()
    biquad()
    print(json.dumps(RESULTS, indent=2))
    print("All independent KCL, state-equation and integration checks passed.")


if __name__ == "__main__":
    main()
