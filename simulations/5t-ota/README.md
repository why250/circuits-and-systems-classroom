# Five-transistor OTA ngspice lab

This directory contains a runnable educational circuit and the original SKY130
structural export. See [the schematic and simulation results](../../5T-OTA-Schematic-and-Simulation.md)
and [circuit provenance](../../circuits/5t-ota/README.md).

## Model and circuit identity

`ota-core.cir` is generated from `circuits/5t-ota/educational.icproj.json`.
Its five MOS devices retain Gallery connectivity and W/L: input NMOS
4 um / 0.5 um, PMOS loads 8 um / 0.5 um, tail NMOS 8 um / 1 um.
MOS cards use D/G/S/B order. SI dimensions carry `u` suffixes;
**do not add `.option scale=1u` to the educational decks**.

`models.lib` provides explicit long-channel LEVEL=1 coefficients, channel-length
modulation, body effect and Meyer/overlap capacitances. These are teaching
coefficients, not fitted SKY130 models. Ideal sources supply VDD, common mode
and VB. The lab has no transistor bias generator, mismatch, extracted wires
or calibrated flicker noise.

## Testbenches

Nominal conditions are VDD = 1.8 V, VSS = 0 V, common mode = 0.9 V,
VB = 0.65 V, CL = 1 pF and temperature = 27 C. The bias sweep changes VB.
Core port order is `VDD VSS vinp vinn vout vb`. The supply-transfer benches
use an explicit `vss` node to excite the negative rail; other benches connect
VSS to ground.

| Deck | Excitation and evidence |
|---|---|
| `op.cir` | Balanced inputs; OUT, X, Y, supply current, eight parameters and three capacitances per MOS |
| `bias-sweep.cir` | VB 0.55–0.75 V, 1 mV steps; node voltages, supply current and five saturation margins |
| `ac-differential.cir` | VINP AC 0.5 at 0 degrees, VINN AC 0.5 at 180 degrees; differential input 1 V; 1 Hz–100 GHz, 80 points/decade |
| `ac-common-mode.cir` | Both inputs AC 1 at 0 degrees; complex OUT/X/Y gains on the same frequency grid |
| `ac-output-resistance.cir` | Unit AC current into OUT; inputs, bias and rails AC grounded; complex output impedance |
| `ac-psrr-positive.cir` | VDD AC 1; inputs and VB fixed to ground; OUT and CL ground-referenced |
| `ac-psrr-negative.cir` | VSS AC 1; VDD, inputs and VB fixed to ground; OUT and CL ground-referenced |
| `noise.cir` | One-sided input/output voltage amplitude densities and individual M1–M5 contributions; input reference is the balanced differential source; KF defaults to zero |
| `noise-flicker.cir` | Same bias/grid; illustrative NMOS KF=2e-33, PMOS KF=1e-33, AF=1 via altermod; total and separate thermal/flicker contributions for M1–M5; OP/model/geometry snapshots |
| `poles-zeros.cir` | Differential voltage-transfer roots, signed rad/s; 1 Gohm DC input return and linear controlled sources; PZ supplies the excitation |
| `dc-transfer.cir` | Balanced differential sweep -20 mV to +20 mV in 0.1 mV steps; common mode stays fixed |
| `transient.cir` | 100 uV differential pulse; 5 us delay, 10 ns edges, 20 us width, 50 us period; 40 us run with at most 10 ns steps |

The high-frequency sweeps expose the full compact-model roots and errors of the
reduced transfer model. They do not establish physical LEVEL=1 accuracy at
100 GHz. All AC source amplitudes select linearized transfer functions; they
do not imply large-signal operation.

## Illustrative flicker-noise comparison

The baseline `noise.cir` keeps KF=0. The added `noise-flicker.cir` changes
only KF/AF in its own process; no model or project regeneration is needed.
The nominal coefficients are chosen to show a crossover near 1 kHz, not
to predict a fabrication process. The measured input PSD crossover is
1.40333 kHz. KF uses ngspice MOS1's convention, with W/L in meters and
`Cox = epsilon_ox / TOX`; AF is the drain-current exponent.

To explore other strengths, edit the two KF `altermod` lines in the new deck
and rerun the same Python command. Keep KF positive and AF=1 for this lab's
analytic comparisons. The crossover must remain within the sweep.
Increasing both KF values by the same factor moves the low-frequency
crossover by that factor; noise amplitudes combine by adding powers.
The summary records actual coefficients and geometry, source contributions,
six density samples and four integration bands. The note's numerical tables
describe the checked nominal coefficients and need updating after changes.

At the nominal settings, input RMS over 10 Hz–100 kHz changes from
4.26163 uV (thermal) to 4.52873 uV (thermal plus flicker). For 1 Hz–1 kHz,
it changes from 0.425971 to 1.39371 uV. The plot also varies the lower cutoff
at a fixed 100 kHz upper limit. Never integrate ideal 1/f noise down to zero.
See the companion note for equations and the full comparison tables.

## Run and reproduce

