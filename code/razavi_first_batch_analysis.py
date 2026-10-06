"""Independent analytical checks for the first three Analog Mind topic notes.

Requires NumPy and Matplotlib. No PDK, SPICE, or measured data is used.
Figures: comparator probability/timing models and z-domain filter models.
"""

from pathlib import Path
import math
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
NORMAL = NormalDist()


def alias_frequency(frequency, sample_rate):
    return (frequency + sample_rate / 2) % sample_rate - sample_rate / 2


def fir_response(coefficients, omega):
    coefficients = np.asarray(coefficients)
    return np.exp(-1j * np.outer(omega, np.arange(len(coefficients)))) @ coefficients


def accumulator(inputs, alpha):
    outputs = np.empty_like(inputs, dtype=float)
    previous = 0.0
    for k, value in enumerate(inputs):
        previous = alpha * previous + value
        outputs[k] = previous
    return outputs


def check_sampler():
    k_b = 1.380649e-23
    temperature = 348.0
    delta_rounded, delta_exact = 1e-3, 1 / 1024
    loss_db = 1.0
    c_rounded = 24 * k_b * temperature / (delta_rounded**2 * (10 ** (loss_db / 10) - 1))
    c_exact = 24 * k_b * temperature / (delta_exact**2 * (10 ** (loss_db / 10) - 1))
    c_selected = 0.5e-12
    attenuation_db = 0.5
    nyquist = 2.5e9
    r_limit = math.sqrt(10 ** (attenuation_db / 10) - 1) / (2 * math.pi * nyquist * c_selected)
    attenuation = 10 * math.log10(1 + (2 * math.pi * nyquist * r_limit * c_selected) ** 2)
    assert math.isclose(attenuation, attenuation_db, rel_tol=1e-12)
    assert c_selected > c_exact > c_rounded
    sample_rate, record, cycles = 5e9, 4096, 2023
    assert math.gcd(record, cycles) == 1
    phase_indices = cycles * np.arange(record, dtype=np.int64) % record
    assert len(np.unique(phase_indices)) == record
    assert math.isclose(alias_frequency(3 * 2.47e9, sample_rate), 2.41e9)
    bins = [min((h * cycles) % record, record - (h * cycles) % record) for h in range(1, 6)]
    assert len(set(bins)) == len(bins)
    print(f"Sampler: 1-dB noise budget C/side = {c_rounded * 1e15:.2f} fF (rounded LSB), {c_exact * 1e15:.2f} fF (exact LSB)")
    print(f"Sampler: 0.5-dB attenuation Ron limit = {r_limit:.2f} ohm")
    print(f"Sampler: coherent input = {cycles / record * sample_rate / 1e9:.9f} GHz; {record} input phases; bins h1..h5 = {bins}")


def comparator_models():
    sigma_offset_mv = math.sqrt(4.4**2 + 1.5**2 + 0.9**2)
    yield_fraction = 2 * NORMAL.cdf(5 / sigma_offset_mv) - 1
    tau_ps = 5.7 / math.log(10)
    probability = NORMAL.cdf(1)
    standard_error = math.sqrt(probability * (1 - probability) / 100)
    # Verify independent two-point offset/noise extraction against a nonzero-offset model.
    offset, sigma = 0.20e-3, 0.31e-3
    points = np.array([-0.05e-3, 0.45e-3])
    probs = [NORMAL.cdf((point - offset) / sigma) for point in points]
    inferred_sigma = (points[1] - points[0]) / (NORMAL.inv_cdf(probs[1]) - NORMAL.inv_cdf(probs[0]))
    inferred_offset = points[0] - inferred_sigma * NORMAL.inv_cdf(probs[0])
    assert math.isclose(inferred_sigma, sigma, rel_tol=1e-12)
    assert math.isclose(inferred_offset, offset, rel_tol=1e-12)
    print(f"Comparator: RSS offset sigma = {sigma_offset_mv:.4f} mV; Gaussian +/-5 mV yield = {100 * yield_fraction:.2f}%")
    print(f"Comparator: regeneration tau from decade shift = {tau_ps:.4f} ps; SE(p) at 100 trials = {standard_error:.4f}")

    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.6), layout="constrained")
    area_ratio = np.linspace(0.5, 8, 250)
    # Illustrative single dominant mismatch component, not full StrongARM resizing.
    axes[0].plot(area_ratio, 4.4 / np.sqrt(area_ratio), color="#2b6cb0")
    axes[0].set(xlabel="Input-pair area / initial area", ylabel="Mismatch sigma (mV)", title="Single-component area law")
    axes[0].text(0.05, 0.05, "Fixed mismatch coefficient\nOther pairs/parasitics excluded", transform=axes[0].transAxes, fontsize=9)
    magnitudes = np.logspace(-2, 0, 200)  # mV
    delays = 22 + tau_ps * np.log(1 / magnitudes)
    axes[1].semilogx(magnitudes, delays, color="#c05621")
    axes[1].scatter([1, 0.1, 0.01], [22, 27.7, 33.4], color="#276749", zorder=3)
    axes[1].set(xlabel="Input magnitude (mV)", ylabel="Illustrative crossing time (ps)", title="Regeneration time shift")
    axes[1].text(0.05, 0.05, "22 ps at 1 mV; 5.7 ps/decade\nLocal exponential model", transform=axes[1].transAxes, fontsize=9)
    inputs_mv = np.linspace(-1.2, 1.2, 300)
    for offset_mv, label in [(0, "Zero offset"), (0.20, "Offset = 0.20 mV")]:
        axes[2].plot(inputs_mv, [NORMAL.cdf((v - offset_mv) / 0.31) for v in inputs_mv], label=label)
    axes[2].axhline(0.5, color="#7b8794", ls=":")
    axes[2].set(xlabel="Differential input (mV)", ylabel="Probability of decision 1", title="Gaussian decision model")
    axes[2].legend(fontsize=8)
    for axis in axes:
        axis.grid(alpha=0.18)
    fig.suptitle("StrongARM design intuition — independent analytical models", fontsize=14)
    fig.supxlabel("Illustrative scaling and probability curves; source timing values are not a reproduced PDK simulation.", fontsize=9)
    fig.savefig(FIGURES / "strongarm_comparator_models.png", dpi=170)
    plt.close(fig)


