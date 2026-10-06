"""Reproduce the illustrative analytical models in Bootstrapped-Sampling-Switch.md.

Requires NumPy and Matplotlib. This is not SPICE or a PDK simulation.
"""

from pathlib import Path
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


VDD = 1.2  # V
VT0 = 0.35  # V
GAMMA_BODY = 0.40  # sqrt(V)
TWO_PHI = 0.70  # V
BETA = 5.0e-3  # A/V^2
CB = 2.0e-12  # F
CPG = 0.10e-12  # F, fixed-ground loading, initially discharged
CS = 1.0e-12  # F
R_SOURCE = 50.0  # ohm
TEMPERATURE = 300.0  # K
K_B = 1.380649e-23  # J/K
BITS = 12
FULL_SCALE = 1.0  # V, defines LSB/initial error; input sweep ends at 0.9 V


def threshold(vin, gamma=GAMMA_BODY):
    return VT0 + gamma * (np.sqrt(TWO_PHI + vin) - math.sqrt(TWO_PHI))


def bootstrap_vgs(vin, cb=CB, cpg=CPG):
    alpha = cb / (cb + cpg)
    return alpha * VDD - (1.0 - alpha) * vin


def on_resistance(vgs, vt):
    """Local small-VDS triode approximation, undefined below positive overdrive."""
    overdrive = np.asarray(vgs) - vt
    resistance = np.full_like(overdrive, np.nan, dtype=float)
    np.divide(1.0, BETA * overdrive, out=resistance, where=overdrive > 0)
    return resistance


def main():
    vin = np.linspace(0.0, 0.9, 361)
    np.testing.assert_allclose(bootstrap_vgs(vin, cpg=0.0), VDD)
    constant_ron = on_resistance(bootstrap_vgs(vin, cpg=0.0), threshold(vin, gamma=0.0))
    np.testing.assert_allclose(constant_ron, 1.0 / (BETA * (VDD - VT0)))

    vgs = bootstrap_vgs(vin)
    vt = threshold(vin)
    ron = on_resistance(vgs, vt)
    if not np.all(np.isfinite(ron)):
        raise ValueError("Example requires positive overdrive across the input range")

    worst_ron = float(np.max(ron))
    tau = (R_SOURCE + worst_ron) * CS
    target_fraction = 1.0 / 2 ** (BITS + 1)
    settling = (BITS + 1) * math.log(2.0) * tau
    if not math.isclose(math.exp(-settling / tau), target_fraction, rel_tol=1e-12):
        raise AssertionError("Half-LSB settling identity failed")
    sigma = math.sqrt(K_B * TEMPERATURE / CS)
    lsb = FULL_SCALE / 2**BITS
    max_input = float(vin[-1])
    allowed_loss = 0.10  # V
    cb_min = CPG * ((VDD + max_input) / allowed_loss - 1)

    print("Analytical model only; no PDK or transistor-level simulation.")
    print(f"alpha = {CB / (CB + CPG):.6f}")
    print(f"At Vin = {max_input:.2f} V: VGS = {vgs[-1]:.4f} V, VT = {vt[-1]:.4f} V")
    print(f"Worst local Ron = {worst_ron:.2f} ohm; tau = {tau * 1e9:.4f} ns")
    print(f"Frozen-R half-LSB settling = {settling * 1e9:.4f} ns")
    print(f"Minimum CB for 0.10 V modeled loss = {cb_min * 1e12:.4f} pF")
    print(f"RC thermal noise = {sigma * 1e6:.4f} uV RMS = {sigma / lsb:.4f} LSB RMS")
    print("Analytical invariants passed: ideal bootstrap, zero-body-effect Ron, settling target.")

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), layout="constrained")
    axes[0].plot(vin, VDD - vin, label="Conventional gate = VDD", color="#7b8794")
    axes[0].plot(vin, np.full_like(vin, VDD), label="Ideal bootstrap", color="#2b6cb0")
    axes[0].plot(vin, vgs, label="Finite CB + ground loading", color="#c05621")
    axes[0].plot(vin, vt, "--", label="Threshold with body effect", color="#276749")
    axes[0].set(xlabel="Input voltage (V)", ylabel="Voltage (V)", title="Gate drive and threshold")
    axes[0].legend(fontsize=8)

    axes[1].plot(vin, constant_ron, label="Ideal, no body effect", color="#7b8794")
    axes[1].plot(vin, on_resistance(VDD, vt), label="Ideal + body effect", color="#2b6cb0")
    axes[1].plot(vin, ron, label="Finite CB + body effect", color="#c05621")
    axes[1].set(xlabel="Input voltage (V)", ylabel="Local on-resistance (ohm)", title="Small-VDS resistance")
    axes[1].legend(fontsize=8)

    times = np.linspace(0, 5e-9, 501)
    axes[2].semilogy(times * 1e9, np.exp(-times / tau), color="#c05621", label="Frozen worst local resistance")
    axes[2].axhline(target_fraction, ls="--", color="#2b6cb0", label="12-bit half-LSB / full-scale")
    axes[2].axvline(settling * 1e9, ls=":", color="#276749", label=f"{settling * 1e9:.2f} ns")
    axes[2].set(xlabel="Acquisition time (ns)", ylabel="Error / initial error", title="Local first-order settling")
    axes[2].legend(fontsize=8)
    for axis in axes:
        axis.grid(True, alpha=0.18)
    fig.suptitle("Bootstrapped sampling switch — illustrative analytical model", fontsize=15)
    fig.supxlabel("Hypothetical parameters; driver dynamics, extracted parasitics and device stress require transistor-level validation.", fontsize=9)

    output = Path(__file__).resolve().parents[1] / "figures" / "bootstrapped_switch_analysis.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=170)
    plt.close(fig)
    print(f"Figure: {output}")


if __name__ == "__main__":
    main()
