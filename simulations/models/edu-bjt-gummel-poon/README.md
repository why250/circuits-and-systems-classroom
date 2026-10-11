# Shared educational Gummel–Poon BJT library

Use [v1.lib](v1.lib), version **1.0.0**, as the starting point for this project's compatible NPN circuit **derivation → testbench → simulation curves → numerical comparison** studies. It is an educational SPICE Gummel–Poon model, not a SKY130 model or a process-calibrated device. A requested PDK, process-performance question, or required mechanism absent from this model takes precedence.

The model name is `NPN_EDU`. This version promotes the exact model card already exercised in the [BJT emitter-degenerated differential-pair lab](../../bjt-degenerated-differential-pair/README.md). Its [local snapshot](../../bjt-degenerated-differential-pair/models.lib) remains unchanged. No PNP model has been validated or included. Circuit connections, supplies, bias, resistors, loads, input-source impedance and temperature belong to each experiment.

SHA-256 of `v1.lib`:

```text
68738c2f2da61269687ceef68d5feea3b99537c1b2b1ae894a2619bc1f44261e
```

## Coefficients and physical scope

| Parameter | Value | Unit / role |
|---|---|---|
| IS | 1e-15 | A; transport saturation current |
| BF / NF | 100 / 1 | Ideal forward current gain / forward emission coefficient |
| VAF | 100 | V; forward Early voltage, giving finite output conductance |
| BR / NR / VAR | 1 / 1 / 100 | Reverse gain / emission coefficient / Early voltage (V) |
| RB / RC / RE | 0 / 0 / 0 | Ω; intrinsic series resistances are excluded |
| CJE / VJE / MJE | 1p / 0.75 / 0.33 | F / V / dimensionless; BE depletion-capacitance parameters |
| CJC / VJC / MJC | 0.3p / 0.75 / 0.33 | F / V / dimensionless; BC depletion-capacitance parameters |
| TF / TR | 200p / 1n | s; forward / reverse transit-time parameters |
| KF / AF | 0 / 1 | White baseline; optional BJT base-current flicker coefficient / exponent |
| TNOM | 27 | °C; nominal model temperature, distinct from the experiment's `.temp` |

The baseline includes finite base current, forward/reverse junction behavior, Early effect, bias-dependent depletion and diffusion charge, and collector/base shot noise. Explicit circuit resistors contribute thermal noise; ideal bias sources do not. Zero intrinsic series resistance simplifies the nodal and noise reconstruction, but excludes intrinsic base-resistance thermal noise. BF is a model coefficient; do not assume the actual operating-point ratio `ic/ib` equals BF exactly.

The library supplies no calibrated high-current gain rolloff, substrate network, device matching statistics, process corners, avalanche characterization, extracted interconnect or nonideal bias-source noise. Basic simulator temperature behavior is not a characterized process-temperature model. Transit-time and capacitance coefficients are illustrative; numerical gain, bandwidth, noise or GHz roots from this model do not predict SKY130 performance.

For accurate AC reconstruction, read the simulator's charge derivatives rather than assuming constant model-card capacitances. The validated lab includes `cpi`, `cmu` and the signed BE/BC cross-charge derivative `cexbc` in its independent nodal equations. `cexbc` is a controlled charge derivative, not a standalone negative capacitor. Its effect was measurable at high frequency in this example; apply the charge model required by the new circuit and simulator.

## Reuse in a new experiment

For a deck executed from `simulations/<topic>/`:

```spice
.include "../models/edu-bjt-gummel-poon/v1.lib"
.temp 27
* Primitive BJT terminal order: collector, base, emitter.
Q1 out vin emitter NPN_EDU
```

This shows syntax, not a complete biased circuit. Load either the shared library or a version-pinned local snapshot, avoiding duplicate definitions of `NPN_EDU`. The teaching instance uses three terminals with default unit area. The original four-terminal SKY130 subcircuit has its own terminal mapping; this primitive does not reproduce its grounded substrate or substrate parasitics. Preserve the original project and structural PDK netlist separately when creating a teaching reconstruction.

