"""Run the authored ngspice decks, check bias/linearization, and plot results.

Usage: python code/run_5t_ota.py --ngspice /path/to/ngspice
Requires numpy and matplotlib. All paths are relative to this script's repo.
"""

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from ota_5t_metrics import EXTRA_DECKS, HEADERS, check_metrics, plot_metrics

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "simulations" / "5t-ota"
FIGURES = ROOT / "figures" / "5t-ota"
DECKS = ("op", "ac-differential", "ac-common-mode", "dc-transfer", "transient")
ALL_DECKS = DECKS + EXTRA_DECKS
DEVICE_NAMES = ("m1", "m2", "m3", "m4", "m5")
PARAMETERS = ("id", "gm", "gds", "gmbs", "vgs", "vds", "von", "vdsat")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(executable, args, cwd):
    options = {}
    if os.name == "nt":
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = 0
        options.update(startupinfo=info, creationflags=subprocess.CREATE_NO_WINDOW)
    result = subprocess.run([executable, *args], cwd=cwd, capture_output=True,
                            text=True, timeout=60, **options)
    if result.returncode:
        raise RuntimeError(f"ngspice failed ({result.returncode}): {result.stderr}")
    return result


def load(path):
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    if not np.isfinite(data).all():
        raise ValueError(f"Nonfinite values in {path.name}")
    return data


def crossing(frequency, gain_db, level):
    indices = np.flatnonzero((gain_db[:-1] >= level) & (gain_db[1:] < level))
    if not len(indices):
        return None
    i = indices[0]
    return float(10 ** np.interp(level, gain_db[i:i+2][::-1],
                               np.log10(frequency[i:i+2])[::-1]))


def linearize(devices, vp, vn):
    """Independent DC KCL for [Y, OUT, X], with supply/bias AC grounded."""
    a, b, p, q, tail = (devices[name] for name in DEVICE_NAMES)
    ga, gb = a["gm"] + a["gmbs"], b["gm"] + b["gmbs"]
    matrix = np.array([
        [a["gds"] + p["gds"] + p["gm"], 0, -a["gds"] - ga],
        [q["gm"], b["gds"] + q["gds"], -b["gds"] - gb],
        [-a["gds"], -b["gds"], a["gds"] + b["gds"] + ga + gb + tail["gds"]],
    ])
    rhs = [-a["gm"] * vp, -b["gm"] * vn, a["gm"] * vp + b["gm"] * vn]
    return np.linalg.solve(matrix, rhs)


def validate_and_summarize(data, op, devices):
    dm, cm, dc, tran = (data[name] for name in DECKS[1:])
    if not np.array_equal(dm[:, 0], cm[:, 0]):
        raise ValueError("Differential/common-mode frequency grids differ")
    if dm.shape[0] < 700 or dc.shape[0] != 401 or tran.shape[0] < 2500:
        raise ValueError("Incomplete waveform acquisition")
    saturation = {}
    for name, device in devices.items():
        # ngspice MOS1 reports PMOS vdsat with a negative sign but normalized vds.
        margin = abs(device["vds"]) - abs(device["vdsat"])
        saturation[name] = margin
        if margin <= 0 or device["gm"] <= 0 or device["id"] <= 0:
            raise ValueError(f"{name} is not biased in conducting saturation")
    branch_sum = devices["m1"]["id"] + devices["m2"]["id"]
    if not np.isclose(branch_sum, devices["m5"]["id"], rtol=1e-5):
        raise ValueError("Tail/branch current balance failed")
    adm = dm[:, 1] + 1j * dm[:, 2]
    acm = cm[:, 1] + 1j * cm[:, 2]
    y_dm, out_dm, x_dm = linearize(devices, 0.5, -0.5)
    y_cm, out_cm, x_cm = linearize(devices, 1, 1)
    observed = [adm[0].real, acm[0].real, cm[0, 3], cm[0, 5]]
    predicted = [out_dm, out_cm, x_cm, y_cm]
    if not np.allclose(observed, predicted, rtol=2e-5, atol=1e-8):
        raise ValueError(f"KCL/AC mismatch: {observed} vs {predicted}")
    center = np.argmin(abs(dc[:, 0]))
    slope = (dc[center+1, 3] - dc[center-1, 3]) / (dc[center+1, 0] - dc[center-1, 0])
    if not np.isclose(slope, out_dm, rtol=0.01):
        raise ValueError("Differential DC slope disagrees with AC gain")
    plateau = tran[(tran[:, 0] > 12e-6) & (tran[:, 0] < 14e-6), 2]
    step_gain = (float(plateau.mean()) - op["out_V"]) / 100e-6
    if not np.isclose(step_gain, out_dm, rtol=0.02):
        raise ValueError("Small differential step disagrees with linear gain")
    gain_db = 20 * np.log10(abs(adm))
    approximate = devices["m1"]["gm"] / (devices["m2"]["gds"] + devices["m4"]["gds"])
    return {
        "operating_point": op,
        "device_parameters": devices,
        "saturation_margin_V": saturation,
        "differential_gain_V_per_V": float(adm[0].real),
        "differential_gain_dB": float(gain_db[0]),
        "common_mode_gain_V_per_V": float(acm[0].real),
        "cmrr_dB": float(20 * np.log10(abs(adm[0] / acm[0]))),
        "common_mode_tail_gain_V_per_V": float(cm[0, 3]),
        "common_mode_mirror_gain_V_per_V": float(cm[0, 5]),
        "bandwidth_3dB_Hz": crossing(dm[:, 0], gain_db, gain_db[0] - 3),
        "unity_gain_frequency_Hz": crossing(dm[:, 0], gain_db, 0),
        "gm_Rout_approximation_V_per_V": float(approximate),
        "dc_center_slope_V_per_V": float(slope),
        "transient_step_gain_V_per_V": step_gain,
        "independent_kcl": {"differential_Y_OUT_X": [float(v) for v in (y_dm, out_dm, x_dm)],
                            "common_mode_Y_OUT_X": [float(v) for v in (y_cm, out_cm, x_cm)]},
        "checks": ["five conducting saturated MOS devices", "tail current KCL",
                   "independent small-signal KCL including gmb and gds",
                   "DC center slope vs AC", "small open-loop step vs AC"],
    }


