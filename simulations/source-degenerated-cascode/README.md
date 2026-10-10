# Source-degenerated cascode ngspice lab

Read [the analytical reference](../../Source-Degenerated-Cascode-Analysis.md)
and [the equation-to-simulation companion](../../Source-Degenerated-Cascode-Schematic-and-Simulation.md).
The circuit is a two-NMOS, resistor-loaded cascode with source degeneration,
not the folded topology implied by its original filename.

## Model identity and conditions

`cascode-core.cir` is extracted from the user's actual connections and
inherited parameters. Port order is `VDD VSS VIN OUT VB`. M1/M2 retain
W=1 um, L=150 nm and unit multiplicity. Both bodies connect to VSS.
Default RLVAL=REVAL=50 ohm. Only teaching model bindings replace SKY130.

`models.lib` defines an explicit LEVEL=1 NMOS model: VTO=0.45 V,
KP=200 uA/V^2, LAMBDA=0.03/V, GAMMA=0.4 sqrt(V), PHI=0.7 V,
TOX=20 nm, CGSO=CGDO=200 pF/m, KF=0, AF=1. Junction capacitances
default to zero. This is not a SKY130 fit or a valid short-channel
prediction merely because the original length is retained.

Nominal supplies/bias are VDD=1.8 V, VSS=0, VIN=0.75 V, VB=1.25 V,
CL=1 pF and 27 C. CL is a testbench addition. The two cases are:

- `baseline-*`: original RL=50 ohm and RE=50 ohm.
- `load-10k-*`: explicit RL=10 kohm experiment; every other condition
  stays the same, and OP is recomputed.

The original file and educational editable copy both retain 50-ohm resistors.
The 10-kohm case is an override in its testbenches. SI-suffixed primitive
W/L values must **not** be multiplied again with `.option scale=1u`.
Supply/input/bias are ideal sources; no mismatch or bias-generator noise is
included. OUT, VIN, VB and CL reference fixed external ground during PSRR tests.

## All 26 testbenches

The following 12 deck types are executed for each of the two cases:

| Suffix | Measurement |
|---|---|
| `op` | OUT/E/X, supply current, 11 parameters per MOS, TOX/LD/W/L; full OP log |
| `ac-input` | VIN AC=1; complex OUT/E/X and VIN source current; 1 Hz–100 THz, 100 points/decade |
| `ac-bias` | VB AC=1; VIN/rails grounded in AC; complex bias coupling |
| `ac-output` | Unit AC current into OUT; all voltage sources grounded in AC; loaded output impedance |
| `ac-psrr-positive` | VDD AC=1; VIN/VB/VSS fixed to external ground |
| `ac-psrr-negative` | VSS AC=1; VIN/VB/VDD fixed to external ground; CL bottom remains ground |
| `noise` | KF=0 thermal input/output amplitude densities and individual M1/M2/RE/RL contributions |
| `noise-flicker` | Separate process: KF=2e-33, AF=1; MOS total/flicker/channel sources plus resistors and OP snapshot |
| `poles-zeros` | Voltage-transfer PZ roots; input DC from controlled source and 1 Gohm return; no shorting input source |
| `dc-transfer` | VIN 0.45–1.05 V, 0.5 mV steps; output, nodes, current, saturation margins and gm |
| `bias-sweep` | VB 0.9–1.7 V, 2 mV steps; same capture; VIN fixed at 0.75 V |
| `transient` | 100 uV single-input pulse; times scale with RL*CL; small open-loop response |

The other two decks are:

- `load-sweep.cir`: 13 RL values, 50 ohm through 40 kohm; RE=50 ohm;
  OP and 1 Hz AC are recomputed at every point. The first sampled
  saturation violation is RL=20 kohm, not an exact transition threshold.
- `degeneration-sweep.cir`: eight RE values, 0.1 ohm through 5 kohm;
  RL=10 kohm; each point recomputes OP and AC. It does not hold gm fixed.

The very broad frequency sweep exposes mathematical feedforward roots in
the teaching model. Its THz endpoint does not assert physical validity.
AC unit amplitudes normalize transfer functions, not large voltage/current swings.

## Reproduce

Python needs NumPy and Matplotlib. Use an existing ngspice executable;
no PDK or global installation is required. From any directory:

```sh
python /path/to/circuits-and-systems-classroom/code/run_cascode.py --ngspice /path/to/ngspice
```

This computer's tested PowerShell command is:

```powershell
python 'D:\Users\Documents\GitHub\circuits-and-systems-classroom\code\run_cascode.py' --ngspice 'D:\Users\Documents\GitHub\circuits-and-systems-classroom\.tools\ngspice\ngspice-33-w7\ngspice.exe'
```