Choose bias and load from the new circuit's equations and headroom, then execute OP checks. For forward-active small-signal analysis, check forward BE bias and reverse BC bias on each NPN, including across relevant sweeps. A fixed 0.2 V VCE threshold is not sufficient to establish forward-active operation. Neither the differential pair's 3.3 V supply, 1.8 V input common mode, 0.85 V tail bias nor 10 pF output load is a library default.

Relative ngspice includes in these examples resolve from the execution directory. A temporary-directory runner must stage the required directory structure or a byte-identical version-pinned snapshot, then adjust the include path. Record the source library version and executed model hash, along with the simulator version and experiment conditions.

## Local extensions and versioning

- Treat v1 coefficients as frozen. Publish intentional baseline changes as a new version and revalidate affected experiments; do not silently replace existing circuit-local snapshots or execution reports.
- Keep mechanism experiments local. Record overrides, parameter values and their rationale, and retain the baseline comparison. Do not tune coefficients solely to force agreement with an approximation.
- The baseline KF=0 excludes flicker noise. In the ngspice BJT convention, the optional base-current source has one-sided PSD `KF * abs(IB)^AF / f`, in A²/Hz with current in amperes and frequency in hertz. It differs from MOS1's area/oxide-normalized convention; do not transfer KF between compact-model families.
- The differential-pair extension uses KF=1e-14, AF=1, producing approximately a 249 Hz input-referred crossover at that circuit's bias. It is a selected teaching coefficient, not device data or a universal corner frequency. A control-block override in a separate ngspice run preserves the shared white baseline:

```spice
.control
altermod NPN_EDU KF=1e-14 AF=1
* Run the experiment's noise command here with its defined output and input source.
.endc
```

Reuse of a device library does not validate a new circuit's gain, CMRR, PSRR, noise, transfer function or settling equations. The [companion document](../../../BJT-Degenerated-Differential-Pair-Schematic-and-Simulation.md) contains the model-specific derivations, plots and executed independent checks. Its device parameters come from ngspice OP; analytical independence concerns construction and solution of the circuit equations, not device calibration or independently predicted bias.

## Executed reuse checks

On **2026-10-11**, [the checker](../../../code/check_educational_bjt.py) executed six representative differential-pair decks twice with ngspice-33: once using the frozen snapshot and once using shared v1. The cases cover OP, differential/common-mode complex AC, white/flicker noise, and transient response. The shared flicker deck loads v1 and uses the process-local override above; the original deck retains its inline extension.

All six comparisons passed with **zero observed difference** in the exported numerical data. Acceptance uses relative tolerance 1e-8 and zero absolute tolerance, checks aligned acquisition shapes/axes and finite values, and does not hide small noise densities or cancelled zeros. This establishes snapshot/shared-library reuse consistency for the tested decks, separate from the existing lab's independent circuit-equation checks. No PDK validation or standalone generic BJT example run is claimed.

From the project root, run:

```powershell
python code/check_educational_bjt.py --ngspice 'path\to\ngspice.exe'
```

The script also accepts `NGSPICE_BIN` or an executable on PATH and works from another directory when invoked by absolute script path. It needs Python and NumPy, runs hidden simulator processes on Windows in temporary directories, and publishes only after checks pass. It preserves the original lab files and results.

[The summary](results/summary.json) records the version, execution time, simulator/executable identity, input hashes, tolerances and comparisons. [Evidence](results/) retains both staged decks, model cards and logs, plus shared-run raw data. The existing companion's figures remain the visual teaching evidence; this promotion introduces no new circuit or metric.

For model semantics, consult the [ngspice BJT documentation](https://nmg.gitlab.io/ngspice-manual/bjts/bipolarjunctiontransistors_bjts.html) and [manual index](https://ngspice.sourceforge.io/docs.html), accounting for the actual recorded simulator version.
