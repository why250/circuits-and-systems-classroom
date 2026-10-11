# Fixed-circuit cascode structure study

Read [the main companion](../../../Source-Degenerated-Cascode-Schematic-and-Simulation.md).
The current source is the saved [KiCad schematic](../../../circuits/source-degenerated-cascode/kicad/cascode-dc.kicad_sch).
It uses RL=1 kohm, RE=50 ohm, VIN=0.85 V, VB=1.4 V, VDD=1.8 V,
VSS=0, CL=1 pF and two NMOS_EDU instances with w=1u l=150n m=10.
The existing model snapshot is unchanged. This is an educational LEVEL=1
study with KF=0, not a process simulation.

## Reproduce

From the repository root on this Windows computer:

```powershell
python code/run_cascode_structure.py
```

The runner uses the per-user KiCad installation at
`%LOCALAPPDATA%/Programs/KiCad/10.0` and its bundled ngspice DLL.
NumPy, SciPy and Matplotlib are required. It exports the saved schematic,
validates all terminal tuples, executes in a temporary directory and
publishes the decks, raw acquisitions, CSV files, logs and report here
after independent checks pass. The schematic and historical decks are
not edited. Later saved schematic edits are incorporated on a rerun;
check the resulting parameters and hashes before reusing printed numbers.

All source subprocess windows are hidden. Each `.cir` also includes a
standalone ngspice control block; its model include is relative to this
directory. Load it from this directory in an ngspice installation to
repeat an individual experiment. The shared-DLL runner normalizes node
and device names in commands because the exported circuit uses slash-prefixed
nodes and the shared API does not normalize every analysis argument.

## Executed experiments

| Deck | Question and conditions |
|---|---|
| `op.cir` | Current, headroom, gm/gmb/gds, geometry and total device capacitances |
| `ac-input.cir` | Signed VIN-to-OUT/E/X transfer and input current; VIN AC=1 |
| `ac-bypass.cir` | Source feedback removed in AC with CB=100 uF across RE |
| `bypass-op.cir` | Bypass capacitor preserves the saved DC bias |
| `ac-output.cir` | Loaded output impedance with a 1 A AC current normalization |
| `ac-bias.cir` | VB-to-OUT/E/X transfer with VB AC=1 |
| `noise.cir` | Thermal total and M1/M2/RE/RL spectra, referenced to V2 |
| `poles-zeros.cir` | Signed poles and zeros with a controlled input and finite DC return |
| `dc-transfer.cir` | VIN=0.76–0.93 V, 0.5 mV step; OUT/E/X and saturation margins |
| `clamp-op.cir` | Ideal source clamp at nominal E preserves the initial bias |
| `sine-clamped-10mV.cir` | Same-input distortion control with source motion prevented |
| `sine-5mV.cir` through `sine-50mV.cir` | Four 1 kHz amplitudes: 5, 10, 20 and 50 mV peak |
| `step.cir` | 100 uV input step with 20 ps edge; small-signal settling |

There are **16 decks**, counting the four normal sinusoidal amplitudes separately.
RL, RE and dimensions are not scanned. The bypass capacitor and ideal source
clamp are diagnostic variants; they are not added to the source schematic.

## Predictions and extraction rules

- Complex AC uses 80 points/decade from 1 Hz to 100 THz. The independent
  E/X/OUT circuit matrix includes body effect, finite output conductance,
  intrinsic device capacitances and CL. The broad grid exposes mathematical
  model roots; it does not assert process validity at those frequencies.
- gm, gmb, gds and queried capacitances include m=10. Circuit calculations
  use those simulated OP parameters directly; they do not multiply by m again.
- Native noise spectra are amplitude densities. Independent current-source
  PSDs are propagated with their own KCL transfers, then compared with the
  squared native spectra. PSDs add; input referral divides amplitude density
  by signal-gain magnitude. Finite-band integration is 10 Hz–100 kHz with
  interpolated endpoints.
- Intrinsic output resistance removes RL conductance from the linearized
  KCL matrix. This model calculation is distinct from the loaded current-injection
  simulation; a separate unloaded nonlinear OP is not claimed.
- PZ poles are checked against the C/G eigenvalues, zeros against the independently
  derived transfer numerator, and both reconstruct the complex AC transfer.
- Independent nonlinear DC solves current and X using LEVEL=1 square-law/triode
  equations with body effect and channel-length modulation. Current multiplicity
  is included explicitly. The measured central derivative uses +/-0.5 mV.
- Sinusoids run for 10 ms with maximum timestep 1 us. Least-squares fits of
  DC and sine/cosine harmonics 1–8 over the final 4 ms give fundamental amplitude,
  H2 and THD. Independent device-equation solutions at the measured VIN samples
  give quasistatic waveform/harmonic predictions. At 1 kHz, omitted dynamic
  corrections are tiny compared with the output pole.
- The source-clamped distortion control keeps the initial bias and input amplitude
  equal, while output amplitude changes. It is not an equal-output comparison.
- Small-step settling is the last exit from a relative plateau-error band,
  measured from the rising-edge end and before the falling edge. The dominant-pole
  expression assumes an instantaneous edge.

The [report](summary.json) records hashes, tools, conditions, metrics and checks.
Raw `.dat` files preserve acquisition values; `.csv` files provide named columns.
The [figure directory](../../../figures/source-degenerated-cascode/current/) contains
six PNG/SVG plot pairs and a cropped native KiCad SVG export. The SVG schematic
is regenerated by the runner; its optional PNG preview can be rasterized using
an SVG renderer, such as the workspace's bundled Node `sharp` package.

## Historical data

The parent directory's 26 original decks and `results/` still describe m=1,
VIN=0.75 V, VB=1.25 V and the original 50-ohm / 10-kohm load cases.
Read [the historical companion](../../../Source-Degenerated-Cascode-Historical-Baseline.md)
for those experiments. No current-case flicker or supply-noise simulation is
included in the thermal totals here.
