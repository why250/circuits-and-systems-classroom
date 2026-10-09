"""Independent metric checks and per-section plots for the educational 5T OTA.

Called by run_5t_ota.py; simulations are performed by ngspice, not by this module.
"""
import re

import matplotlib.pyplot as plt
import numpy as np

EXTRA_DECKS = ("ac-output-resistance", "ac-psrr-positive", "ac-psrr-negative", "noise", "bias-sweep", "poles-zeros")
HEADERS = {
    "ac-output-resistance": "frequency_Hz,Zout_real_ohm,Zout_imag_ohm",
    "ac-psrr-positive": "frequency_Hz,Asplus_real,Asplus_imag",
    "ac-psrr-negative": "frequency_Hz,Asminus_real,Asminus_imag",
    "noise": "frequency_Hz,output_V_sqrtHz,input_V_sqrtHz,M1_output_V_sqrtHz,M2_output_V_sqrtHz,M3_output_V_sqrtHz,M4_output_V_sqrtHz,M5_output_V_sqrtHz",
    "bias-sweep": "VB_V,OUT_V,X_V,Y_V,I_VDD_A,M1_margin_V,M2_margin_V,M3_margin_V,M4_margin_V,M5_margin_V",
}


def kcl_matrix(devices):
    a, b, p, q, t = (devices[f"m{i}"] for i in range(1, 6))
    ka, kb = a["gm"]+a["gmbs"]+a["gds"], b["gm"]+b["gmbs"]+b["gds"]
    return np.array([[a["gds"]+p["gds"]+p["gm"], 0, -ka],
                     [q["gm"], b["gds"]+q["gds"], -kb],
                     [-a["gds"], -b["gds"], ka+kb+t["gds"]]])


def supply_kcl(devices, vdd, vss):
    """[Y, OUT, X] response, with VINP/VINN/VB fixed to external ground."""
    a, b, p, q, t = (devices[f"m{i}"] for i in range(1, 6))
    rhs = [(p["gm"]+p["gds"])*vdd-a["gmbs"]*vss,
           (q["gm"]+q["gds"])*vdd-b["gmbs"]*vss,
           (a["gmbs"]+b["gmbs"]+t["gm"]+t["gds"])*vss]
    return np.linalg.solve(kcl_matrix(devices), rhs)


def complex_gain(data):
    return data[:, 1]+1j*data[:, 2]


def pz_transfer(f, poles, zeros, gain):
    s = 2j*np.pi*f
    result = np.full(f.shape, gain, dtype=complex)
    for zero in zeros:
        result *= 1-s/zero
    for pole in poles:
        result /= 1-s/pole
    return result


def cumulative_variance(f, density):
    power = density**2
    return np.r_[0, np.cumsum(np.diff(f)*(power[1:]+power[:-1])/2)]


