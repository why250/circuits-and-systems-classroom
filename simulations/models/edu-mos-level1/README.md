# Shared educational long-channel MOS library

Use [v1.lib](v1.lib) as the default starting point for this project's MOS circuit **derivation → testbench → simulation curves → numerical comparison** workflow when the question is compatible with a long-channel square-law model. It is a teaching model library, not a process-calibrated PDK. A requested PDK or a mechanism absent from LEVEL=1 takes precedence.

The library promotes the coefficients already exercised in the [5T OTA](../../5t-ota/README.md) and the NMOS model used in the [source-degenerated cascode](../../source-degenerated-cascode/README.md). Model names are `NMOS_EDU` and `PMOS_EDU`. Circuit topology, dimensions, body connections, bias and load belong to each experiment, not to the library.

## Baseline coefficients and mechanisms

| Parameter | NMOS_EDU | PMOS_EDU | Unit / role |
|---|---|---|---|
| LEVEL | 1 | 1 | Long-channel square-law model |
| VTO | +0.45 | -0.45 | V; zero-body-bias threshold |
| KP | 200u | 80u | A/V²; transconductance coefficient, not device beta |
| LAMBDA | 0.03 | 0.04 | 1/V; channel-length modulation and finite output conductance |
| GAMMA | 0.4 | 0.4 | V½; body-effect coefficient |
| PHI | 0.7 | 0.7 | V; body-effect surface-potential parameter |
| TOX | 20n | 20n | m; oxide thickness for intrinsic capacitance and the MOS1 noise convention |
| CGSO / CGDO | 200p / 200p | 200p / 200p | F/m; gate-source/drain overlap capacitance per unit width |
| KF / AF | Omitted: defaults 0 / 1 | Omitted: defaults 0 / 1 | Baseline has no flicker noise; AF is its drain-current exponent |

The baseline includes finite output resistance, body effect, bias-dependent Meyer gate capacitances, overlap capacitances, cutoff/triode/saturation nonlinear behavior, and channel thermal noise. In saturated strong inversion the MOS1 thermal source uses the long-channel factor 2/3. Added resistors have their own thermal noise; ideal voltage/current sources add none.

Junction depletion capacitances and source/drain series resistances default to zero in these cards. No calibrated short-channel effects, mobility degradation, velocity saturation, DIBL, weak-inversion behavior, statistical mismatch, extracted interconnect or bias-generator noise is supplied. Basic simulator temperature behavior is not a characterized process-temperature model. Document simulator defaults and versions when they affect a conclusion. Retaining a short W/L from an imported drawing does not turn this model into a short-channel process prediction.

## Include it in a new lab

For a deck run from `simulations/<topic>/`, use:

```spice
.include "../models/edu-mos-level1/v1.lib"
.temp 27
* Primitive MOS terminal order: drain, gate, source, body.
M1 out vin source vss NMOS_EDU w=4u l=0.5u m=1
M2 out bias vdd vdd PMOS_EDU w=8u l=0.5u m=1
```

These instance lines show syntax, not a complete biased circuit. Load either the shared library or the local snapshot, not both definitions of `NMOS_EDU`/`PMOS_EDU` in one deck. Use explicit SI suffixes (`u`, `n`) and **do not add `.option scale=1u`**. Bind bodies according to the actual circuit; changing a body connection changes threshold and small-signal coupling. Determine suitable dimensions, bias, load and supplies from the new circuit's equations and headroom. Neither the OTA's VB nor its device ratios are universal defaults.

Relative includes in these ngspice examples resolve from the execution directory. A temporary-directory runner must stage dependencies at the same relative paths, or stage a byte-identical version-pinned snapshot and adjust the deck's include accordingly. Record the source model version and executed file hash. The [common-source example](examples/common-source.cir) and its [checker](../../../code/check_educational_mos.py) demonstrate staging without depending on the user's current directory.

## Keep extensions local and versioned

