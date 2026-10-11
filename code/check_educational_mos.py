"""Execute the shared teaching MOS example and compare with independent equations.

Also compare representative legacy OTA/cascode decks with their frozen model
snapshots and shared v1, without overwriting any existing lab results.
Requires NumPy. Run with --ngspice /path/to/ngspice; all paths are script-relative.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / "simulations/models/edu-mos-level1"
EXAMPLE = LIBRARY / "examples/common-source.cir"
REGRESSION_CASES = (
    ("5t-ota", "ota-core.cir", ("op", "ac-differential", "ac-common-mode", "noise", "noise-flicker")),
    ("source-degenerated-cascode", "cascode-core.cir",
     ("baseline-op", "baseline-ac-input", "baseline-noise", "load-10k-op", "load-10k-ac-input", "load-10k-noise")),
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_ngspice(executable, deck, work):
    options = {}
    if os.name == "nt":
        info = subprocess.STARTUPINFO()
        info.dwFlags = subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = 0
        options.update(startupinfo=info, creationflags=subprocess.CREATE_NO_WINDOW)
    result = subprocess.run([str(executable), "-b", "-o", f"{deck}.log", f"{deck}.cir"],
                            cwd=work, capture_output=True, text=True, timeout=60, **options)
    log_path = work / f"{deck}.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    if result.returncode or not log or re.search(
            r"(?im)^\s*(?:error\b|fatal\b|doAnalyses:)|simulation\(s\) aborted", log):
        raise RuntimeError(f"{deck} failed:\n{log}\n{result.stderr}")
    return log


def load(path):
    data = np.loadtxt(path, skiprows=1, ndmin=2)
    if not np.isfinite(data).all():
        raise ValueError(f"Nonfinite data: {path}")
    return data


def close(observed, predicted, label, tolerance=2e-5):
    # Zero absolute tolerance avoids masking tiny noise powers.
    if not np.allclose(observed, predicted, rtol=tolerance, atol=0):
        raise ValueError(f"{label}: observed {observed}, predicted {predicted}")


def check_example(work):
    op = load(work / "common-source-op.dat")
    ac = load(work / "common-source-ac.dat")
    noises = [load(work / f"common-source-noise-{kind}.dat") for kind in ("n", "p")]
    if op.shape != (1, 15) or ac.shape != (321, 5):
        raise ValueError("Common-source acquisition is incomplete")
    for noise in noises:
        if noise.shape != (321, 3) or not np.array_equal(noise[:, 0], ac[:, 0]):
            raise ValueError("Noise/AC frequency grid mismatch")
    values = op[0, 1:]
    vdd, resistance, overdrive = 1.8, 20000, .15
    temperature, boltzmann = 300.15, 1.380649e-23
    devices = {}
    for i, (name, kp, ratio, lam, width) in enumerate((
            ("NMOS_EDU", 200e-6, 8, .03, 4e-6),
            ("PMOS_EDU", 80e-6, 16, .04, 8e-6))):
        a = .5*kp*ratio*overdrive**2
        # Solve saturated square law and resistor KCL together; no SPICE OP
        # parameters feed this bias prediction. PMOS current is a magnitude.
        expected_out = ((vdd-resistance*a) if i == 0 else
                        resistance*a*(1+lam*vdd))/(1+resistance*a*lam)
        vds = expected_out if i == 0 else vdd-expected_out
        if vds <= overdrive:
            raise ValueError("Independent prediction is not saturated")
        current = a*(1+lam*vds)
        gm, gds = 2*current/overdrive, a*lam
        gmb = gm*.4/(2*np.sqrt(.7))
        cgd = 200e-12*width
        close(values[[i, 2+i, 4+i, 6+i, 8+i, 12+i]],
              [expected_out, current, gm, gds, gmb, cgd], f"{name} OP")
        s = 2j*np.pi*ac[:, 0]
        conductance = 1/resistance+gds
        prediction = (-gm+s*cgd)/(conductance+s*(1e-12+cgd))
        observed = ac[:, 1+2*i]+1j*ac[:, 2+2*i]
        close(observed, prediction, f"{name} complex AC")
        # One-sided channel plus load-resistor thermal current PSD.
        current_psd = 4*boltzmann*temperature*((2/3)*gm+1/resistance)
        out_density = np.sqrt(current_psd)/abs(conductance+s*(1e-12+cgd))
        in_density = out_density/abs(prediction)
        close(noises[i][:, 1], out_density, f"{name} output thermal noise", tolerance=2e-4)
        close(noises[i][:, 2], in_density, f"{name} input thermal noise", tolerance=2e-4)
        devices[name] = {
            "predicted_OUT_V": float(expected_out), "observed_OUT_V": float(values[i]),
            "predicted_ID_A": float(current), "observed_ID_A": float(values[2+i]),
            "predicted_gm_S": float(gm), "predicted_gds_S": float(gds), "predicted_gmb_S": float(gmb),
            "gain_1Hz_V_per_V": float(observed[0].real),
            "input_noise_1Hz_V_sqrtHz": float(noises[i][0, 2]),
            "saturation_margin_V": float(vds-overdrive),
        }
    return devices, {"op": op, "ac": ac, "noise-n": noises[0], "noise-p": noises[1]}


def regression(executable, work):
    comparisons, source_hashes = [], {}
    for lab_name, core, decks in REGRESSION_CASES:
        lab = ROOT / "simulations" / lab_name
        for source in (lab / core, lab / "models.lib", *(lab / f"{deck}.cir" for deck in decks)):
            source_hashes[str(source.relative_to(ROOT)).replace("\\", "/")] = digest(source)
        for deck in decks:
            variants = {}
            for variant in ("snapshot", "shared-v1"):
                destination = work / lab_name / deck / variant
                destination.mkdir(parents=True)
                for source in (lab / core, lab / f"{deck}.cir"):
                    shutil.copy2(source, destination / source.name)
                model = lab / "models.lib" if variant == "snapshot" else LIBRARY / "v1.lib"
                shutil.copy2(model, destination / "models.lib")
                run_ngspice(executable, deck, destination)
                outputs = {path.name: load(path) for path in destination.glob("*.dat")}
                if not outputs:
                    raise ValueError(f"No regression waveforms: {lab_name}/{deck}")
                variants[variant] = outputs
            original, shared = variants["snapshot"], variants["shared-v1"]
            if original.keys() != shared.keys():
                raise ValueError(f"Regression output set differs: {deck}")
            errors = {}
            for name, baseline in original.items():
                replacement = shared[name]
                if baseline.shape != replacement.shape:
                    raise ValueError(f"Regression data shape differs: {deck}/{name}")
                close(replacement, baseline, f"{lab_name}/{deck}/{name}", tolerance=1e-8)
                delta = abs(replacement-baseline)
                nonzero = baseline != 0
                errors[name] = float(np.max(delta[nonzero]/abs(baseline[nonzero]))) if nonzero.any() else 0
            comparisons.append({"lab": lab_name, "deck": deck,
                                "max_relative_error_by_output": errors, "passed": True})
    return comparisons, source_hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ngspice", default=os.environ.get("NGSPICE_BIN", "ngspice"))
    args = parser.parse_args()
    executable = Path(shutil.which(args.ngspice) or args.ngspice).resolve()
    if not executable.is_file():
        raise FileNotFoundError(f"ngspice not found: {executable}")
    with tempfile.TemporaryDirectory(prefix="classroom-edu-mos-") as temporary:
        work = Path(temporary)
        examples = work / "examples"
        examples.mkdir()
        shutil.copy2(LIBRARY / "v1.lib", work / "v1.lib")
        shutil.copy2(EXAMPLE, examples / EXAMPLE.name)
        log = run_ngspice(executable, "common-source", examples)
        devices, waveforms = check_example(examples)
        comparisons, legacy_hashes = regression(executable, work / "regression")
        report = {
            "validation_date": datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
            "library": "Classroom educational MOS v1; not process-calibrated",
            "simulator_detected_version": sorted(set(re.findall(r"ngspice-([^\s]+) done", log))),
            "simulator_executable_sha256": digest(executable),
            "source_sha256": {"v1.lib": digest(LIBRARY / "v1.lib"),
                              "examples/common-source.cir": digest(EXAMPLE),
                              "code/check_educational_mos.py": digest(Path(__file__))},
            "conditions": {"VDD_V": 1.8, "NMOS_VG_V": .6, "PMOS_VG_V": 1.2,
                           "Rload_ohm": 20000, "CL_F": 1e-12, "temperature_C": 27},
            "common_source": devices,
            "checks": ["NMOS/PMOS bias from square law and resistor KCL",
                       "NMOS/PMOS gm, gds, gmb and overlap capacitance",
                       "NMOS/PMOS full complex AC transfer including Cgd",
                       "NMOS/PMOS one-sided channel and load thermal noise",
                       "representative OTA/cascode snapshot vs shared-v1 waveforms"],
            "legacy_source_sha256": legacy_hashes,
            "regression_comparisons": comparisons,
            "all_checks_passed": True,
        }
        # No existing lab results are overwritten. Publish only checked evidence.
        destination = LIBRARY / "results"
        destination.mkdir(exist_ok=True)
        headers = {"op": "scale,OUTn_V,OUTp_V,IDn_A,IDp_A,gmn_S,gmp_S,gdsn_S,gdsp_S,gmbn_S,gmbp_S,Cgsn_F,Cgsp_F,Cgdn_F,Cgdp_F",
                   "ac": "frequency_Hz,An_real,An_imag,Ap_real,Ap_imag",
                   "noise-n": "frequency_Hz,output_V_sqrtHz,input_V_sqrtHz",
                   "noise-p": "frequency_Hz,output_V_sqrtHz,input_V_sqrtHz"}
        for name, data in waveforms.items():
            np.savetxt(destination / f"common-source-{name}.csv", data, delimiter=",",
                       header=headers[name], comments="", fmt="%.9e")
        (destination / "common-source.log").write_text(log, encoding="utf-8")
        for path in (work / "regression").rglob("*.log"):
            target = destination / "regression" / path.relative_to(work / "regression")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        (destination / "summary.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
        print(json.dumps({"common_source": devices, "legacy_decks_compared": len(comparisons),
                          "all_checks_passed": True}, indent=2))


if __name__ == "__main__":
    main()