If the executable is on PATH, omit `--ngspice`; `NGSPICE_BIN` is also supported.
The 2026-10-10 run used the existing official ngspice-33-w7 Windows package,
Python 3.13, NumPy 2.2.6 and Matplotlib 3.10.6. Logs identify ngspice-33.

The runner locates sources relative to itself, uses a temporary execution
directory and hides Windows simulator windows. It checks process exits,
logs, acquisition completeness, finite values and frequency axes before
publishing numerical results. It does not alter PATH or install tools.

Ordinary reruns preserve the `.cir` files. To intentionally regenerate all
testbench stimuli from the runner's nominal defaults, add `--generate-decks`.
That option overwrites authored decks, so omit it after manually editing a deck.
The numerical checks describe the two declared nominal cases; changing supply,
bias, dimensions, model or load requires reviewing those assumptions and
updating published tables rather than merely accepting old assertions.

Regenerate the extracted core/original netlist, teaching project and SVG with
`python code/export_cascode.py` before rerunning after a source change.
The optional schematic PNG is a rasterization of that SVG; its generation is
not required to execute the numerical lab.

For a manual single-deck run, change to this lab directory:

```sh
ngspice -b -o baseline-op.log baseline-op.cir
```

Its raw outputs are written relative to the execution directory. The runner
retains all raw `.dat` files and logs in `results/`, adds waveform CSVs,
signed PZ-root CSVs and combined sweep CSVs, and saves `summary.json`.

## Independent checks and evidence

Device gm/gmb/gds/capacitances come from OP; independence is in the
separately derived circuit equations, not in a second process model.

- Nominal conducting saturation, series current equality and resistor voltage drops.
- Saturated square-law current and body-effect thresholds using OP terminal voltages.
- Closed-form signal/bias gains, E/X movement and loaded output resistance.
- Full-frequency E/X/OUT matrix solutions for signal, bias, current injection and both supplies.
- Input capacitor currents versus measured source admittance; VIN and VB DC derivatives versus AC.
- C/G eigenvalue poles, independent numerator zeros and full complex PZ reconstruction versus AC.
- Per-source thermal and flicker spectra versus independent full-frequency noise-current transfers.
- Source power sums, input referral, unchanged OP/channel/resistor noise after adding KF.
- Finite-band thermal/flicker variance addition and the low-frequency white+B/f integral.
- Small-step gain and 1%/0.1% last-exit open-loop settling against the slow pole.
- Recomputed load/degeneration sweep gains versus each point's independent KCL.

Full-model relations are checked tightly. Simple gain/pole estimates are
compared and their approximation errors explained, not forced to match.
The signed roots include one LHP and one RHP zero; there is no mirror pole.
Both nominal circuits are stable in this open-loop teaching model.

`results/summary.json` records the actual date, executable hash, simulator
identity, all deck/script/project hashes, conditions, metrics and checks.
Eight PNG/SVG plot pairs are in `figures/source-degenerated-cascode/`:
`bias-and-dc`, `ac-and-impedance`, `input-impedance`, `psrr-and-bias`,
`noise`, `settling`, `poles-and-load` and `degeneration`.
Plots use actual ngspice data; analytical overlays identify their origin.

In ngspice-33 MOS1, KF/AF inputs work but their `@model[...]` queries do not.
The runner records KF/AF from the executed deck, queries TOX/LD/W/L,
and checks the source equation across the entire spectrum. KF=2e-33 is
illustrative, and AF=1 is the drain-current exponent. Noise densities are
one-sided V/sqrt(Hz); square them before integration or power addition.
Do not integrate ideal 1/f noise to zero frequency.

## Original SKY130 binding

`original-sky130.cir` structurally extracts the source's four elements,
original port order and global ground. Calls use
`sky130_fd_pr__nfet_01v8` with D/G/S/B order and W=1, L=0.15 in the
wrapper's micrometer convention. Correct PDK model files, corner,
version and scaling policy are required; avoid scaling twice.
This netlist has no bias/stimulus/PDK include and was **not simulated here**.
The teaching biases and results are not a foundry-model guarantee.

## Sources

- [ngspice documentation](https://ngspice.sourceforge.io/docs.html).
- [Official download page](https://ngspice.sourceforge.io/download.html).
- [MOS1 channel/flicker-noise source](https://github.com/ngspice/ngspice/blob/master/src/spicelib/devices/mos1/mos1noi.c).
- [Source project identity](../../circuits/source-degenerated-cascode/provenance.json).

No public Gallery URL was supplied or inferred for this circuit.