- Pin `v1.lib` and its hash in new experiments. Preserve existing circuit-local model snapshots and old result reports. Do not silently replace them with a moving shared file.
- Treat v1 coefficients as fixed. Publish intentional baseline coefficient changes as a new version and revalidate the affected experiments.
- For a lesson on a particular mechanism, use a separate deck/process with an explicit override, or a separately named local model. Record the change and retain the baseline comparison. For example, disabling LAMBDA removes finite-ro effects; disabling GAMMA removes body effect; neither change should alter the shared baseline.
- Add 1/f noise only when relevant. The [OTA flicker deck](../../5t-ota/noise-flicker.cir) demonstrates process-local `altermod` overrides: NMOS KF=2e-33, PMOS KF=1e-33, AF=1. These are illustrative MOS1 coefficients. Their crossover depends on device dimensions, current and circuit transfer; do not assume a universal 1 kHz corner or transfer KF between compact-model conventions. Keep thermal and flicker PSDs separately available.
- Use the same mechanism/assumption/equation checks for each new topology. Reusing the library does not validate a copied gain, CMRR, PSRR, settling or noise formula. Use a physical PDK when the task requires its missing mechanisms or process performance, preserving a separate teaching baseline when useful.

## Executed generic example and regression checks

The [example](examples/common-source.cir) contains separate resistor-loaded NMOS and PMOS common-source stages. VDD=1.8 V, Rload=20 kohm, CL=1 pF, temperature=27°C. NMOS W/L=4u/0.5u with VG=0.6 V; PMOS W/L=8u/0.5u with VG=1.2 V. Both have 0.15 V gate overdrive and bodies tied to their sources. Unit AC voltage excites a linearized transfer, not a large-signal swing.

Define $a=\tfrac12 KP(W/L)V_{OV}^2$. Saturated square law and resistor KCL give independent bias predictions:

$$
V_{o,n}=\frac{V_{DD}-Ra_n}{1+Ra_n\lambda_n},\qquad
V_{o,p}=\frac{Ra_p(1+\lambda_p V_{DD})}{1+Ra_p\lambda_p}.
$$

From those predictions, calculate $I_D$, $g_m=2I_D/V_{OV}$, $g_{ds}=a\lambda$, and $g_{mb}=g_m\gamma_b/(2\sqrt\Phi)$ at zero body bias. With fixed source/body voltages and no drain-junction capacitance, each stage has

$$
A_v(s)=\frac{-g_m+sC_{gd}}{1/R+g_{ds}+s(C_L+C_{gd})}.
$$

The gate-drain overlap is $C_{gd}=CGDO\,W$ in saturation. For independent load and channel noise, the one-sided output PSD is

$$
S_{v,o}(f)=\frac{4k_BT[(2/3)g_m+1/R]}
{|1/R+g_{ds}+j2\pi f(C_L+C_{gd})|^2},\qquad
S_{v,in}=\frac{S_{v,o}}{|A_v|^2}.
$$

The checker uses coefficients and circuit equations for these predictions, without importing ngspice OP parameters into them. It verifies OP parameters and full complex AC/noise curves from 1 Hz to 100 MHz. Both devices remain saturated at this bias.

| Observable | NMOS common source | PMOS common source |
|---|---|---|
| Output bias, independent prediction / ngspice | 1.42461417 / 1.42461414 V | 0.30521987 / 0.30521990 V |
| Drain-current magnitude | 18.7693 uA | 15.2610 uA |
| Gain at 1 Hz | -4.95167 V/V | -4.02325 V/V |
| Input thermal density at 1 Hz, including load resistor | 7.57569 nV/√Hz | 8.62126 nV/√Hz |

The 2026-10-11 run used ngspice-33. Eleven representative OTA/cascode decks were also executed twice in temporary directories: once with their original model snapshot and once with shared v1. OP, AC and noise captures matched within a relative tolerance of 1e-8, with zero absolute tolerance. This checks representative reuse; it does not certify every circuit or simulator. Existing lab files and results were not overwritten.

From any working directory, run the [checker](../../../code/check_educational_mos.py) with an absolute script path, or from the project root:

```sh
python code/check_educational_mos.py --ngspice /path/to/ngspice
```

It needs NumPy, reuses an existing executable, hides Windows subprocess windows, and publishes evidence only after checks pass. [The report](results/summary.json) records model/deck/checker/executable hashes and the compared legacy inputs. [Example CSVs and execution/regression logs](results/) are retained separately from the circuit labs.

For a manual example run, change to `simulations/models/edu-mos-level1/examples/` and run `ngspice -b -o common-source.log common-source.cir`; its DAT files are written there. The checker stages this directory layout in temporary storage instead.