def plot(data):
    dm, cm, dc, tran = (data[name] for name in DECKS[1:])
    adm, acm = dm[:, 1] + 1j * dm[:, 2], cm[:, 1] + 1j * cm[:, 2]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    axes[0, 0].semilogx(dm[:, 0], 20*np.log10(abs(adm)), label="Differential")
    axes[0, 0].semilogx(cm[:, 0], 20*np.log10(abs(acm)), label="Common mode")
    axes[0, 0].set(xlabel="Frequency (Hz)", ylabel="Gain (dB)", title="Open-loop AC gain")
    axes[0, 0].legend()
    axes[0, 1].semilogx(dm[:, 0], np.unwrap(np.angle(adm))*180/np.pi)
    axes[0, 1].set(xlabel="Frequency (Hz)", ylabel="Phase (deg)", title="Differential phase")
    axes[1, 0].plot(dc[:, 0]*1e3, dc[:, 3])
    axes[1, 0].set(xlabel="VINP - VINN (mV)", ylabel="OUT (V)", title="Fixed 0.9 V common mode")
    axes[1, 1].plot(tran[:, 0]*1e6, tran[:, 2], label="Output")
    axes[1, 1].set(xlabel="Time (us)", ylabel="OUT (V)", title="100 uV differential input step")
    for ax in axes.flat:
        ax.grid(True, alpha=0.25)
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / "simulation.png", dpi=160)
    fig.savefig(FIGURES / "simulation.svg")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ngspice", default=os.environ.get("NGSPICE_BIN", "ngspice"))
    parser.add_argument("--simulator-label", default=None,
                        help="Optional provenance label if the Windows binary cannot print --version")
    args = parser.parse_args()
    executable = shutil.which(args.ngspice) or str(Path(args.ngspice).resolve())
    if not Path(executable).is_file():
        raise FileNotFoundError(f"ngspice not found: {executable}")
    # Publish only after all decks and independent checks pass.
    with tempfile.TemporaryDirectory(prefix="classroom-5t-ota-") as temp:
        work = Path(temp)
        sources = [*(LAB / f"{deck}.cir" for deck in ALL_DECKS), LAB / "ota-core.cir", LAB / "models.lib"]
        for source in sources:
            shutil.copy2(source, work / source.name)
        data, logs = {}, {}
        for deck in ALL_DECKS:
            run(executable, ["-b", "-o", f"{deck}.log", f"{deck}.cir"], work)
            log = (work / f"{deck}.log").read_text(errors="replace")
            if re.search(r"(?im)^\s*(?:error\b|fatal\b|doAnalyses:)|simulation\(s\) aborted", log):
                raise RuntimeError(f"{deck}: {log}")
            logs[deck] = log
            if deck != "poles-zeros":
                data[deck] = load(work / f"{deck}.dat")
        device_data = load(work / "devices.dat")[0, 1:]
        if len(device_data) != len(DEVICE_NAMES)*len(PARAMETERS):
            raise ValueError("Device parameter capture is incomplete")
        devices = {name: dict(zip(PARAMETERS, map(float, device_data[i*8:(i+1)*8])))
                   for i, name in enumerate(DEVICE_NAMES)}
        values = data["op"][0, 1:]
        op = dict(zip(("out_V", "X_V", "Y_V", "supply_current_A"), map(float, values)))
        op["power_W"] = -op["supply_current_A"]*1.8
        summary = validate_and_summarize(data, op, devices)
        cap_data = load(work / "capacitances.dat")[0, 1:]
        if len(cap_data) != 15:
            raise ValueError("Device capacitance capture is incomplete")
        caps = {name: dict(zip(("cgs", "cgd", "cgb"), map(float, cap_data[i*3:(i+1)*3])))
                for i, name in enumerate(DEVICE_NAMES)}
        flicker_op = load(work / "flicker-op.dat")
        if not np.allclose(flicker_op, data["op"], rtol=1e-8, atol=1e-12):
            raise ValueError("Flicker coefficients changed the operating point")
        model_data = load(work / "flicker-models.dat")[0, 1:]
        geometry_data = load(work / "flicker-geometry.dat")[0, 1:]
        if len(model_data) != 4 or len(geometry_data) != 10:
            raise ValueError("Flicker model/geometry capture is incomplete")
        # MOS1 in ngspice-33 accepts KF/AF but does not expose them via @model.
        # Read the executed deck; the independent source-PSD checks verify them.
        coefficients = {(name.upper(), parameter.upper()): float(value)
                        for name, parameter, value in re.findall(
                            r"(?im)^\s*altermod\s+(\w+)\s+(kf|af)\s*=\s*([-+\d.eE]+)\s*$",
                            (work / "noise-flicker.cir").read_text())}
        flicker_parameters = {
            "parameter_origin": "KF/AF from executed deck; TOX/LD and device W/L captured from ngspice OP",
            "models": {name: {"KF": coefficients[(name, "KF")], "AF": coefficients[(name, "AF")],
                              **dict(zip(("TOX_m", "LD_m"), map(float, model_data[i*2:(i+1)*2])))}
                       for i, name in enumerate(("NMOS_EDU", "PMOS_EDU"))},
            "geometry": {name: dict(zip(("W_m", "L_m"), map(float, geometry_data[i*2:(i+1)*2])))
                         for i, name in enumerate(DEVICE_NAMES)},
        }
        summary["metrics"] = check_metrics(data, logs, summary, caps, flicker_parameters)
        summary.update({
            "validation_date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
            "model": "Educational LEVEL=1, not a PDK",
            "conditions": {"VDD_V": 1.8, "VCM_V": 0.9, "VB_V": 0.65,
                           "CL_F": 1e-12, "temperature_C": 27},
            "simulator_label": args.simulator_label or "ngspice (see executable SHA-256)",
            "simulator_detected_version": sorted(set(re.findall(r"ngspice-([^\s]+) done", "\n".join(logs.values())))),
            "simulator_executable_sha256": digest(Path(executable)),
            "source_sha256": {source.name: digest(source) for source in sources},
            "script_sha256": {path.name: digest(path) for path in
                              (Path(__file__), Path(__file__).with_name("ota_5t_metrics.py"))},
        })
        results = LAB / "results"
        results.mkdir(exist_ok=True)
        headers = {
            "op": "scale_V,OUT_V,X_V,Y_V,I_VDD_A",
            "ac-differential": "frequency_Hz,Ad_real,Ad_imag",
            "ac-common-mode": "frequency_Hz,Acm_real,Acm_imag,X_gain_real,X_gain_imag,Y_gain_real,Y_gain_imag",
            "dc-transfer": "VDIFF_V,VINP_V,VINN_V,OUT_V",
            "transient": "time_s,VDIFF_V,OUT_V",
        }
        headers.update(HEADERS)
        for deck in ALL_DECKS:
            if deck != "poles-zeros":
                np.savetxt(results / f"{deck}.csv", data[deck], delimiter=",",
                           header=headers[deck], comments="", fmt="%.9e")
            (results / f"{deck}.log").write_text(logs[deck], encoding="utf-8")
        shutil.copy2(work / "devices.dat", results / "devices.dat")
        shutil.copy2(work / "capacitances.dat", results / "capacitances.dat")
        for name in ("flicker-op", "flicker-models", "flicker-geometry"):
            shutil.copy2(work / f"{name}.dat", results / f"{name}.dat")
        roots = summary["metrics"]["pole_zero"]
        root_rows = [[kind, i+1, *root, np.hypot(*root)/(2*np.pi)]
                     for kind in ("poles", "zeros")
                     for i, root in enumerate(roots[f"{kind}_rad_per_s"])]
        with (results / "poles-zeros.csv").open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(["kind", "index", "real_rad_per_s", "imag_rad_per_s", "magnitude_Hz"])
            writer.writerows(root_rows)
        (results / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
        plot(data)
        plot_metrics(data, summary, FIGURES)
        # Matplotlib SVG path formatting contains trailing spaces by default.
        for path in FIGURES.glob("*.svg"):
            if path.stem not in ("schematic", "gallery-original"):
                path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
        print(json.dumps({key: summary[key] for key in (
            "differential_gain_dB", "common_mode_gain_V_per_V", "cmrr_dB",
            "common_mode_tail_gain_V_per_V", "bandwidth_3dB_Hz", "unity_gain_frequency_Hz", "checks")}, indent=2))


if __name__ == "__main__":
    main()
