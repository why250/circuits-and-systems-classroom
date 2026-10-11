# 5T OTA: validated case and tool details

Read this when reusing this repository's 5T OTA artifacts, studying an example of the workflow, or handling ngspice MOS1 noise. Conclusions are limited to this circuit, model, and tool version. Linked original artifacts are authoritative for equations, numbers, and execution reports; do not duplicate a numerical table in the skill.

## Authoritative artifacts

The project root is `../../../..` relative to this file:

- [Preliminary analysis](../../../../5T-Differential-Amplifier-Analysis.md): retained historical learning starting point. Later verification corrected some equations; this is not the authoritative source for validated equations.
- [Companion document connecting equations to simulation](../../../../5T-OTA-Schematic-and-Simulation.md): topology, small-signal KCL, engineering approximations, individual tests, plots, comparisons, and model boundaries.
- [Simulation run guide](../../../../simulations/5t-ota/README.md): testbenches, execution entry point, and local rerun instructions.
- [Execution script](../../../../code/run_5t_ota.py): actual ngspice invocation, OP reading, independent KCL solution, data checks, and evidence publication.
- [Metrics and plotting module](../../../../code/ota_5t_metrics.py): supply/impedance KCL, noise-source calculations, PZ reconstruction, settling time, and plots.
- [Circuit provenance](../../../../circuits/5t-ota/provenance.json): original circuit identity, parameters, and structural comparison.
- [Execution report](../../../../simulations/5t-ota/results/summary.json): model conditions, actual versions, hashes, metrics, and passed checks. Counts and values change as tests expand; read the report instead of reusing historical counts.

Do not copy the entire 5T runner as a generic tool for other circuits. Its device count, three-node matrix, input definition, and bias are specific to this OTA. Reuse the execution/checking/plotting structure, then establish the equations and testbenches for the new circuit.

## Key corrections from preliminary analysis to verification

- This is a differential pair with a single-ended current-mirror load. M3 is diode-connected and M4 is the mirror output device; the output load is not a diode-connected device.
- After defining `vd = vinp - vinn`, determine the gain sign and devices contributing to output resistance from the actual output terminal.
- Under common-mode excitation, the tail node follows the input. A large tail resistance does not make it AC ground. Include gm, gmb, and gds; do not copy common-mode/CMRR equations from a resistor-loaded differential pair.
- PSRR depends on bias, input, and output reference grounds. Negative-supply perturbation is not automatically equivalent to a common-mode input.
- Compare simplified current-mirror poles/zeros separately from full-model PZ roots. A zero alone does not determine settling time. High-frequency sweeps expose model differences rather than proving process accuracy at high frequencies.
- The 100 uV differential step verifies small-signal open-loop settling. It does not establish closed-loop stability or large-signal slew performance.

## Noise extension and parameter selection

Retain the [thermal-only deck](../../../../simulations/5t-ota/noise.cir), then compare with the [thermal-plus-1/f deck](../../../../simulations/5t-ota/noise-flicker.cir). The new deck changes KF/AF using `altermod` only in its own process, preserving the baseline model, OP, topology, and capacitances.

Educational coefficients in this case target an input-noise PSD corner in the kHz range, based on independent KCL at this bias and the exact MOS1 source equations. Actual coefficients, corners, and integrated values are in the companion document/report; they are not process-calibrated. One-sided noise data are amplitude densities: square them to obtain power, integrate, and then take the square root.

For MOS1 with unit multiplicity, the 1/f drain-source current PSD has the form

`KF * |Id|^AF / (f * W * (L - 2*LD) * Cox^2)`, where `Cox = epsilon_ox / TOX` and W/L are in meters. AF is the current exponent. This KF definition is not universal across compact models. The equation follows the [ngspice MOS1 source code](https://github.com/ngspice/ngspice/blob/master/src/spicelib/devices/mos1/mos1noi.c) and was checked against source-component results from local ngspice-33.

Useful checks in this case include per-device thermal/flicker power addition, power addition across devices, differential-input normalization, preservation of the original thermal spectrum, low-frequency independent KCL for each device, the full-band 1/f relationship between mechanism power ratios, and low-frequency analytical integration. Select checks appropriate to each new topic's model.

## Validated Windows/ngspice-33 details

- The local runner uses the official ngspice-33-w7 executable package and adjacent DLLs; it does not depend on global PATH. Discover available tools in other environments instead of hard-coding this computer's absolute paths.
- Use batch mode, write logs to files, and hide Windows subprocess windows. A missing optional init file did not prevent this case's analyses; that does not justify ignoring other errors or missing outputs.
- MOS1 accepts KF/AF inputs, but `@model[kf]` and `@model[af]` queries report unavailable parameters in this version. The verified approach records KF/AF from the executed deck, captures TOX/LD and device W/L, and checks their actual effect with independent source PSDs.
- Use ngspice's normalized lowercase model names in `@model[...]` queries. Uppercase names caused model-not-found errors in this run.
- Model capabilities and query interfaces are different: a failed KF query does not imply that the simulator lacks 1/f noise support.

These tool details describe a known version. Consult current documentation and verify behavior when using another version, preferring interfaces supported by that version.