Install ngspice from [the official download page](https://ngspice.sourceforge.io/download.html)
and Python with NumPy and Matplotlib. From the repository root:

```sh
python code/run_5t_ota.py --ngspice /path/to/ngspice
```

Windows PowerShell example with an existing executable:

```powershell
python code\run_5t_ota.py --ngspice 'C:\tools\ngspice\bin\ngspice.exe'
```

If ngspice is on PATH, omit `--ngspice`; `NGSPICE_BIN` also selects it.
The 2026-10-10 local rerun used Python 3.13, NumPy 2.2.6 and Matplotlib 3.10.6.
The official ngspice-33-w7 package is retained in the ignored `.tools/` directory.
On this computer, this PowerShell command works from any directory:

```powershell
python 'D:\Users\Documents\GitHub\circuits-and-systems-classroom\code\run_5t_ota.py' --ngspice 'D:\Users\Documents\GitHub\circuits-and-systems-classroom\.tools\ngspice\ngspice-33-w7\ngspice.exe' --simulator-label 'Official ngspice-33-w7 Windows package'
```

The script finds inputs relative to itself, uses a temporary execution directory,
hides Windows simulator windows and writes logs through `-o`. It publishes
results after all simulations and checks pass. It does not install software
or change PATH.

For a single manual run, change to this directory, then run:

```sh
ngspice -b -o op.log op.cir
```

That deck writes `op.dat` and `devices.dat` relative to its execution directory.
The Python runner stores CSV waveforms, signed root CSV, capacitances and logs
in `results/`. Its helper `code/ota_5t_metrics.py` generates PNG/SVG pairs in
`figures/5t-ota/`: `bias`, `differential`, `common-mode`, `dynamics`,
`poles-zeros`, `settling`, `psrr`, `noise` and `noise-flicker`, plus the `simulation` overview.
The companion note embeds each plot next to the corresponding derivation.

Checks are independently formulated from circuit behavior:

- Five conducting saturated devices at balanced OP; input currents sum to tail current.
- AC gains and common-mode X/Y movement agree with a separate gm/gmb/gds KCL matrix.
- The central DC slope agrees with AC within 1%; the small-step plateau agrees within 2%.
- Dataset completeness, finite values and equal frequency axes before CMRR calculation.
- Matched common-mode equations, output test-current KCL and independently stamped positive/negative supply KCL agree with AC.
- Saturated tail current agrees with the LEVEL=1 square law across the bias sweep; leaving saturation is explicitly recorded.
- Differential input noise referral and the sum of independent MOS noise powers agree over the full sweep; low-frequency current-noise KCL agrees for all five devices.
- Flicker coefficients preserve OP and the thermal baseline. Each MOS's thermal/flicker PSDs sum to its total, and independent KCL matches its low-frequency flicker PSD.
- The per-device flicker/thermal PSD ratio agrees with the MOS1 1/f source equation over the entire sweep. Integrated variances add; the analytic Swhite+B/f integral agrees in the low-frequency 1 kHz bands.
- Full signed PZ reconstruction agrees with the complex AC transfer (relative tolerance 0.02%); scalar pole/zero approximations are compared, not treated as exact.
- The final transient level is measured at 20–24 us. Both 1% and 0.1% last-exit settling times agree with the dominant-pole estimate within 1%.

Saturation is not asserted over the entire DC sweep. The transient checks an
open-loop small step; closed-loop settling, slew rate and feedback stability
need separate benches. Noise includes a thermal baseline and a separate
illustrative flicker comparison; ideal sources omit bias-circuit noise.
Results apply to the specified model, dimensions, stimuli,
reference conventions and load.

## Retained execution evidence

The 2026-10-10 local rerun used the official
[`ngspice-33-w7` experimental Windows package](https://ngspice.sourceforge.io/experimental/ngspice-33-w7.7z);
logs identify `ngspice-33`. The executable ran from the project's `.tools/`
directory, without global installation. Executable/source hashes, detected
version, conditions, checked metrics and date are in
[results/summary.json](results/summary.json). All twelve logs, waveform/root
CSVs, and the executable/input/script hashes are retained alongside it.
The Windows simulator may report a missing optional
init file; decks explicitly set their required capture options.
In ngspice-33 MOS1, `@model[kf]` and `@model[af]` are unavailable despite
KF/AF being supported inputs. The runner parses those coefficients from the
executed deck and checks their simulated PSDs against the independent
equation. TOX/LD and device W/L are captured from ngspice; the raw model,
geometry and OP snapshots are retained in `results/flicker-*.dat`.

## Original SKY130 export

`gallery-original.cir` retains `sky130_fd_pr__nfet_01v8` and
`sky130_fd_pr__pfet_01v8` subcircuit calls, port order and parameters.
It has no supplies, stimulus or PDK include. It is structurally verified
but **was not simulated here**.

Its printed W/L values are micrometers (`w=4`, `l=0.5`) under the Analog Canvas
SKY130 binding, distinct from the educational deck's SI-suffixed values.
Use the corresponding SKY130 SPICE model package, pin its version and corner,
and reproduce its scaling policy. The Analog Canvas SKY130 environment uses
a 1e-6 default scale. Follow the selected wrapper's instructions and avoid
scaling both parameter values and the simulator a second time.

Create a separate SKY130 testbench and verify OP first; educational VB and
results are not a SKY130 bias or performance guarantee. Keep those results
separate from these LEVEL=1 results. No PDK files are vendored here.