def check_metrics(data, logs, summary, capacitances):
    """Reject inconsistent acquisition; record approximations without forcing agreement."""
    dm, cm = data["ac-differential"], data["ac-common-mode"]
    f, adm, acm = dm[:, 0], complex_gain(dm), complex_gain(cm)
    devices = summary["device_parameters"]
    d = devices["m1"]
    p = devices["m3"]
    gt = devices["m5"]["gds"]
    k = d["gm"]+d["gmbs"]+d["gds"]
    denominator = 2*k*(p["gm"]+p["gds"])+gt*(p["gm"]+p["gds"]+d["gds"])
    exact_cm = -d["gm"]*gt/denominator
    exact_x = 2*d["gm"]*(p["gm"]+p["gds"])/denominator
    if not np.allclose([acm[0].real, cm[0, 3]], [exact_cm, exact_x], rtol=1e-5):
        raise ValueError("Matched common-mode formulas disagree with AC")
    impedance = data["ac-output-resistance"]
    rout = np.linalg.solve(kcl_matrix(devices), [0, 1, 0])[1]
    if not np.array_equal(f, impedance[:, 0]) or not np.isclose(impedance[0, 1], rout, rtol=2e-5):
        raise ValueError("Output current injection disagrees with independent KCL")
    supplies = {}
    for suffix, unit in (("positive", (1, 0)), ("negative", (0, 1))):
        wave = data[f"ac-psrr-{suffix}"]
        if not np.array_equal(f, wave[:, 0]):
            raise ValueError("PSRR frequency grids differ")
        observed = complex_gain(wave)[0].real
        predicted = supply_kcl(devices, *unit)[1]
        if not np.isclose(observed, predicted, rtol=2e-5):
            raise ValueError(f"{suffix} supply AC/KCL mismatch")
        supplies[suffix] = {"supply_gain_V_per_V": float(observed),
                            "independent_kcl_V_per_V": float(predicted),
                            "psrr_dB": float(20*np.log10(abs(adm[0]/observed)))}

    noise = data["noise"]
    if not np.array_equal(f, noise[:, 0]) or np.any(noise[:, 1:3] <= 0):
        raise ValueError("Noise acquisition is incomplete")
    if not np.allclose(noise[:, 1]/abs(adm), noise[:, 2], rtol=2e-5):
        raise ValueError("Input noise normalization is not differential voltage gain")
    if not np.allclose(np.sum(noise[:, 3:]**2, axis=1), noise[:, 1]**2, rtol=2e-5):
        raise ValueError("Independent MOS noise powers do not sum to total")
    # MOS1 saturation channel thermal noise: Si = 4 kT (2/3) gm, one-sided.
    boltzmann, temperature, gamma = 1.380649e-23, 300.15, 2/3
    injections = np.array([[1, 0, -1], [0, 1, -1], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    current_to_out = np.linalg.solve(kcl_matrix(devices), injections.T)[1]
    channel_psd = 4*boltzmann*temperature*gamma*np.array([devices[f"m{i}"]["gm"] for i in range(1, 6)])
    expected_components = abs(current_to_out)*np.sqrt(channel_psd)
    if not np.allclose(noise[0, 3:], expected_components, rtol=2e-4):
        raise ValueError("Noise spectra disagree with independent current-noise KCL")
    approximate_psd = (8*boltzmann*temperature*gamma/d["gm"]
                       + 8*boltzmann*temperature*gamma*p["gm"]/d["gm"]**2)
    band = (f >= 10) & (f <= 100e3)
    variance = cumulative_variance(f[band], noise[band, 2])[-1]
    output_variance = cumulative_variance(f[band], noise[band, 1])[-1]

    # PZ uses rad/s; preserve complex roots and their signs.
    roots = {kind: [] for kind in ("pole", "zero")}
    for kind, real, imag in re.findall(r"(pole|zero)\(\d+\)\s*=\s*([-+\d.eE]+),\s*([-+\d.eE]+)", logs["poles-zeros"]):
        roots[kind].append(complex(float(real), float(imag)))
    poles, zeros = (np.array(roots[kind]) for kind in ("pole", "zero"))
    if len(poles) != 3 or len(zeros) != 3 or np.any(poles.real >= 0):
        raise ValueError("Unexpected or unstable PZ transfer")
    pole_order = np.argsort(abs(poles))
    zero_order = np.argsort(abs(zeros))
    poles, zeros = poles[pole_order], zeros[zero_order]
    reconstructed = pz_transfer(f, poles, zeros, summary["independent_kcl"]["differential_Y_OUT_X"][1])
    relative_error = float(np.max(abs(reconstructed-adm)/abs(adm)))
    if relative_error > 2e-4:
        raise ValueError("Extracted PZ transfer does not reconstruct differential AC")

    # Ground other nodes for these scalar capacitance estimates. Cgd3 cancels
    # because its gate and drain share Y. Coupling prevents an exact pole formula.
    caps = capacitances
    cy = caps["m3"]["cgs"]+caps["m4"]["cgs"]+caps["m4"]["cgd"]+caps["m1"]["cgd"]
    co = 1e-12+caps["m2"]["cgd"]+caps["m4"]["cgd"]
    wo = (devices["m2"]["gds"]+devices["m4"]["gds"])/co
    wy = p["gm"]/cy
    tau = -1/poles[0].real
    tran = data["transient"]
    rising_end = 5.01e-6
    mask = (tran[:, 0] >= rising_end) & (tran[:, 0] < 24e-6)
    times, output = tran[mask, 0]-rising_end, tran[mask, 2]
    final = float(np.mean(tran[(tran[:, 0] > 20e-6) & (tran[:, 0] < 24e-6), 2]))
    movement = final-summary["operating_point"]["out_V"]
    error = abs(output-final)/abs(movement)
    settling = {}
    for label, fraction in (("1_percent", .01), ("0_1_percent", .001)):
        outside = np.flatnonzero(error > fraction)
        if not len(outside) or outside[-1]+1 >= len(times):
            raise ValueError(f"Cannot establish {label} open-loop settling")
        settling[label] = {"ngspice_s": float(times[outside[-1]+1]),
                           "dominant_pole_s": float(tau*np.log(1/fraction))}
        if not np.isclose(settling[label]["ngspice_s"], settling[label]["dominant_pole_s"], rtol=.01):
            raise ValueError(f"{label} small-step settling disagrees with dominant pole")
    bias = data["bias-sweep"]
    margins = bias[:, 5:10]
    active = np.all(margins > 0, axis=1)
    tail_theory = .5*200e-6*(8/1)*(bias[:, 0]-.45)**2*(1+.03*bias[:, 2])
    if not np.allclose(-bias[active, 4], tail_theory[active], rtol=2e-5):
        raise ValueError("Saturated tail current disagrees with MOS1 square-law expression")
    boundary = np.flatnonzero(margins[:, 4] <= 0)

    result = {
        "output_resistance": {"ngspice_ohm": float(impedance[0, 1]), "independent_kcl_ohm": float(rout),
                              "ro2_parallel_ro4_ohm": float(1/(devices["m2"]["gds"]+devices["m4"]["gds"]))},
        "matched_common_mode_formula": {"Acm_V_per_V": float(exact_cm), "X_gain_V_per_V": float(exact_x)},
        "psrr_reference": "VINP, VINN, VB, output and CL fixed to external ground; excite one rail at a time",
        "psrr_at_1Hz": supplies,
        "noise": {"convention": "one-sided voltage amplitude densities; differential input reference; KF defaults to zero",
                  "input_density_1Hz_V_sqrtHz": float(noise[0, 2]),
                  "leading_order_density_V_sqrtHz": float(np.sqrt(approximate_psd)),
                  "kcl_density_V_sqrtHz": float(np.linalg.norm(expected_components)/abs(adm[0])),
                  "band_Hz": [10, 100000], "integrated_input_rms_V": float(np.sqrt(variance)),
                  "integrated_output_rms_V": float(np.sqrt(output_variance)),
                  "white_noise_input_rms_V": float(np.sqrt(approximate_psd*(100000-10))),
                  "MOS_output_density_1Hz_V_sqrtHz": noise[0, 3:].tolist()},
        "capacitances_F": caps,
        "pole_zero": {"poles_rad_per_s": [[float(z.real), float(z.imag)] for z in poles],
                      "zeros_rad_per_s": [[float(z.real), float(z.imag)] for z in zeros],
                      "PZ_AC_max_relative_error": relative_error,
                      "scalar_CY_F": float(cy), "scalar_CO_F": float(co),
                      "output_pole_approx_Hz": float(wo/(2*np.pi)),
                      "mirror_pole_approx_Hz": float(wy/(2*np.pi)),
                      "mirror_zero_approx_Hz": float(2*wy/(2*np.pi)),
                      "dominant_tau_s": float(tau)},
        "open_loop_small_step_settling": {"reference": "time after 10 ns rising edge completes; relative to DC output movement",
                                          "final_OUT_V": final, **settling},
        "bias_sweep": {"VB_range_V": [float(bias[0, 0]), float(bias[-1, 0])],
                       "first_sample_tail_not_saturated_V": float(bias[boundary[0], 0]) if len(boundary) else None},
    }
    summary["checks"].extend(["matched common-mode formulas", "output current injection vs KCL", "positive/negative supply KCL vs AC",
        "differential noise referral and uncorrelated source power sum", "MOS1 thermal noise vs independent KCL",
        "full PZ transfer reconstructs complex AC", "saturated bias-sweep square law",
        "1% and 0.1% small-step settling vs dominant pole"])
    return result


def plot_metrics(data, summary, folder):
    """Each figure pairs raw SPICE evidence with an identified analytic model."""
    metrics = summary["metrics"]
    dm, cm, dc, tran, bias, noise = (data[name] for name in (
        "ac-differential", "ac-common-mode", "dc-transfer", "transient", "bias-sweep", "noise"))
    f, adm, acm = dm[:, 0], complex_gain(dm), complex_gain(cm)
    gain = summary["differential_gain_V_per_V"]
    op = summary["operating_point"]
    devices = summary["device_parameters"]
    names = [f"m{i}" for i in range(1, 6)]
    pz = metrics["pole_zero"]
    wo, wy = 2*np.pi*pz["output_pole_approx_Hz"], 2*np.pi*pz["mirror_pole_approx_Hz"]
    s = 2j*np.pi*f
    reduced = gain*(1+s/(2*wy))/((1+s/wo)*(1+s/wy))
    def save(fig, name):
        for ax in fig.axes:
            ax.grid(True, alpha=.22)
        fig.suptitle("Five-transistor OTA | educational LEVEL=1 | ngspice", fontsize=12)
        fig.savefig(folder/f"{name}.png", dpi=160)
        fig.savefig(folder/f"{name}.svg")
        plt.close(fig)
    def db(z):
        return 20*np.log10(abs(z))
    def phase(z):
        return np.unwrap(np.angle(z))*180/np.pi

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    ax = axes[0, 0]
    for col, label in ((1, "OUT / Y"), (2, "X")):
        ax.plot(bias[:, 0], bias[:, col], label=label)
    ax.axvline(.65, color="grey", ls=":")
    ax.set(xlabel="VB (V)", ylabel="Node voltage (V)", title="Balanced-input bias"); ax.legend()
    ax = axes[0, 1]
    ax.plot(bias[:, 0], -bias[:, 4]*1e6, label="ngspice tail current")
    valid = bias[:, 9] > 0
    theory = .5*200e-6*8*(bias[:, 0]-.45)**2*(1+.03*bias[:, 2])
    ax.plot(bias[valid, 0], theory[valid]*1e6, "--", label="Saturation square law")
    ax.set(xlabel="VB (V)", ylabel="Tail current (uA)", title="P = VDD x Itail; nominal 58.04 uW"); ax.legend()
    power = ax.secondary_yaxis("right", functions=(lambda x: x*1.8, lambda x: x/1.8))
    power.set_ylabel("Supply power (uW)")
    ax = axes[1, 0]
    for i, label in ((5, "M1 / M2"), (7, "M3 / M4"), (9, "M5 tail")):
        ax.plot(bias[:, 0], bias[:, i], label=label)
    ax.axhline(0, color="black", ls=":")
    ax.set(xlabel="VB (V)", ylabel="|VDS| - |VDSsat| (V)", title="Saturation margin; positive means saturated"); ax.legend()
    ax = axes[1, 1]
    ix = np.arange(5)
    for offset, param, label in ((-.25, "gm", "gm"), (0, "gmbs", "gmb"), (.25, "gds", "gds")):
        ax.bar(ix+offset, [devices[n][param]*1e6 for n in names], width=.25, label=label)
    ax.set(yscale="log", ylabel="OP conductance (uS)", title="Parameters used in independent KCL", xticks=ix, xticklabels=[n.upper() for n in names]); ax.legend()
    save(fig, "bias")

    fig, grid = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    axes = grid.ravel()
    axes[0].semilogx(f, db(adm), label="ngspice")
    axes[0].axhline(db(summary["gm_Rout_approximation_V_per_V"]), ls="--", color="orange", label="gm Rout (DC)")
    axes[0].axvline(summary["bandwidth_3dB_Hz"], ls=":", color="grey", label="-3 dB")
    axes[0].axvline(summary["unity_gain_frequency_Hz"], ls=":", color="purple", label="Unity gain")
    axes[0].set(xlabel="Frequency (Hz)", ylabel="Gain (dB)", title="Differential gain", xlim=(1, 1e9)); axes[0].legend(fontsize=8)
    axes[1].semilogx(f, phase(adm))
    axes[1].set(xlabel="Frequency (Hz)", ylabel="Phase (deg)", title="Differential phase", xlim=(1, 1e9))
    axes[2].plot(dc[:, 0]*1e3, dc[:, 3], label="ngspice DC")
    mid = abs(dc[:, 0]) <= 2e-3
    axes[2].plot(dc[mid, 0]*1e3, op["out_V"]+gain*dc[mid, 0], "--", label="OP + Adm x vd")
    axes[2].set(xlabel="VINP - VINN (mV)", ylabel="OUT (V)", title="Local slope and compression"); axes[2].legend(fontsize=8)
    axes[3].loglog(f, abs(complex_gain(data["ac-output-resistance"])), label="ngspice OUT current injection")
    axes[3].axhline(metrics["output_resistance"]["ro2_parallel_ro4_ohm"], ls="--", color="orange", label="ro2 || ro4 (DC)")
    axes[3].set(xlabel="Frequency (Hz)", ylabel="|Zout| (ohm)", title="Output impedance, CL = 1 pF", xlim=(1, 1e9)); axes[3].legend(fontsize=8)
    save(fig, "differential")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)
    axes[0].semilogx(f, db(acm), label="OUT")
    axes[0].semilogx(f, db(cm[:, 5]+1j*cm[:, 6]), "--", label="Y")
    axes[0].axhline(db(metrics["matched_common_mode_formula"]["Acm_V_per_V"]), ls=":", color="black", label="Matched LF formula")
    axes[0].set(xlabel="Frequency (Hz)", ylabel="Magnitude (dB)", title="Common-mode output / mirror"); axes[0].legend(fontsize=8)
    axes[1].semilogx(f, abs(cm[:, 3]+1j*cm[:, 4]), label="ngspice X")
    axes[1].axhline(metrics["matched_common_mode_formula"]["X_gain_V_per_V"], ls="--", label="Exact LF formula")
    a = devices["m1"]
    axes[1].axhline(a["gm"]/(a["gm"]+a["gmbs"]), ls=":", color="black", label="gm / (gm + gmb)")
    axes[1].set(xlabel="Frequency (Hz)", ylabel="|X / VCM| (V/V)", title="Tail follows common mode"); axes[1].legend(fontsize=8)
    axes[2].semilogx(f, db(adm/acm))
    axes[2].axhline(summary["cmrr_dB"], ls=":", color="grey")
    axes[2].set(xlabel="Frequency (Hz)", ylabel="CMRR (dB)", title=f"CMRR at 1 Hz: {summary['cmrr_dB']:.2f} dB")
    save(fig, "common-mode")

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
    for suffix, label in (("positive", "+"), ("negative", "-")):
        transfer = complex_gain(data[f"ac-psrr-{suffix}"])
        line, = axes[0].semilogx(f, db(transfer), label=f"As{label}")
        axes[0].axhline(db(metrics["psrr_at_1Hz"][suffix]["independent_kcl_V_per_V"]), color=line.get_color(), ls=":")
        rejection = metrics["psrr_at_1Hz"][suffix]["psrr_dB"]
        axes[1].semilogx(f, db(adm/transfer), label=f"PSRR{label}: {rejection:.2f} dB at 1 Hz")
    axes[0].set(xlabel="Frequency (Hz)", ylabel="Supply gain magnitude (dB)", title="OUT referred to ground; dotted lines: DC KCL"); axes[0].legend()
    axes[1].set(xlabel="Frequency (Hz)", ylabel="Input-referred PSRR (dB)", title="Fixed ground-referenced VINP, VINN and VB"); axes[1].legend()
    save(fig, "psrr")

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.3), constrained_layout=True)
    axes[0].loglog(f, noise[:, 1]*1e9, label="Output")
    axes[0].loglog(f, noise[:, 2]*1e9, label="Differential input")
    axes[0].axhline(metrics["noise"]["leading_order_density_V_sqrtHz"]*1e9, color="black", ls=":", label="LF formula")
    axes[0].set(xlabel="Frequency (Hz)", ylabel="Density (nV / sqrt(Hz))", title="Thermal noise; KF = 0"); axes[0].legend(fontsize=8)
    axes[1].bar(np.arange(5), noise[0, 3:]**2/abs(adm[0])**2*1e18)
    axes[1].set(yscale="log", xticks=np.arange(5), xticklabels=[n.upper() for n in names], ylabel="Input-referred PSD (nV^2/Hz)", title="Uncorrelated channel contributions at 1 Hz")
    band = (f >= 10) & (f <= 100e3)
    rms = np.sqrt(cumulative_variance(f[band], noise[band, 2]))
    axes[2].semilogx(f[band], rms*1e6, label="Integrated ngspice PSD")
    axes[2].semilogx(f[band], np.sqrt(metrics["noise"]["leading_order_density_V_sqrtHz"]**2*(f[band]-10))*1e6, "--", label="sqrt(Svin x bandwidth)")
    axes[2].set(xlabel="Upper integration limit (Hz); lower = 10 Hz", ylabel="Input RMS (uV)", title="10 Hz-100 kHz input noise"); axes[2].legend(fontsize=8)
    save(fig, "noise")

    poles = np.array([complex(*z) for z in pz["poles_rad_per_s"]])
    zeros = np.array([complex(*z) for z in pz["zeros_rad_per_s"]])
    reconstructed = pz_transfer(f, poles, zeros, gain)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    for response, style, label in ((adm, "-", "ngspice AC"), (reconstructed, "--", "Full ngspice PZ reconstruction"), (reduced, ":", "Two-pole / one-zero approximation")):
        axes[0].semilogx(f, db(response), style, label=label)
        axes[1].semilogx(f, phase(response), style, label=label)
    axes[0].axvline(pz["mirror_pole_approx_Hz"], color="grey", ls=":")
    axes[0].set(xlabel="Frequency (Hz)", ylabel="Gain (dB)", title="Mirror approximation and the full linearized circuit"); axes[0].legend()
    axes[1].set(xlabel="Frequency (Hz)", ylabel="Phase (deg)", title="High-frequency feedthrough adds poles and zeros"); axes[1].legend()
    save(fig, "dynamics")

    fig, ax = plt.subplots(figsize=(11, 4.7), constrained_layout=True)
    roots = list(poles)+list(zeros)
    labels = [f"P{i+1}" for i in range(3)]+[f"Z{i+1}" for i in range(3)]
    for i, (root, label) in enumerate(zip(roots, labels)):
        color = "tab:red" if root.real > 0 else ("tab:blue" if label[0] == "P" else "tab:orange")
        ax.plot([0, root.real], [i, i], color=color, alpha=.4)
        ax.scatter(root.real, i, color=color, marker="x" if label[0] == "P" else "o", s=60)
        ax.annotate(f"{abs(root)/(2*np.pi):.4g} Hz ({'RHP' if root.real > 0 else 'LHP'})", (root.real, i), xytext=(-8 if root.real > 0 else 8, 7), ha="right" if root.real > 0 else "left", textcoords="offset points", fontsize=9)
    ax.axvline(0, color="black", lw=.8)
    ax.set_xscale("symlog", linthresh=1e5)
    ax.set(xlabel="Real part of s (rad/s), symmetric logarithmic scale",
           yticks=np.arange(6), yticklabels=labels, ylim=(-.5, 5.7),
           title="ngspice PZ roots: imaginary parts are zero; x = pole, o = zero",
           xlim=(-1e12, 1e12), xticks=[-1e12, -1e10, -1e8, -1e6, 0, 1e6, 1e8, 1e10, 1e12])
    save(fig, "poles-zeros")

    fig, axes = plt.subplots(2, 1, figsize=(10, 7), constrained_layout=True)
    tau = pz["dominant_tau_s"]
    final = metrics["open_loop_small_step_settling"]["final_OUT_V"]
    movement = final-op["out_V"]
    mask = (tran[:, 0] >= 5.01e-6) & (tran[:, 0] < 24e-6)
    t = tran[mask, 0]-5.01e-6
    output = tran[mask, 2]
    prediction = op["out_V"]+100e-6*gain*(1-np.exp(-(t+5e-9)/tau))
    axes[0].plot(t*1e6, (output-op["out_V"])*1e3, label="ngspice")
    axes[0].plot(t*1e6, (prediction-op["out_V"])*1e3, "--", label="Adm vd (1-exp(-t/tau))")
    axes[0].set(xlabel="Time after rising edge (us)", ylabel="Output movement (mV)", title="100 uV differential open-loop step", xlim=(0, 9)); axes[0].legend()
    axes[1].semilogy(t*1e6, np.maximum(abs(output-final)/abs(movement), 1e-9), label="ngspice, final value from plateau")
    axes[1].semilogy(t*1e6, np.exp(-(t+5e-9)/tau), "--", label="Dominant-pole prediction")
    for label, fraction in (("1_percent", .01), ("0_1_percent", .001)):
        ts = metrics["open_loop_small_step_settling"][label]["ngspice_s"]
        axes[1].axhline(fraction, color="grey", ls=":")
        axes[1].axvline(ts*1e6, ls=":", label=f"{fraction*100:g}%: {ts*1e6:.3f} us")
    axes[1].set(xlabel="Time after rising edge (us)", ylabel="Error / final output movement", ylim=(1e-5, 1), xlim=(0, 9), title="Small-signal settling, distinct from closed-loop settling or slew rate"); axes[1].legend(fontsize=8)
    save(fig, "settling")