def z_models():
    omega = np.linspace(0, math.pi, 1201)
    low = fir_response([1, 1], omega)
    difference = fir_response([1, -1], omega)
    bandpass = fir_response([1, -1, -1, 1], omega)
    np.testing.assert_allclose(np.abs(low), 2 * np.abs(np.cos(omega / 2)), atol=1e-14)
    np.testing.assert_allclose(np.abs(difference), 2 * np.abs(np.sin(omega / 2)), atol=1e-14)
    np.testing.assert_allclose(bandpass, difference**2 * low, atol=1e-14)
    steps = np.ones(32)
    np.testing.assert_allclose(accumulator(steps, 0.9), (1 - 0.9 ** (np.arange(32) + 1)) / 0.1)
    np.testing.assert_allclose(accumulator(steps, 1), np.arange(32) + 1)

    # Independently implement the source's delaying-integrator feedback topology.
    rng = np.random.default_rng(20261004)
    signal = rng.normal(size=128)
    error = rng.normal(size=128)
    state = 0.0
    output = np.empty(128)
    for k in range(128):
        state += (signal[k - 1] - output[k - 1]) if k else 0.0
        output[k] = state + error[k]
    expected = np.r_[0, signal[:-1]] + error - np.r_[0, error[:-1]]
    np.testing.assert_allclose(output, expected, atol=2e-14)

    osr = 64
    omega_band = math.pi / osr
    integration_grid = np.linspace(-omega_band, omega_band, 10001)
    numeric_noise = np.trapezoid(4 * np.sin(integration_grid / 2) ** 2, integration_grid) / (2 * math.pi)
    exact_noise = 2 / math.pi * (omega_band - math.sin(omega_band))
    approximation = math.pi**2 / (3 * osr**3)
    assert math.isclose(numeric_noise, exact_noise, rel_tol=3e-8)
    assert math.isclose(approximation, exact_noise, rel_tol=2e-4)
    print(f"z-domain: OSR 64 in-band white-error variance / sigma_E^2 = {exact_noise:.9g}")
    print("z-domain: frequency identities, accumulator recurrences, and independent feedback STF/NTF checks passed.")

    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.1), layout="constrained")
    frequency = omega / (2 * math.pi)
    for coeff, label in [([0.5, 0.5], "2-sample average"), ([1 / 3] * 3, "3-sample average"), ([1, -1], "First difference")]:
        axes[0, 0].plot(frequency, np.abs(fir_response(coeff, omega)), label=label)
    axes[0, 0].set(xlabel="Frequency / sample rate", ylabel="Magnitude", title="Delayed copies: averaging and differencing")
    axes[0, 0].legend(fontsize=8)
    axes[0, 1].plot(frequency, np.abs(bandpass), color="#c05621")
    axes[0, 1].set(xlabel="Frequency / sample rate", ylabel="Magnitude", title="[1, -1, -1, 1]: both endpoint zeros")
    for alpha in [0.9, 0.98, 1.0]:
        axes[1, 0].plot(np.arange(32), accumulator(steps, alpha), label=f"alpha = {alpha}")
    axes[1, 0].set(xlabel="Sample index", ylabel="Response to unit step", title="Leak limits accumulator growth")
    axes[1, 0].legend(fontsize=8)
    z_inv = np.exp(-1j * omega[1:])
    for alpha in [1.0, 0.9]:
        ntf = (1 - alpha * z_inv) / (1 + (1 - alpha) * z_inv)
        axes[1, 1].semilogx(frequency[1:], 20 * np.log10(np.abs(ntf)), label=f"Integrator alpha = {alpha}")
    axes[1, 1].set(xlabel="Frequency / sample rate", ylabel="Noise-transfer magnitude (dB)", title="Leak changes the complete loop NTF")
    axes[1, 1].legend(fontsize=8)
    for axis in axes.flat:
        axis.grid(alpha=0.18)
    fig.suptitle("Discrete-time design models — derived from explicit coefficients and states", fontsize=14)
    fig.savefig(FIGURES / "z_transform_models.png", dpi=170)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    print("Analytical checks only; no transistor simulation or measurement.")
    check_sampler()
    comparator_models()
    z_models()
    print(f"Figures saved under {FIGURES}")


if __name__ == "__main__":
    main()
