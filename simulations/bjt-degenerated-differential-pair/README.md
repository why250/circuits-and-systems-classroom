# BJT differential-pair educational ngspice lab

Read [the schematic, metric derivations and simulation comparisons](../../BJT-Degenerated-Differential-Pair-Schematic-and-Simulation.md). General formulas and assumptions are maintained separately in [the analytical reference](../../BJT-Degenerated-Differential-Pair-Analysis.md). The source is a resistor-loaded, emitter-degenerated differential pair, saved as [CML buffer.icproj.json](../../circuits/bjt-degenerated-differential-pair/CML%20buffer.icproj.json). Its declared SKY130 model is not supplied; this lab executes a separately identified educational NPN model.

## Baseline

- Q1/Q2 differential input pair; Q3 tail sink. Original collector resistors remain 1 kΩ; both input emitter resistors and the tail emitter resistor remain 50 Ω.
- Added bias: VDD = 3.3 V, lower rail = 0 V, input common mode = 1.8 V, bias = 0.85 V, temperature = 27 °C.
- Added loads: 10 pF from **each** output to the lower rail.
- [Model v1.0.0](models.lib): educational Gummel–Poon NPN with IS = 1e-15 A, BF = 100, VAF = 100 V, TF = 200 ps, CJE = 1 pF, CJC = 0.3 pF. Intrinsic RB/RC/RE = 0. The model is not a process characterization.
- The same model card is available in the [versioned shared BJT library](../models/edu-bjt-gummel-poon/README.md) for new studies. This lab retains its original frozen snapshot and results; shared-library promotion does not change its executed model.
- White baseline KF = 0. An independent extension uses KF = 1e-14, AF = 1; the coefficient follows the BJT base-current noise convention and yields a roughly 249 Hz input-noise corner in this example.
- Differential input is `vinp - vinn`; differential output is `voutp - voutn`. Single-ended metrics use `voutp`.

## Run

Requires Python with NumPy and Matplotlib, plus an ngspice executable. Paths are resolved from the runner; execution does not depend on the shell's current working directory.

```powershell
python code/run_bjt_differential_pair.py --ngspice 'path\to\ngspice.exe'
```

The actual run used the [official ngspice-33-w7 Windows archive](https://ngspice.sourceforge.io/experimental/ngspice-33-w7.7z), extracted into the ignored local `.tools/` directory:

```powershell
python code/run_bjt_differential_pair.py --ngspice '.tools\ngspice\ngspice-33-w7\ngspice-33-w7\ngspice.exe'
```

`NGSPICE_BIN` or an executable on PATH can also select the simulator. The runner uses hidden Windows processes and log files, runs in a temporary directory, and publishes after every declared comparison passes. It does not install software system-wide.

Source-only extraction and schematic regeneration:

```powershell
python code/bjt_differential_pair_source.py
```

This extraction reads the supplied schema-68 routes/contacts/unrouted connections directly, including virtual substrate S terminals. It asserts the expected device nets and resistor values. It does not relabel the file as an older schema or edit the original. The schematic is a connectivity-checked reconstruction.

## Executed testbenches

| Deck | Experiment |
|---|---|
| `op`, `op-mismatch` | Bias and device derivatives; mismatch gets its own bias |
| `ac-dm`, `ac-cm` | Differential/common-mode transfer, internal nodes, input currents |
| `ac-vdd`, `ac-vss`, `ac-vb` | Separately normalized rail and bias perturbations |
| `ac-vss-tracking-bias` | Lower rail moves while bias-to-lower-rail voltage stays fixed |
| `output-resistance` | One-output current injection with other output free |
| `mismatch-cm`, `mismatch-vdd` | RD2 +1%, common/supply leakage to differential output |
| `dc-transfer` | −200 to +200 mV differential sweep, 0.5 mV step |
| `dc-common-mode` | 1.1–2.8 V common-mode sweep, 5 mV step, active-region boundaries |
| `transient` | 100 µV open-loop differential step, 50 ps edge, 250 ns record |
| `noise-white`, `noise-flicker` | Differential output noise, referred to differential source VDM |

Generated [testbenches](testbenches/) are complete standalone decks except for `models.lib`, which the runner copies into its temporary working directory. To run one manually, copy the desired `.cir` and `models.lib` into the same directory and use `ngspice -b -o run.log name.cir`.

AC and noise grids are 1 Hz–10 GHz, 100 points/decade. Complex waveform exports contain frequency then real/imaginary pairs in the vector order named in the `.cir` deck. DC/transient/noise exports contain the independent axis followed by real scalar columns. Headers are preserved. These `.dat` files are raw simulator waveform exports, not independently predicted data.

## Checks and evidence

[checks.json](results/checks.json) records the actual run, model conditions, numerical metrics, passed comparisons, simulator version and executable hash, source/model/script hashes, and limitations of independent calculation. [Results](results/) retain waveform tables and simulator logs. Plot pairs are in [figures/bjt-degenerated-differential-pair](../../figures/bjt-degenerated-differential-pair/).

The dedicated [pole-zero and transfer figure](../../figures/bjt-degenerated-differential-pair/poles-zeros-and-transfer.png) shows analytical complex-plane roots, actual AC magnitude/phase overlaid with the derived rational transfer, all root frequency scales, and a magnified −3 dB bandwidth crossing. Its [SVG](../../figures/bjt-degenerated-differential-pair/poles-zeros-and-transfer.svg) is regenerated by the same runner. The manifest records both bandwidth calculations and the maximum relative complex-transfer error.

Independent calculations use device parameters captured from ngspice OP; independence refers to assembly/solution of nodal equations, the reduced transfer polynomial, and noise-source propagation. Full complex AC sweeps use relative tolerance 5e-5 and absolute voltage-transfer tolerance 3e-10. Noise PSD comparison uses relative tolerance 8e-5 and absolute tolerance 1e-30 V²/Hz; tiny PSD values cannot be hidden by a generic absolute tolerance. DC slope and small-step checks use separately declared tolerances in the runner.

The Gummel–Poon cross-charge derivative `cexbc` is included alongside `cpi/cmu`. The closed-form polynomial neglects reverse-junction `gmu` near 1e-12 S, while full nodal equations retain it. Poles and zeros are calculated from the independent differential half-circuit polynomial and checked through its complex AC response; no separate SPICE PZ run is claimed.

Noise is one-sided and referred to the same differential input used for signal gain. Finite integration uses 10 Hz–10 MHz. Matched tail noise cancels at the differential output; this does not apply to single-ended noise or mismatched circuits. Internal base resistance, source/bias noise, sampling aliases and advanced physical noise correlations are outside the model.

No SKY130 model execution, substrate coupling, process corners, statistical mismatch, feedback phase margin, or large-signal recovery is claimed. The original [structural netlist](source-structural.cir) preserves the four-terminal SKY130 calls for a future PDK study; it is not an executable PDK testbench without the external model.
